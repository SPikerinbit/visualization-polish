#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if ! pdflatex --version | sed -n '1p' | grep -Fq '(TeX Live 2026)'; then
  printf '%s\n' 'This manuscript requires pdfLaTeX from TeX Live 2026.' >&2
  exit 1
fi
pdflatex -interaction=nonstopmode -halt-on-error -recorder main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error -recorder main.tex
pdflatex -interaction=nonstopmode -halt-on-error -recorder main.tex
if grep -Eq 'undefined references|undefined citations|There were undefined|Overfull' main.log; then
  printf '%s\n' 'Inspect main.log for unresolved references or layout overflow.' >&2
  exit 1
fi
