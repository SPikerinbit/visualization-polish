# 最终交付只读 QA

**结论：四路内容齐全、PDF/PNG同版、未证实caption硬碰撞；但不能宣布“本轮紧凑整合与交接全部完成”。需一次有界收口的是分页策略及交接状态文档，不是重画全部图。**

父提供最终身份：PR19 HEAD `f55de18cf87ea324ecb1b94eefc5486bf6a0581f`，不采用旧wrapper PR1。本轮不联网验证push/HEAD。审核时间2026-11-18（Asia/Shanghai）。已安全复制工件并解压到`source/`，Read全部十页；仅运行Poppler/PIL/标准库检查，不运行构建或工件代码，不改repo、不联系Cloud。

## 已实证通过的项目

- `round2-integration-main.pdf`为10页Letter；以110dpi独立渲染，**十张提供PNG均逐像素完全一致**，没有拿错版证据。
- 页1：通栏framework与单栏SW/LT/pointer，caption各自绑定；无独立LIMIT机制图。framework显示stop at K反向请求线。四个机制PDF hash均与最新c959d22声明吻合（不是bed819cd）。
- 页2–3：表1/表2及E1 Full/LIMIT仅两张宽表；模型、六数据集横向，各模型13列。Full caption已补“Full ranking”。未出现E4验证汇总表。
- 页4–5：五段算法齐全，无跨栏裁断、溢出或遗失；Replay三元契约、显式LIMIT缺K耗尽等修复保留。
- 页6：E2主12格，2×6；`fig-e2-exp5-container-12.tex`每格仅以`width=0.33\columnwidth`投放，入口显式恢复241.14749 TeX pt栏宽。没有height/resizebox压高，故**没有缩高误缩面板的证据**。每格约79.58 TeX pt；caption明确k/h/成本轴义。大量下白来自分页，而不是面板纵横比被挤扁。
- 页7：E3单栏4×2、标题TeX外置；`fig-e3.tex`内部局部设置subfigcapskip=1pt，未回退-7pt。无10k/n/标题重叠；刻度仍约4.6pt、图例5pt，是既有小字例外。
- 页7–9：四个E4a（DL20/COVID×n100/n500）、E4b、E4c全在。Off/On图例最先、完整kh、无色带；E4b无inset；E4c四panel及非支配红线保持。
- 页10：E5通栏4×2，Full独立断区不连500，未见明显标签碰撞。
- 无标题页、论文正文、review行号或重复独立展示图。

## 优先疑点的bbox结论：不是硬碰撞

坐标以下均为PDF bp，原点左上；XML边界有约0.33bp取整误差。

- **页8两caption无挤接。** Figure8左栏最右约x=295.67；Figure9右栏起x=318，保留约22.33bp栏间隔。两者首行同在y=435.67，末行均至498.67，是正常并排，不是串成一句。缩略图造成视觉疑似。
- **页9 E4c caption未越页底。** y=632.0–695.0；正文底约708.6，尚余约13.6bp，页码y=716.67，亦不相撞。贴近底部但没有截字，不能据此返修整张E4c。

## 当前真正需收口的事项

### 1. 整合紧凑性：有源码支撑的分页问题，不泛指所有空白

并非每张图都有clearpage，但仍存在与“不要逐图隔页、压白”不符的具体整合结果：

- **页6 E2被显式清页。** `integration/main.tex:121–128`用twocolumn banner后紧接clearpage，注释称“12-cell figure fills this page”，实际内容止y≈313.33，离正文底约395bp，约63%正文高度空置。E3因此被硬移到页7。这一处不能以“无per-figure clearpage”一概否认。
- 页3仅LIMIT表，内容止y≈295.67，下余约413bp；源中E1宽浮动表后的`FloatBarrier`（104）先排尽宽表，算法不能接其下。不是另一个隐藏newpage。
- 页5仅算法5，内容止y≈192，下余约517bp，右栏也空。算法为不可拆盒子（`algorithms.tex:21–36`的Needspace），按顺序自然落到新页；随后`main.tex:121`的twocolumn banner又清走余页。**算法5前没有显式newpage**，但整体分区策略把它孤立了。

