# Round 2 tables and pseudocode

Standalone VLDB-geometry preview. No paper body. Table 1 is the approved dataset table and is not restyled. Experiment cells are a synthetic layout: official measurements are not in this tree.

## Build

```bash
./build.sh
```

The script runs the ranking tests, regenerates `tex/generated/`, and compiles `tex/preview.tex` with the repository `paper/tex/vendor` classes. Output is `build/preview.pdf` and `build/page-*.png`. Do not edit numbers in `tex/generated/` by hand.

`TEXINPUTS` must be the absolute path of `paper/tex/vendor`. `build.sh` sets that.
