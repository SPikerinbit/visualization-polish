#!/usr/bin/env python3
"""Write doc/label-page-map.md from main.aux and main.pdf text."""
from __future__ import annotations
import json, re, subprocess
from pathlib import Path

tex = Path(__file__).resolve().parents[1] / "tex"
aux = (tex / "main.aux").read_text(errors="replace")
pdf = tex / "main.pdf"
text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
pages = text.split("\f")
label_pages = {}
for m in re.finditer(r"\\newlabel\{([^}]+)\}\{\{(\d+)", aux):
    label_pages[m.group(1)] = int(m.group(2))
sources = {
    "fig:exp2-surface-2x2": "integration/fig-e2-main.tex",
    "fig:exp3-scale": "integration/fig-e3-scale.tex",
    "fig:exp4b-beta": "integration/fig-e4b.tex",
    "fig:exp4c-full": "integration/fig-e4c.tex",
    "fig:exp4c-topk": "integration/fig-e4c.tex",
    "fig:exp5-k-sweep-off": "integration/fig-e5-sweep.tex",
    "fig:exp5-k-sweep-on": "integration/fig-e5-sweep.tex",
    "fig:eg:sliding_window": "integration/fig-sw.tex",
    "fig:eg:loser_tree_kway_group_merge": "integration/fig-lt.tex",
    "fig:eg:pointer-rule": "integration/fig-pointer.tex",
    "fig:exp:semantic_external_merge": "integration/fig-framework-algo1.tex",
    "fig:limit-demand-trial": "integration/fig-limit-appendix.tex",
    "alg:semantic_external_merge": "integration/pseudocode-alg1-only.tex",
    "alg:sliding_window_kway_group_merge": "integration/pseudocode-alg2-only.tex",
    "alg:loser_tree_kway_group_merge": "integration/pseudocode-alg3-only.tex",
    "alg:replay_segment_node": "integration/pseudocode-alg4-5.tex",
    "alg:refresh_loser_tree_path": "integration/pseudocode-alg4-5.tex",
}
out = Path(__file__).resolve().parents[1] / "doc" / "label-page-map.md"
lines = ["# Label → page → source (auto-generated)\n", f"PDF pages: {len(pages)}\n\n", "| Label | Page | TeX source |\n", "|-------|------|------------|\n"]
for lab in sorted(sources):
    pg = label_pages.get(lab, "—")
    lines.append(f"| `{lab}` | {pg} | `{sources[lab]}` |\n")
out.write_text("".join(lines))
(json_path := out.with_suffix(".json")).write_text(json.dumps({"label_pages": label_pages, "pages": len(pages)}, indent=2) + "\n")
print(f"wrote {out} and {json_path}")