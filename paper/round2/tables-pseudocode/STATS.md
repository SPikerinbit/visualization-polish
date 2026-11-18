# 统计复算说明

正式评测数据不在本目录。`src/synthetic.py` 生成的是合法合成版式，schema 为 `sema.exp1.sheet.v2`，审计为 `sema.exp1.audit.v2`。表题、审计字段 `synthetic` 和本说明都写明：表中数字不是测量结果，序位也不是显著性。

## 数据从哪来

- 排序实现：`src/ranking.py`。输入拒绝浮点，均值和名次用 `Decimal` / `Fraction`。
- 合成表：`src/synthetic.py` 的 `build_sheets()`。两个模型 `Qwen3.5-9B`、`Qwen3.5-27B`，两种需求 `full` 与 `limit10`（K=10）。
- 排版：`src/emit.py` 写出 `tex/generated/exp1-full.tex`、`exp1-limit.tex` 和 `exp1-audit.json`。显示位数必须与未舍入值一致，否则生成直接失败：质量三位小数，token 组内求和以千为单位两位小数，latency 两位小数。
- 复算：`PYTHONPATH=src python3 -m unittest discover -s src/tests`，然后 `PYTHONPATH=src python3 -m emit`。

六个数据集的顺序固定为 Q9、DL20、DL22、COVID、DBpedia、Robust04。Token 三列是组内求和，不是三个 benchmark 各投一票：Q9 只有 Q9；TREC 是 DL20+DL22；BEIR 是 COVID+DBpedia+Robust04。Latency 列是六集等权平均，单位秒。

## 序位规则

每个模型、每个需求、质量 / token / latency 各自独立排序。

1. 数据集内部按未舍入均值排名。质量越大越好，token 和 latency 越小越好。完全相等用 midrank。排列标准差不在这一步拆平局。`n_repeats < 2` 的重复方差不使用。
2. 主键是六集 midrank 的等权平均，用分数保存。印出的整数是这个顺序上的竞赛名次：1 加上严格更好的方法数。它不是平均名次的四舍五入。任一数据集缺失则该方法在该指标上不合格，印 `---`，不用其余五集重新加权。
3. 主键相同才看次键。质量：把 Spearman 写成 `(ρ+1)/2`，或使用仍在 `[0,1]` 内的 nDCG，再取六集平均，越大越好。nDCG 超出 `[0,1]` 直接拒绝，不做 min-max。Token 和 latency：六集均值的平均，越小越好。禁止用三个 benchmark 组名次的平均来排序。三组求和与六集总和成比例，可以用；被禁止的是三组名次再平均。
4. 次键仍相同：按 Q9、DL20、DL22、COVID、DBpedia、Robust04 的原始均值做字典序，方向与该指标一致。
5. 六维向量仍相同，并且每个并列方法在六个数据集上都有合法重复次数时，才用更小的平均排列标准差（质量，且 `n_permutations ≥ 2`）或更小的平均重复方差（token / latency，且 `n_repeats ≥ 2`）拆开。
6. 到这里仍相同：共用一个整数，下一个整数跳过。方法名、显示舍入、随机顺序都不是键。

## 三个可复核的例子

以下分数来自 `tex/generated/exp1-audit.json`，不是手填进表的。

Qwen3.5-9B Full 的 Pointwise 质量 midrank 是 2、2、2、1、1、1，等权平均正好是 3/2。竞赛名次是 1。若把 1.5 四舍五入会得到 2，表中印的是 1。同表其余质量平均名次也不是印出的整数，例如 Ext. Pointwise 为 5/3，Ext. Merge 为 23/6，SW 为 109/12，LT(h) 为 119/12。

Qwen3.5-9B Full 的 token：ListK 与 Tournament 的六集平均名次都是 11/2。六集均值 Tournament 为 1605，ListK 为 1750，所以 Tournament 的整数是 5，ListK 是 6。三组求和（千）ListK 为 1.40 / 3.10 / 6.00，Tournament 为 1.41 / 3.12 / 5.10。若改成三个组名次再平均，ListK 会因为 Q9 和 TREC 两组更小而排到 Tournament 前面。表没有采用这个键。

Qwen3.5-9B Full 的 latency：只有这一张表把 SW 的六集 latency 复制给 LT(h)。两者平均名次都是 19/2，六集均值都是 4.95，整数都是 9，没有方法占据 10。其余三张表的 latency 整数是 1 到 10，不共用。DL20 上 SW 与 LT(h) 的质量均值都是 0.670，标准差分别是 0.030 和 0.011；标准差不拆数据集内的并列，所以这一对 midrank 相同。

合成单元格的 `n_repeats` 为 1，重复方差为空，因此第 5 步的方差键在这些印出的表上不起作用。测试覆盖了：标准差不拆数据集内并列、向量完全相同后合法标准差或重复方差可以拆开、`n_permutations = 1` 时不用标准差、颠倒方法名不改变整数、缺一个数据集会使该方法不合格。
