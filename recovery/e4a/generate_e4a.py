#!/usr/bin/env python3
"""Synthetic layout sample for experiment 4a (Off vs On-cold).

The numbers are a reproducible drawing sample. They are not measurements,
not a frozen cost model, and not evidence that caching or selection helps.

Run from any working directory:

    python3 recovery/e4a/generate_e4a.py

Outputs, next to this file:

    data/e4a_synthetic.json
    figures/e4a-compact-<dataset>-n<100|500>.pdf
    and a PNG at the same 178 mm width for each PDF

    Legacy proposal-B sheets under figures/e4a-layout-b-*.pdf are not regenerated.

Marker y values are taken only from the measured series of the matching
cache state. Predicted token scores are stored so a reader can check that
they were not used as heights.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.legend_handler import HandlerBase
from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "e4a_synthetic.json"
FIG_DIR = ROOT / "figures"

WIDTH_MM = 178.0
WIDTH_IN = WIDTH_MM / 25.4
HEIGHT_MM_TARGET = 98.0  # compact A sheets: aim 90--105 mm
HEIGHT_IN = HEIGHT_MM_TARGET / 25.4
PNG_DPI = 160
MIN_TEXT_PT = 7.0
COMPACT_TOP = 0.947
COMPACT_BOTTOM = 0.15
COMPACT_HSPACE = 0.30
LOWER_ROW_TITLE_PAD = 15.5  # points; clears k-group labels above LT/SW titles
MIN_ROW_GAP_MM = 3.0

OFF = "#1F4E79"
ON = "#C46B2C"
INK = "#1C242B"
MUTED = "#5C6B76"
GRID = "#E3E8EC"
BAND = ("#F3F6F9", "#F8F5F1")

# Proposal, not the frozen display list. Ordered by k, then h.
# Every point is legal for both SW and LT at m=20 with 25 runs.
DISPLAY = (
    (2, 1),
    (2, 2),
    (2, 4),
    (4, 1),
    (4, 2),
    (4, 3),
    (8, 1),
    (8, 2),
)
GROUPS = ((2, 0, 2), (4, 3, 5), (8, 6, 7))
INDEX = {pair: i for i, pair in enumerate(DISPLAY)}

PATTERNS = {
    "a": np.array([8, 2, 5, 1, 3, 6, 4, 9], dtype=float),
    "b": np.array([3, 6, 1, 5, 8, 2, 7, 4], dtype=float),
    "c": np.array([9, 4, 6, 3, 1, 5, 8, 7], dtype=float),
    "d": np.array([2, 7, 3, 8, 4, 1, 5, 6], dtype=float),
}

# dataset, n, demand, family, off measured, off predicted, on measured,
# on predicted, off pattern, on pattern, On level shift at the n=100 token
# scale. n=500 multiplies that shift by 3. The shift only moves the whole
# On-cold measured series so the sample is not a uniform discount of Off.
SPECS = (
    ("DL20", 100, "Full", "SW", (4, 2), (4, 3), (4, 1), (4, 1), "a", "c", -7000),
    ("DL20", 100, "LIMIT10", "SW", (2, 2), (2, 2), (8, 2), (2, 1), "b", "d", 16000),
    ("DL20", 100, "Full", "LT", (8, 1), (2, 1), (4, 2), (4, 3), "c", "a", 9000),
    ("DL20", 100, "LIMIT10", "LT", (4, 1), (4, 1), (2, 4), (2, 4), "d", "b", -12000),
    ("DL20", 500, "Full", "SW", (4, 3), (8, 2), (2, 2), (2, 4), "b", "d", 18000),
    ("DL20", 500, "LIMIT10", "SW", (8, 1), (8, 1), (4, 2), (2, 1), "a", "c", -5000),
    ("DL20", 500, "Full", "LT", (2, 4), (8, 2), (8, 2), (8, 2), "d", "b", 14000),
    ("DL20", 500, "LIMIT10", "LT", (4, 2), (2, 2), (4, 3), (4, 1), "c", "a", -11000),
    ("TREC-COVID", 100, "Full", "SW", (2, 1), (2, 4), (4, 2), (4, 2), "c", "a", 11000),
    ("TREC-COVID", 100, "LIMIT10", "SW", (8, 2), (2, 1), (2, 2), (8, 1), "d", "b", -8000),
    ("TREC-COVID", 100, "Full", "LT", (4, 3), (4, 3), (8, 1), (2, 2), "a", "c", 15000),
    ("TREC-COVID", 100, "LIMIT10", "LT", (8, 2), (4, 1), (2, 4), (8, 2), "b", "d", -14000),
    ("TREC-COVID", 500, "Full", "SW", (4, 1), (8, 1), (8, 1), (8, 1), "d", "b", 6000),
    ("TREC-COVID", 500, "LIMIT10", "SW", (2, 4), (2, 4), (4, 3), (2, 1), "c", "a", -9000),
    ("TREC-COVID", 500, "Full", "LT", (8, 2), (4, 2), (2, 1), (2, 2), "b", "d", 17000),
    ("TREC-COVID", 500, "LIMIT10", "LT", (4, 2), (4, 2), (8, 2), (8, 2), "a", "c", -3000),
)

HIT_FRAC = np.array([0.22, 0.11, 0.31, 0.16, 0.08, 0.27, 0.13, 0.19])
HIT_FRAC_HAT = np.array([0.09, 0.24, 0.14, 0.33, 0.18, 0.07, 0.29, 0.12])

plt.rcParams.update(
    {
        "font.family": "Liberation Serif",
        "mathtext.fontset": "dejavusans",
        "font.size": 8,
        "axes.labelsize": 8,
        "axes.titlesize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "axes.edgecolor": "#C5CED4",
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.unicode_minus": False,
        "savefig.pad_inches": 0,
    }
)


def segment_cap(family: str, k: int, m: int = 20) -> int:
    """Same cap the merge planner uses: SW is m//k, LT is max_segment."""
    if family == "SW":
        return m // k
    return m // (1 + (k - 1).bit_length())


