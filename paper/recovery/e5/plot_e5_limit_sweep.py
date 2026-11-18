#!/usr/bin/env python3
"""LIMIT n sweep for experiment 5. Placeholder curves only.

Reads recovery/e5/data/e5_limit_sweep.csv. Writes one Off PDF/PNG and one
On-cold PDF/PNG at a 178 mm media box. Does not import viz/ and does not
draw the LIMIT execution diagram.

The LIMIT axis is an ordered list of contract points with equal slot
spacing. It is not a linear K axis. Full is a separate axes, broken off
the LIMIT spine, and is not joined by a line.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "e5_limit_sweep.csv"
META = ROOT / "data" / "e5_limit_sweep_meta.json"
FIG = ROOT / "figures"

LIMIT_N = (10, 20, 50, 100, 200, 300, 400, 490, 500)
FAMILIES = ("SW", "LT")
DATASETS = ("DL20", "COVID")
STATES = ("Off", "On-cold")

# Colors sampled from the original paper panel
# fig/panels/exp2/exp2_movies_tokens.pdf (SW red circle, LT blue triangle).
# SLT green is intentionally absent.
SW_COLOR = (0.839, 0.153, 0.157)
LT_COLOR = (0.122, 0.467, 0.706)
STYLE = {
    "SW": dict(color=SW_COLOR, marker="o", ms=5.2, lw=1.15),
    "LT": dict(color=LT_COLOR, marker="^", ms=5.6, lw=1.15),
}

W_MM = 178.0
H_MM = 112.0
MM = 1.0 / 25.4

# Millimetre layout inside the 178 mm page. Tuned so 8 pt tick labels
# for 490 and 500 do not meet, and so the Full label is not a tenth tick.
LEFT = 13.2
LIMIT_W = 59.6
BREAK = 2.6
FULL_W = 13.4
GUTTER = 11.2
RIGHT = 2.4
# vertical
LEGEND_Y = 3.4
NOTE_Y = 9.6
XLABEL_Y = 15.2
TICK_ROOM = 7.4
ROW_H = 31.0
ROW_GAP = 6.2
BOTTOM_ROW_Y = 23.6
TOP_ROW_Y = BOTTOM_ROW_Y + ROW_H + ROW_GAP
HEADER_Y = TOP_ROW_Y + ROW_H + 2.4
TITLE_Y = HEADER_Y + 5.6
STAMP_Y = TITLE_Y + 5.2


def _font() -> None:
    regular = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
    bold = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
    font_manager.fontManager.addfont(regular)
    font_manager.fontManager.addfont(bold)
    plt.rcParams.update({
        "font.family": "Liberation Serif",
        "font.size": 8,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "axes.linewidth": 0.8,
        "axes.edgecolor": "black",
        "axes.labelcolor": "black",
        "xtick.color": "black",
        "ytick.color": "black",
        "text.color": "black",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.unicode_minus": False,
        "mathtext.fontset": "stix",
    })


def load_rows() -> list[dict]:
    with DATA.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    meta = json.loads(META.read_text())
    if meta["limit_n"] != list(LIMIT_N):
        raise SystemExit("meta limit_n does not match the contract list")
    if meta["y_limits_ndcg10"] != [0.66, 0.80]:
        raise SystemExit("meta NDCG window changed without a matching plot edit")
    seen = set()
    for row in rows:
        if row["synthetic"] != "true":
            raise SystemExit("a row is not marked synthetic")
        key = (row["state"], row["dataset"], row["family"], row["endpoint"], row["limit_n"])
        if key in seen:
            raise SystemExit(f"duplicate row {key}")
        seen.add(key)
        if row["family"] not in FAMILIES:
            raise SystemExit(f"unexpected family {row['family']}")
        if row["state"] not in STATES or row["dataset"] not in DATASETS:
            raise SystemExit(f"unexpected facet {key}")
        if row["endpoint"] == "limit":
            if int(row["limit_n"]) not in LIMIT_N:
                raise SystemExit(f"limit_n outside the contract: {row['limit_n']}")
        elif row["endpoint"] == "full":
            if row["limit_n"] != "":
                raise SystemExit("Full must not carry a LIMIT n (and must not be 510)")
        else:
            raise SystemExit(f"bad endpoint {row['endpoint']}")
        cost = float(row["cost_input_equiv_1e3"])
        ndcg = float(row["ndcg10"])
        if not (0 < ndcg < 1):
            raise SystemExit(f"NDCG@10 out of range: {ndcg}")
        if cost <= 0:
            raise SystemExit(f"non-positive cost: {cost}")
    for state in STATES:
        for dataset in DATASETS:
            for family in FAMILIES:
                limits = [r for r in rows if _match(r, state, dataset, family, "limit")]
                fulls = [r for r in rows if _match(r, state, dataset, family, "full")]
                got = [int(r["limit_n"]) for r in limits]
                if got != list(LIMIT_N):
                    raise SystemExit(f"LIMIT order broken for {state} {dataset} {family}: {got}")
                if len(fulls) != 1:
                    raise SystemExit("Full must be exactly one point per series")
                if float(fulls[0]["cost_input_equiv_1e3"]) == float(limits[-1]["cost_input_equiv_1e3"]):
                    raise SystemExit("Full cost equals LIMIT 500; the modes would stack")
                if float(fulls[0]["ndcg10"]) == float(limits[-1]["ndcg10"]):
                    raise SystemExit("Full NDCG@10 equals LIMIT 500; the modes would stack")
    return rows


def _match(row, state, dataset, family, endpoint) -> bool:
    return (
        row["state"] == state
        and row["dataset"] == dataset
        and row["family"] == family
        and row["endpoint"] == endpoint
    )


def _series(rows, state, dataset, family, endpoint):
    picked = [r for r in rows if _match(r, state, dataset, family, endpoint)]
    if endpoint == "limit":
        picked.sort(key=lambda r: LIMIT_N.index(int(r["limit_n"])))
    return picked


def _box(x_mm, y_mm, w_mm, h_mm):
    return [x_mm / W_MM, y_mm / H_MM, w_mm / W_MM, h_mm / H_MM]


def _open_spines(ax_limit, ax_full) -> None:
    ax_limit.spines["right"].set_visible(False)
    ax_full.spines["left"].set_visible(False)


def _gap_breaks(fig, x_left_mm, x_right_mm, y_mm, h_mm):
    """Two short diagonals in the gap. They stay off the 500 and Full labels."""
    mid = (x_left_mm + x_right_mm) / 2
    half = 0.48
    rise = 0.42
    artists = []
    for y_edge in (y_mm, y_mm + h_mm):
        artists.append(fig.add_artist(plt.Line2D(
            [(mid - half) / W_MM, (mid + half) / W_MM],
            [(y_edge - rise) / H_MM, (y_edge + rise) / H_MM],
            transform=fig.transFigure,
            color="black",
            lw=0.8,
            solid_capstyle="butt",
            clip_on=False,
            zorder=6,
        )))
    return artists


def _style_limit(ax, ylim, show_x: bool) -> None:
    ax.set_xlim(-0.45, 8.45)
    ax.set_ylim(*ylim)
    ax.set_yticks(_yticks(ylim))
    ax.yaxis.grid(True, color=(0.75, 0.75, 0.75), lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=3.0, width=0.7, pad=2.4)
    if show_x:
        ax.set_xticks(range(9))
        ax.set_xticklabels([str(n) for n in LIMIT_N])
        for label in ax.get_xticklabels():
            label.set_rotation(0)
            label.set_ha("center")
            label.set_va("top")
    else:
        ax.set_xticks(range(9))
        ax.set_xticklabels([""] * 9)
        ax.tick_params(labelbottom=False)
    for spine in ("top",):
        ax.spines[spine].set_visible(False)


def _yticks(ylim):
    lo, hi = ylim
    if hi - lo < 1:
        return [0.66, 0.70, 0.74, 0.78]
    step = 10
    start = int(lo // step) * step
    if start < lo:
        start += step
    ticks = []
    value = start
    while value < hi:
        ticks.append(value)
        value += step
    return ticks


def _style_full(ax, ylim) -> None:
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(*ylim)
    ax.set_xticks([0.0])
    ax.set_xticklabels(["Full"])
    ax.tick_params(axis="y", left=False, labelleft=False, length=0)
    ax.tick_params(axis="x", length=3.0, width=0.7, pad=2.4)
    ax.yaxis.grid(True, color=(0.75, 0.75, 0.75), lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.set_facecolor((0.96, 0.96, 0.96))
    for spine in ("top",):
        ax.spines[spine].set_visible(False)
    for label in ax.get_xticklabels():
            label.set_fontweight("bold")


def _draw_series(ax_limit, ax_full, rows, state, dataset, metric) -> None:
    key = "cost_input_equiv_1e3" if metric == "cost" else "ndcg10"
    for family in FAMILIES:
        limits = _series(rows, state, dataset, family, "limit")
        full = _series(rows, state, dataset, family, "full")[0]
        style = STYLE[family]
        ys = [float(r[key]) for r in limits]
        # One line, one marker per LIMIT point. Full is not in this sequence.
        ax_limit.plot(
            range(9),
            ys,
            color=style["color"],
            marker=style["marker"],
            markersize=style["ms"],
            linewidth=style["lw"],
            markerfacecolor=style["color"],
            markeredgecolor="white",
            markeredgewidth=0.45,
            zorder=3,
            label=family,
        )
        # Dodge inside the Full band only. Both marks stay on Full.
        # The offset is not a LIMIT n and is not a second Full observation.
        dodge = -0.24 if family == "SW" else 0.24
        ax_full.plot(
            [dodge],
            [float(full[key])],
            linestyle="none",
            color=style["color"],
            marker=style["marker"],
            markersize=style["ms"] + 0.4,
            markerfacecolor=style["color"],
            markeredgecolor="white",
            markeredgewidth=0.45,
            zorder=3,
        )


def draw(rows, state: str) -> plt.Figure:
    meta = json.loads(META.read_text())
    cost_ylim = tuple(meta["y_limits_1e3"][state])
    ndcg_ylim = tuple(meta["y_limits_ndcg10"])
    fig = plt.figure(figsize=(W_MM * MM, H_MM * MM))
    origins = [LEFT, LEFT + LIMIT_W + BREAK + FULL_W + GUTTER]

    axes = {}
    for col, dataset in enumerate(DATASETS):
        x0 = origins[col]
        for row_name, y0, ylim, show_x in (
            ("cost", TOP_ROW_Y, cost_ylim, False),
            ("ndcg", BOTTOM_ROW_Y, ndcg_ylim, True),
        ):
            ax_l = fig.add_axes(_box(x0, y0, LIMIT_W, ROW_H))
            ax_f = fig.add_axes(_box(x0 + LIMIT_W + BREAK, y0, FULL_W, ROW_H))
            _style_limit(ax_l, ylim, show_x=show_x)
            _style_full(ax_f, ylim)
            if not show_x:
                ax_f.set_xticklabels([""])
                ax_f.tick_params(labelbottom=False)
            _open_spines(ax_l, ax_f)
            _gap_breaks(fig, x0 + LIMIT_W, x0 + LIMIT_W + BREAK, y0, ROW_H)
            _draw_series(ax_l, ax_f, rows, state, dataset, "cost" if row_name == "cost" else "ndcg")
            axes[(dataset, row_name)] = (ax_l, ax_f)
            if col == 0:
                if row_name == "cost":
                    ylabel = r"$U$ ($\times 10^{3}$)" if state == "Off" else r"$U{-}Q$ ($\times 10^{3}$)"
                    ax_l.set_ylabel(ylabel)
                else:
                    ax_l.set_ylabel("NDCG@10")

    fig.canvas.draw()
    for col, dataset in enumerate(DATASETS):
        ax_l, ax_f = axes[(dataset, "cost")]
        center = (ax_l.get_position().x0 + ax_f.get_position().x1) / 2
        fig.text(center, HEADER_Y / H_MM, dataset, ha="center", va="bottom", fontsize=9)

    if state == "Off":
        title = r"Off, equivalent input cost $U$"
    else:
        title = r"On-cold, equivalent input cost $U{-}Q$ at $\beta{=}0$"
    fig.text(0.5, TITLE_Y / H_MM, title, ha="center", va="bottom", fontsize=9)
    fig.text(
        0.5,
        STAMP_Y / H_MM,
        "Synthetic placeholder. A gap is not a measured advantage.",
        ha="center",
        va="bottom",
        fontsize=8.5,
        color=(0.55, 0.12, 0.12),
        fontweight="bold",
    )
    for x0 in origins:
        fig.text(
            (x0 + LIMIT_W / 2) / W_MM,
            XLABEL_Y / H_MM,
            "LIMIT n",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    fig.text(
        0.5,
        NOTE_Y / H_MM,
        "Ordered contract slots, equal spacing, not linear in n.  "
        "Full is a separate mode and is not joined to LIMIT 500.",
        ha="center",
        va="bottom",
        fontsize=7.5,
    )
    handles = [
        Line2D(
            [0],
            [0],
            color=STYLE[name]["color"],
            marker=STYLE[name]["marker"],
            markersize=STYLE[name]["ms"],
            linewidth=STYLE[name]["lw"],
            markerfacecolor=STYLE[name]["color"],
            markeredgecolor="white",
            markeredgewidth=0.45,
            label=name,
        )
        for name in FAMILIES
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, LEGEND_Y / H_MM),
        ncol=2,
        frameon=False,
        fontsize=8.5,
        handlelength=2.6,
        columnspacing=1.6,
        borderaxespad=0.0,
    )
    return fig


def _overlaps(a, b, pad=0.4) -> bool:
    return not (
        a.x1 < b.x0 + pad
        or b.x1 < a.x0 + pad
        or a.y1 < b.y0 + pad
        or b.y1 < a.y0 + pad
    )


def audit(fig: plt.Figure, state: str) -> list[str]:
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    problems = []
    labels = []
    for ax in fig.axes:
        for tick in ax.get_xticklabels():
            text = tick.get_text().strip()
            if not text:
                continue
            if text.isdigit() and int(text) not in LIMIT_N:
                problems.append(f"numeric tick outside LIMIT n: {text}")
            if text in {"510", "K=510"}:
                problems.append(text)
            box = tick.get_window_extent(renderer)
            labels.append((text, box, ax))
            if box.x0 < -1 or box.y0 < -1 or box.x1 > fig.bbox.width + 1 or box.y1 > fig.bbox.height + 1:
                problems.append(f"tick '{text}' falls outside the page")
    for i, (ta, ba, _) in enumerate(labels):
        for tb, bb, _ in labels[i + 1:]:
            if _overlaps(ba, bb):
                problems.append(f"tick labels overlap: '{ta}' and '{tb}'")
    for ax in fig.axes:
        for line in ax.get_lines():
            if line.get_transform() != ax.transData:
                continue
            xs = list(line.get_xdata())
            ys = list(line.get_ydata())
            if line.get_linestyle() in ("none", "None"):
                continue
            if len(xs) != 9:
                problems.append(f"a connected line has {len(xs)} points, expected 9 LIMIT points")
            if any(float(y) != float(y) for y in ys):
                problems.append("connected line contains a NaN")
            if max(float(x) for x in xs) > 8.01:
                problems.append("LIMIT line extends past the last LIMIT slot")
    # Full markers must be on the narrow axes only.
    for ax in fig.axes:
        pos = ax.get_position()
        width_mm = pos.width * W_MM
        if width_mm > 20:
            continue
        for line in ax.get_lines():
            if line.get_linestyle() not in ("none", "None"):
                # break-mark segments are short and use the axes transform;
                # data lines on the Full axes are forbidden.
                if line.get_transform() == ax.transData and len(line.get_xdata()) > 1:
                    problems.append("Full axes has a connected data line")
    texts = [t.get_text() for t in fig.texts]
    blob = " ".join(texts)
    for required in ("Synthetic placeholder", "LIMIT n", "not linear", "not joined"):
        if required not in blob:
            problems.append(f"missing note text: {required}")
    if texts.count("LIMIT n") != 2:
        problems.append(f"expected LIMIT n under each limit axis, found {texts.count('LIMIT n')}")
    if "510" in blob or "SLT" in blob:
        problems.append("forbidden token in figure text")
    if state == "On-cold" and r"\beta" not in blob and "β" not in blob:
        problems.append("On-cold figure does not state beta=0")
    for artist in fig.artists:
        if not isinstance(artist, Line2D):
            continue
        mark = artist.get_window_extent(renderer)
        for text, box, _ in labels:
            if _overlaps(mark, box, pad=0.0):
                problems.append(f"axis break overlaps tick '{text}'")
    for text in fig.texts:
        if text.get_text() != "LIMIT n":
            continue
        box = text.get_window_extent(renderer)
        for label, lbox, _ in labels:
            if label == "Full" and _overlaps(box, lbox, pad=0.0):
                problems.append("LIMIT n label overlaps the Full tick")
    for ax in fig.axes:
        if ax.get_position().width * W_MM > 20:
            continue
        dodged = []
        for line in ax.get_lines():
            if line.get_transform() != ax.transData:
                continue
            if line.get_marker() not in ("o", "^"):
                problems.append(f"unexpected marker {line.get_marker()}")
            dodged.extend(float(x) for x in line.get_xdata())
        if sorted(round(x, 2) for x in dodged) != [-0.24, 0.24]:
            problems.append(f"Full markers are not the two dodged points: {dodged}")
    return problems


def write(fig: plt.Figure, stem: str) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    pdf = FIG / f"{stem}.pdf"
    png = FIG / f"{stem}.png"
    fig.savefig(pdf, format="pdf")
    fig.savefig(png, format="png", dpi=300)
    plt.close(fig)


def main() -> int:
    _font()
    rows = load_rows()
    stems = {"Off": "e5-limit-sweep-off", "On-cold": "e5-limit-sweep-on"}
    failed = False
    for state in STATES:
        fig = draw(rows, state)
        problems = audit(fig, state)
        stem = stems[state]
        if problems:
            failed = True
            print(f"{stem}: FAIL")
            for item in problems:
                print(f"  - {item}")
        else:
            print(f"{stem}: layout audit passed")
        write(fig, stem)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
