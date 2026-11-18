# Local check, not a parent acceptance

Checked on commit `7fe71c8` and the placement preview built with it. The parent’s 11:19 review of the earlier 4.1 bp page is what this revision answers. That review has not been repeated on these files.

## Which PR

Latest mechanism sources are PR 16, branch `cursor/round2-mechanisms-6f22`. PR 13 is `cursor/framework-algo1-cost-6f22` and is the older numbered framework. It does not contain this directory.

## What was rendered and opened

`framework.pdf` is 504.394 × 119.054 bp (178.0 × 42.0 mm). `sw.pdf` is 240 × 96 bp. `lt.pdf` is 240 × 124 bp. `pointer.pdf` is 240 × 150 bp. Column width in the sigconf class after `\maketitle` is recorded in the preview log.

The SVG viewBox unit is 1 bp, so `font-size` is the page size. SW titles are 7 bp and the other SW text is 6.5 bp. LT text is 6.5 bp. Pointer column titles are 7 bp and the other pointer text is 6.5 bp. Framework labels are 6.5 pt and 7 pt.

LT does not reach 7 bp. A 7 bp pair of digits is 7.8 bp wide. Four leaves in each of three panels at 240 bp leave about 2.8 bp between capsules, and the call outline sits in that gap.

Opened `framework.png`, `sw.png`, `lt.png`, and `pointer.png` after the rebuild. Framework: solid data runs from the root merge to Full and to LIMIT; the dashed request starts on LIMIT, breaks at `K`, and ends on the root; the three `k,h` dashes end on the three merges and pass above or below the data. SW and LT keep the three v2 states and the same numbers. Pointer is two rows by three columns; L/R and the thick pointer remain; winner and loser are named once in the legend; Build is marked `R` and Refresh is marked `L`.

`src/preview.tex` is an `acmart` sigconf document with `pvldb` and no article prose. After `\maketitle` the log records `\textwidth` = 506.295 pt and `\columnwidth` = 241.14749 pt. The framework is placed at `\textwidth`. SW, LT(h), and pointer are placed at `\linewidth` in the columns. A second `pdflatex` pass writes `preview.pdf` (2 pages). Page 2 shows the full-width framework and the three column figures.

## Not claimed

No formula, because `finite.py` is absent. ListK Fig. 1 is a different diagram. This note does not say the parent accepted the figures.
