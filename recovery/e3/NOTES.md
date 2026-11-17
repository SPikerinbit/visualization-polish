# E3 规模扩展组图（只此一张）

页面宽度 178 mm，高度 136 mm。矢量 `e3-scale.pdf`，300 dpi `e3-scale.png`。数据脚本 `make_layout_data.py`，绘图脚本 `plot_e3_scale.py`，表 `e3_layout_data.json`，可 include 片段 `e3-scale.tex`。未改论文源，未编译论文，未合并。

## 没有用户新原图

新实验三没有用户提供的规模曲线原图。参考包清单写明 E3–E5 没有新原图。本目录不是在某一张新原图上改出来的。

## 实际打开

- 附件 `逐图制作说明.md` 图 E3 第 1–8 栏，以及文末表 T-E3-aux（辅助表未定，本轮不做）。
- 附件 `给后续制作者的交接要求.md`、`references/manifest.md`。
- 论文曲线裁剪：`scatter-lotus-fig4-acc-time.png`、`scatter-lotus-fig6-acc-time.png`、`scatter-palimpzest-fig3-pareto.png`。参考包没有一张通用折线论文图（说明第 6 栏），没有另找新论文。
- 旧稿：论文包 `exp.tex` 的 `\label{fig:exp3-ablation}`（单栏 `figure`，图例 `0.65\linewidth`，子图 `0.33\columnwidth`），以及 `fig/panels/exp3/exp3_legend.pdf`、`exp3_dl20_full_tokens.pdf`、`exp3_movies_full_tokens.pdf`、`exp3_dl20_top10_tokens.pdf`。这是旧 RQ2 消融（Movies/DL20 × full/top10 × token/latency/quality），不是新实验三的科学内容。
- 当前检查点里的 `viz/figures/exp3-2x2.pdf` 与 `exp3-row.pdf` 只用来避开昨夜退步，不当基线。

## 保留

- 旧稿图例在面板外、横排、无框、衬线字。本图用 Liberation Serif，三行共享图例放在面板上方。
- 旧稿的线型分层：实线加标记，虚线另作一层。这里虚线只表示预测版式，实线加实心圆只表示实测版式，不沿用 Loser Tree / Segmented Loser Tree 的故事。
- 旧稿面板的细全框、无网格、刻度朝外。纵轴不用科学计数法冒充 token。
- 确认过的五组 SW、五组 LT、1k/5k/10k、Full 与 LIMIT 10、9B 与 DL20 只作为设定名称。同一 \((k,h)\) 在 Full 与 LIMIT 10 用同一颜色。补充点不连进五条线，图内和 caption 都不称 best。

## 改变

- 构图改成 2×2：上排 Full，下排 LIMIT 10，左 SW，右 LT。不再用旧稿 2 行×3 列的 token/latency/quality。
- 横轴是线性的输入规模，刻度 1k、5k、10k。不改成树层数，也不改成等距分档。
- 去掉检查点图里的 tab10、每面板图例、贴在线上的 `sup (...)`、以及看起来像 token 结果的纵轴。
- 五条线用同一斜率，预测是实测脚手架加固定 3.4 个版式单位。高低顺序等于确认清单的顺序，不是排名。
- 补充星是空心黑星，单独标 \((250,2)\)、\((500,2)\)、\((250,1)\)、\((500,1)\)，放在线束上方。
- 图内第一行写明 Synthetic layout only. Not a measured result.

## 看图后改的一次

第一版图例三行贴在一起，LT 标题夹在两行色标中间；曲线几乎水平，面板上半截空着。只改了这一次：图例行距拉开，共同斜率从每千输入 0.4 提到 0.9，纵轴收到 8–82，补充星放到 69。改完再看了整图、图例带、SW 面板、LT 面板和星标近景。178.00 mm × 136.00 mm。标签无重叠，星标文字在坐标框内。没有第二次改。

## 仍不足

- 没有正式测量。数字不能当费用或模型误差。
- 线性还是对数，说明里仍是未定。本图选了线性。
- 纵轴的等价输入刻度、以及要不要拆 Off/On，都未定。本图不拆，单位写成 layout units。
- 补充星没有沿用“与最近一条同家族线同色”。堆叠顺序会伪造最近邻，同色会被读成那条固定曲线上的点。星是独立黑色。
- SW 面板上沿留白，是为了和 LT 补充星共用同一纵轴范围。
- 逐规模 best \((k,h)\) 的辅助表未做。说明里该表是否入稿未定，本任务也不做表。
- `fig:exp3-scale` 只是建议标签。旧 `fig:exp3-ablation` 未改。片段未插入 `exp.tex`。
- 旧实验三是单栏 `figure`。本图按本次指定的双栏 178 mm 写成 `figure*`。单栏还是双栏仍可再定。
- 10k 上的 \((500,2)\) 与 \((500,1)\) 靠右框较近，但没有出框。
- SW 的绿与 LT 的绿同在图例里、分属两行。颜色只区分参数，不编码 \(k\) 或 \(h\) 的大小。
