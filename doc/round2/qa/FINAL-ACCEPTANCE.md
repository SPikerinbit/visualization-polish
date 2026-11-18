# 本轮版式验收（有例外）

状态：本轮无正文壳的版式验收完成。不是科研验收，也不是 TeX Live 2026 合同通过。

验收对象是版式提交 `060ef6d951ff6471f4dcbb39aa4c449c1d131425`，不是记录这句话的文档提交。文档提交只追加本文件和交接说明，不改 TeX、图或 PDF。

- PDF：`paper/round2/integration/main.pdf`
- PDF SHA256：`05cece898d313acdb41c272ec2ecf031ab1532c098685f3438d428471a3cde0a`
- 当时源包 SHA256：`80489ae016ddd75dd7180551bb5c74dff6db02a76cfb867249d882bf8b31f5c5`
- 入口：`paper/round2/integration/main.tex`
- 复现：`cd paper/round2/integration && ./build.sh`（本机 TeX Live 2023）

仍未闭合：全部合成而非实测；Table 2 公式与 Expect 未核，Setwise 缺式；原 3D k-sweep TeX 缺失，E2 用的是二维 exp5-m；引擎是 TeX Live 2023，不是 2026；E3 刻度约 4.6pt、图例 5pt；展示型号 Qwen3.5 与历史 Qwen3.8 的部署 manifest 未核。

以下是父附最终短复核原文。

# 最终有界复核

**结论：原三项分页问题已解决，未见新裁断/漏件或尺寸回退；可按既有例外完成本轮版式交付。不是实测、公式、原3D复刻或TL2026合同全通过。**

对象：父提供 PR19 HEAD `060ef6d951ff6471f4dcbb39aa4c449c1d131425`（本轮未联网核对push）。安全复制/解压到本目录，未覆盖旧审核。实际Read关键变动页3/4/5/8，全部9页以PDF文字覆盖和独立110dpi渲染检查；9张提供PNG与PDF渲染逐像素完全一致。父负责再Read全部9PNG。未执行构建/工件代码、未改repo、未联系Cloud。

## 三项分页闭环

- 页3：LIMIT通栏下接算法1/2；不再独占一页。算法1至31行、SW至21行完整，无跨栏裁断。
- 页4：算法3左栏，算法4/5右栏；算法5不再独占一页。入口只在第4段前做column newpage，没有对每个算法或图逐一clearpage。
- 页5：E2通栏12格下接左栏E3单栏4×2；原E2后的无条件clearpage已删除。现clearpage只在盒高超过banner下整栏高度时触发（E4a约418pt > 可用394pt），不是逐图隔页。

E2、E3总caption均绑定图件；页5文字底约568.7bp，远离页底。页3文字底667.3bp；页8 E4c caption仍止695.0bp，未越正文底约708.6bp。算法/图题没有本轮新增硬碰撞。页4及其他页仍有空白，但不重开“填满所有空白”的新要求。

## 尺寸和覆盖未回退

与上一包逐字节比较：4个机制PDF、16个E2输出PDF、16个折线/散点PDF均未变；E2容器与E3图段TeX亦未变。E2继续width=0.33×241.14749 TeX pt，未加height缩高；PDF中首末子图标题位置x≈79.33/473.00bp及字号7pt与旧包一致。E3局部subfigcapskip=1pt保持。

9页内容：1机制四图；2表1/2与E1 Full；3 E1 LIMIT+算法1/2；4算法3/4/5；5 E2+E3；6两张E4a n100；7两张E4a n500；8 E4b/E4c；9 E5。没有漏E4a COVID n100、E4c或第五段算法，无新增独立LIMIT机制图/E4验证表。

## 交接状态

NEXT-BOT现行段及STAGING已明确四路均纳入；旧seed明确标为非现行，不再有可执行的“未纳入”禁令。矩阵确为64行，commit/QA两列全部非空，并明确区分未闭合科学事项，没有把所有项冒充科研通过。

**文档小限制（不再阻塞本轮版式）：** 矩阵“最终commit”列统一写PR19/分支及父已审十页的f55de18，而非本次060ef6d完整SHA；它是审计快照指针，不是精确新HEAD锁。父交接时应以本记录首段的新HEAD及以下hash锁定交付，不能把矩阵旧快照读成当前产物SHA。NEXT-BOT标题/父QA待办仍描述审前状态；本记录补充本次有限通过结论。

已知合成、公式未核、原3D TeX缺失、TL2023非2026、E3小字例外均沿用，不重新开启设计或科研验收。

## 文件锁定与复现定位

- PDF SHA256：`05cece898d313acdb41c272ec2ecf031ab1532c098685f3438d428471a3cde0a`
- ZIP SHA256：`80489ae016ddd75dd7180551bb5c74dff6db02a76cfb867249d882bf8b31f5c5`
- 上述两项均实际计算，与父给hash一致。
- 源入口：`source/paper/round2/integration/main.tex`。
- 复现脚本：`source/paper/round2/integration/build.sh`；从source根进入`paper/round2/integration`后运行`./build.sh`（仅定位，本次未执行）。
