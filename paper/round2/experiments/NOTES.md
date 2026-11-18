# E3 / E4a / E4b / E4c / E5

只做这五张实验图。未改 `main.tex`、未做 E2、未做表和机制图、未并入 main。数字都是已有的合成版式样本，没有为了好看改数。

栏宽先用 `paper/recovery/pseudocode/structure.md` 记下的 TeX Live 测量：`\columnwidth = 241.1475 pt`，`\textwidth = 506.295 pt`。本轮安装了 TeX Live 2023，用仓库里的 `paper/tex/vendor/acmart.cls` 和 `pvldb.sty` 编译了无正文预览 `tex/preview.tex`。日志打出 `\columnwidth=241.14749pt`，`\textwidth=506.295pt`，`\textheight=626.0pt`。编译结果在 `tex/preview.pdf`（8 页）。接触图仍是按同一宽度贴的 PNG，预览 PDF 才是 `\subfigure` 实排。

## 印刷尺度

原面板 PDF（`paper/tex/fig/panels`）画布都是 133.2 pt。内容流里数据折线是 1.6 pt，网格 0.765 pt `#B0B0B0`，坐标框 1.36 pt。Fig. 8（`exp.tex` 的 `fig:exp4-topk`）按 `0.25\columnwidth` 放入后，线约 0.72 pt。`0.33\columnwidth` 的实验图约 0.96 pt。

E3 的八张面板按 Fig. 8 的 60.29 pt 方框绘制，折线 0.72 pt。和原 Fig. 8 面板放到同一宽度后，横向暗像素宽度一致。刻度字从印刷后的约 4.1 pt 提到 4.6 pt，否则 1k/5k/10k 在这个方框里糊成一团。E4a/E4b/E5 的折线用 0.33 栏的印刷线宽 0.96 pt。字体是 Liberation Serif，数学是 STIX；机器上没有 Times New Roman。

## E3

单栏四列两行。上排预测、下排实测。列是 SW Full、SW LIMIT、LT Full、LT LIMIT。子图名在 `tex/fig-e3.tex`，不写进 PDF。图例一行十项：左五是 SW 的 \((k,h)\)，右五是 LT。

横轴是 1k、5k、10k 的线性位置，不是等距档。纵轴是版式单位，八张共用 11.1–66.2。预测 = 实测 + 3.4，所以两排几乎同高，这是脚手架，不是两条接近的实测曲线。Full 和 LIMIT 被写成了同一组数，所以同一行里 SW 的两列、LT 的两列看起来一样。没有另造一组数把它们分开。

LT 补充点 \((250,2)\)、\((250,1)\)（5k）和 \((500,2)\)、\((500,1)\)（10k）仍在 `figures/e3/e3-facts.json`。它们不在五条线上，也不是最优。画进 60 pt 方框会把纵轴拉到 69，五条线被压扁，所以没有画。

## E4a

单栏，每个数据集 × \(n\) 一张，四行是 SW Full、SW LIMIT、LT Full、LT LIMIT。图例顺序：Prefix cache off、Prefix cache on、Predicted、Measured。无背景色带。白底浅灰网格。横轴写完整 \((k,h)\)，标在最底下面板，上面三张共用同一组刻度。

\(n{=}100\)、\(m{=}20\) 只有 5 个 run，\(k{=}8\) 非法。\((8,1)\to(5,1)\)，\((8,2)\to(5,2)\)，这条 \(n{=}100\) 曲线用原来的生成器重算。\(n{=}500\) 的整数从 `paper/recovery/e4a/data/e4a_synthetic.json` 原样抄来，\(k{=}8\) 在 25 个 run 下合法，没有删。星和菱形都落在实测高度上。显示子集上的最低点不是合法域上的最优。真实选点仍后置。

## E4b

单栏一张。五条 \(\beta\in\{0,0.25,0.5,0.75,1\}\)，\(U-(1-\beta)Q\)。\(U,Q\) 未改。没有背景色带，没有局部放大，也没有换成另一种 inset。0.1 和 0.9 只留在数据里。

这组数不是 \(n{=}100\)。\((8,1)\)、\((8,2)\) 只在 run 数 ≥ 8 时合法（\(n{=}500\)、\(m{=}20\) 有 25 个 run）。

## E4c 与红虚线

