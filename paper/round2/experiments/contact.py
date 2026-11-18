"""Print-size contact sheets and a same-size comparison with original panels.

Canvases are sized in points and rasterized at 300 dpi, so the PNG is the
physical size. A second sheet at 3x is only for inspection and is labeled.
"""

from __future__ import annotations

from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

from style import COLUMN_PT, FONT_REGULAR, TEXT_PT, printed

ROOT = Path(__file__).resolve().parent
ORIG = ROOT.parents[1] / "tex" / "fig" / "panels"
DPI = 300


def _px(pt: float) -> int:
    return max(1, round(pt * DPI / 72.0))


def _render(path: Path, width_pt: float) -> Image.Image:
    doc = pymupdf.open(path)
    page = doc[0]
    zoom = width_pt / page.rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom * DPI / 72.0, zoom * DPI / 72.0), alpha=False)
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return image


def _font(size: int) -> ImageFont.ImageFont:
    return ImageFont.truetype(FONT_REGULAR, size)


def _canvas(width_pt: float, height_pt: float) -> Image.Image:
    return Image.new("RGB", (_px(width_pt), _px(height_pt)), "white")


def _label(draw: ImageDraw.ImageDraw, xy, text: str, size: int = 18) -> None:
    draw.text(xy, text, fill=(20, 20, 20), font=_font(size))


def e3_column(fig_dir: Path, out: Path) -> None:
    """Placement mock of tex/fig-e3.tex at one column width."""
    panel = printed(133.2, 0.25)
    legend_h = 16.5
    caption_h = 11.0
    gap = 2.0
    row_gap = 8.0
    height = 8 + legend_h + 4 + 2 * (panel + caption_h) + row_gap + 6
    image = _canvas(COLUMN_PT, height)
    draw = ImageDraw.Draw(image)
    legend = _render(fig_dir / "e3-legend.pdf", COLUMN_PT)
    image.paste(legend, (0, _px(4)))
    names = (
        ("e3-sw-full-predicted.pdf", "SW Full, pred."),
        ("e3-sw-limit10-predicted.pdf", "SW LIMIT, pred."),
        ("e3-lt-full-predicted.pdf", "LT Full, pred."),
        ("e3-lt-limit10-predicted.pdf", "LT LIMIT, pred."),
        ("e3-sw-full-measured.pdf", "SW Full, meas."),
        ("e3-sw-limit10-measured.pdf", "SW LIMIT, meas."),
        ("e3-lt-full-measured.pdf", "LT Full, meas."),
        ("e3-lt-limit10-measured.pdf", "LT LIMIT, meas."),
    )
    y = 4 + legend_h + 2
    for row in range(2):
        for col in range(4):
            name, caption = names[row * 4 + col]
            panel_img = _render(fig_dir / name, panel)
            x = col * panel
            image.paste(panel_img, (_px(x), _px(y)))
            draw.text((_px(x + 1), _px(y + panel + 1.2)), caption, fill=(0, 0, 0), font=_font(14))
        y += panel + caption_h + (row_gap if row == 0 else 0)
    image.save(out / "e3-column-1x.png", dpi=(DPI, DPI))
    big = image.resize((image.width * 3, image.height * 3), Image.Resampling.NEAREST)
    badge = ImageDraw.Draw(big)
    badge.rectangle((0, 0, 520, 36), fill=(255, 248, 230))
    badge.text((8, 6), "3x print size, for inspection. Acceptance size is e3-column-1x.png.", fill=(80, 40, 0), font=_font(22))
    big.save(out / "e3-column-3x.png", dpi=(DPI, DPI))


def e3_vs_original(fig_dir: Path, out: Path) -> None:
    panel = printed(133.2, 0.25)
    original = ORIG / "exp4" / "exp4_topk_movies_m20_tokens.pdf"
    ours = fig_dir / "e3-sw-full-measured.pdf"
    left = _render(original, panel)
    right = _render(ours, panel)
    gap = _px(14)
    label_h = _px(28)
    canvas = Image.new("RGB", (left.width + right.width + gap + _px(8), max(left.height, right.height) + label_h + _px(8)), "white")
    canvas.paste(left, (_px(2), label_h))
    canvas.paste(right, (_px(2) + left.width + gap, label_h))
    draw = ImageDraw.Draw(canvas)
    draw.text((2, 2), "Fig. 8 panel at 0.25 column", fill="black", font=_font(13))
    draw.text((_px(2) + left.width + gap, 2), "E3 panel, same box", fill="black", font=_font(13))
    canvas.save(out / "e3-vs-fig8-1x.png", dpi=(DPI, DPI))
    big = canvas.resize((canvas.width * 4, canvas.height * 4), Image.Resampling.NEAREST)
    ImageDraw.Draw(big).text((4, canvas.height * 4 - 28), "4x nearest-neighbor. Same physical box as Fig. 8.", fill=(60, 30, 0), font=_font(18))
    big.save(out / "e3-vs-fig8-4x.png", dpi=(DPI, DPI))


def paste_native(pdf: Path, out: Path, name: str) -> None:
    doc = pymupdf.open(pdf)
    page = doc[0]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(DPI / 72.0, DPI / 72.0), alpha=False)
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    image.save(out / name, dpi=(DPI, DPI))


def build(root: Path) -> None:
    out = root / "contact"
    out.mkdir(parents=True, exist_ok=True)
    e3_column(root / "figures" / "e3", out)
    e3_vs_original(root / "figures" / "e3", out)
    for name in (
        "e4a-dl20-n100.pdf",
        "e4a-dl20-n500.pdf",
        "e4a-covid-n100.pdf",
        "e4a-covid-n500.pdf",
    ):
        paste_native(root / "figures" / "e4a" / name, out, name.replace(".pdf", "-1x.png"))
    paste_native(root / "figures" / "e4b" / "e4b-beta.pdf", out, "e4b-beta-1x.png")
    paste_native(root / "figures" / "e4c" / "e4c-quality-cost.pdf", out, "e4c-quality-cost-1x.png")
    paste_native(root / "figures" / "e5" / "e5-limit-sweep.pdf", out, "e5-limit-sweep-1x.png")
    # Original exp4 token panel at its 0.33-column print size, beside a
    # note of the stroke we matched. The E4a figure is a full column, so
    # the fair stroke comparison is this printed original, not a stretch.
    original = _render(ORIG / "exp4" / "exp4_lt_movies_m8_tokens.pdf", printed(133.2, 0.33))
    pad = _px(8)
    canvas = Image.new("RGB", (original.width + pad, original.height + _px(36)), "white")
    canvas.paste(original, (pad // 2, _px(28)))
    ImageDraw.Draw(canvas).text(
        (4, 4),
        "Original exp4 panel at 0.33 column (stroke reference)",
        fill="black",
        font=_font(12),
    )
    canvas.save(out / "original-exp4-033col-1x.png", dpi=(DPI, DPI))
