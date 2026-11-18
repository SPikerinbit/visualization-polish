#!/usr/bin/env python3
"""Column-width SW, unified LT(h), and pointer figures.

The viewBox unit is 1 bp. Rendered at width 240 bp (pointer 240 bp),
so a font-size of 6.5 is 6.5 bp on the page. Same states, numbers,
and topology as the user v2 vectors; whitespace and type are refit
so the column page is readable.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent
INK = "#2A3034"
PAPER = "#FBF6EC"
BLUE = "#3E7A9A"
RED = "#C56A55"
GRAY = "#9A9086"
PALE = "#D5CBBC"
PTXT = "#6E675C"
STROKE = "#C9C0B2"
TREE = "#B7AFA3"
WHITE = "#FFFFFF"

FONT = "Liberation Sans, Arial, Helvetica, sans-serif"


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


class Svg:
    def __init__(self, w, h, title, desc):
        self.w, self.h = w, h
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img">',
            f"<title>{esc(title)}</title>",
            f"<desc>{esc(desc)}</desc>",
            "<defs>",
            '<marker id="dk" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            f'<path d="M1 1.4 L8.5 5 L1 8.6 Z" fill="{INK}"/></marker>',
            '<marker id="gy" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M1 1.6 L8.2 5 L1 8.4 Z" fill="{TREE}"/></marker>',
            '<marker id="rd" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M1 1.6 L8.2 5 L1 8.4 Z" fill="{RED}"/></marker>',
            "</defs>",
            f'<rect width="100%" height="100%" fill="{PAPER}"/>',
            f'<g font-family="{FONT}" fill="{INK}">',
        ]

    def text(self, x, y, s, size=6.5, anchor="middle", fill=INK, weight="400"):
        self.parts.append(
            f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" font-size="{size}" '
            f'fill="{fill}" font-weight="{weight}">{esc(s)}</text>'
        )

    def line(self, x1, y1, x2, y2, stroke=TREE, sw=0.7, dash=None, marker=None):
        extra = ""
        if dash:
            extra += f' stroke-dasharray="{dash}"'
        if marker:
            extra += f' marker-end="url(#{marker})"'
        self.parts.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{stroke}" stroke-width="{sw}" fill="none"{extra}/>'
        )

    def circ(self, cx, cy, r, fill, stroke=None, sw=0.7):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ' stroke="none"'
        self.parts.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r}" fill="{fill}"{st}/>')

    def rect(self, x, y, w, h, rx, fill, stroke, sw=0.7, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>'
        )

    def path(self, d, stroke, sw=0.8, fill="none", dash=None, marker=None):
        extra = ""
        if dash:
            extra += f' stroke-dasharray="{dash}"'
        if marker:
            extra += f' marker-end="url(#{marker})"'
        self.parts.append(
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linejoin="round" stroke-linecap="round"{extra}/>'
        )

    def finish(self, name):
        self.parts.append("</g></svg>\n")
        path = OUT / name
        path.write_text("".join(self.parts))
        return path


def chip(svg, cx, cy, text, kind, r=4.3, fs=6.5):
    """kind: emit, keep, head, pale."""
    if kind == "emit":
        svg.circ(cx, cy, r, BLUE)
        svg.text(cx, cy + fs * 0.35, text, fs, fill=WHITE)
    elif kind == "keep":
        svg.circ(cx, cy, r, WHITE, STROKE, 0.8)
        svg.text(cx, cy + fs * 0.35, text, fs, fill=PTXT)
    elif kind == "head":
        svg.circ(cx, cy, r, GRAY)
        svg.text(cx, cy + fs * 0.35, text, fs, fill=WHITE)
    else:
        svg.circ(cx, cy, r, PALE)
        svg.text(cx, cy + fs * 0.35, text, fs, fill=PTXT)


def capsule(svg, cx, cy, items, r=4.15, fs=6.5, gap=0.7, pad=0.8):
    """Two-item (or one-item) rounded node. Returns (left, right, top, bot)."""
    n = len(items)
    step = 2 * r + gap
    width = n * step - gap + 2 * pad
    height = 2 * r + 1.6
    x = cx - width / 2
    y = cy - height / 2
    svg.rect(x, y, width, height, height / 2, WHITE, STROKE, 0.7)
    x0 = cx - (n - 1) * step / 2
    for i, (t, k) in enumerate(items):
        chip(svg, x0 + i * step, cy, t, k, r=r, fs=fs)
    return x, x + width, y, y + height


def sw():
    # 8-circle rows set the width. 6.5 bp digits (glyph ~7.2) sit in r=4.5.
    W, H = 240, 96
    svg = Svg(W, H, "Sliding-window merge",
              "Three rounds. Blue is emitted, hollow is retained, gray heads are inside the call, pale is unread.")
    FS = 6.5
    RT = 4.5
    rounds = [
        {
            "title": "Round 1",
            "top": [("1", "emit"), ("2", "emit"), ("3", "emit"), ("4", "emit"), ("5", "emit"),
                    ("7", "keep"), ("8", "keep"), ("9", "keep")],
            "split": 5,
            "runs": [
                ("R₁", [("3", "head"), ("7", "head")], [("12", "pale"), ("16", "pale")]),
                ("R₂", [("1", "head"), ("5", "head")], [("6", "pale"), ("14", "pale")]),
                ("R₃", [("2", "head"), ("8", "head")], [("11", "pale"), ("15", "pale")]),
                ("R₄", [("4", "head"), ("9", "head")], [("10", "pale"), ("13", "pale")]),
            ],
        },
        {
            "title": "Round 2",
            "top": [("6", "emit"), ("7", "emit"), ("8", "emit"), ("9", "emit"), ("10", "emit"),
                    ("11", "keep"), ("12", "keep"), ("14", "keep")],
            "split": 5,
            "runs": [
                ("R₁", [("7", "keep"), ("12", "head")], [("16", "pale")]),
                ("R₂", [("6", "head"), ("14", "head")], []),
                ("R₃", [("8", "keep"), ("11", "head")], [("15", "pale")]),
                ("R₄", [("9", "keep"), ("10", "head")], [("13", "pale")]),
            ],
        },
        {
            "title": "Round 3",
            "top": [("11", "emit"), ("12", "emit"), ("13", "emit"), ("14", "emit"),
                    ("15", "emit"), ("16", "emit")],
            "split": None,
            "runs": [
                ("R₁", [("12", "keep"), ("16", "head")], []),
                ("R₂", [("14", "keep")], []),
                ("R₃", [("11", "keep"), ("15", "head")], []),
                ("R₄", [("13", "head")], []),
            ],
        },
    ]
    step = 2 * RT + 1.05
    widths = []
    for rd in rounds:
        widths.append((len(rd["top"]) - 1) * step + 2 * RT)
    gap = (W - 4 - sum(widths)) / 2
    xs = []
    x = 2
    for w in widths:
        xs.append(x)
        x += w + gap

    top_y = 16
    dot_y = 30
    run_y = 46
    unread_y = 64
    boxes = []
    for i, rd in enumerate(rounds):
        x0 = xs[i]
        w = widths[i]
        cx = x0 + w / 2
        svg.text(cx, 7.2, rd["title"], 7, weight="600")
        centers = []
        for j, (t, k) in enumerate(rd["top"]):
            c = x0 + RT + j * step
            centers.append(c)
            chip(svg, c, top_y, t, k, r=RT, fs=FS)
        if rd["split"] is not None:
            s = rd["split"]
            cut = (centers[s - 1] + centers[s]) / 2
            svg.line(cut, top_y - RT - 1.2, cut, top_y + RT + 1.2, INK, 0.6, dash="0.7 0.7")
        # merge dot and upward arrow
        svg.line(cx, dot_y - 3.2, cx, top_y + RT + 0.4, TREE, 0.75, marker="gy")
        svg.circ(cx, dot_y, 1.15, TREE)
        run_cs = []
        span = w - 2
        for j in range(4):
            run_cs.append(x0 + span * (j + 0.5) / 4)
        for rcx in run_cs:
            svg.line(cx, dot_y, rcx, run_y - 6.2, TREE, 0.7)
        caps = []
        for (lab, heads, unread), rcx in zip(rd["runs"], run_cs):
            svg.text(rcx, run_y - 7.4, lab, 6.5, fill=INK)
            if len(heads) == 1:
                chip(svg, rcx, run_y, heads[0][0], heads[0][1], r=4.15, fs=FS)
                caps.append((rcx - 5.2, rcx + 5.2, run_y - 5.3, run_y + 5.3))
            else:
                caps.append(capsule(svg, rcx, run_y, heads, r=4.15, fs=FS, gap=0.55)[:4])
            if not unread:
                svg.text(rcx, unread_y + 1.6, "∅", 7, fill=PTXT)
            else:
                ustep = 8.2
                u0 = rcx - (len(unread) - 1) * ustep / 2
                for k, (t, kind) in enumerate(unread):
                    chip(svg, u0 + k * ustep, unread_y, t, kind, r=3.7, fs=6.5)
        left = min(c[0] for c in caps) - 1.2
        right = max(c[1] for c in caps) + 1.2
        top = min(c[2] for c in caps) - 1.0
        bot = max(c[3] for c in caps) + 1.0
        svg.rect(left, top, right - left, bot - top, 2.2, "none", RED, 0.9, dash="2.2 1.3")
        boxes.append((left, top, right, bot, centers, rd))

    # retained heads of one round feed the next call
    for i in range(2):
        _, top, right, bot, centers, rd = boxes[i]
        nleft, ntop, nright, nbot, _, _ = boxes[i + 1]
        x1 = centers[rd["split"]] - RT
        y1 = top_y + RT + 0.6
        x2 = nleft - 0.4
        y2 = (ntop + nbot) / 2
        svg.path(
            f"M {x1:.2f} {y1:.2f} C {x1+8:.2f} {y1:.2f}, {x2+2:.2f} {y2-8:.2f}, {x2:.2f} {y2:.2f}",
            TREE, 0.75, marker="gy",
        )

    # legend
    ly = 90
    svg.rect(36, ly - 3.2, 12, 6.2, 1.4, "none", RED, 0.9, dash="2.2 1.3")
    svg.text(52, ly + 1.5, "call", 6.5, anchor="start")
    chip(svg, 86, ly, "5", "emit", r=3.6, fs=6.5)
    svg.text(92, ly + 1.5, "emitted", 6.5, anchor="start")
    chip(svg, 138, ly, "7", "keep", r=3.6, fs=6.5)
    svg.text(144, ly + 1.5, "retained", 6.5, anchor="start")
    svg.finish("sd_merge.svg")


def lt():
    W, H = 240, 124
    svg = Svg(W, H, "Unified LT(h)",
              "h=2 loser tree. (a) initialized, (b) one path refresh, (c) updated. Right subtree pointer stays on R4.")
    # three panels, leaf capsules drive the width
    # r=4.15, two circles, capsule ~18.2; four leaves + gaps ~76
    panels_x = [0.5, 80.5, 160.5]
    PW = 78.5
    titles = ["(a) Initialized state", "(b) One path refresh", "(c) Updated state"]
    FS = 6.5
    R = 4.0
    CAP = 17.5  # two 6.5 bp digits plus a gap the call outline can sit in

    def leaf_centers(x0):
        gap = (PW - 4 * CAP) / 3
        return [x0 + CAP / 2 + i * (CAP + gap) for i in range(4)], CAP

    def node_pair(cx, cy, items):
        return capsule(svg, cx, cy, items, r=R, fs=FS, gap=0.4, pad=0.55)

    def tree(x0, emit, root, left, right, leaves, ptr, rho=None, call=False):
        """ptr is a set of edges: 'root-left','root-right','left-0','left-1','right-0','right-1'."""
        cs, cap = leaf_centers(x0)
        ly = 96
        my = 74
        ry = 52
        ey = 28
        if rho is not None:
            svg.text(x0 + 8, ey + 1.5, "ρ", 6.5, fill=PTXT)
            for i, (t, k) in enumerate(rho):
                chip(svg, x0 + 16 + i * 9.2, ey, t, k, r=3.9, fs=6.5)
        elif emit is not None:
            node_pair((cs[0] + cs[3]) / 2, ey, emit)
            svg.line((cs[0] + cs[3]) / 2, ry - 6.2, (cs[0] + cs[3]) / 2, ey + 6.0, TREE, 0.7, marker="gy")
        lcx = (cs[0] + cs[1]) / 2
        rcx = (cs[2] + cs[3]) / 2
        rootx = (lcx + rcx) / 2
        node_pair(rootx, ry, root)
        node_pair(lcx, my, left)
        node_pair(rcx, my, right)
        # edges
        edges = {
            "root-left": (rootx, ry + 5.6, lcx, my - 5.6),
            "root-right": (rootx, ry + 5.6, rcx, my - 5.6),
            "left-0": (lcx, my + 5.6, cs[0], ly - 5.4),
            "left-1": (lcx, my + 5.6, cs[1], ly - 5.4),
            "right-0": (rcx, my + 5.6, cs[2], ly - 5.4),
            "right-1": (rcx, my + 5.6, cs[3], ly - 5.4),
        }
        for name, (x1, y1, x2, y2) in edges.items():
            svg.line(x1, y1, x2, y2, TREE, 0.65)
        for name in ptr:
            x1, y1, x2, y2 = edges[name]
            # stop short of the node so the head sits on the edge
            svg.line(x1, y1 + 0.4, x2, y2 - 0.2, INK, 1.15, marker="dk")
        labs = ["R₁", "R₂", "R₃", "R₄"]
        for c, lab, items in zip(cs, labs, leaves):
            if not items:
                svg.circ(c, ly, R, WHITE, STROKE, 0.7)
                svg.text(c, ly + 2.2, "∅", 7, fill=PTXT)
            elif len(items) == 1:
                chip(svg, c, ly, items[0][0], items[0][1], r=R, fs=FS)
            else:
                node_pair(c, ly, items)
            svg.text(c, ly + 9.2, lab, 6.5)
        if call:
            # Just outside each refreshed capsule, and only around R2 at the leaves.
            a = CAP / 2 + 0.7
            b = R + 1.5
            c = cs[1]
            jog = ly - (CAP / 2) - 2.2
            pts = [
                (rootx - a, ry - b), (rootx + a, ry - b), (rootx + a, ry + b),
                (lcx + a, my - b), (lcx + a, my + b), (c + a, jog),
                (c + a, ly + b), (c - a, ly + b), (c - a, jog),
                (lcx - a, my + b), (lcx - a, my - b), (rootx - a, ry + b),
            ]
            d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f} "
            for x, y in pts[1:]:
                d += f"L {x:.1f} {y:.1f} "
            d += "Z"
            svg.path(d, RED, 0.85, dash="2.1 1.2")
        return cs

    for x0, title in zip(panels_x, titles):
        svg.text(x0 + PW / 2, 8, title, 6.5, weight="600")

    pale = lambda a, b: [(a, "pale"), (b, "pale")]
    head = lambda a, b: [(a, "head"), (b, "head")]
    tree(panels_x[0],
         emit=[("1", "emit"), ("2", "emit")],
         root=head("3", "4"), left=head("5", "7"), right=head("8", "9"),
         leaves=[pale("12", "16"), pale("6", "14"), pale("11", "15"), pale("10", "13")],
         ptr={"root-left", "left-1", "right-1"})
    tree(panels_x[1],
         emit=None,
         root=head("3", "4"), left=head("5", "7"), right=pale("8", "9"),
         leaves=[pale("12", "16"), head("6", "14"), pale("11", "15"), pale("10", "13")],
         ptr={"root-left", "left-1", "right-1"},
         rho=[("3", "head"), ("4", "head"), ("5", "head"), ("6", "head"), ("7", "head"), ("14", "head")],
         call=True)
    tree(panels_x[2],
         emit=[("3", "emit"), ("4", "emit")],
         root=head("5", "6"), left=head("7", "14"), right=head("8", "9"),
         leaves=[pale("12", "16"), [], pale("11", "15"), pale("10", "13")],
         ptr={"root-left", "left-0", "right-1"})

    # open arrows between panels, in the gap beside the root band
    for x in (75.5, 155.5):
        svg.line(x, 52, x + 5, 52, PTXT, 0.8, marker="gy")

    ly = 116
    svg.rect(28, ly - 3.1, 11, 6, 1.3, "none", RED, 0.85, dash="2.1 1.2")
    svg.text(42, ly + 1.4, "call", 6.5, anchor="start")
    svg.line(78, ly, 90, ly, INK, 1.15, marker="dk")
    svg.text(94, ly + 1.4, "pointer", 6.5, anchor="start")
    chip(svg, 148, ly, "3", "emit", r=3.5, fs=6.5)
    svg.text(154, ly + 1.4, "emitted", 6.5, anchor="start")
    svg.finish("lt_unified.svg")


def pointer():
    W, H = 240, 150
    svg = Svg(W, H, "Pointer update",
              "Two rows, three columns. Build assigns the pointer to R. Refresh returns it to L. "
              "Winner and loser are color; the red letter is the side that exhausts.")
    FS = 7
    RD = 4.3
    svg.text(40, 8, "State", FS, weight="600")
    svg.text(120, 8, "Node replay", FS, weight="600")
    svg.text(196, 8, "Updated state", FS, weight="600")

    def state(cx, y, parent, left, right, ptr_to, emit=None):
        """Small tree. y is the parent-capsule center. cx is the parent x."""
        px, lx, rx = cx, cx - 16, cx + 16
        cy = y + 22
        if emit is not None:
            capsule(svg, px, y - 16, emit, r=RD, fs=6.5, gap=0.55)
            svg.line(px, y - 10.2, px, y - 5.6, TREE, 0.7, marker="gy")
        else:
            svg.text(px, y - 12, "P", 6.5)
        if parent is None:
            svg.text(px, y - 9.2, "P", 6.5)
            svg.circ(px, y, 6.2, WHITE, STROKE, 0.7)
            svg.text(px, y + 2.3, "∅", 7, fill=PTXT)
        else:
            if emit is None:
                svg.text(px, y - 8.6, "P", 6.5)
            capsule(svg, px, y, parent, r=RD, fs=6.5, gap=0.5)
        svg.line(px - 3, y + 5.5, lx, cy - 5.6, TREE, 0.65)
        svg.line(px + 3, y + 5.5, rx, cy - 5.6, TREE, 0.65)
        if ptr_to == "R":
            svg.line(px + 3.2, y + 6.2, rx, cy - 6.4, INK, 1.25, marker="dk")
        elif ptr_to == "L":
            svg.line(px - 3.2, y + 6.2, lx, cy - 6.4, INK, 1.25, marker="dk")
        svg.text(lx, cy - 8.2, "L", 6.5)
        svg.text(rx, cy - 8.2, "R", 6.5)
        capsule(svg, lx, cy, left, r=RD, fs=6.5, gap=0.5)
        if right is None:
            svg.circ(rx, cy, 6.2, WHITE, STROKE, 0.7)
            svg.text(rx, cy + 2.3, "∅", 7, fill=PTXT)
        else:
            capsule(svg, rx, cy, right, r=RD, fs=6.5, gap=0.5)

    def replay(cx, y, left_lab, left_items, right_lab, right_items, seq, exhaust):
        """seq: list of (letter, number, kind). exhaust is 'R' or 'L' at the winner/loser cut."""
        capsule(svg, cx - 20, y, left_items, r=RD, fs=6.5, gap=0.5)
        capsule(svg, cx + 22, y, right_items, r=RD, fs=6.5, gap=0.5)
        svg.text(cx - 20, y - 8.4, left_lab, 6.5)
        svg.text(cx + 22, y - 8.4, right_lab, 6.5)
        svg.line(cx, y + 7.2, cx, y + 12.5, TREE, 0.7, marker="gy")
        sy = y + 22
        xs = [cx - 24, cx - 8, cx + 8, cx + 24]
        for x, (let, num, kind) in zip(xs, seq):
            svg.text(x, sy - 6.6, let, 6.5, fill=PTXT)
            chip(svg, x, sy, num, kind, r=RD, fs=6.5)
        # cut between item 1 and item 2 (0-based), the exhaustion point
        cut = (xs[1] + xs[2]) / 2
        svg.line(cut, sy + 5.2, cut, sy + 8.6, RED, 1.15)
        svg.text(cut, sy + 14.2, exhaust, 6.5, fill=RED, weight="600")

    svg.text(3, 18, "(a) Build", 6.5, anchor="start", fill=PTXT)
    state(38, 40, None, [("3", "head"), ("7", "head")], [("1", "head"), ("5", "head")], None)
    replay(120, 36, "L", [("3", "head"), ("7", "head")], "R", [("1", "head"), ("5", "head")],
           [("R", "1", "emit"), ("L", "3", "emit"), ("R", "5", "head"), ("L", "7", "head")], "R")
    state(202, 40, [("5", "head"), ("7", "head")],
          [("12", "pale"), ("16", "pale")], [("6", "pale"), ("14", "pale")],
          "R", emit=[("1", "emit"), ("3", "emit")])

    svg.text(3, 76, "(b) Refresh", 6.5, anchor="start", fill=PTXT)
    state(38, 98, [("5", "head"), ("7", "head")],
          [("12", "pale"), ("16", "pale")], [("6", "head"), ("14", "head")], "R")
    replay(120, 94, "P→L", [("5", "head"), ("7", "head")], "R→R", [("6", "head"), ("14", "head")],
           [("L", "5", "emit"), ("R", "6", "emit"), ("L", "7", "head"), ("R", "14", "head")], "L")
    state(202, 98, [("7", "head"), ("14", "head")],
          [("12", "pale"), ("16", "pale")], None,
          "L", emit=[("5", "emit"), ("6", "emit")])

    # shared legend: color carries winner/loser; red letter is the exhausted side
    ly = 142
    svg.line(4, ly, 16, ly, INK, 1.25, marker="dk")
    svg.text(18, ly + 1.6, "pointer", 6.5, anchor="start")
    chip(svg, 58, ly, "1", "emit", r=3.5, fs=6.5)
    svg.text(63, ly + 1.6, "winner", 6.5, anchor="start")
    chip(svg, 100, ly, "5", "head", r=3.5, fs=6.5)
    svg.text(105, ly + 1.6, "loser", 6.5, anchor="start")
    svg.line(140, ly - 2.2, 140, ly + 2.2, RED, 1.15)
    svg.text(144, ly + 1.6, "R/L exhaust", 6.5, anchor="start", fill=RED)
    chip(svg, 198, ly, "12", "pale", r=3.5, fs=6)
    svg.text(203, ly + 1.6, "unread", 6.5, anchor="start")
    svg.finish("pointer_rule.svg")


if __name__ == "__main__":
    sw()
    lt()
    pointer()
    print("wrote svgs")
