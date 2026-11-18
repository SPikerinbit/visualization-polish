#!/usr/bin/env python3
"""Build the unified LT(h) main-figure TikZ at the v2 canvas.

Coordinates are the v2 SVG pixel grid (1700 x 635). The PDF media box matches
fig-F-lt-unified-v2.pdf (504.96 bp x 187.92 bp) so a same-size comparison is
possible. Node centers are the v2 centers; edges stop on the segment outline.
"""

from __future__ import annotations

import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "lt-h-main.tex"

W_PX, H_PX = 1700.0, 635.0
W_BP, H_BP = 504.95999, 187.92

# v2 segment container: 93 x 50, semicircle caps (rx = 25).
CAP_W, CAP_H = 93.0, 50.0
CAP_R = CAP_H / 2.0
CAP_FOCUS = (CAP_W - CAP_H) / 2.0  # 21.5

ROOT = (285.0, 217.0)
LEFT = (155.0, 340.0)
RIGHT = (415.0, 340.0)
LEAF = {
    "R1": (90.0, 477.0),
    "R2": (220.0, 477.0),
    "R3": (350.0, 477.0),
    "R4": (480.0, 477.0),
}
EMIT_Y = 100.0
PANEL_OX = (0.0, 565.0, 1130.0)


def X(px: float) -> float:
    return px * W_BP / W_PX


def Y(py: float) -> float:
    return (H_PX - py) * H_BP / H_PX


def hypot(dx: float, dy: float) -> float:
    return math.hypot(dx, dy)


def inside_capsule(px: float, py: float, cx: float, cy: float, pad: float = 0.0) -> bool:
    """Stadium centered on (cx, cy). pad grows the radius."""
    ax, bx = cx - CAP_FOCUS, cx + CAP_FOCUS
    qx = min(max(px, ax), bx)
    return (px - qx) ** 2 + (py - cy) ** 2 <= (CAP_R + pad) ** 2 + 1e-6


def ray_border(cx: float, cy: float, dx: float, dy: float, gap: float = 1.15) -> tuple[float, float]:
    """Point where the ray from the center along (dx, dy) leaves the stadium, plus gap."""
    length = hypot(dx, dy)
    ux, uy = dx / length, dy / length
    if abs(uy) > 1e-9:
        t_flat = CAP_R / abs(uy)
        if abs(t_flat * ux) <= CAP_FOCUS + 1e-6:
            t = t_flat + gap
            return cx + t * ux, cy + t * uy
    cap = CAP_FOCUS if ux >= 0 else -CAP_FOCUS
    # (t*ux - cap)^2 + (t*uy)^2 = CAP_R^2
    b = -2.0 * ux * cap
    c = cap * cap - CAP_R * CAP_R
    disc = max(0.0, b * b - 4.0 * c)
    sd = math.sqrt(disc)
    t = max((-b + sd) / 2.0, (-b - sd) / 2.0) + gap
    return cx + t * ux, cy + t * uy


def outward_normal(ux: float, uy: float, child_is_left: bool) -> tuple[float, float]:
    """Screen-space normal (y down) pointing away from the sibling."""
    left_turn = (uy, -ux)
    right_turn = (-uy, ux)
    if child_is_left:
        return left_turn if left_turn[0] < 0 else right_turn
    return left_turn if left_turn[0] > 0 else right_turn


def pointer_curve(
    parent: tuple[float, float],
    child: tuple[float, float],
    child_is_left: bool,
    offset: float = 24.0,
    bow: float = 4.0,
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]:
    """Arrow from parent border to child border, bowed off the straight tree edge.

    Endpoints stay on the stadium outlines. The shaft leaves the tree edge so
    the two marks do not read as one double stroke.
    """
    dx, dy = child[0] - parent[0], child[1] - parent[1]
    length = hypot(dx, dy)
    ux, uy = dx / length, dy / length
    nx, ny = outward_normal(ux, uy, child_is_left)
    a = (parent[0] + nx * offset, parent[1] + ny * offset)
    b = (child[0] + nx * offset, child[1] + ny * offset)
    start = _line_exit(parent, a, b, toward=1.0)
    end = _line_exit(child, a, b, toward=-1.0)
    mx = (start[0] + end[0]) / 2.0
    my = (start[1] + end[1]) / 2.0
    c1 = (mx - ux * length * 0.08 + nx * bow, my - uy * length * 0.08 + ny * bow)
    c2 = (mx + ux * length * 0.08 + nx * bow, my + uy * length * 0.08 + ny * bow)
    return start, c1, c2, end


