# 新旧结构

11 个旧环境 → 5 个。$h=1$ 仍是 LT($h$)。无分段 LT 第三算法。

| 旧 label | 现在 |
|---|---|
| `alg:semantic_external_merge` | 唯一含 $K$/$\Pi$；$\MergeGroup$ 产出流；Buffer 根 drain；Full 末切片 |
| `alg:sliding_window_kway_group_merge` | 局部有序**流**；无 $\Pi$/$K$ |
| `alg:loser_tree_kway_group_merge` | 同上；$k=1$ yield 到耗尽 |
| 其余 Init / Replay / Refresh | 未改 |

## 列宽

`\columnwidth` = 241.14749pt（acmart v2.19 + pvldb）。TeX Live 2023。

## 不足

- `Expect` 无公式。
- 无 16 元素 trace。
- Buffer 根在实现里仍把 `top_k` 下传到根生成器（`runtime.py` 170–181）；纸面 Alg~2/3 不写，作用域表已说明。
- Init 仍为压缩叙述。