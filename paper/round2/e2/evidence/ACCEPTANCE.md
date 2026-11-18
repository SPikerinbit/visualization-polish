# E2 acceptance record

Measurement record for the parent. Not a visual pass.

## This round

Three items only. Tick size, legend size, page count, and the 79.28 pt cell were already checked on `e8e3c0c` and were not rebuilt as a new design.

1. Axis meaning. Each panel PDF has a short `k` on the front axis and `h` on the depth axis. The caption says: front axis \(k\) (fan-in), depth axis \(h\) (segment length); vertical tokens ×10³. Placed `k` / `h` / cost numerals are 5.357 pt. Legend words are 6.806 pt (`Measured`, `Predicted`, `Meas. min`, `Pred. min`).
2. Inner whitespace. p01 ink (gray < 245) runs from 17.02 pt to 123.05 pt on the 133.2 pt page: empty band 27.16 pt (20.4%), which is 16.2 pt in the 79.28 pt cell. The previous band was 49.3 pt (29.3 pt placed). `pdftotext -bbox` on p01–p12: every word, including `k` and `h` and the cost numerals, is inside 133.2×133.2. Point set unchanged (Syn-A 96 with the five LT gaps; other LT panels 101; SW panels keep the legal domain).
3. Area evidence. `tex/exp5-baseline-same-env.tex` now keeps the original multiline `\subfigure` breaks. Placed step 78.632 pt, overlap 0.650 pt, on both the exp5-m page and the E2 12-cell page. The 5.13 pt overlap is gone, so the right frame is no longer covered by the next cell. Vector-inclusive figure boxes, same dpi, no rescale: exp5-m 482.27×239.91 pt, E2 479.82×240.96 pt. Cell blocks are both 479.82 pt wide (heights 181.89 and 182.09). The earlier 234.4/233.7 ratio is withdrawn. exp5-m is still the 2D batch-size figure. No 3D k-sweep float was found.

## Pages

`out/e2-vldb-preview.pdf` has two pages. CropBox is the figure; MediaBox is letter. Page 1 is 2×6, captions (a)–(f) then (g)–(l). Page 2 is 2×5, captions (a)–(e) then (f)–(j), and the caption says Syn-F and Syn-L are omitted. `out/e2-figure-12.png` matches page 1. `out/e2-layout-2x6.png` is the same raster. `out/e2-layout-2x5.png` matches page 2.

## Data

Schematic heights from `plot_surfaces.py`. Not vLLM measurements and not the production cost model.
