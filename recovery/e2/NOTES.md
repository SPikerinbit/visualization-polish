# E2 预测/实测双曲面 — 这一轮只做这一张

基于 `f2d4cfa`。新文件只在 `recovery/e2/`。没有改 `viz/`，没有动 `main`，没有编 Layout Supplement，没有把图写进论文 TeX。

## 打开过的文件

- `recovery-spec/逐图制作说明.md` 图 E2 的 8 栏
- `recovery-spec/给后续制作者的交接要求.md`（含 4.1）
- `references/user-originals/fig-E2-cost-surface-reference.png`（已看图）
- `references/paper-baselines/3d-hintqpt-fig2-surfaces.png`（已看图）
- `references/paper-baselines/3d-picasso-fig1-cost.png`（已看图）
- 仓库 `实验结果可视化/可参考：实验二3D/plot_surface.py` 与 `compute_surface.py`
- `viz/evidence/.../plan.py` 的 `max_segment`（只读，用来数合法域）

## 保留

- 同一套 3D 轴、正交相机 `elev=26`、`azim=-54`。蓝 `#087F9B` 实面，橙 `#DA821E` 网面。
- 两层三角形放进**同一个** `Poly3DCollection`，按平均深度一起排序。
- 格子至少 3 个实点才剖分；缺角不补点。没进三角形的相邻边仍然描出来，空洞边不消失。
- 高处有一块与主带不相连的碎面（合成缺口，用来让这条规则看得见）。
- 浅色坐标框，面是主体。z 轴上有刻度 120 / 170 / 220 / 270，单位是千 token。
- 顶点上仍有点：蓝实心、橙空心。

## 相对原脚本改了什么，以及为什么

- 预测最优点的菱形画在该 `(k,h)` 的**实测**高度上。`plot_surface.py` 把菱形放在预测高度，和已确认规则冲突，这一处不沿用。
- 两个角色是同一个配置时，只在那个实测高度画一个组合符号（橙菱形底下叠蓝星）。不画第二高度，也不画连接两种高度的竖线。
- 版式是 PVLDB `figure*` 的 7.0 in（178 mm），不是脚本的 13.6×8.7 in。组图轴题缩短为 `Tokens (1k)`、`Segment h`，因为全称在小面板上被裁掉。单面板英雄图仍用全称。
- 海报尺寸上的面透明度 0.55 / 0.22 缩到 178 mm 后只剩一排点。自查后蓝面改为 0.68、橙面 0.34，橙边加粗，顶点缩小。颜色和“蓝面 + 橙网”没有换。
- 数据是公式场，不是 vLLM，也不是 `finite.py`（该文件未取得，没有调用）。图眉写明 not experimental results。没有误差、regret、SAME MINIMUM 这类结果句。
- 合法域按合同计数：LT 101（`k=2..25`，`h≤max_segment`），SW 46（`k=2..20`，`h≤m/k`）。不是昨夜 `k≤8, h≤5` 的稀疏网格，也不是旧脚本那 50 点。
- 2×2 与 2×3 都是未确认的布局小样。2×2 是同一 slot 的 SW/LT × Full/LIMIT10。2×3 是 LT 的三个 slot × Full/LIMIT10。面板 (b)/(a) 与英雄图是同一张面。

## 自查（178 mm 宽的 PNG，不是脚本 exit 0）

第一稿：图例压住面板标题；顶点盖住三角面，看起来像点云。改了面透明度、点大小、图例改成两行并下移坐标区、小面板 h 轴改短标签。复查后标题、图例五项、z 刻度 120/170/220/270、k 刻度 2/8/14/20/25、h 刻度 1/4/7/10 都能读。英雄图 y 轴 “Segment length h” 完整，但离页脚很近。

## 剩余不足（父审，不在这轮填）

- 没有 `surface_data.json`。高度不能当成实验结果，也不能用来比较方法。
- 示意场随 h 升高，所以实测最低点都落在 h=1。这是公式的形状，不是 LT/SW 的结论。
- 2×2 把 SW 和 LT 放在同一套 k/h/z 范围里。SW 的面比 LT 矮、短，格子里显得空。要不要分家族给轴，未确认。
- Full 模式的 `select_parameters` 会把 SW 的 h 收成 None。这里画的是合同里数出来的 46 点固定域，不是那次收起来的搜索。
- 组合符号的样式是提案。数据集用了 DL20、模型只用了已写明的 9B；COVID、第二个模型、哪个布局进正文，都没定。
- matplotlib 的透明面深度排序仍可能有个别三角形前后不对。没有换成另一套渲染器。
- 未插入论文。旧 `fig:exp2-k` 不是这张图，不要覆盖。
