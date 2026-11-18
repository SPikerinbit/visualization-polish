#!/bin/sh
set -eu
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PAPER_ROOT="$ROOT"
mkdir -p "$ROOT/doc"
cd "$ROOT/tex"
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
python3 "$ROOT/scripts/label_page_map.py"
if [ -d "$ROOT/../doc" ]; then
  cp "$ROOT/doc/label-page-map.md" "$ROOT/../doc/label-page-map.md"
  cp "$ROOT/doc/label-page-map.json" "$ROOT/../doc/label-page-map.json"
fi
python3 "$ROOT/scripts/structure_check.py"