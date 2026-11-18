# Round-2 E2 — cost prediction vs measured (3D)

Deliverables live only under `paper/round2/e2/`. No merge to `main`, no edits to shared integration TeX.

## Run

```bash
cd paper/round2/e2
python3 plot_surfaces.py
cd tex && latexmk -pdf -interaction=nonstopmode preview-main.tex
```

## Outputs

| Path | Description |
|------|-------------|
| `out/e2-vldb-preview.pdf` | Two CropBox pages: 12-cell, then 10-cell |
| `out/e2-figure-12.pdf` / `out/e2-figure-12.png` | Page 1 only. `e2-layout-2x6.png` is the same raster |
| `out/e2-layout-2x5.png` | Page 2 (10-cell derivative) |
| `out/panels/p01–p12.pdf` | Per-panel vectors included by the TeX container |
| `evidence/area-exp5m-vs-e2-same-width.png` | exp5-m above, E2 12-cell below, same dpi |
| `IMPLEMENTATION-BASELINE.md` | Decisions, camera, and what is still missing |

`python3 plot_surfaces.py` renders the panels and compiles the preview. Do not use a montage PDF.

## References

- User reference: `refs/fig-E2-cost-surface-reference.png`
- Original script copy: `refs/recovery-spec/references/scripts-3d/plot_surface.py`