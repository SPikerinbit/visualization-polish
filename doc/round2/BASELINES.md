# 实现基线（仓库相对路径）

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
