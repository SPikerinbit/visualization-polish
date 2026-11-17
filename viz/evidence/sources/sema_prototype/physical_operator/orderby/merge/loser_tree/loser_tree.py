from __future__ import annotations

import asyncio
import logging
import math
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Dict, List, Tuple

from sema_prototype.physical_operator.orderby.merge._shared.producer import (
    BaseProducer,
    QueueProducer,
)
from sema_prototype.physical_operator.orderby.merge._shared.evidence import (
    ListwiseBufferConfig,
    TreeListwiseBuffer,
    normalize_evidence_config,
)
from sema_prototype.physical_operator.orderby._common import (
    LT_INIT,
    LT_PATH_REFRESH,
    ordering_call_scope,
)
from sema_prototype.physical_operator.orderby._common import record_merge_pass
from sema_prototype.physical_operator.orderby._common import safe_gather

from .._shared.plan import init_plan
from sema_prototype.llm.execution_control import check_query_active, note_output_ready

logger = logging.getLogger(__name__)

_POOL_META_KEYS = {"__run_id__", "__window_item_id__", "__small_limit_id__"}


@dataclass
class _PointerSegmentNode:
    """Persistent state for one pointer-guided segmented loser-tree node.

    Leaves retain only their run identity.  Internal nodes retain exactly the
    two objects described by the paper: a real-item ``loser`` segment and the
    child ``pointer`` whose replay slot exhausted first.  Missing tail items
    are represented by virtual +infinity slots during replay, never by stored
    rows and never in an LLM request.
    """

    node_id: int
    left: int = -1
    right: int = -1
    run_idx: int | None = None
    loser: List[Dict[str, Any]] = field(default_factory=list)
    pointer: int | None = None

    @property
    def is_leaf(self) -> bool:
        return self.run_idx is not None


@dataclass(frozen=True)
class _SegmentReplayResult:
    """Result of one deterministic ``ReplaySegmentNode`` operation."""

    winner: List[Dict[str, Any]]
    loser: List[Dict[str, Any]]
    pointer: int
    pointer_side: str
    left_virtual: int
    right_virtual: int


