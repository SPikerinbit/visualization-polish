"""E4c: single-column 2 by 2 quality-cost scatter.

Each plotted coordinate is the equal-weight mean of the DL20 and COVID
dataset-level placeholders. Those placeholders already stand in for a
3-query mean; query rows were never stored, so this is not a 6-query
recompute. No per-query cloud.

The red dashed guide is the non-dominated set of those means
(lower equivalent tokens, higher quality). Vertices are exactly those
means. ListK Fig. 4's caption calls its red dotted curve a Pareto
frontier, and that curve also runs off toward the axis; we do not add
those endpoints and we do not fit a curve (Fig. 5's fits stay there).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from pdfutil import configure_matplotlib, overflow_labels, overlapping_tick_labels
from style import COLUMN_PT, GRID_RGB, SW_RGB, pt_to_in, printed

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[1] / "recovery" / "e4c" / "data" / "synthetic_means.json"

GRID_PT = printed(0.765, 0.33)
SPINE_PT = printed(1.36, 0.33)
TICK_W = printed(0.8, 0.33)
TICK_LEN = max(printed(2.2, 0.33), 2.0)
LINE_PT = printed(1.6, 0.33)
MARKER_PT = 5.0
TICK_FONT = 6.2
LABEL_FONT = 7.0
RED = SW_RGB  # the paper's red, drawn dashed so it is not the SW series

# Tableau hues already used as fills in the original panels, with SW and LT
# locked to the original circle / triangle pair. Other methods are one
# mean each, so marker shape carries the identity with the color.
METHODS = (
    {"id": "pointwise", "legend": "Pointwise", "color": "#FF7F0E", "marker": "s"},
    {"id": "ext_pointwise", "legend": "Ext. Pointwise", "color": "#2CA02C", "marker": "P"},
    {"id": "bubble", "legend": "Ext. Bubble", "color": "#9467BD", "marker": "D"},
    {"id": "merge", "legend": "Ext. Merge", "color": "#8C564B", "marker": "v"},
    {"id": "listk", "legend": "ListK", "color": "#CC79A7", "marker": "X"},
    {"id": "tournament", "legend": "Tournament", "color": "#17BECF", "marker": "h"},
    {"id": "lotus", "legend": "Lotus", "color": "#BCBD22", "marker": "*"},
    {"id": "setwise", "legend": "Setwise", "color": "#7F7F7F", "marker": "<"},
    {"id": "sw", "legend": "SW", "color": "#D62728", "marker": "o"},
    {"id": "lt", "legend": "LT", "color": "#1F77B4", "marker": "^"},
)


def load_points() -> list[dict]:
    payload = json.loads(SOURCE.read_text())
    if payload.get("per_query_points") is not False:
        raise RuntimeError("E4c source is not a method-mean table")
    rows = payload["points"]
    expected = {
        (m, d, s, method["id"])
        for m in ("full", "topk")
        for d in ("DL20", "COVID")
        for s in ("Off", "On-cold")
        for method in METHODS
    }
    got = {(r["metric"], r["dataset"], r["state"], r["method"]) for r in rows}
    if got != expected:
        missing = expected - got
        extra = got - expected
        raise RuntimeError(f"E4c coverage mismatch missing={missing} extra={extra}")
    return rows


def average(rows: list[dict]) -> list[dict]:
    """1/2 of the two dataset-level means. Quality and cost stay separate."""
    by_method = {m["id"]: m for m in METHODS}
    out = []
    for metric in ("full", "topk"):
        for state in ("Off", "On-cold"):
            for method in METHODS:
                pair = [
                    r
                    for r in rows
                    if r["metric"] == metric and r["state"] == state and r["method"] == method["id"]
                ]
                if len(pair) != 2 or {r["dataset"] for r in pair} != {"DL20", "COVID"}:
                    raise RuntimeError(f"need both datasets for {metric} {state} {method['id']}")
                out.append(
                    {
                        "metric": metric,
                        "state": state,
                        "method": method["id"],
                        "legend": by_method[method["id"]]["legend"],
                        "x": 0.5 * (pair[0]["x"] + pair[1]["x"]),
                        "y": 0.5 * (pair[0]["y"] + pair[1]["y"]),
                        "x_dl20": next(r["x"] for r in pair if r["dataset"] == "DL20"),
                        "x_covid": next(r["x"] for r in pair if r["dataset"] == "COVID"),
                        "y_dl20": next(r["y"] for r in pair if r["dataset"] == "DL20"),
                        "y_covid": next(r["y"] for r in pair if r["dataset"] == "COVID"),
                    }
                )
    return out


def nondominated(points: list[dict]) -> list[dict]:
    """Lower cost and higher quality. No invented endpoints."""
    keep = []
    for point in points:
        dominated = False
        for other in points:
            if other is point:
                continue
            cheaper_or_eq = other["x"] <= point["x"]
            better_or_eq = other["y"] >= point["y"]
            strict = other["x"] < point["x"] or other["y"] > point["y"]
            if cheaper_or_eq and better_or_eq and strict:
                dominated = True
                break
        if not dominated:
            keep.append(point)
    keep.sort(key=lambda p: (p["x"], -p["y"]))
    # A line through one point would be an invented segment.
    return keep


def _inner_ticks(limits: tuple[float, float], step: float) -> list[float]:
    low, high = limits
    span = high - low
    start = step * (int(low / step) + 1)
    ticks = []
    value = start
    while value < high - 0.06 * span:
        if value > low + 0.04 * span:
            ticks.append(round(value, 4))
        value += step
    return ticks or [round(0.5 * (low + high), 4)]


def _limits(values: list[float], pad: float = 0.10) -> tuple[float, float]:
    low, high = min(values), max(values)
    span = high - low
    return low - pad * span, high + pad * span


def draw(means: list[dict], fronts: dict) -> plt.Figure:
    fig = plt.figure(figsize=(pt_to_in(COLUMN_PT), pt_to_in(310)))
    xs = [p["x"] / 1000.0 for p in means]
    xlim = _limits(xs, 0.08)
    full_y = _limits([p["y"] for p in means if p["metric"] == "full"])
    topk_y = _limits([p["y"] for p in means if p["metric"] == "topk"])
    slots = {
        ("full", "Off"): (0.14, 0.50, "Full, Off", full_y, True, False),
        ("full", "On-cold"): (0.57, 0.50, "Full, On", full_y, False, False),
        ("topk", "Off"): (0.14, 0.14, "LIMIT 10, Off", topk_y, True, True),
        ("topk", "On-cold"): (0.57, 0.14, "LIMIT 10, On", topk_y, False, True),
    }
    by_method = {m["id"]: m for m in METHODS}
    for (metric, state), (left, bottom, title, ylim, show_y, show_x) in slots.items():
        ax = fig.add_axes([left, bottom, 0.36, 0.30])
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_xticks(_inner_ticks(xlim, 10))
        ax.set_yticks(_inner_ticks(ylim, 0.1 if ylim[1] - ylim[0] > 0.2 else 0.05))
        ax.tick_params(labelleft=show_y, labelbottom=show_x)
        ax.set_axisbelow(True)
        ax.grid(True, color=GRID_RGB, linewidth=GRID_PT, zorder=0)
        ax.set_facecolor("white")
        for spine in ax.spines.values():
            spine.set_linewidth(SPINE_PT)
        ax.tick_params(length=TICK_LEN, width=TICK_W, labelsize=TICK_FONT, pad=1.2)
        ax.set_title(title, fontsize=7.0, pad=1.5)
        if show_y:
            ylabel = "Spearman" if metric == "full" else "NDCG@10"
            ax.set_ylabel(ylabel, fontsize=LABEL_FONT)
        if show_x:
            ax.set_xlabel(r"tokens $\times 10^{3}$", fontsize=LABEL_FONT)
        front = fronts[(metric, state)]
        if len(front) >= 2:
            ax.plot(
                [p["x"] / 1000.0 for p in front],
                [p["y"] for p in front],
                color=RED,
                linestyle="--",
                linewidth=LINE_PT,
                zorder=2,
                solid_capstyle="round",
            )
        panel_points = [p for p in means if p["metric"] == metric and p["state"] == state]
        for point in panel_points:
            spec = by_method[point["method"]]
            ax.plot(
                [point["x"] / 1000.0],
                [point["y"]],
                linestyle="none",
                marker=spec["marker"],
                markersize=MARKER_PT if spec["marker"] != "*" else MARKER_PT + 1.4,
                markerfacecolor=spec["color"],
                markeredgecolor="black",
                markeredgewidth=0.35,
                zorder=3,
            )
    handles = [
        Line2D(
            [0],
            [0],
            color=m["color"],
            lw=0,
            marker=m["marker"],
            markersize=4.6 if m["marker"] != "*" else 6.0,
            markerfacecolor=m["color"],
            markeredgecolor="black",
            markeredgewidth=0.3,
            label=m["legend"],
        )
        for m in METHODS
    ]
    handles.append(
        Line2D([0], [0], color=RED, lw=LINE_PT, ls="--", label="Non-dominated")
    )
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.50, 0.988),
        ncol=4,
        frameon=False,
        fontsize=5.5,
        handlelength=1.2,
        columnspacing=0.65,
        borderaxespad=0.0,
    )
    problems = overflow_labels(fig) + overlapping_tick_labels(fig)
    if problems:
        raise RuntimeError(f"E4c labels: {problems}")
    return fig


def build(out: Path) -> dict:
    configure_matplotlib()
    out.mkdir(parents=True, exist_ok=True)
    rows = load_points()
    means = average(rows)
    fronts = {}
    front_note = []
    for metric in ("full", "topk"):
        for state in ("Off", "On-cold"):
            panel = [p for p in means if p["metric"] == metric and p["state"] == state]
            front = nondominated(panel)
            fronts[(metric, state)] = front
            front_note.append(
                {
                    "metric": metric,
                    "state": state,
                    "n_means": len(panel),
                    "n_nondominated": len(front),
                    "line_drawn": len(front) >= 2,
                    "methods_in_order": [p["method"] for p in front],
                    "vertices": [{"method": p["method"], "x": p["x"], "y": p["y"]} for p in front],
                }
            )
    fig = draw(means, fronts)
    fig.savefig(out / "e4c-quality-cost.pdf")
    fig.savefig(out / "e4c-quality-cost.png", dpi=300)
    plt.close(fig)
    facts = {
        "source": str(SOURCE),
        "aggregation": "dataset-level placeholder mean, then DL20 and COVID at weight 1/2",
        "per_query": False,
        "shared_x": True,
        "shared_y_within_metric_only": True,
        "red_line": (
            "Descriptive non-dominated set of the plotted means. "
            "Lower equivalent tokens and higher quality. "
            "Not a fit, not a significance test, no added endpoints."
        ),
        "fronts": front_note,
        "means": means,
        "line_pt": LINE_PT,
    }
    (out / "e4c-facts.json").write_text(json.dumps(facts, indent=2) + "\n")
    return facts