def legal_domain(family: str, m: int = 20, runs: int = 25) -> list[tuple[int, int]]:
    points = []
    for k in range(2, runs + 1):
        cap = segment_cap(family, k, m)
        if cap < 1:
            continue
        points.extend((k, h) for h in range(1, cap + 1))
    return points


def build_curve(min_idx: int, pattern: str, scale: float, lift: float) -> np.ndarray:
    raw = PATTERNS[pattern].copy()
    raw -= raw.min()
    raw += 4.0
    raw[min_idx] = 0.0
    for i in range(raw.size):
        if i != min_idx and raw[i] < 3.5:
            raw[i] = 3.5 + (i % 3) * 0.45
    tokens = np.rint(raw * scale + lift).astype(int)
    if int(tokens[min_idx]) != int(tokens.min()) or int(np.count_nonzero(tokens == tokens.min())) != 1:
        raise RuntimeError(f"minimum is not unique at {min_idx}: {tokens.tolist()}")
    return tokens


def decompose(cost: np.ndarray, fractions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Split a positive U-Q series into integers U and Q with Q > 0."""
    safe = np.clip(fractions, 0.05, 0.45)
    u_values = np.rint(cost / (1.0 - safe)).astype(int)
    q_values = u_values - cost
    if np.any(q_values <= 0) or np.any(u_values - q_values != cost):
        raise RuntimeError("failed to decompose U-Q")
    return u_values, q_values


def make_panels() -> list[dict]:
    panels = []
    for spec_i, spec in enumerate(SPECS):
        dataset, n, demand, family, off_meas, off_pred, on_meas, on_pred, off_pat, on_pat, shift = spec
        scale = 3400 if n == 100 else 11200
        lift = {100: {"Full": 52000, "LIMIT10": 58000}, 500: {"Full": 175000, "LIMIT10": 158000}}[n][demand]
        on_shift = shift if n == 100 else shift * 3
        off_cost = build_curve(INDEX[off_meas], off_pat, scale, lift)
        on_cost = build_curve(INDEX[on_meas], on_pat, scale, lift + on_shift)
        # Selection scores stay in token units but sit far from the measured
        # series, so a swapped y-axis cannot pass the height check by accident.
        pred_gap = 150000 if n == 100 else 500000
        pred_off = build_curve(INDEX[off_pred], on_pat, scale, lift + pred_gap)
        pred_on = build_curve(INDEX[on_pred], off_pat, scale, lift + on_shift + pred_gap + 20000)
        turn = spec_i % HIT_FRAC.size
        q_frac = np.roll(HIT_FRAC, turn)
        qhat_frac = np.roll(HIT_FRAC_HAT, (turn + 3) % HIT_FRAC.size)
        u_on, q_on = decompose(on_cost, q_frac)
        uhat_on, qhat_on = decompose(pred_on, qhat_frac)
        if np.any(qhat_on == q_on):
            qhat_on = qhat_on + 1
            uhat_on = pred_on + qhat_on
        panel = {
            "dataset": dataset,
            "query_slot": "representative-1",
            "model": "9B",
            "n": n,
            "demand": demand,
            "family": family,
            "beta": 0,
            "off_measured_kh": list(off_meas),
            "off_predicted_kh": list(off_pred),
            "on_measured_kh": list(on_meas),
            "on_predicted_kh": list(on_pred),
            "synthetic_on_level_shift_tokens": int(on_shift),
            "points": [],
        }
        for i, (k, h) in enumerate(DISPLAY):
            panel["points"].append(
                {
                    "k": k,
                    "h": h,
                    "U_off": int(off_cost[i]),
                    "Q_off": 0,
                    "measured_off_U": int(off_cost[i]),
                    "Uhat_off": int(pred_off[i]),
                    "predicted_off_U": int(pred_off[i]),
                    "U_on": int(u_on[i]),
                    "Q_on": int(q_on[i]),
                    "measured_on_U_minus_Q": int(on_cost[i]),
                    "Uhat_on": int(uhat_on[i]),
                    "Qhat_on": int(qhat_on[i]),
                    "predicted_on_U_minus_Q": int(pred_on[i]),
                }
            )
        panels.append(panel)
    return panels


def series(panel: dict, key: str) -> np.ndarray:
    return np.array([point[key] for point in panel["points"]], dtype=int)


def validate(panels: list[dict]) -> None:
    sw = legal_domain("SW")
    lt = legal_domain("LT")
    if len(sw) != 46 or len(lt) != 101:
        raise RuntimeError(f"legal domain drifted: SW {len(sw)} LT {len(lt)}")
    legal = set(sw) & set(lt)
    if list(DISPLAY) != sorted(DISPLAY, key=lambda kh: (kh[0], kh[1])):
        raise RuntimeError("display axis is not grouped by k then h")
    if any(pair not in legal for pair in DISPLAY):
        raise RuntimeError("a display category is outside the shared legal domain")

    below = 0
    crossings = 0
    far = 0
    coincide = {"off": 0, "on": 0}
    separate = {"off": 0, "on": 0}
    for panel in panels:
        off = series(panel, "measured_off_U")
        on = series(panel, "measured_on_U_minus_Q")
        pred_off = series(panel, "predicted_off_U")
        pred_on = series(panel, "predicted_on_U_minus_Q")
        q_on = series(panel, "Q_on")
        qhat = series(panel, "Qhat_on")
        u_on = series(panel, "U_on")
        if np.any(u_on - q_on != on):
            raise RuntimeError("On-cold measured series is not U-Q")
        if np.any(qhat == q_on):
            raise RuntimeError("predicted Q copies measured Q")
        if np.any(off <= 0) or np.any(on <= 0):
            raise RuntimeError("non-positive measured cost")
        roles = {
            "off": (tuple(panel["off_measured_kh"]), tuple(panel["off_predicted_kh"]), off, pred_off),
            "on": (tuple(panel["on_measured_kh"]), tuple(panel["on_predicted_kh"]), on, pred_on),
        }
        for state, (meas_kh, pred_kh, measured, predicted) in roles.items():
            meas_i = INDEX[meas_kh]
            pred_i = INDEX[pred_kh]
            if int(measured.argmin()) != meas_i or int(predicted.argmin()) != pred_i:
                raise RuntimeError(f"argmin drifted for {panel['dataset']} {state}")
            if abs(int(measured[pred_i]) - int(predicted[pred_i])) < 1000:
                raise RuntimeError("predicted height is too close to the measured height")
            if abs(int(measured[meas_i]) - int(predicted[meas_i])) < 1000:
                raise RuntimeError("measured minimum height matches the predicted score")
            if meas_kh == pred_kh:
                coincide[state] += 1
            else:
                separate[state] += 1
                if abs(meas_i - pred_i) >= 4:
                    far += 1
        if np.median(on) < np.median(off):
            below += 1
        if np.any(np.diff(np.sign(on - off)) != 0):
            crossings += 1
    if not (4 <= below <= 12):
        raise RuntimeError(f"On-vs-Off level story is one-sided ({below} panels)")
    if crossings < 4:
        raise RuntimeError(f"curves rarely cross ({crossings})")
    if far < 4 or min(coincide.values()) < 2 or min(separate.values()) < 2:
        raise RuntimeError(f"role variety is too thin: coincide {coincide} separate {separate} far {far}")


def shared_limits(panels: list[dict]) -> dict[int, tuple[float, float]]:
    limits = {}
    for n in (100, 500):
        values = []
        for panel in panels:
            if panel["n"] != n:
                continue
            values.extend(series(panel, "measured_off_U").tolist())
            values.extend(series(panel, "measured_on_U_minus_Q").tolist())
        lo, hi = min(values), max(values)
        span = hi - lo
        limits[n] = ((lo - 0.10 * span) / 1000.0, (hi + 0.22 * span) / 1000.0)
    return limits


def nice_ticks(lo: float, hi: float) -> np.ndarray:
    span = hi - lo
    step = 10 if span <= 90 else 20 if span <= 180 else 50
    start = np.ceil(lo / step) * step
    stop = np.floor(hi / step) * step
    ticks = np.arange(start, stop + step * 0.5, step)
    if ticks.size < 3:
        step = max(step // 2, 5)
        start = np.ceil(lo / step) * step
        stop = np.floor(hi / step) * step
        ticks = np.arange(start, stop + step * 0.5, step)
    return ticks


def marker_plan(panel: dict) -> list[dict]:
    plan = []
    binding = (
        ("off", tuple(panel["off_measured_kh"]), tuple(panel["off_predicted_kh"]), "measured_off_U", "predicted_off_U"),
        ("on", tuple(panel["on_measured_kh"]), tuple(panel["on_predicted_kh"]), "measured_on_U_minus_Q", "predicted_on_U_minus_Q"),
    )
    for state, meas_kh, pred_kh, measured_key, predicted_key in binding:
        measured = series(panel, measured_key)
        predicted = series(panel, predicted_key)
        meas_i = INDEX[meas_kh]
        pred_i = INDEX[pred_kh]
        if pred_i == meas_i:
            kinds = (("both", pred_i),)
        else:
            kinds = (("predicted", pred_i), ("measured", meas_i))
        for kind, index in kinds:
            plotted = int(measured[index])
            plan.append(
                {
                    "state": state,
                    "kind": kind,
                    "k": DISPLAY[index][0],
                    "h": DISPLAY[index][1],
                    "index": index,
                    "plotted_tokens": plotted,
                    "predicted_tokens_not_plotted": int(predicted[index]),
                    "measured_minimum_tokens": int(measured[meas_i]),
                }
            )
            if plotted != int(measured[index]):
                raise RuntimeError("marker left the measured series")
            if plotted == int(predicted[index]):
                raise RuntimeError("marker landed on the predicted height")
            if kind == "predicted":
                extra = plotted - int(measured[meas_i])
                plan[-1]["extra_measured_tokens"] = int(extra)
                plan[-1]["extra_measured_percent"] = round(100.0 * extra / int(measured[meas_i]), 1)
    return plan


class CoincideHandler(HandlerBase):
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        artists = []
        for frac, color in ((0.30, OFF), (0.74, ON)):
            cx = xdescent + width * frac
            cy = ydescent + height * 0.50
            artists.append(
                Line2D(
                    [cx],
                    [cy],
                    marker="D",
                    linestyle="None",
                    markersize=6.2,
                    markerfacecolor="white",
                    markeredgecolor=color,
                    markeredgewidth=0.9,
                    transform=trans,
                )
            )
            artists.append(
                Line2D(
                    [cx],
                    [cy],
                    marker="*",
                    linestyle="None",
                    markersize=8.0,
                    color=color,
                    markerfacecolor=color,
                    markeredgecolor="white",
                    markeredgewidth=0.4,
                    transform=trans,
                )
            )
        return artists


def draw_markers(ax, panel: dict, records: list[dict]) -> None:
    measured = {
        "off": series(panel, "measured_off_U") / 1000.0,
        "on": series(panel, "measured_on_U_minus_Q") / 1000.0,
    }
    for mark in marker_plan(panel):
        color = OFF if mark["state"] == "off" else ON
        x = mark["index"]
        y = measured[mark["state"]][x]
        if abs(y * 1000 - mark["plotted_tokens"]) > 0.1:
            raise RuntimeError("display scale drifted off the measured token count")
        if mark["kind"] in ("predicted", "both"):
            ax.plot(
                [x],
                [y],
                linestyle="None",
                marker="D",
                markersize=6.4,
                markerfacecolor="white",
                markeredgecolor=color,
                markeredgewidth=1.05,
                zorder=5,
            )
        if mark["kind"] in ("measured", "both"):
            ax.plot(
                [x],
                [y],
                linestyle="None",
                marker="*",
                markersize=9.2,
                color=color,
                markeredgecolor="white",
                markeredgewidth=0.45,
                zorder=6,
            )
        records.append({**mark, "figure_y_thousands": round(float(y), 3)})
        # Extra measured tokens stay in the marker record. Drawn callouts sat on
        # the role markers at 178 mm, so they are not painted onto the curves.


def draw_groups(ax) -> None:
    transform = blended_transform_factory(ax.transData, ax.transAxes)
    for band, (k, start, stop) in enumerate(GROUPS):
        ax.axvspan(start - 0.5, stop + 0.5, color=BAND[band % 2], zorder=0, lw=0)
        bracket_y = -0.20
        x0, x1 = start - 0.32, stop + 0.32
        ax.plot([x0, x1], [bracket_y, bracket_y], transform=transform, color="#8B97A1", lw=0.6, clip_on=False)
        ax.plot([x0, x0], [bracket_y, bracket_y + 0.035], transform=transform, color="#8B97A1", lw=0.6, clip_on=False)
        ax.plot([x1, x1], [bracket_y, bracket_y + 0.035], transform=transform, color="#8B97A1", lw=0.6, clip_on=False)
        ax.text(
            (start + stop) / 2,
            -0.25,
            f"k={k}",
            transform=transform,
            ha="center",
            va="top",
            fontsize=7,
            color=INK,
            clip_on=False,
        )


def style_axis(ax, ylim: tuple[float, float], show_y: bool) -> None:
    ax.set_xlim(-0.55, len(DISPLAY) - 0.45)
    ax.set_ylim(*ylim)
    ax.set_xticks(range(len(DISPLAY)))
    ax.set_xticklabels([str(h) for _k, h in DISPLAY])
    ax.set_yticks(nice_ticks(*ylim))
    ax.yaxis.grid(True, color=GRID, lw=0.45, zorder=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(length=2.4, width=0.5, pad=1.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if not show_y:
        ax.tick_params(labelleft=False)


def panel_title(panel: dict, mode: str) -> str:
    demand = "Full" if panel["demand"] == "Full" else "LIMIT10"
    if mode == "compact":
        return f"{panel['family']}, {demand}"
    if mode == "dataset":
        return f"{panel['family']}  ·  {demand}  ·  n={panel['n']}"
    short = "DL20" if panel["dataset"] == "DL20" else "COVID"
    return f"{short}  ·  {demand}  ·  n={panel['n']}"


def add_compact_legend(fig) -> None:
    """One tight legend row; synthetic / axis contract live in the TeX caption."""
    handles = [
        Line2D([0], [0], linestyle="None", marker="D", markersize=5.5, markerfacecolor="white", markeredgecolor=OFF, markeredgewidth=0.95, label="Off pred."),
        Line2D([0], [0], linestyle="None", marker="*", markersize=8, color=OFF, markeredgecolor="white", markeredgewidth=0.35, label="Off min."),
        Line2D([0], [0], linestyle="None", marker="D", markersize=5.5, markerfacecolor="white", markeredgecolor=ON, markeredgewidth=0.95, label="On pred."),
        Line2D([0], [0], linestyle="None", marker="*", markersize=8, color=ON, markeredgecolor="white", markeredgewidth=0.35, label="On min."),
        Line2D([0], [0], color=OFF, lw=1.35, label=r"Off $U$"),
        Line2D([0], [0], color=ON, lw=1.35, label=r"On $U{-}Q$"),
        Line2D([0], [0], linestyle="None", label="both"),
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.988),
        ncol=7,
        frameon=False,
        fontsize=MIN_TEXT_PT,
        handletextpad=0.28,
        columnspacing=0.85,
        borderaxespad=0.2,
        handlelength=1.6,
        handler_map={handles[-1]: CoincideHandler()},
    )


def _assert_compact_row_gap(fig, axes) -> None:
    """k-group labels on the upper row must clear lower-row panel titles (>=3 mm)."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    k_top = max(
        text.get_window_extent(renderer).transformed(fig.transFigure.inverted()).y1
        for ax in axes[0].flat
        for text in ax.texts
        if text.get_text().startswith("k=")
    )
    title_bottom = min(
        ax.title.get_window_extent(renderer).transformed(fig.transFigure.inverted()).y0
        for ax in axes[1].flat
    )
    gap_mm = (title_bottom - k_top) * fig.get_figheight() * 25.4
    if gap_mm < MIN_ROW_GAP_MM:
        raise RuntimeError(f"inter-row gap {gap_mm:.2f} mm < {MIN_ROW_GAP_MM} mm")


