#!/usr/bin/env python3
"""Measure E1 main-table rule geometry (not ink spans) in the checkpoint PDF."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parent
PDF = ROOT / "render" / "main.pdf"
TEXT_LEFT = 54.0
TEXT_RIGHT = 560.3
TEXT_WIDTH = 506.295
MAIN_PAGES = (3, 4, 5, 6)


def rule_spans(page: fitz.Page, min_width: float = 350.0) -> list[tuple[float, float, float]]:
    """Return (x0, x1, y) for long horizontal rules (booktabs toprule/bottomrule)."""
    spans: list[tuple[float, float, float]] = []
    for drawing in page.get_drawings():
        rect = drawing.get("rect")
        if rect is not None:
            w = rect.x1 - rect.x0
            h = rect.y1 - rect.y0
            if w >= min_width and h <= 2.5:
                spans.append((rect.x0, rect.x1, (rect.y0 + rect.y1) / 2))
                continue
        for item in drawing.get("items", ()):
            if item[0] != "l":
                continue
            p1, p2 = item[1], item[2]
            if abs(p1.y - p2.y) > 1.0:
                continue
            x0, x1 = sorted((p1.x, p2.x))
            if x1 - x0 >= min_width:
                spans.append((x0, x1, (p1.y + p2.y) / 2))
    dedup: dict[tuple[int, int], tuple[float, float, float]] = {}
    for x0, x1, y in spans:
        key = (int(round(y)), int(round((x0 + x1) / 2)))
        dedup[key] = (x0, x1, y)
    return sorted(dedup.values(), key=lambda t: (t[2], t[0]))


def _span_info(x0: float, x1: float, y: float, label: str) -> dict:
    width = x1 - x0
    return {
        "segment": label,
        "x0": round(x0, 1),
        "x1": round(x1, 1),
        "y": round(y, 1),
        "width_pt": round(width, 1),
        "within_text_edges": x0 >= TEXT_LEFT - 0.6 and x1 <= TEXT_RIGHT + 0.6,
        "width_ok": width <= TEXT_WIDTH + 0.6,
    }


def band_rule_widths(page: fitz.Page) -> list[dict]:
    """Upper/lower E1 tabular toprules (widest rules at each band)."""
    spans = rule_spans(page)
    if not spans:
        return []
    wide = [s for s in spans if s[1] - s[0] >= TEXT_WIDTH - 20]
    if not wide:
        wide = spans
    upper = min(wide, key=lambda t: t[2])
    lower_pool = [s for s in wide if s[2] > upper[2] + 80]
    if not lower_pool:
        return [_span_info(*upper, "upper")]
    lower = min(lower_pool, key=lambda t: t[2])
    return [_span_info(*upper, "upper"), _span_info(*lower, "lower")]


def measure(pdf: Path) -> dict:
    doc = fitz.open(pdf)
    report = {
        "pdf": str(pdf),
        "text_left_pt": TEXT_LEFT,
        "text_right_pt": TEXT_RIGHT,
        "textwidth_pt": TEXT_WIDTH,
        "pages": {},
        "ok": True,
    }
    for page_no in MAIN_PAGES:
        page = doc[page_no - 1]
        bands = band_rule_widths(page)
        page_ok = all(b["within_text_edges"] and b["width_ok"] for b in bands)
        report["pages"][str(page_no)] = {"bands": bands, "ok": page_ok}
        if not page_ok:
            report["ok"] = False
    doc.close()
    return report


def main() -> None:
    pdf = PDF if len(sys.argv) < 2 else Path(sys.argv[1])
    if not pdf.exists():
        print(f"missing {pdf}", file=sys.stderr)
        sys.exit(1)
    report = measure(pdf)
    print(json.dumps(report, indent=2))
    if not report["ok"]:
        sys.exit(2)


if __name__ == "__main__":
    main()