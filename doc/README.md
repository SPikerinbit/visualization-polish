# 图表与历史资料索引

[返回论文首页](../README.md) · [当前主稿](../main.tex)

## 主稿中的图表

改图注或子图顺序，先看下表的 TeX 文件；换图面，再沿其中的 `includegraphics` 和 [实验分节中的图目录](../exp.tex) 找到实际 PDF。同名旧稿或独立预览不会自动更新主稿。

| 对象 | 当前主稿中的入口 |
| --- | --- |
| Framework 与完整归并示例 | [总览图](../manuscript/fig-framework.tex) · [Algorithm 1 执行过程](../manuscript/fig-merge-trace.tex) |
| SW、LT 与指针回放 | [SW](../manuscript/fig-sw.tex) · [LT](../manuscript/fig-lt.tex) · [指针](../manuscript/fig-pointer.tex) |
| E1：完整排序与有序前缀 | [Full 表](../tables/exp1_full.tex) · [LIMIT 表](../tables/exp1_topk.tex) |
| E2、E3：成本预测与规模 | [E2 成本曲面](../manuscript/fig-e2-exp5-container-12.tex) · [E3 输入规模](../manuscript/fig-e3.tex) |
| E4：前缀缓存 | [缓存开关](../manuscript/fig-e4a-C2.tex) · [命中折价](../manuscript/fig-e4b.tex) · [质量与成本](../manuscript/fig-e4c.tex) |
| E5：改变输出行数 | [LIMIT 与 Full 的成本图](../manuscript/fig-e5.tex) |

## 重画与追溯

- **找制图源文件：** 第二轮制图材料按[机制图](../paper/round2/mechanisms/)、[表格与伪代码](../paper/round2/tables-pseudocode/)、[E2 曲面](../paper/round2/e2/)和 [E3–E5 实验图](../paper/round2/experiments/)分组。目录中有不同方案；导出前先用上表确认当前主稿引用的是哪一版。
- **查设计依据：** [实验图表配置说明](round2/EXPERIMENT-VISUALIZATION-CONFIG.md)记录布局和数据对接建议；[第二轮交接与审阅记录](round2/)保留当时的决策。判断当前实验设置，请读[主稿 Experimental Setup](../exp.tex)，不要把历史样例当成测量。
- **查旧版本：** [早期论文工程](../paper/tex/)、[独立可视化工程](../viz/)和[恢复材料](../recovery/)分别保存旧稿、独立预览和恢复过程。这里的入口用于追溯，不替代根目录主稿。
