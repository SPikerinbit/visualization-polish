# 下一 bot 入口（本轮版式验收完成，有例外；已并入 main）

全部远端分支第一次同时成为祖先的提交是 `01c91122897d636b77d78b8fe046e0882bce19a4`。它之上的文档提交只改 `doc/round2/`。版式工程仍是 `060ef6d951ff6471f4dcbb39aa4c449c1d131425`，文档验收仍是它的后继 `d6c4ef1ce7094437231b18f38c738f890ea20a0f`。这两个提交都是 `main` 的祖先。PDF SHA256 仍是 `05cece898d313acdb41c272ec2ecf031ab1532c098685f3438d428471a3cde0a`。合并记录见 `MERGE-TO-MAIN.md`。

版式验收对象是 `060ef6d951ff6471f4dcbb39aa4c449c1d131425`。PDF SHA256 `05cece898d313acdb41c272ec2ecf031ab1532c098685f3438d428471a3cde0a`。记录这次结论的文档提交是该提交的后继，只改 `doc/round2/`，不代替 `060ef6d`，也不改 PDF。

本轮是有例外的版式验收完成，不是科研验收，也不是 TeX Live 2026 通过。验收原文：`qa/FINAL-ACCEPTANCE.md`。

四路：机制 `c959d22b0eeffaeb78f345b320faaa849164c1a6`（不要 `bed819cd`）；表格 `b12cd37113919d32d15a596b0d7e0913cd1c4ec4`；E2 `05f921f20c634dbb4d6e05eb5f4003d17f354183`；折线 `22b432ca01054da271366518d5ba6684795b1b20`。入口 `paper/round2/integration/main.tex`。复现 `cd paper/round2/integration && ./build.sh`。本机 TeX Live 2023。

未闭合，不能写成通过：全部合成；Table 2 公式与 Expect 未核，Setwise 缺式；原 3D k-sweep TeX 缺失；E3 刻度约 4.6pt、图例 5pt；Qwen3.8 对 Qwen3.5 的部署 manifest 未核。



- 已纳入四路：机制 `c959d22b0eeffaeb78f345b320faaa849164c1a6`（不要 `bed819cd`）；表格 `b12cd37113919d32d15a596b0d7e0913cd1c4ec4`；E2 `05f921f20c634dbb4d6e05eb5f4003d17f354183`；折线 `22b432ca01054da271366518d5ba6684795b1b20`。
- 模板：`paper/round2/integration/main.tex`。复现 `paper/round2/integration/build.sh`。无标题页。没有逐图 clearpage；只有比通栏下整栏还高的盒子才换页。
- 父已读的 9 页版式就是 `060ef6d951ff6471f4dcbb39aa4c449c1d131425`。十页审计 `qa/history/FINAL-AUDIT-f55de18.md` 只是否认证碰撞的历史。分页过程见 `qa/PAGINATION-CLOSEOUT.md`。PR19，未 merge `main`。
- E2 例外：合成；原 3D k-sweep TeX 仍缺失；exp5-m 是二维参照。主 12 图版式可以沿用，不要重画，也不要说“原 3D 只换图”已完全满足。
- 废弃 PNG：131758 bytes、SHA256 `5b0a4740e0687377f2021a0d04945566a19330fdbb73c67eaf99d5a832034277`。正确主 PNG 是 162298 bytes、`cddf9a1a1a4fd305cb5971ecb4485b2cbc4028d61293feb968f8aacfff99675f`。
- 4.1pt 是 SW/LT 单栏问题，不是 Framework。
- 真实数据仍后置。历史型号 Qwen3.8-27B 对表现行 Qwen3.5-27B，等部署 manifest。

下面是 14:30 种子原文，已归档，**不是现行状态**。种子里的“未纳入 / 待最终查询 / 待补”不要执行。现行身份以上面的四路 SHA、`qa/PAGINATION-CLOSEOUT.md` 和 `STAGING-HEADS.md` 为准。科学例外仍然成立：合成、公式未核、原 3D TeX 缺失、TeX Live 2023 不是 2026。


# NEXT-BOT-HANDOFF-SEED

交接种子更新：2026-11-18（Asia/Shanghai），以**14:30四路恢复**状态为快照。本文件须由最终整合代理补入真实branch/HEAD/源包/PDF/复现与终验记录后，才成为最终交接。**当前不是final，也不声称commit/push已完成。**

## 1. 接手先读与当前目标

