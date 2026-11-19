"""E4a: single-column Off / On-cold curves with a full (k, h) axis.

n=500 display values are copied from the existing synthetic JSON.
n=100 is regenerated with the same generator because (8, 1) and (8, 2)
are illegal when m=20 leaves only 5 runs. Those roles move to (5, 1)
and (5, 2). Real selection is still deferred: minima are over the
displayed categories only.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from legal import assert_legal, is_legal
from pdfutil import configure_matplotlib, overflow_labels, overlapping_tick_labels
from style import COLUMN_PT, GRID_RGB, pt_to_in, printed

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[1] / "recovery" / "e4a" / "data" / "e4a_synthetic.json"

LINE_PT = 1.1
MARKER_LINE_PT = 2.8
EDGE_PT = printed(1.0, 0.33)
GRID_PT = 0.35
GRID_RGB = "#D6D6D6"
SPINE_PT = 0.65
TICK_W = printed(0.8, 0.33)
TICK_LEN = max(printed(2.2, 0.33), 2.0)
STAR_PT = 5.5
DIAMOND_PT = 9.0
# Column-width category labels need to stay at the original printed
# label size, not the native 11 pt canvas size.
TICK_FONT = 7.2
LABEL_FONT = 7.4

OFF = "#1F77B4"
ON = "#FF7F0E"

DISPLAY_500 = ((2, 1), (2, 2), (2, 4), (4, 1), (4, 2), (4, 3), (8, 1), (8, 2))
DISPLAY_100 = ((2, 1), (2, 2), (2, 4), (4, 1), (4, 2), (4, 3), (5, 1), (5, 2))
REMAP_100 = {(8, 1): (5, 1), (8, 2): (5, 2)}

PATTERNS = {
    "a": np.array([8, 2, 5, 1, 3, 6, 4, 9], dtype=float),
    "b": np.array([3, 6, 1, 5, 8, 2, 7, 4], dtype=float),
    "c": np.array([9, 4, 6, 3, 1, 5, 8, 7], dtype=float),
    "d": np.array([2, 7, 3, 8, 4, 1, 5, 6], dtype=float),
}
HIT_FRAC = np.array([0.22, 0.11, 0.31, 0.16, 0.08, 0.27, 0.13, 0.19])
HIT_FRAC_HAT = np.array([0.09, 0.24, 0.14, 0.33, 0.18, 0.07, 0.29, 0.12])

# dataset, n, demand, family, off measured, off predicted, on measured,
# on predicted, off pattern, on pattern, On level shift at n=100.
SPECS = (
    ("DL20", 100, "Full", "SW", (4, 2), (4, 3), (4, 1), (4, 1), "a", "c", -7000),
    ("DL20", 100, "LIMIT10", "SW", (2, 2), (2, 2), (8, 2), (2, 1), "b", "d", 16000),
    ("DL20", 100, "Full", "LT", (8, 1), (2, 1), (4, 2), (4, 3), "c", "a", 9000),
    ("DL20", 100, "LIMIT10", "LT", (4, 1), (4, 1), (2, 4), (2, 4), "d", "b", -12000),
    ("TREC-COVID", 100, "Full", "SW", (2, 1), (2, 4), (4, 2), (4, 2), "c", "a", 11000),
    ("TREC-COVID", 100, "LIMIT10", "SW", (8, 2), (2, 1), (2, 2), (8, 1), "d", "b", -8000),
    ("TREC-COVID", 100, "Full", "LT", (4, 3), (4, 3), (8, 1), (2, 2), "a", "c", 15000),
    ("TREC-COVID", 100, "LIMIT10", "LT", (8, 2), (4, 1), (2, 4), (8, 2), "b", "d", -14000),
)


def _remap(pair: tuple[int, int]) -> tuple[int, int]:
    return REMAP_100.get(pair, pair)


def _build_curve(min_idx: int, pattern: str, scale: float, lift: float) -> np.ndarray:
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


def _decompose(cost: np.ndarray, fractions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    safe = np.clip(fractions, 0.05, 0.45)
    u_values = np.rint(cost / (1.0 - safe)).astype(int)
    q_values = u_values - cost
    if np.any(q_values <= 0) or np.any(u_values - q_values != cost):
        raise RuntimeError("failed to decompose U-Q")
    return u_values, q_values


def synthesize_n100() -> list[dict]:
    index = {pair: i for i, pair in enumerate(DISPLAY_100)}
    panels = []
    for spec_i, spec in enumerate(SPECS):
        dataset, n, demand, family, off_meas, off_pred, on_meas, on_pred, off_pat, on_pat, shift = spec
        off_meas, off_pred = _remap(off_meas), _remap(off_pred)
        on_meas, on_pred = _remap(on_meas), _remap(on_pred)
        for pair in (off_meas, off_pred, on_meas, on_pred):
            if pair not in index:
                raise RuntimeError(f"role {pair} missing from the n=100 axis")
            assert_legal(family, [pair], n)
        scale = 3400
        lift = {"Full": 52000, "LIMIT10": 58000}[demand]
        off_cost = _build_curve(index[off_meas], off_pat, scale, lift)
        on_cost = _build_curve(index[on_meas], on_pat, scale, lift + shift)
        pred_gap = 150000
        pred_off = _build_curve(index[off_pred], on_pat, scale, lift + pred_gap)
        pred_on = _build_curve(index[on_pred], off_pat, scale, lift + shift + pred_gap + 20000)
        turn = spec_i % HIT_FRAC.size
        u_on, q_on = _decompose(on_cost, np.roll(HIT_FRAC, turn))
        uhat_on, qhat_on = _decompose(pred_on, np.roll(HIT_FRAC_HAT, (turn + 3) % HIT_FRAC.size))
        if np.any(qhat_on == q_on):
            qhat_on = qhat_on + 1
            uhat_on = pred_on + qhat_on
        points = []
        for i, (k, h) in enumerate(DISPLAY_100):
            points.append(
                {
                    "k": k,
                    "h": h,
                    "measured_off_U": int(off_cost[i]),
                    "predicted_off_U": int(pred_off[i]),
                    "measured_on_U_minus_Q": int(on_cost[i]),
                    "predicted_on_U_minus_Q": int(pred_on[i]),
                    "U_on": int(u_on[i]),
                    "Q_on": int(q_on[i]),
                }
            )
        panels.append(
            {
                "dataset": dataset,
                "n": n,
                "demand": demand,
                "family": family,
                "off_measured_kh": list(off_meas),
                "off_predicted_kh": list(off_pred),
                "on_measured_kh": list(on_meas),
                "on_predicted_kh": list(on_pred),
                "points": points,
                "regenerated_because": "n=100 k=8 is illegal at m=20 (5 runs); (8,1)->(5,1), (8,2)->(5,2)",
            }
        )
    return panels


def load_n500() -> list[dict]:
    payload = json.loads(SOURCE.read_text())
    panels = []
    for panel in payload["panels"]:
        if panel["n"] != 500:
            continue
        pairs = [(p["k"], p["h"]) for p in panel["points"]]
        if pairs != list(DISPLAY_500):
            raise RuntimeError(f"n=500 axis drifted: {pairs}")
        assert_legal(panel["family"], pairs, 500)
        for role in (
            panel["off_measured_kh"],
            panel["off_predicted_kh"],
            panel["on_measured_kh"],
            panel["on_predicted_kh"],
        ):
            if not is_legal(panel["family"], role[0], role[1], 500):
                raise RuntimeError(f"illegal n=500 role {role}")
        copied = []
        for point in panel["points"]:
            if point["U_on"] - point["Q_on"] != point["measured_on_U_minus_Q"]:
                raise RuntimeError("stored On series is not U-Q")
            copied.append(
                {
                    "k": point["k"],
                    "h": point["h"],
                    "measured_off_U": point["measured_off_U"],
                    "predicted_off_U": point["predicted_off_U"],
                    "measured_on_U_minus_Q": point["measured_on_U_minus_Q"],
                    "predicted_on_U_minus_Q": point["predicted_on_U_minus_Q"],
                    "U_on": point["U_on"],
                    "Q_on": point["Q_on"],
                }
            )
        panels.append(
            {
                "dataset": panel["dataset"],
                "n": 500,
                "demand": panel["demand"],
                "family": panel["family"],
                "off_measured_kh": list(panel["off_measured_kh"]),
                "off_predicted_kh": list(panel["off_predicted_kh"]),
                "on_measured_kh": list(panel["on_measured_kh"]),
                "on_predicted_kh": list(panel["on_predicted_kh"]),
                "points": copied,
                "copied_from": str(SOURCE),
            }
        )
    if len(panels) != 8:
        raise RuntimeError(f"expected 8 n=500 panels, got {len(panels)}")
    return panels


def _validate(panel: dict) -> None:
    off = np.array([p["measured_off_U"] for p in panel["points"]])
    on = np.array([p["measured_on_U_minus_Q"] for p in panel["points"]])
    pred_off = np.array([p["predicted_off_U"] for p in panel["points"]])
    pred_on = np.array([p["predicted_on_U_minus_Q"] for p in panel["points"]])
    labels = [(p["k"], p["h"]) for p in panel["points"]]
    if int(off.argmin()) != labels.index(tuple(panel["off_measured_kh"])):
        raise RuntimeError("Off measured argmin drifted")
    if int(on.argmin()) != labels.index(tuple(panel["on_measured_kh"])):
        raise RuntimeError("On measured argmin drifted")
    if int(pred_off.argmin()) != labels.index(tuple(panel["off_predicted_kh"])):
        raise RuntimeError("Off predicted argmin drifted")
    if int(pred_on.argmin()) != labels.index(tuple(panel["on_predicted_kh"])):
        raise RuntimeError("On predicted argmin drifted")
    if np.any(np.abs(pred_off - off) < 1000) or np.any(np.abs(pred_on - on) < 1000):
        raise RuntimeError("predicted score is close enough to be mistaken for a height")
    if panel["n"] == 100 and any(p["k"] >= 6 for p in panel["points"]):
        raise RuntimeError("n=100 axis still contains k>=6")


def _style(ax, labels, ylim, show_x: bool) -> None:
    ax.set_xlim(-0.45, len(labels) - 0.55)
    ax.set_ylim(*ylim)
    ax.set_xticks(range(len(labels)))
    if show_x:
        ax.set_xticklabels([f"({k},{h})" for k, h in labels])
    else:
        ax.set_xticklabels([""] * len(labels))
    ax.set_axisbelow(True)
    ax.grid(True, color=GRID_RGB, linewidth=GRID_PT, zorder=0)
    ax.set_facecolor("white")
    for spine in ax.spines.values():
        spine.set_linewidth(SPINE_PT)
    ax.tick_params(length=TICK_LEN, width=TICK_W, labelsize=TICK_FONT, pad=1.4)
    ax.tick_params(axis="x", labelsize=7.2)


def _mark(ax, x, y, color, role: str) -> None:
    if role == "measured":
        ax.plot(
            [x],
            [y],
            linestyle="none",
            marker="*",
            markersize=STAR_PT,
            markerfacecolor=color,
            markeredgecolor="black",
            markeredgewidth=0.45,
            zorder=5,
        )
    elif role == "predicted":
        ax.plot(
            [x],
            [y],
            linestyle="none",
            marker="D",
            markersize=DIAMOND_PT * 0.72,
            markerfacecolor="none",
            markeredgecolor=color,
            markeredgewidth=0.8,
            zorder=4,
        )
    else:
        raise ValueError(role)


def draw_figure(panels: list[dict]) -> plt.Figure:
    labels = [(p["k"], p["h"]) for p in panels[0]["points"]]
    measured = []
    for panel in panels:
        measured.extend(p["measured_off_U"] for p in panel["points"])
        measured.extend(p["measured_on_U_minus_Q"] for p in panel["points"])
    low, high = min(measured) / 1000.0, max(measured) / 1000.0
    pad = 0.08 * (high - low)
    ylim = (low - pad, high + pad)
    width = pt_to_in(COLUMN_PT)
    height = pt_to_in(300)
    fig = plt.figure(figsize=(width, height))
    legend_handles = [
        Line2D([0], [0], color=OFF, lw=LINE_PT, marker="o", markersize=MARKER_LINE_PT, label="Off"),
        Line2D([0], [0], color=ON, lw=LINE_PT, ls="--", marker="o", markersize=MARKER_LINE_PT, label="On-cold"),
        Line2D([0], [0], color="black", lw=0, marker="*", markersize=5.5, label="Min."),
        Line2D([0], [0], color="black", lw=0, marker="D", markersize=6.5, markerfacecolor="none", label="Pred."),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.54, 0.995),
        ncol=4,
        frameon=False,
        fontsize=7.2,
        handlelength=1.45,
        columnspacing=0.9,
        borderaxespad=0.0,
    )
    # Top to bottom: SW Full, SW LIMIT, LT Full, LT LIMIT.
    order = (("SW", "Full"), ("SW", "LIMIT10"), ("LT", "Full"), ("LT", "LIMIT10"))
    by_key = {(p["family"], p["demand"]): p for p in panels}
    tops = (0.754, 0.544, 0.334, 0.124)
    for (family, demand), top in zip(order, tops):
        panel = by_key[(family, demand)]
        ax = fig.add_axes([0.165, top, 0.81, 0.165])
        show_x = demand == "LIMIT10" and family == "LT"
        _style(ax, labels, ylim, show_x=show_x)
        if show_x:
            ax.set_xlabel(r"configuration $(k,h)$", fontsize=LABEL_FONT, labelpad=1.5)
        
        title = "SW" if family == "SW" else "LT"
        mode = "Full" if demand == "Full" else "LIMIT 10"
        ax.set_title(f"{title}, {mode}", loc="left", fontsize=7.4, pad=1.2, color="black")
        xs = np.arange(len(labels))
        off = np.array([p["measured_off_U"] for p in panel["points"]]) / 1000.0
        on = np.array([p["measured_on_U_minus_Q"] for p in panel["points"]]) / 1000.0
        ax.plot(xs, off, color=OFF, lw=LINE_PT, marker="o", markersize=MARKER_LINE_PT,
                markerfacecolor=OFF, markeredgecolor=OFF, markeredgewidth=EDGE_PT, zorder=3)
        ax.plot(xs, on, color=ON, lw=LINE_PT, ls="--", marker="o", markersize=MARKER_LINE_PT,
                markerfacecolor=ON, markeredgecolor=ON, markeredgewidth=EDGE_PT, zorder=3)
        roles = (
            ("off", OFF, tuple(panel["off_predicted_kh"]), tuple(panel["off_measured_kh"]), off),
            ("on", ON, tuple(panel["on_predicted_kh"]), tuple(panel["on_measured_kh"]), on),
        )
        for _state, color, pred, meas, series in roles:
            pred_i = labels.index(pred)
            meas_i = labels.index(meas)
            # Heights are the measured series. Predicted scores are not drawn.
            if pred == meas:
                _mark(ax, pred_i, series[pred_i], color, "measured")
                _mark(ax, pred_i, series[pred_i], color, "predicted")
            else:
                _mark(ax, pred_i, series[pred_i], color, "predicted")
                _mark(ax, meas_i, series[meas_i], color, "measured")
    fig.text(0.025, 0.53, r"Equivalent input tokens $\times 10^{3}$", rotation=90, ha="center", va="center", fontsize=7.4)
    fig.text(0.55, 0.018, "Synthetic layout sample; not measured", ha="center", fontsize=7.2, color="#555555")
    problems = overflow_labels(fig) + overlapping_tick_labels(fig)
    if problems:
        raise RuntimeError(f"E4a labels: {problems}")
    return fig


def build(out: Path) -> dict:
    configure_matplotlib()
    out.mkdir(parents=True, exist_ok=True)
    n100 = synthesize_n100()
    n500 = load_n500()
    for panel in n100 + n500:
        _validate(panel)
    groups = {}
    for panel in n100 + n500:
        groups.setdefault((panel["dataset"], panel["n"]), []).append(panel)
    written = []
    for (dataset, n), panels in groups.items():
        if len(panels) != 4:
            raise RuntimeError(f"expected 4 panels for {dataset} n={n}")
        fig = draw_figure(panels)
        slug = dataset.lower().replace("trec-", "")
        name = f"e4a-{slug}-n{n}.pdf"
        fig.savefig(out / name)
        fig.savefig(out / f"e4a-{slug}-n{n}.png", dpi=300)
        plt.close(fig)
        written.append(name)
    facts = {
        "source_n500": str(SOURCE),
        "n100_remap": {"(8,1)": "(5,1)", "(8,2)": "(5,2)"},
        "n100_axis": [list(p) for p in DISPLAY_100],
        "n500_axis": [list(p) for p in DISPLAY_500],
        "files": written,
        "line_pt": LINE_PT,
        "minima": "displayed categories only; not the legal-domain argmin",
        "panels": [
            {
                "dataset": p["dataset"],
                "n": p["n"],
                "demand": p["demand"],
                "family": p["family"],
                "off_measured": p["off_measured_kh"],
                "off_predicted": p["off_predicted_kh"],
                "on_measured": p["on_measured_kh"],
                "on_predicted": p["on_predicted_kh"],
            }
            for p in n100 + n500
        ],
    }
    (out / "e4a-facts.json").write_text(json.dumps(facts, indent=2) + "\n")
    (out / "e4a-n100.json").write_text(json.dumps(n100, indent=2) + "\n")
    return facts
