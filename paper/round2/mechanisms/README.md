# Round 2 mechanism figures

Four figures only. Nothing outside `paper/round2/mechanisms/` is an input to the paper build.

## Files

| Figure | Source | Column / print PDF | Same-size recolor |
|---|---|---|---|
| Framework | `src/framework.tex` | `framework.pdf` 504.4 × 181.4 bp (178.0 × 64.0 mm) | new drawing |
| SW | `src/sd_merge.svg` | `sw.pdf` 240 × 72.7 bp | `sw-v2size.pdf` 505 × 153 bp |
| Unified LT(h) | `src/lt_unified.svg` | `lt.pdf` 240 × 89.6 bp | `lt-v2size.pdf` 505 × 189 bp |
| Pointer | `src/pointer_rule.svg` | `pointer.pdf` 249 × 177 bp | same file (already the v2 media box) |

`contact.png` is the review sheet: framework at text width, each of SW / LT / pointer beside the user v2 at the same pixel width, then the column-width renders.

VLDB sigconf after `\maketitle`: `\textwidth` = 506.295 TeX pt = 504.40 bp, `\columnwidth` = 241.147 TeX pt = 240.25 bp. SW and LT column files are 240 bp wide.

## What changed

Framework is the approved flat drawing, not the old numbered 16-element figure. Left side is four ordered runs with no digits. The middle is two merge nodes feeding one merge node. The cost-model box only says that it selects `k,h`, and three dashed blue drops land on the three merge nodes. Full and LIMIT are separate outputs. A dashed red pull under LIMIT ends on a stop tick labeled “stop at K”. No formula. `finite.py` is not in this tree, so none is drawn. There is no separate LIMIT figure and no segmented-LT figure.

SW, LT, and pointer are the user v2 vectors (`算法机制图/第二版/revision_v3/{sd_merge,lt_unified,pointer_rule}.svg`) with colors replaced and one legend edit. A color-stripped comparison of the SVG text matches the originals aside from that legend word and the page wash. Topology, numbers, and pointer targets are unchanged: Build assigns the pointer to R; Refresh in this example returns it to L.

Colors, shared by all four: paper `#FBF6EC`, emit `#3E7A9A`, call `#C56A55`, warm gray chips, merge nodes `#F4DFB8`.

Pointer legend: “next unread” is now “unread”. L/R labels and the thick pointer arrows are the original geometry.

## Size

SW and LT were drawn at 1700 user units with 29-unit labels. On the v2 page (505 bp) that is 8.6 pt. On a 240 bp column it is 4.1 pt. The column PDF is the single-column placement of that same drawing. `sw-v2size.pdf` and `lt-v2size.pdf` are the recolor at the user v2 media box, so the recolor can be judged without the column scale. Pointer labels are 23–29 units on a 1000-unit drawing; at 249 bp the legend is 5.7 pt and the column titles are 7.2 pt, which is the user v2 size.

## Looked at, not copied

ListK preprint Fig. 1 (page 2) is a listwise prompt beside an optimizer flow (tournament filter, quickselect, quicksort). It is not the geometry of these four figures.

`pointer_previous/` in the same revision directory is an older draft. The v2 pointer file used here is `pointer_rule.svg`.
