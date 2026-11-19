# 实验可视化配置说明（E1–E5）

用途：把当前审阅版的表、图反推成采集与交接清单，供 SemaPrototype 的实验输出接入可视化工程。**这不是运行结果或已定稿的实验协议。** 当前 PDF 中的实验数字都是合成排版样例；本次快照冻结版式，不把样例认定为实测。正式输出另开目录，保持与 fixture 隔离。

## 1. 开跑前：先冻结运行清单和记录格式

以下路径和字段是建议的交换合同，不表示当前绘图脚本已经支持实测输入。

| 文件 | 每条记录的粒度 | 至少保存 |
|---|---|---|
| `manifest.json` | 一次实验发布 | `schema_version, data_kind, experiment_id, code_commit, evaluation_commit, model_id/revision, tokenizer_id/revision, prompt_hash, dataset_revision/qrels_revision, corpus_build_id, evaluation_query_set_id, seeds`；硬件、服务端与缓存版本、并发/批大小/计时范围、计费/成本口径 |
| `queries.parquet` 或 CSV | 一次实际执行的一个 query × permutation × repeat | `run_id, query_id, permutation_id, repeat_id, model_id, dataset_id, method_id, demand, n, K, m, k, h, cache_state, batch_kind, status`；质量分数及指标、端到端秒数、输入/输出/命中 tokens、可分则分开记初始 run 与归并；可关联保存请求/回复 ID、失败原因 |
| `configs.csv` | 一个可枚举配置 | `config_id, model_id, dataset_id, n, m, initial_run_count, demand, K, family, k, h, feasible, feasibility_reason`；候选域版本与计算规则；每批次保存完整候选集合 |
| `predictions.csv` | 一个模型版本对一个配置的预测 | `config_id, predictor_id, predictor_commit, simulation_seed, simulation_trials, cost_scope, predicted_calls, predicted_item_appearances, predicted_input_tokens`，存在缓存预测时另存分项和预测 `beta`；按相同候选集合保存预测选点 |
| `aggregates/` | 精确到各图要求的聚合表 | 保留源运行 ID/清单哈希、分母、失败数、样本数、配置键、未舍入值。生成器写审计文件，不手改 TeX 或 PDF 数字 |

- 共享键建议是 `model_id, dataset_id, demand, n, K, m, family, k, h, cache_state` 加具体图需要的批次、`beta` 等；Full 的 `K` 为空，不能把 Full 当 LIMIT 的更大 K。不可用字段保留空值，不填零。预测和实测按键对齐，不能靠 CSV 行号或绘图顺序。
- `cache_state` 至少区分 `off` 与 `on-cold`，记录每个请求的实际 hit tokens 和用于冷启动的隔离/重置方式。启用缓存、实际命中、以及离线给命中部分打折是三件事；不要用一种表示替代另一种。
- 模型表头当前显示 `Qwen3.5-9B` 和用户指定的 `Qwen3.8-27B`。这只是版面标签；真实部署清单需记录具体 checkpoint/revision 与 tokenizer，核验之前不要把显示名当作已跑的模型。
- 记录实测状态及失败原因，不静默删掉慢例、非法配置或不命中的执行。原始明细保留完整精度；仅渲染时舍入。预先确定聚合单位（query、permutation、repeat 分别代表什么）与排除规则。计时只取指定的独立延迟批次，不拿离线预测或 token 运行替代。
- 成本分三类：端到端逻辑总 tokens、归并阶段实际/预测的输入 tokens、缓存下等价 tokens。分别存每个计数，不以图上的等价值反推分量，不把等价 tokens 当实际美元或延迟。

## 2. E1：端到端质量、Tokens、Latency（现稿 Table 3–4）

