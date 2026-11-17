# Round 3

Inspection PDF on this VM: TeX Live 2023, 20 pages. `viz/build.sh` still refuses 2023. On TeX Live 2026 it now skips bibtex when `main.aux` has no `\citation`, then runs the two remaining pdflatex passes. A real bibtex failure is not ignored.

| Item | Result | Inspection page |
|---|---|---|
| 1. build.sh bibtex | Fixed in the script. No citations, so bibtex is skipped. | — |
| 2. z-axis ticks | Restored on the spine of every panel, values 80, 110, 140. Titles no longer list those numbers. The 2×3 page is marked as the denser alternative. | 7 and 8 |
| 3. Exp 4c shared limits | Off and On-cold use one x range and one y range, with the same ticks 30–110. A unit test checks the shared bounds. | 12 and 13 |
| 4. Old tables | Page 1 is the parameter-setting table and the method table. The symbol table is separate and is not described as the parameter table. Validation numbers are synthetic. Best `(k,h)` stays open. | 1–3 |
| 5. LIMIT figure | Two states. Dashed arrow down is a request. Solid arrow up is a yield. After K the next request is crossed out. 6 and 14 stay unread. aclose is labeled cleanup. | 20, above Algorithm 1 |
| 6. LT main figure | Four steps of one example: windows, call 1, yield, one refresh. h=1 is a note, not a second algorithm. The pointer panels stay separate. | 17 |

Page 1 no longer carries an abstract, a copyright block, or an unfilled title page. The class file and margins were not edited.

Known limits: some figure pages still end with open space when the next figure does not fit. `finite.py` is still unread. Formal measurements are not in these plots.
