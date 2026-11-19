#!/bin/sh
# Compile checked-in review assets, without regenerating plots or changing data.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
export TEXINPUTS="$PWD/../../tex/vendor:${TEXINPUTS:-}"
pdflatex --version | head -1
pdflatex -interaction=nonstopmode -halt-on-error -recorder main.tex
pdflatex -interaction=nonstopmode -halt-on-error -recorder main.tex
if grep -q 'Overfull' main.log; then echo 'Layout overflow: inspect main.log' >&2; exit 1; fi
TEXT=$(pdftotext -raw main.pdf - | tr '\n' ' ')
printf '%s' "$TEXT" | grep -q 'ALL EXPERIMENTAL VALUES ARE SYNTHETIC'
printf '%s' "$TEXT" | grep -q 'within each dataset segment'
printf '%s' "$TEXT" | grep -q 'not joined to LIMIT'
pdfinfo main.pdf | grep Pages
