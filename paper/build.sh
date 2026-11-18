#!/bin/sh
set -eu
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/tex"
ver=$(pdflatex --version | head -n 1)
printf '%s\n' "$ver"
printf '%s\n' "$ver" | grep -q "TeX Live 2026" || {
  printf 'REFUSING: pdfLaTeX must be TeX Live 2026. Found: %s\n' "$ver" >&2
  printf 'Use paper/build-local.sh on TeX Live 2023 for a non-release inspection build.\n' >&2
  exit 1
}
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
fi

python3 - << PY
from pathlib import Path
import re, subprocess, sys

tex = Path('.').resolve()
paper = tex.parent
pdf = tex / 'main.pdf'
aux = (tex / 'main.aux').read_text(errors='replace')
labels = set(re.findall(r"\\newlabel\{([^}]+)\}", aux))
required_labels = {
    'fig:exp2-surface-2x2', 'fig:exp3-scale',
    'fig:exp4a-dl20-n100', 'fig:exp4a-covid-n500', 'fig:exp4b-beta',
    'fig:exp4c-full', 'fig:exp4c-topk',
    'fig:exp5-k-sweep-off', 'fig:exp5-k-sweep-on',
    'fig:exp:semantic_external_merge', 'fig:eg:sliding_window', 'fig:eg:loser_tree_kway_group_merge',
    'alg:semantic_external_merge', 'alg:sliding_window_kway_group_merge',
    'alg:loser_tree_kway_group_merge', 'alg:replay_segment_node',
    'alg:refresh_loser_tree_path',
}
missing_labels = sorted(lab for lab in required_labels if lab not in labels)
for rel in (
    'fig-approved/sw-wide.pdf', 'fig-approved/algo1-framework.pdf',
    'fig-approved/e4a-compact-dl20-n100.pdf',
    'fig-approved/e4a-compact-trec-covid-n500.pdf',
    'fig-approved/e4b-beta.pdf',
    'fig-approved/exp4c-full-labeled.pdf',
    'fig-approved/exp4c-topk-labeled.pdf',
    'fig-approved/e5-limit-sweep-off.pdf',
    'fig-approved/e5-limit-sweep-on.pdf',
    'integration/pseudocode-alg1-only.tex',
):
    if not (tex / rel).exists():
        missing_labels.append(f'missing-file:{rel}')
text = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'], text=True)
if 'VISUAL LAYOUT PREVIEW' not in text or 'NOT EXPERIMENTAL RESULTS' not in text:
    missing_labels.append('footer')
elif not re.search(
    r"VISUAL LAYOUT PREVIEW\s+[-\u2010-\u2015—–]+\s+NOT EXPERIMENTAL RESULTS", text
):
    missing_labels.append('footer-exact')
map_json = paper / 'doc' / 'label-page-map.json'
if not map_json.is_file():
    missing_labels.append('missing-file:paper/doc/label-page-map.json')
if missing_labels:
    raise SystemExit(f'structure check failed: {missing_labels}')
print(f'structure ok pages={len(text.split(chr(12)))} labels={len(labels)} map={map_json}')
PY