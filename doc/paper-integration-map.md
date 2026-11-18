# VLDB 2027 paper TeX integration map

Authoritative integration entry: `paper/tex/main.tex` (restored from `_VLDB__27__Cost_effective_Multi_way_Merge_Semantic_ORDER_BY.zip`). Official PVLDB Vol.~20 stack: `paper/tex/vendor/acmart.cls`, `pvldb.sty`, `ACM-Reference-Format.bst` (same pins as `viz/tex/vendor/`).

Specialist trees live under `paper/recovery/` and `paper/viz/recovery/` (git-archived from PR branches; not merged to `main`).

## Parent-approved figures (7)

| Item | PR branch | Source dir | Paper inclusion | Label |
|------|-----------|------------|-----------------|-------|
| E2 2x2 | `cursor/e2-dual-surface-c6cc` @ `84a84ad` | `recovery/e2/` | `exp.tex` → `\ref{sec:exp:cost}` via `integration/fig-e2-main.tex` | `fig:exp2-surface-2x2` |
| E2 2x3 | same | `recovery/e2/out/e2-layout-2x3.pdf` | `appendix.tex` → `integration/fig-e2-appendix.tex` | `fig:exp2-surface-2x3` |
| Unified LT | `cursor/lt-h-main-figure-d022` (latest) | `recovery/lt/` | `framework.tex` §LT, `figure*` | `fig:eg:loser_tree_kway_group_merge` |
| Pointer A | `cursor/pointer-local-figure-1615` @ `258b9ac` | `recovery/pointer/pdf/pointer-scheme-a.pdf` | `framework.tex` after LT figure | `fig:eg:pointer-rule` (new) |
| E3 scale | `cursor/e3-scale-layout-14e8` | `recovery/e3/` | `exp.tex` → `\ref{sec:exp:ablation}` | `fig:exp3-scale` (new; does not retire `fig:exp3-ablation`) |
| E5 LIMIT sweep | `cursor/e5-limit-sweep-5af7` | `recovery/e5/` | `exp.tex` → `\ref{sec:exp:limit-sweep}` | `fig:exp5-k-sweep-off`, `fig:exp5-k-sweep-on` |
| SW wide | `cursor/sw-sliding-window-figure-ad37` | `recovery/sw/sw-wide.pdf` | `framework.tex` §SW, `figure*` | `fig:eg:sliding_window` |
| LIMIT trial | `cursor/recovery-limit-ondemand-trial-a880` | `viz/recovery/limit/` | appendix optional | `fig:limit-demand-trial` |
| Framework algo1 | `cursor/framework-algo1-cost-6f22` @ `5b3a024` | `recovery/framework/` | `framework.tex` `figure*` replaces Fig.1 | `fig:exp:semantic_external_merge` |
| E4b / E4c / pseudocode | PR12 / PR11 / PR10 | `recovery/e4b`, `e4c`, `pseudocode` | `exp-body.tex` / `framework` / appendix | see `label-page-map.md` |

PDF copies for `\includegraphics` are in `paper/tex/fig-approved/`. Captions are in `paper/tex/integration/*.tex` (integrator-authored wrappers only; no graphic edits).

## Old source → new location (unchanged experiments)

| Old label / asset | Status |
|---|---|
| `fig:exp2-k` | **Kept** — old LIMIT-$K$ sensitivity panels; not replaced by E2 surfaces |
| `fig:exp3-ablation` | **Kept** — legacy panels until measured E3 ships |
| `fig:exp4-full`, `fig:exp4-topk` | **Pending** — await Exp4a specialist |
| `fig:exp5-m` | **Kept** — batch-size $m$ study; distinct from E5 LIMIT-$n$ sweep |
| `fig:eg:segment_loser_tree` | **Kept** — pending policy on retiring vs.\ unified LT |
| `fig:exp:semantic_external_merge` | **Pending** framework intro figure |
| `tables/exp1_*`, `tab:datasets`, `tab:ranking-algorithms` | **Kept** old text/tables — await table specialist + new numbers |
| Pseudocode / `alg:*` in `framework.tex` | **Pending** pseudocode pass |

## Pending slots (no agent drawing)

See `paper/tex/integration/placeholders-pending.tex` and inline comments: Exp4a/4b/4c, Exp1 refreshed tables, framework intro, pseudocode consolidation.

## Build

- Release: `paper/build.sh` (TeX Live 2026 only).
- VM inspection: `paper/build-local.sh` (this environment: TeX Live 2023).

## Synthetic notice

Page footer via `eso-pic`: `SYNTHETIC DATA --- PAPER INTEGRATION (SPECIALIST FIGURES ONLY)`. Specialist captions already state synthetic/layout where applicable.