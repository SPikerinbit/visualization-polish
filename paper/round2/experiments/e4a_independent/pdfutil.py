"""PDF content-stream measurements and Matplotlib font setup."""

from __future__ import annotations

import re
import zlib
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from style import FONT_BOLD, FONT_REGULAR


def configure_matplotlib() -> None:
    font_manager.fontManager.addfont(FONT_REGULAR)
    font_manager.fontManager.addfont(FONT_BOLD)
    plt.rcParams.update(
        {
            "font.family": "Liberation Serif",
            "mathtext.fontset": "stix",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.unicode_minus": False,
            "savefig.pad_inches": 0.0,
            "text.color": "black",
            "axes.labelcolor": "black",
            "xtick.color": "black",
            "ytick.color": "black",
            "axes.edgecolor": "black",
        }
    )


def _streams(data: bytes) -> list[bytes]:
    out = []
    for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        raw = match.group(1)
        try:
            out.append(zlib.decompress(raw))
        except zlib.error:
            out.append(raw)
    return out


def line_widths(path: Path) -> Counter:
    text = b"\n".join(_streams(Path(path).read_bytes()))
    widths = [round(float(w), 3) for w in re.findall(rb"([\d.]+)\s+w\b", text)]
    return Counter(widths)


def media_box(path: Path) -> tuple[float, float]:
    data = Path(path).read_bytes()
    boxes = re.findall(
        rb"/MediaBox\s*\[\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\]",
        data,
    )
    if not boxes:
        raise RuntimeError(f"no MediaBox in {path}")
    x0, y0, x1, y1 = (float(v) for v in boxes[0])
    return x1 - x0, y1 - y0


def assert_has_width(path: Path, expected: float, tol: float = 0.08) -> float:
    counts = line_widths(path)
    if not counts:
        raise RuntimeError(f"no stroke widths in {path}")
    nearest = min(counts, key=lambda w: abs(w - expected))
    if abs(nearest - expected) > tol:
        raise RuntimeError(
            f"{path.name}: expected a stroke near {expected:.3f} pt, "
            f"nearest {nearest} in {counts.most_common(8)}"
        )
    return nearest


def overflow_labels(fig) -> list[str]:
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    width, height = fig.bbox.width, fig.bbox.height
    problems = []
    artists = []
    for ax in fig.axes:
        artists.extend(ax.get_xticklabels())
        artists.extend(ax.get_yticklabels())
        title = ax.title
        if title.get_text().strip():
            artists.append(title)
        label = ax.xaxis.label
        if label.get_text().strip():
            artists.append(label)
        label = ax.yaxis.label
        if label.get_text().strip():
            artists.append(label)
    artists.extend(fig.texts)
    if fig.legends:
        for legend in fig.legends:
            artists.extend(legend.get_texts())
    for artist in artists:
        text = artist.get_text().strip()
        if not text:
            continue
        box = artist.get_window_extent(renderer)
        if box.width <= 0 or box.height <= 0:
            continue
        if box.x0 < -1.5 or box.y0 < -1.5 or box.x1 > width + 1.5 or box.y1 > height + 1.5:
            problems.append(text)
    return problems


def overlapping_tick_labels(fig, pad: float = 0.6) -> list[str]:
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    labels = []
    for ax in fig.axes:
        for tick in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
            text = tick.get_text().strip()
            if not text or not tick.get_visible():
                continue
            labels.append((text, tick.get_window_extent(renderer), id(ax)))
    problems = []
    for i, (left, box_l, ax_l) in enumerate(labels):
        for right, box_r, ax_r in labels[i + 1 :]:
            if ax_l != ax_r:
                continue
            separated = (
                box_l.x1 < box_r.x0 + pad
                or box_r.x1 < box_l.x0 + pad
                or box_l.y1 < box_r.y0 + pad
                or box_r.y1 < box_l.y0 + pad
            )
            if not separated:
                problems.append(f"{left} | {right}")
    return problems
