"""Round-2 E2: predicted vs measured cost surfaces (cost-only, no quality inset).

Rendering follows ``refs/.../plot_surface.py`` face/edge alphas and camera;
panel PDFs match ``fig:exp5-m`` cell size (1.85 in). Group layout is TeX
``figure*`` with per-panel ``\\includegraphics``, not a single montage PDF.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
PANELS = OUT / "panels"
EVIDENCE = ROOT / "evidence"
REFS = ROOT / "refs"
REFERENCE = REFS / "fig-E2-cost-surface-reference.png"
EXP5_PANELS = Path("/agent/repos/visualization-polish/paper/tex/fig/panels/exp5")

PAGE_WIDTH_IN = 7.0
# sigconf: one exp5-m cell is 0.33\\columnwidth (~1.10 in on paper); source PDFs are 1.85 in.
PANEL_IN = 1.85

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

# plot_surface.py poster mesh style (scaled down for panel edge linewidths).
POSTER = dict(face_b=0.55, face_o=0.22, edge_b=0.55, edge_o=0.80, edge_ca=0.64, edge_co=0.86, loose=0.9)


def max_segment(g: int, m: int) -> int:
    return m // (1 + (g - 1).bit_length()) if g > 1 else m


def legal_domain(family: str) -> list[tuple[int, int]]:
    if family == "LT":
        upper = min(RUNS, 2 ** (M - 1))
        return [(k, h) for k in range(2, upper + 1) for h in range(1, max_segment(k, M) + 1)]
    if family == "SW":
        upper = min(RUNS, M)
        return [(k, h) for k in range(2, upper + 1) for h in range(1, (M // k) + 1)]
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
        raise RuntimeError(f"no triangles for {spec['id']}")
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
            **POSTER,
            pt_s=12.0, pt_lw_b=0.25, pt_lw_o=0.65, pt_a=0.85,
            star=175, diamond=85, mark_lw=0.9,
            tick=11.0, label=14.0, zoom=1.04, grid_lw=0.6,
        )
    # Panel: keep every (k,h) marker but below face dominance (original s=12 @ 13.6 in).
    base = {k: v for k, v in POSTER.items() if k not in ("loose", "edge_b", "edge_o")}
    return dict(
        **base,
        # Printed cell is 79.282pt (scale 0.59521). Source 9.0pt → ~5.36pt on the page.
        pt_s=1.7, pt_lw_b=0.08, pt_lw_o=0.18, pt_a=0.7,
        star=26, diamond=12, mark_lw=0.3, loose=0.28,
        tick=9.0, label=8.0, zoom=0.92, grid_lw=0.4,
        edge_b=0.32, edge_o=0.40,
    )


def _paint_panes(ax, grid_lw: float) -> None:
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.fill = False
        axis.pane.set_edgecolor("#E8EDF0")
        axis._axinfo["grid"]["color"] = "#DFE6EA"
        axis._axinfo["grid"]["linewidth"] = grid_lw
        axis.line.set_color("#A8B4BC")


def _axis_caption(index: int, cols: int, rows: int) -> dict[str, bool]:
    row, col = index // cols, index % cols
    return {
        "x_ticks": row == rows - 1,
        "x_label": row == rows - 1 and col == cols // 2,
        "y_ticks": True,
        "y_label": row == rows - 1 and col == 0,
        "z_ticks": col == 0,
        "z_label": col == 0 and row == rows // 2,
    }


def draw_series(
    ax,
    series: Series,
    layout: str,
    frame: dict,
    captions: dict[str, bool],
) -> None:
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
            ec = size["edge_ca"] if color == BLUE else size["edge_co"]
            edges.append(to_rgba(color, ec))
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
        linewidths=size["pt_lw_b"], alpha=size["pt_a"], depthshade=False, zorder=5,
    )
    ax.scatter(
        x, y, predicted, s=size["pt_s"], facecolors="none", edgecolors=ORANGE,
        linewidths=size["pt_lw_o"], alpha=size["pt_a"], depthshade=False, zorder=6,
    )

    best, selected = series.best, series.selected
    if series.coincide:
        ax.scatter(
            [best.k], [best.h], [best.u], s=size["diamond"] * 1.2, marker="D",
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

    ax.set_xlim(*frame["xlim"])
    ax.set_ylim(*frame["ylim"])
    ax.set_zlim(*frame["zlim"])
    ax.set_xticks(list(frame["xticks"]) if captions.get("x_ticks", True) else [])
    ax.set_yticks(list(frame["yticks"]) if captions.get("y_ticks", True) else [])
    ax.set_zticks(list(frame["zticks"]) if captions.get("z_ticks", True) else [])
    ax.view_init(**CAMERA)
    ax.set_proj_type("ortho")
    ax.set_box_aspect(BOX, zoom=size["zoom"])
    _paint_panes(ax, size["grid_lw"])

    pad = 3 if layout == "panel" else 12
    ax.tick_params(axis="x", labelsize=size["tick"], pad=0, colors=TICK)
    ax.tick_params(axis="y", labelsize=size["tick"], pad=0, colors=TICK)
    ax.tick_params(axis="z", labelsize=size["tick"], pad=1, colors=TICK)

    ax.set_xlabel("Fan-in $k$" if captions.get("x_label") else "", labelpad=pad, color=INK, fontsize=size["label"])
    ax.set_ylabel("Segment length $h$" if captions.get("y_label") else "", labelpad=pad, color=INK, fontsize=size["label"])
    z_text = "1k" if layout == "panel" else "Merge input tokens (1k)"
    ax.set_zlabel(z_text if captions.get("z_label") else "", labelpad=pad + 2, color=INK, fontsize=size["label"])


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


def render_legend() -> None:
    """Fixed 5.60 in width so 0.8\\linewidth inclusion does not upscale the type."""
    _apply_font()
    fig = plt.figure(figsize=(5.60, 0.28), facecolor="white")
    handles = [
        Line2D([0], [0], color=BLUE, linewidth=3.2, alpha=0.7, marker="o", markersize=3.2, label="Measured"),
        Line2D(
            [0], [0], color=ORANGE, linewidth=1.6, alpha=0.9, marker="o",
            markerfacecolor="white", markersize=3.2, label="Predicted",
        ),
        Line2D(
            [0], [0], marker="*", color="none", markerfacecolor=BLUE, markeredgecolor="white",
            markeredgewidth=0.3, markersize=6.5, linestyle="None", label="Meas. min",
        ),
        Line2D(
            [0], [0], marker="D", color="none", markerfacecolor=ORANGE, markeredgecolor="white",
            markeredgewidth=0.3, markersize=4.2, linestyle="None", label="Pred. min",
        ),
    ]
    fig.legend(
        handles=handles,
        loc="center",
        ncol=4,
        frameon=False,
        fontsize=6.8,
        handlelength=1.35,
        columnspacing=1.15,
        labelcolor=INK,
        borderaxespad=0.0,
    )
    OUT.mkdir(parents=True, exist_ok=True)
    # Do not use bbox_inches='tight': that shrinks the PDF and TeX then enlarges the type.
    fig.savefig(OUT / "e2-legend.pdf")
    fig.savefig(OUT / "e2-legend.png", dpi=200)
    plt.close(fig)


def render_panel(series: Series, stem: str, index: int, grid: tuple[int, int]) -> None:
    _apply_font()
    PANELS.mkdir(parents=True, exist_ok=True)
    frame = _frames([series])[0]
    # Each vector panel is self-contained for TeX inclusion (readable z ticks + cost axis).
    caps = {
        "x_ticks": True,
        "x_label": False,
        "y_ticks": True,
        "y_label": False,
        "z_ticks": True,
        "z_label": False,
    }
    # Fixed MediaBox. Inset the axes so z numerals and h=10 stay inside 133.2pt.
    fig = plt.figure(figsize=(PANEL_IN, PANEL_IN), facecolor="white")
    ax = fig.add_axes([0.07, 0.12, 0.70, 0.80], projection="3d", computed_zorder=False)
    draw_series(ax, series, "panel", frame, caps)
    for ext in ("pdf", "png"):
        fig.savefig(PANELS / f"{stem}.{ext}", dpi=220 if ext == "png" else None)
    plt.close(fig)


def render_hero(spec: dict) -> Series:
    _apply_font()
    series = build_series(spec)
    frame = _frames([series])[0]
    fig = plt.figure(figsize=(7.0, 4.1), facecolor="white")
    ax = fig.add_axes([-0.02, 0.1, 0.78, 0.82], projection="3d", computed_zorder=False)
    draw_series(
        ax, series, "hero", frame,
        {"x_ticks": True, "x_label": True, "y_ticks": True, "y_label": True, "z_ticks": True, "z_label": True},
    )
    handles = [
        Line2D([0], [0], color=BLUE, linewidth=6, alpha=0.65, marker="o", markersize=5, label="Measured vLLM cost"),
        Line2D(
            [0], [0], color=ORANGE, linewidth=3, alpha=0.85, marker="o",
            markerfacecolor="white", markersize=5, label="Cost model prediction",
        ),
    ]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.02, 0.93), frameon=False, ncol=2, fontsize=10)
    fig.text(0.02, 0.97, "Cost only (Spearman inset removed). Synthetic heights.", fontsize=8.5, color=GRAY)
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"e2-hero-cost-only.{ext}", dpi=220 if ext == "png" else None)
    plt.close(fig)
    return series


def _page_size_in(pdf: Path) -> tuple[float, float]:
    from pypdf import PdfReader

    box = PdfReader(str(pdf)).pages[0].mediabox
    return float(box.width) / 72, float(box.height) / 72


def _pdflatex(tex_dir: Path, name: str) -> None:
    env = {**os.environ, "TEXINPUTS": f"../../../tex/vendor:"}
    for _ in range(2):
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", name],
            cwd=tex_dir, env=env, check=False, capture_output=True,
        )


def compile_tex_preview() -> None:
    """Compile, then keep only the 12-cell page and the 10-cell page."""
    from pypdf import PdfReader, PdfWriter

    tex_dir = ROOT / "tex"
    _pdflatex(tex_dir, "exp5-baseline-same-env.tex")
    _pdflatex(tex_dir, "preview-main.tex")
    src = tex_dir / "preview-main.pdf"
    if not src.exists():
        raise RuntimeError("preview-main.pdf was not produced")
    reader = PdfReader(str(src))
    page_12 = page_10 = None
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if "(l)" in text and "Syn-L, SW" in text:
            page_12 = i
        elif "Ten-cell derivative" in text:
            page_10 = i
    if page_12 is None or page_10 is None or page_12 == page_10:
        raise RuntimeError(f"expected separate 12 and 10 pages, got 12={page_12} 10={page_10} n={len(reader.pages)}")
    writer = PdfWriter()
    writer.add_page(reader.pages[page_12])
    writer.add_page(reader.pages[page_10])
    dest = OUT / "e2-vldb-preview.pdf"
    with dest.open("wb") as handle:
        writer.write(handle)
    only12 = PdfWriter()
    only12.add_page(reader.pages[page_12])
    with (OUT / "e2-figure-12.pdf").open("wb") as handle:
        only12.write(handle)
    # Raster of those exact pages. Names match the PDFs, not an older montage.
    subprocess.run(["pdftoppm", "-png", "-r", "160", "-f", "1", "-l", "1", str(dest), "/tmp/e2-12"], check=True)
    subprocess.run(["pdftoppm", "-png", "-r", "160", "-f", "2", "-l", "2", str(dest), "/tmp/e2-10"], check=True)
    Image.open("/tmp/e2-12-1.png").save(OUT / "e2-layout-2x6.png")
    Image.open("/tmp/e2-12-1.png").save(OUT / "e2-figure-12.png")
    Image.open("/tmp/e2-10-2.png").save(OUT / "e2-layout-2x5.png")


def pdf_to_png(pdf: Path, png: Path, dpi: int = 200) -> None:
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi), "-singlefile", str(pdf), str(png.with_suffix(""))],
        check=False,
    )


def _content_bbox(page) -> tuple[float, float, float, float]:
    """Union of text and images on a page, in PDF points (origin bottom-left)."""
    rects = []
    for block in page.get_text("dict")["blocks"]:
        rects.append((block["bbox"][0], block["bbox"][1], block["bbox"][2], block["bbox"][3]))
    for info in page.get_image_info():
        box = info["bbox"]
        rects.append((box[0], box[1], box[2], box[3]))
    if not rects:
        raise RuntimeError("empty page")
    return (
        min(r[0] for r in rects),
        min(r[1] for r in rects),
        max(r[2] for r in rects),
        max(r[3] for r in rects),
    )


def _figure_page(pdf: Path, marker: str):
    import fitz

    doc = fitz.open(pdf)
    for page in doc:
        if marker in (page.get_text() or ""):
            return doc, page
    raise RuntimeError(f"{marker} not in {pdf}")


def area_evidence() -> dict:
    import fitz

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    baseline = ROOT / "tex" / "exp5-baseline-same-env.pdf"
    preview = OUT / "e2-vldb-preview.pdf"
    _bdoc, bpage = _figure_page(baseline, "Batch size")
    _edoc, epage = _figure_page(preview, "Syn-L")
    bb = _content_bbox(bpage)
    eb = _content_bbox(epage)
    dpi = 160
    bpix = bpage.get_pixmap(dpi=dpi, clip=fitz.Rect(*bb))
    epix = epage.get_pixmap(dpi=dpi, clip=fitz.Rect(*eb))
    bimg = Image.frombytes("RGB", (bpix.width, bpix.height), bpix.samples)
    eimg = Image.frombytes("RGB", (epix.width, epix.height), epix.samples)
    # Same dpi and same page scale. Do not resample one crop onto the other.
    width = max(bimg.width, eimg.width)
    gap = 28
    canvas = Image.new("RGB", (width, bimg.height + eimg.height + gap), "white")
    canvas.paste(bimg, (0, 0))
    canvas.paste(eimg, (0, bimg.height + gap))
    canvas.save(EVIDENCE / "area-exp5m-vs-e2-same-width.png")
    # Show only the figure on the delivered preview pages (CropBox). MediaBox stays letter.
    pad = 2.0
    src = fitz.open(preview)
    boxes = []
    already = src[0].cropbox.height < 400
    for page, marker in ((src[0], "Syn-L"), (src[1], "Ten-cell")):
        if already:
            continue
        box = _content_bbox(page)
        boxes.append(box)
        page.set_cropbox(fitz.Rect(box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad))
    tmp_pdf = preview.with_suffix(".crop.pdf")
    src.save(tmp_pdf, encryption=fitz.PDF_ENCRYPT_KEEP)
    src.close()
    tmp_pdf.replace(preview)
    shown = fitz.open(preview)
    for index, name in ((0, "e2-layout-2x6.png"), (1, "e2-layout-2x5.png")):
        pix = shown[index].get_pixmap(dpi=160, alpha=False)
        png = OUT / name
        pix.save(png)
        if index == 0:
            pix.save(OUT / "e2-figure-12.png")
    shown.close()
    only = fitz.open(preview)
    only.select([0])
    only.save(OUT / "e2-figure-12.pdf")
    only.close()
    metrics = {
        "note": "Same sigconf environment. Crops are figure content bboxes, not the paper MediaBox. exp5-m is the 2D batch-size figure, not a 3D k-sweep float.",
        "baseline_figure_bbox_pt": [round(v, 2) for v in bb],
        "e2_12_figure_bbox_pt": [round(v, 2) for v in eb],
        "baseline_figure_wh_pt": [round(bb[2] - bb[0], 2), round(bb[3] - bb[1], 2)],
        "e2_12_figure_wh_pt": [round(eb[2] - eb[0], 2), round(eb[3] - eb[1], 2)],
        "height_ratio_e2_over_baseline": round((eb[3] - eb[1]) / (bb[3] - bb[1]), 4),
    }
    (EVIDENCE / "area-metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


PANEL_META_12 = [
    ("a", "p01", "LT", "Full", "Syn-A"),
    ("b", "p02", "LT", "Full", "Syn-B"),
    ("c", "p03", "LT", "Full", "Syn-C"),
    ("d", "p04", "LT", "LIMIT10", "Syn-D"),
    ("e", "p05", "LT", "LIMIT10", "Syn-E"),
    ("f", "p06", "LT", "LIMIT10", "Syn-F"),
    ("g", "p07", "SW", "Full", "Syn-G"),
    ("h", "p08", "SW", "Full", "Syn-H"),
    ("i", "p09", "SW", "Full", "Syn-I"),
    ("j", "p10", "SW", "LIMIT10", "Syn-J"),
    ("k", "p11", "SW", "LIMIT10", "Syn-K"),
    ("l", "p12", "SW", "LIMIT10", "Syn-L"),
]

# 10-panel derivative: drop Syn-F and Syn-L (LIMIT10 tail slots), relabel a–j.
PANEL_META_10 = [
    (chr(ord("a") + i), pid, fam, dem, case)
    for i, (_l, pid, fam, dem, case) in enumerate(
        [row for row in PANEL_META_12 if row[0] not in ("f", "l")]
    )
]

KINDS = {
    "p01": ("shift", 14, 2.5, 0.3, True),
    "p02": ("warp", 16, 2.0, 1.3, False),
    "p03": ("bias", 7, 4.0, 0.8, False),
    "p04": ("cross", 12, 3.0, 0.4, False),
    "p05": ("shift", 6, 2.0, 1.8, False),
    "p06": ("warp", 18, 3.5, 2.2, True),
    "p07": ("shift", 5, 2.0, 0.2, True),
    "p08": ("warp", 11, 3.0, 1.1, False),
    "p09": ("bias", 8, 2.5, 0.65, False),
    "p10": ("cross", 9, 2.0, 1.5, False),
    "p11": ("shift", 13, 1.5, 0.95, False),
    "p12": ("warp", 17, 1.0, 2.0, False),
}


def _spec_from_meta(letter: str, pid: str, family: str, demand: str, case: str) -> dict:
    kind, vk, vh, ph, gap = KINDS[pid]
    return dict(
        id=pid, letter=letter, family=family, demand=demand, case=case,
        kind=kind, valley_k=vk, valley_h=vh, phase=ph, gap=gap,
    )


SPECS_12 = [_spec_from_meta(*row) for row in PANEL_META_12]
SPECS_10 = [_spec_from_meta(*row) for row in PANEL_META_10]


def write_manifest(all_series: list[Series]) -> None:
    payload = {
        "warning": "NOT EXPERIMENTAL RESULTS — schematic heights for layout only.",
        "camera": CAMERA,
        "panel_pdf_in": PANEL_IN,
        "tex_container": "fig-e2-exp5-container-12.tex (per-panel includegraphics)",
        "panels": [
            {
                "id": s.spec["id"],
                "letter": s.spec["letter"],
                "case": s.spec["case"],
                "n_points": len(s.rows),
                "z_ticks": list(_frames([s])[0]["zticks"]),
            }
            for s in all_series
        ],
    }
    (OUT / "synthetic_manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def inspect_panels() -> list[str]:
    """Every text glyph in each panel PDF must sit inside that PDF's MediaBox."""
    import xml.etree.ElementTree as ET
    from pypdf import PdfReader

    issues: list[str] = []
    for spec in SPECS_12:
        pdf = PANELS / f"{spec['id']}.pdf"
        box = PdfReader(str(pdf)).pages[0].mediabox
        width, height = float(box.width), float(box.height)
        if abs(width - 133.2) > 0.6 or abs(height - 133.2) > 0.6:
            issues.append(f"{spec['id']}: MediaBox {width:.2f}x{height:.2f}, expected 133.2")
        xml = subprocess.check_output(["pdftotext", "-bbox", str(pdf), "-"], text=True)
        root = ET.fromstring(xml)
        words = list(root.iter("{http://www.w3.org/1999/xhtml}word"))
        texts = [w.text or "" for w in words]
        if not any(t.isdigit() and int(t) >= 100 for t in texts):
            issues.append(f"{spec['id']}: no cost numeral inside the page text")
        for word in words:
            x0, y0 = float(word.get("xMin")), float(word.get("yMin"))
            x1, y1 = float(word.get("xMax")), float(word.get("yMax"))
            if x0 < -0.4 or y0 < -0.4 or x1 > width + 0.4 or y1 > height + 0.4:
                issues.append(f"{spec['id']}: '{word.text}' bbox ({x0:.1f},{y0:.1f})-({x1:.1f},{y1:.1f}) outside {width:.1f}x{height:.1f}")
    (EVIDENCE / "panel-inspection.txt").write_text("\n".join(issues) or "all panel glyphs inside MediaBox", encoding="utf-8")
    return issues


def _drop_stale() -> None:
    stale = [
        OUT / "e2-layout-2x5.pdf",
        OUT / "e2-layout-2x6.pdf",
        OUT / "e2-layout-2x6-tex.png",
        ROOT / "tex" / "exp5-m-area-block.pdf",
        EVIDENCE / "area-compare-10-vs-12.png",
        EVIDENCE / "area-compare-10-vs-12.pdf",
        EVIDENCE / "area-vs-reference-and-exp5.png",
        EVIDENCE / "small-multiple-spotcheck.png",
    ]
    for path in stale:
        path.unlink(missing_ok=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    _drop_stale()
    render_legend()
    twelve: list[Series] = []
    for index, spec in enumerate(SPECS_12):
        series = build_series(spec)
        twelve.append(series)
        render_panel(series, spec["id"], index, (6, 2))
    write_manifest(twelve)
    issues = inspect_panels()
    if issues:
        raise SystemExit("panel clip check failed:\n" + "\n".join(issues))
    compile_tex_preview()
    metrics = area_evidence()
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()