def draw_compact_figure(path: Path, grid: list[list[dict]], ylim: tuple[float, float]) -> list[dict]:
    fig, axes = plt.subplots(2, 2, figsize=(WIDTH_IN, HEIGHT_IN), squeeze=False)
    records = []
    for r, row in enumerate(grid):
        for c, panel in enumerate(row):
            ax = axes[r][c]
            xs = np.arange(len(DISPLAY))
            off = series(panel, "measured_off_U") / 1000.0
            on = series(panel, "measured_on_U_minus_Q") / 1000.0
            style_axis(ax, ylim, show_y=(c == 0))
            draw_groups(ax)
            ax.plot(xs, off, color=OFF, lw=1.2, solid_capstyle="round", zorder=2)
            ax.plot(xs, on, color=ON, lw=1.2, solid_capstyle="round", zorder=2)
            draw_markers(ax, panel, records)
            title_pad = LOWER_ROW_TITLE_PAD if r == 1 else 2.5
            ax.set_title(panel_title(panel, "compact"), pad=title_pad, color=INK, fontsize=8)
            if c == 0:
                ax.set_ylabel("tokens ×10³", labelpad=2)
    add_compact_legend(fig)
    fig.subplots_adjust(
        left=0.10,
        right=0.992,
        top=COMPACT_TOP,
        bottom=COMPACT_BOTTOM,
        hspace=COMPACT_HSPACE,
        wspace=0.11,
    )
    _assert_compact_row_gap(fig, axes)
    fig.savefig(path.with_suffix(".pdf"))
    fig.savefig(path.with_suffix(".png"), dpi=PNG_DPI)
    plt.close(fig)
    return records


