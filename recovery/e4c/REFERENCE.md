# E4c 质量–费用散点 checkpoint

只做实验四 c。不改 `viz/` 公共图、不并进论文、不编译独立展示 PDF。数值是布局检验，不是测量结果。

## 打开过的文件

- `/tmp/recovery-spec/逐图制作说明.md`（图 E4c 八栏）
- `/tmp/recovery-spec/给后续制作者的交接要求.md`
- `/tmp/recovery-spec/references/manifest.md`
- `/tmp/recovery-spec/references/paper-baselines/scatter-palimpzest-fig3-pareto.png`
- `/tmp/recovery-spec/references/paper-baselines/scatter-lotus-fig4-acc-time.png`
- `/tmp/recovery-spec/references/paper-baselines/scatter-lotus-fig6-acc-time.png`
- 仓库 `paper-experiments.md` 第 6 节实验四 c、`可视化建议.md` 实验四 c、`doc/最终可视化决策.md` 中 Off/On 共用轴限那一句

无用户 4c 原图。`viz/pipeline/render_exp.py` 里的旧散点不是原图，不拿来当基线。

## 这两张附图实际是什么

Palimpzest Fig. 3 是计划搜索：黑菱形 naive plan、绿圆优化 plan，橙虚线是 Pareto frontier，caption 写 bottom-right 更好且计划落在 frontier 上。那是计划 Pareto，不是十个算法的均值。

LOTUS Fig. 4 和 Fig. 6 是同一程序在不同精度/召回目标下的参数扫描：红圆 proxy、绿圆 oracle、蓝星是一组 γ 目标。星不是十个算法的均值，也没有 Off/On 成对。

没有与「十算法各一个均值、Off/On 轴限一致、无小点」同口径的先例。下面只借鉴形和留白，不把它们写成先例。

## 保留

- Palimpzest：大实心标记、框起来的坐标、浅网格、两侧面板都印完整刻度数字、标签离开点时用短引线，引线停在点外。
- LOTUS Fig. 4：点少、图例用标记样本而不是再画一条线。
- LOTUS Fig. 6：点在框里铺开。Fig. 4 下半截空着，不学。
- 合同：每方法每面板一个等权均值；Full 用 Spearman，LIMIT 10 用 NDCG@10，两张图；Off 与 On-cold 的轴限由该图全部均值计算，四块面板同一套刻度；色和形跨面板、跨两版一致；十方法按 E1 顺序，无第三家族 SLT。

## 不拿过来的

- Pareto 虚线和 “bottom-right is better / on the frontier”。
- 把方法收成「baseline 菱形 / 优化圆点」两类。
- LOTUS 的星形参数云，以及图内图例压住数据。十个方法的图例放在轴外。
- 美元轴、runtime 轴。横轴是 β=0、输出权重 1 的等价 token，不是金额。
- `可视化建议.md` 里「再画轻量逐 query 点」。八栏和本任务已禁止 per-query 小点。

## 不足（未锁定，父审决定）

- 无用户原图，不能做同尺寸并排。
- Off | On-cold 为左右列、DL20 | COVID 为上下行，是本 checkpoint 的排法，八栏写明排列未定。
- 编号+图例，和短名直接标注，两版都交，不代选。
- 刻度用绝对 token，不用 ×10³。八栏说量纲未定时先写 token。
- `fig:exp4c-quality-cost` 未插入论文。`tex/exp4c.tex` 只是可 `\input` 的片段。
- 模拟点铺满共享轴，是为了检验空图和放大，不是效应大小。

## 一次印刷尺寸修订

在 178 mm、300 dpi 下看了四张 PNG。刻度已是完整数字（token 20000–50000，质量两位小数），四块面板一致；编号和短名都在点外；SetH、Lotus 的短引线停在自己的点上。两处要改：

- 合成说明和 “DL20, Off / On-cold” 标题叠在一行上。顶边距从 0.30 in 加到 0.50 in，说明单独占上面一行。
- LT 用 matplotlib 的 `8`，图里是八边形，图例缩成圆，和 Pointwise 的圆分不清。改成左三角 `<`，图例标记放到 7.6 pt，和图内一致。

没有改轴限、色板、模拟坐标或再出第三版。改完只复查了标题带、图例和 LT 附近：说明与标题分开，10 号在左三角外，图例 10 也是左三角。
