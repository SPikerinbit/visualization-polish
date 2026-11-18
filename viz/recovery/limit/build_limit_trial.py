#!/usr/bin/env python3
"""Generate the LIMIT on-demand concept trial and check arrow endpoints.

The picture is a synthetic mechanism example on the shared 16-element runs.
It is not a measured result and not an execution trace. Public paper files
are not modified; this script only writes this directory.
"""

from __future__ import annotations

import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent

# sigconf text width: 8.5in minus 54pt inner and outer margins.
# 8.5*72.27 - 108 = 506.295pt = 177.96mm. Wide mechanism figures use 178mm.
PAGE_W = 178.0
MARGIN_X = 1.4
PANEL_GAP = 3.2
PANEL_W = (PAGE_W - 2 * MARGIN_X - 2 * PANEL_GAP) / 3

R = 2.25
ROW_PITCH = 6.45
PAD_B = 1.0
ROOT_H = 8.2
ROOT_GAP = 1.8
ARROW_GAP = 12.4
DRIVER_H = 12.6
TITLE_CLEAR = 3.6

# Run circle centers, bottom row first: R4, R3, R2, R1.
CY = [PAD_B + R + i * ROW_PITCH for i in range(4)]
RUNS_TOP = CY[-1] + R
ROOT_BOTTOM = RUNS_TOP + ROOT_GAP
ROOT_TOP = ROOT_BOTTOM + ROOT_H
DRIVER_BOTTOM = ROOT_TOP + ARROW_GAP
DRIVER_TOP = DRIVER_BOTTOM + DRIVER_H
TITLE_Y = DRIVER_TOP + TITLE_CLEAR
PANEL_H = TITLE_Y + 1.6

LEGEND_BOTTOM = 1.0
LEGEND_H = 14.4
PANELS_Y = LEGEND_BOTTOM + LEGEND_H + 1.4
NOTE_Y = PANELS_Y + PANEL_H + 3.5
PAGE_H = NOTE_Y + 2.4

BOX_L = 0.55
BOX_R = PANEL_W - 0.55
REQ_X = 8.2
YLD_X = 34.4
ACL_X = 51.6
SLOT_R = 2.15
SLOT_XS = (31.4, 37.6)
SLOT_CY = DRIVER_BOTTOM + 6.55

# Tight run group, centered. Four stacked runs, not a 2x2 pairing.
GROUP_W = 31.2
GROUP_L = (PANEL_W - GROUP_W) / 2
LABEL_E = GROUP_L + 6.4
CIRCLE_X0 = GROUP_L + 6.4 + 0.85 + R
CIRCLE_PITCH = 2 * R + 1.2

RUNS = (
    ("R_1", (3, 7, 12, 16)),
    ("R_2", (1, 5, 6, 14)),
    ("R_3", (2, 8, 11, 15)),
    ("R_4", (4, 9, 10, 13)),
)
# CY index: R1 is the top row.
ROW_INDEX = {"R_1": 3, "R_2": 2, "R_3": 1, "R_4": 0}

INK = "262B30"
BLUE = "1F6F8B"
BLUEFILL = "E5F1F7"
MUTED = "5C6B76"
GRAY = "8E99A4"
RULE = "C5CED4"


@dataclass(frozen=True)
class Rect:
    name: str
    panel: int
    x0: float
    y0: float
    x1: float
    y1: float

    def contains_open(self, x: float, y: float, eps: float = 0.02) -> bool:
        return (self.x0 + eps) < x < (self.x1 - eps) and (self.y0 + eps) < y < (self.y1 - eps)

    def on_boundary(self, x: float, y: float, tol: float = 0.03) -> bool:
        inside_x = self.x0 - tol <= x <= self.x1 + tol
        inside_y = self.y0 - tol <= y <= self.y1 + tol
        on_x = abs(x - self.x0) <= tol or abs(x - self.x1) <= tol
        on_y = abs(y - self.y0) <= tol or abs(y - self.y1) <= tol
        return inside_x and inside_y and (on_x or on_y) and not (
            (self.x0 + tol) < x < (self.x1 - tol) and (self.y0 + tol) < y < (self.y1 - tol)
        )


@dataclass(frozen=True)
class Disk:
    name: str
    panel: int
    x: float
    y: float
    r: float


