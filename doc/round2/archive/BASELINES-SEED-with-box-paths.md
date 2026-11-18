# 存档：交接种子里的本机 BOX 路径

状态：**非现行路径合同**。BOX 绝对/本机路径不能当仓库来源。现行映射见 `../BASELINES.md`。

# 实现基线与来源

更新：2026-11-18（Asia/Shanghai）。性质：可追溯实现输入、科学口径与已知差距；**不是最终成品通过报告**。现行视觉决策见《最新用户决策.md》。

## 1. 三类路径必须分清

- **目标仓库**：`https://github.com/SPikerinbit/visualization-polish`。`paper/round2/...`是目标仓库相对路径，必须随最终commit可重现；不能只指向本机下载目录。
- **本机资料根**：`BOX=/workspace/paper-materials`。本文表中的BOX相对路径均为本机现有资料，不能假称已在新commit提交。
- **上游实现仓库**：`https://github.com/BITQiKangK/SemaPrototype`，分支`OperatorSemanticOrderBy`。冻结源码快照commit `0d96d0bf116e52f1664ae2539446f05921f5e947`；不等于正式数据部署的最新身份。
- **原资料树相对路径**：`visualization-polish/`本地解包资料含中文目录及`unpacked-paper/`，并非本次检查过HEAD的git工作树。可用于原来源定位，不把它的本机相对名当已验证远端路径。
- 本地审核副本对应各路历史snapshot，当前正在返修。最终整合者必须记录新分支名/HEAD、复制来源、SHA256、可运行命令和实际产物路径。

## 2. 资产与TeX来源映射

| 基线 | 原资料/本机位置（相对BOX） | 目标仓库接入位置/状态 |
|---|---|---|
| 用户v2 SW/LT/Pointer与framework旧例 | `recovery-spec/references/user-originals/fig-F-*-v2.{pdf,png}`；渲染来源`mech-refs/v2/` | `paper/round2/mechanisms/`负责引用/复制；最终manifest核具体文件名，不能假称已提交 |
| v1色彩参考 | 同目录`fig-F-*-v1.*`；`mech-refs/v1/`与原`unpacked-paper/fig/` | 只借柔化颜色，不把旧构图恢复为现行批准 |
| 原v2元数据 | `visualization-polish/算法机制图/第二版/revision_v3/{figure_data,validated_states}.json`；备份在`recovery-spec/references/source-metadata/` | 原资料相对路径为`算法机制图/第二版/revision_v3/`；本机该目录未有渲染图，使用已保存v2 PDF/PNG |
| 原3D截图 | `recovery-spec/references/user-originals/fig-E2-cost-surface-reference.png`；`cost-surface-reference.png` | `paper/round2/e2/refs/fig-E2-cost-surface-reference.png`在已审E2副本存在 |
| 原3D脚本 | `visualization-polish/实验结果可视化/可参考：实验二3D/{compute_surface,plot_surface}.py`；备份`recovery-spec/references/scripts-3d/` | 原资料相对路径`实验结果可视化/可参考：实验二3D/`；E2已审副本`refs/recovery-spec/references/scripts-3d/`有复制 |
| 原论文TeX/图 | `visualization-polish/unpacked-paper/{exp,framework}.tex`、`fig/panels/` | 现稿参考`paper/tex/fig/panels/`及旧`src/`并存；最终核实际入口，不能同时盲改两树 |
| 用户组图源码参考 | `visualization-polish/实验可视化组图tex源码参考.txt` | 原资料相对路径同名；含2D exp4-full/topk和exp5-m，不含已定位3D容器 |
| E3 Fig8参照 | 原`exp.tex`390–415行`fig:exp4-topk`，单栏四图，每格0.25 columnwidth | 外置标题/子图说明；只借面积/layout，不搬旧科学内容 |
| E2当前12格容器 | 已审副本`round2-e2-independent-audit/recheck/tex/fig-e2-exp5-container-12.tex` | `paper/round2/e2/tex/fig-e2-exp5-container-12.tex`；**复用2D exp5-m，不是找到3D原容器** |
| E2当前10格容器 | 同目录`fig-e2-exp5-container-10.tex` | 同路径目标；删除F/L的最小派生，不称原TeX原封不动 |
| Table1完整批准版本 | `paper-integration-review6/paper/recovery/tables/tex/tab-datasets.tex` | 新包`paper/round2/tables-pseudocode/tex/tab-datasets.tex`应完整保留批准体/caption；首稿caption不同，正在修复 |
| 表格/伪代码本轮首稿 | `round2-tables-review/` | `paper/round2/tables-pseudocode/`；当前README旧文本不能代替新HEAD验收 |
| E3–E5及E4a-c | 本地未取得当前恢复后完整产物/编译证据 | `paper/round2/experiments/`，具体入口/文件清单由PR17最终manifest补；不能假称全部已生成 |
| 原模板 | `vldb-template/VLDB-Template-main/`；现稿vendor | 最终集成TeX入口待父代理锁定，TL2026 pdfLaTeX；不是完整论文正文 |

