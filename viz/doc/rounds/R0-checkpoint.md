# R0 检查点

只做这一轮。没有开始第二轮。

PDF 用官方 VLDB-Template 的 `acmart.cls` v2.19（2026/06/27）和 `pvldb.sty`（2026/07/06），未改类文件。引擎是本机 TeX Live 2023 的 pdfLaTeX，不是 TeX Live 2026，也不是旧的 `vldb.cls`。正文是 Linux Libertine，图里的字是 TeX Gyre Termes，都嵌入了。纸张 letter。18 页。大的 overfull 已消掉。页脚红字是 SYNTHETIC DATA — LAYOUT PREVIEW ONLY，不压正文。

看过第 1 页、实验表、实验五、机制图。下标表会把 ± 撞进相邻列，所以主表改成同行 ±，下标只留一块对照。滑窗图的调用序号仍贴着第一颗药丸，图注写明了行的含义。指针图六个面板不再叠字：叶子不跳到后续尾巴，刷新只填被指向的孩子，pointer 与 winner、loser 同面板写出。

11 个测试通过，覆盖舍入、并列平均名次、缺失、单次运行不造方差、曲面不跨缺角、replay 与补充点不混入固定曲线。

未做：第二套强调配色、模型左右并列、`init_plan` 和上游 `aclose` 的调用方、把合成高度说成结果。