1. `最新用户决策.md`：现行用户要求，失效历史独立列出，不能拿旧预算/待授权状态挡住已授权工作。
2. `实现基线与来源.md`：原图、原TeX、原脚本、真实尺度、指标/合法域及缺口；区别目标仓库相对路径与本机绝对路径。
3. `决策覆盖矩阵.tsv`：逐条需求映射和终验状态；未最终QA不得改成pass。
4. 当前真实目标：收完正在返修的四路，完成本轮验收、无正文VLDB整合、完整源与决策commit/push、交给下一bot。**接手后优先真实数据接入与重算，不重新向用户征求已确认视觉设计**。
5. Fast=false，无周额度上限，按任务选合适模型/思考；避免无效循环。当前执行代理只写本地四个seed文件，未动仓库/CloudAgent，最终提交与PDF整合由主代理下一步cloud执行。

## 2. 当前四路/PR/写入边界

来源：主代理14:30恢复说明及已有工作记录；不是本次新查远端状态。全部分支名、新HEAD、最新产物hash仍须整合者从真实PR补齐。

| 任务 | Cloud ID | PR | 独占仓库相对目录 | branch/最新HEAD | 当前状态 |
|---|---|---|---|---|---|
| 机制图 | bc-cedcb24f-973e-56d2-8c47-76ee635d6f22 | https://github.com/SPikerinbit/visualization-polish/pull/16 | `paper/round2/mechanisms/` | `c959d22b0eeffaeb78f345b320faaa849164c1a6` | 已纳入壳。不用 `bed819cd`。4.1pt 是 SW/LT，不是 Framework |
| E2 | bc-14b89998-426a-520b-96b9-13239d2c5c87 | https://github.com/SPikerinbit/visualization-polish/pull/15 | `paper/round2/e2/` | `05f921f20c634dbb4d6e05eb5f4003d17f354183` | 已纳入主 12。原 3D TeX 仍缺失 |
| 表格/伪代码 | bc-fb22a563-9ef7-51ea-9ebf-664ef76e8dad | https://github.com/SPikerinbit/visualization-polish/pull/18 | `paper/round2/tables-pseudocode/` | `b12cd37113919d32d15a596b0d7e0913cd1c4ec4` | 已纳入。公式未核 |
| 折线/散点 | bc-6a4aa676-95d6-5dca-b11a-2c589c1e436b | https://github.com/SPikerinbit/visualization-polish/pull/17 | `paper/round2/experiments/` | `22b432ca01054da271366518d5ba6684795b1b20` | 已纳入五段图。不用 preview。小字例外仍在 |

- 机制图的旧wrapper是PR13：`https://github.com/SPikerinbit/visualization-polish/pull/13`。不得把旧wrapper当PR16新HEAD，最终核实际依赖/需要的包装文件，不盲目重复合并。
- 旧PR1及旧review-round*/paper-integration-review*属于历史失败或被否定交付；不作为最终视觉批准。其他旧专项PR只在具体来源需要时引用，不能顺手将旧分支整合覆盖新决策。
- 四路初始基线记录为`archive2d05b2de`（历史短标识，需最终解析完整commit）；不是当前整合HEAD。
- PR15已知首稿commit `702e7d8852fafd32f3842ecd546186996903ab02`是**未通过首稿**，只供历史追踪，不可当最新验收对象。
- 上游Sema源码快照commit `0d96d0bf116e52f1664ae2539446f05921f5e947`不是本次visualization-polish源提交，也不证明部署/正式数据匹配。

## 3. 真实时间线与状态诚信

- 11:04已取消旧周用量上限，保留Fast关闭；随后四路实际启动。
- 约11:50已收到表格伪代码首稿并审阅，但首稿存在硬阻塞。
- **11:50–14:27实际停滞**，不能写“持续运行/一直返修”。
- 14:27用户明确要求继续完成验收、commit/push决策和基线并交接；14:30四路才真正恢复。
- 不能把提交任务、收到旧报告、测试通过、恢复执行分别偷换成“完成返修/终验/已push”。

## 4. 已验范围与尚未验范围

### 本地已读的旧审核证据（仍有效地描述其snapshot，不是新稿通过）

- `/workspace/paper-materials/round2-tables-review/AUDIT.md`
  - 已核两张横向E1、每模型13列、12套聚合与存储证据一致、synthetic披露；Table2来源分组结构可准入。
  - 不代表真实数据统计完成，不代表所有整数不并列或最终物理尺寸通过。
  - 旧阻塞：9B Full SW/LT latency向量全等，均9缺10；Table1caption删准备缺口；Replay返回w但调用方解包w,l,p；显式LIMIT且K缺省未定义。
  - Table2公式unchecked/Setwise缺式、P(k)/mu_sw未定义，不能从“分组好看”升级为公式正确。
