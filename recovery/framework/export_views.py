#!/usr/bin/env python3
"""Export print-size PDFs and same-width comparisons. No paper files are edited."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
NATIVE = HERE / "algo1-framework.pdf"
V1 = Path("/tmp/recovery-spec/references/user-originals/fig-F-algo1-v1.pdf")
V2 = Path("/tmp/recovery-spec/references/user-originals/fig-F-algo1-v2.pdf")

# Probed sigconf + pvldb, after \maketitle.
TEXTWIDTH_PT = 506.295
COLUMN_PT = 241.14749
COLUMN_PRINT_PT = 0.95 * COLUMN_PT  # 229.090pt, figure + 0.95\linewidth


def page_pts(pdf: Path) -> tuple[float, float]:
    info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    for line in info.splitlines():
        if line.startswith("Page size:"):
            parts = line.split()
            return float(parts[2]), float(parts[4])
    raise RuntimeError(f"no page size in {pdf}")


def render(pdf: Path, width_px: int, dest: Path) -> Image.Image:
    dest.parent.mkdir(parents=True, exist_ok=True)
    stem = dest.with_suffix("")
    subprocess.check_call(
        ["pdftoppm", "-png", "-r", "72", "-scale-to-x", str(width_px), "-scale-to-y", "-1", str(pdf), str(stem)]
    )
    # pdftoppm appends -1 when the pattern has no printf field.
    produced = Path(str(stem) + "-1.png")
    if not produced.exists():
        produced = dest
    image = Image.open(produced).convert("RGB")
    if produced != dest:
        image.save(dest)
        produced.unlink()
    return image


def wrap_pdf(src: Path, width_pt: float, dest: Path) -> None:
    native_w, native_h = page_pts(src)
    height_pt = native_h * (width_pt / native_w)
    tex = HERE / "_wrap.tex"
    tex.write_text(
        "\\documentclass{article}\n"
        f"\\usepackage[paperwidth={width_pt:.3f}pt,paperheight={height_pt:.3f}pt,margin=0pt]{{geometry}}\n"
        "\\usepackage{graphicx}\n"
        "\\pagestyle{empty}\n"
        "\\begin{document}\n"
        "\\noindent\\includegraphics"
        f"[width={width_pt:.3f}pt]{{{src.name}}}\n"
        "\\end{document}\n"
    )
    subprocess.check_call(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
        cwd=HERE,
        stdout=subprocess.DEVNULL,
    )
    (HERE / "_wrap.pdf").replace(dest)
    for suffix in (".aux", ".log", ".out"):
        junk = HERE / f"_wrap{suffix}"
        if junk.exists():
            junk.unlink()
    tex.unlink()


def font(size: int) -> ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def labeled_pair(left: Image.Image, left_caption: str, right: Image.Image, right_caption: str, dest: Path) -> None:
    gap = 28
    cap_h = 36
    width = left.width + gap + right.width
    height = cap_h + max(left.height, right.height)
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    face = font(18)
    canvas.paste(left, (0, cap_h))
    canvas.paste(right, (left.width + gap, cap_h))
    draw.text((8, 8), left_caption, fill=(20, 20, 20), font=face)
    draw.text((left.width + gap + 8, 8), right_caption, fill=(20, 20, 20), font=face)
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest)


def main() -> None:
    wrap_pdf(NATIVE, COLUMN_PRINT_PT, HERE / "algo1-framework-column.pdf")
    wrap_pdf(NATIVE, TEXTWIDTH_PT, HERE / "algo1-framework-textwidth.pdf")

    native_w, _ = page_pts(NATIVE)
    # Native PNG at about 160 dpi.
    native_px = max(1, round(native_w / 72 * 160))
    render(NATIVE, native_px, HERE / "algo1-framework.png")

    # Same-width pairs. v1 is 482pt; v2 is 504.96pt.
    v1_px = 1200
    new_at_v1 = render(NATIVE, v1_px, HERE / "_new-v1w.png")
    v1 = render(V1, v1_px, HERE / "_v1.png")
    labeled_pair(
        v1,
        "v1, its own media width (482pt)",
        new_at_v1,
        "new framework, scaled to the same 482pt width",
        HERE / "compare-v1.png",
    )

    v2_px = 1200
    new_at_v2 = render(NATIVE, v2_px, HERE / "_new-v2w.png")
    v2 = render(V2, v2_px, HERE / "_v2.png")
    labeled_pair(
        v2,
        "v2, its own media width (505pt)",
        new_at_v2,
        "new framework, scaled to the same 505pt width",
        HERE / "compare-v2.png",
    )

    # Two real template sizes. Template files are not edited.
    col_px = round(COLUMN_PRINT_PT / 72 * 160)
    star_px = round(TEXTWIDTH_PT / 72 * 160)
    col = render(HERE / "algo1-framework-column.pdf", col_px, HERE / "_col.png")
    star = render(HERE / "algo1-framework-textwidth.pdf", star_px, HERE / "_star.png")
    labeled_pair(
        col,
        "real single-column print: 0.95\\linewidth = 229.09pt",
        star,
        "real textwidth print: figure* \\linewidth = 506.30pt",
        HERE / "compare-sizes.png",
    )

    for temporary in HERE.glob("_*.png"):
        temporary.unlink()


if __name__ == "__main__":
    main()