有界结论：图件无需重绘；必须重新决定上述分区/页推进方式后，才能称“紧凑整合完成”。页1机制图/页10通栏图下白并不据此一并判错，也不要求把所有空白填满。

### 2. 下一bot文档仍有相互冲突的现行状态

- `NEXT-BOT.md:3`说四路已进壳，**第10行却仍写“未纳入：机制PR16、折线PR17”**；后面保留大段未归档seed及待补block。无法称清楚交接。
- `STAGING-HEADS.md:3`仍禁止把机制/折线混进integration，与下表“已纳入”矛盾。
- 矩阵确有**64条**，但所有最终commit/新QA列仍为待补，G01等仍记seed/待最终整合；没有实际PR19及最终HEAD回填。NEXT-BOT最终身份/源包/PDF hash/终验块亦未闭合。
- `CURRENT-DECISIONS`与`BASELINES`总体有用，已明示合成、公式未验、3D原TeX缺失和TL2023事实；但现行交接页不能要求下一个bot自行猜哪些禁令失效。应只收口状态/最终身份/当前限制，不重开已确定视觉设计。

## 已知限制：保留披露，不假装科研通过

全部实验数字synthetic；E1排列std/序位不是显著性；E4c仅数据集级占位均值；E5不是三query复算。Table2成本公式与Expect未核，Setwise缺式。原3D k-sweep TeX未定位，E2复用的是2D exp5-m容器，不能声称原3D只换图已完全满足。当前引擎明确为TeX Live2023，不是合同TL2026；这是已披露但**未满足的环境要求**，不能把新acmart类日期当引擎升级。历史Qwen3.8/当前Qwen3.5身份仍需真实部署manifest解决。上述不妨碍交接现有图源，但不得称全部合同/科学验收完成。

## 文件与复现定位

本地完整审核目录：`/workspace/paper-materials/round2-final-review/`。
源码入口：`source/paper/round2/integration/main.tex`；构建说明入口：`source/paper/round2/integration/build.sh`；vendor在`source/paper/tex/vendor/`。静态核查其相对输入路径与随包资源存在。作者复现命令为从源码根进入`paper/round2/integration`运行`./build.sh`；本轮**没有执行**。脚本两遍pdfLaTeX，不重画图；当前PDF Producer也确为TL2023。复现路径不等于TL2026已验证。

### 最终文件 SHA256

- `round2-integration-main.pdf` `558d290327542773e816191fda0836d050f1b73770cb6ed140354613eb6c0d5c`
- `round2-integration-src.zip` `c2b6c3ef620021fb5d43dc7c8a5f46185721fe2e1a5b79af1e6a9a815efc9d08`
- `round2-page-01.png` `f3095a5381e4364ad69ae8ed37766a942e5459997fdd10c7073fbb01d6462e01`
- `round2-page-02.png` `1e9948bc909a83d896026ecceee9c1d3cf9b1db5feabeae3b80b14960429bb02`
- `round2-page-03.png` `14cdbf14a669d325264f6376fa97f0edfb8df8cbf6e268ebcf4845198f6e76e0`
- `round2-page-04.png` `1ab5e046ecc3c7523e533a8d3e305c6d9894a999d302745640e0de7231a0f011`
- `round2-page-05.png` `ec722ac96b247363718924aafa65b73f094b262cf04ea8aaff7467bac65f9980`
- `round2-page-06.png` `ac908712fd0522ee275bc9675c4e1c0d237e2a283009f2694bdff7decce62c83`
- `round2-page-07.png` `41d0f003bbeecbb8719f7402a8c816c629d4ee08bb9ca73a98e61ddbac663ef0`
- `round2-page-08.png` `6b0ee6d91a650a18d4464b7de6156515bda9484043b664711bc0be79b54bfae7`
- `round2-page-09.png` `d5dafe8b2f69413daeff2a842b7588ceb6bff9afb036ed6c4d13979558ffc3e3`
- `round2-page-10.png` `2b941e0f955eaa6d1323a076501fe21aba17cc97216da93fef18e5f17b10234d`