- `/workspace/paper-materials/round2-e2-independent-audit/recheck/audit/RECHECK-BRIEF.md`
  - 已核旧修订副本2页10/12图、PDF/PNG一致、完整刻度bbox、旧裁字问题修复。
  - 尚不能最终整合：k/h轴义缺失、3D面板内部上下空白约37%、同环境2D参照因hspace/换行改变导致面板重叠遮挡。
  - 所报面积高近似不能验为正确同容器对照；旧bbox函数未计完整矢量绘图。
  - CropBox必须正确观察，pdftoppm不加-cropbox呈现MediaBox整页不能误报新稿多空页。

### 14:30恢复后的新稿

四路均**待新产物+新HEAD核验**。本seed没有拿到新的最终PDF/source，未编译、未重新画图、未新查远端。不要复用旧报告“已修”句子给新稿打pass，也不要误把旧报告未通过当成新稿必然未修。

## 5. 返修闭环的硬检查

1. **Table1**：与批准完整源比较表体、caption、准备缺口文字；不是只比较tabular。冻结参考`paper-integration-review6/paper/recovery/tables/tex/tab-datasets.tex`，恢复DL22/Robust04缺口提示。
2. **E1**：保持两表/13列/权重/tie-break；可以改明确标synthetic的展示fixture输入，不改真实数据或规则强排；全等原证据测试必须保留，验证不会制造差异/显著性。std后备键必须有合法重复数，缺n不得偷用。
3. **伪代码**：Replay接口、存储副作用与调用方一致；无K、K0、耗尽、Full/LIMIT路径边界有定义；内容凝练且核心可见。
4. **机制图**：SW/LT单栏约4.1pt微字必须修复；Framework字在最终通栏尺寸可读，反向pull方向/停止K正确。不要借返修重开批准构图。
5. **E2**：公共TeX或紧凑caption明确k/h/成本轴方向与单位，内部留白压缩但不剪刻度；原2D参照恢复字节布局/换行语义不遮框；统一宽度用完整内容bbox；3D原TeX仍未定位须披露。
6. **E3–E5/E4各图**：工件实际存在、能编译、符合最新栏宽/子图数量，白底浅灰格、图例与外置标签正确；E4c红线重算有义，E5只微调不重构。
7. **整合**：无正文，仅必要caption；不强制每图一页制造大片空白；删除E4验证表、独立LIMIT图及实际引用；无SLT第三家族、旧错误标签/占位页；Table1不被统一样式误改。

## 6. 重现命令（旧包已记录；本seed未执行）

以下是接手定位入口，不是新HEAD通过证明。实际环境须为TeX Live 2026/pdfLaTeX，所有命令从最终仓库根开始；执行结果/版本/退出码由整合者补记。

### 表格/伪代码：旧包README

```bash
cd paper/round2/tables-pseudocode
./build.sh
# 旧README：运行src/tests，重生成tex/generated，编译tex/preview.tex
# 输出build/preview.pdf、build/page-*.png
# TEXINPUTS要求paper/tex/vendor的绝对路径，由脚本设置
```

单独统计入口（旧STATS记载，需新HEAD核查）：
```bash
PYTHONPATH=src python3 -m unittest discover -s src/tests
PYTHONPATH=src python3 -m emit
```

### E2：旧包README

```bash
cd paper/round2/e2
python3 plot_surfaces.py
cd tex
latexmk -pdf -interaction=nonstopmode preview-main.tex
```

预期旧入口产物：`out/e2-layout-2x5.{pdf,png}`、`out/e2-layout-2x6.{pdf,png}`、`out/panels/p01.pdf`…`p12.pdf`、`out/e2-vldb-preview.pdf`。若脚本自动编译，不能再把重复编译算作额外独立验证。

观察CropBox示例（不改变图）：
```bash
pdftoppm -cropbox -png -r 160 out/e2-vldb-preview.pdf /tmp/e2-crop
```

### 机制图、折线散点与最终整合

