"""Pure ORDER BY planning: profiles, topology, workload, search and resolved layout."""

from __future__ import annotations
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Sequence, TypeVar
from dataclasses import asdict
from collections import Counter
import math

T = TypeVar("T")
MODEL_VERSION = "orderby-input-v5"
CONFIG_VERSION = "orderby-config-v6"
PROFILE_VERSION = "orderby-profile-v1"

# 配置类型


@dataclass(frozen=True)
class InputTokenProfile:
    H: float
    L: float
    source: str = "explicit"
    fit_error: float = 0.0
    tokenizer: str | None = None
    scope: str = "explicit"
    template_fingerprint: str | None = None
    counting_version: str | None = None
    profile_version: str = "orderby-profile-v1"
    uncovered: tuple[str, ...] = ()
    fallback_reasons: tuple[str, ...] = ()
    counting_stats: tuple[tuple[str, float], ...] = ()

    def __post_init__(self):
        if (
            not math.isfinite(self.H)
            or self.H < 0
            or not math.isfinite(self.L)
            or self.L <= 0
        ):
            raise ValueError("token profile requires finite H >= 0 and L > 0")

    @property
    def rho(self):
        return self.H / self.L

    def to_dict(self):
        return dict(asdict(self), rho=self.rho)


@dataclass(frozen=True)
class CostEstimate:
    algorithm: str
    k: int
    h: int | None
    mode: str
    init_calls: float
    init_items: float
    refresh_calls: float
    refresh_items: float
    H: float
    L: float
    version: str = MODEL_VERSION
    tail_delta_calls: float = 0.0
    tail_delta_items: float = 0.0
    calibration: tuple = field(default=(), compare=False)
    planning_seconds: float = field(default=0.0, compare=False)
    expectation: dict = field(default_factory=dict, compare=False)

    @property
    def total_calls(self):
        return self.init_calls + self.refresh_calls - self.tail_delta_calls

    @property
    def total_items(self):
        return self.init_items + self.refresh_items - self.tail_delta_items

    @property
    def input_tokens(self):
        return self.H * self.total_calls + self.L * self.total_items

    def to_dict(self):
        return dict(
            asdict(self),
            input_tokens=self.input_tokens,
            init_tokens=self.H * self.init_calls + self.L * self.init_items,
            refresh_tokens=self.H * self.refresh_calls + self.L * self.refresh_items
            - self.H * self.tail_delta_calls - self.L * self.tail_delta_items,
            base_input_tokens=self.H * (self.init_calls + self.refresh_calls)
            + self.L * (self.init_items + self.refresh_items),
            tail_delta_tokens=self.H * self.tail_delta_calls + self.L * self.tail_delta_items,
            total_calls=self.total_calls,
            total_items=self.total_items,
        )


@dataclass(frozen=True)
class MergeRequest:
    algorithm: str = "sliding_window"
    k: int | None = None
    h: int | str | None = None
    m: int = 20
    limit: int | None = None
    mode: str | None = None
    parameter_policy: str = "token_best"
    profile: InputTokenProfile | None = None
    input_token_counting: tuple = ()
    use_evidence: bool = False
    shuffle_mode: str = "none"
    full_tail_correction: bool = True
    tail_cache_dir: str | None = None
    mc_samples: int = 16384
    mc_seed: int = 2410000

    def __post_init__(self):
        from .finite import validate_sampling
        validate_sampling(self.mc_samples, self.mc_seed)
        if not isinstance(self.full_tail_correction, bool):
            raise ValueError("full_tail_correction must be boolean")
        if self.algorithm not in {"sliding_window", "loser_tree", "auto"}:
            raise ValueError(f"unknown merge algorithm {self.algorithm!r}")
        if self.m is None:
            raise ValueError("m must be an integer >= 1")
        for name, value, minimum in (
            ("m", self.m, 1),
            ("k", self.k, 2),
            ("limit", self.limit, 0),
        ):
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int) or value < minimum
            ):
                raise ValueError(f"{name} must be an integer >= {minimum}")
        if self.h not in (None, "maximum") and (
            isinstance(self.h, bool) or not isinstance(self.h, int) or self.h < 1
        ):
            raise ValueError("h must be null, maximum, or a positive integer")
        if self.mode not in {None, "full", "buffer"}:
            raise ValueError("invalid merge mode")
        if self.parameter_policy not in {"none", "token_best"}:
            raise ValueError("invalid parameter_policy")
        if self.shuffle_mode not in {"none", "balanced", "progressive"}:
            raise ValueError(f"Unknown shuffle_mode {self.shuffle_mode!r}")
        if self.use_evidence and (
            self.algorithm == "auto" or self.parameter_policy != "none"
        ):
            raise ValueError("evidence requires manual parameter_policy='none'")


