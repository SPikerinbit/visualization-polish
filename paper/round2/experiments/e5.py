"""E5 LIMIT sweep. The panel composition is unchanged.

Full stays on a broken-off axis and is not joined to LIMIT 500.
Slots stay equally spaced. Off and On-cold are the two extra columns of
one full-width 4 by 2 figure. The in-figure banner moves to the caption.
Line width moves from the previous 1.15 pt toward the original paper's
printed 0.96 pt. Colors stay the original SW red and LT blue.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from pdfutil import configure_matplotlib
from style import SW_RGB, LT_RGB, TEXT_PT, pt_to_in, printed

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parents[1] / "recovery" / "e5" / "data" / "e5_limit_sweep.csv"
META = ROOT.parents[1] / "recovery" / "e5" / "data" / "e5_limit_sweep_meta.json"

LIMIT_N = (10, 20, 50, 100, 200, 300, 400, 490, 500)
LINE_PT = printed(1.6, 0.33)  # 0.956 pt, was 1.15 on the wide draft
MARKER_PT = 3.6  # was 5.2; narrower panels, still above the 2.9 pt print marker
EDGE_PT = 0.35

# Millimetres inside the 178.61 mm text block.
W_MM = TEXT_PT * 25.4 / 72.0
H_MM = 104.0


def _font_setup() -> None:
    configure_matplotlib()
    plt.rcParams.update({"font.size": 7.0})


def load() -> tuple[list[dict], dict]:
    meta = json.loads(META.read_text())
    if meta["limit_n"] != list(LIMIT_N):
        raise RuntimeError("LIMIT list drifted")
    with DATA.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        if row["synthetic"] != "true":
            raise RuntimeError("E5 row is not marked synthetic")
        if row["endpoint"] == "full" and row["limit_n"] != "":
            raise RuntimeError("Full carries a LIMIT n")
        if row["endpoint"] == "limit" and int(row["limit_n"]) not in LIMIT_N:
            raise RuntimeError(f"unexpected LIMIT n {row['limit_n']}")
    return rows, meta


def _series(rows, state, dataset, family, endpoint):
    picked = [
        r
        for r in rows
        if r["state"] == state
        and r["dataset"] == dataset
        and r["family"] == family
        and r["endpoint"] == endpoint
    ]
    if endpoint == "limit":
        picked.sort(key=lambda r: LIMIT_N.index(int(r["limit_n"])))
        if [int(r["limit_n"]) for r in picked] != list(LIMIT_N):
            raise RuntimeError("LIMIT order broken")
    elif len(picked) != 1:
        raise RuntimeError("Full must be one point")
    return picked


def _box(x_mm, y_mm, w_mm, h_mm):
    return [x_mm / W_MM, y_mm / H_MM, w_mm / W_MM, h_mm / H_MM]


def _yticks(ylim):
    lo, hi = ylim
    if hi - lo < 1:
        return [0.66, 0.70, 0.74, 0.78]
    start = int(lo // 10) * 10
    if start < lo:
        start += 10
    ticks = []
    value = start
    while value < hi - 1e-9:
        ticks.append(value)
        value += 10
    return ticks


def _gap(fig, x_left, x_right, y_mm, h_mm):
    mid = (x_left + x_right) / 2
    half = 0.42
    rise = 0.38
    for y_edge in (y_mm, y_mm + h_mm):
        fig.add_artist(
            Line2D(
                [(mid - half) / W_MM, (mid + half) / W_MM],
                [(y_edge - rise) / H_MM, (y_edge + rise) / H_MM],
                transform=fig.transFigure,
                color="black",
                lw=0.7,
                solid_capstyle="butt",
                clip_on=False,
                zorder=6,
            )
        )


def draw(rows, meta) -> plt.Figure:
    fig = plt.figure(figsize=(pt_to_in(TEXT_PT), pt_to_in(H_MM * 72.0 / 25.4)))
    # Four groups. Each cost panel keeps its own y numbers because Off and
    # On-cold do not share a cost scale.
    y_tick = 6.6
    limit_w = 28.6
    break_w = 1.55
    full_w = 6.15
    gutter = 1.15
    group_w = y_tick + limit_w + break_w + full_w
    used = 4 * group_w + 3 * gutter
    left0 = (W_MM - used) / 2
    columns = (
        ("DL20", "Off", "DL20, Off"),
        ("DL20", "On-cold", "DL20, On"),
        ("COVID", "Off", "COVID, Off"),
        ("COVID", "On-cold", "COVID, On"),
    )
    row_h = 30.2
    bottom_y = 18.4
    top_y = bottom_y + row_h + 2.6
    origins = []
    x = left0
    for _dataset, _state, _title in columns:
        origins.append(x)
        x += group_w + gutter

    def style_limit(ax, ylim, show_x: bool) -> None:
        ax.set_xlim(-0.45, 8.45)
        ax.set_ylim(*ylim)
        ax.set_yticks(_yticks(ylim))
        ax.yaxis.grid(True, color=(0.75, 0.75, 0.75), lw=0.45, zorder=0)
        ax.set_axisbelow(True)
        ax.set_facecolor("white")
        ax.tick_params(length=2.2, width=0.55, pad=1.0, labelsize=5.5)
        ax.set_xticks(range(9))
        if show_x:
            # Nine contract labels in a quarter of the text width. Horizontal
            # labels touch; 60 degrees keeps every slot, including 490 and 500.
            ax.set_xticklabels(
                [str(n) for n in LIMIT_N],
                rotation=60,
                ha="right",
                va="top",
                rotation_mode="anchor",
            )
        else:
            ax.set_xticklabels([""] * 9)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        for spine in ax.spines.values():
            spine.set_linewidth(0.7)

    def style_full(ax, ylim, show_x: bool) -> None:
        ax.set_xlim(-1.0, 1.0)
        ax.set_ylim(*ylim)
        ax.set_xticks([0.0])
        ax.set_xticklabels(["Full"] if show_x else [""])
        ax.tick_params(axis="y", left=False, labelleft=False, length=0)
        ax.tick_params(axis="x", length=2.2, width=0.55, pad=1.1, labelsize=5.6)
        ax.yaxis.grid(True, color=(0.75, 0.75, 0.75), lw=0.45, zorder=0)
        ax.set_axisbelow(True)
        ax.set_facecolor((0.96, 0.96, 0.96))
        ax.spines["left"].set_visible(False)
        ax.spines["top"].set_visible(False)
        for spine in ax.spines.values():
            spine.set_linewidth(0.7)

    def draw_series(ax_l, ax_f, state, dataset, metric) -> None:
        key = "cost_input_equiv_1e3" if metric == "cost" else "ndcg10"
        for family, color, marker, dodge in (
            ("SW", SW_RGB, "o", -0.24),
            ("LT", LT_RGB, "^", 0.24),
        ):
            limits = _series(rows, state, dataset, family, "limit")
            full = _series(rows, state, dataset, family, "full")[0]
            ys = [float(r[key]) for r in limits]
            ax_l.plot(
                range(9),
                ys,
                color=color,
                marker=marker,
                markersize=MARKER_PT,
                linewidth=LINE_PT,
                markerfacecolor=color,
                markeredgecolor="white",
                markeredgewidth=EDGE_PT,
                zorder=3,
            )
            ax_f.plot(
                [dodge],
                [float(full[key])],
                linestyle="none",
                color=color,
                marker=marker,
                markersize=MARKER_PT,
                markerfacecolor=color,
                markeredgecolor="white",
                markeredgewidth=EDGE_PT,
                zorder=3,
            )

    for origin, (dataset, state, title) in zip(origins, columns):
        cost_ylim = tuple(meta["y_limits_1e3"][state])
        ndcg_ylim = tuple(meta["y_limits_ndcg10"])
        for y0, ylim, metric, show_x in (
            (top_y, cost_ylim, "cost", False),
            (bottom_y, ndcg_ylim, "ndcg", True),
        ):
            ax_l = fig.add_axes(_box(origin + y_tick, y0, limit_w, row_h))
            ax_f = fig.add_axes(_box(origin + y_tick + limit_w + break_w, y0, full_w, row_h))
            style_limit(ax_l, ylim, show_x)
            style_full(ax_f, ylim, show_x)
            _gap(fig, origin + y_tick + limit_w, origin + y_tick + limit_w + break_w, y0, row_h)
            draw_series(ax_l, ax_f, state, dataset, metric)
            if metric == "cost":
                ax_l.set_ylabel(
                    r"$U\times 10^{3}$" if state == "Off" else r"$U{-}Q\times 10^{3}$",
                    fontsize=5.8,
                    labelpad=0.8,
                )
        center = (origin + y_tick + (limit_w + break_w + full_w) / 2) / W_MM
        fig.text(center, (top_y + row_h + 0.7) / H_MM, title, ha="center", va="bottom", fontsize=7.0)
        fig.text(
            (origin + y_tick + limit_w / 2) / W_MM,
            (bottom_y - 11.2) / H_MM,
            "LIMIT n",
            ha="center",
            va="top",
            fontsize=6.2,
        )

    handles = [
        Line2D([0], [0], color=SW_RGB, marker="o", markersize=MARKER_PT, lw=LINE_PT,
               markerfacecolor=SW_RGB, markeredgecolor="white", markeredgewidth=EDGE_PT, label="SW"),
        Line2D([0], [0], color=LT_RGB, marker="^", markersize=MARKER_PT, lw=LINE_PT,
               markerfacecolor=LT_RGB, markeredgecolor="white", markeredgewidth=EDGE_PT, label="LT"),
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.012),
        ncol=2,
        frameon=False,
        fontsize=7.0,
        handlelength=2.2,
        columnspacing=1.4,
        borderaxespad=0.0,
    )
    _audit(fig)
    return fig


def _overlaps(a, b, pad=0.3) -> bool:
    return not (a.x1 < b.x0 + pad or b.x1 < a.x0 + pad or a.y1 < b.y0 + pad or b.y1 < a.y0 + pad)


def _audit(fig) -> None:
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    labels = []
    for ax in fig.axes:
        for tick in ax.get_xticklabels():
            text = tick.get_text().strip()
            if not text:
                continue
            if text.isdigit() and int(text) not in LIMIT_N:
                raise RuntimeError(f"tick outside the contract: {text}")
            box = tick.get_window_extent(renderer)
            if box.x0 < -1 or box.y0 < -1 or box.x1 > fig.bbox.width + 1 or box.y1 > fig.bbox.height + 1:
                raise RuntimeError(f"tick {text} outside the page")
            labels.append((text, box))
    for i, (left, box_l) in enumerate(labels):
        for right, box_r in labels[i + 1 :]:
            # Rotated LIMIT labels have tall boxes that cross without the
            # glyphs touching. Those are checked on the contact sheet.
            if left.isdigit() and right.isdigit():
                continue
            if _overlaps(box_l, box_r, pad=0.2):
                raise RuntimeError(f"E5 tick overlap: {left} and {right}")
    for ax in fig.axes:
        width_mm = ax.get_position().width * W_MM
        for line in ax.get_lines():
            if line.get_linestyle() in ("none", "None"):
                continue
            if line.get_transform() != ax.transData:
                continue
            xs = list(line.get_xdata())
            if width_mm < 20 and len(xs) > 1:
                raise RuntimeError("Full axis has a connected line")
            if width_mm >= 20 and xs and max(float(x) for x in xs) > 8.01:
                raise RuntimeError("LIMIT line reaches into Full")
            if width_mm >= 20 and len(xs) != 9:
                raise RuntimeError(f"LIMIT line has {len(xs)} points")
    blob = " ".join(t.get_text() for t in fig.texts)
    if "Synthetic" in blob or "510" in blob or "SLT" in blob:
        raise RuntimeError(f"unexpected figure text: {blob}")
    if blob.count("LIMIT n") != 4:
        raise RuntimeError("LIMIT n should sit under each limit axis")


def build(out: Path) -> dict:
    _font_setup()
    out.mkdir(parents=True, exist_ok=True)
    rows, meta = load()
    fig = draw(rows, meta)
    fig.savefig(out / "e5-limit-sweep.pdf")
    fig.savefig(out / "e5-limit-sweep.png", dpi=300)
    plt.close(fig)
    facts = {
        "source_csv": str(DATA),
        "source_meta": str(META),
        "width_mm": W_MM,
        "height_mm": H_MM,
        "line_pt": LINE_PT,
        "marker_pt": MARKER_PT,
        "columns": ["DL20 Off", "DL20 On", "COVID Off", "COVID On"],
        "full_joined": False,
        "spacing": "equal contract slots, not linear in n",
        "y_limits": meta["y_limits_1e3"],
        "ndcg_limits": meta["y_limits_ndcg10"],
        "banner_moved_to_caption": True,
        "values": "unchanged placeholder cells",
    }
    (out / "e5-facts.json").write_text(json.dumps(facts, indent=2) + "\n")
    return facts
