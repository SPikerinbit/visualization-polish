# E2 最后只读复核

**结论：主12图可进入整合。** 本次仅解压、读PDF/文本/bbox、render与测量；未改源码、未编译、未重绘、未云端操作。版本标签为提供的 `05f921f20c634dbb4d6e05eb5f4003d17f354183`，未做git commit验证。

- **轴语义通过**：12个panel均有前底轴k、向深度轴h；主PDF caption明确“Front axis k (fan-in), depth axis h (segment length); vertical tokens ×10³”。高分辨实图与文本一致。
- **字号/裁切通过**：主图嵌入刻度5.357pt、图例6.806pt；全部12个源panel用无限clip查文字bbox，均未越133.2pt页界。主12图render也未见轴字或数字被邻图裁挡。
- **留白改善属实**：沿用上轮10倍render、灰度<245的实际可见内容口径，p01上17.2pt、下10.2pt，合计约20.57%；作者矢量口径20.39%，差异为栅格/阈值口径，可视为所报20.4%已达到（上轮37.0%）。
- **baseline修复通过**：实际panel宽79.282pt；第一、二origin为66.092/144.724pt，步长78.632pt，重叠0.650pt；高分辨前两格右框及30刻度完整，不再发生旧5.13pt覆盖。
- **面积对照可用**：新对照是相同物理比例、完整二维exp5-m对完整E2，并非纸张/封面对照。独立联合文字与矢量路径bbox（不加stroke外扩）测得两组主体同宽479.816pt，含caption高度原238.966pt、新240.061pt，差约0.46%。作者含stroke边界约239.91/240.96pt，结论一致。旧234.4/233.7pt数据已明确撤回。

## PNG字节矛盾已定位，不阻塞主图
ZIP内 `out/e2-figure-12.png` 与 `out/e2-layout-2x6.png` **确实相同**，均162298 bytes，SHA256：
`cddf9a1a1a4fd305cb5971ecb4485b2cbc4028d61293feb968f8aacfff99675f`
外附figure12 PNG也完全匹配；但外附layout别名 `01M7PP4PYWYNSK9J2M1P8VX9ZF.png` 是131758 bytes，SHA256 `5b0a4740e0687377f2021a0d04945566a19330fdbb73c67eaf99d5a832034277`，不是ZIP最新版。**废弃这份外附别名，不能据它否定当前主图；无法仅凭文件判断缓存/复制环节成因。**
外附PDF与ZIP `out/e2-vldb-preview.pdf`字节完全一致：355530 bytes、2页12/10格；独立主12图PDF为1页。

## 当前实际主图与证据
- **本次直接从主PDF重新render**：`/workspace/paper-materials/round2-e2-independent-audit/final/audit/current-main-12.png`
- 主PDF：`out/e2-figure-12.pdf`；正确主PNG：`out/e2-figure-12.png`。
- 细节：`audit/p01.png`、`audit/baseline-first-two.png`、`audit/main-bbox.html`。

整合仍明确两项例外：**synthetic、不是实验结果；原3D k-sweep TeX容器仍未找到，当前参照为二维exp5-m。** 保持逐panel原生TeX缩放，不能把裁后的整张PDF强制铺宽后仍声称字号完全不变。本次不要求新增设计迭代。