@dataclass(frozen=True)
class InitBlock:
    root: int
    frontier: tuple[int, ...]
    replay: tuple[int, ...]


@dataclass(frozen=True)
class MergeNode:
    size: int
    children: tuple["MergeNode", ...] = ()

    @property
    def fan_in(self):
        return len(self.children)


@dataclass(frozen=True)
class PlannedGroup:
    inputs: tuple[int, ...]
    lengths: tuple[int, ...]
    h: int | None
    initialization: tuple[InitBlock, ...] = ()


@dataclass(frozen=True)
class ResolvedMergePlan:
    request: MergeRequest
    estimate: CostEstimate
    execution_mode: str
    cost_mode: str
    run_lengths: tuple[int, ...]
    passes: tuple[tuple[PlannedGroup, ...], ...]
    version: str = CONFIG_VERSION

    @property
    def algorithm(self):
        return self.estimate.algorithm

    @property
    def k(self):
        return self.estimate.k


# 归并拓扑


def merge_groups(items: Sequence[T], k: int) -> list[list[T]]:
    if k < 2:
        raise ValueError("fan-in k must be at least 2")
    return [list(items[i : i + k]) for i in range(0, len(items), k)]


@lru_cache(maxsize=32)
def binary_topology(g: int):
    if g < 1:
        raise ValueError("a topology needs at least one input")
    left, right, run, depths = [], [], [], [0] * g

    def build(lo, hi, depth):
        i = len(left)
        left.append(-1)
        right.append(-1)
        run.append(-1)
        if hi - lo == 1:
            run[i] = lo
            depths[lo] = depth
        else:
            mid = (lo + hi + 1) // 2
            left[i] = build(lo, mid, depth + 1)
            right[i] = build(mid, hi, depth + 1)
        return i

    build(0, g, 0)
    return tuple(left), tuple(right), tuple(run), tuple(depths)


@lru_cache(maxsize=64)
def init_plan(g: int, h: int, m: int) -> tuple[InitBlock, ...]:
    if h < 1 or (g > 1 and 2 * h > m):
        raise ValueError("two segments must fit within m")
    left, right, run, _ = binary_topology(g)
    frontier = {i for i, r in enumerate(run) if r >= 0}
    blocks = []
    while 0 not in frontier:
        units = {}

        def collect(i):
            units[i] = (i,) if i in frontier else collect(left[i]) + collect(right[i])
            return units[i]

        collect(0)
        cuts = []

        def cut(i):
            if i in frontier or len(units[i]) * h <= m:
                cuts.append(i)
            else:
                cut(left[i])
                cut(right[i])

        cut(0)
        for i in cuts:
            if i in frontier:
                continue
            ops = []

            def replay(j):
                if j not in frontier:
                    replay(left[j])
                    replay(right[j])
                    ops.append(j)

            replay(i)
            blocks.append(InitBlock(i, units[i], tuple(ops)))
        frontier = set(cuts)
    return tuple(blocks)


@lru_cache(maxsize=16)
def build_merge_plan(lengths: tuple[int, ...], k: int) -> MergeNode:
    leaves = {n: MergeNode(n) for n in set(lengths) if n > 0}
    nodes = [leaves[n] for n in lengths if n > 0]
    interned = {}

    def parent(group):
        if len(group) == 1:
            return group[0]
        key = tuple(map(id, group))
        if key not in interned:
            interned[key] = MergeNode(sum(v.size for v in group), tuple(group))
        return interned[key]

    if not nodes:
        return MergeNode(0)
    while len(nodes) > 1:
        nodes = [parent(g) for g in merge_groups(nodes, k)]
    return nodes[0]


def walk_groups(node: MergeNode):
    if node.children:
        for child in node.children:
            yield from walk_groups(child)
        yield node


def max_segment(g: int, m: int) -> int:
    return m // (1 + (g - 1).bit_length()) if g > 1 else m


