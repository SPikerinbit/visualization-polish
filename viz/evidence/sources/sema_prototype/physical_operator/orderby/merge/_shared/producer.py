"""Queue sources, background pumps, and ranked-stream consumption."""
from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from collections import deque
from typing import Any, AsyncIterator, Dict, List, Optional

_PUMP_SENTINEL = object()


class BaseProducer(ABC):
    """Streaming interface for a ranked-item source."""

    @abstractmethod
    async def next_candidates(self, k: int) -> List[Dict[str, Any]]:
        """Return up to k next items in ranked order."""
        ...

    @abstractmethod
    def exhausted(self) -> bool:
        """True when no more items will ever be produced."""
        ...

    async def aclose(self) -> None:
        """Release any background resources (prefetch pumps, generators).

        Default no-op; pump-backed producers override to cancel their pump
        task and recursively close upstreams.  Idempotent.
        """
        return None

class QueueProducer(BaseProducer):
    """Wraps a pre-computed ranked list; serves items in order.

    Use this to attach any merge algorithm's output to the buffer layer:
        producer = QueueProducer(await self._sliding_window_merge(...))
    """

    def __init__(self, items: List[Dict[str, Any]]) -> None:
        self._queue: Deque[Dict[str, Any]] = deque(items)

    async def next_candidates(self, k: int) -> List[Dict[str, Any]]:
        result = []
        for _ in range(min(k, len(self._queue))):
            result.append(self._queue.popleft())
        return result

    def exhausted(self) -> bool:
        return not self._queue

class _PumpedGroupProducer(BaseProducer):
    """Base adapter that drives a per-tree stream generator with a bounded
    look-ahead pump.

    A background task continuously advances the generator and feeds an
    ``asyncio.Queue(maxsize=fetch_batch)``; consumers pull from the queue via
    ``next_candidates``.  Because every internal producer runs its own pump,
    generators at different tree levels — and sibling subtrees at the same
    level — execute concurrently, giving true cross-level pipelining.

    The generator's code and its sequence of upstream pulls / listwise calls
    are unchanged; only the driving task differs.  The queue ``maxsize`` bounds
    speculative prefetch to ``fetch_batch`` items per producer (the only extra
    work versus strict lazy demand under top_k early-stop).

    Subclasses implement :meth:`_ensure_gen` to build ``self._gen``.
    """

    def __init__(
        self,
        *,
        upstreams: List[BaseProducer],
        fetch_batch: int = 1,
    ) -> None:
        if not upstreams:
            raise ValueError(f"{type(self).__name__} requires at least one upstream.")
        self._upstreams = upstreams
        self._fetch_batch = max(1, fetch_batch)
        self._gen: AsyncIterator[Dict[str, Any]] | None = None
        self._gen_done = False
        self._queue: "asyncio.Queue[Any] | None" = None
        self._pump_task: "asyncio.Task[None] | None" = None
        self._pump_exc: BaseException | None = None

    def _ensure_gen(self) -> None:  # pragma: no cover - overridden
        raise NotImplementedError

    def _start_pump(self) -> None:
        if self._pump_task is None:
            self._ensure_gen()
            self._queue = asyncio.Queue(maxsize=self._fetch_batch)
            self._pump_task = asyncio.create_task(self._pump())

    async def _pump(self) -> None:
        assert self._gen is not None and self._queue is not None
        try:
            async for item in self._gen:
                await self._queue.put(item)
        except asyncio.CancelledError:
            # Abandoned via aclose(); do not enqueue the EOF sentinel.
            raise
        except Exception as exc:  # noqa: BLE001 - surfaced to consumer
            self._pump_exc = exc
        await self._queue.put(_PUMP_SENTINEL)

    async def next_candidates(self, k: int) -> List[Dict[str, Any]]:
        if k <= 0:
            return []
        self._start_pump()
        assert self._queue is not None
        result: List[Dict[str, Any]] = []
        while len(result) < k and not self._gen_done:
            item = await self._queue.get()
            if item is _PUMP_SENTINEL:
                self._gen_done = True
                if self._pump_exc is not None:
                    raise self._pump_exc
                break
            result.append(item)
        return result

    def exhausted(self) -> bool:
        return self._gen_done and (self._queue is None or self._queue.empty())

    async def aclose(self) -> None:
        if self._pump_task is not None and not self._pump_task.done():
            self._pump_task.cancel()
            try:
                await self._pump_task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
        if self._gen is not None:
            try:
                await self._gen.aclose()
            except Exception:  # noqa: BLE001
                pass
        for up in self._upstreams:
            await up.aclose()

