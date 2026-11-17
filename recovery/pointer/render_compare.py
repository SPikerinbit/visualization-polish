#!/usr/bin/env python3
"""Rasterize the manuscript pointer figure and the two schemes at one scale."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
ORIG = REPO / "算法机制图" / "第二版" / "revision_v3" / "pointer_rule.pdf"
DPI = 150  # same pixels per inch, so equal pt width is equal px width


def raster(pdf: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    prefix = dest.with_suffix("")
    subprocess.check_call(
        ["pdftoppm", "-png", "-r", str(DPI), "-f", "1", "-l", "1", str(pdf), str(prefix)],
        stdout=subprocess.DEVNULL,
    )
    made = prefix.parent / (prefix.name + "-1.png")
    made.replace(dest)
    return dest


def header(text: str, width: int) -> Image.Image:
    bar = Image.new("RGB", (width, 36), (255, 255, 255))
    draw = ImageDraw.Draw(bar)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    draw.text((8, 8), text, fill=(38, 43, 48), font=font)
    return bar


def side_by_side(left: Image.Image, right: Image.Image, left_name: str, right_name: str) -> Image.Image:
    # Scale is already equal. Do not resample either figure.
    lw, lh = left.size
    rw, rh = right.size
    if abs(lw - rw) > 2:
        raise SystemExit(f"widths differ: {left_name} {lw}px vs {right_name} {rw}px")
    width = max(lw, rw)
    left_bar = header(left_name, width)
    right_bar = header(right_name, width)
    canvas = Image.new("RGB", (width * 2 + 16, max(lh, rh) + 36), (255, 255, 255))
    canvas.paste(left_bar, (0, 0))
    canvas.paste(right_bar, (width + 16, 0))
    canvas.paste(left, (0, 36))
    canvas.paste(right, (width + 16, 36))
    return canvas


def main() -> None:
    png = ROOT / "png"
    orig = raster(ORIG, png / "original-v2.png")
    scheme_a = raster(ROOT / "pdf" / "pointer-scheme-a.pdf", png / "scheme-a.png")
    scheme_b = raster(ROOT / "pdf" / "pointer-scheme-b.pdf", png / "scheme-b.png")
    a = Image.open(orig).convert("RGB")
    b = Image.open(scheme_a).convert("RGB")
    c = Image.open(scheme_b).convert("RGB")
    side_by_side(
        a,
        b,
        "original v2  249.12 x 177.12 pt",
        "scheme A before/after  same width",
    ).save(png / "compare-scheme-a.png")
    side_by_side(
        a,
        c,
        "original v2  249.12 x 177.12 pt",
        "scheme B three steps  same width",
    ).save(png / "compare-scheme-b.png")
    print(a.size, b.size, c.size)


if __name__ == "__main__":
    main()
