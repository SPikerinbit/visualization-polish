#!/bin/sh
set -eu
cd "$(dirname "$0")/tex"
ver=$(pdflatex --version | head -n 1)
printf 'LOCAL INSPECTION BUILD (not release): %s\n' "$ver"
kpsewhich eso-pic.sty >/dev/null || apt-get install -qq -y texlive-pictures >/dev/null 2>&1 || true
export TEXINPUTS=./vendor:${TEXINPUTS:-}
export BSTINPUTS=./vendor:${BSTINPUTS:-}
export BIBINPUTS=./vendor:${BIBINPUTS:-}
pdflatex -interaction=nonstopmode main.tex || true
if grep -q '\\citation{' main.aux 2>/dev/null; then
  bibtex main || true
fi
pdflatex -interaction=nonstopmode main.tex || true
pdflatex -interaction=nonstopmode main.tex || true