def add_header(fig, subtitle: str) -> None:
    fig.add_artist(Rectangle((0, 0.955), 1, 0.045, transform=fig.transFigure, facecolor="#FBF1E8", edgecolor="none", zorder=0))
    fig.text(
        0.5,
        0.977,
        "SYNTHETIC DATA  —  not an experimental result. No cache or model advantage is claimed.",
        ha="center",
        va="center",
        fontsize=8,
        color="#7A3419",
        zorder=2,
    )
    role_handles = [
        Line2D([0], [0], linestyle="None", marker="D", markersize=6.2, markerfacecolor="white", markeredgecolor=OFF, markeredgewidth=1.0, label="Off predicted pick"),
        Line2D([0], [0], linestyle="None", marker="*", markersize=9, color=OFF, markeredgecolor="white", markeredgewidth=0.4, label="Off measured minimum"),
        Line2D([0], [0], linestyle="None", marker="D", markersize=6.2, markerfacecolor="white", markeredgecolor=ON, markeredgewidth=1.0, label="On-cold predicted pick"),
        Line2D([0], [0], linestyle="None", marker="*", markersize=9, color=ON, markeredgecolor="white", markeredgewidth=0.4, label="On-cold measured minimum"),
    ]
    line_handles = [
        Line2D([0], [0], color=OFF, lw=1.5, label=r"Off measured ($U$)"),
        Line2D([0], [0], color=ON, lw=1.5, label=r"On-cold measured ($U-Q$)"),
        Line2D([0], [0], linestyle="None", label="both roles, one $(k,h)$"),
    ]
    fig.legend(
        handles=role_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.948),
        ncol=4,
        frameon=False,
        fontsize=7.5,
        handletextpad=0.35,
        columnspacing=1.15,
        borderaxespad=0,
    )
    fig.legend(
        handles=line_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.912),
        ncol=3,
        frameon=False,
        fontsize=7.5,
        handlelength=2.6,
        handletextpad=0.4,
        columnspacing=1.2,
        borderaxespad=0,
        handler_map={line_handles[2]: CoincideHandler()},
    )
    fig.text(0.5, 0.868, subtitle, ha="center", va="center", fontsize=8, color=INK)


