# Round 2 against the TL2026 acceptance review

The inspection PDF in this commit was compiled on this VM with TeX Live 2023. `viz/build.sh` refuses that engine. It is not a TeX Live 2026 acceptance build. The parent box should run `viz/build.sh`.

`pdflatex --version` here is `pdfTeX 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian)`. Running `sh viz/build.sh` exits 1 before it writes a PDF.

The inspection PDF is 20 pages. `pdfinfo` reports 20 pages. Every page has body text. There is no trailing blank page. All five algorithms are in the text. The coverage test checks that.

| Review item | Status | Where in the inspection PDF |
|---|---|---|
| 1. Unshipped floats and blank pages 17–18 | Fixed for shipping. Algorithm 2 is on page 19. Exp 4b is page 11. The virtual figure and the LIMIT figure are on page 19 with Algorithms 1–2. The old blank pages are gone. | Pages 11, 19–20 |
| 1. First page was a wall of stubs | The stubs moved to this file. Page 1 is the template title, a three-line abstract, and the symbol table. The lower half of page 1 is still empty because the template title block does not fill the page. | Page 1 |
| 1. Uneven leftover whitespace | Improved by stacking figures in one column instead of leaving single-column floats behind `figure*`. A short figure can still leave the rest of its page open when the next figure does not fit. That is recorded, not hidden. | Pages 7–15 |
| 2. SW chips | Rebuilt with a call-number gutter and separate out / keep / unread lanes. | Page 16 |
| 3. Exp 4c | Means now span roughly 0.4 to 0.9. Points are numbered. One shared legend. Off and On-cold share limits. No per-query dots and no Pareto line. | Pages 12–13 |
| 4. 3D surfaces | Integer h ticks. Combined marker when both roles share a point. On the six-panel page the spine digits were being clipped, so each panel title states the shared scale 80 / 110 / 140 tokens and the spine digits are omitted. The hole is still unfilled. | Pages 7–8 |
| 5. Pseudocode | All five algorithms ship. Captions are ragged. `InitPlan` is one word. The root segment is “nonempty”, not `tmp` compared with a zero. No `zi4` italic-shape warning in the inspection log. | Pages 19–20 |
| 6. Exp 4b | In the PDF. The enlargement is a second panel with the same `(4,1)` and `(4,3)` labels. It does not cover the main series. | Page 11 |
| 7. Pointer | Split into two larger figures. Chips are separate. Panels (c) and (g) mark the item where the slot count reaches `h`. The next panel writes the pointer and states the previous value. The code can also repeat the same child. | Pages 17–18 |
| 8. Exp 4a and Exp 5 | 4a has a legend and unstacked category labels. The tick before Full is `500`; the caption says that tick is LIMIT 500, because the words “LIMIT 500” were cut off the axis. One Full square per method. | Pages 10, 14–15 |
| 9. Missing old tables | Page 6 adds the dataset contract, a symbolic method list, a synthetic validation shape, and a per-scale best table whose best role is `open`. Old measured numbers are not copied. The old parameter table is the symbol table on page 1. | Pages 1 and 6 |

## Eight source files

Checksums are in `evidence/manifest.json`. No wrapper text was on the three new files.

`init_plan` (`plan.py` 227–265) packs subtrees whose real segments fit in one call, then replays those nodes. It is not one sliding-window merge of every leaf.

`select_parameters` (`plan.py` 604–698) minimizes estimated input tokens. The numeric expectation is `finite.expectation`, and `finite.py` was not in this batch. The frozen v3 formula is only the uncorrected ablation. It is not drawn as the production model.

`materialize_producer` (`producer.py` 221–244) calls `aclose` in `finally`, including when the drain stops at `K`. `execute_family` (`runtime.py` 217–226) uses that drain in buffer mode.

## Before / after

`doc/before-after.pdf` places the round-1 drawings next to these ones for the SW figure, the six surfaces, Exp 4c, Exp 4b, and the pointer figure. It is an inspection sheet, not a TL2026 compile.
