# VLDB 2027 layout supplement

Charts, tables, and pseudocode. Plot heights are synthetic.

## Acceptance build

`build.sh` runs only under TeX Live 2026. On any other engine, including Ubuntu TeX Live 2023, it exits 1 and does not claim success.

```bash
cd viz
sh build.sh
```

The script checks `pdflatex --version` for `TeX Live 2026`, checks that `eso-pic.sty` and `placeins.sty` resolve, and sets:

```bash
TEXINPUTS=./vendor:
BSTINPUTS=./vendor:
BIBINPUTS=./vendor:
```

`tex/vendor` is the unmodified PVLDB Vol. 20 class (`acmart.cls` v2.19, 2026/06/27, and `pvldb.sty`). Do not edit those files to change margins.

## What this VM compiled

This environment has TeX Live 2023. A local inspection PDF can be produced with the same `TEXINPUTS` / `BSTINPUTS` / `BIBINPUTS` lines, but that file is not the acceptance PDF. The round-2 notes say so: `doc/review-round2.md`.

```bash
cd viz
python3 -m pytest tests -q
LAYOUT_REQUIRE_PDF=1 python3 -m pytest tests/test_pdf_coverage.py -q
```

The coverage test fails if a declared figure is missing from the log, if any of Algorithms 1–5 is missing from the PDF text, or if a page has almost no text.
