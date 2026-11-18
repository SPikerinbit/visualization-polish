# 远端分支并入 main

用户 t66 明确要求把全部远端分支合并进 `main`。本记录只说明合并结果。版式验收对象没有改。

## 身份

- 合并前 `origin/main`：`ce8463178ab15877754a96f1c00dbeb157be71ac`（两笔提交，无状态检查）。
- 权威文档头：`d6c4ef1ce7094437231b18f38c738f890ea20a0f`（PR19）。它只记录验收，不代替版式工程。
- 版式工程：`060ef6d951ff6471f4dcbb39aa4c449c1d131425`。
- 验收 PDF SHA256：`05cece898d313acdb41c272ec2ecf031ab1532c098685f3438d428471a3cde0a`。合并后该 blob 未变。
- 全部分支头第一次同时成为祖先：`01c91122897d636b77d78b8fe046e0882bce19a4`。其后的文档提交只改 `doc/round2/`，不改 `paper/round2` 与 `paper/tex`，也不代替版式 SHA。

## 检查

GitHub combined status 对 `main` 与 `d6c4ef1` 都是 `pending`，`total_count=0`。没有可等待的检查。PR 列表里 `mergeable` 未计算。未绕保护、未跳 hook、未 force、未改写已推提交、未删除远端分支。`ManagePullRequest` 不能执行 merge，因此在干净的 `main` 工作树上做常规 merge 后 push。

## 分支结果

全部 `origin/cursor/*` 头在合并后都是 `main` 的祖先。没有因秘密或互斥目标而停下的分支。`viz/tex/vendor/PIN.txt` 是 acmart/pvldb 文件校验和，不是密钥。

| 分支 | 头 | 结果 |
| --- | --- | --- |
| cursor/round2-handoff-234e | d6c4ef1 | fast-forward，main 从 ce84631 到该头（ahead 22, behind 0） |
| cursor/vldb2027-figure-checkpoint-234e | 2d05b2d | 已是 d6c4ef1 祖先，Already up to date |
| cursor/e2-dual-surface-c6cc | 84a84ad | 干净 merge，历史稿留在 `recovery/e2/` |
| cursor/e3-scale-layout-14e8 | 001f4dd | 干净 merge，`recovery/e3/` |
| cursor/e4a-off-on-cold-curves-29a9 | 607f3ee | 干净 merge，`recovery/e4a/` |
| cursor/e4b-beta-curves-7203 | 11ec8d4 | 干净 merge，`recovery/e4b/` |
| cursor/e4c-quality-cost-scatter-fef1 | 1b90777 | 干净 merge，`recovery/e4c/` |
| cursor/e5-limit-sweep-5af7 | 0738331 | 干净 merge，`recovery/e5/` |
| cursor/framework-algo1-cost-6f22 | 5b3a024 | 干净 merge，`recovery/framework/`。这是 PR13 失败包装，未覆盖 `paper/round2/mechanisms` |
| cursor/lt-h-main-figure-d022 | 9f1f827 | 干净 merge，`recovery/lt/` |
| cursor/pointer-local-figure-1615 | 258b9ac | 干净 merge，`recovery/pointer/` |
| cursor/recovery-limit-ondemand-trial-a880 | 2275088 | 干净 merge，`recovery/` 下对应历史目录 |
| cursor/sw-sliding-window-figure-ad37 | 1647f5f | 干净 merge，`recovery/sw/` |
| cursor/vldb-pseudocode-4e18 | 2973a86 | 干净 merge，`recovery/pseudocode/` |
| cursor/round2-mechanisms-6f22 | c959d22 | 干净 merge。机制图已在验收树中，无新文件覆盖 |
| cursor/round2-e3-e5-figures-436b | 22b432c | add/add 冲突，保留验收侧五份 fig tex |
| cursor/vldb2027-table-checkpoint-9ab5 | dd90fa5 | 干净 merge，独有工程在 `recovery/tables/`。未把旧 `paper/tex` 科学结论写回验收稿 |
| cursor/e2-round2-cost-surfaces-5c87 | 05f921f | 无父提交，`--allow-unrelated-histories`。树已包含于验收版，无文件冲突 |
| cursor/tables-pseudocode-8dad | b12cd37 | 无父提交，`--allow-unrelated-histories`。七个 add/add 保留验收侧 |

## 冲突怎么解

没有使用 `-s ours`。冲突只出现在双方都新增、内容不同的验收路径上。保留 `d6c4ef1` 一侧：

- `paper/round2/experiments/tex/fig-e3.tex`、`fig-e4a.tex`、`fig-e4b.tex`、`fig-e4c.tex`、`fig-e5.tex`（折线分支是集成前的稿，验收侧含已确认的 caption 与 E3 `\subfigcapskip=1pt`）。
- `paper/round2/tables-pseudocode/` 的 `HANDOFF.md`、`STATS.md`、`src/emit.py`、`tex/algorithms.tex`、`tex/generated/exp1-full.tex`、`tex/generated/exp1-limit.tex`、`tex/preview.tex`（表格头 `b12cd37` 仍是祖先；验收侧是其后的版式修改）。

`paper/round2`、`doc/round2`（本文件写入之前）、`paper/tex/main.tex` 相对 `d6c4ef1` 无差异。

## 历史稿不是终稿

`recovery/` 是各早期分支的原路径副本，包括 PR1/PR13 失败稿与表格检查点。它们不是 `paper/round2` 终稿。终稿入口仍是 `paper/round2/integration/main.tex`。Qwen3.5 与 Qwen3.8 的 json 都保留在 `recovery/tables/data/`，本合并不裁定模型名。

## 复现

`cd paper/round2/integration && ./build.sh`。引擎 pdfTeX 3.141592653-2.6-1.40.25（TeX Live 2023/Debian），9 页。重编 PDF 的 SHA256 为 `2e201101b1a9d5f2c67b6e05bee30aa90605b3d903bfa9cd019b254b33cd5a36`，与验收字节不同，但 `pdftotext -layout` 全文相同，110 dpi 九页 PNG 逐页相同。未重画，工作树恢复验收 PDF。未声称科研通过或 TeX Live 2026。