def draw_figure(path: Path, grid: list[list[dict]], limits: dict[int, tuple[float, float]], subtitle: str, title_mode: str) -> list[dict]:
    nrows = len(grid)
    ncols = len(grid[0])
    height = 8.55 if nrows == 4 else 4.95
    fig, axes = plt.subplots(nrows, ncols, figsize=(WIDTH_IN, height), squeeze=False)
    records = []
    for r, row in enumerate(grid):
        for c, panel in enumerate(row):
            ax = axes[r][c]
            xs = np.arange(len(DISPLAY))
            off = series(panel, "measured_off_U") / 1000.0
            on = series(panel, "measured_on_U_minus_Q") / 1000.0
            style_axis(ax, limits[panel["n"]], show_y=(c == 0))
            draw_groups(ax)
            ax.plot(xs, off, color=OFF, lw=1.25, solid_capstyle="round", zorder=2)
            ax.plot(xs, on, color=ON, lw=1.25, solid_capstyle="round", zorder=2)
            draw_markers(ax, panel, records)
            ax.set_title(panel_title(panel, title_mode), pad=3, color=INK, fontsize=8)
            if c == 0:
                # One short line. A longer label was clipped by the panel height at 178 mm.
                ax.set_ylabel("tokens ×10³", labelpad=3)
    add_header(fig, subtitle)
    fig.text(
        0.5,
        0.012,
        "Category axis, grouped by k; ticks are h. Lines join this display subset only. Omitted legal (k, h) are not interpolated. Same n shares one y scale.",
        ha="center",
        va="bottom",
        fontsize=6.5,
        color=MUTED,
    )
    top = 0.845 if nrows == 4 else 0.785
    bottom = 0.078 if nrows == 4 else 0.115
    hspace = 0.72 if nrows == 4 else 0.58
    wspace = 0.12 if ncols == 2 else 0.16
    fig.subplots_adjust(left=0.102, right=0.988, top=top, bottom=bottom, hspace=hspace, wspace=wspace)
    fig.savefig(path.with_suffix(".pdf"))
    fig.savefig(path.with_suffix(".png"), dpi=PNG_DPI)
    plt.close(fig)
    return records


