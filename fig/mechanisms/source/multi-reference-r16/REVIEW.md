# R16: preserve causal diagram structure, strengthen experimental comparisons

Cloud-only review candidate. No external write. Baseline: GitHub main
`a288db90974714c651c396603456909b8e71a2a1`; exact vector assets
were matched against `visual-sync-stage` (not the older, misleadingly named
`lt-review-r11-main` renderer). Next comparator: R15 `488fa92`. The approved
Fig. 2 R13 source and Fig. 3 R14 source remain archived under their existing
visual-history tags. Review used the manuscript placements and original figure
pixels at actual width, not enlarged drafts alone.

| Item | Review evidence and choice |
|---|---|
| Fig. 1 | Self-RAG ICLR Oral Fig. 1, SIEVE PVLDB Fig. 4, main and R15. Same-family prefix/output glyph; all LT nodes have consistent 2-/4-slot segment width. Amber only on one real connected path, including one leaf per tree. Keep the author-requested absence of a Plan→Execute connector despite reviewer preference. |
| Fig. 2 | Main and PVLDB CrocSort Fig. 3: quiet fixed tracks and aligned labels. Remove the redundant bottom sentence, not the C₂ provenance key or data. |
| Fig. 3 | Independent SW review vs main, LongLoRA Fig. 3 and Fu et al. Fig. 9. Shrink left stubs and give rounds a wider panel/glyph pitch. Remove repeated cutoff text but retain both amber witnesses, first-refill legend, all-buffered cue and emit/retain. No arrow restored. |
| Fig. 4 | Independent LT review, HOT SIGMOD Fig. 7 and FedRoad ICDE Fig. 6. Preserve both full tree states, compact the geometry. B uses three visually paired segments, single downward action, and one ranked strip, with the same amber provenance. Keep downward old/new pointers distinguished from upward replays. |
| Fig. 5 | Independent pointer review vs FIBA Fig. 2/HOT/FedRoad, plus laid-out inspection. Remove duplicate slot headings and early counters; important old-parent alias appears on the node itself. Keep actual before/after arrows and both first-exhausted cases. |
| E1 tables | Independent reviewer checked rank legend and mock-data disclosure. Change Place to Rank and spell out mean ± SD in setup. No data, marks, precision or rank changed. |
| Fig. 6 / E2 | Two reviewers; OtterTune SIGMOD Fig. 1 / MEMIT ICLR Oral Fig. 5. Use one wider and clearer shared key, explicitly locate model pick at reference cost, retain complete LT/SW × Full/LIMIT group headers. Panel coordinates/graphics untouched. Next trial: test dash/halo strength at 83.15 bp without compromising plotted structure. |
| Fig. 7 / E3 | Two reviewers; OtterTune Fig. 1, Yue et al. ICDE 2024 Fig. 6. Strengthen three-row key legibility, maintain purple 10k and exact glyph locations. Clarify minima among the five sampled points; retain original discrete support and same honest axes. Four raster A/B checks show zero overlap of added inset ink with data/strong ink. |
| Fig. 8 / E4a | Two reviewers; Liu PVLDB Fig. 9, ConnectIt Fig. 3, CrocSort Fig. 7. Clarify shared SW/LT heads, separate Full and LIMIT 10, bottom-only k with identical centers, larger labels, attached vertical scale and aligned hatch. Retain 6×10 single-column panels and exact 166 colored fixture / 74 hatched cells. No claim of 166 observations. Future import needs explicit feasible-unmeasured in addition to infeasible and true zero. |
| Fig. 9 / E4b | Two reviewers; OtterTune Fig. 5, Symmetries ICLR Oral Fig. 2, Yue et al. Fig. 6. Replace duplicate legend and inset with one color/coordinate ledger; foreground star and diamond at exact reference-surface points, nest on agreement. Five of seven discounts; beta 1 is still On-cold. |
| Fig. 10 / E5 | Independent line reviews confirm all nine categories plus separate Full and correct composite marker; frozen and unchanged. |

Visual layout data only. The integrated paper retains one explicit review-copy
notice; no extra stamps in graphics. E3 120 vertices and all marker anchors
bit-for-bit in audit values, E4b 35 exact vertices and both sets of choices
preserved. The stack is recompiled with TeX Live 2026 pdfLaTeX, not Overleaf
itself. Logs and paper crops are retained in the cloud working copy.
