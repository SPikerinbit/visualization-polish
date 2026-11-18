# 伪代码证据对照

commit `0d96d0bf116e52f1664ae2539446f05921f5e947`。八个源校验在 `viz/evidence/manifest.json`。未运行 ranker。

`finite.py` 不在八个源中。`Expect` 只作接口声明。

## 作用域（本轮修正）

| 概念 | 伪代码位置 | 源码 |
|---|---|---|
| 可选 $K$、全局 $\Pi$ | 仅 Algorithm~1 | `operator.py` 292–293 最终切片；merge 本身无 $\Pi$ |
| $\MergeGroup(G,f,h)$ | 显式组 $G$ 与 $(f,h)$ | `plan.py` 730–751 `PlannedGroup`；`runtime.py` 153–197 |
| 每 pass 与物化同循环 | Full 本趟物化再进下趟 | `runtime.py` 230–282：`current` 每 pass 替换为物化结果 |
| Full 闭合 $\Pi$ | `Π ←` 唯一物化 run | `runtime.py` 288–289 `current[0]` |
| Buffer 不中途物化 | 循环只接流；末趟一根流 | `runtime.py` 217–226 建树后 drain |
| 中间组不设 $K$ | Algorithm~2/3 无 $K$、无 $\Pi$ | `runtime.py` 170–181：仅 `root=True` 时 `top_k=limit`；其它 `None` |
| Buffer 根截断 | Algorithm~1 drain | `runtime.py` 217–226 `materialize_producer(root, top_k=limit)` |
| Buffer 无 $K$ 仍排干 | Algorithm~1 `stop at $K$ if specified, else exhaust` | 同上：`top_k=None` 时 `producer.py` 221–244 排到耗尽 |
| Full 各组合并 | 每 pass 全量物化 | `runtime.py` 249–278 `materialize_producer(p, top_k=None)` |
| Full 最终 $K$ | Algorithm~1 末行 | `runtime.py` 289 `out[:limit]` |
| 根 **finally** 关闭 | Algorithm~1 Buffer | `producer.py` 221–244，含提前达到 $K$ |
| SW/LT 生成器语义 | yield 到耗尽 | 纸面 merge 无 $K$；实现仅在 Buffer **根**上仍传 `top_k`（`runtime.py` 170、181） |

## 步骤 → 行

| 算法步骤 | 源 |
|---|---|
| mode：无 $K$ 或 $K\ge\|D\|$ → Full；否则 Buffer | `operator.py` `_resolve_mode` 27–41 |
| 升序且 $K$ → Full | `operator.py` 205–207 |
| 切块、`ListwiseRank` → $R_i$ | `_common.py` 175–198 |
| $\arg\min\Expect$；平局 LT, $k$, $h$ | `plan.py` 604–698 |
| `while |R|>1` 每 pass 分组 | `runtime.py` 232–282 / 143–199 |
| Full：`materialize MergeGroup` 后 $\mathcal{R}'$ | `runtime.py` 278 `materialize_producer(..., top_k=None)` |
| Buffer：$\mathcal{R}'$ 为流，最后 drain | `runtime.py` 161–197；217–226 |
| $\Pi\leftarrow$ 唯一 run（Full） | `runtime.py` 288–289 |
| Buffer drain + finally | `producer.py` 221–244 |
| 升序 reverse 再 slice | `operator.py` 290–293 |
| SW：$I$ 活跃下标 | `sliding_window.py` 376–380 |
| SW：单路 fast path 按 pull 序 yield | 386–398，504–547；`_sw_stream` 113–118 逐行 yield |
| SW：safe prefix；余下留 $B$ | 612–628；480–486 |
| SW：**无** merge 级 $K$（纸面） | 组内 `top_k` 恒 `None`，见 `runtime.py` 248–268（Full）与非 root 161–181 |
| LT：$k=1$ yield 到耗尽 | `loser_tree.py` 284–295（无 `top_k` 时到源尽） |
| LT：$S$ 段 yield + Refresh | 601–642（生成器层；**根** Buffer 可带 `top_k`） |
| Init / Replay / Refresh | 同上一 checkpoint |
| 家族名 | `orderby.py` 第 6 行 |

## 纸面小例（静态，未跑）

**两层，$K$ 缺省，Buffer。** 四个叶 run 长度 $(3,3,3,3)$，$k{=}2$，一层 $\MergeGroup$ 得两根流，再合并成根流。中间两组合并无 $K$。根 `materialize_producer(..., top_k=None)` 排干 12 行；无 `[:limit]`。

**两层，$K{=}5$，Buffer。** 同上拓扑，根 `top_k=5` 只取 5 行后 `finally` `aclose`；未拉取的行不通过中间组回收。

**Full，$K{=}5$，升序。** 每层 `materialize_producer(..., top_k=None)` 得到完整 pass；`reverse` 后 `[:5]`。中间 run 不提前截断。

## 未写入

evidence shuffle、confident prefix、prefetch、解释阶段、token 画像。