### 本次本地存在性/指纹核对（不是远端push证明）

| 相对BOX路径 | 状态 | SHA256 |
|---|---|---|
| `recovery-spec/references/user-originals/fig-F-algo1-v1.pdf` | 存在 | `622157c74198dfc928f8d8b4599e6b91f1763c54539a455bac492e8faec505af` |
| `recovery-spec/references/user-originals/fig-F-algo1-v2.pdf` | 存在 | `5791f464fcfaa96c5ac6a0bf8c9ac567e01a99b9527423256ce2c2c2f7cd1a88` |
| `recovery-spec/references/user-originals/fig-F-sw-v2.pdf` | 存在 | `04e9b6f893632774a8c337839f530d73e271cab2e3c3b02b5a9c7748cdb633f0` |
| `recovery-spec/references/user-originals/fig-F-lt-unified-v2.pdf` | 存在 | `ae9ca756241ff19b6e2731ae4a20d7d1501dde14187f80b615a291b6813f5a41` |
| `recovery-spec/references/user-originals/fig-F-pointer-v2.pdf` | 存在 | `5d429a48381cd61e0fdbd9e600e869af06ea60bc6dea825a5424880ac2ff9ce1` |
| `recovery-spec/references/user-originals/fig-E2-cost-surface-reference.png` | 存在 | `607297feec77a34024dabf03b9604c3d8d82a55f757c65ffd214878b9d075828` |
| `recovery-spec/references/scripts-3d/plot_surface.py` | 存在 | `bbc4d851bd19af03daacd24bcb21d9d490dc09aed4d40efc69c238f45964d606` |
| `recovery-spec/references/scripts-3d/compute_surface.py` | 存在 | `2216ea1ae4ff93dbdc8cdccf3b1935a91096074827b4bb15490e9a3c6c12cb99` |
| `visualization-polish/unpacked-paper/exp.tex` | 存在 | `85676e27f89fa55d958a1744df631e5a04e77a69acead8e31f52ca6cbf24ae30` |
| `visualization-polish/实验可视化组图tex源码参考.txt` | 存在 | `e6cbf974cdf7f88c73955ea78f31c9c5dd98a8fedeb01847fd79f7f1e9007119` |
| `visual-refs/pdfs/listk-semantic-orderby.pdf` | 存在 | `778690913a935c2993f280157bddf95ebd1f8c7d1d397fb82667364866f7cadd` |

已实际见到`round2-tables-review/build/preview.pdf`、`round2-e2-independent-audit/recheck/out/e2-vldb-preview.pdf`。它们是待返修snapshot，不是final。旧agent附件哈希路径不能保证存续；优先以上已存在原件并保留来源指纹。

## 3. 缺失与不能假称核验的来源

