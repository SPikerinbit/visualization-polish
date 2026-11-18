# 分页收口（过程记录）

本文件记录从十页到 9 页的排版。版式验收结论在 `FINAL-ACCEPTANCE.md`，对象是 `060ef6d951ff6471f4dcbb39aa4c449c1d131425`。这里不是科研通过。

对象：PR19 `cursor/round2-handoff-234e`。父已看过的十页是 `f55de18cf87ea324ecb1b94eefc5486bf6a0581f`。那一版的只读审计在 `history/FINAL-AUDIT-f55de18.md`。本文件只记录那次审计之后的有界修复。

## 审计已经否掉的疑点

页 8 两条 E4a caption 间隔约 22.3bp，页 9 E4c caption 距正文底约 13.6bp。都不是硬碰撞。没有为这两处挪图或重画。E2 面板仍是 `0.33` 倍 sigconf 栏宽（241.14749pt），没有 height 或 resizebox。E3 仍在图内设置 `\subfigcapskip=1pt`。

## 分页

实测：E2 通栏之后，当页栏高是 393.98409pt。E3 盒子 256.14305pt，放得下，所以现在和 E2 同页，在左栏。E4a 盒子 418.00354pt，比这栏高 24pt，单栏折行仍留在同一页，会溢出 24.01945pt。只有这种“比整栏还高”的盒子才 `\clearpage` 到下一页。E2 后面那条无条件 `\clearpage` 已删。

LIMIT 不再是浮动表。表 1、表 2 和 Full 排完后才 `\FloatBarrier`。LIMIT 是下一页的通栏，算法 1 和算法 2 接在表下。算法 4 换到另一栏，所以算法 3 在左、算法 4 和算法 5 在右，算法 5 不再独占一页。

本轮编译 9 页，TeX Live 2023，`./build.sh` 退出 0，没有 Overfull vbox。页数不是目标。

## 复现

```bash
cd paper/round2/integration
./build.sh
```

引擎是 `pdfTeX 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian)`。合同里的 TeX Live 2026 仍未满足。

## 四路入口

| 路 | SHA | 目录 |
|---|---|---|
| 机制 | `c959d22b0eeffaeb78f345b320faaa849164c1a6`（图 `859a6fea272855eaf6976e23b199aea9557c04b9`） | `paper/round2/mechanisms/`，不用 `bed819cd` |
| 表格 | `b12cd37113919d32d15a596b0d7e0913cd1c4ec4` | `paper/round2/tables-pseudocode/` |
| E2 | `05f921f20c634dbb4d6e05eb5f4003d17f354183` | `paper/round2/e2/` |
| 折线 | `22b432ca01054da271366518d5ba6684795b1b20` | `paper/round2/experiments/` 的五段 tex 和 `figures/`，不用 preview |

最终入口是 `paper/round2/integration/main.tex`。PR19。未 merge `main`。基线失败快照 `2d05b2de0b8eb6a6fc71df7c7662d708e0eee971` 没有改写。

## 例外（仍然不算通过）

合成，不是实测。Table 2 公式和 Expect 未核，Setwise 缺式。E1 的 std 和序位不是显著性。E4c 是数据集级占位均值。E5 不是三 query 复算。原 3D k-sweep TeX 未找到，E2 用的是二维 exp5-m 容器。E3 刻度约 4.6pt、图例 5pt。型号展示是 Qwen3.5，历史 Qwen3.8 仍等部署 manifest。TeX Live 2026 未满足。
