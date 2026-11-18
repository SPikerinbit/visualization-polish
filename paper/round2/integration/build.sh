#!/bin/sh
# Rebuild the round-2 shell from admitted sources. Does not redraw E2 panels.
# Exit 0 only means this shell compiled. It is not parent acceptance of the paper.
set -eu
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
if [ ! -f ../e2/out/panels/p01.pdf ]; then
  echo "missing admitted E2 panels under paper/round2/e2/out/panels" >&2
  exit 1
fi
if [ ! -f ../tables-pseudocode/tex/generated/exp1-full.tex ]; then
  echo "missing admitted E1 tables" >&2
  exit 1
fi
export TEXINPUTS="$ROOT/../../tex/vendor:${TEXINPUTS:-}"
rm -f main.aux main.log main.out main.pdf
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
pdftotext -layout main.pdf - | grep -q "Full ranking"
pdftotext -layout main.pdf - | grep -q "Front axis"
echo "integration shell compiled: $ROOT/main.pdf"
pdfinfo main.pdf | awk '/Pages/{print}'
