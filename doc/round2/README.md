# Round-2 交接（进行中，不是验收完成）

分支从失败快照 `2d05b2de` 另开。那一版视觉被用户否定，本目录不把旧 PDF 改写成终稿。

## 现在可以看的

- 现行要求：`CURRENT-DECISIONS.md`（64 条在 `决策覆盖矩阵.tsv`）
- 仓库路径：`BASELINES.md`
- 已父准入并纳入树内的只有两路：表格 PR18、E2 主 12 图 PR15。见 `STAGING-HEADS.md` 与 `qa/`。
- 最小模板：`paper/round2/integration/`。里面只有这两路。没有机制图，没有 E3–E5。
- 失效旧说法：`archive/SUPERSEDED.md`。更早的表格/E2 审核在 `archive/`，**不能**当新稿通过。

## 还没做

机制与折线等父给出已审 HEAD 后再纳入。真实数据、Table 2 公式、`finite.py`、原 3D k-sweep TeX 都未闭合。E2 不能写成“用户要求的原 3D 只换图已经完全通过”：主 12 图版式已父读通过，容器仍是二维 `exp5-m` 替代。

型号：历史合同 `paper-experiments.md` 写 Qwen3.8-27B；当前合成表印 Qwen3.5-27B。真实条件等部署 manifest，不在这里猜。
