# E2 TeX container (round-2)

## 3D k-sweep float

`unpacked-paper/exp.tex` still has no 3D cost-surface float. `fig:exp2-k` (lines 218–251) is six 2D LIMIT-K curves. Do not treat it as the source container.

## What is reused

`tex/fig-e2-exp5-container-12.tex` follows `fig:exp5-m` (lines 417–472): `figure*`, legend at `0.8\linewidth`, `\vspace{-2ex}`, cells at `0.33\columnwidth`, `\hspace{-2.5ex}`, a blank line between the two rows of six. Each cell is its own PDF (`out/panels/p01.pdf`–`p12.pdf`). Titles are outside the PDF: Syn-A … Syn-L.

`fig:exp5-m` is a 2D batch-size figure. Reusing its grid is not a claim that the 3D k-sweep container was found.

## 10-cell file

`tex/fig-e2-exp5-container-10.tex` drops Syn-F and Syn-L and keeps the same cell width and legend. It is a derivative.

## Area

`tex/exp5-baseline-same-env.tex` recompiles the original 12 panels in the same sigconf class as the E2 preview. `evidence/area-exp5m-vs-e2-same-width.png` stacks the two figure bounding boxes at the same dpi, without resampling one onto the other. An earlier comparison used a broken two-column compile and a title page; that file is not the evidence.
