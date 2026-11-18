"""Legal (k, h) domain from the merge planner.

``select_parameters`` in ``plan.py`` caps fan-in by the number of runs and
by ``m``. Phase-1 runs of length at most ``m`` give ``r = ceil(n / m)``.
SW: ``k <= min(r, m)`` and ``h <= m // k``.
LT: ``k <= min(r, 2**(m-1))`` and ``h <= max_segment(k, m)``.

At ``m=20``, ``n=100`` has ``r=5``, so ``k=8`` is illegal.
At ``n=500``, ``r=25`` and ``k=8`` is legal for both families.
"""

from __future__ import annotations


def initial_runs(n: int, m: int = 20) -> int:
    if n < 1 or m < 2:
        raise ValueError(f"bad n, m: {n}, {m}")
    return (n + m - 1) // m


def max_segment(g: int, m: int) -> int:
    return m // (1 + (g - 1).bit_length()) if g > 1 else m


def upper_k(family: str, n: int, m: int = 20) -> int:
    runs = initial_runs(n, m)
    if family == "SW":
        return min(runs, m)
    if family == "LT":
        return min(runs, 2 ** (m - 1))
    raise ValueError(family)


def segment_cap(family: str, k: int, m: int = 20) -> int:
    if family == "SW":
        return m // k
    if family == "LT":
        return max_segment(k, m)
    raise ValueError(family)


def is_legal(family: str, k: int, h: int, n: int, m: int = 20) -> bool:
    if k < 2 or h < 1:
        return False
    if k > upper_k(family, n, m):
        return False
    cap = segment_cap(family, k, m)
    return 1 <= h <= cap


def assert_legal(family: str, pairs, n: int, m: int = 20) -> None:
    bad = [(k, h) for k, h in pairs if not is_legal(family, k, h, n, m)]
    if bad:
        raise RuntimeError(f"illegal {family} (k,h) at n={n}, m={m}: {bad}")