- 按模型 × 方法 × 数据集 × 需求收集。六集固定顺序为 Q9、DL20、DL22、TREC-COVID、DBpedia-Entity、Robust04；数据集快照、qrels/参考排序和缺口要单列登记。Full 用完整排名的 Spearman ρ；LIMIT K=10 用 nDCG@10。保留当前表列出的全部方法；ListK Full/LIMIT 分别用 Sort/Select，LT(h)仍是一个算法族。各条件对齐 query 集合，缺测不能靠其余数据集补位。当前方案区分质量/费用批次（query 并发 10，排列 0–9）与独立延迟批次（query 并发 1，排列 0）；启动前按实际执行策略核实并记录。报告 Q9 只有一个 query 的事实。
- 每个 permutation 先按已冻结的 query 聚合协议计算质量，再用独立 permutation 的结果求质量 mean 和 permutation SD（标注采用何种 SD 口径）；不要把同一 query 的多次排列当独立 query。保存 `n_permutations`。token 和 latency 若要用于残余并列拆分，另存每集 `n_repeats, repeat_variance`。
- 两张宽表只各保留一行方法名。每模型的 13 列是六集质量 mean ± SD（各三位小数）、3 组端到端逻辑 token（input + output）均值之和、六集等权平均延迟（秒）、Q/T/L 整数序位。token 中 Q9 独列，TREC=DL20+DL22，BEIR=COVID+DBpedia+Robust04；单位为千 tokens，显示两位小数。不用 query 总数做跨集加权。
- 排名用未舍入指标：逐数据集同值用 midrank，然后六集等权平均。对照 [统计协议](../../paper/round2/tables-pseudocode/STATS.md)：并列再比较六集指标均值、固定顺序的原始六维向量；只有合法重复数和离散度齐全才用离散度拆残余并列。最终为竞赛序位，全等允许并列。第一加粗、第二下划线；不能把 SD 或名次当显著性。
- [现有 emitter](../../paper/round2/tables-pseudocode/src/emit.py) 只支持版式 fixture，且对展示位数有精确值检查。**接真实数据时要加独立的实测输入适配，并拆开未舍入排名与仅展示舍入**；不要为了通过当前脚本提前舍入实测，或者改原数据。

## 3. E2：成本模型曲面与选点

### 现图事实

12个独立panel，2×6通栏；Syn-A…L是合成身份，不是真实query。前三格LT Full、后三格LT LIMIT10；第二行SW对应排列。前轴k、深轴h，竖轴merge input tokens×10³；各panel自适应竖轴，不能按视觉高度跨panel比较。星=显示配置中observed-role最低点；菱形=预测选择的配置，**菱形高度取该配置observed-role值**，不是预测成本。坐标行与图内角色必须一致，重合仍保留两角色。

`paper/round2/e2/out/unchanged-points.csv`字段 `panel,k,h,synthetic_actual,synthetic_predicted`；对应生成器和IMPLEMENTATION-BASELINE.md明确没有真实surface_data或vLLM测量可替代这些合成面。不能将字段名字actual/observed误称实测。

### 最低原始数据与配置

每 `model,dataset,query,n,m,mode,K,family,k,h` 一行实测merge阶段U，另存预测输入成本P及预测版本；逐点保存调用数A、累计item提交/出现数D、U/Q/O及实际阶段账目，才能分别验证工作量预测与token预测。预测必须调用前冻结，不能用同一点实测值回填。选点记录需包含候选域、可行性、argmin tie-break、选择的(k,h)、预测值与选择时间。

仓库实验方案（`paper-experiments.md`）约定两模型、DL20/COVID各3query、n500、m20、SW/LT、Full/LIMIT10。25个初始run下固定域SW46点、LT101点，合计3528个merge条件是合同目标，不是已观测数量。E2每张曲面应绑定单query，不能未经定义先平均不同query的曲面。12panel只是展示容量，不能据此推断已展示全部模型/6query组合；需要冻结panel→真实条件映射及附录策略。fixture的gap不能当作可行域缺失证明；真实运行缺点必须记录失败/缺失，不插值补造观测。

可共享兼容Phase1产物，但merge成本与逻辑端到端加回实际Phase1费用须分列，真实执行支出不能重复计入。采用哪些观测的兼容性需核源码、输入、prompt、种子及执行策略。

### 可行性护栏

固定SW：2≤k≤min(run_count,m)，1≤h≤floor(m/k)。历史 block-init LT 候选域约束曾采用：k受run_count限制，h≤floor(m/(1+ceil(log2 k)))，还需其他执行约束。当前Framework caption却写LT b(k)=k+1，与该冻结证据冲突，不能让图注成为实验合法域权威。运行前绑定实际planner版本复核；不要默改代码或择有利公式。h=1仍属于LT，不另建SLT曲线。

## 4. E3：规模扩展

### 现图事实

