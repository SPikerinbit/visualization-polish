#!/bin/sh
# Build the manuscript from the checked-in figures and tables.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
export TEXINPUTS="./vendor:${TEXINPUTS:-}"
export BSTINPUTS="./vendor:${BSTINPUTS:-}"
pdflatex -interaction=nonstopmode -halt-on-error -recorder main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error -recorder main.tex
pdflatex -interaction=nonstopmode -halt-on-error -recorder main.tex
if grep -Eq 'undefined references|undefined citations|There were undefined|Overfull' main.log; then
  printf '%s\n' 'Inspect main.log for unresolved references or layout overflow.' >&2
  exit 1
fi
