# LIMIT 按需机制试稿：保留条件与局限

状态：概念试稿。用户只授权先画一版看是否保留。不是终稿必收，不 merge，不写入论文 `tex`。

## 打开过的文件

- `/tmp/recovery-spec/逐图制作说明.md` 的共用合同与「图 F-LIMIT-trial」八栏
- `/tmp/recovery-spec/给后续制作者的交接要求.md`
- `/tmp/recovery-spec/references/manifest.md`
- 参考图：`mech-bwtree-fig3-split.png`、`mech-wiscsort-fig3-dataflow.png`、`mech-origami-fig2-mcmerge-steps.png`、`mech-crocsort-fig2-parallel-merge.png`
- 8 个源：`operator.py`、`orderby.py`、`_common.py`、`plan.py`、`producer.py`、`runtime.py`、`loser_tree.py`、`sliding_window.py`
- `figure_data.json`、`revision_v3-README.md`、`acmart.cls` sigconf 页边

无用户独立 LIMIT 原图。没有用 r1–r3 或仓库里已有的 `viz/figures/mech-limit.pdf` 当基线，也没有改它。

## 从参考图留下的做法

- Bw-Tree Fig. 3：三格同一几何，只改箭和着色；箭端落在盒子边界。
- WiscSort Fig. 3：请求/产出用不同线型，图例放在图内。
- Origami Fig. 2：元素位置不动，变的是标记。
- CrocSort Fig. 2：没有可照搬的按需协议，不抄它的线程框。

## 什么时候可以保留

同时满足下面几条，才值得请用户决定留不留：

1. 要讲的是 drain 驱动的按需停止，不是实验五的 K 曲线。
2. 读者能在三格对照里看见：`emitted < K` 时 request 仍向下，`emitted = K` 后这条 request 不再出现，空心尾仍在 run 里。
3. `aclose` 只被读成 cleanup。
4. Full 不被读成无穷 K，run 不被读成自己知道 K 然后停止。

任一不成立，就不要收进正文。

## 局限（图上没有证明的事）

- \(\Pi_K=(1,2)\) 是这 16 个元素的有序前缀，不是一次运行日志。窗口内容、pointer、预取到的额外项都没有画。
- 非 root `StreamProducer` 可以有 `one_slot_after_second_pull_v1` 预取；`aclose` 会取消它。图不声称“空心 = 从未被读过”。
- root 的 SW/LT 在被调用时还有自己的 `top_k` 计数。图把停止画在 drain 的 `emitted` 上，因为下一次请求是 drain 不再发出的。
- `finite.py` 不在这 8 个源里。图上没有期望公式。
- 四条 run 竖排是为了放进 178 mm 的三格，不是 \(k=2\) 的配对。
- 建议位置是新的 `figure*`，宽 178 mm。单栏约 85 mm，放不下。label `fig:limit-demand-trial` 是提议，论文里还没有。
- 本目录没有被 `main.tex` 引入。公共的 `viz/tex`、`viz/pipeline`、`viz/figures`、`viz/tests` 都没有改。
