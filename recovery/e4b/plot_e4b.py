#!/usr/bin/env python3
"""Synthetic layout sample for experiment 4b. Not an experimental result.

Reads e4b_beta.json and writes e4b-beta.pdf (vector, 178 mm wide) and
e4b-beta.png next to this script. Does not touch shared paper sources.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerBase
from matplotlib.lines import Line2D
from matplotlib.patches import ConnectionPatch, Rectangle

HERE = Path(__file__).resolve().parent
DATA = HERE / "e4b_beta.json"
PDF = HERE / "e4b-beta.pdf"
PNG = HERE / "e4b-beta.png"

WIDTH_MM = 178.0
HEIGHT_MM = 79.0
MM_TO_IN = 1.0 / 25.4

INK = "#262B30"
MUTED = "#5C6B76"
FRAME = "#5C6B76"
GRID = "#E1E6EA"

# Five series colors. Role is marker shape, not a second palette.
SERIES = {
    "0": "#1B4F72",
    "0.25": "#1A7A6D",
    "0.5": "#C47B2B",
    "0.75": "#8C4A6A",
    "1": "#3E454C",
}
BETA_LABEL = {
    "0": r"$\beta$ = 0",
    "0.25": r"$\beta$ = 0.25",
    "0.5": r"$\beta$ = 0.5",
    "0.75": r"$\beta$ = 0.75",
    "1": r"$\beta$ = 1",
}
BETA_VALUE = {"0": 0.0, "0.25": 0.25, "0.5": 0.5, "0.75": 0.75, "1": 1.0}

K_BAND = {
    2: "#F4F7F8",
    4: "#F7F5F1",
    8: "#F3F6F4",
}


def kh_label(k: int, h: int) -> str:
    return f"({k}, {h})"


def cost(u: float, q: float, beta: float) -> float:
    return u - (1.0 - beta) * q


class OverlayHandler(HandlerBase):
    """Legend glyph: open diamond with a star centered on it."""

    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        cx = 0.5 * width - 0.5 * xdescent
        cy = 0.5 * height - 0.5 * ydescent
        diamond = Line2D(
            [cx],
            [cy],
            marker="D",
            markersize=6.4,
            markerfacecolor="white",
            markeredgecolor=INK,
            markeredgewidth=1.05,
            linestyle="None",
            color=INK,
        )
        star = Line2D(
            [cx],
            [cy],
            marker="*",
            markersize=7.2,
            markerfacecolor=INK,
            markeredgecolor="white",
            markeredgewidth=0.55,
            linestyle="None",
            color=INK,
        )
        diamond.set_transform(trans)
        star.set_transform(trans)
        return [diamond, star]


def load_rows():
    payload = json.loads(DATA.read_text())
    rows = payload["configs"]
    keys = [(row["k"], row["h"]) for row in rows]
    if keys != sorted(keys, key=lambda kh: (kh[0], kh[1])):
        raise SystemExit("configs must be ordered by k then h")
    index = {kh: i for i, kh in enumerate(keys)}
    zoom = [(item["k"], item["h"]) for item in payload["zoom_configs"]]
    if any(kh not in index for kh in zoom):
        raise SystemExit("zoom category is not on the main axis")
    zidx = [index[kh] for kh in zoom]
    if zidx != list(range(zidx[0], zidx[0] + len(zidx))):
        raise SystemExit("zoom categories must be a contiguous run")
    betas = payload["betas_drawn"]
    if betas != ["0", "0.25", "0.5", "0.75", "1"]:
        raise SystemExit("main figure is the five confirmed betas")
    for key, label in BETA_LABEL.items():
        if key in {"0.25", "0.5", "0.75"} and "0." not in label:
            raise SystemExit(f"beta label missing a leading zero: {label}")
        if label.startswith(r"$\beta$ = .") or "=. " in label:
            raise SystemExit(f"beta label can be misread: {label}")
    curves = {}
    for key in betas:
        beta = BETA_VALUE[key]
        curves[key] = [cost(row["U"], row["Q"], beta) for row in rows]
        pred = payload["predicted"][key]
        meas = min(range(len(rows)), key=lambda i: (curves[key][i], i))
        expect = payload["expected_measured"][key]
        got = rows[meas]
        if (got["k"], got["h"]) != (expect["k"], expect["h"]):
            raise SystemExit(f"measured argmin for beta {key} drifted")
        pk = (pred["k"], pred["h"])
        if pk not in index:
            raise SystemExit(f"predicted config for beta {key} is not on the axis")
        # The mark has to sit on this curve's measured cost, not on a predicted height.
        pred_y = curves[key][index[pk]]
        meas_y = curves[key][meas]
        if pred_y != cost(rows[index[pk]]["U"], rows[index[pk]]["Q"], beta):
            raise SystemExit("predicted mark left the measured curve")
        if meas_y != curves[key][meas]:
            raise SystemExit("measured mark left the curve")
    return payload, rows, curves, index, zidx


def style_axes(ax, xs, labels):
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=7.5, color=INK)
    ax.tick_params(axis="y", labelsize=7.5, colors=MUTED, width=0.5, length=3)
    ax.tick_params(axis="x", colors=MUTED, width=0.5, length=3)
    ax.grid(axis="y", color=GRID, lw=0.45, zorder=1)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color("#C5CED4")
        spine.set_linewidth(0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def draw_bands(ax, rows, x0, x1):
    spans = []
    start = 0
    for i, row in enumerate(rows):
        if i == len(rows) - 1 or rows[i + 1]["k"] != row["k"]:
            spans.append((start, i, row["k"]))
            start = i + 1
    for lo, hi, k in spans:
        left = max(x0, lo - 0.5)
        right = min(x1, hi + 0.5)
        if right <= left:
            continue
        ax.axvspan(left, right, color=K_BAND[k], zorder=0, lw=0)


def draw_series(ax, curves, rows, index, keep, ylim):
    xs_all = list(range(len(rows)))
    for key in ("0", "0.25", "0.5", "0.75", "1"):
        color = SERIES[key]
        xs = [i for i in xs_all if i in keep]
        ys = [curves[key][i] for i in xs]
        ax.plot(
            xs,
            ys,
            color=color,
            lw=1.45,
            marker="o",
            ms=3.1,
            mew=0,
            solid_capstyle="round",
            zorder=3,
        )
    return ylim


def draw_roles(ax, payload, curves, index, keep):
    for key in ("0", "0.25", "0.5", "0.75", "1"):
        color = SERIES[key]
        pred = payload["predicted"][key]
        meas = payload["expected_measured"][key]
        pi = index[(pred["k"], pred["h"])]
        mi = index[(meas["k"], meas["h"])]
        same = pi == mi
        if same and mi in keep:
            y = curves[key][mi]
            ax.scatter(
                [mi],
                [y],
                s=86,
                marker="D",
                facecolors="white",
                edgecolors=color,
                linewidths=1.15,
                zorder=6,
            )
            ax.scatter(
                [mi],
                [y],
                s=58,
                marker="*",
                c=color,
                edgecolors="white",
                linewidths=0.55,
                zorder=7,
            )
            continue
        if pi in keep:
            ax.scatter(
                [pi],
                [curves[key][pi]],
                s=42,
                marker="D",
                facecolors="white",
                edgecolors=color,
                linewidths=1.15,
                zorder=6,
            )
        if mi in keep:
            ax.scatter(
                [mi],
                [curves[key][mi]],
                s=78,
                marker="*",
                c=color,
                edgecolors="white",
                linewidths=0.6,
                zorder=7,
            )


def build():
    payload, rows, curves, index, zidx = load_rows()
    labels = [kh_label(row["k"], row["h"]) for row in rows]
    plt.rcParams.update(
        {
            "font.family": "Liberation Serif",
            "mathtext.fontset": "stix",
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.labelcolor": INK,
            "text.color": INK,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.unicode_minus": False,
        }
    )
    fig = plt.figure(figsize=(WIDTH_MM * MM_TO_IN, HEIGHT_MM * MM_TO_IN), dpi=300)
    fig.patch.set_facecolor("white")

    main = fig.add_axes((0.075, 0.085, 0.585, 0.79))
    zoom = fig.add_axes((0.748, 0.085, 0.232, 0.79))

    all_y = [y for series in curves.values() for y in series]
    main_lo, main_hi = min(all_y) - 10, max(all_y) + 12
    zoom_vals = [curves[key][i] for key in curves for i in zidx]
    zoom_lo, zoom_hi = min(zoom_vals) - 6, max(zoom_vals) + 7

    x_left, x_right = -0.55, len(rows) - 0.35
    z_left, z_right = zidx[0] - 0.62, zidx[-1] + 0.62

    for ax, lo, hi, xlim in (
        (main, main_lo, main_hi, (x_left, x_right)),
        (zoom, zoom_lo, zoom_hi, (z_left, z_right)),
    ):
        draw_bands(ax, rows, xlim[0], xlim[1])
        ax.set_xlim(*xlim)
        ax.set_ylim(lo, hi)

    draw_series(main, curves, rows, index, set(range(len(rows))), (main_lo, main_hi))
    draw_series(zoom, curves, rows, index, set(zidx), (zoom_lo, zoom_hi))
    draw_roles(main, payload, curves, index, set(range(len(rows))))
    draw_roles(zoom, payload, curves, index, set(zidx))

    style_axes(main, list(range(len(rows))), labels)
    style_axes(zoom, zidx, [labels[i] for i in zidx])
    main.set_yticks([60, 80, 100, 120, 140, 160])
    zoom.set_yticks([70, 80, 90, 100, 110, 120])
    main.set_ylabel(r"equivalent input tokens,  $U-(1-\beta)Q$", fontsize=8)
    main.set_xlabel(r"configuration $(k, h)$", fontsize=8, labelpad=3)

    box = Rectangle(
        (z_left, zoom_lo),
        z_right - z_left,
        zoom_hi - zoom_lo,
        fill=False,
        edgecolor=FRAME,
        linewidth=0.85,
        linestyle="-",
        zorder=5,
        clip_on=False,
    )
    main.add_patch(box)
    for y in (zoom_lo, zoom_hi):
        fig.add_artist(
            ConnectionPatch(
                xyA=(z_right, y),
                coordsA="data",
                axesA=main,
                xyB=(z_left, y),
                coordsB="data",
                axesB=zoom,
                color=FRAME,
                lw=0.75,
                zorder=1,
            )
        )

    line_handles = [
        Line2D([0], [0], color=SERIES[key], lw=1.6, label=BETA_LABEL[key])
        for key in ("0", "0.25", "0.5", "0.75", "1")
    ]
    pred_handle = Line2D(
        [0],
        [0],
        marker="D",
        markersize=5.6,
        markerfacecolor="white",
        markeredgecolor=INK,
        markeredgewidth=1.05,
        linestyle="None",
        color=INK,
        label="predicted",
    )
    meas_handle = Line2D(
        [0],
        [0],
        marker="*",
        markersize=8.2,
        markerfacecolor=INK,
        markeredgecolor="white",
        markeredgewidth=0.5,
        linestyle="None",
        color=INK,
        label="measured",
    )
    both_handle = Line2D([0], [0], linestyle="None", label="both roles")
    fig.legend(
        line_handles + [pred_handle, meas_handle, both_handle],
        [h.get_label() for h in line_handles] + ["predicted", "measured", "both roles"],
        loc="upper center",
        bbox_to_anchor=(0.50, 0.985),
        ncol=8,
        frameon=False,
        fontsize=7.5,
        handlelength=1.6,
        handletextpad=0.35,
        columnspacing=0.85,
        borderaxespad=0,
        handler_map={both_handle: OverlayHandler()},
    )

    fig.savefig(PDF, dpi=300)
    fig.savefig(PNG, dpi=300)
    plt.close(fig)
    check_page(PDF)
    print(f"wrote {PDF}")
    print(f"wrote {PNG}")


def check_page(path: Path):
    import pymupdf

    doc = pymupdf.open(path)
    page = doc[0]
    width_mm = page.rect.width * 25.4 / 72.0
    if abs(width_mm - WIDTH_MM) > 0.2:
        raise SystemExit(f"PDF width {width_mm:.2f} mm is not {WIDTH_MM} mm")
    if doc[0].get_images():
        raise SystemExit("PDF contains a raster image; expected vector marks")
    print(f"pdf {width_mm:.2f} mm x {page.rect.height * 25.4 / 72.0:.2f} mm, vector")


if __name__ == "__main__":
    build()
