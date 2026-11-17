"""Candidate preparation, LLM ranking, and opt-in execution observations."""

from __future__ import annotations
import asyncio
import contextlib
import contextvars
import logging
from typing import Any, Callable, Dict, Iterator, List, Mapping, Tuple
import pandas as pd
from sema_prototype.llm.orderby_dialect import get_active_dialect
from sema_prototype.llm.prompt_permutation import permute_listwise_items

logger = logging.getLogger(__name__)
ORDERBY_RAW_CONTENT_FIELD = "__orderby_raw_content__"
BASE_SORT = "phase1_base_sort"
SW_REFRESH = "sw_window_refresh"
LT_INIT = "lt_init"
LT_PATH_REFRESH = "lt_path_refresh"
MERGE_OTHER = "merge_other"
PATH_REFRESH_STAGES = {LT_PATH_REFRESH}
REFRESH_STAGES = {SW_REFRESH, *PATH_REFRESH_STAGES}
_ACTIVE_STAGE: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "sema_ordering_consistency_stage", default=None
)
Observer = Callable[[str, Mapping[str, Any]], None]
_OBSERVERS: contextvars.ContextVar[tuple[Observer, ...]] = contextvars.ContextVar(
    "sema_orderby_observers", default=()
)


@contextlib.contextmanager
def orderby_observer_context(observer: Observer) -> Iterator[None]:
    observers = _OBSERVERS.get()
    token = _OBSERVERS.set(
        observers if observer in observers else (*observers, observer)
    )
    try:
        yield
    finally:
        _OBSERVERS.reset(token)


def emit_orderby_event(event: str, **payload: Any) -> None:
    for observer in _OBSERVERS.get():
        observer(event, payload)


@contextlib.contextmanager
def ordering_call_scope(stage: str) -> Iterator[None]:
    token = _ACTIVE_STAGE.set(str(stage))
    try:
        yield
    finally:
        _ACTIVE_STAGE.reset(token)


def record_listwise_ranking(*, prompt_items, ordered_items, desc: str) -> None:
    emit_orderby_event(
        "listwise_ranking",
        prompt_items=prompt_items,
        ordered_items=ordered_items,
        desc=desc,
    )


def record_merge_pass(**values: Any) -> None:
    emit_orderby_event("merge_pass", **values)


def record_sliding_window_merge_round(record: Mapping[str, Any]) -> None:
    emit_orderby_event("merge_round", record=record)


class OrderbyPayloadMixin:
    def _create_sentinel_item(self, run_idx: int) -> Dict[str, Any]:
        return {
            "id": f"sentinel_{run_idx}",
            "content": None,
            "run_idx": run_idx,
            "is_sentinel": True,
        }

    def _prepare_rows(
        self,
        df: pd.DataFrame,
        instruction: str,
    ) -> list[dict[str, Any]]:
        # The benchmark's hidden raw-content contract is already fully
        # resolved, so no instruction-to-column inference should run (or leak a
        # visible column name) on that path.
        ranking_columns = (
            None
            if ORDERBY_RAW_CONTENT_FIELD in df.columns
            else self._resolve_columns(instruction, df)
        )
        rows: list[dict[str, Any]] = []
        for pos, (_idx, row) in enumerate(df.iterrows()):
            row_dict = row.to_dict()
            raw_content = row_dict.get(ORDERBY_RAW_CONTENT_FIELD)
            content = (
                str(raw_content)
                if isinstance(raw_content, str)
                else self._build_row_content(row_dict, ranking_columns)
            )
            rows.append(
                {
                    **row_dict,
                    # Keep positional index so downstream df.iloc[...] stays valid
                    # even when the DataFrame carries non-contiguous labels.
                    "__global_idx__": pos,
                    "content": content,
                }
            )
        return rows

    def _build_row_content(
        self,
        row: Dict[str, Any],
        columns: List[str] | None = None,
    ) -> str:
        visible_columns = columns or [
            key for key in row.keys() if not str(key).startswith("__")
        ]
        if not visible_columns:
            visible_columns = [
                key for key in row.keys() if not str(key).startswith("__")
            ]
        lines = []
        for column in visible_columns:
            if column in row:
                lines.append(f"{column}: {row[column]}")
        return "\n".join(lines)

    def _ensure_item_content(self, item: Dict[str, Any]) -> str:
        content = item.get("content")
        # An explicitly prepared string is authoritative even when empty.
        # Falling through would reconstruct it as ``text: `` and violate the
        # benchmark's byte-exact content-only contract.
        if isinstance(content, str):
            return content
        visible = {
            key: value
            for key, value in item.items()
            if not str(key).startswith("__")
            and key not in {"id", "run_idx", "is_sentinel", "content"}
        }
        return self._build_row_content(visible)


