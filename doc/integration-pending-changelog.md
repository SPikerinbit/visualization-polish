# Integration pass: changed vs pending (2026-11-18)

## Merged (parent-approved, not redrawn)

- PR13 framework Fig.1 @ `5b3a024` → `fig-approved/algo1-framework.pdf`, replaces `fig:exp:semantic_external_merge` (`figure*`, 178mm width)
- PR10 pseudocode @ `2973a86` → `integration/pseudocode-*.tex` (Alg1–5); legacy Init/Alg6 in `tex/legacy/appendix-algorithms-old.tex`
- PR11 E4c labeled Full + LIMIT10 → `fig-approved/exp4c-*-labeled.pdf`
- PR12 E4b beta curves → `fig-approved/e4b-beta.pdf`
- PR8 E4a compact四张 @ `607f3ee` → 正文 DL20 $n{=}100$ + COVID $n{=}500$；附录另两 Panel 仅版式代表（`\providecommand` 共享 caption）
- PR14 tables @ `dd90fa5` → `paper/tex/tables/generated/` + `paper/recovery/tables/`
- Prior specialist figures under `fig-approved/`

## Unified LT($h$) (not a third family)

- Removed from PDF render: standalone segmented figure, old Alg6 block, legacy `fig:exp3-ablation` panels, measured experiment tables, old Exp4/5/m panels
- Cost: $a\in\{\mathrm{SW},\mathrm{LT}\}$; $\Pcost_{\SLT}$ appendix block archived
- Intro/conclusion/table row updated; $\mathrm{SLT}$ macro remains in `main.tex` for backward refs only

## Pending (real open items only)

- Measured E1/E4 numbers and validation table cells
- Legacy LT($h$) global-order proof (archived, short appendix stub)
- `finite.py` / production `Expect` calibration
- Midrank and cost-model statistics (contract sign-off)

## Withdrawn from render (no gray placeholder)

- Legacy figures: `fig:exp2-k`, `fig:exp4-full`, `fig:exp5-m`

## Build

- `paper/build.sh`: TeX Live 2026, clean aux, 3× pdflatex, structure check
- Footer: `VISUAL LAYOUT PREVIEW --- NOT EXPERIMENTAL RESULTS`