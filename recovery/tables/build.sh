#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python3 emit.py --write-checkpoint
python3 -m unittest tests/test_tables.py
( cd render && TEXINPUTS=../vendor: pdflatex -interaction=nonstopmode main.tex >/tmp/e1-tables-pass1.log )
( cd render && TEXINPUTS=../vendor: pdflatex -interaction=nonstopmode main.tex >/tmp/e1-tables-pass2.log )
( cd probe && TEXINPUTS=../vendor: pdflatex -interaction=nonstopmode main.tex >/tmp/e1-probe.log )
echo "---- page geometry ----"
grep -E "TEXTWIDTH=|COLUMNWIDTH=|TEXTHEIGHT=|COLUMNSEP=" /tmp/e1-tables-pass2.log
echo "---- overfull / underfull ----"
grep -E "Overfull|Underfull" /tmp/e1-tables-pass2.log /tmp/e1-probe.log || true
python3 measure_layout.py
ART=/opt/cursor/artifacts
mkdir -p "$ART"
cp render/main.pdf "$ART/e1-tables.pdf"
cp probe/main.pdf "$ART/e1-tables-probe.pdf"
pdftoppm -png -r 140 render/main.pdf "$ART/e1-tables-page" >/dev/null
pdftoppm -png -r 140 probe/main.pdf "$ART/e1-tables-probe-page" >/dev/null
rm -f "$ART/e1-tables-tex.zip"
zip -r "$ART/e1-tables-tex.zip" \
  NOTES.md emit.py ranking.py synthetic.py catalog.py build.sh measure_layout.py \
  tex render data probe vendor tests .gitignore >/dev/null
echo "Artifacts under $ART"
