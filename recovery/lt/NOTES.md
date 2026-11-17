# LT(h) 主机制图 checkpoint

只做统一 LT(h) 这一张主图。没有 pointer 局部图，没有 SW、框架、实验、伪代码，也没有改论文源。

## 打开过的文件

- `/tmp/recovery-spec/逐图制作说明.md`（图 F-LT 八栏，以及 0.1 共同合同）
- `/tmp/recovery-spec/给后续制作者的交接要求.md`（第 4.4 节）
- `/tmp/recovery-spec/references/source-metadata/validated_states.json`
- `/tmp/recovery-spec/references/source-metadata/figure_data.json`
- `/tmp/recovery-spec/references/source-metadata/revision_v3-README.md`
- `/tmp/recovery-spec/references/user-originals/fig-F-lt-unified-v2.pdf` 与 `.png`（主逻辑基线，版心 504.96×187.92 pt）
- `/tmp/recovery-spec/references/user-originals/fig-F-lt-segmented-v1.pdf` 与 `.png`（只借层次，不沿用它的拆算法和另一套数字）
- `/tmp/recovery-spec/references/user-originals/fig-F-lt-binary-v1.png`（只借路径加粗和调用号）
- `/tmp/recovery-spec/references/paper-baselines/mech-adaptive-fig3-tournament.png`
- 仓库里的 `算法机制图/第二版/revision_v3/lt_unified.svg`（核对 v2 的节点坐标和箭头旋转）
- `viz/evidence/sources/sema_prototype/physical_operator/orderby/merge/loser_tree/loser_tree.py`
- 同目录的 `plan.py`（`init_plan`）、`_common.py`（`LT_INIT` / `LT_PATH_REFRESH`）

## 源码里这张图用到的事实

`loser_tree.py` 的内部节点只存 `loser` 和 `pointer`。胜段是一次 replay 的返回值，到根之后吐出，不写进节点。

`refresh_path`：从根沿 pointer 走到叶子，`fill_leaf` 取下一段，窗口是这段加上路径上每个节点的 loser，然后 **一次** `rank_structural`（`ListwiseRank`）。随后自底向上 `install_replay`，用的是这一次的 rank map，不再发调用。

本例（json `lt`，k=4，h=2）：

| | 根 | 左内部 | 右内部 | 叶上未读 |
|---|---|---|---|---|
| (a) 已吐出 [1,2] 之后 | loser [3,4]，pointer 左 | loser [5,7]，pointer 右（R2） | loser [8,9]，pointer 左（R3） | R1 12,16；R2 6,14；R3 11,15；R4 10,13 |
| (b) 这一次调用的成员 | [3,4] | [5,7] | 不进入 | 新装入的是 R2 的 [6,14]。ρ=[3,4,5,6,7,14] |
| (c) 调用返回之后 | loser [5,6]，pointer 右 | loser [7,14]，pointer 左（R1） | 与 (a) 相同 | R2 无未读，记 ∅ |

json 里叶子的 `winner` 是上一次填进树的那一段（例如 R2 在 (c) 仍记 [6,14]，`next=4`）。图上叶子画的是未读尾，和 v2 一样，不把这段再画一份在叶子里。

根 pointer 与 json 一致：刷新前指向左孩子，刷新后指向右孩子。v2 SVG 里根上那条浅灰向上的线是吐出方向，不是 pointer。

没有把初始化的那次 ListwiseRank 画出来。(a) 已经是 [1,2] 吐出之后。也没有画 3,4,5,6,7,14 的逐步比较；那是 pointer 图的事。这一例左节点的 pointer 从右变到左、根从左变到右，是这次 replay 的返回值，不写成“耗尽就翻转”。

## 保留

- v2 的三栏，以及它的节点中心（根 285,217，左 155,340，右 415,340，四叶 90/220/350/480,477）。三栏平移 0 / 565 / 1130，(a) 和 (c) 可以叠合。
- 同一 16 个元素，k=4，h=2。右子树数字不动。R2 在 (c) 为 ∅。
- 蓝底是已经进入 Π 的胜段。空心是未读。红虚线是一次 ListwiseRank。
- v1 的调用号、加粗刷新路径、未参与的边用更浅的线、run 标签。
- Adaptive Fig. 3 的读法：败者留在节点，胜者另用一条到容器边缘为止的箭头往上走。拓扑不挪。

## 相对 v2 改了什么

- 树边停在段容器边上，不再从圆心穿到圆心。
- pointer 是弯出树边的黑箭头，头部落在被指孩子的容器边上。刷新前：根→左，左→R2，右→R3。刷新后：根→右，左→R1，右→R3。
- 向上的蓝箭头只表示胜段离开根、进入 Π，旁边写 “winner to Π”。它不起于 [3,4] 的内部，也不使用 pointer 的线型。
- (b) 用一个虚线区域包住 [3,4]、[5,7]、[6,14]，配一个红色调用号 1 和 ρ 的六个数。右子树、R1、R3、R4 在区域外。
- 数字改为深色字、白底。图例小样用小圆角，避免大圆角把小矩形画成叉。

## 逐边

三栏的六条树边都停在父子容器边上。(b) 里根–左、左–R2 加粗，其余仍是浅线。

pointer 的头尾都在容器外沿，不进胶囊：

- (a)(b) 根指向左内部；左内部指向 R2；右内部指向 R3。
- (c) 根指向右内部；左内部指向 R1；右内部仍指向 R3。
- (a)(c) 的蓝箭头从根容器上沿到已吐出胶囊的下沿。
- (b) 没有这条蓝箭头。吐出发生在调用返回之后，由 (b) 到 (c) 的栏间箭头接上。
- 栏间两支浅箭头只表示 (a)→(b)→(c)，端点在两树之间的空档。

## 交付文件

- `lt-h-main.tex`：TikZ 源，由 `build_figure.py` 写出。
- `lt-h-main.pdf`：504.95×187.92 pt，与 v2 原 PDF 同版心。
- `lt-h-main.png`：485 dpi，3402×1266。
- `compare-v2.png`：原 PDF 与新 PDF 以同一 dpi 光栅化后上下排列。
- `insert.tex`：建议用 `figure*`、`width=\textwidth`。没有改模板，也没有插进论文。

## 还没解决

- (b) 里加粗路径和 pointer 已经分开（直边 / 弯箭），但这两条线仍然是全图最密的地方。
- 虚线在 R1 右侧留的缝最窄，没有压到 [12,16]，但余量不大。
- 节点 replay 的槽位顺序没有画。不能从这张图读出“为什么这次返回的是另一个孩子”。
- 正文符号表里的 ρ 目前写成 rank position。这张图沿 v2 和制作说明，ρ 是这一次调用的输入列表。插入论文时要先统一这个符号。
- 单栏 `0.95\columnwidth` 会把 7.5 pt 的数字缩到大约 3.4 pt。是否改成 `figure*` 要父验收时决定。旧的 segmented 图环境也还在，本 checkpoint 不删。
