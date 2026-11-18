# 实现基线（仓库相对路径）

## 最新云端候选证据边界（2026-11-18）

- 本次文档更新读取的main为b75370d8e643ddb62762cf4ba8709abd0becccd3；只增加现行决定与证据说明，不新增视觉源或产物。旧记录仍保留历史。
- Framework v16为仓库外云端候选：TL2026、实际VLDB模板textwidth506.295TeXpt（约178mm）、图高48.73mm、最小字号7.251bp，实际模板与同尺寸A/B编译通过并做局部强审；不是用户终验。四输入内容/对象保留，三棵树节点与文字不变，连接端点修整。后续源工件入库时补稳定相对路径/hash，不以本条虚构已推送。
- 已修request/system-prompt标题带字墨净距，v16还修+config底部净距；可移植生成器在独立路径运行后字节复现SVG。合入时同步生成器、两份SVG、PDF/PNG及新caption，防止旧376高作者源回退当前438高图。本文档提交不包含这些文件。
- 用户认可仅指四输入实体化内容与视觉语言；新的连线/内部细节/Full Ranking与LIMIT K标题候选，以及整稿，仍待最终审阅。
- Fig.8去k括线、Fig.11上方独立legend、机制图灰度及实际尺寸对齐为新要求；其他工件是否已完成按相应最终候选检查，不由Framework的局部编译结果代证。synthetic/部署未核的既有边界不变。

---

## 本次证据与未交付边界（2026-11-18）