def initialization_counts(node: MergeNode, h: int, m: int) -> tuple[int, int]:
    if all(c.size >= h for c in node.children):
        calls = init_call_count(node.fan_in, h, m)
        return calls, h * (node.fan_in - 1 + calls)
    left, right, run, _ = binary_topology(node.fan_in)
    sizes = {i: min(h, node.children[r].size) for i, r in enumerate(run) if r >= 0}
    calls = docs = 0
    for block in init_plan(node.fan_in, h, m):
        b = sum(sizes[i] for i in block.frontier)
        if b > 1:
            calls += 1
            docs += b
        for i in block.replay:
            sizes[i] = min(h, sizes[left[i]] + sizes[right[i]])
    return calls, docs


@lru_cache(maxsize=8192)
def _frontier_count(g, capacity):
    if g <= capacity:
        return 1, int(g > 1)
    a, ca = _frontier_count((g + 1) // 2, capacity)
    b, cb = _frontier_count(g // 2, capacity)
    return a + b, ca + cb


@lru_cache(maxsize=8192)
def init_call_count(g, h, m):
    """Count the identical balanced-subtree packing without materializing IDs.

    Contracting maximal packed subtrees preserves the balanced binary shape.
    Singleton frontier units pass through without a request.
    """
    capacity = m // h
    if capacity < 2:
        raise ValueError("two segments must fit within m")
    calls = 0
    while g > 1:
        g, added = _frontier_count(g, capacity)
        calls += added
    return calls


# token 画像


def fit_profile(pairs, **metadata):
    """Fit nonnegative H,L to request counts; no backend dependencies."""
    if not pairs:
        raise ValueError("no token measurements")
    xm = sum(x for x, y in pairs) / len(pairs)
    ym = sum(y for x, y in pairs) / len(pairs)
    den = sum((x - xm) ** 2 for x, y in pairs)
    L = sum((x - xm) * (y - ym) for x, y in pairs) / den if den else ym / max(1, xm)
    H = ym - L * xm
    if H < 0:
        H = 0.0
        L = sum(x * y for x, y in pairs) / sum(x * x for x, y in pairs)
    if L <= 0:
        L = 1e-9
        H = max(0, ym - L * xm)
    error = math.sqrt(sum((H + L * x - y) ** 2 for x, y in pairs) / len(pairs)) / max(
        1, ym
    )
    return InputTokenProfile(H, L, fit_error=error, **metadata)


async def measure_profile(rows, m, prepare, counter):
    """Measure once through injected real-request builder and batch counter."""
    import random
    import hashlib
    import json

    if not rows:
        raise ValueError("cannot measure an empty input")
    samples = random.Random(0).sample(list(rows), min(64, len(rows)))
    n = min(m, len(samples))
    widths = sorted({1, min(n, (m + 1) // 2), n})
    requests, bs, seen = [], [], set()
    for b in widths:
        for offset in range(3):
            request = prepare(
                [samples[(offset * b + i) % len(samples)] for i in range(b)]
            )
            digest = hashlib.sha256(
                json.dumps(
                    request, sort_keys=True, ensure_ascii=False, default=str
                ).encode()
            ).hexdigest()
            if digest not in seen:
                seen.add(digest)
                requests.append(request)
                bs.append(b)
    counts = await counter.count_requests(requests)
    if len({(x.source, x.scope) for x in counts}) != 1:
        raise ValueError("a token profile must use one counting backend")
    template = hashlib.sha256(
        json.dumps(requests, sort_keys=True, default=str).encode()
    ).hexdigest()
    return fit_profile(
        list(zip(bs, [c.tokens for c in counts])),
        source=counts[0].source,
        scope=counts[0].scope,
        template_fingerprint=template,
        counting_version=counts[0].version,
        uncovered=tuple(sorted({f for c in counts for f in c.uncovered})),
        fallback_reasons=tuple(counter.fallback_reasons),
        counting_stats=tuple(counter.stats.items()),
    )


# 工作量估计


@lru_cache(maxsize=4096)
def sw_mu(g: int, h: int) -> float:
    """IID-source stopping time: first source with h arrivals (long-run mean).

    Polynomial coefficients are multiplied by t! while convolving, so the
    intermediates are probabilities rather than tiny factorial reciprocals.
    """
    if g < 1 or h < 1:
        raise ValueError("g and h must be positive")
    if h == 1 or g == 1:
        return float(h)
    coefficients = [1.0]
    for _ in range(g):
        out = [0.0] * (len(coefficients) + h - 1)
        for t in range(len(out)):
            out[t] = math.fsum(
                math.comb(t, j) * (1.0 / g)**j * coefficients[t-j]
                for j in range(max(0, t-len(coefficients)+1), min(h-1, t)+1)
            )
        coefficients = out
    return math.fsum(coefficients)


def estimate_cost(lengths, algorithm, k, h, m, limit, profile, *, mode=None,
                  full_tail_correction=True, tail_cache_dir=None,
                  mc_samples=16384, mc_seed=2410000):
    """Expected finite merge work, priced with the measured input-token profile.

    Full execution sums materialized groups; prefix execution retains the
    producer dependencies until the root has produced LIMIT. The legacy switch
    disables the finite Full model for the existing uncorrected-v3 ablation.
    """
    from .finite import expectation, validate_sampling
    validate_sampling(mc_samples, mc_seed)
    from dataclasses import replace

    lengths = tuple(n for n in lengths if n > 0)
    mode = mode or ("buffer" if limit is not None and limit < sum(lengths) else "full")
    if mode == "full" and not full_tail_correction:
        legacy = _estimate_cost_v3(lengths, algorithm, k, h, m, limit, profile,
                                   mode=mode, full_tail_correction=False,
                                   tail_cache_dir=tail_cache_dir)
        return replace(legacy, version="orderby-input-v3-uncorrected",
                       expectation={"method": "legacy_uncorrected", "mode": mode})
    if mode not in {"full", "buffer"}:
        raise ValueError("invalid cost mode")
    if algorithm not in {"loser_tree", "sliding_window"}:
        raise ValueError(f"unknown merge family {algorithm!r}")
    if len(lengths) < 2 or limit == 0:
        return CostEstimate(algorithm, k, h, mode, 0, 0, 0, 0, profile.H, profile.L)
    if k < 2 or m < 2:
        raise ValueError("merging multiple runs requires k,m >= 2")
    if mode == "buffer" and (h is None or limit is None):
        raise ValueError("prefix estimation requires h and LIMIT")
    g = min(k, len(lengths))
    cap = max_segment(g, m) if algorithm == "loser_tree" else m // g
    if cap < 1 or (h is not None and (h < 1 or h > cap)):
        raise ValueError("merge request exceeds m")
    work = expectation(lengths, algorithm, k, h, m, limit, mode=mode,
                       cache_dir=tail_cache_dir, mc_samples=mc_samples, mc_seed=mc_seed)
    metadata = work.to_metadata()
    metadata["token_standard_error"] = math.sqrt(max(
        0.0, profile.H**2 * work.se_calls**2 + profile.L**2 * work.se_items**2
        + 2 * profile.H * profile.L * work.cov_calls_items))
    return CostEstimate(algorithm, k, h, mode, work.IA, work.ID,
                        work.A - work.IA, work.D - work.ID, profile.H, profile.L,
                        expectation=metadata)


def _estimate_cost_v3(lengths, algorithm, k, h, m, limit, profile, *, mode=None,
                      full_tail_correction=True, tail_cache_dir=None):
    """Frozen v3 approximation, retained for explicit baseline comparisons."""
    mode = mode or ("buffer" if limit is not None and limit < sum(lengths) else "full")
    plan = build_merge_plan(tuple(lengths), k)
    IA = ID = RA = RD = DA = DD = 0.0
    calibration = []

    def correction(node, hv, multiplicity=1):
        nonlocal DA, DD
        if mode != "full" or not full_tail_correction:
            return
        from .tail import tail_correction
        c = tail_correction(tuple(v.size for v in node.children), algorithm, hv, m, tail_cache_dir)
        DA += multiplicity * c.delta_calls
        DD += multiplicity * c.delta_items
        calibration.append(dict(fan_in=node.fan_in, size=node.size, h=hv,
                                multiplicity=multiplicity, **asdict(c)))
    if not plan.children or limit == 0:
        return CostEstimate(algorithm, k, h, mode, 0, 0, 0, 0, profile.H, profile.L)
    if algorithm == "loser_tree":
        if mode == "buffer" and h is None:
            raise ValueError("prefix LT requires one shared h")
        groups = {}

        def collect(node, multiplicity=1):
            if not node.children:
                return
            key = id(node)
            if key in groups:
                groups[key][1] += multiplicity
            else:
                groups[key] = [node, multiplicity]
            by_id = {id(c): c for c in node.children}
            for child_id, count in Counter(map(id, node.children)).items():
                collect(by_id[child_id], multiplicity * count)

        collect(plan)
        for node, multiplicity in groups.values():
            hv = h if h is not None else max_segment(node.fan_in, m)
            if hv < 1 or hv > max_segment(node.fan_in, m):
                raise ValueError("LT refresh path exceeds m")
            a, b = initialization_counts(node, hv, m)
            IA += a * multiplicity
            ID += b * multiplicity
            if mode == "full":
                rounds = max(0, math.ceil(node.size / hv) - 1)
                RA += rounds * multiplicity
                RD += rounds * multiplicity * hv * (1 + (node.fan_in - 1).bit_length())
                correction(node, hv, multiplicity)
        if mode == "buffer":
            path_cache = {}

            def path(node):
                if not node.children:
                    return (0, 0)
                if id(node) not in path_cache:
                    if all(not c.children for c in node.children):
                        path_cache[id(node)] = (1, 1 + (node.fan_in - 1).bit_length())
                    elif all(c is node.children[0] for c in node.children):
                        a, b = path(node.children[0])
                        path_cache[id(node)] = (
                            a + 1,
                            b + 1 + (node.fan_in - 1).bit_length(),
                        )
                    else:
                        depths = binary_topology(node.fan_in)[3]
                        options = [
                            (a + 1, b + depths[i] + 1)
                            for i, c in enumerate(node.children)
                            for a, b in [path(c)]
                        ]
                        path_cache[id(node)] = max(
                            options,
                            key=lambda p: profile.H * p[0] + profile.L * h * p[1],
                        )
                return path_cache[id(node)]

            a, b = path(plan)
            rounds = max(0, (min(limit, plan.size) - 1) // h)
            RA, RD = rounds * a, rounds * h * b
    elif algorithm == "sliding_window":

        def visit(node, demand):
            nonlocal IA, ID, RA, RD
            if not node.children or demand <= 0:
                return
            g = node.fan_in
            hv = h if h is not None else m // g
            if hv < 1 or g * hv > m:
                raise ValueError("SW window exceeds m")
            b = sum(min(hv, c.size) for c in node.children)
            # Complete short inputs can be borrowed into the first full window.
            if mode == "full" and h is None:
                b = min(node.size, g * hv)
            mu = sw_mu(g, hv)
            calls = max(1.0, min(demand, node.size) / mu)
            IA += int(b > 1)
            ID += b if b > 1 else 0
            RA += calls - 1
            RD += (calls - 1) * g * hv
            correction(node, h)
            for child in node.children:
                x = (
                    child.size
                    if mode == "full"
                    else min(child.size, hv + max(0, demand - mu) / g)
                )
                visit(child, x)

        visit(plan, plan.size if mode == "full" else min(limit, plan.size))
    else:
        raise ValueError(f"unknown merge family {algorithm!r}")
    return CostEstimate(algorithm, k, h, mode, IA, ID, RA, RD, profile.H, profile.L,
                        tail_delta_calls=DA, tail_delta_items=DD,
                        calibration=tuple(calibration))


# 参数选择


def select_parameters(
    lengths,
    m,
    limit,
    profile,
    *,
    algorithm="auto",
    k=None,
    h=None,
    mode=None,
    policy="token_best",
    full_tail_correction=True,
    tail_cache_dir=None,
    mc_samples=16384,
    mc_seed=2410000,
):
    import time
    from dataclasses import replace
    started = time.perf_counter()
    from .finite import validate_sampling
    validate_sampling(mc_samples, mc_seed)
    if policy not in {"token_best", "none"}:
        raise ValueError(f"unsupported parameter_policy {policy!r}")
    if algorithm not in {"auto", "loser_tree", "sliding_window"}:
        raise ValueError(f"unknown merge algorithm {algorithm!r}")
    mode = mode or ("buffer" if limit is not None and limit < sum(lengths) else "full")
    r = len([n for n in lengths if n > 0])
    if r < 2 or limit == 0:
        return CostEstimate(
            "loser_tree" if algorithm == "auto" else algorithm,
            k or 2,
            h if isinstance(h, int) else None,
            mode,
            0,
            0,
            0,
            0,
            profile.H,
            profile.L,
        )
    if m < 2:
        raise ValueError("merging multiple runs requires m >= 2")
    maximum_h = h == "maximum"
    if maximum_h:
        h = None
    candidates = []
    for family in (
        ["loser_tree", "sliding_window"] if algorithm == "auto" else [algorithm]
    ):
        upper = min(r, 2 ** (m - 1)) if family == "loser_tree" else min(r, m)
        ks = (
            [k]
            if k is not None
            else ([min(6, upper)] if policy == "none" else range(2, upper + 1))
        )
        for kv in ks:
            if kv < 2 or kv > upper:
                continue
            effective = min(kv, r)
            cap = (
                max_segment(effective, m) if family == "loser_tree" else m // effective
            )
            if h is not None:
                hs = [h]
            elif mode == "full" and family == "sliding_window":
                hs = [None]
            elif mode == "full" and (maximum_h or policy == "none"):
                hs = [cap]
            elif mode == "full":
                hs = range(1, cap + 1)
            elif maximum_h:
                hs = [min(limit, cap)]
            elif policy == "none":
                hs = [1]
            else:
                hs = range(1, min(limit, cap) + 1)
            for hv in hs:
                if cap < 1 or (hv is not None and (hv < 1 or hv > cap)):
                    continue
                candidates.append(
                    estimate_cost(lengths, family, kv, hv, m, limit, profile, mode=mode,
                                  full_tail_correction=full_tail_correction,
                                  tail_cache_dir=tail_cache_dir,
                                  mc_samples=mc_samples, mc_seed=mc_seed)
                )
    if not candidates:
        raise ValueError("no feasible (algorithm,k,h) under m and explicit parameters")
    best = min(x.input_tokens for x in candidates)
    tied = [
        x
        for x in candidates
        if math.isclose(x.input_tokens, best, rel_tol=1e-12, abs_tol=1e-12)
    ]
    return replace(min(tied, key=lambda x: (x.algorithm != "loser_tree", x.k, x.h or 0)),
                   planning_seconds=time.perf_counter()-started)


# 执行计划


def resolve_merge_plan(lengths, request):
    """Search compressed costs, then materialize only the selected layout."""
    lengths = tuple(n for n in lengths if n > 0)
    validate_request_capacity(len(lengths), request)
    n = sum(lengths)
    cost_mode = "buffer" if request.limit is not None and request.limit < n else "full"
    execution_mode = request.mode or cost_mode
    # An explicit buffer demand remains a pipeline even when K equals n.
    # Selection and execution must use the same scheduling semantics.
    cost_mode = execution_mode
    estimate = select_parameters(
        lengths,
        request.m,
        request.limit,
        request.profile or InputTokenProfile(0, 1),
        algorithm=request.algorithm,
        k=request.k,
        h=request.h,
        mode=cost_mode,
        policy=request.parameter_policy,
        full_tail_correction=request.full_tail_correction,
        tail_cache_dir=request.tail_cache_dir,
        mc_samples=request.mc_samples, mc_seed=request.mc_seed,
    )
    current = lengths
    passes = []
    while len(current) > 1:
        groups = []
        for start in range(0, len(current), estimate.k):
            sizes = current[start : start + estimate.k]
            g = len(sizes)
            hv = estimate.h
            if hv is None and g > 1 and estimate.algorithm == "loser_tree":
                hv = max_segment(g, request.m)
            groups.append(
                PlannedGroup(
                    tuple(range(start, start + g)),
                    sizes,
                    hv,
                    (
                        init_plan(g, hv, request.m)
                        if g > 1 and estimate.algorithm == "loser_tree"
                        else ()
                    ),
                )
            )
        passes.append(tuple(groups))
        current = tuple(sum(g.lengths) for g in groups)
    return ResolvedMergePlan(
        request, estimate, execution_mode, cost_mode, lengths, tuple(passes)
    )


def validate_request_capacity(run_count, request):
    """Reject impossible explicit controls before token measurement or sorting."""
    if run_count < 2 or request.limit == 0:
        return
    if request.m < 2:
        raise ValueError("merging multiple runs requires m >= 2")
    families = (
        ("loser_tree", "sliding_window")
        if request.algorithm == "auto"
        else (request.algorithm,)
    )
    for family in families:
        k = request.k if request.k is not None else 2
        if k > run_count:
            continue
        cap = max_segment(k, request.m) if family == "loser_tree" else request.m // k
        if cap >= 1 and (not isinstance(request.h, int) or request.h <= cap):
            return
    raise ValueError("no feasible (algorithm,k,h) under m and explicit parameters")
