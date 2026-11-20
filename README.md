# Semantic ORDER BY 论文与图表

**当前论文入口是根目录的 [main.tex](main.tex)。** 编辑正文、图注或表格时，从下面对应的文件进入。仓库中另有早期论文工程和独立图稿，根目录主稿不依赖它们编译。

| 我要做什么 | 从这里开始 |
| --- | --- |
| 改引言、问题定义或算法 | [Introduction](inrto.tex) · [Preliminaries](problem%20statement.tex) · [多路归并、SW 与 LT](framework.tex) |
| 改成本模型或推导 | [Token Cost Model](manuscript/cost.tex) · [附录与证明](appendix.tex) |
| 改实验设置或填写结果 | [Experimental Setup](manuscript/experiment-setup.tex) · [E1–E5 结果分节与图表引用](exp-body.tex) |
| 改图注、换图或改表 | [图注与伪代码](manuscript/) · [主稿引用的图件](fig/) · [论文表格](tables/) |
| 找某张图的制图材料或历史版本 | [图表与历史资料索引](doc/README.md) |

**实验状态：** E1 的两张表及实验图中的数值是合成的排版示例，不是实测结果；E1–E5 的结果正文尚未填写。

## 编译当前稿

- **Overleaf：** 主文件选根目录的 `main.tex`，编译器选 **pdfLaTeX**，TeX Live 版本选 **2026**。
- **本地：** 在仓库根目录运行 `sh build-manuscript.sh`，生成 `main.pdf`。[脚本](build-manuscript.sh)检查引擎版本，运行 pdfLaTeX 和 BibTeX，并检查未解析的引用和版面溢出。
- **单独打包：** 保留根目录的 TeX 文件、`ref.bib`、原模板的类与参考文献样式文件，以及 `manuscript/`、`tables/`、`fig/`。不需要原始 ZIP 或 `paper/`。当前稿沿用原模板的 ACM 双栏审阅版式，不是 camera-ready 稿。