class _PumpedProducer(BaseProducer):
    """Wraps a BaseProducer in a background asyncio task with a bounded queue.

    The inner producer is advanced by a single pump task that pushes items
    one at a time into a bounded queue.  The parent reads from the queue
    without waiting for the inner producer to complete a full round, enabling
    cross-layer pipeline overlap inside a producer tree.

    ``fetch_batch`` (queue maxsize) controls how many items can be pre-buffered.
    The default of 1 gives a one-item lookahead — enough for the parent's LLM
    call to overlap with the child's next round — with minimal wasted work on
    early-stop paths.

    Call ``start()`` after construction to launch the background task.  Call
    ``aclose()`` (or rely on ``drain_producer``'s try/finally) to cancel the
    task and close the inner producer recursively.
    """

    def __init__(self, inner: BaseProducer, fetch_batch: int = 1) -> None:
        self._inner = inner
        self._queue: asyncio.Queue[Optional[Dict[str, Any]]] = asyncio.Queue(
            maxsize=max(1, fetch_batch)
        )
        self._pump_task: Optional[asyncio.Task] = None  # type: ignore[type-arg]
        self._error: Optional[Exception] = None
        self._eof = False
        self._closing = False

    def start(self) -> "_PumpedProducer":
        self._pump_task = asyncio.create_task(self._pump_loop())
        return self

    async def _pump_loop(self) -> None:
        try:
            while not self._inner.exhausted():
                items = await self._inner.next_candidates(1)
                if not items:
                    break
                for item in items:
                    await self._queue.put(item)
        except Exception as exc:
            # Deliver background failures to the consumer instead of treating
            # them as EOF and returning a silently truncated ranking.
            self._error = exc
        finally:
            if self._closing:
                try:
                    self._queue.put_nowait(None)
                except asyncio.QueueFull:
                    pass
            else:
                await self._queue.put(None)  # EOF sentinel

    async def next_candidates(self, k: int) -> List[Dict[str, Any]]:
        if self._eof or k <= 0:
            return []
        result: List[Dict[str, Any]] = []
        while len(result) < k and not self._eof:
            item = await self._queue.get()
            if item is None:
                self._eof = True
                if self._error is not None:
                    raise self._error
                break
            result.append(item)
        return result

    def exhausted(self) -> bool:
        return self._eof

    async def aclose(self) -> None:
        self._closing = True
        self._eof = True
        if self._pump_task and not self._pump_task.done():
            self._pump_task.cancel()
            try:
                await self._pump_task
            except asyncio.CancelledError:
                pass
        await self._inner.aclose()

async def materialize_producer(producer: BaseProducer, *, top_k: int | None) -> List[Dict[str, Any]]:
    """Drain a producer into a list, optionally capped at top_k.

    Always closes the producer on exit so look-ahead pump tasks (and any nested
    upstream pumps) are cancelled — including on early-stop at top_k.
    """
    result: List[Dict[str, Any]] = []
    pull_size = top_k if (top_k is not None and top_k > 0) else 64
    try:
        while True:
            if top_k is not None and len(result) >= top_k:
                break
            if producer.exhausted():
                break
            remaining = top_k - len(result) if top_k is not None else pull_size
            batch = await producer.next_candidates(max(1, remaining))
            if not batch:
                break
            result.extend(batch)
    finally:
        await producer.aclose()
    if top_k is not None:
        return result[:top_k]
    return result

async def drain_producer(
    producer: BaseProducer, *, top_k: Optional[int]
) -> List[Dict[str, Any]]:
    """Drain a producer to a list, capping at ``top_k`` when set.

    Always calls ``producer.aclose()`` in a finally block so that any
    background pump tasks started by ``_PumpedProducer`` nodes are cancelled
    on early-stop (top_k < total), preventing task leaks.
    """
    result: List[Dict[str, Any]] = []
    pull_size = top_k if (top_k is not None and top_k > 0) else 64
    try:
        while True:
            if top_k is not None and len(result) >= top_k:
                break
            if producer.exhausted():
                break
            remaining = top_k - len(result) if top_k is not None else pull_size
            batch = await producer.next_candidates(max(1, remaining))
            if not batch:
                break
            result.extend(batch)
    finally:
        await producer.aclose()
    if top_k is not None:
        return result[:top_k]
    return result
