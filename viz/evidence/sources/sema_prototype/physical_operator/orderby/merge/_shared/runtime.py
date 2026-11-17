"""Shared materialized and bounded-prefetch drivers for both merge families."""

from __future__ import annotations
import asyncio
from .producer import BaseProducer, QueueProducer, materialize_producer
from sema_prototype.llm.execution_control import ACTIVE_NODE, check_query_active

_EOF = object()
PREFETCH_POLICY = "one_slot_after_second_pull_v1"


class StreamProducer(BaseProducer):
    """A counted stream; reserve queue space BEFORE advancing the generator."""

    def __init__(self, gen, upstreams, size, *, root=False, prefetch=True):
        self.gen, self.upstreams, self.remaining = gen, upstreams, size
        self.root, self.prefetch = root, prefetch and not root
        self.queue = asyncio.Queue(maxsize=1)
        self.slots = asyncio.Semaphore(1)
        self.task = None
        self.closed = False
        self.error = None
        self.requested = 0
        self.pulls = 0
        self.demand = asyncio.Event()

    async def _advance(self, speculative=False):
        token = ACTIVE_NODE.set((self.root, speculative))
        try:
            return await anext(self.gen)
        finally:
            ACTIVE_NODE.reset(token)

    async def _pump(self):
        try:
            while not self.closed:
                await self.slots.acquire()
                if self.remaining == 0:
                    return
                # The first pull prepares a parent's initial frontier. Do not
                # start another refresh while that parent is still assembling
                # its first window. A second pull establishes continuing demand
                # and enables the same one-slot lookahead for either family.
                while self.requested == 0 and self.pulls < 2:
                    self.demand.clear()
                    await self.demand.wait()
                check_query_active()
                try:
                    item = await self._advance(self.requested == 0)
                except StopAsyncIteration:
                    await self.queue.put(_EOF)
                    return
                await self.queue.put(item)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self.error = exc
            await self.queue.put(_EOF)

    async def next_candidates(self, k):
        k = min(max(0, k), self.remaining)
        if not k or self.closed:
            return []
        self.requested += k
        self.pulls += 1
        self.demand.set()
        out = []
        try:
            if self.prefetch and self.task is None:
                self.task = asyncio.create_task(self._pump())
            while len(out) < k:
                if self.prefetch:
                    item = await self.queue.get()
                    self.slots.release()
                else:
                    try:
                        item = await self._advance()
                    except StopAsyncIteration:
                        item = _EOF
                if item is _EOF:
                    if self.error is not None:
                        raise self.error
                    if self.remaining:
                        raise RuntimeError(
                            "merge producer ended before its declared cardinality"
                        )
                    break
                out.append(item)
                self.remaining -= 1
                self.requested -= 1
            return out
        finally:
            self.requested -= k - len(out)

    def exhausted(self):
        return self.remaining == 0

    async def aclose(self):
        if self.closed:
            return
        self.closed = True
        if self.task is not None:
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)
        try:
            await self.gen.aclose()
        finally:
            await asyncio.gather(
                *(p.aclose() for p in self.upstreams), return_exceptions=True
            )


async def _sw_stream(buffer):
    while not buffer.exhausted():
        rows = await buffer.next_candidates(1)
        if not rows:
            break
        yield rows[0]


