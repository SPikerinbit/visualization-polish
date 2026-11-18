#!/bin/sh
# Rebuild the four mechanism figures. Does not touch files outside this directory.
set -e
cd "$(dirname "$0")"
mkdir -p build
pdflatex -interaction=nonstopmode -output-directory=build src/framework.tex >/dev/null
rsvg-convert -f pdf -d 72 -p 72 -w 240 src/sd_merge.svg -o build/sw-column.pdf
rsvg-convert -f pdf -d 72 -p 72 -w 240 src/lt_unified.svg -o build/lt-column.pdf
rsvg-convert -f pdf -d 72 -p 72 -w 249 src/pointer_rule.svg -o build/pointer.pdf
rsvg-convert -f pdf -d 72 -p 72 -w 505 src/sd_merge.svg -o build/sw-v2size.pdf
rsvg-convert -f pdf -d 72 -p 72 -w 505 src/lt_unified.svg -o build/lt-v2size.pdf
pdftoppm -png -r 140 build/framework.pdf build/framework
pdftoppm -png -r 160 build/sw-column.pdf build/sw
pdftoppm -png -r 160 build/lt-column.pdf build/lt
pdftoppm -png -r 140 build/pointer.pdf build/pointer
pdftoppm -png -r 110 build/sw-v2size.pdf build/sw-v2size
pdftoppm -png -r 110 build/lt-v2size.pdf build/lt-v2size
cp build/framework.pdf framework.pdf
cp build/framework-1.png framework.png
cp build/sw-column.pdf sw.pdf
cp build/sw-1.png sw.png
cp build/lt-column.pdf lt.pdf
cp build/lt-1.png lt.png
cp build/pointer.pdf pointer.pdf
cp build/pointer-1.png pointer.png
cp build/sw-v2size.pdf sw-v2size.pdf
cp build/sw-v2size-1.png sw-v2size.png
cp build/lt-v2size.pdf lt-v2size.pdf
cp build/lt-v2size-1.png lt-v2size.png
pdfinfo framework.pdf
pdfinfo sw.pdf
pdfinfo lt.pdf
pdfinfo pointer.pdf
pdfinfo sw-v2size.pdf
pdfinfo lt-v2size.pdf
