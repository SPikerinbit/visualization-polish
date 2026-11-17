"""Sliding-window merge kernel and full / producer-tree execution drivers.

Both drivers share a sticky uniform-quota window and safe-prefix emission.
Optional evidence accumulates across listwise rounds inside each node;
optional balanced or progressive input ordering is gated on evidence.
Full mode materializes intermediate passes. Buffer mode overlaps adjacent
levels through bounded background pumps and closes them on early stop.
"""

from __future__ import annotations

import asyncio
import logging
import math
import random
import uuid
from collections import deque
from typing import Any, Deque, Dict, List, Optional, Tuple

from sema_prototype.physical_operator.orderby.merge._shared.producer import (
    BaseProducer,
)
from sema_prototype.physical_operator.orderby.merge._shared.evidence import (
    ListwiseBufferConfig,
    _SmallLimitEvidenceTable,
    normalize_evidence_config,
)
from sema_prototype.physical_operator.orderby._common import (
    ordering_call_scope,
    SW_REFRESH,
    record_sliding_window_merge_round,
)
from sema_prototype.llm.execution_control import check_query_active, note_output_ready

logger = logging.getLogger(__name__)

try:
    import scipy  # noqa: F401 - retained for the public compatibility flag.

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


def sliding_window_expected_emission(m: int, k: int) -> float:
    """Expected safe-prefix size for an equal-quota full merge window."""
    if m < 2:
        raise ValueError("Memory size m must be at least 2 for K-Way merge.")
    if k < 2 or k > m:
        raise ValueError(
            f"fan-in k must satisfy 2 <= k <= m; got m={m}, k={k}"
        )
    from .._shared.plan import sw_mu
    return sw_mu(k, m // k)


def sliding_window_log_objective(m: int, k: int) -> float:
    """Log of the k-dependent part of the relaxed full-ranking call model."""
    return -math.log(sliding_window_expected_emission(m, k)) - math.log(math.log(k))


def _balanced_groups(items: List[Any], fanout: int) -> List[List[Any]]:
    """Legacy balanced grouping helper; active execution uses the shared plan.

    Split into contiguous groups whose sizes differ by at most one. Kept for
    existing analysis and tests; it does not determine the execution layout.
    """
    n = len(items)
    if n <= fanout:
        return [list(items)]
    g = -(-n // fanout)
    base, rem = divmod(n, g)
    groups: List[List[Any]] = []
    idx = 0
    for gi in range(g):
        size = base + (1 if gi < rem else 0)
        groups.append(items[idx : idx + size])
        idx += size
    return groups


VALID_SHUFFLE_MODES = {"balanced", "progressive", "none"}


def _validate_refill_policy(refill_policy: str) -> None:
    if refill_policy != "uniform":
        raise ValueError(f"refill_policy must be 'uniform'; got {refill_policy!r}")


class StructuralMergeBuffer(BaseProducer):
    """Uniform-quota merge window with optional evidence and input shuffling."""

    def __init__(
        self,
        *,
        upstreams: List[BaseProducer],
        instruction: str,
        m: int,
        ranker: Any,
        use_evidence: bool = False,
        top_k: Optional[int] = None,
        shuffle_mode: str = "none",
        refill_policy: str = "uniform",
        buffer_cfg: Optional[ListwiseBufferConfig] = None,
        audit_context: Optional[Dict[str, Any]] = None,
        h: int | None = None,
    ) -> None:
        if not upstreams:
            raise ValueError("StructuralMergeBuffer requires at least one upstream.")
        if shuffle_mode not in VALID_SHUFFLE_MODES:
            raise ValueError(
                f"shuffle_mode must be one of {sorted(VALID_SHUFFLE_MODES)}; got {shuffle_mode!r}"
            )
        _validate_refill_policy(refill_policy)
        from .._shared.plan import MergeRequest

        MergeRequest(
            algorithm="sliding_window",
            m=m,
            limit=top_k,
            shuffle_mode=shuffle_mode,
            parameter_policy="none",
        )
        if len(upstreams) > m:
            raise ValueError("active SW inputs must fit within m")
        self._upstreams = upstreams
        self._instruction = instruction
        self._m = m
        self._ranker = ranker
        self._use_evidence = bool(use_evidence)
        self._top_k = top_k
        self._shuffle_mode = shuffle_mode
        self._refill_policy = refill_policy
        self._cfg = normalize_evidence_config(buffer_cfg, use_evidence=use_evidence)
        self._n = len(upstreams)
        if h is not None and (
            isinstance(h, bool) or not isinstance(h, int) or h < 1 or h * self._n > m
        ):
            raise ValueError("fixed SW quota must satisfy fan_in*h <= m")
        self._h = h
        self._needs_refill = False
        self._requested_output = 1

        # Pull sequence preserves upstream order in fast paths and progressive input.
        self._next_seq: List[int] = [0] * self._n
        self._upstream_done: List[bool] = [False] * self._n

        # Sticky working set.
        self._buffer: List[Dict[str, Any]] = []
        self._next_wid = 0

        # Evidence — None on the lightweight path.
        self._evidence: Optional[_SmallLimitEvidenceTable] = None
        if self._use_evidence:
            self._evidence = _SmallLimitEvidenceTable(
                confidence_target=self._cfg.min_pair_observations,
                id_field="__global_idx__",
            )

        # Streaming output state.
        self._pending_output: Deque[Dict[str, Any]] = deque()
        self._emitted_count = 0
        self._stall_count = 0
        self._last_ranked: List[Dict[str, Any]] = []
        self._initialized = False
        self._tail_started = False
        seed = self._cfg.seed if self._cfg is not None else None
        self._rng = random if seed is None else random.Random(seed)
        self._audit_context = dict(audit_context or {})
        self._audit_instance_id = uuid.uuid4().hex
        self._audit_round = 0

    # ------------------------------------------------------------------
    # BaseProducer API
    # ------------------------------------------------------------------

    async def next_candidates(self, k: int) -> List[Dict[str, Any]]:
        if k <= 0:
            return []
        if self._top_k is not None and self._emitted_count >= self._top_k:
            return []
        no_output_rounds = 0
        max_stall = max(20, self._m * 4)
        target_k = k
        if self._top_k is not None:
            target_k = min(target_k, self._top_k - self._emitted_count)
        self._requested_output = target_k
        while len(self._pending_output) < target_k and not self._fully_exhausted():
            prev_buf = len(self._buffer)
            prev_out = len(self._pending_output)
            await self._run_one_round()
            if (
                len(self._buffer) == prev_buf
                and len(self._pending_output) == prev_out
                and self._all_upstreams_drained()
            ):
                # Nothing changed and no further input can arrive — drain
                # whatever remains via a single safe_prefix emit before exit.
                if self._buffer and not self._pending_output:
                    await self._force_drain()
                break
            if len(self._pending_output) == prev_out:
                no_output_rounds += 1
                if no_output_rounds >= max_stall:
                    # Safe_prefix gate is permanently blocking — force-drain remaining buffer.
                    if self._buffer:
                        await self._force_drain()
                    break
            else:
                no_output_rounds = 0
        result: List[Dict[str, Any]] = []
        for _ in range(min(target_k, len(self._pending_output))):
            result.append(self._pending_output.popleft())
        self._emitted_count += len(result)
        return result

    def exhausted(self) -> bool:
        if self._top_k is not None and self._emitted_count >= self._top_k:
            return not self._pending_output
        return self._fully_exhausted() and not self._pending_output

    async def aclose(self) -> None:
        for up in self._upstreams:
            await up.aclose()

    # ------------------------------------------------------------------
    # Upstream pulls
    # ------------------------------------------------------------------

    async def _pull_from_upstream(
        self, i: int, n: int
    ) -> List[Tuple[int, Dict[str, Any]]]:
        """Fetch up to ``n`` items and assign monotonically increasing pull sequences."""
        if n <= 0 or self._upstream_done[i]:
            return []
        result: List[Tuple[int, Dict[str, Any]]] = []
        fresh = await self._upstreams[i].next_candidates(n)
        for raw in fresh:
            seq = self._next_seq[i]
            self._next_seq[i] += 1
            result.append((seq, raw))
        if self._upstreams[i].exhausted():
            self._upstream_done[i] = True
        elif not fresh:
            # Upstream returned nothing without exhausting — treat as done
            # to avoid spinning. In practice this only happens for buggy
            # upstreams; the existing tree producers never do this.
            self._upstream_done[i] = True
        self._tail_started |= self._upstream_done[i]
        return result

    def _upstream_has_supply(self, i: int) -> bool:
        return not self._upstream_done[i] and not self._upstreams[i].exhausted()

    def _all_upstreams_drained(self) -> bool:
        return not any(self._upstream_has_supply(i) for i in range(self._n))

    def _fully_exhausted(self) -> bool:
        if self._top_k is not None and self._emitted_count >= self._top_k:
            return True
        if self._buffer:
            return False
        return self._all_upstreams_drained()

    def _remaining_emit_capacity(self) -> Optional[int]:
        if self._top_k is None:
            return None
        return max(0, self._top_k - (self._emitted_count + len(self._pending_output)))

    def _append_output(self, item: Dict[str, Any]) -> bool:
        remaining = self._remaining_emit_capacity()
        if remaining is not None and remaining <= 0:
            return False
        self._pending_output.append(item)
        note_output_ready(1)
        return True

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    async def _initialize(self) -> None:
        await self._refill_to_targets(self._compute_targets(list(range(self._n))))
        self._initialized = True

    def _count_per_run(self) -> Dict[int, int]:
        counts: Dict[int, int] = {i: 0 for i in range(self._n)}
        for item in self._buffer:
            counts[int(item["__run_id__"])] += 1
        return counts

    def _compute_targets(self, active: List[int]) -> Dict[int, int]:
        """Give each active run ``max(1, m // n_active)`` window slots."""
        if not active:
            return {}
        h = self._h if self._h is not None else max(1, self._m // len(active))
        return {i: h for i in active}

    async def _refill_to_targets(self, targets: Dict[int, int]) -> None:
        """Pull from each run until buffer count reaches ``targets[i]``.

        Runs with exhausted upstreams cause a shortfall; the shortfall is
        compensated by drawing extra items from runs that still have
        available supply. This preserves the buffer at ~m total whenever
        possible while keeping safe_prefix valid (each run's contribution
        size is tracked from the buffer, not from the target).
        """
        if not targets:
            return
        counts = self._count_per_run()
        deficits: Dict[int, int] = {}
        for i, tgt in targets.items():
            need = tgt - counts.get(i, 0)
            if need > 0:
                deficits[i] = need
        if deficits:
            results = await asyncio.gather(
                *(self._pull_from_upstream(i, n) for i, n in deficits.items())
            )
            for i, pulled in zip(deficits.keys(), results):
                self._enqueue_pulled(i, pulled)

        if self._h is not None:
            return

        # Shortfall borrowing: if some target run failed to meet its quota
        # (its upstream is empty), draw extra items from donors that still
        # have supply. Cap at ``sum(targets)`` (= h * n_active) so we do
        # not grow the buffer past the algorithm's contract.
        target_total = sum(targets.values())
        while True:
            # Total buffer occupancy == sum of per-run counts == len(buffer).
            if len(self._buffer) >= target_total:
                return
            counts = self._count_per_run()
            donors = [
                i
                for i in range(self._n)
                if self._upstream_has_supply(i)
                and counts.get(i, 0) >= targets.get(i, 0)
            ]
            if not donors:
                return
            progress = False
            for i in donors:
                if len(self._buffer) >= target_total:
                    return
                pulled = await self._pull_from_upstream(i, 1)
                if pulled:
                    self._enqueue_pulled(i, pulled)
                    progress = True
            if not progress:
                return

    def _enqueue_pulled(
        self, run_id: int, pulled: List[Tuple[int, Dict[str, Any]]]
    ) -> None:
        for seq, raw in pulled:
            ic = dict(raw)
            ic["__run_id__"] = run_id
            ic["__pull_seq__"] = seq
            ic["__window_item_id__"] = self._next_wid
            self._next_wid += 1
            self._buffer.append(ic)

    # ------------------------------------------------------------------
    # Main round
    # ------------------------------------------------------------------

    async def _run_one_round(self) -> None:
        check_query_active()
        if not self._initialized:
            await self._initialize()
        elif self._needs_refill:
            counts = self._count_per_run()
            active = [
                i
                for i in range(self._n)
                if counts.get(i, 0) > 0 or self._upstream_has_supply(i)
            ]
            await self._refill_to_targets(self._compute_targets(active))
            self._needs_refill = False
        if not self._buffer:
            return

        # 1. Single-run fast path: buffer holds only one run's items and
        #    upstream supply for other runs is dead → emit buffer in its
        #    current sorted order (already produced by upstream).
        counts = self._count_per_run()
        non_empty_runs = [i for i, c in counts.items() if c > 0]
        if len(non_empty_runs) == 1 and not any(
            self._upstream_has_supply(i)
            for i in range(self._n)
            if i not in non_empty_runs
        ):
            await self._fast_path_single_run(non_empty_runs[0])
            self._needs_refill = True
            return

        # 2. Build listwise input via shuffle policy.
        batch = self._prepare_listwise_input()
        self._audit_round += 1

        # 3. Evidence pre-rank bookkeeping (positions).
        if self._evidence is not None:
            self._evidence.sync_pool(batch)
            self._evidence.record_input_positions(
                [str(item["__global_idx__"]) for item in batch]
            )

        # 4. Listwise rank.
        stage = (
            "sw_init"
            if self._audit_round == 1
            else (
                "sw_tail_refresh"
                if self._tail_started
                else SW_REFRESH
            )
        )
        with ordering_call_scope(stage):
            ordered = await self._ranker._rank_sliding_window_batch(
                batch, self._instruction
            )
        self._last_ranked = list(ordered)

        # 5. Evidence post-rank bookkeeping (pairwise wins).
        if self._evidence is not None:
            self._evidence.record_ranking(
                [str(item["__global_idx__"]) for item in ordered],
                update_anchor=True,
                record_pairwise=True,
            )

        # 6. Compute emit set using safe_prefix ∩ confident_prefix gates.
        #    Reuse the per-run counts from step 1 — the buffer is not mutated
        #    between there and here (steps 2-5 only read/rank).
        safe_prefix = self._compute_safe_prefix(ordered, counts)
        emit_set = self._emit_with_gates(ordered, counts, safe_prefix=safe_prefix)
        upstream_has_supply = {
            str(i): bool(self._upstream_has_supply(i)) for i in range(self._n)
        }
        expected_h = self._h if self._h is not None else max(1, self._m // max(1, len(non_empty_runs)))
        is_full_window = len(non_empty_runs) == self._n and all(
            counts.get(i, 0) == expected_h for i in range(self._n)
        )
        is_boundary_round = not all(upstream_has_supply.values())
        record_sliding_window_merge_round(
            {
                **self._audit_context,
                "event": "listwise_round",
                "merge_instance_id": self._audit_instance_id,
                "round_index": self._audit_round,
                "tail_active": self._tail_started,
                "configured_m": self._m,
                "effective_fan_in": self._n,
                "refill_policy": self._refill_policy,
                "shuffle_mode": self._shuffle_mode,
                "quota_by_run": {str(i): int(counts.get(i, 0)) for i in range(self._n)},
                "window_size": len(batch),
                "input_run_ids": [int(item["__run_id__"]) for item in batch],
                "output_run_ids": [int(item["__run_id__"]) for item in ordered],
                "safe_prefix_run_ids": [
                    int(item["__run_id__"]) for item in safe_prefix
                ],
                "safe_prefix_len": len(safe_prefix),
                "emitted_prefix_len": len(emit_set),
                "upstream_has_supply": upstream_has_supply,
                "is_full_window": is_full_window,
                "is_boundary_round": is_boundary_round,
                "is_interior_window": is_full_window and not is_boundary_round,
            }
        )
        emit_wids = {item["__window_item_id__"] for item in emit_set}

        # 7. Apply emit: evict from evidence, remove from buffer, queue output.
        for item in emit_set:
            if self._evidence is not None:
                self._evidence.evict(str(item["__global_idx__"]))
        if emit_wids:
            self._buffer = [
                it for it in self._buffer if it["__window_item_id__"] not in emit_wids
            ]
            for item in emit_set:
                if not self._append_output(self._strip_metadata(item)):
                    break

        # Refill only when another demanded round begins.
        self._needs_refill = True

        # 9. Stall accounting.
        if self._use_evidence:
            if emit_set:
                self._stall_count = 0
            else:
                self._stall_count += 1

        # 10. Trim _last_ranked to items still in buffer (for progressive shuffle).
        kept_wids = {it["__window_item_id__"] for it in self._buffer}
        self._last_ranked = [
            it for it in self._last_ranked if it["__window_item_id__"] in kept_wids
        ]

    async def _fast_path_single_run(self, run_id: int) -> None:
        """All remaining items belong to a single run with no upstream cross-
        traffic — emit the buffer in its natural sorted order without a
        further listwise call."""
        run_items = sorted(
            (it for it in self._buffer if int(it["__run_id__"]) == run_id),
            key=lambda it: int(it["__pull_seq__"]),
        )
        record_sliding_window_merge_round(
            {
                **self._audit_context,
                "event": "single_run_fast_path",
                "merge_instance_id": self._audit_instance_id,
                "round_index": self._audit_round,
                "configured_m": self._m,
                "effective_fan_in": self._n,
                "run_id": int(run_id),
                "emitted_prefix_len": len(run_items),
            }
        )
        for item in run_items:
            if self._evidence is not None:
                self._evidence.evict(str(item["__global_idx__"]))
            if not self._append_output(self._strip_metadata(item)):
                return
        run_wids = {it["__window_item_id__"] for it in run_items}
        self._buffer = [
            it for it in self._buffer if it["__window_item_id__"] not in run_wids
        ]
        # Drain remaining upstream into output directly.
        while (
            self._upstream_has_supply(run_id)
            and len(self._pending_output) < self._requested_output
        ):
            need = self._requested_output - len(self._pending_output)
            pulled = await self._pull_from_upstream(run_id, min(16, need))
            if not pulled:
                break
            for _seq, raw in pulled:
                ic = dict(raw)
                if self._evidence is not None:
                    self._evidence.evict(str(ic["__global_idx__"]))
                if not self._append_output(ic):
                    return

    async def _force_drain(self) -> None:
        """Last-resort drain: emit remaining buffer via a final safe_prefix
        pass without a fresh listwise call (uses last_ranked if available)."""
        if not self._buffer:
            return
        if self._last_ranked:
            buf_wids = {it["__window_item_id__"] for it in self._buffer}
            ordered = [
                it for it in self._last_ranked if it["__window_item_id__"] in buf_wids
            ]
            # Anything in buffer not in last_ranked is appended in arrival order.
            seen = {it["__window_item_id__"] for it in ordered}
            for it in self._buffer:
                if it["__window_item_id__"] not in seen:
                    ordered.append(it)
        else:
            ordered = sorted(
                self._buffer,
                key=lambda it: (int(it["__run_id__"]), int(it["__pull_seq__"])),
            )
        for item in ordered:
            if self._evidence is not None:
                self._evidence.evict(str(item["__global_idx__"]))
            if not self._append_output(self._strip_metadata(item)):
                break
        self._buffer = []
        self._last_ranked = []

    # ------------------------------------------------------------------
    # Emit gates
    # ------------------------------------------------------------------

    def _emit_with_gates(
        self,
        ordered: List[Dict[str, Any]],
        counts_in_buffer: Dict[int, int],
        *,
        safe_prefix: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        safe = (
            list(safe_prefix)
            if safe_prefix is not None
            else self._compute_safe_prefix(ordered, counts_in_buffer)
        )
        if not safe:
            return []
        if not self._use_evidence or self._evidence is None:
            return list(safe)
        confident = self._compute_confident_prefix(safe, ordered)
        if confident:
            return confident
        # Stall override: too many rounds with no progress → drop confidence
        # gate this round so safe_prefix can move forward.
        if self._stall_count >= self._cfg.max_stall_rounds:
            logger.info(
                "[AUDIT StructuralMergeBuffer] Stall threshold (%s) reached; "
                "degrading to safe_prefix emit (size=%s).",
                self._cfg.max_stall_rounds,
                len(safe),
            )
            return list(safe)
        return []

    def _compute_safe_prefix(
        self, ordered: List[Dict[str, Any]], counts_in_buffer: Dict[int, int]
    ) -> List[Dict[str, Any]]:
        emitted: Dict[int, int] = {i: 0 for i in counts_in_buffer}
        commit_count = len(ordered)
        for pos, item in enumerate(ordered):
            run_id = int(item["__run_id__"])
            emitted[run_id] = emitted.get(run_id, 0) + 1
            in_buf = counts_in_buffer.get(run_id, 0)
            if in_buf > 0 and emitted[run_id] >= in_buf:
                # If this run has no further supply, safe_prefix can extend
                # past the boundary (no cross-run order can be violated by a
                # never-arriving item). Otherwise truncate at this position.
                if self._upstream_has_supply(run_id):
                    commit_count = pos + 1
                    break
        return ordered[:commit_count]

    def _compute_confident_prefix(
        self,
        safe_prefix: List[Dict[str, Any]],
        ordered: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        assert self._evidence is not None
        emit: List[Dict[str, Any]] = []
        emit_wids: set[int] = set()
        for x in safe_prefix:
            x_id = str(x["__global_idx__"])
            x_wid = x["__window_item_id__"]
            confident = True
            for y in ordered:
                y_wid = y["__window_item_id__"]
                if y_wid == x_wid or y_wid in emit_wids:
                    continue
                y_id = str(y["__global_idx__"])
                if not self._evidence.pair_confident(
                    x_id,
                    y_id,
                    min_observations=self._cfg.min_pair_observations,
                    beta_confidence=self._cfg.beta_confidence,
                ):
                    confident = False
                    break
            if not confident:
                break
            emit.append(x)
            emit_wids.add(x_wid)
        return emit

    # ------------------------------------------------------------------
    # Shuffle policies
    # ------------------------------------------------------------------

    def _prepare_listwise_input(self) -> List[Dict[str, Any]]:
        # Without evidence the merge must be deterministic and
        # schedule-independent: the window is the buffer in arrival order, no
        # shuffle. The shuffle path uses a process-global RNG whose draw order
        # depends on the execution schedule (full-mode rebuilds a buffer per
        # round; buffer-mode keeps nodes resident), so shuffling here would make
        # the two modes diverge. Shuffling is only meaningful when evidence
        # accumulates across rounds (use_evidence=True), so it is gated on that.
        if self._evidence is None:
            return list(self._buffer)
        if self._shuffle_mode == "none":
            return list(self._buffer)
        if self._shuffle_mode == "progressive":
            return self._progressive_input()
        return self._balanced_shuffle()

    def _progressive_input(self) -> List[Dict[str, Any]]:
        if not self._last_ranked:
            return list(self._buffer)
        buf_index = {it["__window_item_id__"]: it for it in self._buffer}
        retained: List[Dict[str, Any]] = []
        retained_wids: set[int] = set()
        for it in self._last_ranked:
            wid = it["__window_item_id__"]
            if wid in buf_index:
                retained.append(buf_index[wid])
                retained_wids.add(wid)
        new_items = [
            it for it in self._buffer if it["__window_item_id__"] not in retained_wids
        ]
        if not new_items:
            return retained or list(self._buffer)
        # For each new item, its insertion point is "after the lowest-ranked
        # retained item from the same run". Group + sort new items by run, then
        # splice at the recorded position. Runs with no retained item go to
        # the tail.
        new_by_run: Dict[int, List[Dict[str, Any]]] = {}
        for it in new_items:
            new_by_run.setdefault(int(it["__run_id__"]), []).append(it)
        for items in new_by_run.values():
            items.sort(key=lambda x: int(x["__pull_seq__"]))
        run_last_pos: Dict[int, int] = {}
        for pos, it in enumerate(retained):
            run_last_pos[int(it["__run_id__"])] = pos
        insertions: Dict[int, List[Dict[str, Any]]] = {}
        tail_items: List[Dict[str, Any]] = []
        for run_id in sorted(new_by_run.keys()):
            run_items = new_by_run[run_id]
            anchor = run_last_pos.get(run_id)
            if anchor is None:
                tail_items.extend(run_items)
            else:
                insertions.setdefault(anchor + 1, []).extend(run_items)
        out: List[Dict[str, Any]] = []
        for pos, it in enumerate(retained):
            out.append(it)
            if (pos + 1) in insertions:
                out.extend(insertions[pos + 1])
        out.extend(tail_items)
        return out

    def _balanced_shuffle(self) -> List[Dict[str, Any]]:
        # Only reached on the evidence path (see _prepare_listwise_input).
        assert self._evidence is not None
        batch = list(self._buffer)
        if len(batch) <= 1:
            return batch
        bucket_order = ("head", "mid", "tail")
        capacities = dict(zip(bucket_order, self._evidence._bucket_sizes(len(batch))))
        assignments: Dict[str, List[Dict[str, Any]]] = {b: [] for b in bucket_order}
        remaining = list(batch)
        self._rng.shuffle(remaining)
        for item in remaining:
            rid = str(item["__global_idx__"])
            available = [b for b in bucket_order if len(assignments[b]) < capacities[b]]
            if not available:
                break
            min_count = min(self._evidence.position_count(rid, b) for b in available)
            tied = [
                b
                for b in available
                if self._evidence.position_count(rid, b) == min_count
            ]
            target = self._rng.choice(tied)
            assignments[target].append(item)
        shuffled: List[Dict[str, Any]] = []
        for b in bucket_order:
            bucket_items = list(assignments[b])
            self._rng.shuffle(bucket_items)
            shuffled.extend(bucket_items)
        return shuffled

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_metadata(item: Dict[str, Any]) -> Dict[str, Any]:
        drop = {"__run_id__", "__window_item_id__", "__pull_seq__"}
        return {k: v for k, v in item.items() if k not in drop}


def build_structural_merge_producer_tree(
    sorted_runs,
    *,
    instruction,
    m,
    k,
    ranker,
    use_evidence=False,
    top_k=None,
    shuffle_mode="none",
    refill_policy="uniform",
    buffer_cfg=None,
    h=None,
):
    """Build from the same resolved layout as materialized execution."""
    from .._shared.plan import MergeRequest, InputTokenProfile, resolve_merge_plan
    from .._shared.runtime import build_family_tree

    _validate_refill_policy(refill_policy)
    if top_k == 0:
        return None
    request = MergeRequest(
        algorithm="sliding_window",
        k=k,
        h=h,
        m=m,
        limit=top_k,
        mode="buffer",
        parameter_policy="none",
        profile=InputTokenProfile(0, 1),
        use_evidence=use_evidence,
        shuffle_mode=shuffle_mode,
    )
    plan = resolve_merge_plan(tuple(map(len, sorted_runs)), request)
    return build_family_tree(
        ranker,
        sorted_runs,
        instruction,
        plan=plan,
        cfg=buffer_cfg,
    )


async def structural_merge_full(
    sorted_runs,
    *,
    instruction,
    m,
    k,
    top_k,
    ranker,
    use_evidence=False,
    shuffle_mode="none",
    refill_policy="uniform",
    buffer_cfg=None,
    h=None,
):
    from .. import merge_runs

    _validate_refill_policy(refill_policy)
    return await merge_runs(
        ranker,
        sorted_runs,
        instruction,
        algorithm="sliding_window",
        k=k,
        h=h,
        m=m,
        limit=top_k,
        mode="full",
        parameter_policy="none",
        use_evidence=use_evidence,
        shuffle_mode=shuffle_mode,
        cfg=buffer_cfg,
    )


class SlidingWindowMixin:
    async def _rank_sliding_window_batch(
        self,
        batch: List[Dict[str, Any]],
        instruction: str,
    ) -> List[Dict[str, Any]]:
        return await self._dialect_rank_listwise(
            batch, instruction, desc="SlidingWindow-Merge", retries=3
        )

    async def _sliding_window_merge(
        self, sorted_runs, instruction, m, k=6, top_k=None, *, h=None
    ):
        from .. import merge_runs

        return await merge_runs(
            self,
            sorted_runs,
            instruction,
            algorithm="sliding_window",
            k=k,
            h=h,
            m=m,
            limit=top_k,
            mode="buffer",
            parameter_policy="none",
        )

    def build_sliding_window_root_producer(
        self,
        sorted_runs,
        *,
        instruction,
        m,
        k,
        top_k=None,
        use_evidence=False,
        shuffle_mode="none",
        buffer_cfg=None,
        h=None,
    ):
        return build_structural_merge_producer_tree(
            sorted_runs,
            instruction=instruction,
            m=m,
            k=k,
            ranker=self,
            top_k=top_k,
            use_evidence=use_evidence,
            shuffle_mode=shuffle_mode,
            buffer_cfg=buffer_cfg,
            h=h,
        )

    async def _sliding_window_full_merge(
        self, sorted_runs, instruction, m, k=6, top_k=None, *, h=None
    ):
        return await structural_merge_full(
            sorted_runs,
            instruction=instruction,
            m=m,
            k=k,
            h=h,
            top_k=top_k,
            ranker=self,
        )

    async def _structural_sort_merge(
        self,
        sorted_runs,
        instruction,
        *,
        m,
        k,
        top_k,
        mode,
        use_evidence=False,
        shuffle_mode="none",
        refill_policy="uniform",
        buffer_cfg=None,
        h=None,
    ):
        from .. import merge_runs

        _validate_refill_policy(refill_policy)
        return await merge_runs(
            self,
            sorted_runs,
            instruction,
            algorithm="sliding_window",
            k=k,
            h=h,
            m=m,
            limit=top_k,
            mode=mode,
            parameter_policy="none",
            use_evidence=use_evidence,
            shuffle_mode=shuffle_mode,
            cfg=buffer_cfg,
        )
