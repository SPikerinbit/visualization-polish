#!/bin/sh
# Rebuild the four print figures and a same-scale contact sheet.
set -e
cd "$(dirname "$0")"
mkdir -p build
python3 src/build_svgs.py
pdflatex -interaction=nonstopmode -output-directory=build src/framework.tex >/dev/null
# viewBox unit is 1 bp, so the PDF page is the print size
rsvg-convert -f pdf -d 72 -p 72 src/sd_merge.svg -o build/sw.pdf
rsvg-convert -f pdf -d 72 -p 72 src/lt_unified.svg -o build/lt.pdf
rsvg-convert -f pdf -d 72 -p 72 src/pointer_rule.svg -o build/pointer.pdf
pdftoppm -png -r 160 build/framework.pdf build/framework
pdftoppm -png -r 160 build/sw.pdf build/sw
pdftoppm -png -r 160 build/lt.pdf build/lt
pdftoppm -png -r 160 build/pointer.pdf build/pointer
cp build/framework.pdf framework.pdf
cp build/framework-1.png framework.png
cp build/sw.pdf sw.pdf
cp build/sw-1.png sw.png
cp build/lt.pdf lt.pdf
cp build/lt-1.png lt.png
cp build/pointer.pdf pointer.pdf
cp build/pointer-1.png pointer.png
python3 - << 'PY'
from PIL import Image, ImageDraw
# 6 px per bp: every figure keeps its real page size.
S = 6
pages = [
    ("framework  504.4 x 119.1 bp   178.0 x 42.0 mm", "framework.png"),
    ("SW  240 x 96 bp", "sw.png"),
    ("LT(h)  240 x 124 bp", "lt.png"),
    ("pointer  240 x 150 bp", "pointer.png"),
]
# the committed pngs are 160 dpi = 160/72 px per bp. Rescale from that
# back to S px/bp so the sheet is one physical scale.
src_scale = 160 / 72
blocks = []
for label, name in pages:
    im = Image.open(name).convert("RGB")
    w = int(round(im.width * S / src_scale))
    h = int(round(im.height * S / src_scale))
    im = im.resize((w, h), Image.Resampling.LANCZOS)
    cap = Image.new("RGB", (im.width, im.height + 18), (255, 255, 255))
    ImageDraw.Draw(cap).text((4, 2), label, fill=(30, 30, 30))
    cap.paste(im, (0, 18))
    blocks.append(cap)
bar_w = int(round(20 / 25.4 * 72 * S))  # 20 mm
bar = Image.new("RGB", (max(b.width for b in blocks), 28), (255, 255, 255))
d = ImageDraw.Draw(bar)
d.line((12, 16, 12 + bar_w, 16), fill=(20, 20, 20), width=2)
d.text((16 + bar_w, 8), "20 mm", fill=(20, 20, 20))
d.text((4, 2), "same px/bp; left edges align", fill=(80, 80, 80))
gap = 10
W = max(b.width for b in blocks)
H = sum(b.height for b in blocks) + bar.height + gap * len(blocks)
sheet = Image.new("RGB", (W, H), (245, 245, 245))
y = 0
for b in blocks:
    sheet.paste(b, (0, y))
    y += b.height + gap
sheet.paste(bar, (0, y))
sheet.save("contact.png")
print("contact", sheet.size)
PY
pdfinfo framework.pdf
pdfinfo sw.pdf
pdfinfo lt.pdf
pdfinfo pointer.pdf