def bezier(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    n: int = 36,
) -> list[tuple[float, float]]:
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1.0 - t
        pts.append(
            (
                u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
                u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
            )
        )
    return pts


def _line_exit(
    node: tuple[float, float],
    a: tuple[float, float],
    b: tuple[float, float],
    toward: float,
) -> tuple[float, float]:
    """Border point of the offset line. toward=+1 leaves the node toward b."""
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay

    def at(t: float) -> tuple[float, float]:
        return ax + t * vx, ay + t * vy

    # t of the node's center projected onto the line, then walk out.
    # Sample. The offset is smaller than the radius, so the line cuts the stadium.
    hits: list[float] = []
    steps = 1200
    prev = None
    prev_t = None
    for i in range(steps + 1):
        t = -0.25 + 1.5 * i / steps
        ins = inside_capsule(*at(t), *node, pad=0.0)
        if prev is not None and ins != prev and prev_t is not None:
            # binary refine
            lo, hi = prev_t, t
            for _ in range(18):
                mid = (lo + hi) / 2.0
                if inside_capsule(*at(mid), *node) == prev:
                    lo = mid
                else:
                    hi = mid
            hits.append((lo + hi) / 2.0)
        prev, prev_t = ins, t
    if len(hits) < 2:
        raise RuntimeError(f"pointer missed capsule at {node}: hits={hits}")
    # The two hits bracket the interior. Pick the one on the `toward` side
    # of the projected center.
    pcx = ((node[0] - ax) * vx + (node[1] - ay) * vy) / (vx * vx + vy * vy)
    if toward > 0:
        t_hit = max(h for h in hits if h >= pcx - 1e-6)
    else:
        t_hit = min(h for h in hits if h <= pcx + 1e-6)
    # Nudge just outside along the line, away from the interior.
    step = 1.3 / hypot(vx, vy)
    t_hit += step if toward > 0 else -step
    return at(t_hit)


def samples(p: tuple[float, float], q: tuple[float, float], n: int = 40) -> list[tuple[float, float]]:
    return [
        (p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n)
        for i in range(n + 1)
    ]


def fmt(v: float) -> str:
    return f"{v:.3f}"


def pt(px: float, py: float) -> str:
    return f"({fmt(X(px))},{fmt(Y(py))})"


