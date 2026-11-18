#!/bin/sh
set -eu
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PAPER_ROOT="$ROOT"
mkdir -p "$ROOT/doc"
cd "$ROOT/tex"
ver=$(pdflatex --version | head -n 1)
printf '%s\n' "$ver"
if [ "${PAPER_BUILD_ALLOW_LOCAL_TEX:-0}" != 1 ]; then
  printf '%s\n' "$ver" | grep -q "TeX Live 2026" || {
    printf 'REFUSING: pdfLaTeX must be TeX Live 2026. Found: %s\n' "$ver" >&2
    printf 'Use paper/build-local.sh on TeX Live 2023 for a non-release inspection build.\n' >&2
    printf 'Or set PAPER_BUILD_ALLOW_LOCAL_TEX=1 only to verify scripts (non-release).\n' >&2
    exit 1
  }
else
  printf 'NOTE: PAPER_BUILD_ALLOW_LOCAL_TEX=1 — engine check skipped; post-check still runs.\n' >&2
fi
for pkg in eso-pic.sty placeins.sty cleveref.sty tcolorbox.sty sansmath.sty; do
  kpsewhich "$pkg" >/dev/null
done
export TEXINPUTS=./vendor:${TEXINPUTS:-}
export BSTINPUTS=./vendor:${BSTINPUTS:-}
export BIBINPUTS=./vendor:${BIBINPUTS:-}
rm -f main.aux main.out main.toc main.bbl main.blg main.log
pdflatex -interaction=nonstopmode main.tex
if grep -q '\\citation{' main.aux; then
  bibtex main
else
  printf 'No \\citation in main.aux; skipping bibtex.\n'
fi
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

python3 "$ROOT/scripts/label_page_map.py"
if [ -d "$ROOT/../doc" ]; then
  cp "$ROOT/doc/label-page-map.md" "$ROOT/../doc/label-page-map.md"
  cp "$ROOT/doc/label-page-map.json" "$ROOT/../doc/label-page-map.json"
fi

python3 "$ROOT/scripts/structure_check.py"