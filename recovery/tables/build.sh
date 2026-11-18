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
