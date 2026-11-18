# Algo1 框架图 checkpoint

只做整体框架。没有改 SW / LT 局部、pointer、LIMIT、实验、伪代码，也没有改 `pvldb.sty`、`acmart.cls` 或任何论文公共 tex。Intro 未制作：它用的不是这 16 个元素，旧稿没有 label，是否入稿未定，不能拿来替换这张主框架。

## 打开过的文件

- `/tmp/recovery-spec/逐图制作说明.md`（0.1 共用合同，图 F-框架八栏）
- `/tmp/recovery-spec/给后续制作者的交接要求.md`（4.2）
- `/tmp/recovery-spec/references/user-originals/fig-F-algo1-v1.png` 与 `.pdf`（482×338 pt）
- `/tmp/recovery-spec/references/user-originals/fig-F-algo1-v2.png` 与 `.pdf`（504.96×210 pt）
- `/tmp/recovery-spec/references/user-originals/fig-F-intro-v2.png`（只看，未画）
- `/tmp/recovery-spec/references/paper-baselines/mech-wiscsort-fig3-dataflow.png`
- `/tmp/recovery-spec/references/source-metadata/figure_data.json`
- `/tmp/recovery-spec/references/source-metadata/revision_v3-README.md`
- `viz/evidence/sources/.../plan.py` 的 `select_parameters`、`estimate_cost`、`resolve_merge_plan`
- `viz/evidence/sources/.../operator.py` 的执行顺序：`base_sort` 之后才 `prepare_merge_plan`
- `viz/tex/vendor/acmart.cls` 与 `pvldb.sty`（只测量，未改）

栏宽是用 vendored class 实测的，不是估计：`sigconf,nonacm` + `pvldb`，`\maketitle` 之后 `\columnwidth=241.14749pt`，`\textwidth=506.295pt`。单栏 `figure` 里 `\linewidth` 就是 241.14749pt，所以 `0.95\linewidth = 229.090pt`。`figure*` 的 `\linewidth = 506.295pt`。pdfinfo 报的是 bp（72/英寸），229.090 TeX pt = 228.234 bp。

## 保留

- 同一 16 个元素：`C1={12,3,16,7}` … `C4={9,13,4,10}`，`R1=(3,7,12,16)` … `R4=(4,9,10,13)`，`Q1=(1,3,5,6,7,12,14,16)`，`Q2=(2,4,8,9,10,11,13,15)`，`Π=1..16`。
- v1 的层次：Phase 1 四个编号胶囊、Pass 1 / Pass 2、空心圆可追踪、插件虚线框、图例。
- v2 的调用语义：红虚线框是一次 listwise 的范围；MergeGroup 是插件，不再编号；最终 `Π` 蓝填充。
- 分组仍是这个例子的 `k=2`。`k` 写在控制线上，不再当作 Pass 自己的标签。

## 改了什么

选参接在 Phase 1 的 run 之后、MergeGroup 之前，和 `operator.py` 的顺序一致。

输入：

- 数据：四条 run 的长度 `|R_i|`，从 `G1`/`G2` 底角进入 `|R_i|` 框，再进入估计接口；测量到的 token profile `(H,L)`。
- 控制：listwise 容量 `m`；demand，Full 或 LIMIT `K`。Full 不是更大的 `K`。

接口里只写已经核对过的选择规则：估计输入 token 最低，平手则 LT、更小的 `k`、更小的 `h`。`finite.py` 未核，图上写明不画公式。

输出是控制线，不是数据流：插件是 SW 或 LT(`h`)，同一个生成器，`h=1` 不是第二种算法；`(k,h)` 进入三个 MergeGroup。这张轨迹的分组是 `k=2`。`h` 没有编一个数，因为这张总图没有展开插件内部，也没有跑估计。

同一条 demand 从接口出来，标成 mode，接到右侧说明：本轨迹是 Full，吐出整条 `Π`；LIMIT `K` 停在前缀。

实线黑箭头是数据，青绿虚线箭头是控制。红虚线只表示调用范围，不是箭头。

## 看图后改的一次

第一稿有两处边不对：右路 run 长度线指到了 profile 框；Pass 2 的数据箭头悬在 `Q1`/`Q2` 中间的空白里。现在两条长度线都停在 `|R_i|` 的上边，`Q1`/`Q2` 的内角分别进入 Pass 2 顶边的左右，控制线进入顶边中点。mode 改从 Pass 1 和 Q 之间的空档向右，再沿右槽进入说明框的右边，不穿过 Q 或 MergeGroup。

## 边

| 边 | 起点 | 终点 | 语义 |
|---|---|---|---|
| D1–D4 | `C_i` 下边 | 对应 ListwiseRank 上边 | 数据，未排序块 |
| D5–D8 | 调用下边 | `G1`/`G2` 上边 | 数据，排好的 run |
| D9–D10 | `G1` 右下角、`G2` 左下角 | `\|R_i\|` 上边 | 数据，run 长度 |
| D11 | `\|R_i\|` 下边 | 估计接口上边 | 数据 |
| D12 | profile 下边 | 估计接口上边 | 数据，`(H,L)` |
| C1 | `m` 下边 | 估计接口上边 | 控制 |
| C2 | demand 下边 | 估计接口上边 | 控制 |
| C3–C4 | 接口下边左右 | 两个 Pass 1 MergeGroup 的内侧 | 控制，`(k,h)` |
| C5 | 接口下边中点 | Pass 2 MergeGroup 上边中点 | 控制，同一组 `(k,h)` |
| C6 | C5 在 Pass 1 与 Q 之间分出 | 右侧说明框的右边 | 控制，mode |
| D13–D14 | Pass 1 MergeGroup 下边 | `Q1`/`Q2` 上边 | 数据 |
| D15–D16 | `Q1` 右下角、`Q2` 左下角 | Pass 2 上边左右 | 数据 |
| D17 | Pass 2 下边 | `Π` 上方 | 数据 |

## 不足

- 按现有单栏 `figure` + `0.95\linewidth`，印刷宽度是 229.09pt。16 个圆和接口文字在这个宽度上小于舒适阅读尺寸。通栏 `figure*` 的 `\linewidth` 是 506.30pt，和 v2 的 505pt、v3 记录的 178mm 同一量级，能读。模板没有改。两种真实尺寸在 `compare-sizes.png`。
- `h` 仍是符号。插件内部不在这张图。
- 估计公式没有画，因为 `finite.py` 不在已核源里。
- mode 线绕到右侧，路线偏长，换来的是不穿框。
- “SW or LT(`h`) / example `k=2`” 靠着中轴控制线，中间有白底，间距仍然紧。
- 图比 v1 高，多出来的是选参带。
- `k=2` 是这张例子的分组，不是一次未运行的估计结果。

## 放回

片段在 `include-snippet.tex`。环境仍是单栏 `figure`，`width=0.95\linewidth`，label 仍是 `fig:exp:semantic_external_merge`。`figure*` 只写在注释里，没有启用。
