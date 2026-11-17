"""ORDER BY physical operator: prepare, base-sort, merge, and map rows."""

from __future__ import annotations
import asyncio
import contextlib
import logging
import time
from typing import Any, Dict, List, Type
import pandas as pd
from pydantic import BaseModel
from sema_prototype.llm.stats import RequestStats
from sema_prototype.logical_operator.orderby import OrderbyConfig
from sema_prototype.physical_operator.base import SemanticOperator
from ._common import (
    OrderbyPayloadMixin,
    OrderbyRankingMixin,
    emit_orderby_event,
    safe_gather,
)
from .merge import OrderbyMergeMixin
from .merge._shared.producer import materialize_producer

logger = logging.getLogger(__name__)
VALID_MODES = {"buffer", "full"}


def _resolve_mode(mode: str | None, limit: int | None) -> str:
    """Resolve the execution-form mode.

    Explicit ``mode`` wins. With ``None`` the rule is: ``buffer`` when a
    top-k limit is provided (streaming, early termination beats per-layer
    fan-out), otherwise ``full`` (full sort benefits from per-layer
    ``safe_gather`` parallelism).
    """
    if mode is None:
        return "buffer" if limit is not None else "full"
    if mode not in VALID_MODES:
        raise ValueError(
            f"Unknown mode {mode!r}. Expected one of {sorted(VALID_MODES)} or None (auto)."
        )
    return mode