@dataclass(frozen=True)
class Edge:
    name: str
    panel: int
    x0: float
    y0: float
    x1: float
    y1: float
    kind: str  # request, yield, aclose


def panel_origin(i: int) -> tuple[float, float]:
    return (MARGIN_X + i * (PANEL_W + PANEL_GAP), PANELS_Y)


def circle_xy(run: str, index: int) -> tuple[float, float]:
    return (CIRCLE_X0 + index * CIRCLE_PITCH, CY[ROW_INDEX[run]])


def build():
    rects: list[Rect] = []
    disks: list[Disk] = []
    edges: list[Edge] = []
    labels: list[Rect] = []
    yielded = {0: set(), 1: {1}, 2: {1, 2}}
    prefix = {0: (), 1: (1,), 2: (1, 2)}
    titles = {
        0: r"(a) emitted $= 0$",
        1: r"(b) emitted $= 1 < K$",
        2: r"(c) emitted $= K$",
    }

    ids = [n for _, row in RUNS for n in row]
    if sorted(ids) != list(range(1, 17)):
        raise SystemExit("run identities are not the shared 16 elements")

    for p in range(3):
        ox, oy = panel_origin(p)

        def G(x, y):
            return (ox + x, oy + y)

        def add_rect(name, x0, y0, x1, y1):
            a, b = G(x0, y0)
            c, d = G(x1, y1)
            rects.append(Rect(name, p, a, b, c, d))

        def add_label(name, x, y, w, h, anchor="west"):
            # x,y is the anchor point in panel-local coordinates. h is the text height.
            gx, gy = G(x, y)
            if anchor == "west":
                labels.append(Rect(name, p, gx, gy - 0.45, gx + w, gy + h - 0.45))
            elif anchor == "east":
                labels.append(Rect(name, p, gx - w, gy - 0.45, gx, gy + h - 0.45))
            elif anchor == "center":
                labels.append(Rect(name, p, gx - w / 2, gy - h / 2, gx + w / 2, gy + h / 2))
            else:
                raise ValueError(anchor)

        add_rect("driver", BOX_L, DRIVER_BOTTOM, BOX_R, DRIVER_TOP)
        add_rect("root", BOX_L, ROOT_BOTTOM, BOX_R, ROOT_TOP)
        add_rect("counter", 1.7, DRIVER_BOTTOM + 1.55, 9.15, DRIVER_BOTTOM + 7.15)
        add_label("holds", 1.7, DRIVER_TOP - 2.85, 20.0, 2.5)
        add_label("kconst", 10.4, DRIVER_BOTTOM + 4.15, 12.5, 2.7)
        add_label("title", 0.4, TITLE_Y, 52.0, 2.8)
        add_label("root1", 1.9, ROOT_BOTTOM + 5.15, 36.0, 2.6)
        add_label("root2", 1.9, ROOT_BOTTOM + 2.15, 38.0, 2.4)
        add_label("prefix", (SLOT_XS[0] + SLOT_XS[1]) / 2, DRIVER_BOTTOM + 10.55, 8.0, 2.4, "center")

        for sx in SLOT_XS:
            disks.append(Disk(f"slot-{sx}", p, *G(sx, SLOT_CY), SLOT_R + 0.18))

        for run, row in RUNS:
            cy = CY[ROW_INDEX[run]]
            x_left = CIRCLE_X0 - R - 0.55
            x_right = CIRCLE_X0 + 3 * CIRCLE_PITCH + R + 0.55
            add_rect(run, x_left, cy - R - 0.5, x_right, cy + R + 0.5)
            add_label(run + "-lab", LABEL_E, cy, 6.2, 2.6, "east")
            for j, num in enumerate(row):
                disks.append(Disk(f"{run}-{num}", p, *G(*circle_xy(run, j)), R + 0.16))

        # Arrow lanes. Present or absent is the state change; x is fixed.
        mid = (DRIVER_BOTTOM + ROOT_TOP) / 2
        if p < 2:
            x, y0 = G(REQ_X, DRIVER_BOTTOM)
            _, y1 = G(REQ_X, ROOT_TOP)
            edges.append(Edge("request", p, x, y0, x, y1, "request"))
            add_label("request-word", REQ_X + 1.55, mid - 2.15, 9.4, 2.4)
        else:
            add_label("not-issued", REQ_X + 1.55, mid - 2.15, 13.2, 2.4)

        if p >= 1:
            x, y0 = G(YLD_X, ROOT_TOP)
            _, y1 = G(YLD_X, DRIVER_BOTTOM)
            edges.append(Edge("yield", p, x, y0, x, y1, "yield"))
            add_label("yield-word", YLD_X - 1.55, mid + 2.15, 10.4, 2.4, "east")
        if p == 2:
            x, y0 = G(ACL_X, DRIVER_BOTTOM)
            _, y1 = G(ACL_X, ROOT_TOP)
            edges.append(Edge("aclose", p, x, y0, x, y1, "aclose"))
            add_label("aclose-word", ACL_X - 1.55, mid + 1.7, 9.2, 2.3, "east")
            add_label("cleanup-word", ACL_X - 1.55, mid - 1.35, 11.2, 2.3, "east")

    return rects, disks, edges, labels, yielded, prefix, titles


