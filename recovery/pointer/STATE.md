# Pointer 局部图状态表

数字来自 `validated_states.json` 的 `pointer`，并与 `loser_tree.py` 的 `_replay_validated_segment`（148–183 行）和 `refresh_path` 的入槽（539–552 行）对照。没有新跑 trace。json 里的 `L`/`R` 只出现在这张对照表，图上不用这两个字母。

| json | 图上的名字 | 含义 |
|---|---|---|
| slot `L` | slot 0 | replay 的第一个参数。耗尽时 pointer 写成物理 child 0 |
| slot `R` | slot 1 | replay 的第二个参数。耗尽时 pointer 写成物理 child 1 |
| pointer `R` | child 1 | 物理右孩子，本例是 run R2 |
| pointer `L` | child 0 | 物理左孩子，本例是 run R1 |

16 元素身份（与 SW / 统一 LT 相同，本节点只用前两条）：

| Run | 有序内容 | 本图角色 |
|---|---|---|
| R1 | 3, 7, 12, 16 | child 0 |
| R2 | 1, 5, 6, 14 | child 1 |
| R3 | 2, 8, 11, 15 | 不在这个节点 |
| R4 | 4, 9, 10, 13 | 不在这个节点 |

`h = 2`。两例的两个槽都正好满 `h`，没有虚位。`+\infty` 不画。

## Build

| 项 | 值 |
|---|---|
| 旧 pointer | 无。节点字段初值是空，不是 child 0 |
| slot 0 | child 0 的段 [3, 7] |
| slot 1 | child 1 的段 [1, 5] |
| z | 1（slot 1，count 1），3（slot 0，count 1），5（slot 1，count 2），7 |
| 耗尽 | z 的下标 2（从 0 计），元素 5。slot 1 的计数先到 h=2。扫描在这里停 |
| 7 | 仍在 loser 里，不再记一次耗尽 |
| winner | [1, 3]，向上送出，不存在节点里 |
| loser | [5, 7]，写入节点 |
| 返回 pointer | child 1。这是赋值，不是从旧值翻转 |
| 更新后的未读 | child 0 为 [12, 16]，child 1 为 [6, 14] |

## Refresh

| 项 | 值 |
|---|---|
| 旧 pointer | child 1。它就是 Build 刚赋的值，所以下一步只填这个孩子 |
| slot 0 | 节点里已存的 loser [5, 7]。不是 child 0 的段 |
| slot 1 | 沿 pointer 填到的新段 [6, 14] |
| child 0 | [12, 16] 不进入 z，保持未读 |
| z | 5（slot 0，count 1），6（slot 1，count 1），7（slot 0，count 2），14 |
| 耗尽 | z 的下标 2，元素 7。slot 0 的计数先到 h=2 |
| 14 | 仍在 loser 里，不再记一次耗尽 |
| winner | [5, 6]，向上送出，不存在节点里 |
| loser | [7, 14] |
| 返回 pointer | child 0。旧值是 child 1，所以这一例是 child 1 → child 0 |
| 更新后 | child 0 仍是 [12, 16]；child 1 为空（R2 的 1, 5, 6, 14 都已进入过 replay） |

返回的孩子是「哪个槽的计数先到 h」，可以和旧 pointer 是同一个孩子。这两例里没有出现「返回值等于旧值」。图上写了这条规则，没有另画一个例子。
