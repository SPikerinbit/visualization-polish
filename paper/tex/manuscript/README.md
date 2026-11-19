# Integrated manuscript

The paper entry is [main.tex](../main.tex). Build from this checkout with `sh paper/tex/build-manuscript.sh` using pdfLaTeX and BibTeX. The artwork is included as vector PDFs from `paper/round2/`; there is no figure regeneration step. The source is intentionally stored as separate uncompressed TeX files.

- Introduction and Preliminaries still use the original `inrto.tex` and `problem statement.tex`. The unchanged Introduction's previous query and baseline counts are not the revised E1 protocol.
- The original five reviewed algorithms are integrated into the methods narrative. The manuscript copy of Algorithm 2 follows the current fixed-quota SW implementation. The separate layout review and historical algorithms remain available for provenance.
- E1 numeric cells and E1 through E5 result prose are empty. The included experiment plots are synthetic layout figures and will be regenerated from experiment outputs. The setup follows the [2026-11-19 experiment plan](https://github.com/SPikerinbit/SemaPrototype_cost_model_v6/blob/master/experiments/studies/2026-11-19/unified-paper-release/approved-plan.md).
- Cloud proof build: TeX Live 2025/dev, not a substitute for the final TeX Live 2026 submission build.