class Fig:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.problems: list[str] = []

    def add(self, s: str) -> None:
        self.lines.append(s)

    def capsule(self, cx: float, cy: float, style: str) -> None:
        x0, x1 = cx - CAP_W / 2.0, cx + CAP_W / 2.0
        y0, y1 = cy - CAP_H / 2.0, cy + CAP_H / 2.0
        self.add(
            f"  \\draw[{style}] {pt(x0, y1)} rectangle {pt(x1, y0)};"
        )

    def pair(self, cx: float, cy: float, nums: tuple[int, int] | None, text: str) -> None:
        if nums is None:
            self.add(
                f"  \\node[{text}] at {pt(cx, cy)} {{$\\varnothing$}};"
            )
            return
        for dx, n in ((-CAP_FOCUS, nums[0]), (CAP_FOCUS, nums[1])):
            self.add(f"  \\node[{text}] at {pt(cx + dx, cy)} {{{n}}};")

    def edge(self, a: tuple[float, float], b: tuple[float, float], style: str, nodes: list[tuple[float, float]]) -> None:
        p = ray_border(*a, b[0] - a[0], b[1] - a[1])
        q = ray_border(*b, a[0] - b[0], a[1] - b[1])
        self._assert_clear(p, q, a, b, nodes, kind="tree")
        self.add(f"  \\draw[{style}] {pt(*p)} -- {pt(*q)};")

    def pointer(
        self,
        parent: tuple[float, float],
        child: tuple[float, float],
        child_is_left: bool,
        nodes: list[tuple[float, float]],
    ) -> None:
        start, c1, c2, end = pointer_curve(parent, child, child_is_left)
        curve = bezier(start, c1, c2, end)
        for s in curve[2:-2]:
            for n in nodes:
                if inside_capsule(*s, *n, pad=-0.3):
                    self.problems.append(
                        f"pointer {parent}->{child} enters {n} at ({s[0]:.1f},{s[1]:.1f})"
                    )
                    return
        self.add(
            f"  \\draw[ptr] {pt(*start)} .. controls {pt(*c1)} and {pt(*c2)} .. {pt(*end)};"
        )

    def _assert_clear(self, p, q, a, b, nodes, kind: str) -> None:
        for s in samples(p, q, 48)[1:-1]:
            for n in nodes:
                if inside_capsule(*s, *n, pad=-0.4):
                    self.problems.append(
                        f"{kind} {a}->{b} enters capsule {n} at ({s[0]:.1f},{s[1]:.1f})"
                    )
                    return


def call_polygon() -> list[tuple[float, float]]:
    """One outline around the root loser, the left loser, and loaded R2.

    The corridor is wide on purpose. A tight notch around each pill reads as
    three calls. The bottom stays above the R2 label, and the lower-left
    corner stays to the right of R1.
    """
    return [
        (148.0, 164.0),
        (356.0, 164.0),
        (356.0, 246.0),
        (292.0, 286.0),
        (292.0, 508.0),
        (146.0, 508.0),
        (146.0, 404.0),
        (72.0, 404.0),
        (72.0, 246.0),
        (148.0, 214.0),
    ]


def _seg_dist(p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
    ax, ay = a
    bx, by = b
    px, py = p
    vx, vy = bx - ax, by - ay
    denom = vx * vx + vy * vy
    if denom == 0:
        return hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / denom))
    return hypot(px - (ax + t * vx), py - (ay + t * vy))


def point_in_poly(x: float, y: float, poly: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(poly) - 1
    for i, (xi, yi) in enumerate(poly):
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi
        ):
            inside = not inside
        j = i
    return inside


