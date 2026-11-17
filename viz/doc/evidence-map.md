# 实现证据

Commit `0d96d0bf116e52f1664ae2539446f05921f5e947`。五份文件 SHA-256 与字节数见 `evidence/manifest.json`，与浏览器 manifest 一致。没有包装文本。

| 算法 | 文件 | 函数与行 |
|---|---|---|
| 模式与 K | `operator.py` | `_resolve_mode` 27–41；升序强制 full 205–207；`short_limit` 237–241；截断 292–293 |
| 选参调用 | `operator.py` | `prepare_merge_plan` 265–267；`parameters_selected` 273–279。公式在未读的 `plan.py` |
| Phase 1 | `_common.py` | `_listwise_sort` 175–198；阶段名 15–21 |
| 一次 ListwiseRank | `_common.py` | `_dialect_rank_listwise` 200–259 |
| SW 固定 h | `sliding_window.py` | 136–140、`_compute_targets` 292–297；短缺借用仅在 h 为空时 323–324 |
| SW 安全前缀 | `sliding_window.py` | `_compute_safe_prefix` 612–628；未发出的行留在 buffer 480–486 |
| SW 停在 K | `sliding_window.py` | `next_candidates` 177–186；`_append_output` 270–276；`aclose` 222–224 只说明被调用时会关上游 |
| LT 同一过程 | `loser_tree.py` | `_loser_tree_stream_generator` 255–276；h 298–307；`_loser_tree_compute_params` 188–194 |
| 节点字段 | `loser_tree.py` | `_PointerSegmentNode` 35–50；建树不补成 2 的幂 197–211 |
| Replay | `loser_tree.py` | `_replay_validated_segment` 148–183 |
| 次序修复 | `loser_tree.py` | `_preserve_segment_run_order` 69–107，排序后 409、599 行调用 |
| 初始化 | `loser_tree.py` | 482–501 调用 `init_plan`。块怎么划分不在这五份文件里 |
| 刷新三步 | `loser_tree.py` | `refresh_path` 516–578：沿 pointer 下降并 `fill_leaf`，收集后一次排序，自底向上 `install_replay` |
| LT 停在 K | `loser_tree.py` | 624–641，达到 K 后 return，不再 refresh |
| 家族名 | `logical_operator/orderby.py` | `VALID_MERGE_ALGORITHMS` 第 6 行只有 sliding_window、loser_tree、auto |

`tests/test_ranking.py` 用同一条 replay 规则核对了满段例子和虚拟 +∞ 例子。例子里的数字来自第二版图的状态，不是这次 commit 的运行日志。