def _stamp_base_sort_rank(chunk: List[Dict[str, Any]]) -> None:
    """Stamp each item with its 0-indexed rank within this base-sort chunk.

    The stamp is retained for experiment adapters and base-sort provenance.
    """
    for rank, item in enumerate(chunk):
        item["__base_sort_rank__"] = rank


async def safe_gather(tasks: List[asyncio.Task]):
    try:
        return await asyncio.gather(*tasks)
    except Exception as exc:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.error("[FATAL] LLM concurrency group aborted due to exception: %s", exc)
        raise RuntimeError("LLM execution fast-failed to prevent token drain.") from exc


from sema_prototype.llm.execution_control import ranking_work


class OrderbyRankingMixin:
    async def _listwise_sort(
        self,
        items: List[Dict[str, Any]],
        instruction: str,
        m: int = 12,
    ) -> Tuple[List[Dict[str, Any]], List[List[Dict[str, Any]]]]:
        if len(items) <= m:
            sorted_chunk = await self._llm_listwise_sort(items, instruction)
            _stamp_base_sort_rank(sorted_chunk)
            return sorted_chunk, [sorted_chunk]

        chunks = [items[i : i + m] for i in range(0, len(items), m)]

        async def process_chunk(chunk):
            if len(chunk) >= 2:
                return await self._llm_listwise_sort(chunk, instruction)
            return chunk

        tasks = [asyncio.create_task(process_chunk(chunk)) for chunk in chunks]
        sorted_chunks = await safe_gather(tasks)
        for chunk in sorted_chunks:
            _stamp_base_sort_rank(chunk)
        flattened = [item for chunk in sorted_chunks for item in chunk]
        return flattened, list(sorted_chunks)

    async def _dialect_rank_listwise(
        self,
        items: List[Dict[str, Any]],
        instruction: str,
        *,
        desc: str,
        retries: int = 5,
    ) -> List[Dict[str, Any]]:
        """Rank *items* BEST→WORST via the active orderby dialect.

        The dialect owns serialization, prompt shell, structured-output schema
        and parsing (which always normalizes to 0-based BEST→WORST positions and
        repairs into a full permutation). The structured ``response_format``
        still constrains decoding, so this is the single listwise entry point
        every base-sort / merge call routes through.
        """
        n = len(items)
        if n <= 1:
            return list(items)
        for attempt in range(retries):
            try:
                # Apply inside the retry loop so the experiment audit contains
                # one record for every actual LLM invocation. Stable-hash mode
                # returns the same order for retries of the same candidate set.
                prompt_items = permute_listwise_items(items, stage=desc)
                texts = [self._ensure_item_content(item) for item in prompt_items]
                spec = get_active_dialect().listwise(texts, instruction)
                with ranking_work(
                    n,
                    _ACTIVE_STAGE.get()
                    or (BASE_SORT if desc == "Listwise-BaseSort" else desc),
                    retry=attempt > 0,
                ):
                    responses = await self._execute_orderby_batch(
                        [spec.messages],
                        desc=desc,
                        response_format=spec.response_format,
                    )
                raw_response = responses[0]
                if not raw_response:
                    raise ValueError("Empty response from LLM.")
                order = spec.parse(raw_response)
                ordered_items = [prompt_items[pos] for pos in order]
                record_listwise_ranking(
                    prompt_items=prompt_items,
                    ordered_items=ordered_items,
                    desc=desc,
                )
                return ordered_items
            except Exception as exc:
                logger.warning(
                    "[AUDIT WARN] Listwise rank failed (%s, attempt %s/%s): %s",
                    desc,
                    attempt + 1,
                    retries,
                    exc,
                )
                await asyncio.sleep(2 ** min(attempt, 4))

        raise RuntimeError(f"FATAL: listwise rank ({desc}) collapsed after retries.")

    async def _llm_listwise_sort(
        self,
        chunk: List[Dict[str, Any]],
        instruction: str,
        retries: int = 5,
    ) -> List[Dict[str, Any]]:
        return await self._dialect_rank_listwise(
            chunk, instruction, desc="Listwise-BaseSort", retries=retries
        )

    async def _compare_two(
        self, item_a: Dict[str, Any], item_b: Dict[str, Any], instruction: str
    ) -> str:
        spec = get_active_dialect().pairwise(
            self._ensure_item_content(item_a),
            self._ensure_item_content(item_b),
            instruction,
        )

        for attempt in range(3):
            try:
                responses = await self._execute_orderby_batch(
                    [spec.messages],
                    desc="PairCompare",
                    response_format=spec.response_format,
                )
                raw_response = responses[0]
                if not raw_response:
                    raise ValueError("Empty response from LLM.")
                return spec.parse(raw_response)
            except Exception as exc:
                logger.warning(
                    "[AUDIT WARN] Compare failed (Attempt %s/3): %s",
                    attempt + 1,
                    exc,
                )
                await asyncio.sleep(1)

        raise RuntimeError("FATAL: Pairwise comparison failed after all retries.")
