"""Round-2 E2: predicted vs measured cost surfaces only (no quality inset).

Mechanism aligned with ``refs/recovery-spec/.../plot_surface.py``:
interleaved Poly3DCollection, orthographic camera elev=26 azim=-54,
adjacent-grid triangulation, vertex markers on every (k,h) sample.

Heights are synthetic schematic fields — not experimental results.
Predicted-minimum diamond is drawn at the measured height of that (k,h).
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
PANELS = OUT / "panels"
REFS = ROOT / "refs"
REFERENCE = REFS / "fig-E2-cost-surface-reference.png"

PAGE_WIDTH_IN = 7.0
BLUE = "#087F9B"
ORANGE = "#DA821E"
INK = "#20303D"
GRAY = "#657581"
TICK = "#516370"

M = 20
RUNS = 25
BOX = (1.45, 1.00, 0.92)
CAMERA = dict(elev=26, azim=-54)

LT_GAP = {(3, 5), (3, 6), (4, 4), (5, 4), (6, 5)}
SW_GAP = {(2, 5), (3, 4), (4, 4)}


def max_segment(g: int, m: int) -> int:
    return m // (1 + (g - 1).bit_length()) if g > 1 else m


def legal_domain(family: str) -> list[tuple[int, int]]:
    if family == "LT":
        upper = min(RUNS, 2 ** (M - 1))
        return [
            (k, h)
            for k in range(2, upper + 1)
            for h in range(1, max_segment(k, M) + 1)
        ]
    if family == "SW":
        upper = min(RUNS, M)
        return [
            (k, h)
            for k in range(2, upper + 1)
            for h in range(1, (M // k) + 1)
        ]
    raise ValueError(family)


def schematic_measured(k: int, h: int, valley_k: float, valley_h: float, phase: float) -> float:
    dk = (k - valley_k) / 10.0
    dh = (h - valley_h) / 4.2
    return 146.0 + 3.4 * (h - 1) + 15.0 * dk * dk + 10.0 * dh * dh + 1.2 * math.sin(0.36 * k + phase)


def schematic_predicted(
    k: int, h: int, kind: str, valley_k: float, valley_h: float, phase: float, measured: float,
) -> float:
    if kind == "bias":
        return measured + 24.0
    if kind == "shift":
        return schematic_measured(k, h, valley_k + 7.0, valley_h + 1.0, phase + 1.4) + 12.0
    if kind == "warp":
        return schematic_measured(k, h, valley_k - 6.0, valley_h + 1.5, phase + 0.8) + 8.0 * math.sin(0.62 * k + phase)
    if kind == "cross":
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
    rows: list[Row] = []
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
        raise RuntimeError(f"no triangles for panel {spec.get('id')}")
    triangle_edges = {
        tuple(sorted((int(tri[a]), int(tri[b]))))
        for tri in triangles
        for a, b in ((0, 1), (1, 2), (2, 0))
    }
    grid_edges: set[tuple[int, int]] = set()
    for (k, h), i in index.items():
        for neighbor in ((k + 1, h), (k, h + 1)):
            if neighbor in index:
                grid_edges.add(tuple(sorted((i, index[neighbor]))))
    loose = sorted(grid_edges - triangle_edges)
    best = min(rows, key=lambda row: (row.u, row.k, row.h))
    selected = min(rows, key=lambda row: (row.p, row.k, row.h))
    return Series(spec, rows, np.asarray(triangles, dtype=int), loose, best, selected)


def _tick_step(span: float) -> int:
    raw = span / 3.3
    for step in (10, 20, 25, 30, 40, 50):
        if step >= raw * 0.85:
            return step
    return 50


def shared_z(series_list: list[Series]) -> tuple[tuple[float, float], tuple[int, ...]]:
    values = [value for series in series_list for row in series.rows for value in (row.u, row.p)]
    low, high = min(values), max(values)
    span = max(high - low, 1.0)
    z0, z1 = low - 0.08 * span, high + 0.10 * span
    step = _tick_step(z1 - z0)
    start = math.ceil((z0 + 0.06 * span) / step) * step
    ticks: list[int] = []
    value = start
    while value <= z1 - 0.05 * span + 1e-6:
        ticks.append(int(round(value)))
        value += step
    if len(ticks) < 3:
        ticks = [int(round(z0 + span * frac)) for frac in (0.22, 0.50, 0.78)]
    return (z0, z1), tuple(ticks[:4])


def xy_window(family: str) -> tuple[tuple[float, float], tuple[float, float], tuple[int, ...], tuple[int, ...]]:
    points = legal_domain(family)
    k_max = max(k for k, _h in points)
    h_max = max(h for _k, h in points)
    xticks = (2, 8, 14, 20) if family == "SW" else (2, 8, 14, 20, 25)
    yticks = tuple(tick for tick in (1, 4, 7, 10) if tick <= h_max)
    return (1.25, k_max + 1.15), (0.35, h_max + 0.75), xticks, yticks


def _sizes(layout: str) -> dict:
    if layout == "hero":
        return dict(
            face_b=0.55, face_o=0.22, edge_b=0.55, edge_o=0.80, loose=0.90,
            pt_s=12.0, pt_lw_b=0.25, pt_lw_o=0.65, star=175, diamond=85, mark_lw=0.9,
            tick=12.0, label=16.0, title=13.0, zoom=1.04,
        )
    if layout == "2x5":
        return dict(
            face_b=0.58, face_o=0.26, edge_b=0.22, edge_o=0.28, loose=0.18,
            pt_s=5.5, pt_lw_b=0.22, pt_lw_o=0.48, star=95, diamond=38, mark_lw=0.45,
            tick=6.0, label=6.8, title=6.5, zoom=0.95,
        )
    if layout == "2x6":
        return dict(
            face_b=0.56, face_o=0.24, edge_b=0.18, edge_o=0.24, loose=0.16,
            pt_s=4.8, pt_lw_b=0.2, pt_lw_o=0.42, star=82, diamond=34, mark_lw=0.42,
            tick=5.6, label=6.4, title=6.2, zoom=0.94,
        )
    raise ValueError(layout)


def _paint_panes(ax) -> None:
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.fill = False
        axis.pane.set_edgecolor("#E8EDF0")
        axis._axinfo["grid"]["color"] = "#DFE6EA"
        axis._axinfo["grid"]["linewidth"] = 0.55
        axis.line.set_color("#A8B4BC")


def draw_series(ax, series: Series, layout: str, frame: dict, labels: dict) -> None:
    size = _sizes(layout)
    rows = series.rows
    x = np.array([row.k for row in rows], dtype=float)
    y = np.array([row.h for row in rows], dtype=float)
    measured = np.array([row.u for row in rows], dtype=float)
    predicted = np.array([row.p for row in rows], dtype=float)

    faces, colors, edges, widths = [], [], [], []
    for z, color, face_a, edge_w in (
        (measured, BLUE, size["face_b"], size["edge_b"]),
        (predicted, ORANGE, size["face_o"], size["edge_o"]),
    ):
        xyz = np.column_stack((x, y, z))
        for triangle in series.tri:
            faces.append(xyz[triangle])
            colors.append(to_rgba(color, face_a))
            edges.append(to_rgba(color, 0.64 if color == BLUE else 0.86))
            widths.append(edge_w)
    poly = Poly3DCollection(
        faces, facecolors=colors, edgecolors=edges, linewidths=widths,
        zsort="average", antialiased=True, shade=False,
    )
    ax.add_collection3d(poly)

    for a, b in series.loose:
        for z, color in ((measured, BLUE), (predicted, ORANGE)):
            ax.plot(
                x[[a, b]], y[[a, b]], z[[a, b]], color=color,
                linewidth=size["loose"], alpha=0.8, solid_capstyle="round", zorder=2,
            )

    ax.scatter(
        x, y, measured, s=size["pt_s"], c=BLUE, edgecolors="white",
        linewidths=size["pt_lw_b"], alpha=0.85, depthshade=False, zorder=3,
    )
    ax.scatter(
        x, y, predicted, s=size["pt_s"], facecolors="none", edgecolors=ORANGE,
        linewidths=size["pt_lw_o"], alpha=0.85, depthshade=False, zorder=4,
    )

    best, selected = series.best, series.selected
    if series.coincide:
        ax.scatter(
            [best.k], [best.h], [best.u], s=size["diamond"] * 1.35, marker="D",
            c=ORANGE, edgecolors="white", linewidths=size["mark_lw"], depthshade=False, zorder=8,
        )
        ax.scatter(
            [best.k], [best.h], [best.u], s=size["star"], marker="*",
            c=BLUE, edgecolors="white", linewidths=size["mark_lw"], depthshade=False, zorder=9,
        )
    else:
        ax.scatter(
            [best.k], [best.h], [best.u], s=size["star"], marker="*",
            c=BLUE, edgecolors="white", linewidths=size["mark_lw"], depthshade=False, zorder=8,
        )
        ax.scatter(
            [selected.k], [selected.h], [selected.u], s=size["diamond"], marker="D",
            c=ORANGE, edgecolors="white", linewidths=size["mark_lw"], depthshade=False, zorder=9,
        )

    pad = {"hero": 12, "2x5": 2, "2x6": 2}[layout]
    ax.set_xlim(*frame["xlim"])
    ax.set_ylim(*frame["ylim"])
    ax.set_zlim(*frame["zlim"])
    ax.set_xticks(list(frame["xticks"]))
    ax.set_yticks(list(frame["yticks"]))
    ax.set_zticks(list(frame["zticks"]))
    ax.view_init(**CAMERA)
    ax.set_proj_type("ortho")
    ax.set_box_aspect(BOX, zoom=size["zoom"])
    ax.view_init(**CAMERA)
    _paint_panes(ax)
    ax.tick_params(axis="x", labelsize=size["tick"], pad=0, colors=TICK)
    ax.tick_params(axis="y", labelsize=size["tick"], pad=0, colors=TICK)
    ax.tick_params(axis="z", labelsize=size["tick"], pad=1, colors=TICK)
    if labels.get("x"):
        ax.set_xlabel("Fan-in $k$" if layout == "hero" else "Fan-in $k$", labelpad=pad, color=INK, fontsize=size["label"])
    else:
        ax.set_xlabel("")
    if labels.get("y"):
        y_text = "Segment length $h$" if layout == "hero" else "Seg. $h$"
        ax.set_ylabel(y_text, labelpad=pad, color=INK, fontsize=size["label"])
    else:
        ax.set_ylabel("")
    if labels.get("z"):
        z_text = "Merge input tokens (1k)" if layout == "hero" else "Tokens (1k)"
        ax.set_zlabel(z_text, labelpad=pad + 1, color=INK, fontsize=size["label"])
    else:
        ax.set_zlabel("")
    short = panel_title(series.spec, short=layout != "hero")
    ax.set_title(short, color=INK, fontsize=size["title"], pad=0, loc="center")


def panel_title(spec: dict, short: bool = False) -> str:
    base = f"({spec['letter']}) {spec['family']}, {spec['demand']}, slot {spec['slot']}"
    if short:
        return base
    return f"{base}, 9B, DL20"


def legend_handles():
    measured = Line2D([0], [0], color=BLUE, linewidth=5, alpha=0.65, marker="o", markersize=4, label="Measured")
    predicted = Line2D(
        [0], [0], color=ORANGE, linewidth=2.5, alpha=0.85, marker="o",
        markerfacecolor="white", markersize=4, label="Predicted",
    )
    star = Line2D(
        [0], [0], marker="*", color="none", markerfacecolor=BLUE, markeredgecolor="white",
        markeredgewidth=0.5, markersize=9, linestyle="None",
    )
    diamond = Line2D(
        [0], [0], marker="D", color="none", markerfacecolor=ORANGE, markeredgecolor="white",
        markeredgewidth=0.45, markersize=5.5, linestyle="None",
    )
    return [measured, predicted, star, diamond, (diamond, star)]


def _legend(fig, fontsize: float) -> None:
    fig.legend(
        legend_handles(),
        ["Measured", "Predicted", "Measured min", "Predicted min (meas. height)", "Both minima"],
        handler_map={tuple: HandlerTuple(ndivide=None, pad=0.08)},
        loc="upper center",
        bbox_to_anchor=(0.5, 0.998),
        frameon=False,
        ncol=5,
        fontsize=fontsize,
        borderaxespad=0,
        handlelength=1.4,
        columnspacing=0.75,
        labelcolor=INK,
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


def _frames(series_list: list[Series]) -> list[dict]:
    grouped: dict[str, list[Series]] = {}
    for series in series_list:
        grouped.setdefault(series.spec["family"], []).append(series)
    cache: dict[str, dict] = {}
    for family, group in grouped.items():
        zlim, zticks = shared_z(group)
        xlim, ylim, xticks, yticks = xy_window(family)
        cache[family] = dict(xlim=xlim, ylim=ylim, zlim=zlim, xticks=xticks, yticks=yticks, zticks=zticks)
    return [cache[series.spec["family"]] for series in series_list]


def _grid_margins(cols: int) -> tuple[float, float, float, float, float, float]:
    if cols == 5:
        return 0.006, 0.998, 0.055, 0.905, 0.06, 0.18
    return 0.004, 0.998, 0.052, 0.902, 0.08, 0.16


def render_montage(name: str, specs: list[dict], cols: int, layout: str, height_in: float) -> list[Series]:
    _apply_font()
    series_list = [build_series(spec) for spec in specs]
    frames = _frames(series_list)
    rows = math.ceil(len(specs) / cols)
    left, right, bottom, top, wspace, hspace = _grid_margins(cols)
    fig = plt.figure(figsize=(PAGE_WIDTH_IN, height_in), facecolor="white")
    legend_size = _sizes(layout)["tick"] + 0.5
    grid = fig.add_gridspec(rows, cols, left=left, right=right, bottom=bottom, top=top, wspace=wspace, hspace=hspace)
    for index, series in enumerate(series_list):
        ax = fig.add_subplot(grid[index // cols, index % cols], projection="3d", computed_zorder=False)
        on_left = index % cols == 0
        on_bottom = index // cols == rows - 1
        draw_series(
            ax, series, layout, frames[index],
            {"x": on_bottom, "y": on_bottom and on_left, "z": on_left and index % rows == 0},
        )
    _legend(fig, legend_size)
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=220 if ext == "png" else None)
    plt.close(fig)
    return series_list


def render_panel(series: Series, stem: str) -> None:
    _apply_font()
    PANELS.mkdir(parents=True, exist_ok=True)
    frame = _frames([series])[0]
    fig = plt.figure(figsize=(1.85, 1.85), facecolor="white")
    ax = fig.add_subplot(111, projection="3d", computed_zorder=False)
    draw_series(ax, series, "2x6", frame, {"x": True, "y": True, "z": True})
    for ext in ("pdf", "png"):
        fig.savefig(PANELS / f"{stem}.{ext}", dpi=220 if ext == "png" else None, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def render_hero(spec: dict) -> Series:
    _apply_font()
    series = build_series(spec)
    frame = _frames([series])[0]
    fig = plt.figure(figsize=(7.0, 4.35), facecolor="white")
    ax = fig.add_axes([-0.02, 0.12, 0.78, 0.82], projection="3d", computed_zorder=False)
    draw_series(ax, series, "hero", frame, {"x": True, "y": True, "z": True})
    handles = [
        Line2D([0], [0], color=BLUE, linewidth=6, alpha=0.65, marker="o", markersize=5, label="Measured vLLM cost"),
        Line2D(
            [0], [0], color=ORANGE, linewidth=3, alpha=0.85, marker="o",
            markerfacecolor="white", markersize=5, label="Cost model prediction",
        ),
    ]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.02, 0.93), frameon=False, ncol=2, fontsize=11)
    fig.text(0.02, 0.97, "Cost only — Spearman quality panel removed", fontsize=9, color=GRAY)
    fig.text(0.02, 0.03, "Synthetic layout field; not experimental results.", fontsize=9, color=GRAY)
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"e2-hero-cost-only.{ext}", dpi=220 if ext == "png" else None)
    plt.close(fig)
    return series


def area_comparison() -> dict:
    from pypdf import PdfReader

    ref_exp5 = Path("/agent/repos/visualization-polish/paper/tex/fig/panels/exp5/exp5_movies_full_tokens.pdf")
    panel_pt = float(PdfReader(str(ref_exp5)).pages[0].mediabox.width)

    def fig_size(path: Path) -> tuple[float, float]:
        r = PdfReader(str(path)).pages[0]
        return float(r.mediabox.width) / 72, float(r.mediabox.height) / 72

    sizes = {
        "exp5_single_panel_source_pdf_in": panel_pt / 72,
        "e2_2x5": fig_size(OUT / "e2-layout-2x5.pdf"),
        "e2_2x6": fig_size(OUT / "e2-layout-2x6.pdf"),
    }
    sizes["target_textwidth_in"] = PAGE_WIDTH_IN
    sizes["exp5_figure_star_reference"] = "unpacked-paper/exp.tex fig:exp5-m (lines 417--472); no 3D k-sweep float found"

    img_a = Image.open(OUT / "e2-layout-2x5.png").convert("RGB")
    img_b = Image.open(OUT / "e2-layout-2x6.png").convert("RGB")
    pad = 36
    canvas = Image.new("RGB", (img_a.width + img_b.width + pad * 3, max(img_a.height, img_b.height) + 80), "white")
    canvas.paste(img_a, (pad, 60))
    canvas.paste(img_b, (img_a.width + pad * 2, 60))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", 20)
        small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", 16)
    except OSError:
        font = small = ImageFont.load_default()
    w5, h5 = sizes["e2_2x5"]
    w6, h6 = sizes["e2_2x6"]
    draw.text((pad, 12), f"10-panel (2×5): {w5:.2f}×{h5:.2f} in @ {PAGE_WIDTH_IN:.1f} in text width", fill=INK, font=font)
    draw.text(
        (img_a.width + pad * 2, 12),
        f"12-panel (2×6, exp5-m row pattern): {w6:.2f}×{h6:.2f} in",
        fill=INK,
        font=font,
    )
    draw.text(
        (pad, canvas.height - 28),
        "Same rendered width; compare vertical footprint to original k-sweep figure* (exp5-m). Heights are synthetic.",
        fill=GRAY,
        font=small,
    )
    evidence = ROOT / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    canvas.save(evidence / "area-compare-10-vs-12.png")
    canvas.save(evidence / "area-compare-10-vs-12.pdf", "PDF", resolution=150.0)
    (evidence / "area-metrics.json").write_text(json.dumps(sizes, indent=2), encoding="utf-8")
    return sizes


HERO_SPEC = dict(
    id="hero", letter="H", family="LT", demand="Full", slot=1, kind="shift",
    valley_k=14, valley_h=2.5, phase=0.3, gap=True,
)

SPECS_12 = [
    dict(id="p01", letter="a", family="LT", demand="Full", slot=1, kind="shift", valley_k=14, valley_h=2.5, phase=0.3, gap=True),
    dict(id="p02", letter="b", family="LT", demand="Full", slot=2, kind="warp", valley_k=16, valley_h=2.0, phase=1.3, gap=False),
    dict(id="p03", letter="c", family="LT", demand="Full", slot=3, kind="bias", valley_k=7, valley_h=4.0, phase=0.8, gap=False),
    dict(id="p04", letter="d", family="LT", demand="LIMIT10", slot=1, kind="cross", valley_k=12, valley_h=3.0, phase=0.4, gap=False),
    dict(id="p05", letter="e", family="LT", demand="LIMIT10", slot=2, kind="shift", valley_k=6, valley_h=2.0, phase=1.8, gap=False),
    dict(id="p06", letter="f", family="LT", demand="LIMIT10", slot=3, kind="warp", valley_k=18, valley_h=3.5, phase=2.2, gap=True),
    dict(id="p07", letter="g", family="SW", demand="Full", slot=1, kind="shift", valley_k=5, valley_h=2.0, phase=0.2, gap=True),
    dict(id="p08", letter="h", family="SW", demand="Full", slot=2, kind="warp", valley_k=11, valley_h=3.0, phase=1.1, gap=False),
    dict(id="p09", letter="i", family="SW", demand="Full", slot=3, kind="bias", valley_k=8, valley_h=2.5, phase=0.65, gap=False),
    dict(id="p10", letter="j", family="SW", demand="LIMIT10", slot=1, kind="cross", valley_k=9, valley_h=2.0, phase=1.5, gap=False),
    dict(id="p11", letter="k", family="SW", demand="LIMIT10", slot=2, kind="shift", valley_k=13, valley_h=1.5, phase=0.95, gap=False),
    dict(id="p12", letter="l", family="SW", demand="LIMIT10", slot=3, kind="warp", valley_k=17, valley_h=1.0, phase=2.0, gap=False),
]

SPECS_10 = SPECS_12[:3] + SPECS_12[3:5] + SPECS_12[6:9] + SPECS_12[9:11]


def write_manifest(series: dict[str, list[Series]]) -> None:
    payload = {
        "warning": "NOT EXPERIMENTAL RESULTS — schematic heights for layout only.",
        "camera": CAMERA,
        "reference_script": "refs/recovery-spec/references/scripts-3d/plot_surface.py",
        "figures": {},
    }
    for name, items in series.items():
        payload["figures"][name] = [
            {
                "panel": s.spec["id"],
                "title": panel_title(s.spec),
                "n_points": len(s.rows),
                "n_triangles": int(len(s.tri)),
                "coincide": s.coincide,
            }
            for s in items
        ]
    (OUT / "synthetic_manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    hero = render_hero(HERO_SPEC)
    ten = render_montage("e2-layout-2x5", SPECS_10, cols=5, layout="2x5", height_in=3.95)
    twelve = render_montage("e2-layout-2x6", SPECS_12, cols=6, layout="2x6", height_in=4.05)
    for spec, series in zip(SPECS_12, twelve, strict=True):
        render_panel(series, spec["id"])
    write_manifest({"hero": [hero], "2x5": ten, "2x6": twelve})
    metrics = area_comparison()
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()