class SemanticOrderby(
    OrderbyMergeMixin, OrderbyRankingMixin, OrderbyPayloadMixin, SemanticOperator
):
    """Sort through the same execution interface used by the other operators."""

    def _record_request_stats(self, stats: RequestStats) -> None:
        self._request_stats = getattr(self, "_request_stats", RequestStats()) + stats
        ledger = getattr(self, "audit_ledger", None)
        if ledger is not None:
            ledger["prompt"] += stats.input_tokens
            ledger["completion"] += stats.output_tokens
            ledger["total"] += stats.input_tokens + stats.output_tokens
            ledger["calls"] += stats.total_requests

    async def _execute_orderby_batch(self, prompts, *, desc, response_format=None):
        responses, stats = await self.batch_executor.execute_with_stats_async(
            prompts,
            desc=desc,
            response_format=response_format,
        )
        self._record_request_stats(stats)
        from sema_prototype.llm.execution_control import note_request_usage

        note_request_usage(stats)
        return responses

    def _client_stats(self) -> RequestStats:
        client = self.batch_executor.llm_client
        if hasattr(client, "snapshot_stats"):
            return client.snapshot_stats()
        return getattr(client, "_stats", RequestStats()).snapshot()

    @contextlib.contextmanager
    def _execution_phase(self, phase: str):
        from sema_prototype.llm.execution_control import ACTIVE_CONTROL

        control = ACTIVE_CONTROL.get()

        def returned_totals():
            rows = control.returned.values() if control is not None else ()
            rows = list(rows)
            return tuple(
                sum(row[key] for row in rows)
                for key in ("calls", "input_tokens", "output_tokens")
            )

        wire_before = returned_totals()
        before = self._request_stats.snapshot()
        client_before = self._client_stats()
        start = time.perf_counter()
        try:
            yield
        finally:
            wall = time.perf_counter() - start
            stats = self._request_stats.delta_from(before, elapsed=wall)
            # Custom/test executors may update client stats directly.
            if not stats.total_requests:
                stats = self._client_stats().delta_from(client_before, elapsed=wall)
            wire_after = returned_totals()
            if wire_after[0] > wire_before[0]:
                stats.input_tokens = wire_after[1] - wire_before[1]
                stats.output_tokens = wire_after[2] - wire_before[2]
            self._phase_stats.append(stats)
            emit_orderby_event("phase_end", phase=phase, stats=stats, wall_seconds=wall)

    async def execute_async(
        self,
        df: pd.DataFrame,
        user_instruction: str,
        *,
        limit: int | None = None,
        K: int | None = None,
        k: int | None = None,
        h: int | str | None = None,
        m: int = 12,
        algorithm: str = "listwise",
        merge_algorithm: str = "sliding_window",
        mode: str | None = None,
        ascending: bool = False,
        parameter_policy: str | None = None,
        input_token_profile: Any | None = None,
        input_token_counting: Any | None = None,
        use_evidence: bool = False,
        shuffle_mode: str = "none",
        input_partition: str = "contiguous",
        input_partition_seed: int = 0,
        full_tail_correction: bool = True,
        tail_cache_dir: str | None = None,
        mc_samples: int = 16384,
        mc_seed: int = 2410000,
        prefetch: bool = True,
        listwise_buffer_config: Any | None = None,
        need_explanation: bool = False,
        **extra: Any,
    ) -> pd.DataFrame:
        from .merge._shared.plan import (
            MODEL_VERSION,
        )
        from .merge import prepare_merge_plan
        from .merge._shared.plan import MergeRequest
        from .merge._shared.runtime import execute_family, PREFETCH_POLICY
        from sema_prototype.llm.execution_control import QueryControl, ACTIVE_CONTROL

        if extra:
            raise TypeError(
                f"Unsupported ORDER BY parameters: {sorted(extra)}. Experimental options belong in run_orderby_experiment()."
            )
        self._request_stats = RequestStats()
        self._phase_stats = []
        self._last_merge_plan = None
        self.audit_ledger = {"prompt": 0, "completion": 0, "total": 0, "calls": 0}
        started = time.perf_counter()
        result = None
        error = None
        resolved_mode = None
        selected = None
        profile = None
        plan = None
        policy = parameter_policy
        control = QueryControl()
        scope = ACTIVE_CONTROL.set(control)
        requested = dict(
            limit=limit,
            K=K,
            k=k,
            h=h,
            m=m,
            algorithm=algorithm,
            merge_algorithm=merge_algorithm,
            mode=mode,
            ascending=ascending,
            parameter_policy=parameter_policy,
            input_token_profile=input_token_profile,
            input_token_counting=input_token_counting,
            use_evidence=use_evidence,
            shuffle_mode=shuffle_mode,
            input_partition=input_partition,
            input_partition_seed=input_partition_seed,
            full_tail_correction=full_tail_correction,
            tail_cache_dir=tail_cache_dir,
            mc_samples=mc_samples,
            mc_seed=mc_seed,
            prefetch=prefetch,
            listwise_buffer_config=listwise_buffer_config,
        )
        emit_orderby_event(
            "execution_start",
            row_count=len(df),
            instruction=user_instruction,
            params=requested,
        )
        try:
            params = OrderbyConfig(**requested).to_params()
            limit = params["limit"]
            merge_algorithm = params["merge_algorithm"]
            policy = params["parameter_policy"]
            listwise_buffer_config = params["listwise_buffer_config"]
            input_token_profile = params["input_token_profile"]
            resolved_mode = _resolve_mode(
                mode, limit if limit is not None and limit < len(df) else None
            )
            # Reversing a best-prefix does not yield the worst-prefix.
            if ascending and limit is not None:
                resolved_mode = "full"
            if use_evidence and (merge_algorithm == "auto" or policy != "none"):
                raise ValueError(
                    "cost selection requires use_evidence=False; evidence runs need parameter_policy='none'"
                )
            if len(df) <= 1 or limit == 0:
                result = df.iloc[:0].copy() if limit == 0 else df.copy()
                return result
            from .merge._shared.plan import validate_request_capacity

            validate_request_capacity(
                (len(df) + m - 1) // m,
                MergeRequest(
                    algorithm=merge_algorithm,
                    k=k,
                    h=h,
                    m=m,
                    limit=limit,
                    parameter_policy=policy,
                ),
            )
            rows = self._prepare_rows(df, user_instruction)
            partition_rows = list(rows)
            if input_partition == "random":
                import random
                random.Random(input_partition_seed).shuffle(partition_rows)
            emit_orderby_event("input_partition", policy=input_partition,
                               seed=input_partition_seed, row_count=len(rows))
            with self._execution_phase("base_sort"):
                _, sorted_runs = await self._listwise_sort(partition_rows, user_instruction, m)
            short_limit = (
                limit
                if resolved_mode == "buffer" and limit is not None and limit < len(rows)
                else None
            )
            request = MergeRequest(
                algorithm=merge_algorithm,
                k=k,
                h=h,
                m=m,
                limit=None if ascending else limit,
                mode=resolved_mode if ascending else mode,
                parameter_policy=policy,
                profile=input_token_profile,
                input_token_counting=tuple(
                    (
                        {"backend": "auto"}
                        if input_token_counting is None
                        else input_token_counting
                    ).items()
                ),
                use_evidence=use_evidence,
                shuffle_mode=shuffle_mode,
                full_tail_correction=full_tail_correction,
                tail_cache_dir=tail_cache_dir,
                mc_samples=mc_samples,
                mc_seed=mc_seed,
            )
            plan = await prepare_merge_plan(
                self, sorted_runs, user_instruction, request, rows=rows
            )
            self._last_merge_plan = plan
            profile = plan.request.profile
            selected = plan.estimate
            self._last_cost_estimate = selected.to_dict()
            self._last_input_token_profile = profile.to_dict() if profile else None
            emit_orderby_event(
                "parameters_selected",
                estimate=selected.to_dict(),
                profile=profile.to_dict() if profile else None,
                parameter_policy=policy,
                requested_algorithm=requested["merge_algorithm"],
            )
            with self._execution_phase("merge"):
                control.limit = short_limit
                sorted_rows = await execute_family(
                    self,
                    sorted_runs,
                    user_instruction,
                    plan=plan,
                    cfg=listwise_buffer_config,
                    prefetch=prefetch,
                )
            if ascending:
                sorted_rows = list(reversed(sorted_rows))
            if limit is not None:
                sorted_rows = sorted_rows[:limit]
            result = df.iloc[
                [row["__global_idx__"] for row in sorted_rows]
            ].reset_index(drop=True)
            if need_explanation:
                # Merge tasks have been joined by execute_family. Explanations
                # are a separate phase, outside the satisfied prefix demand.
                control.limit = None
                control.stopped = False
                with self._execution_phase("explanation"):
                    explanations = await self._generate_ordering_explanations(
                        sorted_rows, user_instruction
                    )
                result = result.copy()
                result[
                    self._get_unique_explanation_column(result, "__orderby_explanation")
                ] = explanations
            return result
        except BaseException as exc:
            error = str(exc) or type(exc).__name__
            raise
        finally:
            control.stopped = True
            ACTIVE_CONTROL.reset(scope)
            wall = time.perf_counter() - started
            stats = RequestStats()
            for phase_stats in self._phase_stats:
                stats = stats + phase_stats
            self._last_execution_request_stats = stats.snapshot()
            self._last_execution_request_stats.elapsed_seconds = wall
            self._last_cost_metadata = dict(
                model_version=MODEL_VERSION,
                input_partition=input_partition,
                input_partition_seed=input_partition_seed,
                full_tail_correction=full_tail_correction,
                tail_cache_dir=tail_cache_dir,
                mc_samples=mc_samples,
                mc_seed=mc_seed,
                execution_mode=resolved_mode,
                cost_mode=plan.cost_mode if plan is not None else None,
                group_h=(
                    [[g.h for g in p] for p in plan.passes] if plan is not None else []
                ),
                prefetch=prefetch if resolved_mode == "buffer" else None,
                prefetch_policy=(
                    PREFETCH_POLICY if resolved_mode == "buffer" and prefetch else "none"
                ),
                requested_algorithm=requested["merge_algorithm"],
                parameter_policy=policy,
                effective_algorithm=selected.algorithm if selected else None,
                estimate=selected.to_dict() if selected else None,
                input_token_profile=profile.to_dict() if profile else None,
                submitted_calls=control.submitted_calls,
                submitted_items=control.submitted_items,
                speculative_calls=control.speculative_calls,
                speculative_items=control.speculative_items,
                retry_calls=control.retry_calls,
                retry_items=control.retry_items,
                request_stages=control.attempts,
                completed_stages=control.completed,
                returned_stages=control.returned,
                returned_input_tokens=sum(
                    row["input_tokens"] for row in control.returned.values()
                ),
                returned_output_tokens=sum(
                    row["output_tokens"] for row in control.returned.values()
                ),
                base_sort_input_tokens=(
                    self._phase_stats[0].input_tokens if self._phase_stats else 0
                ),
                predicted_total_input_tokens=(selected.input_tokens if selected else 0)
                + (self._phase_stats[0].input_tokens if self._phase_stats else 0),
                unknown_input_requests=sum(
                    row.get("unknown_input_requests", 0)
                    for row in control.returned.values()
                ),
                actual_input_tokens=(
                    stats.input_tokens
                    if not any(
                        row.get("unknown_input_requests", 0)
                        for row in control.returned.values()
                    )
                    else None
                ),
                h_policy=(
                    "fixed"
                    if selected and selected.h is not None
                    else "maximum_per_group"
                ),
            )
            emit_orderby_event(
                "execution_end",
                mode=resolved_mode,
                merge_algorithm=selected.algorithm if selected else merge_algorithm,
                effective_k=selected.k if selected else None,
                effective_h=selected.h if selected else None,
                effective_limit=(
                    len(result) if result is not None and limit is not None else None
                ),
                cost_model=self._last_cost_metadata,
                stats=self._last_execution_request_stats,
                wall_seconds=wall,
                error=error,
            )

    async def _generate_ordering_explanations(
        self,
        sorted_items: List[Dict[str, Any]],
        instruction: str,
    ) -> List[str]:
        if not sorted_items:
            return []

        async def compare_pair(idx: int):
            if idx == 0:
                return "Highest ranked according to the criterion.", idx
            item = sorted_items[idx]
            prev_item = sorted_items[idx - 1]
            comparison_result = await self._compare_two(item, prev_item, instruction)
            if comparison_result == "B":
                reason = f"Ranked lower than {prev_item.get('__global_idx__', 'previous item')}."
            else:
                reason = "Comparable to adjacent items."
            return reason, idx

        tasks = [asyncio.create_task(compare_pair(i)) for i in range(len(sorted_items))]
        results = await safe_gather(tasks)
        explanations = [""] * len(sorted_items)
        for reason, idx in results:
            explanations[idx] = reason
        return explanations
