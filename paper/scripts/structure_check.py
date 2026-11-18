#!/usr/bin/env python3
"""Post-compile structure check (cwd may be paper/tex). Requires paper/doc/label-page-map.json."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


def paper_root() -> Path:
    env = os.environ.get("PAPER_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[1]


def main() -> int:
    paper = paper_root()
    tex = paper / "tex"
    pdf = tex / "main.pdf"
    aux_path = tex / "main.aux"
    if not aux_path.is_file() or not pdf.is_file():
        print("structure check failed: missing main.aux or main.pdf", file=sys.stderr)
        return 1

    aux = aux_path.read_text(errors="replace")
    labels = {m.group(1) for m in re.finditer(r"\\newlabel\{([^}]+)\}", aux) if not m.group(1).endswith("@cref")}
    required_labels = {
        "fig:exp2-surface-2x2",
        "fig:exp2-surface-2x3",
        "fig:exp3-scale",
        "fig:exp4a-dl20-n100",
        "fig:exp4a-covid-n500",
        "fig:exp4b-beta",
        "fig:exp4c-full",
        "fig:exp4c-topk",
        "fig:exp5-k-sweep-off",
        "fig:exp5-k-sweep-on",
        "fig:exp:semantic_external_merge",
        "fig:eg:sliding_window",
        "fig:eg:loser_tree_kway_group_merge",
        "alg:semantic_external_merge",
        "alg:sliding_window_kway_group_merge",
        "alg:loser_tree_kway_group_merge",
        "alg:replay_segment_node",
        "alg:refresh_loser_tree_path",
    }
    missing_labels = sorted(lab for lab in required_labels if lab not in labels)
    for rel in (
        "fig-approved/sw-wide.pdf",
        "fig-approved/algo1-framework.pdf",
        "fig-approved/e4a-compact-dl20-n100.pdf",
        "fig-approved/e4a-compact-trec-covid-n500.pdf",
        "fig-approved/e4b-beta.pdf",
        "fig-approved/exp4c-full-labeled.pdf",
        "fig-approved/exp4c-topk-labeled.pdf",
        "fig-approved/e5-limit-sweep-off.pdf",
        "fig-approved/e5-limit-sweep-on.pdf",
        "integration/pseudocode-alg1-only.tex",
    ):
        if not (tex / rel).exists():
            missing_labels.append(f"missing-file:{rel}")

    text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
    if "VISUAL LAYOUT PREVIEW" not in text or "NOT EXPERIMENTAL RESULTS" not in text:
        missing_labels.append("footer")
    elif not re.search(
        r"VISUAL LAYOUT PREVIEW\s+[-\u2010-\u2015—–]+\s+NOT EXPERIMENTAL RESULTS",
        text,
    ):
        missing_labels.append("footer-exact")

    map_json = paper / "doc" / "label-page-map.json"
    if not map_json.is_file():
        missing_labels.append("missing-file:paper/doc/label-page-map.json")

    if missing_labels:
        print(f"structure check failed: {missing_labels}", file=sys.stderr)
        return 1

    pages = len(text.split("\f"))
    print(f"structure ok pages={pages} labels={len(labels)} map={map_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())