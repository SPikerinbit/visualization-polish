# 折线父准入记录（不是舒适字号或实测通过）

以下是父附只读复核原文。图段已从 `22b432ca01054da271366518d5ba6684795b1b20` 的 `paper/round2/experiments/` 纳入整合壳。E3 在自己的 float 里设置 `subfigcapskip=1pt`，没有继承旧主模板的 `-7pt`。这不是实验结论通过，也不是无条件字号通过。

# E3–E5 最新工件只读准入复核

**结论：图件可进入无正文模板整合；有一项必须保留的 E3 排版前提。不是实测、最终论文排版或统计结论通过。**

随附版本为 PR17 / SHA `22b432ca01054da271366518d5ba6684795b1b20`（本轮未联网核对远端）。安全解压到本目录，未覆盖旧稿。实际 Read 了提供 PDF 渲染的全部8页及局部放大、原参考图；只读源码/JSON，未执行工件代码或测试、未重新编译、未改 repo、未回复 Cloud。包内 `tex/preview.pdf` 与另附编译 PDF 的 SHA256 相同：`b965ef31d648ce59d4b12621ed709d067f8488d1fa1a003786407aa4f2b393ab`。

## 逐页检查

|页|实际内容|准入判断|
|--|--|--|
|1|E3，单栏4×2|八图齐全，预测/实测分两行；SW/LT与Full/LIMIT由TeX排标题；一行十项图例、白底灰网格。实际10k、n、子标题已分开，无前稿覆盖。|
|2–5|E4a：DL20 n100、COVID n100、DL20 n500、COVID n500|四组均在，无遗漏COVID n100。完整(k,h)共用横轴，图例先Off/On再Predicted/Measured；无色带。|
|6|E4b|单栏，白底灰网格；无色带、无inset；五条beta曲线与两种最小值标记可辨。|
|7|E4c|单栏2×2；两种需求×cache状态，不再按数据集展开；确实存在。|
|8|E5|通栏4×2；四列为DL20 Off/On、COVID Off/On，费用/质量上下两行；Full独立断区，仅点不连500。490/500旋转标签能分开，未见明显碰撞。|

## 物理尺度、风格与小字风险

PDF为Letter 612×792bp。容器对应栏宽241.1475 TeX pt、通栏506.295 TeX pt。E3每个面板盒约60.29 TeX pt；实际绘图区约44×34pt，线约0.72pt、点径约2.17pt。PDF文本测量刻度约4.6pt、图例5pt、n约5pt，TeX子标题约6pt/7pt。**线条走向、点形在原尺寸可辨，但(k,h)图例和刻度仍是全套最小字，不能等同普通7pt正文的舒适可读性。** 本次以用户指定60pt四列容器为准，可准入整合，不宣称已达到无条件视觉终验。

E4a图件约241×340pt、刻度6pt、图例6.2pt、轴题/小标题7pt；E4b约241×168pt、刻度6.4pt、轴题7.2pt；E4c约241×310pt、刻度6.2pt、图例5.5pt、轴题7pt。E5图件约506×295pt，刻度5.5pt、标题/图例7pt，线0.96pt、点3.6pt。以上未含TeX总caption，PDF测量受XML取整约有0.3pt误差。

已对照原Fig.8面板及原折线参考：保留Tableau色、SW红圆/LT蓝三角、衬线字、细灰网格；E3线宽对齐原0.25栏档，E4/E5约0.96pt对齐原0.33栏档。E5双行/断区构图得以保留。字体为Liberation Serif/STIX，不是Times New Roman；E3网格、边框与线的相对视觉重量仍偏强，但没有新增硬碰撞。

## E4c 独立语义复核

读取本地既有 `paper-integration-review6/paper/recovery/e4c/data/synthetic_means.json`，独立重算40个方法均值，费用/质量分别按DL20、COVID各1/2，与facts中的40点一致（浮点误差<1e-12）。静态代码也明确使用两集各一个数据集级均值，不是逐query池化。独立重算非支配集合（费用不增、质量不减且至少一项严格）：

- Full Off：LT(20400, .540) → SW(21250, .740) → ListK(28350, .745)。
- Full On：仅SW(19100, .745)，无红线段。
- LIMIT Off：仅SW(19500, .705)，无红线段。
- LIMIT On：SW(18500, .705) → Tournament(25250, .715) → ListK(29250, .720)。

与实际红虚线及facts一致；代码只连接上述点，不外推、不加轴端点。全体方法点均在轴限内部，所连均值和线段未越界。两张无红线的panel不是漏画。它是合成均值上的描述性非支配集合，不是拟合、置信带或显著性。

## 阻塞、非阻塞与整合边界

- **未发现阻止图件进入模板整合的新硬碰撞或缺图。**
- **E3整合前提：** 无碰撞预览使用 `subfigcapskip=1pt`；原主模板为-7pt。`fig-e3.tex`本身未封装这个设置。若仅拷贝图段而继承-7pt，n/子标题可能重新覆盖，不能沿用本次准入结论。预览为验图临时重定义endfigure并clearpage，不能据此声称最终模板浮动队列已正确。
- 非阻塞：E4a中间(k,h)刻度与轴题字框接近，实际字形仍分开；caption较长、E4a本体340pt，并不低矮。当前强制换页的大块空白不提前作为成稿阻塞，但整合后仍须复核总占用与8组覆盖。
- 科学缺口：全部synthetic，caption明确披露。E3预测=实测+3.4、Full/LIMIT同数；部分LT补充点未绘出；E4a真实选点后置、n100为合法性重算，最低点仅针对显示子集；E4c源仅为数据集级占位、无3-query原始记录；E5不是三query均值。均不能据此报告真实准确性或性能优势。

## 可整合准确路径

根目录：`/workspace/paper-materials/round2-lines-review/revised/`。

- TeX片段：`tex/fig-e3.tex`、`tex/fig-e4a.tex`、`tex/fig-e4b.tex`、`tex/fig-e4c.tex`、`tex/fig-e5.tex`。
- 对应PDF：`figures/e3/*.pdf`（八面板及legend）；`figures/e4a/e4a-{dl20,covid}-n{100,500}.pdf`；`figures/e4b/e4b-beta.pdf`；`figures/e4c/e4c-quality-cost.pdf`；`figures/e5/e5-limit-sweep.pdf`。
- 本次实看页：`review-render/page-1.png` 至 `page-8.png`。整合应消费图段/图件，不将带review行号及强制分页的预览入口当最终入口。
