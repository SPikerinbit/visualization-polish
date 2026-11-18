# E2 implementation baseline

Handoff for the next edit. This is the decision record for `paper/round2/e2/` only. Do not treat the figures as measurements.

## Decisions already made

- Primary figure is the 12-cell 2×6 `figure*` in `tex/fig-e2-exp5-container-12.tex`. The 10-cell file drops Syn-F and Syn-L and is a derivative, not an original float.
- Each cell is its own vector PDF (`out/panels/p01.pdf`–`p12.pdf`), included at `0.33\columnwidth`. Do not replace that with one montage PDF, and do not scale the cropped whole-figure PDF up to the text width. That crop is about 484 pt wide; stretching it to ~506 pt would enlarge the type.
- Cost only. No Spearman inset.
- Heights are schematic. Captions say so. Do not invent query ids, regret, or vLLM numbers.
- The predicted-minimum diamond is drawn at the **measured** height of that `(k, h)` (`selected.u`). The original script draws it at `sel['P']/1000`. When the two minima coincide, the orange diamond and the blue star share that measured point and there is no vertical connector. The original script draws that connector.
- Integrate through the per-panel TeX container. `out/e2-vldb-preview.pdf` is two CropBox pages (12-cell, then 10-cell). MediaBox stays 612×792. `pdftoppm` without `-cropbox` shows the letter page; the delivery PNGs are CropBox rasters from PyMuPDF.

## Original script (do not claim we re-ran it)

Copy: `refs/recovery-spec/references/scripts-3d/plot_surface.py`.

- One `Poly3DCollection`, both surfaces interleaved, `zsort='average'`.
- Face alpha blue 0.55, orange 0.22. Edge alpha 0.64 / 0.86. Edge width 0.55 / 0.80.
- Scatter `s=12`. Blue filled, orange open. Star `s=175` at measured height. Diamond `s=85` at predicted height.
- Camera `elev=26`, `azim=-54`, orthographic. Box aspect `(1.45, 1, 0.92)`, zoom 1.04.
- Poster limits were `k=2..10`, `h=1..10` (`xlim (1.7, 10.35)`), z label “Merge input tokens (1k)”.
- Colors: blue `#087F9B`, orange `#DA821E`.

`compute_surface.py` needs Windows paths, `sema_prototype`, `finite.py`, and `surface_data.json`. None of those are in this tree. There is no measured surface to plot.

## What the panels actually use

`plot_surfaces.py` keeps the camera, the interleaved collection, the colors, and the face/edge alphas. Panel scatter, star, diamond, and edge widths are smaller so a 79.28 pt cell stays readable (`pt_s=1.7`, star 26, diamond 12, edge width 0.32 / 0.40). Source tick and axis-name size is 9 pt. Placed size is 5.357 pt (`9 × 79.282 / 133.2`). Legend source is a fixed 5.60 in PDF at 6.8 pt, included at `0.8\linewidth`; placed legend type measures 6.806 pt.

Panel axes rectangle is `[0.06, 0.11, 0.74, 0.85]`, zoom 1.08. Short names on the axes are the plain letters `k` (front, fan-in) and `h` (depth, segment length). The vertical unit is only in the caption: tokens ×10³. Do not turn the z label back on inside the cell; it does not fit at 9 pt.

Legal samples, before the schematic gaps: LT `k=2..min(25, 2^(m-1))`, `h=1..max_segment(k, m=20)` → 101 points. SW `k=2..min(25, 20)`, `h=1..(m//k)` → 46 points. Gaps, only when `gap=True`: LT `{(3,5),(3,6),(4,4),(5,4),(6,5)}`, SW `{(2,5),(3,4),(4,4)}`. Syn-A is the LT gap case (96 points). Every other listed point is drawn. Panel names are Syn-A … Syn-L.

## Substitute reference, and what is still missing

`unpacked-paper/exp.tex` has no 3D k-sweep float. `fig:exp2-k` is six 2D LIMIT-K curves. The nearest legal grid is `fig:exp5-m` (lines 417–472), a 2D batch-size figure. `tex/exp5-baseline-same-env.tex` recompiles those panels with the original line breaks. In this sigconf build the placed cell is 79.282 pt, the step is 78.632 pt, and the overlap is 0.650 pt. An earlier one-line compile overlapped by 5.13 pt and hid the right frame; do not use that PDF, and do not cite the withdrawn 234.4 / 233.7 pt ratio.

Current vector-inclusive figure boxes, same dpi, no rescale (`evidence/area-metrics.json`):

- exp5-m figure 482.27 × 239.91 pt. The extra width past the cell block is the 2D “Batch size m” label and a stroke, not a wider grid.
- E2 12-cell figure 479.82 × 240.96 pt.
- Both cell blocks are 479.82 pt wide. Heights 181.89 pt (exp5-m) and 182.09 pt (E2).

Source panel p01 vertical empty band (gray < 245) is 17.02 + 10.15 = 27.16 pt of 133.2 (20.4%). At the 79.28 pt cell that is 16.2 pt. The previous band was 49.3 pt (37%, 29.3 pt placed). Glyphs, including `k` and `h`, stay inside the 133.2 pt MediaBox.

Still missing: `surface_data.json`, vLLM traces, the production cost model, and any original 3D k-sweep TeX. These surfaces are not experimental results.
