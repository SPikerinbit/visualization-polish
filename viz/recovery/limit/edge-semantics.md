# LIMIT 按需试稿：逐边语义

图面坐标来自 `geometry-report.txt`（页面毫米，y 向上）。端点检查 PASS：每条箭的起点和终点落在对应盒子边界上，开区间不进入 driver、root 或任何元素圆。

| 边 | 面板 | 线型与方向 | 起点 → 终点（mm） | 语义 | 不是 |
|---|---|---|---|---|---|
| request | (a)(b) | 墨色虚线，箭头向下 | (a) (9.60, 64.05) → (9.60, 51.65)；(b) (69.07, 64.05) → (69.07, 51.65)。都是 drain 底边到 root 顶边 | `materialize_producer` 在 `len(result) < K` 时调用 `next_candidates` | 不是红色 `ListwiseRank`；不是 run 自己发出的停止 |
| yield | (b)(c) | 蓝色实线，箭头向上 | (b) (95.27, 51.65) → (95.27, 64.05)，标 yield 1；(c) (154.73, 51.65) → (154.73, 64.05)，标 yield 2。root 顶边到 drain 底边 | 一项进入 drain 持有的结果。计数从 0 到 1 再到 2 | 不是下一次请求 |
| 无 request | (c) | 没有箭杆，只有 “not issued” | 与 (a)(b) 同一条 request 的 x，不画线 | `len(result) >= K` 后循环在下一次 `next_candidates` 之前 break | 这几个字不是一条边 |
| aclose | (c) | 灰色点线，空心圆头，向下 | (171.93, 64.05) → (171.93, 51.65)。drain 底边到 root 顶边 | `finally` 里的 `producer.aclose()`，释放泵和上游 | 不是比较，不是排序调用，不是质量指标 |

没有画进 run 圆的边。空心元素留在原位，表示没有进一步的请求打到它们。

计数画在 drain 盒内的 `emitted`。root 盒只写 “answers the pull”，不把 K 画在 run 上。

## 源码对应

- 谁持有已输出计数、何时不再请求、`finally aclose`：`producer.py` `materialize_producer` 221–244，`drain_producer` 246–272。
- 只有 root 得到 `top_k=limit`，非 root 为 `None`：`runtime.py` `build_family_tree` 162–181。buffer 路径由 drain 以 `top_k=limit` 拉取：`execute_family` 217–226。
- Full 是另一条路径：各组 `materialize_producer(..., top_k=None)`，最后才可能切片。`runtime.py` 230–289。`plan.py` 451、709：`limit is not None and limit < n` 才是 buffer，否则 full。`operator.py` `_resolve_mode` 27–41；`limit >= len(df)` 时不再把 limit 交给 mode（202–204）；升序强制 full（205–207）。
- root 上另有第二道门：SW `_emitted_count`（`sliding_window.py` 162、177–186、214），LT `emitted_count`（`loser_tree.py` 282、625–641）。图上的空 request 车道画的是 drain 不再调用，不是 “run 自知 K”。
- `aclose` 关泵并递归关闭上游：`runtime.py` `StreamProducer.aclose` 98–110；SW `aclose` 222–224 只关上游。