- 本次提交以重新读取的远端main e122c13b7ef62ae72a0a4b60c9ef9c906fff45ca为父，仅更新三份doc。独立Framework/机制/E1/实验及整合候选尚未随此提交入库；不得把它们视为仓库已交付或整体已验收。
- 云端GitHub网页实查上游[OperatorSemanticOrderBy提交历史](https://github.com/BITQiKangK/SemaPrototype/commits/OperatorSemanticOrderBy/)：最新条目为2026-11-17“Implement paper experiment workflows and archive study results”，实际链接完整SHA为0d96d0bf116e52f1664ae2539446f05921f5e947，等于现有冻结点；因此该分支无冻结之后的已提交变化，含merge/loser_tree及_shared。Connector当时对上游返回404，结论来自已登录云端网页，不是connector比较成功。不能据此证明部署或未提交工作状态。
- 旧正文LT h=1、现图h=2实例、exhausted-run loser措辞的潜在语义冲突仍待逐项闭合。上述HEAD相同不等于旧正文正确，也不消除实例参数差异。
- 用户最新指定模型2名Qwen3.8-27B；实际部署manifest尚缺，旧Qwen3.5记录仅可追溯，不可无证改写为已部署3.8。实验数值仍synthetic，真实measurement未验证。
- 图像统一规则为视觉层级而非同色：E4a蓝/橙是Off/On-cold缓存配置；各实验系列角色保留。Framework H/L含义、Full同层并发/层间屏障、LIMIT禁prefetch等以CURRENT-DECISIONS最新节为准。
- 仓库外实际TL2026检查及候选对照需在后续合入时补稳定相对路径、hash、构建日志与整体验收。本次不虚构候选已归档；既有相对路径和历史证据保留。

---

## 最新工件组织要求与状态（2026-11-18）

- 当前Fig.7–10的E4a合为通栏16子图；实验每panel独立输出，TeX subfigure组装，legend独立。Fig.12需进一步压缩。编号仅定位当前审阅稿，最终以内容与TeX标签映射为准。
- 本次是doc-only同步，不新增或替换机制图、实验图、算法示例、整合TeX或PDF；本轮云端候选尚未随本次提交推送，也不构成稳定验收基线。后续由主整合者补仓库相对路径、文件hash、源提交与完整模板验收证据，不以机器临时路径冒充仓库工件。
- Framework已核代码依据仍为 `viz/evidence/sources/sema_prototype/physical_operator/orderby/merge/_shared/plan.py`：`select_parameters`接收lengths/m/limit/profile、枚举可行参数并比较input_tokens；`CostEstimate.input_tokens`为H×total_calls+L×total_items（计及适用尾部修正）；`resolve_merge_plan`在逐趟计划前调用一次选参。图内成本不可写成总token。
- 实现/论文区别须保留：Full SW未显式给h时，`select_parameters`可使用h=None，SW运行时按活跃runs分配窗口；论文图按用户约定统一讲选(k,h)。这不是所有实现路径固定数值h的证明。h不表示树深。
- 新增Alg.1总体流程示例的最终源文件及完整状态核验尚待实际合入后登记，不杜撰已归档位置。合成数据披露转到整稿开头并明确非实测，数据和研究缺口本身不变。

---


## 本轮来源与状态补充（2026-11-18，已同步决策）

- 以下原仓库基线路径继续有效；`recovery/`仅用于明确指定的历史来源，不是当前终稿入口。
- 云端已具备TeX Live 2026并实际编译过基线及若干独立候选；下表关于“本机引擎仍TL2023”的文字保留历史，不作为新环境能力断言。当前构建证据应随最终候选归档，不能只留下执行机器绝对路径。
- 本轮E2直接视觉参考为用户新提供的旧3D截图，内容包含成本及Spearman两侧面板。只继承配置点清楚、面与网格次要的表达；仍不恢复已删除的Spearman面板。该附件需由整合者复制入稳定仓库路径并记录hash后再列为已归档；本补充不虚构已上传位置。
- E2轴义来源：`实验结果可视化/可参考：实验二3D/compute_surface.py`中P=est.input_tokens；相邻`plot_surface.py`中U/1000和P/1000及Merge input tokens(1k)。这是输入成本而非Total。`paper/round2/e2/plot_surfaces.py`仍生成合成值；原surface_data.json缺失事实不变。
- 外部参考证据分级：`paper/recovery/e4c/REFERENCE.md`记录Palimpzest Fig.3与LOTUS Fig.4/6的阅读笔记；`paper/round2/experiments/NOTES.md`记录ListK Fig.4/5语义。当前快照未找到笔记所指外部PDF/裁图全集，不得称本轮已直接复核全部论文原图。ListK仍只按已记录预印本身份引用，SemBench只有记录线索不能臆造图号。
- 本轮独立视觉候选不是稳定实现基线。最终合入时逐项补：仓库相对源/图路径、数据不变核验、模板编译环境、图例与指标语义、视觉检查及对应commit。未获验收前明确标“候选”。


---


现行视觉要求见 `CURRENT-DECISIONS.md`。本文件只回答文件在哪。种子里的 BOX 路径在 `archive/BASELINES-SEED-with-box-paths.md`，**不是**现行路径。

## 已在本仓库、可直接打开

| 用途 | 路径 |
|---|---|
| 用户 v2 SW | `算法机制图/第二版/revision_v3/sd_merge.pdf` |
| 用户 v2 统一 LT | `算法机制图/第二版/revision_v3/lt_unified.pdf` |
| 用户 v2 Pointer | `算法机制图/第二版/revision_v3/pointer_rule.pdf` |
| 用户 v2 framework 旧例 | `算法机制图/第二版/revision_v3/algo1_exp.pdf` |
| v2 状态 | `算法机制图/第二版/revision_v3/validated_states.json`、`figure_data.json` |
| v1 只借颜色 | `算法机制图/第一版/sliding_window_exp.pdf`、`loser_tree_exp.pdf`、`segment_loser_tree_exp.pdf`、`algo1-exp.pdf` |
| E2 参考截图 | `paper/recovery/e2/reference/fig-E2-cost-surface-reference.png`；round2 副本 `paper/round2/e2/refs/fig-E2-cost-surface-reference.png` |
| 原 3D 脚本 | `实验结果可视化/可参考：实验二3D/plot_surface.py`、`compute_surface.py`；副本 `paper/round2/e2/refs/recovery-spec/references/scripts-3d/` |
| 二维 exp5-m 面板 | `paper/tex/fig/panels/exp5/exp5_movies_full_tokens.pdf` 等 |
| 组图 TeX 笔记 | `实验可视化组图tex源码参考.txt` |
| 旧论文 TeX | `paper/tex/exp.tex`、`paper/tex/framework.tex` |
| Table 1 批准源 | `paper/recovery/tables/tex/tab-datasets.tex` |
| 机制四图 | `paper/round2/mechanisms/{framework,sw,lt,pointer}.pdf`。来源 HEAD `c959d22b0eeffaeb78f345b320faaa849164c1a6`，图提交 `859a6fea272855eaf6976e23b199aea9557c04b9`。`src/preview.tex` 不是入口。 |
| 折线 E3–E5 图段 | `paper/round2/experiments/tex/fig-e3.tex` 至 `fig-e5.tex`；面板 PDF 在 `paper/round2/experiments/figures/`。来源 SHA `22b432ca01054da271366518d5ba6684795b1b20`。`tex/preview.tex` 只是审图预览，不是入口。 |
| 官方模板 | `paper/tex/vendor/acmart.cls`、`paper/tex/vendor/pvldb.sty`。类文件头写 2026/06/27；本机引擎仍是 TeX Live 2023，见 `TEXLIVE.md`。 |
| 研究合同（含历史型号） | `paper-experiments.md`（文中仍有 `Qwen3.8-27B`，与现行表 `Qwen3.5-27B` 冲突，只留追溯） |
| 上游源码快照 | `viz/evidence/sources/sema_prototype/...`；清单 `viz/evidence/manifest.json`。快照 commit `0d96d0bf116e52f1664ae2539446f05921f5e947` 不是本仓库提交，也不锁定部署。 |

## 明确缺失

- `实验结果可视化/可参考：实验二3D/surface_data.json`：没有。原 `compute_surface.py` 不能在此直接跑出真实曲面。
- `finite.py`：仓库内没有。不得声称有限期望已核。
- 原 3D k-sweep TeX 容器：没有定位。`fig:exp5-m` 是二维 batch-size 组图，只是可核的面积参照，**不是**“原 3D 只换图”已经完成。
- ListK PDF 与用户截图：本工作树没有 `visual-refs/pdfs/listk-semantic-orderby.pdf`。预印本标识仍是 arXiv:2603.17223。不要把笔记写成已核顶会正式版。
- 真实 measurement 全文与部署 condition manifest：没有。下一 bot 接数据前要锁定，不要猜型号改数。

## 合法域（源码位置，不是本轮新证明）

`viz/evidence/sources/sema_prototype/physical_operator/orderby/merge/_shared/plan.py` 的 `max_segment`、候选枚举、`validate_request_capacity`。正常网格：SW `2≤k≤min(r,m)`，`1≤h≤floor(m/k)`；LT `2≤k≤min(r,2^(m−1))`，`h≤floor(m/(1+ceil(log2 k)))`。n=100、m=20、r=5 时 k=8 不合法。

## 原面板线点（笔记，最终投放尺寸再核）

133.2pt 面板：数据线 1.6pt，点包围盒约 4.8pt，浅灰网格 0.765pt `#B0B0B0`。系列色 `#1F77B4` `#2CA02C` `#D62728` `#FF7F0E` `#17BECF` `#CC79A7`。旧 SLT 色只是历史，不恢复第三家族。3D 脚本色 BLUE `#087F9B`、ORANGE `#DA821E`。选点应落在对应实测成本高度，不沿用脚本把菱形画在预测高度的旧细节。