def _preserve_segment_run_order(
    ranked: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Return the closest ranked order that preserves every input-run chain.

    A listwise model may contradict the already established order within one
    input run.  Segment replay must remain a merge of those runs, so only each
    run's current head is eligible at a time.  Among eligible heads we retain
    the model's rank.  With a consistent rank map this is an identity
    operation; with an inconsistent one it produces a stable linear extension
    without adding persistent tree state.
    """
    if len(ranked) <= 1:
        return list(ranked)

    rank_positions = {
        int(item["__window_item_id__"]): index for index, item in enumerate(ranked)
    }
    chains: Dict[int, List[Dict[str, Any]]] = {}
    for item in ranked:
        chains.setdefault(int(item["__run_id__"]), []).append(item)
    for chain in chains.values():
        chain.sort(key=lambda item: int(item["__window_item_id__"]))

    cursors = {run_id: 0 for run_id in chains}
    linearized: List[Dict[str, Any]] = []
    while len(linearized) < len(ranked):
        eligible = [
            chain[cursors[run_id]]
            for run_id, chain in chains.items()
            if cursors[run_id] < len(chain)
        ]
        selected = min(
            eligible,
            key=lambda item: rank_positions[int(item["__window_item_id__"])],
        )
        linearized.append(selected)
        cursors[int(selected["__run_id__"])] += 1
    return linearized


def _replay_segment_node(
    left: List[Dict[str, Any]],
    right: List[Dict[str, Any]],
    positions: Dict[int, int],
    *,
    h: int,
    left_child: int,
    right_child: int,
) -> _SegmentReplayResult:
    """Replay one segment match using real rows plus implicit tail sentinels.

    ``left`` and ``right`` are replay slots, not claims about an item's
    original run.  Each slot is logically padded to ``h`` with +infinity.  The
    padding is materialized only as ``None`` tags below, so it cannot enter a
    prompt, receive metadata, or escape as output.
    """
    if h <= 0:
        raise ValueError("Segment replay requires h >= 1")
    if len(left) > h or len(right) > h:
        raise RuntimeError(
            "Segment replay input exceeds h: "
            f"left={len(left)} right={len(right)} h={h}"
        )

    real_ids = [int(item["__window_item_id__"]) for item in (*left, *right)]
    if len(real_ids) != len(set(real_ids)):
        raise RuntimeError("Segment replay inputs contain duplicate items")
    missing = [item_id for item_id in real_ids if item_id not in positions]
    if missing:
        raise RuntimeError(
            "Segment replay rank map omitted input items: " f"count={len(missing)}"
        )

    return _replay_validated_segment(
        left, right, positions, h=h, left_child=left_child, right_child=right_child
    )


def _replay_validated_segment(
    left, right, positions, *, h, left_child, right_child
) -> _SegmentReplayResult:
    """Pure match after request validation and the window's permutation check."""
    tagged: List[Tuple[Dict[str, Any] | None, int]] = [
        *((item, 0) for item in left),
        *((item, 1) for item in right),
    ]
    tagged.sort(
        key=lambda tagged_item: positions[int(tagged_item[0]["__window_item_id__"])]
    )
    left_virtual = h - len(left)
    right_virtual = h - len(right)
    logical = [
        *tagged,
        *((None, 0) for _ in range(left_virtual)),
        *((None, 1) for _ in range(right_virtual)),
    ]

    counts = [0, 0]
    for _item, side in logical:
        counts[side] += 1
        if counts[side] == h:
            break

    winner = [item for item, _side in logical[:h] if item is not None]
    loser = [item for item, _side in logical[h:] if item is not None]
    pointer = left_child if side == 0 else right_child
    return _SegmentReplayResult(
        winner=winner,
        loser=loser,
        pointer=pointer,
        pointer_side="left" if side == 0 else "right",
        left_virtual=left_virtual,
        right_virtual=right_virtual,
    )


class LoserTreeMixin:
    @staticmethod
    def _loser_tree_compute_params(m: int, k: int) -> Tuple[int, int]:
        """Return ``(d, h)`` for tree depth and per-frontier segment size."""
        if k <= 1:
            return 1, max(1, m)
        d = max(1, math.ceil(math.log2(k)))
        h = max(1, m // (1 + d))
        return d, h

    @staticmethod
    def _loser_tree_build_topology(
        n_leaves: int,
    ) -> Tuple[
        Dict[int, int],
        Dict[int, int],
        Dict[int, int],
        Dict[int, List[int]],
        int,
    ]:
        """Build an exact binary topology without power-of-two padding.

        Returns ``(left, right, leaf_to_run, path_of_leaf, root)``. Paths list
        internal nodes from the leaf parent to the root and remain part of the
        compatibility/testing interface; production refresh follows the
        dynamic ``pointer`` chain instead.
        """
        if n_leaves <= 0:
            raise ValueError("n_leaves must be positive")

        left_children: Dict[int, int] = {}
        right_children: Dict[int, int] = {}
        parents: Dict[int, int] = {}
        leaf_to_run: Dict[int, int] = {}
        run_to_leaf: Dict[int, int] = {}
        counter = [0]

        def build(lo: int, hi: int) -> int:
            node_id = counter[0]
            counter[0] += 1
            if lo == hi:
                leaf_to_run[node_id] = lo
                run_to_leaf[lo] = node_id
                left_children[node_id] = -1
                right_children[node_id] = -1
                return node_id
            mid = (lo + hi) // 2
            left_id = build(lo, mid)
            right_id = build(mid + 1, hi)
            left_children[node_id] = left_id
            right_children[node_id] = right_id
            parents[left_id] = node_id
            parents[right_id] = node_id
            return node_id

        root = build(0, n_leaves - 1)
        parents[root] = -1

        path_of_leaf: Dict[int, List[int]] = {}
        for run_idx in range(n_leaves):
            node = parents.get(run_to_leaf[run_idx], -1)
            path: List[int] = []
            while node != -1:
                path.append(node)
                node = parents.get(node, -1)
            path_of_leaf[run_idx] = path

        return left_children, right_children, leaf_to_run, path_of_leaf, root

    async def _loser_tree_stream_generator(
        self,
        leaf_sources: List[BaseProducer],
        instruction: str,
        m: int,
        *,
        top_k: int | None = None,
        h: int | None = None,
        initialization=None,
        cfg: ListwiseBufferConfig | None = None,
        use_evidence: bool = False,
        trace_hook: Callable[[Dict[str, Any]], None] | None = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Merge one tree with transient winners and stored loser segments.

        This is the production form of the paper's pointer-guided algorithm.
        Every internal node stores only ``loser`` and ``pointer``.  A winner
        segment is transient: it is returned by initialization or by one
        bottom-up path replay, then emitted at the root.  Partial tail segments
        are logically padded to ``h`` with virtual +infinity slots inside
        :func:`_replay_segment_node`; those slots never enter an LLM request.
        """
        if not leaf_sources:
            return
        if m < 2:
            raise ValueError("Pointer-guided LT requires m >= 2")

        emitted_count = 0
        k_actual = len(leaf_sources)
        if k_actual == 1:
            while True:
                if top_k is not None and emitted_count >= top_k:
                    return
                items = await leaf_sources[0].next_candidates(16)
                if not items:
                    return
                for item in items:
                    if top_k is not None and emitted_count >= top_k:
                        return
                    emitted_count += 1
                    yield item

        cfg = normalize_evidence_config(cfg, use_evidence=use_evidence)
        d = (k_actual - 1).bit_length()
        if h is None:
            h = m // (d + 1)
        if h < 1:
            raise ValueError("h must be at least 1")
        if (d + 1) * h > m:
            raise ValueError(
                "Pointer-guided LT fan-in does not fit the listwise "
                f"window: k={k_actual} d={d} h={h} m={m}"
            )

        (
            left_children,
            right_children,
            leaf_to_run,
            _path_of_leaf,
            root,
        ) = self._loser_tree_build_topology(k_actual)
        nodes: Dict[int, _PointerSegmentNode] = {}
        for node_id, left_child in left_children.items():
            if left_child == -1:
                nodes[node_id] = _PointerSegmentNode(
                    node_id=node_id,
                    run_idx=leaf_to_run[node_id],
                )
            else:
                nodes[node_id] = _PointerSegmentNode(
                    node_id=node_id,
                    left=left_child,
                    right=right_children[node_id],
                )

        leaf_done = [False] * k_actual
        next_window_id = 0

        def item_ids(items: List[Dict[str, Any]]) -> List[int]:
            return [int(item["__window_item_id__"]) for item in items]

        def record(event: Dict[str, Any]) -> None:
            if trace_hook is not None:
                trace_hook(event)

        async def fill_leaf(node_id: int) -> List[Dict[str, Any]]:
            nonlocal next_window_id
            check_query_active()
            node = nodes[node_id]
            if not node.is_leaf or node.run_idx is None:
                raise RuntimeError("Only a leaf can be filled")
            run_idx = node.run_idx
            segment: List[Dict[str, Any]] = []
            while len(segment) < h and not leaf_done[run_idx]:
                fresh = await leaf_sources[run_idx].next_candidates(h - len(segment))
                for raw in fresh:
                    item = dict(raw)
                    item["__run_id__"] = run_idx
                    item["__window_item_id__"] = next_window_id
                    next_window_id += 1
                    segment.append(item)
                if leaf_sources[run_idx].exhausted() or not fresh:
                    leaf_done[run_idx] = True
                    break
            record(
                {
                    "phase": "fill_leaf",
                    "node": node_id,
                    "run": run_idx,
                    "tmp": item_ids(segment),
                    "real_size": len(segment),
                    "logical_size": h,
                    "exhausted": leaf_done[run_idx],
                }
            )
            return segment

        async def rank_structural(
            items: List[Dict[str, Any]],
            *,
            phase: str,
        ) -> List[Dict[str, Any]]:
            if len(items) > m:
                raise RuntimeError(
                    f"Pointer-guided LT {phase} window exceeds m: "
                    f"len={len(items)} m={m} h={h} d={d}"
                )
            input_ids = item_ids(items)
            if len(input_ids) != len(set(input_ids)):
                raise RuntimeError(
                    f"Pointer-guided LT {phase} window contains duplicates"
                )
            if len(items) <= 1:
                raw_ranked = list(items)
            else:
                init_stage = LT_INIT
                refresh_stage = LT_PATH_REFRESH
                tail_stage = "lt_tail_refresh"
                stage = (
                    init_stage
                    if phase == "init"
                    else (tail_stage if any(leaf_done) else refresh_stage)
                )
                with ordering_call_scope(stage):
                    raw_ranked = await self._rank_sliding_window_batch(
                        list(items), instruction
                    )
            raw_ranked_ids = [item.get("__window_item_id__") for item in raw_ranked]
            if len(raw_ranked_ids) != len(input_ids) or set(raw_ranked_ids) != set(
                input_ids
            ):
                raise RuntimeError(
                    f"Pointer-guided LT {phase} ranking must return a " "permutation"
                )
            ranked = _preserve_segment_run_order(raw_ranked)
            ranked_ids = [item.get("__window_item_id__") for item in ranked]
            record(
                {
                    "phase": f"{phase}_rank",
                    "window": input_ids,
                    "raw_ranked": [int(item_id) for item_id in raw_ranked_ids],
                    "ranked": [int(item_id) for item_id in ranked_ids],
                    "real_size": len(items),
                    "logical_capacity": (d + 1) * h,
                }
            )
            return ranked

        leaf_nodes = sorted(
            (node_id for node_id, node in nodes.items() if node.is_leaf),
            key=lambda node_id: nodes[node_id].run_idx,
        )
        initial_segments = list(
            await asyncio.gather(*(fill_leaf(node_id) for node_id in leaf_nodes))
        )
        initial_by_run = {
            int(nodes[node_id].run_idx): segment
            for node_id, segment in zip(leaf_nodes, initial_segments)
        }

        def install_replay(
            node_id: int,
            left_segment: List[Dict[str, Any]],
            right_segment: List[Dict[str, Any]],
            positions: Dict[int, int],
            *,
            phase: str,
        ) -> List[Dict[str, Any]]:
            node = nodes[node_id]
            if node.is_leaf:
                raise RuntimeError("Cannot replay an internal match on a leaf")
            pointer_before = node.pointer
            loser_before = list(node.loser)
            replay = _replay_validated_segment(
                left_segment,
                right_segment,
                positions,
                h=h,
                left_child=node.left,
                right_child=node.right,
            )
            node.loser = replay.loser
            node.pointer = replay.pointer
            record(
                {
                    "phase": phase,
                    "node": node_id,
                    "left": item_ids(left_segment),
                    "right": item_ids(right_segment),
                    "tmp": item_ids(replay.winner),
                    "loser_before": item_ids(loser_before),
                    "loser_after": item_ids(replay.loser),
                    "pointer_before": pointer_before,
                    "pointer_after": replay.pointer,
                    "pointer_side": replay.pointer_side,
                    "left_virtual": replay.left_virtual,
                    "right_virtual": replay.right_virtual,
                    "logical_segment_size": h,
                }
            )
            return replay.winner

        segments = {
            node_id: initial_by_run[int(nodes[node_id].run_idx)]
            for node_id in leaf_nodes
        }
        # Topology numbering is shared with the pure estimator's init_plan.
        for block in (
            initialization if initialization is not None else init_plan(k_actual, h, m)
        ):
            check_query_active()
            candidates = [
                item for node_id in block.frontier for item in segments[node_id]
            ]
            ranked = await rank_structural(candidates, phase="init")
            positions = {
                int(item["__window_item_id__"]): i for i, item in enumerate(ranked)
            }
            for node_id in block.replay:
                node = nodes[node_id]
                segments[node_id] = install_replay(
                    node_id,
                    segments[node.left],
                    segments[node.right],
                    positions,
                    phase="build_replay",
                )
        tmp = segments[root]
        global_order = [item for segment in initial_segments for item in segment]
        logger.info(
            "[AUDIT] SegmentLTPointerGuided-stream init "
            "implementation=pointer_guided rank_map_items=%s leaves=%s "
            "d=%s h=%s m=%s use_evidence=%s",
            len(global_order),
            k_actual,
            d,
            h,
            m,
            use_evidence,
        )

        async def refresh_path() -> List[Dict[str, Any]]:
            check_query_active()
            path: List[int] = []
            current_id = root
            while not nodes[current_id].is_leaf:
                node = nodes[current_id]
                if node.pointer not in {node.left, node.right}:
                    raise RuntimeError(
                        "Pointer-guided LT internal node has no valid pointer"
                    )
                path.append(current_id)
                current_id = int(node.pointer)

            through = await fill_leaf(current_id)
            window = list(through)
            for node_id in path:
                window.extend(nodes[node_id].loser)
            ranked = await rank_structural(window, phase="repair")
            positions = {
                int(item["__window_item_id__"]): index
                for index, item in enumerate(ranked)
            }

            for node_id in reversed(path):
                node = nodes[node_id]
                old_pointer = node.pointer
                old_loser = list(node.loser)
                if old_pointer == node.left:
                    left_segment, right_segment = through, old_loser
                else:
                    left_segment, right_segment = old_loser, through
                through = install_replay(
                    node_id,
                    left_segment,
                    right_segment,
                    positions,
                    phase="repair_replay",
                )

            record(
                {
                    "phase": "refresh",
                    "path": path + [current_id],
                    "terminal": current_id,
                    "window": item_ids(window),
                    "ranked": item_ids(ranked),
                    "tmp": item_ids(through),
                    "real_size": len(window),
                    "logical_capacity": (len(path) + 1) * h,
                }
            )
            logger.info(
                "[AUDIT] SegmentLTPointerGuided-stream refresh terminal=%s "
                "path_levels=%s batch=%s output=%s h=%s m=%s use_evidence=%s",
                current_id,
                len(path),
                len(window),
                len(through),
                h,
                m,
                use_evidence,
            )
            return through

        async def rank_epoch(
            pool: List[Dict[str, Any]],
        ) -> List[Dict[str, Any]]:
            if len(pool) > m:
                raise RuntimeError(
                    f"Pointer-guided LT evidence batch exceeds m: " f"{len(pool)} > {m}"
                )
            if len(pool) <= 1:
                return list(pool)
            with ordering_call_scope(LT_PATH_REFRESH):
                raw_ranked = await self._rank_sliding_window_batch(
                    list(pool), instruction
                )
            input_ids = item_ids(pool)
            ranked_ids = [item.get("__window_item_id__") for item in raw_ranked]
            if len(ranked_ids) != len(input_ids) or set(ranked_ids) != set(input_ids):
                raise RuntimeError(
                    "Pointer-guided LT evidence ranking must return a " "permutation"
                )
            return _preserve_segment_run_order(raw_ranked)

        try:
            while tmp:
                record(
                    {
                        "phase": "emit_segment",
                        "tmp": item_ids(tmp),
                        "real_size": len(tmp),
                        "logical_size": h,
                    }
                )
                if use_evidence:
                    epoch_buffer = TreeListwiseBuffer(cfg, use_evidence=True)
                    epoch_buffer.push(tmp)
                    while not epoch_buffer.is_empty:
                        emitted = await epoch_buffer.run_round(
                            rank_epoch,
                            max_emit=len(tmp),
                        )
                        if (
                            not emitted
                            and epoch_buffer.stall_rounds >= cfg.max_stall_rounds
                        ):
                            emitted = epoch_buffer.force_flush()
                        for item in emitted:
                            if top_k is not None and emitted_count >= top_k:
                                return
                            emitted_count += 1
                            yield self._strip_pool_metadata(item)
                else:
                    note_output_ready(
                        min(len(tmp), top_k - emitted_count)
                        if top_k is not None
                        else len(tmp)
                    )
                    for item in tmp:
                        if top_k is not None and emitted_count >= top_k:
                            return
                        emitted_count += 1
                        yield self._strip_pool_metadata(item)
                if top_k is not None and emitted_count >= top_k:
                    return
                tmp = await refresh_path()
        finally:
            logger.info(
                "[AUDIT] SegmentLTPointerGuided-stream complete emitted=%s "
                "implementation=pointer_guided",
                emitted_count,
            )

    @staticmethod
    def _strip_pool_metadata(item: Dict[str, Any]) -> Dict[str, Any]:
        return {key: value for key, value in item.items() if key not in _POOL_META_KEYS}