- 原脚本目录`surface_data.json`当前本机不存在，不能直接运行原脚本复现真实曲面；原`compute_surface.py`硬编码Windows数据/仓库路径，其grid和条件是历史n=200、Full LT、query1030303的独立协议，不能当本轮正式矩阵结果。
- 本地未取得`finite.py`，亦无`pointer_previous/`原目录；保留已有v2图与已提供8个核心文件，不因缺件伪造来源。
- 原3D k-sweep TeX仍未定位。`fig:exp2-k`是六张2D LIMIT K曲线，不是它；`fig:exp5-m`是2D batch-size组图。最新独立复核还发现重编原参照遮住右边框，未修之前面积相近数字不能证明原容器等面积。
- 本机原折线绘图脚本不在原源码zip，线点数值来自PDF矢量对象/已有笔记，不猜rcParams。
- 新正式实验二至五完整结果未在本次材料中出现；不能据此否认历史readiness研究实测存在，但历史协议不能冒充正式矩阵。

## 4. 算法实现/状态证据

本地`semaprototype-source/manifest.json`与`manifest-extra.json`记录上游commit、source URL和各文件SHA256。对应上游仓库相对路径：

- `sema_prototype/physical_operator/orderby/merge/sliding_window/sliding_window.py`
- `sema_prototype/physical_operator/orderby/merge/loser_tree/loser_tree.py`
- `sema_prototype/physical_operator/orderby/_common.py`
- `sema_prototype/physical_operator/orderby/operator.py`
- `sema_prototype/logical_operator/orderby.py`
- `sema_prototype/physical_operator/orderby/merge/_shared/{plan,runtime,producer}.py`

本机副本将`/`编码为`__`，例如`semaprototype-source/sema_prototype__physical_operator__orderby__merge___shared__plan.py`；不是平铺`plan.py`。本次只读，未运行实现trace或LLM实验。

状态资产：`recovery-spec/references/source-metadata/{figure_data,validated_states}.json`与`revision_v3-README.md`。Pointer示例Build时L=[3,7]、R=[1,5]，R先耗尽、pointer=R；Refresh新右段[6,14]和保留[5,7]进入逻辑槽后，L先耗尽、pointer变L。此为该例因果，非“耗尽必翻转”定理；replay使用已有rank map，不是额外LLM调用。README记旧pointer原生88mm×约67.8mm，非新整合页已验尺寸。

### 参数合法域（有实际源码依据）

`plan.py:max_segment`（约296行）、候选枚举（约653行）、`validate_request_capacity`（757行起）提供依据。对正常非退化固定参数网格，初始runs数r=ceil(n/m)：

- SW：2≤k≤min(r,m)，1≤h≤floor(m/k)。
- LT：2≤k≤min(r,2^(m−1))，1≤h≤floor(m/(1+ceil(log2(k))))；代码写成`m // (1 + (k-1).bit_length())`。
- 实际最后小组的effective fan-in、r<2、LIMIT0、缺省控制等退化分支仍按真实执行器核验，不把正常网格公式当全接口形式化证明。
- n100、m20时r5，k8超过run数，(8,1)/(8,2)都不合法；不是仅h不合法。n500、m20、r25时规范给每需求SW46点、LT101点。合成fixture也必须合法，不悄悄clamp参数仍保留原标签。
- 非法区域/未测点留空，不跨不可执行区连完整床单；预测和实测同视角/坐标范围，SW与LT合法域不同不能强压成同域。

## 5. 原论文实际线、点、字的尺度

依据`round2-line-references/NOTES.md`（PDF笔画/字体对象提取，非本次重新绘图测量）。原面板133.2×133.2 PDF pt，即1.85in；sigconf原稿多数用0.33栏，Fig8用0.25栏。TeX pt与PDF pt并非同单位，不能混算。

| 元素 | 原生PDF对象 | 0.33栏约缩放0.5974 | 0.25栏约缩放0.4526 |
|---|---|---|---|
| 数据线 | 1.6pt | 0.96pt | 0.72pt |
| 点形路径包围盒 | 约4.8×4.8pt，边1pt | 约2.87pt | 约2.17pt |
| 浅灰网格 | 0.765pt，#B0B0B0 | 0.46pt | 0.35pt |
| 坐标框 | 1.36pt，黑 | 0.81pt | 0.62pt |
| 刻度线 | 宽0.8pt、长2.2pt | 宽0.48pt | 宽0.36pt |

