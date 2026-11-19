# Experiment layout review

- PDF: [experiment-layout-review.pdf](experiment-layout-review.pdf)
- Configuration: [EXPERIMENT-VISUALIZATION-CONFIG.md](../../../../doc/round2/EXPERIMENT-VISUALIZATION-CONFIG.md)
- Build: `cd paper/round2/integration && ./build.sh` with pdfLaTeX and the required font/packages installed (algorithm2e, TeX Gyre, Libertine, NewTX, Inconsolata, subfigure).
- Verified engine: TeX Live 2025/dev/Debian, not TeX Live 2026. Two passes, 7 pages, no Overfull. PDF SHA256: `b69027d9ab5ec51fedfc3c9145e04cf1dd2883f05474649753113d75ab0e821c`.
- All experimental values are synthetic layout fixtures, not measurements. Framework and selected plot assets are reconstructed candidates, not byte-identical recovery of lost originals.
- Latest Fig8: one row of complete 90-degree `(k,h)` labels at 6.2bp, independent four-item top legend at 6.3bp. Two bottom panels and the legend changed; all other pages and page 6's right column are pixel-identical to the previous review. Dense cross-state marker occlusion remains.
- `build.sh` compiles checked-in assets; it does not regenerate all figures. Fig8 reproducible source is under `experiments/e4a_c2_recovered/`. Historical generators remain for provenance and should not be run indiscriminately over current assets.
