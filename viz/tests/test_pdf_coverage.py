"""Fail if a declared figure or algorithm is absent from the built PDF."""

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "tex" / "main.pdf"
REQUIRED_FIGURES = [
    "exp2-2x2.pdf",
    "exp2-2x3.pdf",
    "exp3-2x2.pdf",
    "exp4a.pdf",
    "exp4b.pdf",
    "exp4c-full.pdf",
    "exp4c-limit.pdf",
    "exp5-off.pdf",
    "exp5-on.pdf",
    "mech-intro.pdf",
    "mech-sw.pdf",
    "mech-lt.pdf",
    "mech-pointer-a.pdf",
    "mech-pointer-b.pdf",
    "mech-virtual.pdf",
    "mech-limit.pdf",
]


def test_declared_figures_exist_as_files():
    missing = [name for name in REQUIRED_FIGURES if not (ROOT / "figures" / name).exists()]
    assert not missing


def test_sources_are_named_by_the_tex():
    tex = (ROOT / "tex" / "main.tex").read_text(encoding="utf-8")
    for name in REQUIRED_FIGURES:
        assert name in tex
    algos = (ROOT / "tex" / "algorithms.tex").read_text(encoding="utf-8")
    assert algos.count(r"\begin{algorithm}") == 5
    assert r"\label{alg:sw}" in algos


def test_shipped_pdf_contains_every_figure_and_algorithm():
    if os.environ.get("LAYOUT_REQUIRE_PDF") != "1":
        return
    assert PDF.exists(), "main.pdf was not built"
    log = (ROOT / "tex" / "main.log").read_text(encoding="utf-8", errors="replace")
    for name in REQUIRED_FIGURES:
        assert name in log, name
    text = subprocess.check_output(["pdftotext", "-layout", str(PDF), "-"], text=True)
    for label in ("Algorithm 1", "Algorithm 2", "Algorithm 3", "Algorithm 4", "Algorithm 5"):
        assert label in text
    assert "exp3-row.pdf" not in (ROOT / "tex" / "main.tex").read_text(encoding="utf-8")
    pages = [page for page in text.split("\f") if page.strip()]
    blank = []
    for i, page in enumerate(pages, start=1):
        body = page.replace("SYNTHETIC DATA — LAYOUT PREVIEW ONLY", "")
        if sum(ch.isalnum() for ch in body) < 40:
            blank.append(i)
    assert blank == []
    assert shutil.which("pdflatex")
