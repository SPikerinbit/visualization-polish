# E2 TeX 容器定位（round-2 修订）

## 3D k-sweep 原容器

在附件 `unpacked-paper/exp.tex` 中 **仍未找到** 用户所述「3D k-sweep 成本曲面组图」专用 float。`fig:exp2-k`（218–251 行）为六张 2D LIMIT-$K$ 曲线，**不是** 3D 源。

## 本轮「只换图」的含义（纠正上一轮表述）

用户要求的是 **复用原组图 TeX 的 subfigure 网格/间距/图例容器，逐格替换各 panel 的矢量 PDF** —— **不是** 用一张拼好的 montage PNG/PDF 做 `\includegraphics[width=\textwidth]{…}`。

### 12 格（忠实 exp5-m 结构）

- 文件：`tex/fig-e2-exp5-container-12.tex`
- 结构对齐 `exp.tex` `fig:exp5-m`（417–472）：`0.8\linewidth` 图例 + 两行六列、`0.33\columnwidth`、`\hspace{-2.5ex}`。
- 每格：`panels/p01.pdf` … `panels/p12.pdf`（matplotlib 独立导出，非位图组图）。
- 子图标题外置：`Syn-A … Syn-L` + LT/SW + Full/LIMIT10（**合成案例名，非 query 实测**）。

### 10 格（派生）

- 文件：`tex/fig-e2-exp5-container-10.tex`
- **省略** Syn-F（`p06`）与 Syn-L（`p12`）两格；**不声称**与原论文某一 float 一一对应。

### 面积对照证据

- 原容器同宽渲染：`tex/exp5-m-area-block.tex` → 编译得到 `tex/exp5-m-area-block.pdf`
- E2 预览：`tex/preview-main.tex` 第 1 页为 12 格容器
- 对照图：`evidence/area-exp5m-vs-e2-same-width.png`（同 sigconf 版宽下上下叠放）
- 数值：`evidence/area-metrics.json`

## 与旧 `fig-e2-layout-2x*.tex` 的关系

单张 montage 方案已弃用为主交付；保留目录内旧文件仅供历史对比，**主路径为 exp5-m 容器 + 分 panel PDF**。