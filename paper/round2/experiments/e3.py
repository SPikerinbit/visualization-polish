"""E3 scale sample: single-column 4 by 2, prediction split from measured.

Panel PDFs are square at Fig. 8's printed size, ``0.25\\columnwidth``.
SW / LT / Full / LIMIT labels are not drawn inside the panels; ``tex/fig-e3.tex``
sets them, following ``fig:exp4-topk`` in the original ``exp.tex``.

Y values are the existing layout scaffold (constant slope, prediction =
measured + 3.4). They are not tokens. Supplement stars stay in the data
file and are not drawn: a shared axis that reached them would crush the
five series inside a Fig. 8 panel, and they are not optima.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from pdfutil import configure_matplotlib, overflow_labels, overlapping_tick_labels
from style import (
    COLUMN_PT,
    GRID_RGB,
    TABLEAU,
    pt_to_in,
    printed,
)

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[1] / "recovery" / "e3" / "e3_layout_data.json"

PANEL_PT = printed(133.2, 0.25)  # 60.286875, Fig. 8 include box
LINE_PT = printed(1.6, 0.25)
MARKER_PT = printed(4.8, 0.25)
EDGE_PT = printed(1.0, 0.25)
GRID_PT = printed(0.765, 0.25)
SPINE_PT = printed(1.36, 0.25)
TICK_PT = printed(0.8, 0.25)
TICK_LEN = printed(2.2, 0.25)
TICK_FONT = printed(9.0, 0.25)
LABEL_FONT = printed(11.05, 0.25)

MARKERS = ("o", "s", "^", "D", "v")
X = (1000, 5000, 10000)
XLABELS = ("1k", "5k", "10k")

# Printed Fig. 8 type is about 4 pt. A 0.4 pt lift keeps the three labels
# distinguishable on the contact sheet without leaving the original scale.
TICK_FONT_USE = max(TICK_FONT, 4.6)
LABEL_FONT_USE = max(LABEL_FONT, 5.0)


def load() -> dict:
    payload = json.loads(SOURCE.read_text())
    if payload["kind"] != "synthetic_layout_only":
        raise RuntimeError("E3 source is not the synthetic layout scaffold")
    if payload["x"]["values"] != [1000, 5000, 10000]:
        raise RuntimeError("E3 x values changed")
    return payload


def _style_ax(ax, ylim) -> None:
    ax.set_xlim(400, 10600)
    ax.set_ylim(*ylim)
    ax.set_xticks(list(X))
    ax.set_xticklabels(list(XLABELS))
    ax.set_yticks([20, 35, 50, 65])
    ax.set_axisbelow(True)
    ax.grid(True, color=GRID_RGB, linewidth=GRID_PT, zorder=0)
    ax.set_facecolor("white")
    for spine in ax.spines.values():
        spine.set_color("black")
        spine.set_linewidth(SPINE_PT)
    ax.tick_params(
        length=TICK_LEN,
        width=TICK_PT,
        labelsize=TICK_FONT_USE,
        pad=1.0,
        colors="black",
    )
    ax.set_xlabel(r"$n$", fontsize=LABEL_FONT_USE, labelpad=0.6)


def _series_handles(payload) -> list[Line2D]:
    handles = []
    for panel in payload["panels"]:
        if panel["mode"] != "Full":
            continue
        for index, series in enumerate(panel["series"]):
            handles.append(
                Line2D(
                    [0],
                    [0],
                    color=TABLEAU[len(handles)],
                    marker=MARKERS[index],
                    markersize=max(MARKER_PT, 3.2),
                    markerfacecolor=TABLEAU[len(handles)],
                    markeredgecolor=TABLEAU[len(handles)],
                    markeredgewidth=0.4,
                    linewidth=max(LINE_PT, 0.85),
                    label=f"{series['k']},{series['h']}",
                )
            )
    if len(handles) != 10:
        raise RuntimeError(f"expected 10 legend entries, got {len(handles)}")
    return handles


def _ylim(payload) -> tuple[float, float]:
    values = []
    for panel in payload["panels"]:
        for series in panel["series"]:
            values.extend(series["measured"])
            values.extend(series["predicted"])
    low, high = min(values), max(values)
    pad = 0.08 * (high - low)
    return low - pad, high + pad


def draw_panel(panel: dict, kind: str, ylim, color_offset: int) -> plt.Figure:
    fig = plt.figure(figsize=(pt_to_in(PANEL_PT), pt_to_in(PANEL_PT)))
    ax = fig.add_axes([0.23, 0.24, 0.73, 0.70])
    _style_ax(ax, ylim)
    key = "predicted" if kind == "predicted" else "measured"
    for index, series in enumerate(panel["series"]):
        color = TABLEAU[color_offset + index]
        ax.plot(
            list(X),
            series[key],
            color=color,
            marker=MARKERS[index],
            markersize=MARKER_PT,
            markerfacecolor=color,
            markeredgecolor=color,
            markeredgewidth=EDGE_PT,
            linewidth=LINE_PT,
            solid_capstyle="round",
            zorder=3,
        )
    problems = overflow_labels(fig) + overlapping_tick_labels(fig)
    if problems:
        raise RuntimeError(f"E3 {panel['family']} {panel['mode']} {kind}: {problems}")
    return fig


def draw_legend(payload) -> plt.Figure:
    handles = _series_handles(payload)
    fig = plt.figure(figsize=(pt_to_in(COLUMN_PT), pt_to_in(16.5)))
    legend = fig.legend(
        handles=handles,
        loc="center",
        ncol=10,
        frameon=False,
        fontsize=5.0,
        handlelength=1.35,
        handletextpad=0.25,
        columnspacing=0.45,
        borderaxespad=0.0,
        labelspacing=0.2,
    )
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    boxes = [text.get_window_extent(renderer) for text in legend.get_texts()]
    for i, left in enumerate(boxes):
        for right in boxes[i + 1 :]:
            if left.x1 > right.x0 - 0.4 and left.y1 > right.y0 and left.y0 < right.y1:
                raise RuntimeError("E3 legend items overlap")
        if left.x1 > fig.bbox.width + 1 or left.x0 < -1:
            raise RuntimeError("E3 legend exceeds the column")
    return fig


def build(out: Path) -> dict:
    configure_matplotlib()
    payload = load()
    out.mkdir(parents=True, exist_ok=True)
    ylim = _ylim(payload)
    drawn = []
    by_key = {(p["family"], p["mode"]): p for p in payload["panels"]}
    column_order = (
        ("SW", "Full"),
        ("SW", "LIMIT10"),
        ("LT", "Full"),
        ("LT", "LIMIT10"),
    )
    order = []
    for kind in ("predicted", "measured"):
        for family, mode in column_order:
            panel = by_key[(family, mode)]
            offset = 0 if family == "SW" else 5
            fig = draw_panel(panel, kind, ylim, offset)
            name = f"e3-{panel['family'].lower()}-{panel['mode'].lower()}-{kind}.pdf"
            path = out / name
            fig.savefig(path)
            fig.savefig(out / (path.stem + ".png"), dpi=300)
            plt.close(fig)
            order.append(
                {
                    "file": name,
                    "family": panel["family"],
                    "mode": panel["mode"],
                    "kind": kind,
                    "pairs": [(s["k"], s["h"]) for s in panel["series"]],
                }
            )
            drawn.append(name)
    legend = draw_legend(payload)
    legend.savefig(out / "e3-legend.pdf")
    legend.savefig(out / "e3-legend.png", dpi=300)
    plt.close(legend)
    note = {
        "source": str(SOURCE),
        "ylim_shared": ylim,
        "x_linear": list(X),
        "prediction_is_separate_panel": True,
        "supplements_not_drawn": [
            {"n": s["n"], "k": s["k"], "h": s["h"], "y": s["y"], "mode": p["mode"]}
            for p in payload["panels"]
            for s in p["supplements"]
        ],
        "panels": order,
        "line_pt": LINE_PT,
        "marker_pt": MARKER_PT,
        "panel_pt": PANEL_PT,
        "tick_font_pt": TICK_FONT_USE,
        "reason_tick_font": (
            f"Fig. 8 printed tick size is {TICK_FONT:.2f} pt. "
            f"Labels are set at {TICK_FONT_USE:.2f} pt so 1k/5k/10k stay readable "
            "at the same include box."
        ),
    }
    (out / "e3-facts.json").write_text(json.dumps(note, indent=2) + "\n")
    return note
