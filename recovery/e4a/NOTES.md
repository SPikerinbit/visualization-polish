# E4a Off / On-cold 成本曲线（一次 checkpoint）

只做实验四 a。没有改 4b、4c、其它图、公共 tex 或 `viz/`。没有独立 Layout Supplement。分面数量没有当成已经拍板的决定。

## 打开过什么

- `/tmp/recovery-spec/逐图制作说明.md` 的 E4a 八栏，以及 0.1。0.1 的 16 元素身份是机制图合同，不用于这张成本图。
- `/tmp/recovery-spec/给后续制作者的交接要求.md`
- `/tmp/recovery-spec/references/manifest.md`
- 参考图实际打开：`scatter-lotus-fig4-acc-time.png`、`scatter-lotus-fig6-acc-time.png`、`scatter-palimpzest-fig3-pareto.png`
- 仓库：`paper-experiments.md` 第 6 节、`可视化建议.md` 实验四 a、`viz/evidence/.../plan.py` 的 `max_segment`、`viz/tex/vendor/acmart.cls` 的 sigconf 页边

无用户新 4a 原图。没有把旧 `fig:exp4-full` / `fig:exp4-topk`、`viz/figures/exp4a.pdf` 或 r1–r3 当基线。

从 LOTUS / Palimpzest 只借用：少而大的标记、图例写清每个标记、轴写出量。不借用散点、Pareto 线、美元轴。

## 图上是什么

两条实测曲线：Off = \(U\)，On-cold = \(U-Q\)（\(\beta=0\)）。单位是输入 token，不是美元。

四个角色：Off 预测配置、Off 实测最低、On-cold 预测配置、On-cold 实测最低。颜色表示缓存状态（蓝 Off，橙 On-cold），形状表示角色（空心菱形 = 预测配置，星 = 实测最低）。两点重合时只画一个组合标记（菱形 + 星）。标记的纵坐标取该配置的实测值。预测分数只存在数据里，脚本会拒绝把预测高度画上去。

横轴是配置类别，按 \(k\) 再按 \(h\) 分组。刻度是 \(h\)，组括号是 \(k\)。线只连接这个展示子集，不把没画的合法点插值补上。

合同格子都在图里：9B、两个代表 query 槽、\(n=100/500\)、Full/LIMIT10、SW/LT。各条件一次，没有误差棒。

## 两个布局（都是建议）

- A：每个数据集一张 `figure*`，4 行 × 2 列。行是 SW/LT × \(n\)，列是 Full / LIMIT10。面板宽，\(k\) 标签松。
- B：每个家族一张 `figure*`，2 行 × 4 列。行是 \(n\)，列是数据集 × Full/LIMIT10。面板窄。

同一 \(n\) 的所有面板共用一个 y 范围；\(n=100\) 和 \(n=500\) 各用各的范围。这是建议，不是已确认的对齐方式。

建议 label：`fig:exp4a-layout-a-dl20`、`fig:exp4a-layout-a-trec-covid`、`fig:exp4a-layout-b-sw`、`fig:exp4a-layout-b-lt`。不要占用 `fig:exp4-full` 或 `fig:exp4-topk`。

## 数据

`data/e4a_synthetic.json` 由 `generate_e4a.py` 写出。状态是 synthetic-layout-sample。

展示点 \((k,h)\)：\((2,1),(2,2),(2,4),(4,1),(4,2),(4,3),(8,1),(8,2)\)。在 \(m=20\)、25 个 run 下，SW 合法域 46 点、LT 合法域 101 点，这些展示点对两个家族都合法。\(k>8\) 没有放进这版展示集。

数据集名字是假设：4a 那一段只写「两集各 1 代表 query」，没有点名。DL20 与 TREC-COVID 是实验二和实验五写明的那一对。

On-cold 的整条曲线有一个合成的水平平移，记在 `synthetic_on_level_shift_tokens`，用来避免样本看起来像 Off 的统一折扣。它不是实测缓存节省。预测用的 \(Q\) 与实测 \(Q\) 不是同一组数。

预测配置相对实测最低多出来的 token 在 marker 记录的 `extra_measured_tokens` / `extra_measured_percent`。图上没有印这些百分数。

重跑：`python3 recovery/e4a/generate_e4a.py`

## 178 mm 上看过一次，并改了这三处

PDF 页面宽 178.00 mm。sigconf 文本宽度约 7.0 in（177.8 mm）。

1. 提案 A 的长副标题两边被裁掉。改成一行短副标题。
2. 分离角色上的「+N%」压在菱形或星上，窄面板里还夹在两个标记之间。百分数移出图面，留在 JSON。
3. 纵轴「input tokens ×10³」比面板高度长，字被切掉。轴上改为「tokens ×10³」。等价输入、Off=\(U\)、On-cold=\(U-Q\) 写在图题和说明里。

改完后再看：图例四角色在一行里能分开；组合标记是同色的菱形加星；\(h\) 与 \(k\) 括号分行；页脚没有压住 \(k\)。没有再改一轮。

## 不足

- 没有正式测量。不能拿这张图比较缓存或选参谁更好。
- 展示的 \((k,h)\) 不是完整合法域，清单仍待定。
- 两个数据集的名字、分面排法、是否 `figure*`、label 都还没被确认。
- 多花的 token 没有画在点旁边。178 mm 上画上去会挡住角色标记。
- Off 的共享 Phase 1 账和 On-cold 的整次冷启动没有按真实账本模拟，只是两条独立的 token 序列。
- \(n=100\) 与 \(n=500\) 不在同一 y 范围。
- 配色是这张图自己的建议，没有和别的实验图锁成一套。
- 提案 A 大约 8.6 in 高，加上图题后一张 `figure*` 可能放不进一页文字区。
- 没有编进整篇论文，也没有印刷页。验收不能靠脚本退出码。
