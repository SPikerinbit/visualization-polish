# 四路 HEAD 快照（不是终验）

查询时间：2026-11-18。只记录当时 GitHub PR `head.sha`。机制与折线 **尚未父准入**，禁止把旧稿或这些 SHA 混进 `paper/round2/integration/`。

| 路 | PR | 分支 | 当时 head.sha | 本整合 |
|---|---|---|---|---|
| 表格/伪代码 | [#18](https://github.com/SPikerinbit/visualization-polish/pull/18) | `cursor/tables-pseudocode-8dad` | `b12cd37113919d32d15a596b0d7e0913cd1c4ec4` | **已纳入** 仅 `paper/round2/tables-pseudocode/`。QA：`qa/PR18-tables-quick-recheck.md`。Full caption 加了 “Full ranking.”，印刷句改为英文 Synthetic fixture for tie-break coverage。 |
| E2 | [#15](https://github.com/SPikerinbit/visualization-polish/pull/15) | `cursor/e2-round2-cost-surfaces-5c87` | `05f921f20c634dbb4d6e05eb5f4003d17f354183` | **已纳入** 仅 `paper/round2/e2/`。QA：`qa/PR15-e2-final-recheck.md`。主图 PNG SHA256 `cddf9a1a1a4fd305cb5971ecb4485b2cbc4028d61293feb968f8aacfff99675f`（162298 bytes）。131758 bytes 的外附 layout 别名 **废弃**。 |
| 机制 | [#16](https://github.com/SPikerinbit/visualization-polish/pull/16) | `cursor/round2-mechanisms-6f22` | `bed819cdfc20c2df5ed067dbd120119daf74bcc6` | 未纳入。旧 wrapper 是 [#13](https://github.com/SPikerinbit/visualization-polish/pull/13) `5b3a024ab527d352204a3559b1a411256992fc9c`，不是 PR16。 |
| 折线 E3–E5 | [#17](https://github.com/SPikerinbit/visualization-polish/pull/17) | `cursor/round2-e3-e5-figures-436b` | `749171a37b2adc266550b067708cb77c4d7e00ae` | 未纳入。 |

基线失败快照仍是 `2d05b2de0b8eb6a6fc71df7c7662d708e0eee971`（`cursor/vldb2027-figure-checkpoint-234e`）。本分支从它长出，不改写该提交。未 merge `main`。

PR15 正文里写过的 `e8e3c0c8…` 与首稿 `702e7d88…` 都不是这次准入对象。准入 SHA 以父指定的 `05f921f2…` 为准，并已从该 commit 检出 `paper/round2/e2/`。
