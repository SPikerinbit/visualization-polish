# Round-2 交接（版式验收完成，有例外）

分支从失败快照 `2d05b2de` 另开。那一版视觉被用户否定，本目录不把旧 PDF 改写成终稿。

## 现在可以看的

- 现行要求：`CURRENT-DECISIONS.md`（64 条在 `决策覆盖矩阵.tsv`）
- 仓库路径：`BASELINES.md`
- 四路都已进模板：机制 `c959d22`、表格 PR18、E2 `05f921f2`、折线 `22b432ca`。见 `STAGING-HEADS.md`。
- 壳：`paper/round2/integration/`。分页收口后是 9 页。没有独立 LIMIT 机制图，没有 E4 验证表，没有 preview 标题和 review 行号。
- `bed819cd` 的失败记录仍在 `qa/history/`，不覆盖这次返修 QA。
- 失效旧说法：`archive/SUPERSEDED.md`。更早的表格/E2 审核在 `archive/`，**不能**当新稿通过。
- 引擎差异：`TEXLIVE.md`。这台机器是 TeX Live 2023。

## 还没做

版式验收对象是 `060ef6d951ff6471f4dcbb39aa4c449c1d131425`，PDF SHA256 `05cece898d313acdb41c272ec2ecf031ab1532c098685f3438d428471a3cde0a`。结论在 `qa/FINAL-ACCEPTANCE.md`。不是科研通过。真实数据、Table 2 公式、`finite.py`、原 3D k-sweep TeX、TeX Live 2026、E3 小字、型号部署 manifest 都未闭合。

复现：`cd paper/round2/integration && ./build.sh`。本机是 TeX Live 2023。

型号：历史合同 `paper-experiments.md` 写 Qwen3.8-27B；当前合成表印 Qwen3.5-27B。真实条件等部署 manifest，不在这里猜。
