# SW 滑动窗口机制图（checkpoint）

只做这一张。没有改论文、没有改其他图、没有 merge。编译通过不是视觉合格。

## 打开过的文件

- `/tmp/recovery-spec/给后续制作者的交接要求.md`
- `/tmp/recovery-spec/逐图制作说明.md`（图 F-SW 八栏，以及 0.1 共同合同）
- `/tmp/recovery-spec/references/user-originals/fig-F-sw-v1.pdf` 与 `.png`（482×338 bp）
- `/tmp/recovery-spec/references/user-originals/fig-F-sw-v2.pdf` 与 `.png`（505×153 bp）
- `/tmp/recovery-spec/references/paper-baselines/mech-origami-fig2-mcmerge-steps.png`
- `/tmp/recovery-spec/references/source-metadata/validated_states.json`
- `/tmp/recovery-spec/references/source-metadata/figure_data.json`
- `/tmp/recovery-spec/references/source-metadata/revision_v3-README.md`
- 仓库 `算法机制图/第二版/revision_v3/sd_merge.svg`（v2 填色，不把昨夜交付稿当基线）
- `viz/evidence/sources/.../sliding_window.py` 的 `_compute_safe_prefix` / `_compute_targets`
- 论文 zip 里 `framework.tex` 的 Algorithm `alg:sliding_window_kway_group_merge` 与 `fig:eg:sliding_window`
- `viz/tex/vendor/acmart.cls`，`[sigconf,review]`，`\maketitle` 之后实测栏宽

Origami 只借鉴“同一步数字留在固定格子里”。没有做新文献检索。

## 保留 / 改变

保留 v1：三轮并排、固定槽位、调用序号 1/2/3、`|B|`、`b_i`、一次 `ListwiseRank`、out/keep 分开、保留项回到下一窗、后轮已吐出仍留在带上、底部 `\Pi` 与 `5+5+6=16`、图例。

保留 v2：窗口、吐出、保留、未读与 `\emptyset` 跟 `validated_states.json` 的 `sd` 一致；红虚线只框本轮窗口。

改变：配色按已确认合同，不再用 v1 的“灰=已吐出、空心=待定”。蓝=已吐出，灰=保留，空心细圈=未读，深圈=本轮新读入窗口。窗口框按行分开并留出竖向空隙。`b_i` 与轮次写在同一行，避免压到圆上。

未改论文模板。单栏还是 `figure*` **未定**。

## 状态（伪代码走查，不是在线 ranker）

输入与合同一致。`ListwiseRank` 按示例的数值序。停止规则是论文算法里的 `e_t=b_t` 且 `p_t+b_t<|R_t|`，完成窗口的那一项计入吐出；没有未见项就不停。这与 `sliding_window.py` 里“上游仍有供给才截断”相同。没有跑异步驱动。

`m=8`，四路都活跃，所以每轮 `h=floor(8/4)=2`。`positions` 是该轮开始时的游标。

| 轮 | 游标 | 窗口 | 未读 | 吐出 | 保留 | `|B|` |
|---|---|---|---|---|---|---|
| 1 | 0,0,0,0 | [3,7] [1,5] [2,8] [4,9] | [12,16] [6,14] [11,15] [10,13] | 1–5 | 7,8,9 | 8 |
| 2 | 1,2,1,1 | [7,12] [6,14] [8,11] [9,10] | [16] ∅ [15] [13] | 6–10 | 11,12,14 | 8 |
| 3 | 2,3,2,3 | [12,16] [14] [11,15] [13] | 全空 | 11–16 | 空 | 6 |

`b=(2,2,2,2)`、`(2,2,2,2)`、`(2,1,2,1)`。第 3 轮沿用 v1 的写法 `b_2=b_4=1`，另外两路的长度由图上的窗口可见。装配顺序与正文例子一致：第一轮 `B={3,7,1,5,2,8,4,9}`，第二轮 `B={7,12,6,14,8,11,9,10}`。

## 箭头

宽图（主稿）每条保留箭头：下划线只在该轮 keep 圆下方，经列间空档上行，在行间空隙里水平走到目标，箭头向下停在下一轮该元素的窗口框上沿外侧。几何检查要求箭尖落在窗口框边上，且最近的圆就是该窗口元素。

| 起点（保留） | 终点（下一轮窗口） |
|---|---|
| 第 1 轮 7, 8, 9 | 第 2 轮 R1 的 7、R3 的 8、R4 的 9 |
| 第 2 轮 11, 12, 14 | 第 3 轮 R3 的 11、R1 的 12、R2 的 14 |
| 第 3 轮无保留 | 无箭头 |

另外每列有一条从窗口块下方指向调用序号的短箭头，不进入圆。

窄图（对照）太窄，不画三条穿行线。保留组一条边线箭头，终点是下一轮窗口右侧的竖括，不进入圆、不指向未读。灰圆仍标出重新进入的元素。这是对照，不是主稿。

坐标在 `arrow-endpoints-wide.json` 与 `arrow-endpoints-stack.json`。

## 尺寸

- 主稿 `sw-wide.pdf`：177.94×115.03 mm，对齐 `\textwidth`（178 mm）。
- 对照 `sw-stack.pdf`：80.52×213.48 mm。栏高约 220 mm，加上 caption 可能放不下。
- `sw-column-scaled.pdf`：把主稿缩到 80.54 mm（当前 `figure` + `0.95\linewidth`）。字号约变为 45%，不可读。只作尺寸证据。

## 仍不足

- 宽图行间的水平线段较长，虽然不进圆，仍占视线。
- 窄图箭头指到窗口侧的括，不逐个点到 7/8/9。
- 窄图高度对单栏加 caption 偏紧。
- 没有在线跑 ranker。超出本例三轮的调度（evidence、shuffle）未画，也不该画进这张示例。
- 本文件不声明视觉合格。