def overlaps(a: Rect, b: Rect, gap: float = 0.35) -> bool:
    return not (
        a.x1 + gap <= b.x0 or b.x1 + gap <= a.x0 or a.y1 + gap <= b.y0 or b.y1 + gap <= a.y0
    )


def validate(rects, disks, edges, labels) -> list[str]:
    errors: list[str] = []
    report: list[str] = []

    # Fixed geometry: every named rectangle has one panel-local box.
    local: dict[tuple[str, int], tuple[float, float, float, float]] = {}
    for r in rects:
        ox, oy = panel_origin(r.panel)
        local[(r.name, r.panel)] = tuple(round(v, 3) for v in (r.x0 - ox, r.y0 - oy, r.x1 - ox, r.y1 - oy))
    for name in {n for n, _ in local}:
        base = local[(name, 0)]
        for p in (1, 2):
            if local[(name, p)] != base:
                errors.append(f"fixed-position fail: {name} panel {p} != panel 0")

    disk_local = {}
    for d in disks:
        ox, oy = panel_origin(d.panel)
        disk_local[(d.name, d.panel)] = (round(d.x - ox, 4), round(d.y - oy, 4), d.r)
    for name in {n for n, _ in disk_local}:
        base = disk_local[(name, 0)]
        for p in (1, 2):
            if disk_local[(name, p)] != base:
                errors.append(f"disk moved: {name}")

    by_panel_edges = {0: [], 1: [], 2: []}
    for e in edges:
        by_panel_edges[e.panel].append(e)
    kinds = {p: sorted(e.kind for e in by_panel_edges[p]) for p in range(3)}
    if kinds != {0: ["request"], 1: ["request", "yield"], 2: ["aclose", "yield"]}:
        errors.append(f"unexpected edges per panel: {kinds}")

    for e in edges:
        if e.kind == "request" and not (e.y0 > e.y1):
            errors.append("request does not point down")
        if e.kind == "yield" and not (e.y1 > e.y0):
            errors.append("yield does not point up")
        if e.kind == "aclose" and not (e.y0 > e.y1):
            errors.append("aclose does not point from the drain to the root")
        if abs(e.x0 - e.x1) > 1e-6:
            errors.append(f"{e.name} is not vertical")

        start_box = "driver" if e.kind in ("request", "aclose") else "root"
        end_box = "root" if e.kind in ("request", "aclose") else "driver"
        start = next(r for r in rects if r.panel == e.panel and r.name == start_box)
        end = next(r for r in rects if r.panel == e.panel and r.name == end_box)
        if not start.on_boundary(e.x0, e.y0):
            errors.append(f"{e.kind} p{e.panel} start is not on {start_box}")
        if not end.on_boundary(e.x1, e.y1):
            errors.append(f"{e.kind} p{e.panel} end is not on {end_box}")

        steps = 80
        for i in range(1, steps):
            t = i / steps
            x = e.x0 + (e.x1 - e.x0) * t
            y = e.y0 + (e.y1 - e.y0) * t
            for r in rects:
                if r.panel == e.panel and r.contains_open(x, y):
                    errors.append(f"{e.kind} p{e.panel} enters {r.name}")
                    break
            for d in disks:
                if d.panel == e.panel and math.hypot(x - d.x, y - d.y) <= d.r + 0.05:
                    errors.append(f"{e.kind} p{e.panel} pierces {d.name}")
                    break
        report.append(
            f"{e.kind} panel {e.panel}: ({e.x0:.2f},{e.y0:.2f}) -> ({e.x1:.2f},{e.y1:.2f}) "
            f"on {start_box} to {end_box}"
        )

    # Absent request still has a reserved label, and no request edge in panel 2.
    if any(e.kind == "request" and e.panel == 2 for e in edges):
        errors.append("panel (c) still draws a request")

    for i, a in enumerate(labels):
        if a.x0 < -0.2 or a.x1 > PAGE_W + 0.2 or a.y0 < 0 or a.y1 > PAGE_H:
            errors.append(f"label off page: {a.name} p{a.panel}")
        for d in disks:
            if d.panel != a.panel:
                continue
            # Approximate the reserved text box against the disk.
            nearest_x = min(max(d.x, a.x0), a.x1)
            nearest_y = min(max(d.y, a.y0), a.y1)
            if math.hypot(d.x - nearest_x, d.y - nearest_y) < d.r + 0.25:
                errors.append(f"label {a.name} hits {d.name}")
        for r in rects:
            if r.panel == a.panel and r.name in {"driver", "root", "counter"} and overlaps(a, r, gap=0.15):
                # Labels that are intentionally inside the driver are marked.
                if a.name in {"holds", "kconst", "prefix", "root1", "root2"} and r.name in {"driver", "root"}:
                    continue
                if a.name in {"holds", "kconst"} and r.name == "counter":
                    errors.append(f"label {a.name} hits counter")
                elif a.name not in {"holds", "kconst", "prefix", "root1", "root2"}:
                    errors.append(f"label {a.name} hits {r.name}")
        for b in labels[i + 1 :]:
            if a.panel == b.panel and overlaps(a, b, gap=0.4):
                errors.append(f"labels overlap: {a.name} and {b.name} in panel {a.panel}")

    # Disks inside their run container, and not inside the driver or root.
    containers = {r.name: r for r in rects}
    for d in disks:
        if d.name.startswith("slot"):
            driver = next(r for r in rects if r.panel == d.panel and r.name == "driver")
            if not (
                driver.x0 + d.r < d.x < driver.x1 - d.r
                and driver.y0 + d.r < d.y < driver.y1 - d.r
            ):
                errors.append(f"{d.name} is not inside the driver")
            continue
        run = d.name.split("-")[0]
        box = next(r for r in rects if r.panel == d.panel and r.name == run)
        if not (
            box.x0 + 0.2 < d.x - (d.r - 0.16)
            and d.x + (d.r - 0.16) < box.x1 - 0.2
            and box.y0 + 0.2 < d.y - (d.r - 0.16)
            and d.y + (d.r - 0.16) < box.y1 - 0.2
        ):
            errors.append(f"{d.name} is not inside its run")
        for r in rects:
            if r.panel == d.panel and r.name in {"driver", "root"} and r.contains_open(d.x, d.y):
                errors.append(f"{d.name} fell into {r.name}")

    # Containers do not overlap each other.
    run_rects = [r for r in rects if r.name.startswith("R_")]
    for i, a in enumerate(run_rects):
        for b in run_rects[i + 1 :]:
            if a.panel == b.panel and overlaps(a, b, gap=0.3):
                errors.append(f"runs overlap: {a.name} {b.name}")

    report.append(f"page {PAGE_W:.2f}mm x {PAGE_H:.2f}mm")
    report.append(f"panel width {PANEL_W:.2f}mm, panel local height {PANEL_H:.2f}mm")
    report.append("edges: " + str(kinds))
    if errors:
        report.append("FAIL")
        report.extend(errors)
    else:
        report.append("PASS")
    return errors, report


