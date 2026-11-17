# LT pointer 局部图（checkpoint）

只做统一 LT 的 pointer 独立局部图。没有改 LT 全局主图、SW、virtual、LIMIT、实验图，也没有把图插进论文。

两案用同一套符号和同一批数字，不是两种算法。

| 方案 | 文件 | 版面 | 实测页盒 |
|---|---|---|---|
| A 前后并排 | `pdf/pointer-scheme-a.pdf` | Build / Refresh 各一行，左 before、右 after | 249.119 × 435.229 pt |
| B 三步展开 | `pdf/pointer-scheme-b.pdf` | 1 耗尽，2 返回 pointer，3 下一刷新 | 249.119 × 617.269 pt |

原稿 `pointer_rule.pdf` 是 249.12 × 177.12 pt。宽度对齐到同一单栏（差 0.001 pt）。高度加高，是为了两位数圆和树边端点不被缩到原稿那种挤法。对照图按同一 dpi 并排，没有把新图缩小去凑原稿高度：`png/compare-scheme-a.png`、`png/compare-scheme-b.png`。

插入片段在 `tikz/insert-fragment.tex`。建议 label `fig:eg:pointer-rule` 是新的，正文里没有这个环境。父代理选定一案后再放进 VLDB 模板。两案不要同时插入。

## 打开过的文件

- `/tmp/recovery-spec/逐图制作说明.md` 的 0.1 共用合同，以及「图 F-Pointer」八栏
- `/tmp/recovery-spec/给后续制作者的交接要求.md` 第 4.5 节
- `/tmp/recovery-spec/references/manifest.md`
- 用户原图：`references/user-originals/fig-F-pointer-v2.png` 与同名 pdf。仓库里的 `算法机制图/第二版/revision_v3/pointer_rule.pdf` SHA-256 与清单一致：`5d429a48381cd61e0fdbd9e600e869af06ea60bc6dea825a5424880ac2ff9ce1`
- `mech-ovc-fig3-pointers.png`。这是 OVC 的 arXiv Fig. 3，不是 EDBT 短文里的图。只借用「两种线各表一种关系」
- `mech-bwtree-fig3-split.png`。只借用「同几何分步、实线物理 / 虚线逻辑分开」。没有抄它的颜色
- `validated_states.json` 的 `pointer` 与 `lt`，`revision_v3/README.md` 的 Pointer rule 读法，`figure_data.json` 的 pointer 字段
- 八个源。pointer 规则只在 `loser_tree.py`：`_replay_validated_segment` 148–183，建树入槽 493–501，`refresh_path` 入槽 539–552，节点字段 35–50。其余七个文件没有另一套 pointer 赋值。没有运行这些源

`pointer_previous/` 未取得，不当作更早的原图。

## 保留

- 同一 16 元素：R1 = 3,7,12,16，R2 = 1,5,6,14，R3、R4 只在页眉标出身份
- Build 的 z = 1,3,5,7，耗尽在 5，h=2，winner [1,3]，loser [5,7]，pointer 赋成右侧孩子
- Refresh 的 z = 5,6,7,14，耗尽在 7，winner [5,6]，loser [7,14]，pointer 从右侧孩子改为左侧孩子
- [12,16] 不参加 Refresh 的 replay；Refresh 之后右侧孩子为空
- 蓝 = 向上送出的 winner，不写入节点；灰 = 存下的 loser；浅色 = 下一截未读
- 粗箭头才是 pointer，细线才是树边。红色只标「计数先到 h」的那一项，不是 ListwiseRank 虚线框
- 独立局部图，不是第三套算法

## 改变，以及原因

- 物理孩子写成 child 0 / child 1，replay 参数写成 slot 0 / slot 1。原稿用 L/R 同时指几何孩子和逻辑槽
- Build 写成 assign，不写成从旧值 L 翻到 R。旧 pointer 是空
- Refresh 写成「返回 child 0，旧值是 child 1」。耗尽不是 flip 的同义词。图例写明返回值可以等于旧值，但 trace 里没有这个例子，所以不画
- 每一行的父、child 0、child 1 用同一套坐标。before / after 可以叠着看。方案 B 用的是同一批树，只是按耗尽 → 返回 → 下一刷新排开
- 原稿中列把 replay 排成另一套不能对齐的格子。这里 replay z 放在同一棵树下方，槽号和计数跟树上的 slot 标签是同一套
- 只加粗发生变化的 pointer。未参加 replay 的孩子用浅边、浅圆

## 空缺（没有编）

- 返回值等于旧 pointer 的例子。规则允许，`validated_states.json` 没有
- Refresh 返回 child 0 之后的下一次 fill。方案 B 第 3 步右侧是空框，不是一棵假树
- 这两例没有短槽，所以没有虚位 `+\infty`
- 3,4,5,6,7,14 在全局 LT 里的逐步比较。那是全局图的范围，json 没给逐步序
- `pointer_previous`

## 验收

几何检查在 `geometry.py`：树边和 pointer 的端点在容器直边上；线段不进入元素圆；pointer 不与树边相交；圆与圆之间留缝。两案都通过。

肉眼看了 340 dpi 的 Build after、Refresh before、Refresh after。第一次渲染时，指向左侧孩子的粗箭头和细树边在孩子顶边附近贴在一起。针对性改了一次：树边改落到顶边内侧，pointer 改落到顶边外侧，箭头改在容器之后再画，让尖端留在边上。改完再看这三处：尖端停在容器顶边，12/16 和 6/14 的圆没有被线穿过，两位数之间有缝。没有做第三次改动。

OVC 的红蓝线没有拿来当配色。Bw-Tree 的分步只用于方案 B 的三步，不表示这是页分裂。
