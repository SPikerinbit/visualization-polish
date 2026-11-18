# Round 2 tables and pseudocode

Standalone VLDB-geometry preview. No paper body. Experiment cells are constructed examples, not measurements. The ranking protocol is `STATS.md`. Decisions for this round are `HANDOFF.md`. Table 2 formulas are unchecked.

## Build

```bash
./build.sh
```

The script runs the ranking tests, regenerates `tex/generated/`, and compiles `tex/preview.tex` with the repository `paper/tex/vendor` classes. Output is `build/preview.pdf` and `build/page-*.png`. Do not edit numbers in `tex/generated/` by hand.

`TEXINPUTS` must be the absolute path of `paper/tex/vendor`. `build.sh` sets that.