def layout_grids(panels: list[dict]) -> dict[str, list[list[dict]]]:
    by_key = {(p["dataset"], p["n"], p["demand"], p["family"]): p for p in panels}

    def cell(dataset, n, demand, family):
        return by_key[(dataset, n, demand, family)]

    grids = {
        "e4a-layout-a-dl20": [
            [cell("DL20", 100, "Full", "SW"), cell("DL20", 100, "LIMIT10", "SW")],
            [cell("DL20", 100, "Full", "LT"), cell("DL20", 100, "LIMIT10", "LT")],
            [cell("DL20", 500, "Full", "SW"), cell("DL20", 500, "LIMIT10", "SW")],
            [cell("DL20", 500, "Full", "LT"), cell("DL20", 500, "LIMIT10", "LT")],
        ],
        "e4a-layout-a-trec-covid": [
            [cell("TREC-COVID", 100, "Full", "SW"), cell("TREC-COVID", 100, "LIMIT10", "SW")],
            [cell("TREC-COVID", 100, "Full", "LT"), cell("TREC-COVID", 100, "LIMIT10", "LT")],
            [cell("TREC-COVID", 500, "Full", "SW"), cell("TREC-COVID", 500, "LIMIT10", "SW")],
            [cell("TREC-COVID", 500, "Full", "LT"), cell("TREC-COVID", 500, "LIMIT10", "LT")],
        ],
        "e4a-layout-b-sw": [
            [
                cell("DL20", 100, "Full", "SW"),
                cell("DL20", 100, "LIMIT10", "SW"),
                cell("TREC-COVID", 100, "Full", "SW"),
                cell("TREC-COVID", 100, "LIMIT10", "SW"),
            ],
            [
                cell("DL20", 500, "Full", "SW"),
                cell("DL20", 500, "LIMIT10", "SW"),
                cell("TREC-COVID", 500, "Full", "SW"),
                cell("TREC-COVID", 500, "LIMIT10", "SW"),
            ],
        ],
        "e4a-layout-b-lt": [
            [
                cell("DL20", 100, "Full", "LT"),
                cell("DL20", 100, "LIMIT10", "LT"),
                cell("TREC-COVID", 100, "Full", "LT"),
                cell("TREC-COVID", 100, "LIMIT10", "LT"),
            ],
            [
                cell("DL20", 500, "Full", "LT"),
                cell("DL20", 500, "LIMIT10", "LT"),
                cell("TREC-COVID", 500, "Full", "LT"),
                cell("TREC-COVID", 500, "LIMIT10", "LT"),
            ],
        ],
    }
    return grids


