# Semantic ORDER BY 论文与图表

**当前论文入口是根目录的 [main.tex](main.tex)。** 编辑正文、图注或表格时，从下面对应的文件进入。仓库中另有早期论文工程和独立图稿，根目录主稿不依赖它们编译。

| 我要做什么 | 从这里开始 |
| --- | --- |
| 改引言、问题定义或算法 | [Introduction](inrto.tex) · [Preliminaries](problem%20statement.tex) · [多路归并、SW 与 LT](framework.tex) |
| 改成本模型或推导 | [Token Cost Model](framework.tex) · [附录与证明](appendix.tex) |
| 改实验设置或填写结果 | [实验章节：Experimental Setup、E1–E5 与图表引用](exp.tex) |
| 改图注、换图或改表 | [机制图与伪代码](framework.tex) · [实验组图](manuscript/) · [主稿引用的图件](fig/) · [论文表格](tables/) |
| 找某张图的制图材料或历史版本 | [图表与历史资料索引](doc/README.md) |

**图件版本：** 根目录 `fig/` 只保留主稿实际引用的 PDF，按 `framework/`、`mechanisms/`、`experiments/` 分组，实验图再按图号整理。Fig. 1 使用 54 条评论的验收版；Fig. 2–7 来自审阅分支 `ba520c9`；Fig. 8–10 来自 11 月 25 日整稿验收版。当前图件已叠加 11 月 26 日统一配色与排版修订，Fig. 2 的黄色节点标出 MergeGroup 接口。过往版本可从 Git 历史找回。五份算法保留原 `main` 的手写伪代码，行号说明与示例在 `framework.tex`。

**实验状态：** E1 的两张表及实验图中的数值是合成的排版示例，不是实测结果；E1–E5 的结果正文尚未填写。

## VLDB 2027 投稿格式

根目录使用 [VLDB 2027 / PVLDB Volume 20 官方模板](https://github.com/vldbproceedings/VLDB-Template/tree/39c95f5c6fcbe652a83be24e4eff8f2134cd3fbc)，附带的 `acmart.cls`、`pvldb.sty` 和 `ACM-Reference-Format.bst` 与该版本一致。首页的 PVLDB Reference Format 和版权许可由 `\vldbtopmatter` 生成。Framework（Figure 1）安排在第 2 页页首，附录置于参考文献前，以便核查页数。

**投稿前：** 核对 `main.tex` 与 CMT 中的作者顺序和单位，并按[官方投稿指南](https://www.vldb.org/2027/submission-guidelines.html)提供实验复现材料或说明例外。稿件中的 DOI 和页码使用官方占位符。实验数据、正文或署名变动后，重新检查 12 页限制（含附录，不含参考文献）。

## 编译当前稿

- **Overleaf：** 主文件选根目录的 `main.tex`，编译器选 **pdfLaTeX**，TeX Live 版本选 **2026**。
- **本地：** 在仓库根目录运行 `sh build-manuscript.sh`，生成 `main.pdf`。[脚本](build-manuscript.sh)检查引擎版本，运行 pdfLaTeX 和 BibTeX，并检查未解析的引用和版面溢出。
- **单独打包：** 保留根目录的 TeX 文件、`ref.bib`、`acmart.cls`、`pvldb.sty`、`ACM-Reference-Format.bst`，以及 `manuscript/`、`tables/`、`fig/`。不需要原始 ZIP 或 `paper/`。保留根目录结构，勿用早期 ZIP 中的 ACM/SIGMOD 模板覆盖。