def main() -> None:
    fig = Fig()
    # The pointer lane must stay off the straight tree edge along its middle.
    pairs = [
        ("root-left", ROOT, LEFT, True),
        ("root-right", ROOT, RIGHT, False),
        ("left-R2", LEFT, LEAF["R2"], False),
        ("left-R1", LEFT, LEAF["R1"], True),
        ("right-R3", RIGHT, LEAF["R3"], True),
        ("right-R4", RIGHT, LEAF["R4"], False),
    ]
    for name, a, b, is_left in pairs:
        edge_a = ray_border(*a, b[0] - a[0], b[1] - a[1], gap=0.0)
        edge_b = ray_border(*b, a[0] - b[0], a[1] - b[1], gap=0.0)
        start, c1, c2, end = pointer_curve(a, b, is_left)
        curve = bezier(start, c1, c2, end, 40)
        mid = curve[8:-8]
        gap = min(_seg_dist(s, edge_a, edge_b) for s in mid)
        if gap < 12.0:
            fig.problems.append(f"pointer {name} lane gap {gap:.1f}px")
        for s in curve[2:-2]:
            for n in (ROOT, LEFT, RIGHT, *LEAF.values(), (ROOT[0], EMIT_Y)):
                if inside_capsule(*s, *n, pad=-0.2):
                    fig.problems.append(f"pointer {name} enters {n}")
                    break

    preamble = r"""
\documentclass[border=0pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{amsmath,amssymb}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning}
\definecolor{ink}{HTML}{262B30}
\definecolor{callred}{HTML}{C44C3C}
\definecolor{emitblue}{HTML}{356D96}
\definecolor{edgequiet}{HTML}{8E979E}
\definecolor{holdstroke}{HTML}{C5CCD2}
\tikzset{
  title/.style={font=\sffamily\bfseries\fontsize{8.7}{10}\selectfont, text=ink, inner sep=0pt, anchor=base},
  digit/.style={font=\sffamily\fontsize{7.5}{8.6}\selectfont, text=ink, inner sep=0pt},
  digitw/.style={font=\sffamily\fontsize{7.5}{8.6}\selectfont, text=white, inner sep=0pt},
  runlab/.style={font=\sffamily\fontsize{7.2}{8.4}\selectfont, text=ink, inner sep=0pt, anchor=base},
  annot/.style={font=\sffamily\fontsize{7.2}{8.4}\selectfont, text=callred, inner sep=0pt},
  pi/.style={font=\sffamily\fontsize{7.2}{8.4}\selectfont, text=emitblue, inner sep=0pt, anchor=west},
  legend/.style={font=\sffamily\fontsize{7.3}{8.6}\selectfont, text=ink, inner sep=0pt, anchor=west},
  stored/.style={draw=ink, line width=0.9pt, fill=white, rounded corners=7.15pt},
  unread/.style={draw=holdstroke, line width=0.8pt, fill=white, rounded corners=7.15pt},
  incall/.style={draw=callred, line width=1.15pt, fill=white, rounded corners=7.15pt},
  emitted/.style={draw=emitblue, line width=0.95pt, fill=emitblue, rounded corners=7.15pt},
  tree/.style={draw=edgequiet, line width=0.75pt, line cap=round},
  pathedge/.style={draw=ink, line width=1.65pt, line cap=round},
  ptr/.style={draw=ink, line width=1.15pt, line cap=round,
              -{Stealth[length=1.45mm,width=1.15mm,inset=0.2pt]}},
  win/.style={draw=emitblue, line width=1.15pt, line cap=round,
              -{Stealth[length=1.45mm,width=1.15mm,inset=0.2pt]}},
  seq/.style={draw=edgequiet, line width=0.8pt, line cap=round,
              -{Stealth[length=1.25mm,width=1.05mm]}},
  lead/.style={draw=callred, line width=0.65pt, line cap=round,
               -{Stealth[length=1.05mm,width=0.8mm,inset=0.15pt]}},
  legsw/.style={line width=0.7pt, rounded corners=1.15pt},
}
\begin{document}
\begin{tikzpicture}[x=1bp,y=1bp]
\useasboundingbox (0,0) rectangle (504.960,187.920);
"""
    fig.add(preamble.strip("\n"))

    # One title line. The reading of each panel is in the caption, not a second line.
    for cx, title in (
        (285.0, "(a) Initialized state"),
        (850.0, "(b) One path refresh"),
        (1415.0, "(c) Updated state"),
    ):
        fig.add(f"  \\node[title] at {pt(cx, 36)} {{{title}}};")

    panels = [
        dict(
            name="a",
            ox=0.0,
            emit=(1, 2),
            root=(3, 4),
            left=(5, 7),
            right=(8, 9),
            leaves=[(12, 16), (6, 14), (11, 15), (10, 13)],
            leaf_style=["unread", "unread", "unread", "unread"],
            node_style={"root": "stored", "left": "stored", "right": "stored"},
            ptrs=[True, False, True],  # child_is_left for root, left-internal, right-internal
            bold=set(),
            winner=True,
            call=False,
            load=False,
        ),
        dict(
            name="b",
            ox=565.0,
            emit=None,
            root=(3, 4),
            left=(5, 7),
            right=(8, 9),
            leaves=[(12, 16), (6, 14), (11, 15), (10, 13)],
            leaf_style=["unread", "incall", "unread", "unread"],
            node_style={"root": "incall", "left": "incall", "right": "stored"},
            ptrs=[True, False, True],
            bold={("root", "left"), ("left", "R2")},
            winner=False,
            call=True,
            load=True,
        ),
        dict(
            name="c",
            ox=1130.0,
            emit=(3, 4),
            root=(5, 6),
            left=(7, 14),
            right=(8, 9),
            leaves=[(12, 16), None, (11, 15), (10, 13)],
            leaf_style=["unread", "unread", "unread", "unread"],
            node_style={"root": "stored", "left": "stored", "right": "stored"},
            ptrs=[False, True, True],
            bold=set(),
            winner=True,
            call=False,
            load=False,
        ),
    ]

    def shift(p, ox):
        return (p[0] + ox, p[1])

    for panel in panels:
        ox = panel["ox"]
        nodes = {
            "root": shift(ROOT, ox),
            "left": shift(LEFT, ox),
            "right": shift(RIGHT, ox),
            "R1": shift(LEAF["R1"], ox),
            "R2": shift(LEAF["R2"], ox),
            "R3": shift(LEAF["R3"], ox),
            "R4": shift(LEAF["R4"], ox),
        }
        links = [
            ("root", "left", ("root", "left")),
            ("root", "right", ("root", "right")),
            ("left", "R1", ("left", "R1")),
            ("left", "R2", ("left", "R2")),
            ("right", "R3", ("right", "R3")),
            ("right", "R4", ("right", "R4")),
        ]
        # Quiet edges first, bold path on top, both under the capsules.
        occupied = list(nodes.values())
        if panel["emit"] is not None:
            occupied.append((nodes["root"][0], EMIT_Y))
        for src, dst, key in links:
            if key in panel["bold"]:
                continue
            fig.edge(nodes[src], nodes[dst], "tree", occupied)
        for src, dst, key in links:
            if key in panel["bold"]:
                fig.edge(nodes[src], nodes[dst], "pathedge", occupied)

        # Capsules and digits before pointers so a tip that kisses the stroke
        # stays visible: pointers are drawn after, and their tips stop outside.
        fig.capsule(*nodes["root"], panel["node_style"]["root"])
        fig.capsule(*nodes["left"], panel["node_style"]["left"])
        fig.capsule(*nodes["right"], panel["node_style"]["right"])
        fig.pair(*nodes["root"], panel["root"], "digit")
        fig.pair(*nodes["left"], panel["left"], "digit")
        fig.pair(*nodes["right"], panel["right"], "digit")
        for key, nums, style in zip(
            ("R1", "R2", "R3", "R4"), panel["leaves"], panel["leaf_style"]
        ):
            fig.capsule(*nodes[key], style)
            fig.pair(*nodes[key], nums, "digit")
            fig.add(
                f"  \\node[runlab] at {pt(nodes[key][0], 548)} {{$R_{key[1]}$}};"
            )

        if panel["emit"] is not None:
            emit_c = (nodes["root"][0], EMIT_Y)
            fig.capsule(*emit_c, "emitted")
            fig.pair(*emit_c, panel["emit"], "digitw")
            # The arrow does not leave the loser box. It is the separate winner exit.
            # A gap remains between the tail and the stored-loser capsule.
            start = (nodes["root"][0], ROOT[1] - CAP_H / 2.0 - 16.0)
            end = (nodes["root"][0], EMIT_Y + CAP_H / 2.0 + 1.2)
            fig.add(f"  \\draw[win] {pt(*start)} -- {pt(*end)};")
            fig.add(
                f"  \\node[pi] at {pt(nodes['root'][0] + 12, 156)} {{winner exit}};"
            )

        # Pointers: root, then the left internal, then the right internal.
        specs = [
            ("root", "left" if panel["ptrs"][0] else "right", panel["ptrs"][0]),
            ("left", "R1" if panel["ptrs"][1] else "R2", panel["ptrs"][1]),
            ("right", "R3" if panel["ptrs"][2] else "R4", panel["ptrs"][2]),
        ]
        for src, dst, is_left in specs:
            fig.pointer(nodes[src], nodes[dst], is_left, occupied)

        if panel["call"]:
            # No second enclosure. Red borders mark the three segments.
            # One leader ties the input row to the root segment.
            fig.add(
                f"  \\node[annot, anchor=west] (callin) at {pt(ox + 8, 100)} {{call 1 input}};"
            )
            chips = [3, 4, 5, 6, 7, 14]
            for i, n in enumerate(chips):
                cx = ox + 168.0 + i * 46.0
                fig.add(f"  \\draw[incall] {pt(cx, 100)} circle (5.70bp);")
                fig.add(f"  \\node[digit] at {pt(cx, 100)} {{{n}}};")
            fig.add(
                f"  \\draw[lead] {pt(ox + 78, 116)} -- {pt(nodes['root'][0], ROOT[1] - CAP_H / 2.0 - 2.0)};"
            )

    # Gutter sequence arrows. Endpoints sit in the empty gap between trees.
    for x0 in (534.0, 1099.0):
        y = 300.0
        fig.add(f"  \\draw[seq] {pt(x0, y)} -- {pt(x0 + 32, y)};")

    # Legend, one baseline, dark, same size as the digits' neighbors.
    # Placed from the left with positioning so items cannot overlap.
    leg_y = Y(618)
    fig.add(f"  \\node[legend] (L0) at (6bp,{fmt(leg_y)}) {{$k{{=}}4$, $h{{=}}2$}};")
    fig.add(
        r"  \draw[legsw, draw=callred, fill=white] ([xshift=6pt,yshift=-2.6pt]L0.east) rectangle ++(9pt,5.2pt);"
    )
    fig.add(
        r"  \node[legend, anchor=west] (L1) at ([xshift=17pt]L0.east) {call 1};"
    )
    fig.add(
        r"  \draw[tree] ([xshift=7pt,yshift=0.4pt]L1.east) -- ++(11pt,0);"
    )
    fig.add(
        r"  \node[legend, anchor=west] (L2) at ([xshift=20pt]L1.east) {tree edge};"
    )
    fig.add(
        r"  \draw[pathedge] ([xshift=7pt,yshift=0.4pt]L2.east) -- ++(11pt,0);"
    )
    fig.add(
        r"  \node[legend, anchor=west] (L3) at ([xshift=20pt]L2.east) {refresh path};"
    )
    fig.add(
        r"  \draw[ptr] ([xshift=7pt,yshift=0.4pt]L3.east) -- ++(11pt,0);"
    )
    fig.add(
        r"  \node[legend, anchor=west] (L4) at ([xshift=20pt]L3.east) {pointer};"
    )
    fig.add(
        r"  \draw[win] ([xshift=7pt,yshift=0.4pt]L4.east) -- ++(11pt,0);"
    )
    fig.add(
        r"  \node[legend, anchor=west] (L5) at ([xshift=20pt]L4.east) {winner exit};"
    )
    fig.add(
        r"  \draw[legsw, draw=emitblue, fill=emitblue] ([xshift=6pt,yshift=-2.6pt]L5.east) rectangle ++(9pt,5.2pt);"
    )
    fig.add(
        r"  \node[legend, anchor=west] (L6) at ([xshift=17pt]L5.east) {emitted};"
    )
    fig.add(
        r"  \draw[legsw, draw=ink, fill=white] ([xshift=6pt,yshift=-2.6pt]L6.east) rectangle ++(9pt,5.2pt);"
    )
    fig.add(
        r"  \node[legend, anchor=west] (L7) at ([xshift=17pt]L6.east) {stored loser};"
    )
    fig.add(
        r"  \draw[legsw, draw=holdstroke, fill=white] ([xshift=6pt,yshift=-2.6pt]L7.east) rectangle ++(9pt,5.2pt);"
    )
    fig.add(
        r"  \node[legend, anchor=west] (L8) at ([xshift=17pt]L7.east) {unread};"
    )

    fig.add(r"\end{tikzpicture}")
    fig.add(r"\end{document}")

    if fig.problems:
        raise SystemExit("geometry check failed:\n" + "\n".join(fig.problems))

    OUT.write_text("\n".join(fig.lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