def subtitles() -> dict[str, tuple[str, str]]:
    scale = "same n shares one y scale"
    return {
        "e4a-layout-a-dl20": (
            "dataset",
            "Proposal A  ·  DL20  ·  one representative query  ·  9B  ·  β = 0  ·  " + scale,
        ),
        "e4a-layout-a-trec-covid": (
            "dataset",
            "Proposal A  ·  TREC-COVID  ·  one representative query  ·  9B  ·  β = 0  ·  " + scale,
        ),
        "e4a-layout-b-sw": (
            "family",
            "Proposal B  ·  SW  ·  both datasets  ·  9B  ·  β = 0  ·  " + scale,
        ),
        "e4a-layout-b-lt": (
            "family",
            "Proposal B  ·  LT  ·  both datasets  ·  9B  ·  β = 0  ·  " + scale,
        ),
    }


def pdf_page_mm(path: Path) -> tuple[float, float]:
    raw = path.read_bytes()
    marker = b"/MediaBox"
    start = raw.rfind(marker)
    if start < 0:
        raise RuntimeError(f"no MediaBox in {path}")
    box = raw[start : start + 80]
    nums = []
    token = ""
    for byte in box:
        char = chr(byte)
        if char.isdigit() or char == ".":
            token += char
        elif token:
            nums.append(float(token))
            token = ""
        if len(nums) == 4:
            break
    width_pt = nums[2] - nums[0]
    height_pt = nums[3] - nums[1]
    return width_pt / 72.0 * 25.4, height_pt / 72.0 * 25.4


