"""Draw the E4c quality-cost mean scatters at 178 mm.

Two styles, two metrics. Off and On-cold in one metric share axis limits taken
from every mean in that metric. No per-query marks and no Pareto line.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D

from layout import place_labels, point_segment_distance
from limits import (
    PAD_FRAC,
    format_quality,
    format_token,
    limits_from_values,
    quality_ticks,
    token_ticks,
)
from sample_means import METHODS, META, POINTS, points_for

ROOT = Path(__file__).resolve().parent
FIGDIR = ROOT / "figures"
DATA_JSON = ROOT / "data" / "synthetic_means.json"

WIDTH_MM = 178.0
WIDTH_IN = WIDTH_MM / 25.4
MARKER_S = 62.0
PANEL_H = 1.84
ROW_GAP = 0.52
TOP_MARGIN = 0.50
LEFT = 0.76
RIGHT_MARGIN = 0.08
COL_GAP = 0.66
BOTTOM_NUMBERED = 0.78
BOTTOM_LABELED = 0.46
HEADER_PT = 8.0
TITLE_PT = 8.0
LABEL_PT = 8.0
TICK_PT = 7.5
LEGEND_PT = 7.0
DIRECT_PT = 7.0
NUMBER_PT = 6.5

FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
INK = "#1c1c1c"
MUTED = "#4d4d4d"
GRID = "#E2E6EA"
LEADER = "#5c5c5c"

# Optional point offsets in typographic points, applied after automatic placement.
# Filled only by the single print-size revision.
MANUAL_NUDGE_PT: dict[tuple[str, str, str, str, str], tuple[float, float]] = {}


def _font() -> None:
    font_manager.fontManager.addfont(FONT)
    plt.rcParams.update({
        "font.family": "Liberation Serif",
        "font.size": TICK_PT,
        "axes.labelsize": LABEL_PT,
        "axes.titlesize": TITLE_PT,
        "xtick.labelsize": TICK_PT,
        "ytick.labelsize": TICK_PT,
        "legend.fontsize": LEGEND_PT,
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.linewidth": 0.6,
        "axes.edgecolor": "#3a3a3a",
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
    })


def metric_limits(metric: str) -> dict:
    rows = points_for(metric)
    xlim = limits_from_values([row["x"] for row in rows], PAD_FRAC)
    ylim = limits_from_values([row["y"] for row in rows], PAD_FRAC)
    xticks = token_ticks(*xlim)
    yticks = quality_ticks(*ylim)
    return {
        "metric": metric,
        "pad_frac": PAD_FRAC,
        "xlim": xlim,
        "ylim": ylim,
        "xticks": xticks,
        "yticks": yticks,
        "xticklabels": [format_token(tick) for tick in xticks],
        "yticklabels": [format_quality(tick) for tick in yticks],
        "n_points": len(rows),
    }


def _panel_w() -> float:
    return (WIDTH_IN - LEFT - RIGHT_MARGIN - COL_GAP) / 2


def _figure_height(style: str) -> float:
    bottom = BOTTOM_NUMBERED if style == "numbered" else BOTTOM_LABELED
    return PANEL_H * 2 + ROW_GAP + TOP_MARGIN + bottom


def _boxes(style: str) -> dict[tuple[str, str], tuple[float, float, float, float]]:
    height = _figure_height(style)
    bottom = BOTTOM_NUMBERED if style == "numbered" else BOTTOM_LABELED
    pw, ph = _panel_w(), PANEL_H
    x0 = LEFT
    x1 = LEFT + pw + COL_GAP
    y0 = bottom
    y1 = bottom + ph + ROW_GAP
    boxes = {
        ("DL20", "Off"): (x0, y1, pw, ph),
        ("DL20", "On-cold"): (x1, y1, pw, ph),
        ("COVID", "Off"): (x0, y0, pw, ph),
        ("COVID", "On-cold"): (x1, y0, pw, ph),
    }
    return {key: (x / WIDTH_IN, y / height, pw / WIDTH_IN, ph / height) for key, (x, y, w, h) in boxes.items()}


def _listk_text(metric: str) -> tuple[str, str]:
    if metric == "full":
        return "ListK Sort", "Sort"
    return "ListK Select", "Select"


def _legend_label(method: dict, metric: str) -> str:
    if method["id"] == "listk":
        legend, _ = _listk_text(metric)
        return f"{method['number']}  {legend}"
    return f"{method['number']}  {method['legend']}"


def _style_text(style: str, method: dict, metric: str) -> tuple[str, float]:
    if style == "numbered":
        return str(method["number"]), NUMBER_PT
    if method["id"] == "listk":
        _, short = _listk_text(metric)
        return short, DIRECT_PT
    return method["short"], DIRECT_PT


def _measure(fig, renderer, samples: list[tuple[str, float]]) -> dict[tuple[str, float], tuple[float, float]]:
    artists = [fig.text(0, 0, text, fontsize=size, alpha=0, color=INK) for text, size in samples]
    fig.canvas.draw()
    sizes = {}
    for artist, sample in zip(artists, samples):
        bb = artist.get_window_extent(renderer)
        sizes[sample] = (bb.width, bb.height)
        artist.remove()
    return sizes


def _draw_panel(ax, rows, methods, limits, dataset, state, style):
    by_id = {method["id"]: method for method in methods}
    ax.set_xlim(*limits["xlim"])
    ax.set_ylim(*limits["ylim"])
    ax.set_xticks(limits["xticks"])
    ax.set_xticklabels(limits["xticklabels"])
    ax.set_yticks(limits["yticks"])
    ax.set_yticklabels(limits["yticklabels"])
    ax.tick_params(length=2.4, width=0.5, direction="out", pad=1.6, labelbottom=True, labelleft=True)
    ax.grid(True, which="major", color=GRID, lw=0.45, zorder=0)
    ax.set_axisbelow(True)
    for row in rows:
        method = by_id[row["method"]]
        ax.scatter(
            [row["x"]],
            [row["y"]],
            s=MARKER_S,
            c=method["color"],
            marker=method["marker"],
            linewidths=0.45,
            edgecolors="#222222",
            zorder=3,
            clip_on=False,
        )
    ax.set_title(f"{dataset}, {state}", loc="center", pad=3, color=INK, fontsize=TITLE_PT)
    ylabel = "Spearman (full ranking)" if rows[0]["metric"] == "full" else "NDCG@10"
    ax.set_ylabel(ylabel)
    if dataset == "COVID":
        ax.set_xlabel("Equivalent tokens, β = 0, output weight 1")
    ax.set_xlim(*limits["xlim"])
    ax.set_ylim(*limits["ylim"])
    ax.set_autoscale_on(False)


def _place_panel(ax, fig, renderer, rows, methods, style, metric, sizes):
    by_id = {method["id"]: method for method in methods}
    bb = ax.bbox
    bounds = (bb.x0, bb.y0, bb.x1, bb.y1)
    radius = (MARKER_S ** 0.5) / 2 * fig.dpi / 72.0
    markers = []
    label_sizes = {}
    for row in rows:
        method = by_id[row["method"]]
        px, py = ax.transData.transform((row["x"], row["y"]))
        markers.append({"id": method["id"], "x": float(px), "y": float(py), "r": radius})
        text, size = _style_text(style, method, metric)
        label_sizes[method["id"]] = sizes[(text, size)]
    placed = place_labels(markers, label_sizes, bounds, dpi=fig.dpi)
    inv = ax.transData.inverted()
    texts = []
    leaders = []
    for rec in placed:
        method = by_id[rec["id"]]
        nudge = MANUAL_NUDGE_PT.get((style, metric, ax.get_title(), method["id"]))
        # Title is "DL20, Off"; nudges are keyed by dataset/state separately below.
        cx, cy = rec["cx"], rec["cy"]
        key = (style, metric, *_panel_key(ax), method["id"])
        if key in MANUAL_NUDGE_PT:
            dx, dy = MANUAL_NUDGE_PT[key]
            cx += dx * fig.dpi / 72.0
            cy += dy * fig.dpi / 72.0
        text, size = _style_text(style, method, metric)
        data_xy = inv.transform((cx, cy))
        artist = ax.text(
            data_xy[0],
            data_xy[1],
            text,
            ha="center",
            va="center",
            fontsize=size,
            color=INK,
            zorder=4,
            clip_on=True,
        )
        texts.append(artist)
        leader_artist = None
        if rec["leader"] is not None:
            (sx, sy), (ex, ey) = rec["leader"]
            # Recompute from the nudged center so a manual move keeps a clean stem.
            width, height = label_sizes[method["id"]]
            rect = (cx - width / 2, cy - height / 2, cx + width / 2, cy + height / 2)
            marker = next(item for item in markers if item["id"] == method["id"])
            from layout import _closest_on_rect, _on_circle

            start = _closest_on_rect(rect, marker["x"], marker["y"])
            end = _on_circle(marker["x"], marker["y"], marker["r"], start[0], start[1])
            gap = ((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2) ** 0.5
            if gap > 4.0 * fig.dpi / 72.0:
                p1 = inv.transform(start)
                p2 = inv.transform(end)
                leader_artist = ax.plot(
                    [p1[0], p2[0]],
                    [p1[1], p2[1]],
                    color=LEADER,
                    lw=0.55,
                    solid_capstyle="butt",
                    zorder=2,
                    clip_on=True,
                )[0]
                leader_artist.set_gid("leader")
                leaders.append(leader_artist)
        _ = nudge
    ax.set_xlim(*ax.get_xlim())
    ax.set_ylim(*ax.get_ylim())
    return texts, leaders


def _panel_key(ax) -> tuple[str, str]:
    dataset, state = ax.get_title().split(", ", 1)
    return dataset, state


def render_figure(metric: str, style: str) -> dict:
    _font()
    limits = metric_limits(metric)
    height = _figure_height(style)
    fig = plt.figure(figsize=(WIDTH_IN, height), dpi=120)
    boxes = _boxes(style)
    axes = {}
    panel_rows = {}
    for (dataset, state), rect in boxes.items():
        ax = fig.add_axes(rect)
        rows = points_for(metric, dataset, state)
        _draw_panel(ax, rows, METHODS, limits, dataset, state, style)
        axes[(dataset, state)] = ax
        panel_rows[(dataset, state)] = rows
    header = {
        "full": "Full ranking, Spearman. Synthetic layout values, not measurements.",
        "topk": "LIMIT 10, NDCG@10. Synthetic layout values, not measurements.",
    }[metric]
    fig.text(0.5, 1 - (0.06 / height), header, ha="center", va="top", fontsize=HEADER_PT, color=MUTED)
    if style == "numbered":
        handles = [
            Line2D(
                [0],
                [0],
                marker=method["marker"],
                color="none",
                markerfacecolor=method["color"],
                markeredgecolor="#222222",
                markeredgewidth=0.4,
                markersize=7.6,
                lw=0,
                label=_legend_label(method, metric),
            )
            for method in METHODS
        ]
        fig.legend(
            handles=handles,
            loc="lower center",
            ncol=5,
            frameon=False,
            bbox_to_anchor=(0.5, 0.012),
            borderaxespad=0.0,
            handletextpad=0.35,
            columnspacing=0.9,
            labelspacing=0.25,
        )
    renderer = fig.canvas.get_renderer()
    samples = []
    for method in METHODS:
        text, size = _style_text(style, method, metric)
        samples.append((text, size))
    sizes = _measure(fig, renderer, samples)
    stored = {}
    for key, ax in axes.items():
        texts, leaders = _place_panel(ax, fig, renderer, panel_rows[key], METHODS, style, metric, sizes)
        stored[key] = (texts, leaders)
        ax.set_xlim(*limits["xlim"])
        ax.set_ylim(*limits["ylim"])
    fig.canvas.draw()
    report_panels = {}
    for key, ax in axes.items():
        texts, leaders = stored[key]
        label_boxes = []
        for artist in texts:
            bb = artist.get_window_extent(renderer)
            label_boxes.append({
                "text": artist.get_text(),
                "bbox": [bb.x0, bb.y0, bb.x1, bb.y1],
            })
        leader_segs = []
        for line in leaders:
            verts = line.get_xydata()
            (x1, y1), (x2, y2) = ax.transData.transform(verts)
            leader_segs.append([float(x1), float(y1), float(x2), float(y2)])
        radius = (MARKER_S ** 0.5) / 2 * fig.dpi / 72.0
        markers = []
        for row in panel_rows[key]:
            px, py = ax.transData.transform((row["x"], row["y"]))
            markers.append({"method": row["method"], "x": float(px), "y": float(py), "r": radius})
        report_panels[f"{key[0]}|{key[1]}"] = {
            "xlim": list(ax.get_xlim()),
            "ylim": list(ax.get_ylim()),
            "xticklabels": [tick.get_text() for tick in ax.get_xticklabels()],
            "yticklabels": [tick.get_text() for tick in ax.get_yticklabels()],
            "n_scatters": sum(collection.get_offsets().shape[0] for collection in ax.collections),
            "labels": label_boxes,
            "leaders": leader_segs,
            "markers": markers,
            "dashed": [line.get_linestyle() for line in ax.lines if line.get_linestyle() not in ("-", "solid", "None")],
        }
    stem = f"exp4c-{metric}-{style}"
    FIGDIR.mkdir(parents=True, exist_ok=True)
    pdf = FIGDIR / f"{stem}.pdf"
    png = FIGDIR / f"{stem}.png"
    fig.savefig(pdf, format="pdf")
    fig.savefig(png, format="png", dpi=300)
    plt.close(fig)
    return {
        "metric": metric,
        "style": style,
        "width_in": WIDTH_IN,
        "height_in": height,
        "pdf": str(pdf),
        "png": str(png),
        "limits": {
            "xlim": list(limits["xlim"]),
            "ylim": list(limits["ylim"]),
            "xticks": limits["xticks"],
            "yticks": limits["yticks"],
            "xticklabels": limits["xticklabels"],
            "yticklabels": limits["yticklabels"],
        },
        "panels": report_panels,
    }


def write_data_json() -> None:
    DATA_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(META)
    payload["methods"] = METHODS
    payload["points"] = [
        {"metric": met, "dataset": dat, "state": st, "method": method, "x": x, "y": y}
        for (met, dat, st, method), (x, y) in sorted(POINTS.items())
    ]
    DATA_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def render_all() -> dict:
    write_data_json()
    reports = [render_figure(metric, style) for metric in ("full", "topk") for style in ("numbered", "labeled")]
    summary = {
        "width_mm": WIDTH_MM,
        "pad_frac": PAD_FRAC,
        "marker_area": MARKER_S,
        "per_query_points": False,
        "pareto_line": False,
        "figures": [
            {
                "metric": report["metric"],
                "style": report["style"],
                "pdf": report["pdf"],
                "png": report["png"],
                "width_in": report["width_in"],
                "height_in": report["height_in"],
                "limits": report["limits"],
            }
            for report in reports
        ],
    }
    (FIGDIR / "axis_limits.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return {"summary": summary, "reports": reports}


def leader_clears_markers(report_panel: dict, clearance_px: float = 1.0) -> list[str]:
    problems = []
    markers = report_panel["markers"]
    for seg in report_panel["leaders"]:
        x1, y1, x2, y2 = seg
        for marker in markers:
            dist = point_segment_distance(marker["x"], marker["y"], x1, y1, x2, y2)
            if dist < marker["r"] - 0.75:
                # The stem ends on its own circumference, so only a pass through the disk counts.
                problems.append(marker["method"])
    return problems


if __name__ == "__main__":
    result = render_all()
    for figure in result["summary"]["figures"]:
        print(figure["pdf"])
        print(figure["png"])
