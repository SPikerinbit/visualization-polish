#!/bin/sh
# Rebuild the round-2 shell. Does not redraw panels and does not claim TeX Live 2026.
# Exit 0 means this shell compiled on the engine below. It is not parent acceptance.
set -eu
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
echo "engine: $(pdflatex --version | head -1)"
test -f ../e2/out/panels/p01.pdf
test -f ../tables-pseudocode/tex/generated/exp1-full.tex
test -f ../experiments/figures/e3/e3-sw-full-measured.pdf
test -f ../experiments/figures/e5/e5-limit-sweep.pdf
export TEXINPUTS="$ROOT/../../tex/vendor:${TEXINPUTS:-}"
rm -f main.aux main.log main.out main.pdf
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
if grep -q 'Overfull \\vbox' main.log; then
  echo "overfull vbox remains" >&2
  grep 'Overfull \\vbox' main.log >&2
  exit 1
fi
TEXT=$(pdftotext -layout main.pdf -)
printf '%s\n' "$TEXT" | grep -q "Full ranking"
printf '%s\n' "$TEXT" | grep -q "Front axis"
printf '%s\n' "$TEXT" | grep -q "Synthetic scale scaffold"
printf '%s\n' "$TEXT" | grep -q "not joined to LIMIT"
printf '%s\n' "$TEXT" | grep -q "displayed categories only"
if printf '%s\n' "$TEXT" | grep -q "figure placement"; then
  echo "preview placement title leaked into the shell" >&2
  exit 1
fi
echo "integration shell compiled: $ROOT/main.pdf"
pdfinfo main.pdf | awk '/Pages|Producer/{print}'
mkdir -p pages
pdftoppm -png -r 110 main.pdf pages/page
echo "pages: $(ls pages/page-*.png | wc -l)"