def compact_layout_grids(panels: list[dict]) -> dict[str, tuple[list[list[dict]], int]]:
    by_key = {(p["dataset"], p["n"], p["demand"], p["family"]): p for p in panels}

    def cell(dataset, n, demand, family):
        return by_key[(dataset, n, demand, family)]

    specs = (
        ("e4a-compact-dl20-n100", "DL20", 100),
        ("e4a-compact-dl20-n500", "DL20", 500),
        ("e4a-compact-trec-covid-n100", "TREC-COVID", 100),
        ("e4a-compact-trec-covid-n500", "TREC-COVID", 500),
    )
    out = {}
    for name, dataset, n in specs:
        grid = [
            [cell(dataset, n, "Full", "SW"), cell(dataset, n, "LIMIT10", "SW")],
            [cell(dataset, n, "Full", "LT"), cell(dataset, n, "LIMIT10", "LT")],
        ]
        out[name] = (grid, n)
    return out


def assert_display_subset_minima(panels_in_fig: list[dict]) -> None:
    """Stars mark the minimum over the eight displayed categories only."""
    for panel in panels_in_fig:
        for state, meas_kh, measured_key in (
            ("off", tuple(panel["off_measured_kh"]), "measured_off_U"),
            ("on", tuple(panel["on_measured_kh"]), "measured_on_U_minus_Q"),
        ):
            vals = series(panel, measured_key)
            idx = INDEX[meas_kh]
            if int(vals[idx]) != int(vals.min()):
                raise RuntimeError(f"{panel['family']} {panel['demand']} {state}: star is not subset minimum")


def main() -> None:
    panels = make_panels()
    validate(panels)
    limits = shared_limits(panels)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    drawn = {}
    for name, (grid, n) in compact_layout_grids(panels).items():
        flat = [p for row in grid for p in row]
        assert_display_subset_minima(flat)
        records = draw_compact_figure(FIG_DIR / name, grid, limits[n])
        drawn[name] = records
        pdf = FIG_DIR / f"{name}.pdf"
        w_mm, h_mm = pdf_page_mm(pdf)
        if abs(w_mm - WIDTH_MM) > 0.2:
            raise RuntimeError(f"{name}.pdf width is {w_mm:.2f} mm")
        if not (90.0 <= h_mm <= 105.0):
            raise RuntimeError(f"{name}.pdf height is {h_mm:.2f} mm (want 90--105)")
        png = FIG_DIR / f"{name}.png"
        expected = round(WIDTH_IN * PNG_DPI)
        with png.open("rb") as handle:
            handle.seek(16)
            pixel_width = int.from_bytes(handle.read(4), "big")
        if abs(pixel_width - expected) > 1:
            raise RuntimeError(f"{name}.png width {pixel_width}px, expected {expected}")

    for name, records in drawn.items():
        for mark in records:
            if mark["plotted_tokens"] == mark["predicted_tokens_not_plotted"]:
                raise RuntimeError(f"{name} plotted a predicted height")

    payload = {
        "status": "synthetic-layout-sample",
        "not_experimental_result": True,
        "no_advantage_claim": True,
        "unit": "input tokens",
        "currency": None,
        "beta": 0,
        "off_measured": "U",
        "on_cold_measured": "U-Q",
        "predicted_scores_are_selection_only": True,
        "markers_use_measured_height": True,
        "measured_minimum_is_display_subset_only": True,
        "display_categories": [{"k": k, "h": h} for k, h in DISPLAY],
        "display_is_proposal": True,
        "legal_domain_m20_25runs": {"SW": 46, "LT": 101},
        "omitted_legal_points_are_not_interpolated": True,
        "dataset_name_assumption": (
            "Experiment 4a says two datasets and one representative query each, "
            "without naming the datasets in that paragraph. DL20 and TREC-COVID "
            "are the pair named for experiments 2 and 5."
        ),
        "shared_y_thousands": {str(n): [round(limits[n][0], 2), round(limits[n][1], 2)] for n in limits},
        "primary_figures": list(compact_layout_grids(panels).keys()),
        "legacy_reference_figures_untouched": [
            "e4a-layout-a-dl20",
            "e4a-layout-a-trec-covid",
            "e4a-layout-b-sw",
            "e4a-layout-b-lt",
        ],
        "panels": panels,
        "markers_by_figure": drawn,
    }
    DATA_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {DATA_PATH}")
    for n, pair in limits.items():
        print(f"y n={n}: {pair[0]:.1f} .. {pair[1]:.1f} ×10³")
    for name in drawn:
        w_mm, h_mm = pdf_page_mm(FIG_DIR / (name + ".pdf"))
        print(f"{name}: {w_mm:.2f} x {h_mm:.2f} mm, {len(drawn[name])} markers")


if __name__ == "__main__":
    main()
