# E2 round-2 acceptance record

This is a measurement record, not a visual pass. A parent still has to look at the printed-size figure.

## What was wrong, and what this build changes

- One preview PDF. Two pages. Page 1 is the 12-cell figure (2×6). Page 2 is the 10-cell derivative (2×5). The title page is not in this PDF.
- `out/e2-layout-2x6.png` and `out/e2-figure-12.png` are rasters of preview page 1 (CropBox = the figure). `out/e2-layout-2x5.png` is the raster of page 2. `out/e2-figure-12.pdf` is page 1 alone.
- Old matplotlib montage PDFs are removed. They were a different edition from the TeX panels.
- Panel MediaBox stays 133.2×133.2 pt. Placed cell is 79.28 pt (`0.33\columnwidth` in this sigconf build). Tick type on the placed page measures 5.36 pt. Legend type measures 6.81 pt. The strings are `Meas. min` and `Pred. min` (no printed backslash).
- Cost numerals are inside each panel MediaBox (checked with `pdftotext -bbox` on p01–p12). The unit is in the one-line caption: tokens ×10³. Heights are synthetic.
- Figure bbox height is 234.4 pt against the recompiled `fig:exp5-m` bbox height 233.7 pt (ratio 1.003) in the same sigconf environment. That recompiled figure is the 2D batch-size grid, not a 3D k-sweep float. None was found in `unpacked-paper/exp.tex`.

## Rows

- Page 1 captions: (a)–(f) on one baseline, (g)–(l) on the next.
- Page 2 captions: (a)–(e), then (f)–(j). Syn-F and Syn-L are omitted. This is a derivative, not an original float.

## Data

Schematic heights from `plot_surfaces.py`. Not vLLM measurements and not the production cost model.
