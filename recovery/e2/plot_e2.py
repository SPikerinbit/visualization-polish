"""E2 measured/predicted surfaces for a PVLDB double-column layout preview.

The mesh follows ``实验结果可视化/可参考：实验二3D/plot_surface.py``:

* one ``Poly3DCollection`` so both surfaces are depth-sorted together
* orthographic camera ``elev=26``, ``azim=-54``
* a square is drawn only when at least three corners exist
* adjacent grid edges that never entered a triangle are still stroked
* faces ``#087F9B`` at 0.55 and ``#DA821E`` at 0.22

``plot_surface.py`` puts the predicted-minimum diamond on the predicted
height. The confirmed rule replaces that one placement: the diamond uses
the measured height of the same ``(k, h)``. When the two roles share a
configuration, one combined mark is drawn at that single measured height.

Heights are a schematic field. They are not vLLM measurements and not the
production cost model (``finite.py`` was not available and is not called).
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba
from matplotlib.legend_handler import HandlerTuple
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
REFERENCE = ROOT / "reference" / "fig-E2-cost-surface-reference.png"

# Paper figure* width: sigconf text width is 7.0 in = 177.8 mm.
PAGE_WIDTH_IN = 7.0

BLUE = "#087F9B"
ORANGE = "#DA821E"
INK = "#20303D"
GRAY = "#657581"
TICK = "#516370"
WARN = "#8A3B32"

M = 20
RUNS = 25
XLIM = (1.35, 26.4)
YLIM = (0.30, 10.95)
XTICKS = (2, 8, 14, 20, 25)
YTICKS = (1, 4, 7, 10)
# z is taller than the poster script's box so the sheet has a visible slope
# inside a 178 mm figure. The long k axis would otherwise flatten it.
BOX = (2.05, 1.02, 1.38)
CAMERA = dict(elev=26, azim=-54)

# Removed only on the gap panels, so a high triangle cannot be joined to the
# main sheet. These points are legal; dropping them is a synthetic hole, not
# a measured missing cell. See NOTES.md.
LT_GAP = {(3, 5), (3, 6), (4, 4), (5, 4), (6, 5)}
SW_GAP = {(2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (3, 4), (4, 4)}


def max_segment(g: int, m: int) -> int:
    """Same rule as plan.py ``max_segment``."""
    return m // (1 + (g - 1).bit_length()) if g > 1 else m


def legal_domain(family: str) -> list[tuple[int, int]]:
    """Structural fixed-(k, h) grid counted in the experiment contract.

    LT: k = 2..min(runs, 2^(m-1)), h = 1..max_segment(k, m) → 101 points.
    SW: k = 2..min(runs, m), h = 1..(m // k) → 46 points.
    Full-mode ``select_parameters`` collapses SW h to None; this grid is the
    fixed-parameter domain the contract counts, not that collapsed search.
    """
    if family == "LT":
        upper = min(RUNS, 2 ** (M - 1))
        points = [
            (k, h)
            for k in range(2, upper + 1)
            for h in range(1, max_segment(k, M) + 1)
        ]
    elif family == "SW":
        upper = min(RUNS, M)
        points = [
            (k, h)
            for k in range(2, upper + 1)
            for h in range(1, (M // k) + 1)
        ]
    else:
        raise ValueError(family)
    return points


def schematic_measured(k: int, h: int, valley_k: float, valley_h: float, phase: float) -> float:
    """Smooth stand-in, in thousands of tokens. Not a cost model.

    A bowl in k and h, plus a mild rise with h, so the sheet slopes and the
    low region is not glued to h = 1 on every panel. Coefficients are capped
    so one corner cannot stretch the shared z axis.
    """
    dk = (k - valley_k) / 10.0
    dh = (h - valley_h) / 4.2
    return 146.0 + 3.4 * (h - 1) + 15.0 * dk * dk + 10.0 * dh * dh + 1.2 * math.sin(0.36 * k + phase)


def schematic_predicted(
    k: int, h: int, kind: str, valley_k: float, valley_h: float, phase: float, measured: float,
) -> float:
    if kind == "bias":
        # Same shape, large level error. Argmin matches; the surfaces do not.
        return measured + 24.0
    if kind == "shift":
        return schematic_measured(k, h, valley_k + 7.0, valley_h + 1.0, phase + 1.4) + 12.0
    if kind == "warp":
        return schematic_measured(k, h, valley_k - 6.0, valley_h + 1.5, phase + 0.8) + 8.0 * math.sin(0.62 * k + phase)
    if kind == "cross":
        # High where the measured field is low, so the pick is a bad configuration.
        return 168.0 + 0.72 * (155.0 - measured) + 4.0 * math.sin(0.45 * h + 0.2 * k)
    raise ValueError(kind)


@dataclass(frozen=True)
class Row:
    k: int
    h: int
    u: float
    p: float


@dataclass(frozen=True)
class Series:
    spec: dict
    rows: list[Row]
    tri: np.ndarray
    loose: list[tuple[int, int]]
    best: Row
    selected: Row

    @property
    def coincide(self) -> bool:
        return (self.best.k, self.best.h) == (self.selected.k, self.selected.h)


def _triangulate(index: dict[tuple[int, int], int]) -> list[list[int]]:
    if not index:
        return []
    ks = [k for k, _h in index]
    hs = [h for _k, h in index]
    triangles: list[list[int]] = []
    for k in range(min(ks), max(ks)):
        for h in range(min(hs), max(hs)):
            square = [(k, h), (k + 1, h), (k + 1, h + 1), (k, h + 1)]
            present = [corner for corner in square if corner in index]
            if len(present) < 3:
                continue
            ids = [index[corner] for corner in present]
            triangles.append(ids[:3])
            if len(ids) == 4:
                triangles.append([ids[0], ids[2], ids[3]])
    return triangles


def build_series(spec: dict) -> Series:
    gap = LT_GAP if spec["family"] == "LT" else SW_GAP
    omitted = gap if spec["gap"] else set()
    rows = []
    for k, h in legal_domain(spec["family"]):
        if (k, h) in omitted:
            continue
        measured = schematic_measured(k, h, spec["valley_k"], spec["valley_h"], spec["phase"])
        predicted = schematic_predicted(
            k, h, spec["kind"], spec["valley_k"], spec["valley_h"], spec["phase"], measured,
        )
        rows.append(Row(k, h, measured, predicted))
    rows.sort(key=lambda row: (row.k, row.h))
    index = {(row.k, row.h): i for i, row in enumerate(rows)}
    triangles = _triangulate(index)
    if not triangles:
        raise RuntimeError(f"no triangles for {spec['letter']}")
    triangle_edges = {
        tuple(sorted((int(tri[a]), int(tri[b]))))
        for tri in triangles
        for a, b in ((0, 1), (1, 2), (2, 0))
    }
    grid_edges = set()
    for (k, h), i in index.items():
        for neighbor in ((k + 1, h), (k, h + 1)):
            if neighbor in index:
                grid_edges.add(tuple(sorted((i, index[neighbor]))))
    loose = sorted(grid_edges - triangle_edges)
    best = min(rows, key=lambda row: (row.u, row.k, row.h))
    selected = min(rows, key=lambda row: (row.p, row.k, row.h))
    return Series(spec, rows, np.asarray(triangles, dtype=int), loose, best, selected)


# Locked after the schematic field was bounded. Four labels stay separable on a
# 2×3 spine; every drawn height has to fall inside this window.
ZLIM = (108.0, 292.0)
ZTICKS = (120, 170, 220, 270)


def shared_z(series_list: list[Series]) -> tuple[tuple[float, float], tuple[int, ...]]:
    values = [value for series in series_list for row in series.rows for value in (row.u, row.p)]
    if min(values) <= ZLIM[0] or max(values) >= ZLIM[1]:
        raise RuntimeError(f"schematic height {min(values):.1f}..{max(values):.1f} escapes {ZLIM}")
    return ZLIM, ZTICKS


def _sizes(layout: str) -> dict:
    # Poster dots (s≈12 on a 13.6 in figure) cover the faces at column width.
    # Keep a vertex mark, but smaller than the triangle it sits on.
    if layout == "hero":
        return dict(mu=5, mp=6, star=230, diamond=80, edge_b=0.70, edge_o=1.05, loose=0.90, dot_lw=0.25, mark_lw=0.65)
    if layout == "2x2":
        return dict(mu=3.2, mp=3.6, star=96, diamond=34, edge_b=0.48, edge_o=0.72, loose=0.55, dot_lw=0.18, mark_lw=0.5)
    if layout == "2x3":
        return dict(mu=2.2, mp=2.6, star=70, diamond=24, edge_b=0.40, edge_o=0.58, loose=0.42, dot_lw=0.15, mark_lw=0.4)
    raise ValueError(layout)


def _paint_panes(ax) -> None:
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.fill = False
        axis.pane.set_edgecolor("#E8EDF0")
        axis._axinfo["grid"]["color"] = "#DFE6EA"
        axis._axinfo["grid"]["linewidth"] = 0.55
        axis.line.set_color("#A8B4BC")


def draw_series(ax, series: Series, layout: str, zlim, zticks, labels: dict) -> None:
    """Draw both surfaces on one axes. ``labels`` selects which titles to print."""
    size = _sizes(layout)
    rows = series.rows
    x = np.array([row.k for row in rows], dtype=float)
    y = np.array([row.h for row in rows], dtype=float)
    measured = np.array([row.u for row in rows], dtype=float)
    predicted = np.array([row.p for row in rows], dtype=float)
    faces, colors, edges, widths = [], [], [], []
    # plot_surface.py uses 0.55 / 0.22, which read on a 13.6 in poster and wash
    # out at 178 mm. These alphas keep that blue sheet / orange tint, only heavier.
    for z, color, alpha, width, edge_alpha in (
        (measured, BLUE, 0.68, size["edge_b"], 0.78),
        (predicted, ORANGE, 0.34, size["edge_o"], 0.92),
    ):
        xyz = np.column_stack((x, y, z))
        for triangle in series.tri:
            faces.append(xyz[triangle])
            colors.append(to_rgba(color, alpha))
            edges.append(to_rgba(color, edge_alpha))
            widths.append(width)
    poly = Poly3DCollection(
        faces,
        facecolors=colors,
        edgecolors=edges,
        linewidths=widths,
        zsort="average",
        antialiased=True,
        shade=False,
    )
    ax.add_collection3d(poly)
    for a, b in series.loose:
        for z, color in ((measured, BLUE), (predicted, ORANGE)):
            ax.plot(
                x[[a, b]],
                y[[a, b]],
                z[[a, b]],
                color=color,
                linewidth=size["loose"],
                alpha=0.85,
                solid_capstyle="round",
                zorder=2,
            )
    ax.scatter(
        x, y, measured,
        s=size["mu"], c=BLUE, edgecolors="white", linewidths=size["dot_lw"],
        alpha=0.92, depthshade=False, zorder=3,
    )
    ax.scatter(
        x, y, predicted,
        s=size["mp"], facecolors="none", edgecolors=ORANGE, linewidths=0.65,
        alpha=0.95, depthshade=False, zorder=4,
    )
    best, selected = series.best, series.selected
    if series.coincide:
        ax.scatter(
            [best.k], [best.h], [best.u],
            s=size["diamond"] * 1.45, marker="D", c=ORANGE, edgecolors="white",
            linewidths=size["mark_lw"], depthshade=False, zorder=8,
        )
        ax.scatter(
            [best.k], [best.h], [best.u],
            s=size["star"], marker="*", c=BLUE, edgecolors="white",
            linewidths=size["mark_lw"], depthshade=False, zorder=9,
        )
    else:
        ax.scatter(
            [best.k], [best.h], [best.u],
            s=size["star"], marker="*", c=BLUE, edgecolors="white",
            linewidths=size["mark_lw"], depthshade=False, zorder=8,
        )
        ax.scatter(
            [selected.k], [selected.h], [selected.u],
            s=size["diamond"], marker="D", c=ORANGE, edgecolors="white",
            linewidths=size["mark_lw"], depthshade=False, zorder=9,
        )
    tick = {"hero": 8.0, "2x2": 7.0, "2x3": 6.5}[layout]
    label = {"hero": 9.0, "2x2": 7.5, "2x3": 7.0}[layout]
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_zlim(*zlim)
    ax.set_xticks(list(XTICKS))
    ax.set_yticks(list(YTICKS))
    ax.set_zticks(list(zticks))
    ax.view_init(**CAMERA)
    ax.set_proj_type("ortho")
    zoom = {"hero": 0.88, "2x2": 0.80, "2x3": 0.76}[layout]
    ax.set_box_aspect(BOX, zoom=zoom)
    ax.view_init(**CAMERA)
    _paint_panes(ax)
    ax.tick_params(axis="x", labelsize=tick, pad=0, colors=TICK)
    ax.tick_params(axis="y", labelsize=tick, pad=0, colors=TICK)
    ax.tick_params(axis="z", labelsize=tick, pad=1, colors=TICK)
    pad = {"hero": 8, "2x2": 3, "2x3": 2}[layout]
    if labels.get("x"):
        ax.set_xlabel("Fan-in k", labelpad=pad, color=INK, fontsize=label)
    else:
        ax.set_xlabel("")
    if labels.get("y"):
        # The full phrase is longer than the h axis on a small multiple and was
        # clipped. The hero keeps it; the groups use the short form.
        y_text = "Segment length h" if layout == "hero" else "Segment h"
        ax.set_ylabel(y_text, labelpad=pad, color=INK, fontsize=label)
    else:
        ax.set_ylabel("")
    if labels.get("z"):
        z_text = "Merge input tokens (1k)" if layout == "hero" else "Tokens (1k)"
        ax.set_zlabel(z_text, labelpad=pad + 2, color=INK, fontsize=label)
    else:
        ax.set_zlabel("")
    ax.set_title(panel_title(series.spec), color=INK, fontsize=label, pad=1, loc="center")


def panel_title(spec: dict) -> str:
    return f"({spec['letter']}) 9B, DL20, slot {spec['slot']}, {spec['demand']}, {spec['family']}"


def legend_handles():
    measured = Line2D([0], [0], color=BLUE, linewidth=5, alpha=0.7, marker="o", markersize=4.5, label="Measured")
    predicted = Line2D(
        [0], [0], color=ORANGE, linewidth=2.2, alpha=0.95, marker="o",
        markerfacecolor="white", markeredgecolor=ORANGE, markersize=4.5, label="Predicted",
    )
    star = Line2D(
        [0], [0], marker="*", color="none", markerfacecolor=BLUE, markeredgecolor="white",
        markeredgewidth=0.6, markersize=11, label="Measured minimum",
    )
    diamond = Line2D(
        [0], [0], marker="D", color="none", markerfacecolor=ORANGE, markeredgecolor="white",
        markeredgewidth=0.5, markersize=6.5, label="Predicted minimum, measured height",
    )
    under = Line2D(
        [0], [0], marker="D", color="none", markerfacecolor=ORANGE, markeredgecolor="white",
        markeredgewidth=0.4, markersize=6.5, linestyle="None",
    )
    over = Line2D(
        [0], [0], marker="*", color="none", markerfacecolor=BLUE, markeredgecolor="white",
        markeredgewidth=0.4, markersize=11, linestyle="None",
    )
    return [measured, predicted, star, diamond, (under, over)]


def _chrome(fig, footer: str, legend_size: float) -> None:
    fig.text(
        0.012, 0.988, "Synthetic layout preview. Not experimental results.",
        fontsize=8.5, color=WARN, va="top", ha="left",
    )
    fig.text(
        0.012, 0.955,
        "Shared camera and z ticks. A missing corner is not filled. Markers sit on a measured height.",
        fontsize=7.0, color=GRAY, va="top", ha="left",
    )
    fig.legend(
        legend_handles(),
        [
            "Measured",
            "Predicted",
            "Measured minimum",
            "Predicted minimum, measured height",
            "Both minima, one height",
        ],
        handler_map={tuple: HandlerTuple(ndivide=None, pad=0.15)},
        loc="upper left",
        bbox_to_anchor=(0.008, 0.932),
        frameon=False,
        ncol=3,
        fontsize=legend_size,
        borderaxespad=0,
        handlelength=1.8,
        columnspacing=1.05,
        labelcolor=INK,
    )
    fig.text(0.012, 0.012, footer, fontsize=6.5, color=GRAY, va="bottom", ha="left")


FOOTER = (
    "z is a schematic merge-input field, in thousands, not measured tokens. "
    "Domain outline is the m = 20 structural cap (LT 101, SW 46). "
    "Dataset, query, and 2×2 vs 2×3 are not chosen."
)


def _apply_font() -> None:
    plt.rcParams.update({
        "font.family": "Liberation Serif",
        "font.size": 8,
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.facecolor": "white",
    })


def render_figure(
    name: str,
    specs: list[dict],
    shape: tuple[int, int],
    height: float,
    layout: str,
    zlim,
    zticks,
) -> list[Series]:
    _apply_font()
    series_list = [build_series(spec) for spec in specs]
    rows, cols = shape
    fig = plt.figure(figsize=(PAGE_WIDTH_IN, height), facecolor="white")
    legend_size = {"hero": 7.5, "2x2": 7.0, "2x3": 6.5}[layout]
    # Leave a band under the two-row legend so panel titles do not run into it.
    top = 0.74 if layout == "hero" else 0.73
    left = 0.06 if layout == "hero" else 0.045
    grid = fig.add_gridspec(
        rows, cols,
        left=left, right=0.978, bottom=(0.15 if layout == "hero" else 0.11), top=top,
        wspace=0.18 if cols == 1 else (0.26 if cols == 2 else 0.34),
        hspace=0.18 if rows == 1 else 0.32,
    )
    for index, series in enumerate(series_list):
        ax = fig.add_subplot(grid[index // cols, index % cols], projection="3d", computed_zorder=False)
        on_left = index % cols == 0
        on_bottom = index // cols == rows - 1
        draw_series(
            ax, series, layout, zlim, zticks,
            {"x": on_bottom, "y": on_left, "z": on_left},
        )
    _chrome(fig, FOOTER, legend_size)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=180)
    plt.close(fig)
    return series_list


def render_comparison(series: Series, zlim, zticks) -> None:
    """Same-frame original PNG against the hero surface, for parent review."""
    _apply_font()
    original = Image.open(REFERENCE).convert("RGB")
    frame_w, frame_h = 1047, 849
    fig = plt.figure(figsize=(frame_w / 160, frame_h / 160), facecolor="white")
    ax = fig.add_axes([0.08, 0.06, 0.86, 0.82], projection="3d", computed_zorder=False)
    draw_series(ax, series, "hero", zlim, zticks, {"x": True, "y": True, "z": True})
    ax.set_title("")
    fig.text(0.08, 0.955, "New hero, synthetic field, same camera family as plot_surface.py", fontsize=8, color=INK, va="top")
    png_path = OUT / "_hero_for_compare.png"
    fig.savefig(png_path, dpi=160)
    plt.close(fig)
    fresh = Image.open(png_path).convert("RGB")

    def fit(image: Image.Image) -> Image.Image:
        canvas = Image.new("RGB", (frame_w, frame_h), "white")
        copy = image.copy()
        copy.thumbnail((frame_w - 10, frame_h - 10), Image.Resampling.LANCZOS)
        canvas.paste(copy, ((frame_w - copy.width) // 2, (frame_h - copy.height) // 2))
        return canvas

    left, right = fit(original), fit(fresh)
    header_h = 42
    sheet = Image.new("RGB", (frame_w * 2 + 18, frame_h + header_h), "white")
    sheet.paste(left, (0, header_h))
    sheet.paste(right, (frame_w + 18, header_h))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", 22)
    draw.text((12, 8), "Original reference", fill=INK, font=font)
    draw.text((frame_w + 30, 8), "New hero (synthetic, not a result)", fill=INK, font=font)
    sheet.save(OUT / "compare-original-vs-hero.png", dpi=(160, 160))
    png_path.unlink()


def manifest(named: dict[str, list[Series]], zlim, zticks) -> None:
    payload = {
        "warning": "NOT EXPERIMENTAL RESULTS. Schematic heights only.",
        "zlim": list(zlim),
        "zticks": list(zticks),
        "camera": CAMERA,
        "box_aspect": list(BOX),
        "figures": {},
    }
    for name, series_list in named.items():
        payload["figures"][name] = []
        for series in series_list:
            payload["figures"][name].append({
                "title": panel_title(series.spec),
                "family": series.spec["family"],
                "kind": series.spec["kind"],
                "gap": series.spec["gap"],
                "n_points": len(series.rows),
                "n_triangles": int(len(series.tri)),
                "measured_min": {"k": series.best.k, "h": series.best.h, "z": round(series.best.u, 3)},
                "predicted_min_at_measured_height": {
                    "k": series.selected.k,
                    "h": series.selected.h,
                    "measured_z": round(series.selected.u, 3),
                    "predicted_z_not_drawn": round(series.selected.p, 3),
                },
                "coincide": series.coincide,
            })
    (OUT / "synthetic_manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


HERO = dict(
    letter="a", family="LT", demand="Full", slot=1, kind="shift",
    valley_k=14, valley_h=2.5, phase=0.3, gap=True,
)

SPECS_2X2 = [
    dict(letter="a", family="SW", demand="Full", slot=1, kind="shift", valley_k=5, valley_h=2.0, phase=0.2, gap=True),
    HERO | dict(letter="b"),
    dict(letter="c", family="SW", demand="LIMIT10", slot=1, kind="warp", valley_k=11, valley_h=3.0, phase=1.1, gap=False),
    dict(letter="d", family="LT", demand="LIMIT10", slot=1, kind="bias", valley_k=9, valley_h=3.0, phase=0.6, gap=False),
]

SPECS_2X3 = [
    HERO | dict(letter="a"),
    dict(letter="b", family="LT", demand="Full", slot=2, kind="warp", valley_k=16, valley_h=2.0, phase=1.3, gap=False),
    dict(letter="c", family="LT", demand="Full", slot=3, kind="bias", valley_k=7, valley_h=4.0, phase=0.8, gap=False),
    dict(letter="d", family="LT", demand="LIMIT10", slot=1, kind="cross", valley_k=12, valley_h=3.0, phase=0.4, gap=False),
    dict(letter="e", family="LT", demand="LIMIT10", slot=2, kind="shift", valley_k=6, valley_h=2.0, phase=1.8, gap=False),
    dict(letter="f", family="LT", demand="LIMIT10", slot=3, kind="warp", valley_k=18, valley_h=3.5, phase=2.2, gap=True),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    everyone = [build_series(spec) for spec in ([HERO] + SPECS_2X2 + SPECS_2X3)]
    zlim, zticks = shared_z(everyone)
    hero = render_figure("e2-hero-panel", [HERO], (1, 1), 4.20, "hero", zlim, zticks)
    two = render_figure("e2-layout-2x2", SPECS_2X2, (2, 2), 6.45, "2x2", zlim, zticks)
    three = render_figure("e2-layout-2x3", SPECS_2X3, (2, 3), 5.55, "2x3", zlim, zticks)
    render_comparison(hero[0], zlim, zticks)
    manifest({"hero": hero, "2x2": two, "2x3": three}, zlim, zticks)
    print(json.dumps({"zlim": zlim, "zticks": zticks, "hero_coincide": hero[0].coincide}, indent=2))


if __name__ == "__main__":
    main()
