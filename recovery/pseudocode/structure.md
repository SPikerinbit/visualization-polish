# 新旧结构

旧稿 11 个环境。这里收成 5 个。\(h=1\) 不是第二套 LT。分段 LT 不再单列。

| 旧 label | 现在 |
|---|---|
| `alg:semantic_external_merge` | 保留。选参、`MergeGroup`、Buffer 的 finally 关闭写在这一段 |
| `alg:sliding_window_kway_group_merge` | 保留。活跃下标是 \(I\)，不是 \(A\) |
| `alg:loser_tree_kway_group_merge` | 保留为唯一 LT(\(h\))。\(h=1\) 走同一过程 |
| `alg:init_loser_tree` | 收进 LT 末尾的 `Init`。不是另一次滑窗 |
| `alg:refresh_loser_tree_path` | 保留。Collect / Rank / Write-back 分列 |
| `alg:segmented_loser_tree_merge` | 删。不再定义这个 label |
| `alg:replay_segment_node` | 保留。一次返回 \((w,\ell,p)\) |
| `alg:repair_segment_path` | 收进 Refresh 的 Write-back。不再单独成段 |
| `alg:pipelined_topk_driver` | 收进驱动：排到 \(K\) 停止，finally 关闭 |
| `alg:pipelined_sw_next` | 收进滑窗的 \(K\) 返回 |
| `alg:pipelined_lt_next` | 收进 LT：\(K\) 达到后不 Refresh |

父代理整合时改引用。本目录不改 `framework.tex` / `appendix.tex`。

`algorithms.tex` 供 `\input`。父稿已有 `algorithm2e` 的 `ruled,vlined,linesnumbered`。片段里有 `\DontPrintSemicolon`。放置用 `[t]`，因为双栏里 `[H]` 会报错。

## 列宽

官方类是 `viz/tex/vendor` 的 `acmart` 2026/06/27 v2.19 加 `pvldb` 2026/07/06。`\columnwidth` = 241.14749pt。引擎是 TeX Live 2023，不是 TeX Live 2026。

看过渲染：空集是带斜线的圆，不是数字 0。\(O_{t+1}\) 的 \(t{+}1\) 在下标里。题注 `Semantic external merge`、`Sliding window`、`LT(\(h\))`、`Replay`、`Refresh` 没有断字。`ListwiseRank` 放在 `\mbox` 里。Notation 按行断开，避免 `estimated` / `absent` 被拆开。

## 不足

- `Expect` 没有公式。
- 没有跑源，也没有 16 元素的 trace。图上的那组数不写进算法。
- 滑窗在 \(K\) 截断时，实现会丢掉 safe prefix 里还没吐出的尾部；算法写成返回且不再 pull。
- `Init` 写的是「装得下的最高结点」，不是 `plan.py` 的递归逐行。
- 次序修复写的是资格规则，不是游标循环。
- 升序、mode、finally 按源写入。evidence 与 v3 公式没有写。
