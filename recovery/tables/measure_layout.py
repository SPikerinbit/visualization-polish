#!/usr/bin/env python3
"""Print table-band widths and font sizes from a compiled checkpoint PDF."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PDF = ROOT / "render" / "main.pdf"


def pdffonts(pdf: Path) -> list[tuple[str, str]]:
    out = subprocess.check_output(["pdffonts", str(pdf)], text=True, errors="replace")
    rows = []
    for line in out.strip().splitlines()[2:]:
        parts = line.split()
        if len(parts) >= 4:
            rows.append((parts[0], parts[3]))
    return rows


def bbox_for_page(pdf: Path, page: int) -> str:
    xml = subprocess.check_output(["pdftotext", "-bbox", "-f", str(page), "-l", str(page), str(pdf), "-"], text=True)
    return xml


def band_widths(page_xml: str) -> dict[str, float]:
    words = re.findall(
        r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>',
        page_xml,
    )
    if not words:
        return {}
    page_w = float(re.search(r'width="([\d.]+)"', page_xml).group(1))
    table_words = [(float(a), float(b), float(c), float(d), t.strip()) for a, b, c, d, t in words if "Table" in t or t.isdigit() or "±" in t or t in {"Method", "Q9", "DL20", "DL22", "COVID", "DBpedia", "Robust04", "Pointwise", "SW", "LT"} or "ListK" in t]
    if len(table_words) < 40:
        table_words = [(float(a), float(b), float(c), float(d), t.strip()) for a, b, c, d, t in words]
    xs = [w[0] for w in table_words] + [w[2] for w in table_words]
    ys = [w[1] for w in table_words] + [w[3] for w in table_words]
    # Split by vertical gap for two bands on main-table pages
    lines = sorted(set(round(w[1], 0) for w in table_words if w[4]))
    if len(lines) < 5:
        return {"page_width_pt": page_w, "ink_width_pt": max(xs) - min(xs)}
    mid_y = (min(ys) + max(ys)) / 2
    top = [w for w in table_words if float(w[1]) < mid_y - 20]
    bot = [w for w in table_words if float(w[1]) > mid_y + 20]
    def span(ws):
        if not ws:
            return 0.0
        return max(w[2] for w in ws) - min(w[0] for w in ws)
    top_w = span(top)
    bot_w = span(bot)
    text_w = 506.295
    return {
        "page_width_pt": page_w,
        "textwidth_pt": text_w,
        "upper_band_pt": round(top_w, 1),
        "lower_band_pt": round(bot_w, 1),
        "upper_pct_page": round(100 * top_w / page_w, 1),
        "lower_pct_page": round(100 * bot_w / page_w, 1),
        "upper_pct_text": round(100 * top_w / text_w, 1),
        "lower_pct_text": round(100 * bot_w / text_w, 1),
    }


def main():
    pdf = PDF if len(sys.argv) < 2 else Path(sys.argv[1])
    if not pdf.exists():
        print(f"missing {pdf}", file=sys.stderr)
        sys.exit(1)
    print(f"PDF: {pdf}")
    print("Fonts (subset name, size pt):")
    for name, size in pdffonts(pdf):
        if any(x in name for x in ("LF", "Libertine", "LinLibertine", "LinuxLibertine")):
            print(f"  {name}: {size}")
    # Page 3 is first 9B full main table in current render/main.tex ordering
    for page in (3,):
        stats = band_widths(bbox_for_page(pdf, page))
        print(f"Page {page} band widths: {stats}")


if __name__ == "__main__":
    main()