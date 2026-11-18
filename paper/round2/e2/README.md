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
| `out/e2-layout-2x5.{pdf,png}` | 10-panel candidate |
| `out/e2-layout-2x6.{pdf,png}` | 12-panel candidate |
| `out/e2-hero-cost-only.{pdf,png}` | Single-panel cost-only (no Spearman) |
| `out/panels/p01–p12.{pdf,png}` | Per-panel vector assets |
| `evidence/area-compare-10-vs-12.png` | Same 7 in width side-by-side |
| `evidence/TEX_CONTAINER_REPORT.md` | Original TeX container findings |

## References

- User reference: `refs/fig-E2-cost-surface-reference.png`
- Original script copy: `refs/recovery-spec/references/scripts-3d/plot_surface.py`