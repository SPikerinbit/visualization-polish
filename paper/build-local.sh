#!/bin/sh
set -eu
cd "$(dirname "$0")/tex"
ver=$(pdflatex --version | head -n 1)
printf 'LOCAL INSPECTION BUILD (not release): %s\n' "$ver"
export TEXINPUTS=./vendor:${TEXINPUTS:-}
export BSTINPUTS=./vendor:${BSTINPUTS:-}
export BIBINPUTS=./vendor:${BIBINPUTS:-}
rm -f main.aux main.out main.toc main.bbl main.blg
pdflatex -interaction=nonstopmode main.tex || true
if grep -q '\\citation{' main.aux 2>/dev/null; then bibtex main || true; fi
pdflatex -interaction=nonstopmode main.tex || true
pdflatex -interaction=nonstopmode main.tex || true
python3 "$PWD/../scripts/label_page_map.py" 2>/dev/null || true