# E2 TeX container

## 3D k-sweep float

`unpacked-paper/exp.tex` has no 3D cost-surface float. `fig:exp2-k` (lines 218–251) is six 2D LIMIT-K curves. It is not the source container.

## What is reused

`tex/fig-e2-exp5-container-12.tex` follows `fig:exp5-m` (lines 417–472): `figure*`, legend at `0.8\linewidth`, `\vspace{-2ex}`, cells at `0.33\columnwidth`, `\hspace{-2.5ex}` except between the third and fourth cell of each row, and a blank line between the two rows. Each cell is `out/panels/p01.pdf`–`p12.pdf`. Titles sit outside the PDF (Syn-A … Syn-L). The caption names the front axis \(k\), the depth axis \(h\), and vertical tokens ×10³.

This reuses the 2D batch-size grid. It is not a claim that a 3D k-sweep container was found.

## 10-cell file

`tex/fig-e2-exp5-container-10.tex` drops Syn-F and Syn-L and keeps the same cell width, legend, and spacing. It is a derivative.

## Area

`tex/exp5-baseline-same-env.tex` recompiles the original exp5 panels in this sigconf class, with the same line breaks as `exp.tex` 417–472. Measured placement: cell 79.282 pt, step 78.632 pt, overlap 0.650 pt. The E2 12-cell page matches those three numbers. A previous baseline put every subfigure on one line and overlapped by 5.13 pt; that PDF is not the evidence, and the 234.4/233.7 pt ratio from it is withdrawn.

`evidence/area-exp5m-vs-e2-same-width.png` stacks the two vector-inclusive figure boxes at 160 dpi and does not resample one onto the other. Numbers are in `evidence/area-metrics.json`. The exp5-m box is 2.45 pt wider than the E2 box because the 2D axis title “Batch size m” extends past the cell. The cell blocks are the same width (479.82 pt).
