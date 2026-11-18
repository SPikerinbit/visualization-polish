# 历史：机制只读 QA 未通过

状态：**失败记录**。整组不得进入 `paper/round2/integration/`，也不能把 SW 单独先标成最终入口已通过。本文不覆盖以后新 HEAD 的终验；新的通过必须另写记录，不能改这份结论。

版本：PR16 `cursor/round2-mechanisms-6f22` `bed819cdfc20c2df5ed067dbd120119daf74bcc6`。父已把有界局部返修发回原制作任务，等新 HEAD 再验。

# 机制图只读短复核

**结论：不能整组准入；SW可准入，LT、pointer与framework仍有明确局部阻塞。** 仅复制解压、读现存源/PDF和高分辨render；未改repo、未执行绘图代码/编译、未回复cloud。提供版本标识：PR16 / `cursor/round2-mechanisms-6f22` / `bed819cdfc20c2df5ed067dbd120119daf74bcc6`；未用git核SHA。包内ACCEPTANCE还写7fe71c8，不据此判断当前PDF，而以实际文件为准。ZIP内四图及preview PDF均与artifact目录同名副本SHA256一致。

## 已通过
- **真实尺度/字号已修**：SW=240×96bp、LT=240×124bp、pointer=240×150bp；SW正文6.5、标题7bp；LT主体6.5bp。preview中缩放1.00105，实字6.507/7.007bp，不再是旧4.1pt。单栏实际约240.25bp=241.15 TeX pt，与241.14749pt目标吻合；framework缩放1.00002，约506.295 TeX pt通栏。
- framework源图177.94×42mm≈178×42mm，扁平通栏、低高度。抽象runs→两层merge→Full/LIMIT正确；cost model三条蓝虚线分别落在三个merge；红虚线的左段箭头**确实落回根merge**，不是只悬空到附近。
- SW与原`fig-F-sw-v2`逐轮数字/三状态拓扑相符；未见新的标签相撞。pointer的2×3、数值、粗指针、L/R、共享winner/loser图例、Build R / Refresh L耗尽标识均保留。四源PDF文字bbox未越页界。

## 剩余阻塞（不能由“修复完成”报告覆盖）
1. **LT粗指针拓扑被改，违反v2不变。** 对照原`fig-F-lt-unified-v2.pdf/png`：
   - 三个状态的右节点[8,9]，原均指向左叶R3=[11,15]，新版均改为右叶R4=[10,13]。
   - Updated state根[5,6]，原指向右子[8,9]，新版改指左子[7,14]。
   - 原数字保留不代表拓扑保留；已有源码`src/build_svgs.py:349-363`的`right-1`及updated `root-left`与高分辨PDF一致。应恢复原v2指针，不由审阅方推断另一算法版本。
2. **pointer标签仍有真实叠字/箭头撞字。** Build和Refresh左侧State的P均画了两遍，相隔约2.8/3.4bp，渲染像“B/叠P”；源`state()`先无emit画P，随后parent分支又画P（398、400、405行）。Build Updated state的R、Refresh State的R和Updated state的L还压在粗箭头端附近。需消除重复P、把L/R从粗指针端移开；不必改2×3或数值。
3. **framework的K仍是孤立红刻度，停止语义未真修。** 红请求已经回根，这一半通过；但源`framework.tex:58-61`红线到x=128mm为止，另一段从116mm开始，K竖杆在122mm，两侧各空6mm。实图即12mm大空隙中央一根孤杆，仅标K，没有stop/达到K停止文字，未与请求线形成明确门闸；仍符合上轮退回的“孤立红刻度”。应在现有路径上把K停止标义与请求路径直接关联，无需重设计。

## 预览交接问题（非图本体拓扑）
preview.pdf第2页LT图在左栏下方，`Figure 3: LT(h)` caption却被分页到右栏pointer上方。源preview用连续center/captionof，发生跨栏拆分；不能直接把这张预览当作最终整合排版通过。实际四图高度96/124/150bp及119.054bp未见无故放大；framework小框文字实测约5.978bp（非报告声称的6.5），字号上调要求目前针对SW/LT，故不单列为新阻塞。

## 实际复查图
本目录`/workspace/paper-materials/round2-mechanisms-review/revised/`：
- `audit/preview-2.png`：真实栏宽与LT caption错栏。
- `audit/lt-360dpi.png` 对 `audit/original-lt.png`：指针拓扑差异。
- `audit/pointer-360dpi.png`：重复P及L/R撞箭头。
- `audit/framework-360dpi.png`：红线回根已修、K仍隔空。
- `audit/preview-bbox.html`：pdftotext bbox。

建议交接：仅三处局部修正（恢复LT原指针、清pointer标签、把K停止接入语义）加预览caption绑定；不再开新一轮构图/视觉研究。
