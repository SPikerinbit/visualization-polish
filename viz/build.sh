#!/bin/sh
set -eu
cd "$(dirname "$0")/tex"
ver=$(pdflatex --version | head -n 1)
printf '%s\n' "$ver"
printf '%s\n' "$ver" | grep -q "TeX Live 2026" || {
  printf 'REFUSING: pdfLaTeX must be TeX Live 2026. Found: %s\n' "$ver" >&2
  printf 'This script does not accept Ubuntu TeX Live 2023.\n' >&2
  exit 1
}
kpsewhich eso-pic.sty >/dev/null
kpsewhich placeins.sty >/dev/null
export TEXINPUTS=./vendor:${TEXINPUTS:-}
export BSTINPUTS=./vendor:${BSTINPUTS:-}
export BIBINPUTS=./vendor:${BIBINPUTS:-}
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
python3 - << 'PY'
from pathlib import Path
import subprocess
pdf = Path("main.pdf")
text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
required = [
    "Algorithm 1",
    "Algorithm 2",
    "Algorithm 3",
    "Algorithm 4",
    "Algorithm 5",
    "LIMIT 500",
    "both roles",
    "ListwiseRank",
]
missing = [item for item in required if item not in text]
pages = [page for page in text.split("\f") if page.strip()]
blank = []
for i, page in enumerate(pages, start=1):
    body = page.replace("SYNTHETIC DATA — LAYOUT PREVIEW ONLY", "")
    body = body.replace("SYNTHETIC DATA --- LAYOUT PREVIEW ONLY", "")
    if sum(ch.isalnum() for ch in body) < 40:
        blank.append(i)
if missing or blank:
    raise SystemExit(f"coverage failed missing={missing} blank_pages={blank}")
print(f"coverage ok pages={len(pages)}")
PY
