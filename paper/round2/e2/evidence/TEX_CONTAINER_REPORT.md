# E2 TeX container定位（round-2）

## 结论

| 项目 | 状态 |
|------|------|
| 原论文中「3D k-sweep 成本曲面组图」专用 `figure*` 容器 | **未在附件 `unpacked-paper/exp.tex` 中找到** |
| `fig:exp2-k`（`exp.tex` 218–251） | **六张 2D LIMIT-$K$ 敏感性曲线**，不是 3D 源容器 |
| 通栏多子图面积参照 | **`fig:exp5-m`**（`exp.tex` 417–472）：`figure*` + 两行各 6 个 `0.33\columnwidth` 子图 + 图例 |

## 本轮复用策略

1. **不覆盖** `fig:exp2-k`。
2. 新标签 `fig:e2-surface-2x5` / `fig:e2-surface-2x6` 使用 **单张通栏 PDF 换图**（与合同「尽量只换图」一致），避免在正文里重写 `\subfigure` 网格。
3. 若将来必须在 TeX 内嵌 12 格而非单 PDF，可参考 `fig:exp5-m` 的负 `\hspace` 压缩；见 `evidence/exp5-m-vs-e2-diff.patch`。

## 尺寸证据

- `evidence/area-metrics.json`：`e2-layout-2x5.pdf` 与 `e2-layout-2x6.pdf` 均为 **7.0 in 宽**（sigconf `\textwidth`）。
- 高度约 **3.95 in / 4.05 in**；原 `exp5` 单 panel 源 PDF 边长约 1.85 in（含边距），组图总行高需与 `fig:exp5-m` 印刷行对齐——见 `area-compare-10-vs-12.png` 同宽对照。

## 数据来源

无正式实测 `surface_data.json`；高度为 `plot_surfaces.py` 内示意场，caption 已标明 synthetic。