def tex_escape_comment(line: str) -> str:
    return line


def emit_tex(yielded, prefix, titles) -> str:
    lines = []
    a = lines.append
    a("% LIMIT on-demand concept trial. Generated by build_limit_trial.py.")
    a("% Not included by the paper. Not a measured result. Not an execution trace.")
    a(r"\documentclass{article}")
    a(r"\usepackage[T1]{fontenc}")
    a(r"\usepackage{mathptmx}")
    a(r"\usepackage{tikz}")
    a(r"\usetikzlibrary{arrows.meta}")
    a(r"\pagestyle{empty}")
    a(r"\setlength{\paperwidth}{%.2fmm}" % PAGE_W)
    a(r"\setlength{\paperheight}{%.2fmm}" % PAGE_H)
    a(r"\pdfpagewidth=\paperwidth")
    a(r"\pdfpageheight=\paperheight")
    a(r"\setlength{\hoffset}{-1in}")
    a(r"\setlength{\voffset}{-1in}")
    a(r"\setlength{\oddsidemargin}{0pt}")
    a(r"\setlength{\topmargin}{0pt}")
    a(r"\setlength{\headheight}{0pt}")
    a(r"\setlength{\headsep}{0pt}")
    a(r"\setlength{\topskip}{0pt}")
    a(r"\setlength{\footskip}{0pt}")
    a(r"\setlength{\marginparsep}{0pt}")
    a(r"\setlength{\marginparwidth}{0pt}")
    a(r"\setlength{\textwidth}{\paperwidth}")
    a(r"\setlength{\textheight}{\paperheight}")
    a(r"\setlength{\parindent}{0pt}")
    a(r"\definecolor{ink}{HTML}{%s}" % INK)
    a(r"\definecolor{yieldblue}{HTML}{%s}" % BLUE)
    a(r"\definecolor{bluefill}{HTML}{%s}" % BLUEFILL)
    a(r"\definecolor{muted}{HTML}{%s}" % MUTED)
    a(r"\definecolor{aclgray}{HTML}{%s}" % GRAY)
    a(r"\definecolor{rule}{HTML}{%s}" % RULE)
    a(r"\begin{document}%")
    a(r"\nointerlineskip")
    a(r"\begin{tikzpicture}[x=1mm,y=1mm,")
    a(r"  every node/.style={inner sep=0pt, outer sep=0pt},")
    a(r"  box/.style={draw=ink, line width=0.7pt, rounded corners=0.5mm},")
    a(r"  runbox/.style={draw=rule, line width=0.6pt, rounded corners=0.45mm},")
    a(r"  counter/.style={draw=ink, line width=0.6pt, rounded corners=0.35mm, fill=white},")
    a(r"  countermet/.style={counter, draw=yieldblue, line width=0.75pt},")
    a(r"  req/.style={draw=ink, line width=0.9pt, dash pattern=on 1.4pt off 1.05pt,")
    a(r"    -{Stealth[length=1.6mm,width=1.15mm]}},")
    a(r"  yld/.style={draw=yieldblue, line width=1.05pt,")
    a(r"    -{Stealth[length=1.75mm,width=1.25mm]}},")
    a(r"  acl/.style={draw=aclgray, line width=0.75pt, dash pattern=on 0.4pt off 0.85pt,")
    a(r"    -{Circle[open,length=1.35mm]}},")
    a(r"  fsmall/.style={font=\fontsize{6.6}{7.4}\selectfont},")
    a(r"  ftitle/.style={font=\fontsize{8}{9}\selectfont},")
    a(r"  fnum/.style={font=\fontsize{7}{8}\selectfont},")
    a(r"  fcount/.style={font=\fontsize{10}{11}\selectfont}")
    a(r"]")
    a(r"\useasboundingbox (0,0) rectangle (%.2f,%.2f);" % (PAGE_W, PAGE_H))
    a(
        r"\node[anchor=west, fsmall, text=ink] at (1.6,%.2f) "
        r"{Shared 16-element runs, $K=2$. Synthetic mechanism example, not a measured result.};"
        % NOTE_Y
    )

    # Legend, one row of swatches, then two footnote lines.
    ly = LEGEND_BOTTOM + 11.15
    a(r"\draw[req] (1.6,%.2f) -- (8.2,%.2f);" % (ly, ly))
    a(r"\node[anchor=west, fsmall, text=ink] at (9.0,%.2f) {request down};" % ly)
    a(r"\draw[yld] (32.5,%.2f) -- (39.1,%.2f);" % (ly, ly))
    a(r"\node[anchor=west, fsmall, text=ink] at (39.9,%.2f) {yield up};" % ly)
    a(r"\draw[acl] (58.5,%.2f) -- (65.1,%.2f);" % (ly, ly))
    a(r"\node[anchor=west, fsmall, text=ink] at (65.9,%.2f) {aclose, cleanup};" % ly)
    a(r"\draw[fill=bluefill, draw=yieldblue, line width=0.7pt] (97.2,%.2f) circle (1.7);" % ly)
    a(r"\node[fnum, text=yieldblue] at (97.2,%.2f) {1};" % ly)
    a(r"\node[anchor=west, fsmall, text=ink] at (99.6,%.2f) {in $\Pi_K$};" % ly)
    a(r"\draw[fill=white, draw=ink, line width=0.65pt] (118.5,%.2f) circle (1.7);" % ly)
    a(r"\node[fnum, text=ink] at (118.5,%.2f) {5};" % ly)
    a(r"\node[anchor=west, fsmall, text=ink] at (120.9,%.2f) {still in the run};" % ly)

    a(
        r"\node[anchor=west, fsmall, text=muted] at (1.6,%.2f) "
        r"{Full is a separate mode, not $K=\infty$. Non-root runs are not given $K$.};"
        % (LEGEND_BOTTOM + 6.35)
    )
    a(
        r"\node[anchor=west, fsmall, text=muted] at (1.6,%.2f) "
        r"{In (c) the request lane is empty: the drain does not call again. aclose is cleanup, not a comparison.};"
        % (LEGEND_BOTTOM + 3.15)
    )

    for p in range(3):
        ox, oy = panel_origin(p)
        a(r"\begin{scope}[shift={(%.3f,%.3f)}]" % (ox, oy))
        a(r"\node[anchor=west, ftitle, text=ink] at (0.4,%.2f) {%s};" % (TITLE_Y, titles[p]))
        a(
            r"\draw[box] (%.2f,%.2f) rectangle (%.2f,%.2f);"
            % (BOX_L, DRIVER_BOTTOM, BOX_R, DRIVER_TOP)
        )
        a(
            r"\draw[box] (%.2f,%.2f) rectangle (%.2f,%.2f);"
            % (BOX_L, ROOT_BOTTOM, BOX_R, ROOT_TOP)
        )
        counter_style = "countermet" if p == 2 else "counter"
        a(
            r"\draw[%s] (1.70,%.2f) rectangle (9.15,%.2f);"
            % (counter_style, DRIVER_BOTTOM + 1.55, DRIVER_BOTTOM + 7.15)
        )
        count_color = "yieldblue" if p == 2 else "ink"
        a(
            r"\node[fcount, text=%s] at (5.42,%.2f) {%d};"
            % (count_color, DRIVER_BOTTOM + 4.35, p)
        )
        a(
            r"\node[anchor=west, fsmall, text=ink] at (1.70,%.2f) {holds emitted};"
            % (DRIVER_TOP - 2.85)
        )
        a(
            r"\node[anchor=west, fsmall, text=ink] at (10.40,%.2f) {of $K=2$};"
            % (DRIVER_BOTTOM + 4.35)
        )
        a(
            r"\node[anchor=center, fsmall, text=muted] at (%.2f,%.2f) {$\Pi_K$};"
            % ((SLOT_XS[0] + SLOT_XS[1]) / 2, DRIVER_BOTTOM + 10.55)
        )
        for i, sx in enumerate(SLOT_XS):
            filled = i < len(prefix[p])
            if filled:
                a(
                    r"\draw[fill=bluefill, draw=yieldblue, line width=0.75pt] (%.2f,%.2f) circle (%.2f);"
                    % (sx, SLOT_CY, SLOT_R)
                )
                a(
                    r"\node[fnum, text=yieldblue] at (%.2f,%.2f) {%d};"
                    % (sx, SLOT_CY, prefix[p][i])
                )
            else:
                a(
                    r"\draw[fill=white, draw=rule, line width=0.6pt, dash pattern=on 0.7pt off 0.55pt] (%.2f,%.2f) circle (%.2f);"
                    % (sx, SLOT_CY, SLOT_R)
                )
        a(
            r"\node[anchor=west, fsmall, text=ink] at (1.90,%.2f) {root producer};"
            % (ROOT_BOTTOM + 5.15)
        )
        a(
            r"\node[anchor=west, fsmall, text=muted] at (1.90,%.2f) {answers the pull};"
            % (ROOT_BOTTOM + 2.15)
        )

        for run, row in RUNS:
            cy = CY[ROW_INDEX[run]]
            x_left = CIRCLE_X0 - R - 0.55
            x_right = CIRCLE_X0 + 3 * CIRCLE_PITCH + R + 0.55
            a(
                r"\draw[runbox] (%.2f,%.2f) rectangle (%.2f,%.2f);"
                % (x_left, cy - R - 0.5, x_right, cy + R + 0.5)
            )
            a(
                r"\node[anchor=east, fnum, text=ink] at (%.2f,%.2f) {$%s$};"
                % (LABEL_E, cy, run)
            )
            for j, num in enumerate(row):
                x = CIRCLE_X0 + j * CIRCLE_PITCH
                if num in yielded[p]:
                    a(
                        r"\draw[fill=bluefill, draw=yieldblue, line width=0.75pt] (%.2f,%.2f) circle (%.2f);"
                        % (x, cy, R)
                    )
                    a(r"\node[fnum, text=yieldblue] at (%.2f,%.2f) {%d};" % (x, cy, num))
                else:
                    a(
                        r"\draw[fill=white, draw=ink, line width=0.65pt] (%.2f,%.2f) circle (%.2f);"
                        % (x, cy, R)
                    )
                    a(r"\node[fnum, text=ink] at (%.2f,%.2f) {%d};" % (x, cy, num))

        mid = (DRIVER_BOTTOM + ROOT_TOP) / 2
        if p < 2:
            a(r"\draw[req] (%.2f,%.2f) -- (%.2f,%.2f);" % (REQ_X, DRIVER_BOTTOM, REQ_X, ROOT_TOP))
            a(
                r"\node[anchor=west, fsmall, text=ink] at (%.2f,%.2f) {request};"
                % (REQ_X + 1.55, mid - 2.15)
            )
        else:
            a(
                r"\node[anchor=west, fsmall, text=muted] at (%.2f,%.2f) {not issued};"
                % (REQ_X + 1.55, mid - 2.15)
            )
        if p >= 1:
            item = prefix[p][-1]
            a(r"\draw[yld] (%.2f,%.2f) -- (%.2f,%.2f);" % (YLD_X, ROOT_TOP, YLD_X, DRIVER_BOTTOM))
            a(
                r"\node[anchor=east, fsmall, text=yieldblue] at (%.2f,%.2f) {yield %d};"
                % (YLD_X - 1.55, mid + 2.15, item)
            )
        if p == 2:
            a(r"\draw[acl] (%.2f,%.2f) -- (%.2f,%.2f);" % (ACL_X, DRIVER_BOTTOM, ACL_X, ROOT_TOP))
            a(
                r"\node[anchor=east, fsmall, text=aclgray] at (%.2f,%.2f) {aclose};"
                % (ACL_X - 1.55, mid + 1.7)
            )
            a(
                r"\node[anchor=east, fsmall, text=aclgray] at (%.2f,%.2f) {cleanup};"
                % (ACL_X - 1.55, mid - 1.35)
            )
        a(r"\end{scope}")

    a(r"\end{tikzpicture}%")
    a(r"\end{document}")
    a("")
    return "\n".join(lines)