单栏 2×2：Full/LIMIT × cache off/on。不按数据集分面。每个点是一个方法。先有 DL20、COVID 各自的数据集级占位均值，再对两集做 1/2。质量和 token 分开平均。没有逐 query 点。

ListK Fig. 4 的图注写 “dominate the Pareto frontier”，红点线是那条前沿，而且线会伸向坐标轴、并不停在点上。Fig. 5(b)(c) 的图注写明是带 \(1/L\) 的线性拟合和二次拟合。这里不拟合，也不把线伸到轴外。

红虚线只连接非支配均值：token 更低、质量更高，至少一个严格。顶点就是这些均值，按 token 从低到高。

| 面板 | 线段 | 顶点（token, 质量） |
|---|---|---|
| Full, Off | 有 | LT (20400, 0.54)，SW (21250, 0.74)，ListK (28350, 0.745) |
| Full, On | 无 | 只有 SW (19100, 0.745) |
| LIMIT 10, Off | 无 | 只有 SW (19500, 0.705) |
| LIMIT 10, On | 有 | SW (18500, 0.705)，Tournament (25250, 0.715)，ListK (29250, 0.720) |

Full Off 的第一段很陡，是因为 LT 只比 SW 少 850 token，Spearman 却低 0.20。没有把点挪开。一个非支配点画不成线段，所以 Full On 和 LIMIT Off 没有红线。这不是漏画。描述性集合，不是拟合，也不是显著。

## E5

通栏八图：DL20 Off、DL20 On、COVID Off、COVID On，上排费用、下排 NDCG@10。面板内部保持原构图：LIMIT 槽等距，不是线性 \(n\)；Full 在断轴后的浅灰带里，不与 LIMIT 500 相连，也不是 \(K{=}510\)。Off 与 On 的费用纵轴仍用原来的两套范围。图内红字横幅和等距说明移到 `tex/fig-e5.tex` 的 caption。

九个 LIMIT 标签在四分之一通栏里横排会贴在一起。标签转了 60°，490 和 500 仍分开。这是宽度逼出来的，槽位和断轴没有改。线宽从旧稿的 1.15 pt 收到原论文 0.33 栏的 0.96 pt。SW 红、LT 蓝未改。格子仍是占位数字，不是 3 个 query 的等权均值。

## 用户决定

- 只写 `paper/round2/experiments/`。不改 `main.tex` 和其他公共入口，不合并 main，不做 E2、表、机制图。
- 质量优先。不把“环境缺命令”当成完成。
- E3 单栏 4×2。预测与实测分成两排。SW / LT / Full / LIMIT 写在 TeX 里，不写进图。
- E4a 单栏，横轴是完整 \((k,h)\)。真实选点后置。合法合成样本不能写成实测。\(n{=}100\) 的 \(k{=}8\) 非法，不得沿用。
- E4b 单栏。去掉背景色带和局部放大，不另做 inset。
- E4c 单栏 2×2，不按数据集分面。两集先各取均值，再等权 1/2。红虚线只连非支配均值。单个非支配点不画线段。
- E5 保持已满意的构图，只做小改。Full 是独立断轴区，不与 LIMIT 连线。合成说明留在 caption，图内不要大红横幅。
- 线宽、点径、配色先对齐原论文印刷尺度，再做有限的可读性调整。不为了好看改数据。
- 只有原样编译后看到具体碰撞，才做局部修改。

## 原线宽、点径、配色、TeX 容器

测量对象是 `paper/tex/fig/panels` 里的原面板 PDF，画布 133.2 pt。内容流：数据折线 1.6 pt，标记路径约 4.8 pt、同色描边 1.0 pt，网格 0.765 pt `#B0B0B0`，坐标框 1.36 pt，刻度宽 0.8 pt、长 2.2 pt，刻度字 9 pt，轴标题 11.05 pt，图例字 12.75 pt。星约 10.2 pt，菱形约 9.49 pt（都是未缩放的面板尺寸）。

从原 PDF 取色：SW `(0.839, 0.153, 0.157)` `#D62728`，LT `(0.122, 0.467, 0.706)` `#1F77B4`，SLT `(0.173, 0.627, 0.173)` `#2CA02C`。其余序列用 Tableau 10，外加 `#CC79A7`。E4c 的红虚线用论文红 `#D62728`。

