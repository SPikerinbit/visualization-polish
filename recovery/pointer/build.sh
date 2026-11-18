#!/bin/sh
# Rebuild the two pointer-rule figures. Does not touch the paper sources.
set -e
cd "$(dirname "$0")"
python3 geometry.py
mkdir -p pdf png /tmp/pointer-build
pdflatex -interaction=nonstopmode -output-directory /tmp/pointer-build tikz/scheme-a.tex >/tmp/pointer-build/a.log
pdflatex -interaction=nonstopmode -output-directory /tmp/pointer-build tikz/scheme-b.tex >/tmp/pointer-build/b.log
cp /tmp/pointer-build/scheme-a.pdf pdf/pointer-scheme-a.pdf
cp /tmp/pointer-build/scheme-b.pdf pdf/pointer-scheme-b.pdf
python3 render_compare.py
echo "pdf/pointer-scheme-a.pdf pdf/pointer-scheme-b.pdf"
