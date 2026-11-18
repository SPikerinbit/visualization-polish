# 实验五 LIMIT n 扫描 — 有界检查点

只做结果曲线。没有画 LIMIT 执行机制图，没有改 `viz/` 或其他图，没有独立 Layout Supplement，没有并进论文。

## 打开了哪些文件

- 附件八栏：`/tmp/recovery-spec/逐图制作说明.md` 的「图 E5 — LIMIT K sweep」
- 附件交接：`/tmp/recovery-spec/给后续制作者的交接要求.md`
- 合同：`paper-experiments.md` 第 7 节，`可视化建议.md` 的「实验五」
- 原论文压缩包里的 `exp.tex`（`fig:exp2-k` 约 218–251 行，`fig:exp4-topk`）
- 原论文样图，已栅格化后看过：
  - `fig/panels/exp2/exp2_legend.pdf`
  - `fig/panels/exp2/exp2_movies_tokens.pdf`
  - `fig/panels/exp2/exp2_movies_latency.pdf`
  - `fig/panels/exp2/exp2_movies_quality.pdf`
  - `fig/panels/exp2/exp2_dl20_tokens.pdf`
  - `fig/panels/exp4/exp4_topk_legend.pdf`
  - `fig/panels/exp4/exp4_topk_movies_m20_tokens.pdf`
  - `fig/panels/exp4/exp4_topk_movies_m20_quality.pdf`
  - `fig/panels/exp4/exp4_topk_dl20_m20_tokens.pdf`
- `viz/figures/exp5-off.pdf` 与 `exp5-on.pdf` 只用来确认不要重画的错误，不是基线

`fig:exp5-m` 是 batch size \(m\)，没有拿来当这张图的样子。

## 从样图保留的可读性

这些是旧图的读法，不是同一实验。

- `fig:exp2-k` 的 SW 是红圆实线，LT 是蓝三角实线。颜色取自 `exp2_movies_tokens.pdf` 的描边 `(0.839, 0.153, 0.157)` 与 `(0.122, 0.467, 0.706)`。没有第三条 SLT 绿虚线。
- 图例在图外、无线框，刻度字水平放置，纵轴用短标签加 \(\times 10^{k}\)。
- 费用和质量分成上下两行，不叠在同一根纵轴上。
- `fig:exp4-topk` 只说明 fan-in \(k\) 的刻度可以很疏。它的横轴是 merge fan-in，不是 LIMIT \(n\)。

## 这张图实际画了什么

- Off 与 On-cold 各一张。每张按 DL20、COVID 分面。每面只有 SW、LT。
- LIMIT 点 `10, 20, 50, 100, 200, 300, 400, 490, 500` 连线。LIMIT 500 是 buffer，在连线的末端。
- Full 在断轴后的窄带里，每条曲线一个点，用同一套圆/三角，不与 LIMIT 500 相连，不是 \(K{=}510\)。
- 横轴写的是 LIMIT \(n\)。九个位置等距，是合同清单的顺序，不是线性 \(n\)。图内写明 equal spacing, not linear in \(n\)。
- 纵轴：Off 为 \(U\)，On-cold 为 \(U{-}Q\)、\(\beta{=}0\)，单位 \(\times 10^{3}\)。两张图的费用纵轴范围不同（Off \([15,58]\)，On-cold \([10,48]\)），没有压成同一标尺。
- 辅助质量是固定的 NDCG@10，含每个 LIMIT \(n\) 和 Full。放在第二行。这是未定项里的一种排法，不是已确认的独立附图。
- 图顶红字：Synthetic placeholder. A gap is not a measured advantage.
- 页面宽度 178 mm（PDF 媒体框已核对为 178.00 mm）。

## 看图后改过的一次

第一稿有三处读起来是错的，只改了这三处：

1. `LIMIT n` 原先写在整页中线，落在左侧 Full 刻度下面。现在每个 LIMIT 轴下面各有一个，不压在 Full 上。
2. 断轴斜线切进 `500` 和 `Full`。斜线改到两轴之间的空隙里。
3. Full 带里 SW 与 LT 的费用几乎叠成一个点。两点在 Full 带内部左右错开 \(\pm 0.24\) 个带内坐标，仍是各一个点，不是方块，也不是第二个 Full 观测。

改完后重看了整图、底栏和 Full 交接处：`490` 与 `500` 分开，Full 不连线，印章和 \(\beta{=}0\) 在页内。

## 不足

- 正式结果还没有。表里每个格子是一个占位数字，不是 3 个 query 的等权均值。曲线上没有标 \((k,h)\)，因为给聚合曲线编一个共同参数是假的。
- 占位曲线会交叉。交叉和 Full 与 LIMIT 500 的高低差都不是实测优势。
- 等距刻度看不出 490 与 500 只差 10。线性轴在半幅宽上无法同时放下这两个标签，所以没有改成线性轴。
- Full 带的左右错开可能被读成两个不同的 Full 位置。caption 写明它只是为了把两个点分开。
- 浅灰带是分隔，不是另一块结果图。没有使用方块标记。
- 质量用第二行还是另图，合同未定。
- 本环境没有 TeX，片段没有编译。矢量 PDF 本身的媒体框是 178 mm。
- 建议标签是 `fig:exp5-k-sweep-off` 与 `fig:exp5-k-sweep-on`。没有占用 `fig:exp2-k` 或 `fig:exp5-m`。