字体TimesNewRomanPSMT/STIXGeneral；系列色原有#1F77B4、#2CA02C、#D62728、#FF7F0E、#17BECF、#CC79A7。旧SLT颜色可作历史样式参考，**不表示恢复第三家族**。组图共享顶部图例，线+点+名，最优标记大于系列点。大小要在最终投放尺寸复核，不照抄大屏样式。

原3D脚本另有直接基线：BLUE=#087F9B、ORANGE=#DA821E；实测面alpha .55/预测面 .22；同邻接网格三角化、orthographic、elev26/azim−54、box_aspect[1.45,1,.92]，每kh点。原脚本将选点菱形画预测高度是历史实现细节；当前科学表达要求选参角色在对应实测成本位置，不得因复刻风格保留错误语义。原3D poster的13.6×8.7英寸/Arial字号不能直接当10或12格最终尺度。

E2旧复核实际测得刻度5.357pt、图例6.806pt、子图题6.974pt；CropBox整张宽469.58pt若强放506pt会再放大约7.8%。这些是旧snapshot测量，不是新HEAD达标值。用逐panel原TeX容器避免无意二次放大。

## 6. ListK及已有外部参考（不新增搜索）

- Shin、Chang、Nargesian，*ListK: Semantic ORDER BY and LIMIT K with Listwise Prompting*，arXiv:2603.17223v1，2026-03-18。https://arxiv.org/abs/2603.17223 。本机`visual-refs/pdfs/listk-semantic-orderby.pdf`。
- 主视觉参考为用户截图：`round2-line-references/listk/user-screenshot-fig4-scifact-scatter.png`、`user-screenshot-fig5-filter-listsize.png`；已有裁图同目录。Fig4/5对应PDF第10/11页。这里只称预印本，不冒称已核顶会正式版本。
- Fig4学共享一行图例、点形/颜色、少装饰；Fig5中拟合有专门模型，不可无据移植。现笔记称Fig4红点线为前沿，仍须由负责代理在本地参考核清线义及caption后给本数据明确定义。
- 伪代码参考是用户t56附件；当前旧哈希附件目录未在本次重验证，最终归档者需保留实际截图/引用，不能只留下易失绝对路径。
- 已有SemBench（PVLDB19(8),2026）与LOTUS（PVLDB18(11),2025）裁图/笔记在`round2-line-references/{sembench,lotus}/`，仅用于微调，不压过用户原图。没有新增外部参考检索。

## 7. 数据/指标/聚合的真实规范

本机`visualization-polish/paper-experiments.md`提供研究合同；`semaprototype-visualization-notes.md`提供指标展示语义，旧布局建议已由最新决策替代。正式测量规范相对上游文档链接为`measurement.md`，本地未取得该完整文件，接真实数据前应解析上游冻结版本，不猜缺失定义。

### 已定位的取值

