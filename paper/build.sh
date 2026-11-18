#!/bin/sh
set -eu
cd "$(dirname "$0")/tex"
ver=$(pdflatex --version | head -n 1)
printf '%s\n' "$ver"
printf '%s\n' "$ver" | grep -q "TeX Live 2026" || {
  printf 'REFUSING: pdfLaTeX must be TeX Live 2026. Found: %s\n' "$ver" >&2
  printf 'Use paper/build-local.sh on TeX Live 2023 for a non-release inspection build.\n' >&2
  exit 1
}
kpsewhich eso-pic.sty >/dev/null
export TEXINPUTS=./vendor:${TEXINPUTS:-}
export BSTINPUTS=./vendor:${BSTINPUTS:-}
export BIBINPUTS=./vendor:${BIBINPUTS:-}
pdflatex -interaction=nonstopmode main.tex
if grep -q '\\citation{' main.aux; then
  bibtex main
else
  printf 'No \\citation in main.aux; skipping bibtex.\n'
fi
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
python3 - << 'PY'
from pathlib import Path
import subprocess
pdf = Path("main.pdf")
text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
labels = [
    "fig:eg:sliding_window",
    "fig:eg:loser_tree_kway_group_merge",
    "fig:eg:pointer-rule",
    "fig:exp2-surface-2x2",
    "fig:exp3-scale",
    "fig:exp5-k-sweep-off",
    "fig:limit-demand-trial",
]
# pdftotext does not preserve labels; check figure captions and footer instead.
needles = [
    "SYNTHETIC DATA",
    "sw-wide",
    "Pointer-guided LT",
    "Local pointer rule",
    "Synthetic layout preview",
    "Optional concept trial",
    "LIMIT",
]
missing = [n for n in needles if n not in text]
if missing:
    raise SystemExit(f"integration smoke failed missing={missing}")
pages = [p for p in text.split("\f") if p.strip()]
print(f"integration build ok pages={len(pages)}")
PY