- `paper/round2/mechanisms/`：**入口/依赖/命令待PR16最新README与manifest补齐**，不猜build.mjs已随包提交。
- `paper/round2/experiments/`：**生成/测试/编译命令待PR17新工件补齐**，不能把“正在补”写为可重现。
- 最终无正文VLDB：**最终.tex入口、完整命令、TL2026路径、编译轮数、页数、警告/日志及PDF SHA256待父整合后填写**。
- 新提交身份：最终记录`git rev-parse HEAD`、分支、PR、干净/有改动状态、每一路合入commit与产物hash。未查之前保持待补，不填写虚构HEAD。

## 7. 最终提交/交接清单（主代理/整合cloud负责）

- 将本目录四个seed转存目标仓库的明确文档目录，更新所有目标相对路径；旧相互矛盾合同仅入archive，不能与现行权威文件并列不分效力。
- 汇入四路确认的新HEAD，保持独占目录边界，处理PR13 wrapper来源，锁真实最终入口，不盲改tex/src两棵树。
- 保存原图/参考/脚本/上游manifest和必要引用，不能只有本机绝对路径；缺件明确列出，不把2D容器冒称3D原件。
- 补复现命令/依赖/版本、synthetic标识、合法域与统计审计、同尺寸对照/新QA报告、最终source+PDF hash。
- 覆盖矩阵逐条填写最终产物路径、页/子图或测试、对应commit和新QA结论；不可全局批量pass。
- commit并push到visualization-polish的真实目标分支/PR，回填完整SHA和链接。若尚未合main，说清分支状态，不能把push等同merge。
- 只有以上完成后才能称“本轮验收/提交/交接完成”。本seed不代替这一步。

### 现行身份（取代下面种子里的待补块）

- integration_branch：`cursor/round2-handoff-234e`
- PR：https://github.com/SPikerinbit/visualization-polish/pull/19
- 版式验收 HEAD：`060ef6d951ff6471f4dcbb39aa4c449c1d131425`。文档提交是它的后继，只锁说明，不锁产物。
- 父已读的十页 HEAD（历史）：`f55de18cf87ea324ecb1b94eefc5486bf6a0581f`
- main 是否已 merge：否。基线 `2d05b2de0b8eb6a6fc71df7c7662d708e0eee971` 未改写。
- 四路 HEAD：机制 `c959d22b0eeffaeb78f345b320faaa849164c1a6`；E2 `05f921f20c634dbb4d6e05eb5f4003d17f354183`；表格 `b12cd37113919d32d15a596b0d7e0913cd1c4ec4`；折线 `22b432ca01054da271366518d5ba6684795b1b20`
- final_tex_entry：`paper/round2/integration/main.tex`
- 复现：`cd paper/round2/integration && ./build.sh`。本机 TeX Live 2023，不是 TeX Live 2026。
- 验收 PDF SHA256：`05cece898d313acdb41c272ec2ecf031ab1532c098685f3438d428471a3cde0a`（9 页，`060ef6d` 的 `paper/round2/integration/main.pdf`）。
- 当时源包 SHA256：`80489ae016ddd75dd7180551bb5c74dff6db02a76cfb867249d882bf8b31f5c5`。
- 十页历史 PDF SHA256：`558d290327542773e816191fda0836d050f1b73770cb6ed140354613eb6c0d5c`，不是本轮交付。
- 验收：`doc/round2/qa/FINAL-ACCEPTANCE.md`。十页审计：`doc/round2/qa/history/FINAL-AUDIT-f55de18.md`。分页过程：`doc/round2/qa/PAGINATION-CLOSEOUT.md`。
- 未解决：合成数据、Table 2 公式、原 3D k-sweep TeX、TeX Live 2026、Qwen3.8 对 Qwen3.5 的部署 manifest。这些不是空白，也不能写成通过。

## 8. 下一bot：真实数据接入，不重开视觉设计

- 保持已确认栏宽/布局/风格，真实数据只驱动数值、合法缺口、最优点、前沿、必要坐标范围与标签适配；不再让用户重复选构图。
- 从上游最终measurement/部署condition/prompt/input manifest/SQLite证据接数据，先解决Qwen3.8-27B旧文字与3.5-27B当前表格的身份冲突，不凭标题改condition。
- 正式结果未齐则保持缺失/原因和synthetic样本隔离，不假称采集完成。E4a真实选点后续接入，不阻塞当前视觉闭环。
- 正式测量重新计算E1均值/std/排名/tie-break与E4c各集均值/两集等权红线；保留全等测试和NULL，不造显著性，不将历史prefix readiness混入不同协议正式条件。
- 保留已有视觉验收记录但对真实数据溢出、合法域、图例/轴可读性再检；若统计/输入身份缺失是研究阻塞，应报告而非通过改图隐藏。
