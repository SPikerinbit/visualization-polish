# Algo1 framework — bounded revision (parent feedback)

## Parent issues addressed

- Compact **178mm × 118mm** layout (figure* width); height was ~163mm and too square.
- v2 data spine restored: $C_i$ → four ListwiseRank → $R_i$ → Pass 1 MergeGroups → $Q_i$ → Pass 2 → $\Pi$, tight vertical spacing.
- Cost block is a **right sidebar**: in $m$, demand, $|R_i|$, $(H,L)$; out $f$, $k$, $h$ only. No `finite.py`, tie rule, or Full$\neq$K text in the figure.
- Control lines to three MergeGroups along gutter $x{=}145$; **no labels on dashed wires**.
- One short output tag: **Full trace** beside $\Pi$. No right-hand mode loop or second explainer box.
- $\Pi$ nodes: `\foreach \i in {1,...,16}`; `verify_trace.py` checks chunks, runs, $Q_1\cup Q_2$, and $\Pi$ are permutations of $1..16$.

## Element table (unchanged)

| Stage | Content |
|---|---|
| $C_1..C_4$ | $\{12,3,16,7\}$, $\{5,14,1,6\}$, $\{11,2,15,8\}$, $\{9,13,4,10\}$ |
| $R_1..R_4$ | $(3,7,12,16)$, $(1,5,6,14)$, $(2,8,11,15)$, $(4,9,10,13)$ |
| $Q_1,Q_2$ | $(1,3,5,6,7,12,14,16)$, $(2,4,8,9,10,11,13,15)$ |
| $\Pi$ | $1..16$ each once |

## Audit text → caption

See `include-snippet.tex` (figure* preview caption): `finite.py`, tie-breaking, Full vs LIMIT $K$.

## Geometry (parent pass 2)

- Data spine $x{\leq}139$mm; column centres 23 / 58 / 93 / 128; $Q_{1,2}$ and Pass~1 groups at 40.5 / 110.5.
- Cost lane 147--177mm only; **no** arrows into the cost box (inputs listed inside).
- Control bus $x{=}141$mm: right `MergeGroup` from the east; left via $y{=}63.5$ then lane $x{=}51.5$; Pass~2 from the east.

## Remaining limits

- `f`, $k$, $h$ values are not drawn (example trace only).