- 六集：Q9、DL20、DL22、TREC-COVID、DBpedia-Entity、Robust04。Q9原生1 query，128有效独立评论；其余目标30 query、候选n>100、cap500，DL22官方去重映射/Robust04授权语料缺口不能删提示或替代填满。
- 机制子集：DL20短1121353/中1109707/长330975；COVID短6/中38/长12。E2/E4c/E5各集3个，E4a/b中等代表，E3首批DL20中等代表。真实ID一致不等于候选输入一致，E4c用主表全标注候选，E2/4a-b/5用检索候选。
- m20参考点；temperature0、固定条件repeat1、generation_seed0。E1每query质量/费用使用初始输入排列seed0..9；这是10种条件，不是10个独立query或温度采样。
- E1 Full全长Spearman、LIMIT10 NDCG@10；费用逻辑Total=input+output；独立latency固定排列0、query并发1，不能用质量费用批次耗时除query数造延迟。
- 质量均值先每query内10排列均值、再query等权；排列波动按每排列索引先跨query均值，再十值std的既有建议/测量契约复核，不能当跨query CI。需要推断以query配对，Q9单query只如实报告排列波动。
- E3参考n=1k/5k/10k，真实最终n与固定(k,h)仍需最终prompt下成本模型冻结，不能把参考输入准备当已完成排序；图横轴3值不等于新授权大规模实验。
- E4b原始beta={0,.1,.25,.5,.75,.9,1}；主图五条0/.25/.5/.75/1，均由On-cold观测离线定价，不为beta重跑排序。
- E5位置10/20/50/100/200/300/400/490/LIMIT500/Full；LIMIT500是显式buffer，Full是显式full，即使相同输出也不合并。质量NDCG@10贯穿全部端点；成本等价输入，On参考beta0。

### 成本与缓存协议

U=逻辑输入、Q=命中输入、O=输出；Total=U+O；等价输入=U−(1−beta)Q；等价总量=U−(1−beta)Q+O，不称美元/GPU量。E4a/b用等价输入；E4c用beta0等价总量（Off=U+O，On=U−Q+O）。beta1 On仍非Off。未知Q保持NULL，不能补零。

`paper-experiments.md`尾部11-16批准项已覆盖较早“自然命中/最终prompt待选”：最终prompt为paper_short，固定前缀限定复用，仅system和首个可变item前共同token前缀，显式整数C及token SHA256，不填充、不复用item、不向块边界取整；每次On-cold完整排序独立namespace，内部Phase1/merge/重试共享。历史自然命中/readiness实测是独立协议，不冒充新正式矩阵。

### 聚合与序位

- E1 Token显示Q9单集、TREC两集、BEIR三集的各集平均Token之和；latency六集均值等权；三指标主排序键各是六集未舍入dataset内midrank的等权平均，不把三个benchmark组名次当三票。
- 原始值Decimal/Fraction等保精度；主键同则Token/latency六集原始均值等权低者优先，质量有声明的尺度处理后高者优先。当前Full全为rho、LIMIT全为nDCG，不必臆造混合指标；rho的(rho+1)/2仅为有声明次级尺度策略。
- 首稿实现另有固定dataset向量字典序及合法重复方差后备键：它们是实现细则，非用户逐条批准或显著性证据，最终须写清且审计。无重复次数证据不得用std强拆。
- 展示合成fixture可以按已要求修改并标测试覆盖，但保留全等原证据回归测试；真实全等不得改数/规则，输出限制必须明示。
- E4c质量与成本分别先各dataset内3 query等权，再DL20/COVID各1/2；均值点不是per-query点云，不因样本少声明广泛显著性。

### 红虚线规则

用当前面板均值点、成本低/质量高定义非支配集，若经本地参考核义确认用Pareto引导，则按成本排序连接非支配点，注明描述性前沿/引导而非拟合；不连任意算法、不造端点、不偷换为单query最佳。若可用点少于两点或数据缺失，记录不足，不编曲线。真数据接入时必须重算，不能沿用合成线。

## 8. 必须显式解决的冲突

1. 本机11-13研究合同模型写`Qwen3.8-27B`，本轮表格STATS/先前整合核对为`Qwen3.5-27B`；9B一致为Qwen3.5-9B。**不能静默猜型号**。最终以真实部署/condition ID及上游最新冻结合同锁定，交接保留此历史文字冲突；不改真实观测身份适配标题。
2. “原3D k-sweep TeX只换图”目标与当前仅找到2D exp5-m的事实未闭合，不能报完全复用原3D。
3. 无并列展示与真实全等不可区分有科学边界；允许改测试fixture不等于允许改数据/规则。
4. Table2调用公式未推导/Setwise缺式、P(k)/mu_sw未定义，结构可核不代表公式通过；finite.py缺失也不允许声称有限期望公式已核。
