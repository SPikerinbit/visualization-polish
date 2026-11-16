# 算法图 · 第三版

## Pointer rule 独立精修

当前 Pointer rule 已按两行三阶段重新排版：去掉 Replay 外框和大型空心箭头，沿用全套图的圆形元素及段容器。三列标题与 SD / LT 一致，采用 29 单位、600 字重、#262b30；Build / Refresh 使用更小、更浅的辅助样式。按照最新修改意见，耗尽位置使用细强调色短线及引线，连接到 Exhaustion point 注释；耗尽方向仍用深色文字说明。红色实线表示局部耗尽事件，其他图中的红色虚线框仍表示调用范围。

此图可用 `build_pointer.mjs` 单独重建；只更新 Pointer rule 的 SVG、PDF、PNG 和工作台中的对应部分。旧版保存在 `pointer_previous`。其他四张图未改动。当前单栏 PDF 宽 88 mm，高约 67.8 mm。树边为 #AAB1B7、0.8 pt，pointer 为 #303840、1.4 pt（按 PDF 实际物理尺寸换算）；箭头头部比此前缩小约 13.5%。树边端点计算至段容器边缘，不延伸至节点内部。

本次只修改图，没有修改论文 LaTeX、正文或伪代码。上一版保留在同级 revision_v2 目录。

本版微调：Algo1 的三个归并框直接写入 MergeGroup，移除 one group merge 图例；SD 的 retained 元素下方增加横线，并以同一条平滑路径连接到下一轮调用框。LT 和 Pointer rule 沿用第二版。

打开 `index.html` 查看和编辑五张图：

- `intro_execution`：最新 Intro，置于工作台首位。数字与对应圆形、段内元素已经分组，支持文字修改、分组拖动、撤销和 SVG 保存。原始图来自 intro_kh_motivation/revision_v3，视觉内容保持不变。

- `algo1_exp`：圆角矩形内直接标注 MergeGroup，底部只保留 one listwise call 图例。
- `sd_merge`：保留三轮归并；下横线只覆盖 retained 尾部，并自然过渡为下一轮的输入箭头。
- `lt_unified`：阶段标题置顶加粗，独立算法图，底部增加图例。
- `pointer_rule`：两行展示同一节点的建树和刷新，显式展示逻辑槽位映射及 pointer 翻转。

每张图提供 SVG、PDF、PNG。前三张 PDF 宽 178 mm，Pointer rule PDF 宽 88 mm，适合单栏。

## 编辑

点击“编辑文字与位置”，双击文字修改、拖动分组、撤销。通过“保存 SVG”下载当前修改。页面中的 PDF / PNG 链接是本版静态导出，不会随手动编辑自动更新。

SVG 保留文字、独立形状、命名分组和曲线路径，可用 Inkscape 或 Illustrator 深入修改。拖动分组时连接线不会自动重排。

`figure_data.json` 保存示例数据、配色与画布尺寸。`build.mjs` 保留可重复生成的源文件；本版默认重新导出 Algo1 和 SD 的 PDF、PNG，同时更新四图的 SVG 与编辑页。重跑不会合并在下载 SVG 中进行的手动修改。

## Pointer rule 的读法

第一行：L=[3,7]，R=[1,5]。完整局部次序为 1_R,3_L,5_R,7_L。R 在第 3 项先耗尽，故 pointer=R；向上传递 [1,3]，父节点保留 [5,7]。

第二行：旧 pointer=R。新右段 [6,14] 进入逻辑槽位 R，父节点保留段 [5,7] 进入相反的逻辑槽位 L。完整局部次序为 5_L,6_R,7_L,14_R。L 先耗尽，pointer 从 R 翻转为 L；向上传递 [5,6]，父节点更新为 [7,14]。实际左孩子的 [12,16] 不参加本轮 replay，以浅灰表示。

红色短线标出首先完成 h 个元素扫描的槽位的最后一项。L/R 标签表示本轮 replay 的逻辑槽位，不代表元素最初的 run 来源。Node replay 使用已有 rank map，不表示额外的 LLM 调用。蓝色 winner 在局部图中表示向上传递，尚不等同于全局最终输出。

数字轨迹保存在 `validated_states.json`，随生成过程核验。
