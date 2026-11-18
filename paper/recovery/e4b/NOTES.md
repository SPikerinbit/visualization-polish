# 图 E4b checkpoint

只做实验四 b 的五条 β 曲线。未改 `viz/`、正文或其它图。未并入论文，未编译独立展示 PDF。

## 打开的文件

- `/tmp/recovery-spec/逐图制作说明.md` 图 E4b 八栏
- `/tmp/recovery-spec/给后续制作者的交接要求.md`
- `/tmp/recovery-spec/references/manifest.md`
- 仓库 `paper-experiments.md` 第 4b 节、`可视化建议.md` 实验四 b
- 实际打开的论文裁剪：
  - `/tmp/recovery-spec/references/paper-baselines/scatter-lotus-fig4-acc-time.png`
  - `/tmp/recovery-spec/references/paper-baselines/scatter-lotus-fig6-acc-time.png`
  - `/tmp/recovery-spec/references/paper-baselines/scatter-palimpzest-fig3-pareto.png`
- 无用户 4b 原图。规格写明不要用 4c 散点指导 4b，这三张只用来核对“能借鉴什么、不能抄什么”。
- 另看了仓库里已有的 `viz/figures/exp4b.pdf`，只为确认昨夜的失败（右栏把 (4,1) 和 (4,3) 跳点连成一条，角色不进图例，合成字样只写在轴名里）。那张图不是基线，本目录没有在它上面改。

## 借鉴

- 角色用形状、系列用颜色：Palimpzest 用菱形和圆点区分角色，而不是再加一套颜色。本图沿用这个分工，预测是空心菱形，实测是星，两者落在同一配置时星套在菱形上。没有画他们的 Pareto 虚线。
- 图例短、符号在 178 mm 上能认：LOTUS 的点少而大。本图一行图例，五条线加三个角色，角色图例用墨色，不用十种颜色。

## 不足

- 没有同口径先例：五条 β、类别 (k, h)、两个最优角色、局部放大。散点图不能当构图模板。
- 没有用户原图可并排。对照的是八栏语义，不是旧 `fig:exp4-full`。
- 横轴顺序规格仍未定。本样本按 k 再按 h 排列，并在说明里标成版式选择。
- 局部放大用右栏加框和两条连线，不用盖住数据的 inset。规格把 inset 还是第二栏留成未定，这是待同意的版式，不是已锁定构图。
- 建议 label `fig:exp4b-beta`，未写入正文，不占用 `fig:exp4-full`。
- U、Q 和预测配置都是编造的。预测 (k, h) 没有用这组 Q 回代。不能从曲线形状读出“最优随 β 移动”或“预测是否准”的结论。
- 合同里的 β = 0.1 和 0.9 只记在数据文件里，主图不画。

## 图上读到的标签

178.00 mm × 79.00 mm 矢量 PDF。合成披露只写在 `e4b-beta.tex` caption，图内无海报横幅。文字层里的标签是：

- 图例：β = 0，β = 0.25，β = 0.5，β = 0.75，β = 1，predicted，measured，both roles
- 主轴刻度：(2, 1) (2, 2) (4, 1) (4, 2) (4, 3) (8, 1) (8, 2)，以及 60 到 160
- 纵轴：equivalent input tokens, U−(1−β)Q
- 横轴名：configuration (k, h)
- 右栏同一字符串：(4, 3) (8, 1) (8, 2)，纵轴 70 到 120

打开 PNG 后核对：右栏框的左缘在 (4, 2) 与 (4, 3) 之间，不压住 (4, 2) 的重合标记；连线接到右栏上下角，不穿过 70–120 的数字；图例不进绘图区。β 的小数都带前导 0。
