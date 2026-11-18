"""Axis limits for the E4c Off / On-cold pair.

Limits come from every mean in one metric figure. Full Spearman and LIMIT-10
NDCG@10 are separate figures and do not share a quality scale. Padding is
outside the data, equal on both ends, so the frame is not a zoom into a
subset and not a half-empty box.
"""

from __future__ import annotations

import math

PAD_FRAC = 0.16
TOKEN_STEP = 10_000
TOKEN_INSET = 0.08
QUALITY_STEP = 0.10
QUALITY_INSET = 0.04
MIN_TICKS = 4


def limits_from_values(values: list[float], pad_frac: float = PAD_FRAC) -> tuple[float, float]:
    if len(values) < 2:
        raise ValueError("need at least two values to place a range")
    lo = min(values)
    hi = max(values)
    span = hi - lo
    if span <= 0:
        raise ValueError("degenerate range")
    return (lo - pad_frac * span, hi + pad_frac * span)


def data_occupancy(values: list[float], pad_frac: float = PAD_FRAC) -> float:
    lo, hi = limits_from_values(values, pad_frac)
    return (max(values) - min(values)) / (hi - lo)


def interior_ticks(lo: float, hi: float, step: float, inset_frac: float) -> list[float]:
    span = hi - lo
    if span <= 0 or step <= 0:
        raise ValueError("bad tick span")
    ticks: list[float] = []
    k = math.floor(lo / step + 1e-9) + 1
    while True:
        raw = k * step
        if raw >= hi - 1e-9:
            break
        if (raw - lo) / span >= inset_frac and (hi - raw) / span >= inset_frac:
            if step >= 1:
                ticks.append(float(int(round(raw))))
            else:
                ticks.append(round(raw, 2))
        k += 1
    return ticks


def token_ticks(lo: float, hi: float) -> list[float]:
    ticks = interior_ticks(lo, hi, TOKEN_STEP, TOKEN_INSET)
    if len(ticks) < MIN_TICKS:
        ticks = interior_ticks(lo, hi, TOKEN_STEP, 0.04)
    if len(ticks) < MIN_TICKS:
        raise ValueError(f"token ticks collapsed to {ticks}")
    return ticks


def quality_ticks(lo: float, hi: float) -> list[float]:
    ticks = interior_ticks(lo, hi, QUALITY_STEP, QUALITY_INSET)
    if len(ticks) < MIN_TICKS:
        ticks = interior_ticks(lo, hi, 0.05, 0.03)
    if len(ticks) < MIN_TICKS:
        raise ValueError(f"quality ticks collapsed to {ticks}")
    return ticks


def format_token(value: float) -> str:
    if abs(value - round(value)) > 1e-6:
        raise ValueError(f"token tick is not an integer: {value}")
    return str(int(round(value)))


def format_quality(value: float) -> str:
    return f"{value:.2f}"
