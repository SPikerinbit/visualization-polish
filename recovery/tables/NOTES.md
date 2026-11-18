# 表格 checkpoint（E1 与既有表）

合成数字，不是实验结果。生成链：`data/*.json` → `emit.py`（`ranking.py`）→ `tex/*.tex` → `render/main.pdf`。不要手改 `tex/` 里的数字或加粗/下划线。

## 复现

```bash
cd recovery/tables
./build.sh
# 或
python3 emit.py --write-checkpoint
python3 -m unittest discover -s tests
```

`build.sh` 会把 PDF/PNG 与含全部 `.py` 的 zip 写到 `/opt/cursor/artifacts/`。

## 版式（本轮返修）

- `table*` 内用 **同一份** `exp1_column_spec()`：Method `0.17\textwidth`，每组三列 `0.105/0.048/0.040\textwidth`，四组（三个数据集 + Avg.\ Rank 槽）。上段三数据集 + **与 Avg.\ Rank 同宽的空槽**；下段三数据集 + 真实 Avg.\ Rank。两段各一个 `tabular`，列对齐。
- 字号：主表与既有表用 `\small`（不用 `\footnotesize` 冒充 8pt）。`tabcolsep=4pt`，`arraystretch=1.06`。
- Caption：主表 3–4 句，明确 synthetic、± 含义、粗/下划线；完整排序合同见下文。
- 仍不强行六数据集一横排；probe 页只作宽度对照。

宽度验收用 `measure_layout.py` 读 PDF **表线**（`\toprule` 等横线 bbox），不测墨字跨度。目标：双栏文字区左右 **54–560.3pt**，表线宽 **≤506.295pt**。主表 `tabcolsep=1pt`（13 列 12 隙共 24pt）+ 列宽合计 0.942`\textwidth`，**无** `makebox`/`resizebox`。版式 `\small`（PDF 约 8pt 级正文）。

## 排序与标记（布局演示；**非最终统计合同**）

当前 JSON→TeX 自动标记实现下列规则，父审计 JSON→四张主表逐格为 **0 mismatch**：

- 名次在**未舍入**均值上；表上显示值只供阅读。
- **质量**：更高更好；同均值且整组都有 permutation std 时，更小 std 优先；若有人记了 `n_permutations`，整组必须都 ≥2 才用 std。
- **Token / 延迟**：更低更好；仅当整组 `n_repeats≥2` 且都有 `repeat_variance` 时用更小方差；否则用更高质量打破；仍并列则平均秩（1.5 占位）。
- 缺测不参与该列与该指标等权平均秩。
- **Avg.\ Rank**：各数据集秩的等权均值；本 checkpoint 采用 **standard midrank（布局演示）**，**待真实统计合同最终确认**，不视为用户已批准。

完整条文与审计失败处理写在本文件；勿再塞进 caption。

## 数据 schema

`sema.exp1.sheet.v1`：`cells[method][dataset][quality|tokens|latency]`。质量可有 `permutation_std`、`n_permutations`。Token/延迟可有 `n_repeats`、`repeat_variance`（不打印 ±；`n_repeats<2` 时方差不参与排名）。

## 仍 open / 不杜撰

- 正式实验数字、`synthetic: false` 的真实 sheet
- `|D|`、Setwise 复杂度、LT 的 `h`–`m` 公式、验证表 `k_cm`/`k*`/regret
- 算法表大 O：拒稿草稿原文，**未**对照当前实现验证
- `tab:params` 注释表仍 `\iffalse`
- 27B label、对照表 label 建议项未批准

## 基线

旧 zip `exp1_full.tex` 骨架 + Abacus/SCISE 的 mean±std 与分段宽表；**不是** `viz/tex/generated/tables.tex` 退步稿。