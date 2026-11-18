# Round 2 mechanism figures

User decisions are in `DECISIONS.md`. What was measured and opened locally is in `ACCEPTANCE.md`. That note is not a parent acceptance.

Only this directory. Print files are the single-column SW, LT(h), and pointer, plus the text-width framework. There is no scaled-down copy of the wide v2 page.

`contact.png` uses one scale (6 px per bp). The framework is about twice as wide as the other three because that is the real page size. A 20 mm bar is on the sheet.

## Page size

| Figure | PDF | Size |
|---|---|---|
| Framework | `framework.pdf` | 504.4 × 119.1 bp, 178.0 × 42.0 mm |
| SW | `sw.pdf` | 240 × 96 bp |
| Unified LT(h) | `lt.pdf` | 240 × 124 bp |
| Pointer | `pointer.pdf` | 240 × 150 bp |

Column width after `\maketitle` is 241.147 TeX pt = 240.25 bp. These three are 240 bp wide. The viewBox unit is 1 bp, so the `font-size` in the SVG is the size on the page.

## Type size on the page

SW: round titles 7 bp; digits, run labels, and the legend 6.5 bp.

LT(h): titles, digits, run labels, and the legend 6.5 bp. Four leaves in each of three panels leave about 2.8 bp between leaf capsules, which is why the digits are 6.5 bp rather than 7 bp. A 7 bp digit pair is 7.8 bp wide and does not fit that gap with a visible call outline.

Pointer: column titles 7 bp; digits, L/R, row labels, and the legend 6.5 bp.

Framework: “ordered runs” 7 pt; merge, Full, LIMIT, cost model, and “stop at K” 6.5 pt.

## What the pictures say

Framework. Four anonymous runs enter two merges, then one root. The cost box sits between them and the dashed blue lines end on those three merges; they carry `k,h`. Solid arrows run from the root to Full and to LIMIT. The dashed red request starts at LIMIT and ends on the root. A bar on that path is labeled “stop at K”.

SW and LT keep the three v2 states, the same numbers, and the same pointers. In every LT state the right node points at R3. In the updated state the root points at its right child. Build sets the pointer to R. This refresh returns it to L. The red outline in LT panel (b) encloses only the refreshed root, its left child, and R2.

Pointer stays two rows by three columns. Winner and loser are not repeated in the cells; the shared legend carries those words, and the colors match the cells. The red letter under the replay is the side that runs out (`R` on Build, `L` on Refresh). L/R on the trees and on the replay slots stay.

Colors are unchanged from the previous round: paper `#FBF6EC`, emit `#3E7A9A`, call `#C56A55`, head gray `#9A9086`, unread `#D5CBBC`.

## Not claimed

`finite.py` is not in this tree, so the cost box has no formula. ListK Fig. 1 is a different diagram and is not the geometry here.