def build_family_tree(
    ranker,
    runs,
    instruction,
    *,
    plan,
    cfg=None,
    prefetch=True,
):
    from ..sliding_window.sliding_window import StructuralMergeBuffer
    from sema_prototype.physical_operator.orderby._common import record_merge_pass

    algorithm, k, m, limit = plan.algorithm, plan.k, plan.request.m, plan.request.limit
    use_evidence, shuffle_mode = plan.request.use_evidence, plan.request.shuffle_mode
    nodes = [(QueueProducer(run), len(run)) for run in runs if run]
    if not nodes:
        return None
    if len(nodes) == 1:
        if limit is not None:
            return QueueProducer(next(run for run in runs if run)[:limit])
        return nodes[0][0]
    level = 0
    for planned_pass in plan.passes:
        level += 1
        record_merge_pass(
            algorithm=algorithm,
            pass_index=level,
            input_runs=len(nodes),
            output_groups=(len(nodes) + k - 1) // k,
            configured_fan_in=k,
        )
        nxt = []
        for group_index, planned_group in enumerate(planned_pass):
            group = [nodes[i] for i in planned_group.inputs]
            h = planned_group.h
            if len(group) == 1:
                nxt.append(group[0])
                continue
            upstreams = [p for p, _ in group]
            size = sum(n for _, n in group)
            root = len(nodes) <= k
            cap = min(size, limit) if root and limit is not None else size
            if algorithm == "loser_tree":
                gen = ranker._loser_tree_stream_generator(
                    upstreams,
                    instruction,
                    m,
                    h=h,
                    initialization=planned_group.initialization,
                    top_k=limit if root else None,
                    cfg=cfg,
                    use_evidence=use_evidence,
                )
            else:
                buf = StructuralMergeBuffer(
                    upstreams=upstreams,
                    instruction=instruction,
                    m=m,
                    ranker=ranker,
                    h=h,
                    top_k=limit if root else None,
                    use_evidence=use_evidence,
                    shuffle_mode=shuffle_mode,
                    buffer_cfg=cfg,
                    audit_context={
                        "execution_mode": "producer_tree",
                        "merge_level": level,
                        "group_index": group_index,
                        "configured_fan_in": k,
                    },
                )
                gen = _sw_stream(buf)
            nxt.append(
                (
                    StreamProducer(gen, upstreams, cap, root=root, prefetch=prefetch),
                    size,
                )
            )
        nodes = nxt
    return nodes[0][0]


async def execute_family(
    ranker,
    runs,
    instruction,
    *,
    plan,
    cfg=None,
    prefetch=True,
):
    algorithm, k, m, limit = plan.algorithm, plan.k, plan.request.m, plan.request.limit
    use_evidence, shuffle_mode = plan.request.use_evidence, plan.request.shuffle_mode
    mode = plan.execution_mode
    if tuple(len(run) for run in runs if run) != plan.run_lengths:
        raise ValueError("execution input differs from resolved merge plan")
    if mode == "buffer":
        root = build_family_tree(
            ranker,
            runs,
            instruction,
            plan=plan,
            cfg=cfg,
            prefetch=prefetch,
        )
        return await materialize_producer(root, top_k=limit) if root else []
    from ..sliding_window.sliding_window import StructuralMergeBuffer
    from sema_prototype.physical_operator.orderby._common import record_merge_pass

    current = [run for run in runs if run]
    level = 0
    for planned_pass in plan.passes:
        level += 1
        record_merge_pass(
            algorithm=algorithm,
            pass_index=level,
            input_runs=len(current),
            output_groups=(len(current) + k - 1) // k,
            configured_fan_in=k,
        )

        async def merge(group_index, planned_group):
            group = [current[i] for i in planned_group.inputs]
            h = planned_group.h
            if len(group) == 1:
                return group[0]
            upstreams = [QueueProducer(run) for run in group]
            if algorithm == "loser_tree":
                gen = ranker._loser_tree_stream_generator(
                    upstreams,
                    instruction,
                    m,
                    h=h,
                    initialization=planned_group.initialization,
                    cfg=cfg,
                    use_evidence=use_evidence,
                )
                p = StreamProducer(
                    gen, upstreams, sum(map(len, group)), root=False, prefetch=False
                )
            else:
                p = StructuralMergeBuffer(
                    upstreams=upstreams,
                    instruction=instruction,
                    m=m,
                    ranker=ranker,
                    h=h,
                    buffer_cfg=cfg,
                    use_evidence=use_evidence,
                    shuffle_mode=shuffle_mode,
                    audit_context={
                        "execution_mode": "materialized_full",
                        "merge_level": level,
                        "group_index": group_index,
                        "configured_fan_in": k,
                    },
                )
            return await materialize_producer(p, top_k=None)

        tasks = [asyncio.create_task(merge(i, g)) for i, g in enumerate(planned_pass)]
        try:
            current = list(await asyncio.gather(*tasks))
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
    out = current[0] if current else []
    return out[:limit] if limit is not None else out
