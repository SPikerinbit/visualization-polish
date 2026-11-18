# 表格 checkpoint（E1 与既有表）

合成数字，不是实验结果。可 `\input` 的 TeX 在 `tex/`。官方类是未改的 `acmart` `[sigconf,nonacm]` 加未改的 `pvldb.sty`。没有改 `\textwidth`、边距或类。实测 `\textwidth` = 506.295pt。首页是双栏。

## 打开过的文件

- `/tmp/recovery-spec/逐图制作说明.md` 的 E1 八栏和既有表
- `/tmp/recovery-spec/给后续制作者的交接要求.md`
- `/tmp/recovery-spec/references/paper-baselines/table-abacus-table2.png`
- `/tmp/recovery-spec/references/paper-baselines/table-scise-table2.png`
- `/tmp/recovery-spec/references/paper-baselines/table-sembench-table4-meanstd.png`
- 仓库 zip 里的旧稿 `tables/exp1_full.tex`、`tables/exp1_topk.tex`、`tables/exp4_validation.tex`，以及 `exp.tex` 的 `tab:datasets`、`tab:ranking-algorithms`，`framework.tex` 里整段注释的 `tab:params`，`appendix.tex` 的 `tab:params-full`
- `paper-experiments.md` 的实验合同

没有把 `viz/tex/generated/tables.tex` 当基线。那一稿把六数据集切成两列一组。

## 原表保留

- `table*`、`\footnotesize`、booktabs、`\cmidrule(lr)` 把一个数据集的质量 / #Tok. / 秒绑在一起，末组是 Avg. Rank
- 方法用 midrule 分组，不画竖线，不加色
- 单栏表仍是 `table`：数据集、算法、参数、旧验证骨架
- 历史 label：`tab:exp1-full`、`tab:exp1-topk`、`tab:datasets`、`tab:ranking-algorithms`、`tab:params-full`、`tab:exp4-validation`
- 最佳组加粗，次佳组下划线，同组同样标记

## 相对旧稿改了什么

- 数据集换成合同里的 Q9、DL20、DL22、TREC-COVID、DBpedia-Entity、Robust04。Movies / Touché / FiQA 不进表
- Full 全部是 Spearman ρ；LIMIT 10 全部是 NDCG@10。不再在 Full 表里混 FiQA 的 nDCG
- 十行：Pointwise（即 OrderByLLM Pointwise）、Ext. Pointwise、Ext. Bubble、Ext. Merge、ListK Sort 或 ListK Select（同一方法）、Tournament、Lotus Quick、Setwise Heap、SW、LT。没有 SLT 行。`h=1` 写在 caption 里，不是第三行
- 质量是三位小数的均值 ± permutation std。Token 是逻辑 Total（input+output）的未舍入均值，显示成千分位的整数，无 ±。延迟是单次隔离运行的一位小数秒，无 ±
- 名次用未舍入均值。质量降序，并列且全员都有 permutation std 时 std 小的在前；若有人记录了 `n_permutations`，则必须全员 ≥ 2，否则不用 std。费用升序；只有全员 `n_repeats ≥ 2` 且方差是数时，才用更小的方差打破；否则用更高的质量。仍并列则占位平均（1 与 2 并列记 1.5，下一名从 3 起）。缺测不参与该列，也不进该指标的等权平均秩
- 27B 的 label `tab:exp1-full-27b`、`tab:exp1-topk-27b`，以及对照表的 label，都是建议，未批准
- `tab:params` 仍是 `\iffalse`，不进 `render/main.tex`，也不冒充 `tab:params-full`

## 布局比较（看了实际 PDF，不是测试）

同一张 9B Full 合成表，在同一 `table*` 宽度下：

- 六数据集一行、inline `mean±std`：Overfull hbox **54.17pt**，右边超出文字区
- 六数据集一行、下标 `±`：Overfull hbox **6.93pt**，仍超出，而且在 footnotesize 行距下标会压到下一行
- 模型左右并排的六数据集矩阵：半宽约 250pt，三数据集的 inline 块本身就超过半宽，放不下
- 采用的主表：一张 `table*` 里上下两段，每段三个数据集，inline `±`。这是 SCISE Table 2 的分段方式，不是把数据集切成两两一张。末段才加 Avg. Rank。每个模型一张表，9B 在上、27B 在下。Full 与 LIMIT 10 各一组，共四张主表
- 紧凑对照两张：左右只放两个模型的平均秩；单栏只放 9B Full 的 Q9 下标。下标对照能看出密度，也能看出和下划线抢行距

主表 PDF 没有 Overfull hbox。主表页文字最低点离纸边约 71pt。首页因为 PVLDB 许可脚注，最低点离纸边约 30pt。

## 数据

`data/*.json`，schema `sema.exp1.sheet.v1`。`python3 emit.py --sheet 某文件.json --out 某.tex` 吃同一 schema。`synthetic: false` 时去掉 “Synthetic layout numbers” 这一句，列规则不变。本目录里的 json 全部是 `synthetic: true`。

## 不足

- 正式数字还没有。表上的数是为了把并列、缺测和舍入陷阱摆出来
- 语料 `|D|`、Setwise 的调用复杂度、LT 的 `h` 与 `m` 的公式、验证表的 `k_cm` / `k*` / regret 都是 open，没有用旧稿数字填
- 算法表里的大 O 是拒稿草稿原文，caption 写了未对照当前实现
- 下标在现有行距下会贴到下一行，所以没有当主表
- 六数据集一行的下标只差 6.93pt。再压 `tabcolsep` 也许能塞进，但会更挤，这一轮没有改成主表
- 两段表的列不上下对齐：下段多了 Avg. Rank
- 27B 和对照表的 label 还没被同意
- 旧 `tab:exp4-validation` 仍是旧 RQ3 的空骨架，不是新的 Off/On 表。E3 的 `(k,h)` 辅助表没有做
- 首页四张单栏表加许可脚注偏满。这是渲染驱动把它们放在 `\maketitle` 后，不是改了边距
