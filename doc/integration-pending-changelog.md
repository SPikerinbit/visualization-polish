# Integration pass: changed vs pending (2026-11-18)

## Merged (parent-approved, not redrawn)

- PR13 framework Fig.1 @ `5b3a024` → `fig-approved/algo1-framework.pdf`, replaces `fig:exp:semantic_external_merge` (`figure*`, 178mm width)

- PR10 pseudocode @ `2973a86` → `integration/pseudocode-*.tex` (Alg1–5); legacy Init/Alg6 in `tex/legacy/appendix-algorithms-old.tex`
- PR11 E4c labeled Full + LIMIT10 → `fig-approved/exp4c-*-labeled.pdf`
- PR12 E4b beta curves → `fig-approved/e4b-beta.pdf`
- Prior seven figures unchanged paths under `fig-approved/`

## Unified LT($h$) (not a third family)

- Removed from PDF render: standalone segmented figure, old Alg6 block, legacy `fig:exp3-ablation` panels, measured experiment tables, old Exp4/5/m panels
- Cost: $a\in\{\mathrm{SW},\mathrm{LT}\}$; $\Pcost_{\SLT}$ appendix block archived
- Intro/conclusion/table row updated; $\mathrm{SLT}$ macro remains in `main.tex` for backward refs only

## Pending visible placeholders

- Exp1 tables, Exp4a, framework intro diagram (`\pendingviz{...}`)
- Legacy figures: `fig:exp2-k`, `fig:exp4-full`, `fig:exp5-m` (sources in `tex/legacy/` or zip-era `fig/panels/`)

## Build

- `paper/build.sh`: clean aux, 3× pdflatex, structure check (labels + assets, not caption substring)
- Footer: `VISUAL LAYOUT PREVIEW --- NOT EXPERIMENTAL RESULTS`