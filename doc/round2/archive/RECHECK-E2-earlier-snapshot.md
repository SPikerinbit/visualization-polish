# E2只读复核简报

**结论：主要技术阻塞已修；仍不宜作为最终图直接整合。补齐轴语义，并修正原2D面积参照后即可进入整合；不需要整体重设计。** 全部仍为synthetic，原3D k-sweep容器仍未找到。目前复用的是二维exp5-m容器，不应混称。仅读文件、测量、render/crop；未改repo、未重绘、未编译。

## 已核实修复
- 新ZIP `out/e2-vldb-preview.pdf`确为2页，分别2×6、2×5，无封面/空白页/混排。外附PDF与ZIP副本SHA256完全相同，外附12格PNG也与ZIP `out/e2-layout-2x6.png`完全相同。独立12格PDF为1页。
- 实际嵌入刻度5.357pt，图例6.806pt，子图题6.974pt；接近所报5.36/6.81pt。12个panel无限clip全文bbox均在各自133.2pt页界内，p01高分辨显示160/200/240完整，旧裁字问题已修。
- 提醒：preview用CropBox裁图，底层MediaBox仍612×792pt；`pdftoppm`不加`-cropbox`会显示底层整页空白，不能据此误报新版多余空白页。交付PNG及正常CropBox显示无此整页问题。

## 剩余三点
**1. 轴语义缺失，属于必须修复项。** k/h标签确实完全没有；不是缩略遗漏：当前源码明确x/y/z label=False，PDF只有数字，caption也只说明tokens×10³。至少在TeX公共标注/紧凑caption中明确“前底轴 fan-in k、右向深度轴 segment length h、竖轴cost tokens×10³”，最好让方向直接对应图轴。不能让读者猜哪轴是k/h。

**2. 3D图内上下空白可压，不是同尺寸面板不可避免。** 在相同133.2pt源panel上，10倍render按灰度<245的实际可见内容bbox测量：
- 新p01：y=27.6..111.5pt，顶部27.6、底部21.7pt为空；上下合计49.3pt，即面板高37.0%。缩进原TeX后相当于每格上16.4、下12.9pt，合计29.3pt。
- 原二维p01：y=2.7..125.8pt，上下合计10.1pt（7.6%）。新图可见内容高度83.9pt，原123.1pt；所以父观察到主体明显偏小是客观的。
- 这49.3pt是空白的几何上界，不等于都能删：补轴语义和边界安全要占一部分。两排累计约58.7pt物理空白提供了压缩余地；不必因3D而全部保留。只裁上下空白/调整既有面板边界即可评估，不需改构图；不可直接紧裁再无条件按新宽度放大，否则字号尺度又变。

**3. 对照原2D右边框被切，不是原panel源图坏，也不是比较PNG最外裁切。**
- `unpacked-paper/fig/panels/exp5/exp5_movies_full_tokens.pdf`单独高分辨render四框完整。
- 新 `tex/exp5-baseline-same-env.pdf` p2里第一、二等panel右边已被截断；故PNG只是如实显示了有问题的重编参照。
- 量得每panel宽79.282pt，但第一到第二origin步长74.149pt，panel互相覆盖5.133pt；后一panel不透明白底遮住前一panel的右框/末位刻度。其TeX把原来多行subfigure内容压成同一行，保留负hspace，未原样保存原容器空格语义。此前正确baseline的对应步长78.632pt，仅重叠0.650pt、源图右框完整。
- 因此所报234.4/233.7pt虽可重现“文字bbox高度近似”，**不能验收为正确同容器面积对照**：当前bbox函数仅并文字/位图、不含矢量绘图，而且原参照已遮挡。用现存正确baseline或恢复原TeX字节级布局参照，再以统一版宽/完整图形bbox比较即可；不需要新视觉研究。

## 整合注意
原TeX的native版宽约504.4pt、每格79.282pt，以上5.357pt是该原生尺度。新版独立12图PDF的CropBox宽469.58pt；若作为整张图强制放至506pt，文字会再放大约7.8%（约5.77pt），不再是原生5.36pt。建议整合时用逐panel TeX容器，不把裁后整张PDF当作原容器原样尺寸。

## 最少复查图（相对本recheck目录）
- `out/e2-layout-2x6.png`：实际交付12图。
- `audit/cropped-preview-1.png`、`cropped-preview-2.png`：pdftoppm加-cropbox的真实两页。
- `audit/new-panel.png`：p01完整刻度、图内空白。
- `audit/original-panel.png`：原二维源panel，右框完整。
- `audit/baseline-first-two.png`：重编原参照内被后图覆盖的右框。
- `audit/measurements.json`、`preview-bbox.html`：本次测量/bbox。