印刷尺寸 = 面板尺寸 ×（栏宽分数 × 241.1475 / 133.2）。Fig. 8 的分数是 0.25，面板边长 60.29 pt，折线约 0.72 pt。0.33 栏的折线约 0.96 pt。E4a、E4b、E5 用这一档。E3 刻度字从印刷后的约 4.1 pt 提到 4.6 pt，否则 1k/5k/10k 在方框里糊住。字体是 Liberation Serif，数学是 STIX。机器上没有 Times New Roman。

TeX 容器：E3 跟随原 `fig:exp4-topk`（`paper/tex/exp.tex` 已是短入口，容器按 Fig. 8 的单栏、`0.25\columnwidth`、图例在上）。E4a/E4b/E4c 用 `figure` 和 `\columnwidth`。E5 用 `figure*` 和 `\textwidth`。文档类是 `\documentclass[sigconf,nonacm,review]{acmart}` 加 `\usepackage{pvldb}`，与 `paper/tex/main.tex` 相同。`pvldb.sty` 不改栏宽。`subfigure` 来自 TeX Live 的 `texlive-latex-extra`。

## 数据聚合与红线

E3 的数来自 `paper/recovery/e3/e3_layout_data.json`。预测 = 实测 + 3.4。Full 与 LIMIT 被指定成同一组数，所以那两列一样。这不是测出来的 Full/LIMIT 结果。

E4a 的 \(n{=}100\) 用原生成器重算，\((8,1)\to(5,1)\)、\((8,2)\to(5,2)\)。\(n{=}500\) 从 `paper/recovery/e4a/data/e4a_synthetic.json` 逐项抄来。星和菱形的高度都是该配置的实测高度。

E4b 的 \(U,Q\) 来自 `paper/recovery/e4b/e4b_beta.json`，公式 \(U-(1-\beta)Q\)，不乘 \(10^3\)。

E4c：每个源点已经是数据集级占位，代表一份没有存下来的 3-query 均值。再对 DL20 和 COVID 做 1/2，费用和质量分开平均。不是 6 个 query 重算。非支配：token 更低且质量更高，至少一个严格。按 token 排序后只连接这些均值。顶点见上表，也写在 `figures/e4c/e4c-facts.json`。少于两个非支配点就不画线段。

E5 的格子来自 `paper/recovery/e5/data/e5_limit_sweep.csv`。LIMIT 槽等距。Off 是 \(U\)，On-cold 是 \(U-Q\)（\(\beta{=}0\)）。这些格子不是 3-query 均值。

## 编译后改过的碰撞

`tex/preview.tex` 第一次按 Fig. 8 原样排（含 `\hspace{-2.6ex}` 和 `main.tex` 的 `\subfigcapskip=-7pt`）时有三处具体碰撞，只改了这三处：

- 子图题 “SW, Full, predicted” 在 0.25 栏里换行后，相邻题叠在一起。`-2.6ex` 还盖住了前一张面板右侧的 10k。题改成两行短标签（SW, Full / predicted），四张面板改为边对边，不再用负间距。
- 轴标题 \(n\) 的 `labelpad=0.6pt` 压在刻度 5k 上。轴底边改到图高的 0.38，`labelpad` 改成 8 pt。\(n\) 现在在 1k/5k/10k 下面，中间约 5 pt。
- `-7pt` 的子图题间距把题拉进面板，盖住 \(n\)。预览里改成 `1pt`。`main.tex` 没有改。

另外，不强制换页时，浮动队列丢掉了 TREC-COVID \(n{=}100\) 和 E4c，并把 E4b 的题排进页脚。预览在每张单栏图后 `\clearpage`，E4c 留在 E5 前面以便 `figure*` 接上。八张图都在 `tex/preview.pdf` 里。E4a 的刻度 \((4,1)\)、\((4,2)\) 与轴标题的字框大约重叠 1 pt，字形本身仍分开，没有再挪。

## 缺件

- 没有 E3–E5 的正式预测或实测。全部图都是合成样本。合法合成不能当成实测。
- E4a 的真实 \((k,h)\) 展示点仍后置。图上的最低点只对显示子集成立，不是合法域上的 argmin。
- E3 的 Full/LIMIT 同数、E4c 的数据集级占位、E5 的格子都不是 query 级复算。
- E4c 的 Full On 和 LIMIT Off 各只有一个非支配点，没有红线段。
- 预览没有正文，也没有并进 `main.tex`。父方还没有审图，这次编译不是视觉通过。
- 机器上没有 Times New Roman，轴上的字是 Liberation Serif。
