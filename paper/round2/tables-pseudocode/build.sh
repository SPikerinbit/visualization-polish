#!/bin/bash
# Rebuild the VLDB preview from the synthetic sheets. Numbers are not edited in TeX.
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../../.. && pwd)"
export TEXINPUTS="${ROOT}/paper/tex/vendor:${TEXINPUTS:-}"
PYTHONPATH=src python3 -m unittest discover -s src/tests
PYTHONPATH=src python3 -m emit
mkdir -p build
# preview.tex lives in tex/ and inputs generated/ relative to that directory.
(
  cd tex
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../build preview.tex
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../build preview.tex
)
rm -f build/page-*.png
pdftoppm -png -r 140 build/preview.pdf build/page
python3 - << 'PY'
from pathlib import Path
log = Path("build/preview.log").read_text(errors="replace")
over = [line for line in log.splitlines() if line.startswith("Overfull")]
under = [line for line in log.splitlines() if line.startswith("Underfull")]
print(f"overfull {len(over)}")
for line in over:
    print(line)
print(f"underfull {len(under)}")
for line in log.splitlines():
    if line.startswith("TEXTWIDTH") or line.startswith("COLUMNWIDTH") or line.startswith("TEXTHEIGHT"):
        print(line)
print("pages", len(list(Path("build").glob("page-*.png"))))
PY