`recovery/e3/e3_layout_data.json`明确 `synthetic_layout_only`。横轴n=1000/5000/10000，线性；四列SW Full/SW LIMIT/LT Full/LT LIMIT，上排predicted虚线、下排reference实线，各族五条固定(k,h)曲线，十个图例。**纵轴是layout units，不是tokens**；预测只是参考fixture加常量偏移，Full/LIMIT复用fixture。不能拿偏移计算预测误差或声称两模式成本相同。

### 最低原始数据与聚合

每 `query,model,family,mode,K,n,k,h` 的真实merge阶段输入U与独立预测P、A/D、阶段账目、输入集合/顺序哈希、运行状态；固定(k,h)跨n保持同一身份。现方案首批为DL20代表query、9B，不可自动加入COVID或平均多个query。现图无误差条，不表示不存在波动；如以后加重复/多query聚合，须另定单位与统计对象。

规模输入为嵌套集合：BM25 Top1000始终保留，固定抽样追加4k再5k不重复文档，然后各自排列；不能先洗牌10k再截前1k。图中1k/5k/10k只是参考规模，合同尚要求最终prompt/H/L后冻结 `scale_sizes/scale_points`，不能把布局五条线直接当批准运行矩阵，不补全大规模(k,h)网格。真实纵轴单位及阶段范围需与E2明确一致后替换layout units，原fixture不得混入实测曲线。

## 5. E4：Prefix cache，而非泛化的选参验证

### E4a / Fig8：真实开关 Off 对 On-cold

现图单栏，8独立panel（n两列×family/mode四行），每panel中DL20、COVID是分隔的两个离散配置段，不连跨dataset曲线。每段8配置、每配置两状态，共256普通点、64角色。纵轴等价输入token×10³，β=0：Off=U_off，On-cold=U_on−Q_on，二者来自各自执行，不能用同一个U做固定轨迹折扣。U包含Q；On成本高于Off不表示负命中。n内共享yrange，n间可不同。星=显示域最小，菱=模型选点在对应显示曲线的高度，不等于预测高度，不证明全域最优。

合同4a/b每集取中等长度代表query，非各3query均值；n100/n500、m20、SW/LT、Full/LIMIT10。最低每条件×(k,h)保存独立Off和On-cold observation、U/Q/O、缓存隔离/清冷证据、完整调用与阶段账目；预测Off/On选点及其独立预测来源另存。缓存On-cold需冷启动执行身份，不能把warm命中数借来。未知Q不能写0；β1虽无需Q计价也须保存其缺失状态。

**当前fixture来源问题必须随交付说明：** 原JSON末两项n100 k8，在此前e4a.py synthesize_n100中派生为k5；16配置身份和7角色改变。64点×4显示/预测cost字段保持原索引值，但COVID n100有32 U_on、32 Q_on因SPECS缩短后命中分解轮转改变，U−Q保持不变。它不是本次重建引入，也不是纯tick重标，更不能说明k8与k5配置等价。n100,m20仅5初始runs使k8超候选域；k5数值仍是合成示意，未经真实成本验证。保存legacy JSON与显式派生fixture双来源，禁止混入科学结果或伪称所有原记录不变。当前派生渲染输入与逐点审计见 `paper/round2/experiments/e4a_c2_recovered/`。

待定：真实显示配置列表应覆盖各状态预测最优和实测最优；不能按已有合成曲线选择真实观测点。现图横轴小号标签在同一基线单排，四项图例一行；这不解决近值/角色遮挡；不得为避免重叠jitter成本或配置坐标。

### E4b：β离线重定价

来源 `recovery/e4b/e4b_beta.json`；现图单On-cold slice、7个离散(k,h)、5曲线β=0,.25,.5,.75,1。公式Cβ=U−(1−β)Q，当前U/Q为layout sample，不是真token或金额。合同还包含β=.1,.9，未画不等于可省略计算。

最低raw是同一真实On-cold observation的U、Q及条件身份，一次排序可派生多个β，不按β重跑。每β需单独冻结的预测cost/选点来源；严禁用当前被评价配置实测Q构造“预测命中”。星/菱均画于该配置Cβ高度；β1仍是cache On无命中折扣，不能冒充Off。现图无明确真实query/family身份时应保留缺口，不能由曲线形状补猜。真实运行采用的slice、共同显示域、定价单位需显式固定。

### E4c：质量—成本比较

