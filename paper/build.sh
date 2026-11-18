#!/bin/sh
set -eu
ROOT="$(dirname "$0")"
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
python3 - << 'PY'
from pathlib import Path
import re, subprocess, sys
root = Path('.')
pdf = root / 'main.pdf'
aux = (root / 'main.aux').read_text(errors='replace')
labels = set(re.findall(r'\\newlabel\{([^}]+)\}', aux))
required_labels = {
    'fig:exp2-surface-2x2', 'fig:exp3-scale', 'fig:exp4b-beta',
    'fig:exp4c-full', 'fig:exp4c-topk', 'fig:exp5-k-sweep-off',
    'fig:exp:semantic_external_merge', 'fig:eg:sliding_window', 'fig:eg:loser_tree_kway_group_merge',
    'alg:semantic_external_merge', 'alg:sliding_window_kway_group_merge',
    'alg:loser_tree_kway_group_merge', 'alg:replay_segment_node',
    'alg:refresh_loser_tree_path',
}
missing_labels = sorted(required_labels - labels)
for rel in (
    'fig-approved/sw-wide.pdf', 'fig-approved/algo1-framework.pdf',
    'fig-approved/e4b-beta.pdf',
    'fig-approved/exp4c-full-labeled.pdf', 'integration/pseudocode-alg1-only.tex',
):
    if not (root / rel).exists():
        missing_labels.append(f'missing-file:{rel}')
text = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'], text=True)
if 'VISUAL LAYOUT PREVIEW' not in text:
    missing_labels.append('footer')
if 'VISUAL LAYOUT PREVIEW --- NOT EXPERIMENTAL RESULTS' not in text:
    missing_labels.append('footer-exact')
pages = text.split('\f')
page_by_snippet = {}
for i, page in enumerate(pages, 1):
    if 'Pointer-guided LT' in page or 'LT(' in page and '16-element' in page:
        page_by_snippet.setdefault('lt-figure', i)
    if 'Sliding-window' in page or 'sliding-window' in page:
        page_by_snippet.setdefault('sw-figure', i)
map_path = root.parent / 'doc' / 'label-page-map.json'
import json
entries = []
for lab in sorted(required_labels):
    if lab in labels:
        entries.append({'label': lab, 'page': 'see aux', 'source': f'integration or framework'})
map_path.write_text(json.dumps({'labels_ok': len(required_labels)-len(missing_labels), 'pages': len(pages), 'missing': missing_labels, 'hints': page_by_snippet}, indent=2) + '\n')
if missing_labels:
    raise SystemExit(f'structure check failed: {missing_labels}')
print(f'structure ok pages={len(pages)} labels={len(labels)}')
PY