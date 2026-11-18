# Source-zip build verification (agent VM, 2026-11-18)

## Artifacts

| File | SHA-256 |
|------|---------|
| `paper-integration-sources.zip` | `95a5ab16910e81df817a6f9483522e9987934c21c86f5577216cc7fe3344174c` |
| `paper/build.sh` (inside zip) | `56d6d91c0a037449174bf36cbda87291927dfda51dc66cda05895f86006b01c7` |

## Procedure

```sh
TMP=$(mktemp -d)
unzip -q paper-integration-sources.zip -d "$TMP"
cd "$TMP"
PAPER_BUILD_ALLOW_LOCAL_TEX=1 ./paper/build.sh
```

- `PAPER_BUILD_ALLOW_LOCAL_TEX=1` skips **only** the TeX Live 2026 engine gate on this TL2023 VM.
- Post-compile steps still run: `scripts/label_page_map.py` → `paper/doc/label-page-map.{md,json}`, repo `doc/` sync, `scripts/structure_check.py`.

## Result

- **Exit code:** `0`
- **Tail:** `structure ok pages=33 labels=77 map=.../paper/doc/label-page-map.json`
- **Label map** includes `fig:exp2-surface-2x3` → page **30**.

## Parent TL2026

Run from extracted root **without** `PAPER_BUILD_ALLOW_LOCAL_TEX` (default). Expect `paper/build.sh` exit **0** with same post-check.

**Commit:** `f9f4194` (layout unchanged from `33b2ed8`; PDF 32 pages).