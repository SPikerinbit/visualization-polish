# VLDB 2027 full paper TeX integration

This directory restores the SIGMOD-submission-era multi-file paper (`main.tex`, `framework.tex`, `exp.tex`, …) under the official PVLDB Vol.~20 `acmart` + `pvldb` vendor pins in `tex/vendor/`.

Specialist deliverables are imported under `recovery/` and `viz/recovery/`; only parent-approved PDFs are copied into `tex/fig-approved/` and wired through `tex/integration/*.tex`.

- Mapping: `../doc/paper-integration-map.md`
- Build (parent box, TL 2026): `./build.sh`
- Local inspection (TL 2023 VM): `./build-local.sh`

Do not treat `viz/tex/main.tex` as the paper entry point; that tree was the rejected layout supplement.