def main() -> None:
    rects, disks, edges, labels, yielded, prefix, titles = build()
    errors, report = validate(rects, disks, edges, labels)
    text = emit_tex(yielded, prefix, titles)
    if "red" in text.lower() or "infty" in text and False:
        pass
    forbidden = ("ListwiseRank", "infinity", "knows $K$", "K=\\infty")
    # K=\infty is allowed only in the explicit denial sentence.
    denial = text.count(r"K=\infty")
    if denial != 1:
        errors.append(f"expected one denial of K=infinity, found {denial}")
    if "ListwiseRank" in text or "knows $K$" in text:
        errors.append("forbidden claim in the figure text")
    (HERE / "limit-ondemand.tex").write_text(text, encoding="utf-8")
    (HERE / "geometry-report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    if errors:
        raise SystemExit(1)
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "limit-ondemand.tex"],
        cwd=HERE,
        check=True,
    )
    subprocess.run(
        ["pdftoppm", "-png", "-r", "170", "limit-ondemand.pdf", "limit-ondemand"],
        cwd=HERE,
        check=True,
    )
    # pdftoppm writes limit-ondemand-1.png for a one-page file.
    produced = HERE / "limit-ondemand-1.png"
    target = HERE / "limit-ondemand.png"
    if produced.exists():
        produced.replace(target)
    info = subprocess.run(["pdfinfo", str(HERE / "limit-ondemand.pdf")], check=True, capture_output=True, text=True)
    print(info.stdout)


if __name__ == "__main__":
    main()
