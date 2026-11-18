#!/usr/bin/env python3
"""Export 178mm figure* PDF/PNG and same-width v2 comparison."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
NATIVE = HERE / "algo1-framework.pdf"
V2 = Path("/tmp/recovery-spec/references/user-originals/fig-F-algo1-v2.pdf")
if not V2.exists():
    V2 = HERE / "../../"  # fallback unused
V2 = Path("/tmp/recovery-spec/references/user-originals/fig-F-algo1-v2.pdf")

# sigconf textwidth after \\maketitle (178mm nominal).
TEXTWIDTH_PT = 506.295
V2_WIDTH_PT = 504.96


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
        [
            "pdftoppm",
            "-png",
            "-r",
            "72",
            "-scale-to-x",
            str(width_px),
            "-scale-to-y",
            "-1",
            str(pdf),
            str(stem),
        ]
    )
    produced = Path(str(stem) + "-1.png")
    image = Image.open(produced).convert("RGB")
    image.save(dest)
    produced.unlink(missing_ok=True)
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
        (HERE / f"_wrap{suffix}").unlink(missing_ok=True)
    tex.unlink(missing_ok=True)


def font(size: int) -> ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def labeled_pair(left: Image.Image, left_cap: str, right: Image.Image, right_cap: str, dest: Path) -> None:
    gap = 24
    cap_h = 34
    canvas = Image.new(
        "RGB",
        (left.width + gap + right.width, cap_h + max(left.height, right.height)),
        "white",
    )
    draw = ImageDraw.Draw(canvas)
    face = font(17)
    canvas.paste(left, (0, cap_h))
    canvas.paste(right, (left.width + gap, cap_h))
    draw.text((8, 7), left_cap, fill=(20, 20, 20), font=face)
    draw.text((left.width + gap + 8, 7), right_cap, fill=(20, 20, 20), font=face)
    canvas.save(dest)


def main() -> None:
    w, h = page_pts(NATIVE)
    if not (500 < w < 512):
        raise SystemExit(f"native width {w}pt is not near 178mm textwidth")
    if h > 360:  # ~127mm
        raise SystemExit(f"native height {h}pt exceeds compact target (~125mm)")

    wrap_pdf(NATIVE, TEXTWIDTH_PT, HERE / "algo1-framework-178mm.pdf")
    native_px = max(1, round(TEXTWIDTH_PT / 72 * 160))
    render(HERE / "algo1-framework-178mm.pdf", native_px, HERE / "algo1-framework.png")
    (HERE / "algo1-framework-178mm.pdf").replace(HERE / "algo1-framework.pdf")

    v2_px = 1200
    new_img = render(HERE / "algo1-framework.pdf", v2_px, HERE / "_new.png")
    v2_img = render(V2, v2_px, HERE / "_v2.png")
    labeled_pair(
        v2_img,
        "v2 baseline (505pt media width)",
        new_img,
        "new framework at the same width (178mm / figure*)",
        HERE / "compare-v2.png",
    )
    for t in HERE.glob("_*.png"):
        t.unlink()

    wmm = TEXTWIDTH_PT / 72 * 25.4
    hmm = page_pts(HERE / "algo1-framework.pdf")[1] / 72 * 25.4
    print(f"exported {wmm:.1f}mm x {hmm:.1f}mm")


if __name__ == "__main__":
    main()