来源 `recovery/e4c/data/synthetic_means.json` 与 `paper/round2/experiments/e4c_independent/e4c.py::average`。4panel为Full/LIMIT10×Off/On-cold，各十方法，共40点。图横轴等价总token×10³：U−(1−β)Q+O，β0、output权重1，非金额；Full纵轴Spearman、LIMIT纵轴NDCG@10。SW/LT填充突出，其他方法符号保留；细圈/虚线只标均值点的非支配集合，不是拟合/显著性或置信带。

**现图聚合精确为**DL20 dataset mean与COVID dataset mean的各1/2，x与y分别平均。源文件每dataset均值声明代表3query，但没有query-level值，因此不能宣称已经计算六query真实均值或方差。真实输入需每 `dataset,query,method,mode,cache_state` 的U/Q/O、质量、配置与qrels/metric版本，先各集3query等权均值，再两dataset等权；若缺query不可静默改变分母。每状态分别测质量，不假设cache状态输出一致。

合同采用E1全标注候选、排列0、十方法；不是4a/b检索候选，即便query ID相同也不可混用。SW/LT每状态独立选参，baseline沿主表原算法参数。复用E1观测需执行隔离等完整条件相容，不把并发10结果冒充隔离执行。Pareto按低cost/高quality在同panel内求，只对已观测均值负责。

## 6. E5：LIMIT K sweep + 独立Full模式

来源 `recovery/e5/data/e5_limit_sweep_meta.json`、`paper/round2/experiments/tex/fig-e5.tex`。当前8独立panel：dataset×cache四列，上费用、下质量；每panel SW/LT两线。固定n500；横轴依次LIMIT 10,20,50,100,200,300,400,490,500与独立Full。LIMIT等距离散槽，不是线性K；Full断开、不连LIMIT500、不伪造K510。全端点质量均NDCG@10，不变成NDCG@K或Full Spearman。

费用Off=U、On-cold=U−Q（β0），单位10³token；Off/On费用轴尺度不同，不能比较表面斜率；质量共用NDCG@10尺度。这里是等价输入，不要与E4c等价总token混用。

合同每集3query、9B、SW/LT、每query×需求×family×cache state分别由模型选择合法(k,h)，执行该点而非事后最低点。原始数据需每个端点的prediction_id、所选(k,h)、选择域/成本、execution observation、实际返回数、mode/停止原因、U/Q/O及NDCG@10。Full与LIMIT500须独立身份，即使输出相同也不合并。Off兼容Phase1可共享并留关联，On完整冷执行。

显示合同为各dataset的3query等权均值，但meta明确当前每cell只是单个placeholder，不是该均值；不能由占位数倒推出3条query观测。共享(k,h)也不可虚构，应另导出逐query选参表。连线只是跨需求的聚合趋势，可能每点参数不同，不是固定配置轨迹。SW偏Full/LT偏LIMIT只是工作假设，不是fixture证实的结论。

## 7. 从实测表替换到交付：验收顺序

1. **覆盖核对**：先冻结合法配置清单，按图预期键做反连接，报告缺测、重复、非法点和失败执行。E2 不插值补实测；E3 不能把 Full/LIMIT 复用样例当结果；E4a 的旧生成器派生配置不能用于真实数据。E5 的 Full 不进入 LIMIT 轨迹。
2. **口径核对**：先核验模型和评测清单。对 E1 复算质量 SD、token 组内和、六集延迟等权及排序；对 E2 逐配置配对预测和实测；对 E4 单独审计缓存分项；对 E5 分清真实并点和印刷尺度下的近点。不反向调整样本迎合预期结论。
3. **生成与复算**：先用独立适配器把真实聚合表转为渲染输入，再分别生成各子图／独立图例和表格。不要直接运行会重造 fixture 的脚本来“导入”真实数字。输出逐图输入哈希、绘图提交、点位完整性报告、异常清单。
4. **提交前**：用 `paper/round2/integration/main.tex` 在 PVLDB 模板中编译并按实占栏宽检查图例、轴标签、标记和页边；保留能追溯的 raw → aggregate → panel → PDF 链。只有所有正式图表替换并逐项核实后，才去除验收稿的合成说明。不能用本轮排版通过代表实测或科研通过。

建议先跑一个覆盖所有字段的小样，打通输入导入、分项复算和每张图的脚本，再批量跑完整 grid。优先核对：模型与语料清单、各实验实际候选域、E3 成本边界、E4/E5 缓存冷启动和聚合协议。
