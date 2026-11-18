# 伪代码证据对照

八个源的 SHA-256 在 `viz/evidence/manifest.json`。commit `0d96d0bf116e52f1664ae2539446f05921f5e947`。本轮没有运行这些文件，没有 trace 16 元素中间状态。

`finite.py` 不在这八个文件里。`Expect` 只声明为输入 token 估计。不写公式。同文件的 v3（`plan.py` 483–598）是未校正对照，不是这条 `Expect`。

## 步骤 → 行

| 算法里的步骤 | 源 |
|---|---|
| 无 \(K\) 或 \(K\ge\|D\|\) 用 Full；否则 Buffer。给定 mode 优先。升序且有 \(K\) 强制 Full | `operator.py` `_resolve_mode` 27–41；202–207；请求里升序把 limit 清空 247 |
| \(K=0\) 或 \(\|D\|\le 1\) 直接返回 | `operator.py` 212–214 |
| 切块后 `ListwiseRank` 得到 \(R_i\) | `_common.py` `_listwise_sort` 175–198；一次调用 200–259 |
| \(\arg\min\mathrm{Expect}\)；平局 LT，再较小 \(k\)，再较小 \(h\) | `plan.py` `select_parameters` 604–698，平局键 691–698。缺省 \(h\) 在键里当 0 |
| 调用必须放进 \(m\) | LT：`loser_tree.py` 303–307，\(h=\lfloor m/(1+\lceil\log_2 k\rceil)\rfloor\) 见 298–300 与 188–194。SW 固定 \(h\)：`sliding_window.py` 136–140 |
| 按组 `MergeGroup` | `plan.py` 730–751；Buffer 建树 `runtime.py` 217–226；Full 逐 pass `runtime.py` 230–278 |
| Buffer 排到 \(\|\Pi\|=K\) 后 **finally** 关闭根 | `producer.py` `materialize_producer` 221–244。达到 \(K\) 也 `aclose`。这不是一次排序 |
| 升序先反转再取前 \(K\) | `operator.py` 290–293 |
| \(I\) 是仍占用 buffer 或仍有供给的 run 下标 | `sliding_window.py` 376–380。不用字母 \(A\) |
| 只剩一个 run：按 pull 序吐出并继续拉到 \(K\) | 386–398，504–547 |
| 固定 \(h\) 不借用；\(h\) 缺省才借用到 \(\|I\|q\) | 292–297，323–353 |
| \(O_1,\ldots,O_t\) 为 safe prefix | `_compute_safe_prefix` 612–628 |
| 达到 \(K\) 则返回，不再 pull | `next_candidates` 177–186；`_append_output` 265–276 |
| 未达 \(K\) 时，safe prefix 之后留在 \(B\) | 480–486。达到 \(K\) 时过程返回；实现会先把整段 safe prefix 移出 buffer，未吐出的尾部不回到 \(B\)，也不再 pull |
| 一棵树，不补成 2 的幂；叶存 run 下标；内部结点只存 loser 与 pointer | `loser_tree.py` 35–50，197–211，255–276 |
| \(k=1\) 直接吐到 \(K\) | 284–295 |
| `Init`：叶子为前沿；装得下的最高结点成块；块内自底向上 replay | `plan.py` `init_plan` 227–265。调用处 `loser_tree.py` 482–501，一次 `ListwiseRank` 在 replay 之前 |
| 旧稿用 Full sliding window 做 LT 初始化 | 这八个源里没有这条路径 |
| Replay：\(+\infty\) 计入 \(h\)，不进 `ListwiseRank`，不进 \(w,\ell\)；pointer 与 \(w,\ell\) 同次返回 | 148–183。排序在 372–409，只含真实行 |
| 次序修复：只放行当前 run 头，头之间保留模型序 | 69–107；调用 409 与 599。SW 不走这一步 |
| Refresh：只填当前 pointer 叶；Collect / Rank / Write-back | `refresh_path` 516–553。`fill_leaf` 340–370 |
| \(\|\Pi\|=K\) 则 return，不再 Refresh | 624–641 |
| LT 生成器的 `finally` 只记日志 | 643–648。关闭上游是驱动层的 `aclose` |
| 家族名只有 sliding_window、loser_tree、auto | `logical_operator/orderby.py` 第 6 行 |

## 未写入算法

evidence、shuffle、confident prefix、prefetch、解释阶段、token 画像拟合。它们在源里，不是这五段的合同。
