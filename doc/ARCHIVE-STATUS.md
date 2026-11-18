# 归档状态（visualization-polish）

**分支：** `cursor/vldb2027-figure-checkpoint-234e`  
**远端 HEAD（归档核对时）：** `01fc0e89563cb3fb2b171ef541aad869d7e7f7aa`  
**PR：** [#1](https://github.com/SPikerinbit/visualization-polish/pull/1)

## 用户裁定（2026-11-18）

用户**否定**本轮视觉/layout 论文整合质量，宣告该轮工作**失败**。本仓库该分支内容为**失败工作归档**（完整 TeX、recovery 生成链、决策文档、build 脚本），**不是**可接受终稿。未经用户另行请求，不再修改图、数据、排版或进行视觉迭代。

## 源码范围（Git 已 track）

- `paper/tex/` — 主稿、integration、`fig-approved/`、`tables/generated/`、`legacy/`
- `paper/tex/vendor/` — PVLDB / acmart 官方模板依赖
- `paper/recovery/**` — 图/表生成与数据（含 `tables/`、`e2`–`e5`、framework、sw、lt、pointer、pseudocode 等）
- `paper/build.sh`、`paper/build-local.sh`、`paper/scripts/*`
- `doc/最终可视化决策.md`、`doc/paper-integration-map.md`、`doc/integration-pending-changelog.md`、`doc/label-page-map.{md,json}`、`doc/build-verify-record.md`

用户附 zip 中 `paper/src/` 旧稿树及 `Qwen3.8-27B-*.json` **不**纳入活跃链；远端以 `Qwen3.5-27B` JSON 与 `01fc0e8` 树为准。

## 决策文档权威路径

[`doc/最终可视化决策.md`](https://github.com/SPikerinbit/visualization-polish/blob/cursor/vldb2027-figure-checkpoint-234e/doc/%E6%9C%80%E7%BB%88%E5%8F%AF%E8%A7%86%E5%8C%96%E5%86%B3%E7%AD%96.md)