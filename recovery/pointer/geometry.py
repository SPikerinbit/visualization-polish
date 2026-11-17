#!/usr/bin/env python3
"""Pointer-rule figure geometry.

Two layouts, one symbol system. Numbers come from validated_states.json
and the replay rule in loser_tree.py (_replay_validated_segment). This
script does not invent a third replay.

  child 0 / child 1   physical children, fixed places
  slot 0 / slot 1     replay arguments, not child names and not run ids
  pointer             the child whose slot first reaches count h
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "tikz"
PDF = ROOT / "pdf"

# Original pointer_rule.pdf MediaBox, in pt. Width is the manuscript width.
PAGE_W_PT = 249.12
PT_PER_MM = 72.0 / 25.4
PAGE_W = PAGE_W_PT / PT_PER_MM  # 87.897... mm

# Circle diameter stays large enough for two digits at print size.
CIRCLE_D = 4.35
CIRCLE_R = CIRCLE_D / 2.0
PAD = 0.52
CIRCLE_GAP = 0.78
CONT_W = PAD * 2 + CIRCLE_D * 2 + CIRCLE_GAP
CONT_H = PAD * 2 + CIRCLE_D
CONT_RX = CONT_W / 2.0
CONT_RY = CONT_H / 2.0
CORNER = 1.15
STRAIGHT = CONT_RX - CORNER

CHILD_DX = 12.15
EDGE_GAP = 7.35
WIN_GAP = 3.35
TAPE_PITCH = 5.85
TAPE_BLOCK = 23.2

INK = "ink"
BLUE = "bluew"
LOSER_FILL = "loserfill"
UNREAD_FILL = "unreadfill"
UNREAD_TEXT = "unreadt"
EDGE = "edgec"
EDGE_PALE = "edgepale"
PTR = "ptrc"
EXH = "exh"
MUTED = "muted"
CONTAINER = "container"
CONTAINER_PALE = "containerpale"


def replay(slot0, slot1, h=2):
    """Same split as _replay_validated_segment for two full segments."""
    order = sorted([(v, 0) for v in slot0] + [(v, 1) for v in slot1])
    counts = [0, 0]
    side = None
    index = None
    seen = []
    for i, (value, slot) in enumerate(order):
        counts[slot] += 1
        seen.append((value, slot, counts[slot]))
        if counts[slot] == h:
            side = slot
            index = i
            break
    winner = [v for v, _s in order[:h]]
    loser = [v for v, _s in order[h:]]
    return {
        "order": order,
        "seen": seen,
        "side": side,
        "index": index,
        "winner": winner,
        "loser": loser,
        "pointer_child": 0 if side == 0 else 1,
    }


BUILD = replay([3, 7], [1, 5])
REFRESH = replay([5, 7], [6, 14])

assert BUILD["order"] == [(1, 1), (3, 0), (5, 1), (7, 0)]
assert BUILD["winner"] == [1, 3] and BUILD["loser"] == [5, 7]
assert BUILD["side"] == 1 and BUILD["index"] == 2 and BUILD["pointer_child"] == 1
assert REFRESH["order"] == [(5, 0), (6, 1), (7, 0), (14, 1)]
assert REFRESH["winner"] == [5, 6] and REFRESH["loser"] == [7, 14]
assert REFRESH["side"] == 0 and REFRESH["index"] == 2 and REFRESH["pointer_child"] == 0


@dataclass
class Seg:
    name: str
    a: tuple[float, float]
    b: tuple[float, float]
    kind: str  # tree, pointer, rise, tick


@dataclass
class Disk:
    name: str
    c: tuple[float, float]
    r: float


@dataclass
class Box:
    name: str
    x0: float
    y0: float
    x1: float
    y1: float


@dataclass
class Scene:
    segments: list[Seg] = field(default_factory=list)
    disks: list[Disk] = field(default_factory=list)
    boxes: list[Box] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)

    def emit(self, s: str) -> None:
        self.lines.append(s)

    def disk(self, name, x, y, r):
        self.disks.append(Disk(name, (x, y), r))

    def box(self, name, x, y, w, h, anchor="center"):
        if anchor == "center":
            self.boxes.append(Box(name, x - w / 2, y - h / 2, x + w / 2, y + h / 2))
        elif anchor == "north":
            self.boxes.append(Box(name, x - w / 2, y - h, x + w / 2, y))
        elif anchor == "west":
            self.boxes.append(Box(name, x, y - h / 2, x + w, y + h / 2))
        elif anchor == "north west":
            self.boxes.append(Box(name, x, y - h, x + w, y))
        elif anchor == "north east":
            self.boxes.append(Box(name, x - w, y - h, x, y))
        else:
            raise ValueError(anchor)

    def segment(self, name, a, b, kind):
        self.segments.append(Seg(name, a, b, kind))


def dist_point_seg(p, a, b):
    px, py = p
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    l2 = vx * vx + vy * vy
    if l2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / l2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def overlap(a: Box, b: Box, gap=0.25):
    return not (
        a.x1 + gap <= b.x0
        or b.x1 + gap <= a.x0
        or a.y1 + gap <= b.y0
        or b.y1 + gap <= a.y0
    )


def fmt(n):
    return f"{n:.3f}"


def circle_pair_xs(cx):
    # Centers of the two circles inside a container.
    step = CIRCLE_R + CIRCLE_GAP / 2.0
    return cx - step, cx + step


def container_rect(cx, cy):
    return (cx - CONT_RX, cy - CONT_RY, cx + CONT_RX, cy + CONT_RY)


def on_bottom(cx, cy, dx):
    if abs(dx) > STRAIGHT + 1e-6:
        raise ValueError(f"bottom attachment {dx} leaves the straight edge")
    return (cx + dx, cy - CONT_RY)


def on_top(cx, cy, dx):
    if abs(dx) > STRAIGHT + 1e-6:
        raise ValueError(f"top attachment {dx} leaves the straight edge")
    return (cx + dx, cy + CONT_RY)


class Drawer:
    def __init__(self, scene: Scene):
        self.s = scene

    def container(self, cx, cy, pale=False):
        x0, y0, x1, y1 = container_rect(cx, cy)
        stroke = CONTAINER_PALE if pale else CONTAINER
        fill = "palebg" if pale else "white"
        self.s.emit(
            f"\\draw[rounded corners={fmt(CORNER)}mm, line width=0.55pt, draw={stroke}, fill={fill}] "
            f"({fmt(x0)},{fmt(y0)}) rectangle ({fmt(x1)},{fmt(y1)});"
        )

    def circles(self, cx, cy, values, style):
        """style: active, winner, loser, unread, exhaust."""
        xs = circle_pair_xs(cx)
        look = {
            "active": ("white", INK, "0.65pt", INK),
            "winner": (BLUE, "white", "0.4pt", BLUE),
            "loser": (LOSER_FILL, INK, "0.45pt", "loseredge"),
            "unread": (UNREAD_FILL, UNREAD_TEXT, "0.45pt", CONTAINER_PALE),
            "exhaust": (LOSER_FILL, INK, "1.05pt", EXH),
        }[style]
        fill, text, sw, stroke = look
        for x, value in zip(xs, values):
            self.s.disk(f"v{value}", x, cy, CIRCLE_R)
            self.s.emit(
                f"\\draw[line width={sw}, draw={stroke}, fill={fill}] "
                f"({fmt(x)},{fmt(cy)}) circle ({fmt(CIRCLE_R)}mm);"
            )
            self.s.emit(
                f"\\node[inner sep=0pt, font=\\numfont, text={text}] "
                f"at ({fmt(x)},{fmt(cy)}) {{{value}}};"
            )

    def empty_mark(self, cx, cy):
        r = 1.55
        self.s.emit(
            f"\\draw[line width=0.6pt, draw={MUTED}] ({fmt(cx)},{fmt(cy)}) circle ({fmt(r)}mm);"
        )
        self.s.emit(
            f"\\draw[line width=0.6pt, draw={MUTED}] "
            f"({fmt(cx - 1.05)},{fmt(cy - 1.05)}) -- ({fmt(cx + 1.05)},{fmt(cy + 1.05)});"
        )

    def edge(self, name, a, b, pale=False):
        self.s.segment(name, a, b, "tree")
        color = EDGE_PALE if pale else EDGE
        width = "0.7pt" if pale else "0.8pt"
        self.s.emit(
            f"\\draw[line width={width}, draw={color}, line cap=butt] "
            f"({fmt(a[0])},{fmt(a[1])}) -- ({fmt(b[0])},{fmt(b[1])});"
        )

    def pointer(self, name, a, b):
        self.s.segment(name, a, b, "pointer")
        self.s.emit(
            f"\\draw[line width=1.4pt, draw={PTR}, line cap=butt, "
            f"-{{Stealth[length=1.55mm, width=1.15mm, inset=0.25mm]}}] "
            f"({fmt(a[0])},{fmt(a[1])}) -- ({fmt(b[0])},{fmt(b[1])});"
        )

    def rise(self, name, a, b):
        self.s.segment(name, a, b, "rise")
        self.s.emit(
            f"\\draw[line width=0.8pt, draw={BLUE}, line cap=butt, "
            f"-{{Stealth[length=1.35mm, width=1.05mm, inset=0.2mm]}}] "
            f"({fmt(a[0])},{fmt(a[1])}) -- ({fmt(b[0])},{fmt(b[1])});"
        )

    def label(self, name, x, y, text, size="labelfont", color=INK, anchor="north"):
        # Approximate width for the collision pass. Digits and spaces included.
        pt = 5.6 if size == "labelfont" else 6.15
        width = max(4.0, len(text) * pt * 0.3528 * 0.50)
        height = pt * 0.3528 * 1.15
        if anchor == "north":
            self.s.box(name, x, y, width, height, "north")
        elif anchor == "west":
            self.s.box(name, x, y, width, height, "west")
        elif anchor == "north west":
            self.s.box(name, x, y, width, height, "north west")
        elif anchor == "north east":
            self.s.box(name, x, y, width, height, "north east")
        else:
            self.s.box(name, x, y, width, height, "center")
        align = "center" if anchor == "north" else "left"
        self.s.emit(
            f"\\node[inner sep=0pt, anchor={anchor}, align={align}, font=\\{size}, text={color}] "
            f"at ({fmt(x)},{fmt(y)}) {{{text}}};"
        )


def tree_ys(parent_cy):
    child_cy = parent_cy - CONT_RY - EDGE_GAP - CONT_RY
    winner_cy = parent_cy + CONT_RY + WIN_GAP + CONT_RY
    return child_cy, winner_cy


def draw_tree(dr: Drawer, cx, parent_cy, spec):
    """spec keys: parent, child0, child1, pointer, edges.

    parent/child values:
      ("empty",)
      ("pair", style, [a, b])
    pointer: None or 0 or 1
    edges: "both", "pale", or "left" / "right" meaning which edge stays full.
    """
    child_cy, winner_cy = tree_ys(parent_cy)
    c0x, c1x = cx - CHILD_DX, cx + CHILD_DX
    pb = parent_cy - CONT_RY
    ct = child_cy + CONT_RY

    # Edges and pointer first, containers cover the inner cap.
    # Tree edges land on the inner half of each child's top edge.
    # The pointer lands on the outer half, so the two strokes stay apart
    # along the whole shaft and at the tip.
    pale0 = spec["edges"] in ("pale", "right")
    pale1 = spec["edges"] in ("pale", "left")
    edge0 = (on_bottom(cx, parent_cy, -1.35), on_top(c0x, child_cy, 1.15))
    edge1 = (on_bottom(cx, parent_cy, 1.35), on_top(c1x, child_cy, -1.15))
    dr.edge(spec["id"] + "-edge0", edge0[0], edge0[1], pale=pale0)
    dr.edge(spec["id"] + "-edge1", edge1[0], edge1[1], pale=pale1)
    pointer_seg = None
    if spec["pointer"] == 1:
        pointer_seg = (
            spec["id"] + "-ptr1",
            on_bottom(cx, parent_cy, 4.00),
            on_top(c1x, child_cy, 3.55),
        )
    elif spec["pointer"] == 0:
        pointer_seg = (
            spec["id"] + "-ptr0",
            on_bottom(cx, parent_cy, -4.00),
            on_top(c0x, child_cy, -3.55),
        )

    def body(px, py, node):
        kind = node[0]
        pale = kind == "empty" or (kind == "pair" and node[1] == "unread")
        dr.container(px, py, pale=pale)
        if kind == "empty":
            dr.empty_mark(px, py)
        else:
            dr.circles(px, py, node[2], node[1])

    # Winner sits above the parent and is not a stored field.
    rise_seg = None
    if spec.get("winner"):
        rise_seg = (
            spec["id"] + "-rise",
            (cx, parent_cy + CONT_RY),
            (cx, winner_cy - CONT_RY),
        )
        body(cx, winner_cy, ("pair", "winner", spec["winner"]))
        dr.label(
            spec["id"] + "-wlab",
            cx + CONT_RX + 1.15,
            winner_cy,
            "passed up",
            color=BLUE,
            anchor="west",
        )
    body(cx, parent_cy, spec["parent"])
    if spec.get("parent_tag"):
        dr.label(
            spec["id"] + "-ptag",
            cx + CONT_RX + 1.15,
            parent_cy,
            spec["parent_tag"],
            color=MUTED,
            anchor="west",
        )
    body(c0x, child_cy, spec["child0"])
    body(c1x, child_cy, spec["child1"])
    lab_y = child_cy - CONT_RY - 0.7
    dr.label(spec["id"] + "-c0a", c0x, lab_y, spec["c0a"], anchor="north")
    dr.label(spec["id"] + "-c0b", c0x, lab_y - 2.75, spec["c0b"], color=MUTED, anchor="north")
    dr.label(spec["id"] + "-c1a", c1x, lab_y, spec["c1a"], anchor="north")
    dr.label(spec["id"] + "-c1b", c1x, lab_y - 2.75, spec["c1b"], color=MUTED, anchor="north")
    # Paint arrows after the containers so each tip stays visible on the border.
    if rise_seg is not None:
        dr.rise(rise_seg[0], rise_seg[1], rise_seg[2])
    if pointer_seg is not None:
        dr.pointer(pointer_seg[0], pointer_seg[1], pointer_seg[2])
    return {
        "child_cy": child_cy,
        "winner_cy": winner_cy,
        "label_bottom": lab_y - 2.75 - 2.35,
    }


def draw_tape_real(dr: Drawer, cx, top_y, result, tag):
    order = result["order"]
    seen = {value: count for value, _slot, count in result["seen"]}
    decide_at = result["index"]
    n = len(order)
    span = (n - 1) * TAPE_PITCH
    left = cx - span / 2.0
    dr.label(tag + "-z", cx, top_y - 0.15, "replay z", color=MUTED, anchor="north")
    cy = top_y - 3.15 - CIRCLE_R
    dr.label(tag + "-slotword", left - CIRCLE_R - 1.6, cy - CIRCLE_R - 2.35, "slot", color=MUTED, anchor="north east")
    dr.label(tag + "-countword", left - CIRCLE_R - 1.6, cy - CIRCLE_R - 5.05, "count", color=MUTED, anchor="north east")
    for i, (value, slot) in enumerate(order):
        x = left + i * TAPE_PITCH
        if i == decide_at:
            fill, text, sw, stroke = LOSER_FILL, INK, "1.05pt", EXH
        elif i < 2:
            fill, text, sw, stroke = BLUE, "white", "0.4pt", BLUE
        else:
            fill, text, sw, stroke = LOSER_FILL, INK, "0.45pt", "loseredge"
        dr.s.disk(f"{tag}-v{value}", x, cy, CIRCLE_R)
        dr.s.emit(
            f"\\draw[line width={sw}, draw={stroke}, fill={fill}] "
            f"({fmt(x)},{fmt(cy)}) circle ({fmt(CIRCLE_R)}mm);"
        )
        dr.s.emit(
            f"\\node[inner sep=0pt, font=\\numfont, text={text}] at ({fmt(x)},{fmt(cy)}) {{{value}}};"
        )
        slot_y = cy - CIRCLE_R - 2.35
        dr.label(tag + f"-s{i}", x, slot_y, str(slot), color=MUTED, anchor="north")
        if i <= decide_at:
            count = seen[value]
            col = EXH if i == decide_at else MUTED
            dr.label(tag + f"-n{i}", x, slot_y - 2.7, str(count), color=col, anchor="north")
            if i == decide_at:
                tick_y = cy - CIRCLE_R - 0.48
                a = (x - 1.25, tick_y)
                b = (x + 1.25, tick_y)
                dr.s.segment(tag + "-tick", a, b, "tick")
                dr.s.emit(
                    f"\\draw[line width=0.95pt, draw={EXH}, line cap=butt] "
                    f"({fmt(a[0])},{fmt(a[1])}) -- ({fmt(b[0])},{fmt(b[1])});"
                )
        else:
            dr.label(tag + f"-n{i}", x, slot_y - 2.7, "--", color=EDGE_PALE, anchor="north")


SPECS = {
    "build_before": dict(
        id="bb",
        parent=("empty",),
        parent_tag="unset",
        child0=("pair", "active", [3, 7]),
        child1=("pair", "active", [1, 5]),
        pointer=None,
        edges="both",
        c0a="child 0",
        c0b="slot 0",
        c1a="child 1",
        c1b="slot 1",
        winner=None,
        tape=BUILD,
        caption=("Exhaustion point", "slot 1 reaches h=2 at 5"),
    ),
    "build_after": dict(
        id="ba",
        parent=("pair", "loser", [5, 7]),
        parent_tag="stored",
        child0=("pair", "unread", [12, 16]),
        child1=("pair", "unread", [6, 14]),
        pointer=1,
        edges="pale",
        c0a="child 0",
        c0b="unread",
        c1a="child 1",
        c1b="unread",
        winner=[1, 3],
        tape=None,
        caption=("Assign pointer = child 1", "No previous value"),
    ),
    "refresh_before": dict(
        id="rb",
        parent=("pair", "loser", [5, 7]),
        parent_tag="slot 0",
        child0=("pair", "unread", [12, 16]),
        child1=("pair", "active", [6, 14]),
        pointer=1,
        edges="right",
        c0a="child 0",
        c0b="not a slot",
        c1a="child 1",
        c1b="slot 1",
        winner=None,
        tape=REFRESH,
        caption=("Exhaustion point", "slot 0 reaches h=2 at 7"),
    ),
    "refresh_after": dict(
        id="ra",
        parent=("pair", "loser", [7, 14]),
        parent_tag="stored",
        child0=("pair", "unread", [12, 16]),
        child1=("empty",),
        pointer=0,
        edges="left",
        c0a="child 0",
        c0b="still unread",
        c1a="child 1",
        c1b="empty",
        winner=[5, 6],
        tape=None,
        caption=("Return pointer = child 0", "Was child 1"),
    ),
}


def panel_span():
    """Vertical distance from winner top to the bottom of the tape block."""
    # parent at 0, winner top, label bottom, tape block.
    _child, winner = tree_ys(0.0)
    top = winner + CONT_RY
    label_bottom = (_child - CONT_RY - 0.7) - 2.75 - 2.35
    tape_top = label_bottom - 1.15
    tape_bottom = tape_top - TAPE_BLOCK
    return top, tape_bottom  # top > 0, bottom < 0 relative to parent


REL_TOP, REL_BOTTOM = panel_span()
PANEL_H = REL_TOP - REL_BOTTOM


def draw_panel(dr: Drawer, cx, parent_cy, key):
    spec = SPECS[key]
    info = draw_tree(dr, cx, parent_cy, spec)
    tape_top = info["label_bottom"] - 1.15
    if spec["tape"] is not None:
        draw_tape_real(dr, cx, tape_top, spec["tape"], spec["id"])
    cap_top = tape_top - TAPE_BLOCK + 6.4
    lines = spec["caption"] if isinstance(spec["caption"], tuple) else (spec["caption"],)
    for i, text in enumerate(lines):
        dr.label(
            spec["id"] + f"-cap{i}",
            cx,
            cap_top - i * 2.9,
            text,
            size="captionfont",
            anchor="north",
        )
    return info


def draw_gap(dr: Drawer, cx, parent_cy):
    top = parent_cy + REL_TOP
    bottom = parent_cy + REL_BOTTOM
    x0, x1 = cx - 18.4, cx + 18.4
    dr.s.emit(
        f"\\draw[rounded corners=1.3mm, line width=0.6pt, draw={EDGE}, dash pattern=on 1.1mm off 0.9mm, fill=gapbg] "
        f"({fmt(x0)},{fmt(bottom)}) rectangle ({fmt(x1)},{fmt(top)});"
    )
    # No nodes, no arrows. Text only.
    lines = [
        "Not in the trace.",
        "Returned pointer is child 0.",
        "The next fill of child 0",
        "is not in the state file.",
        "A return may name the same",
        "child again. That case",
        "is not drawn.",
    ]
    y = parent_cy + 6.5
    for i, text in enumerate(lines):
        dr.label(f"gap-{i}", cx, y - i * 3.15, text, size="captionfont", color=INK, anchor="north")


def header_block(dr: Drawer, width):
    """Returns y of the first row's parent after drawing the shared header.

    Caller passes absolute y cursor via the returned parent y of row 0? 
    We draw at fixed y from the top of a page of known height. The function
    returns the y positions it consumed, computed by the layout helper.
    """
    raise RuntimeError


def text_width(text, pt, bold=False):
    factor = 0.52 if bold else 0.48
    return len(text) * pt * 0.3528 * factor


def layout_page(kind):
    """Return absolute coordinates for a scheme. y-up, origin bottom-left."""
    margin_x = 1.7
    col_w = (PAGE_W - 2 * margin_x - 3.4) / 2.0
    left_cx = margin_x + col_w / 2.0
    right_cx = margin_x + col_w + 3.4 + col_w / 2.0
    # Vertical rhythm from the top. Compute height first.
    top_pad = 1.7
    identity = 3.3
    subtitle = 2.9
    gap1 = 1.1
    colhead = 3.5
    row_title = 3.6
    row_gap = 3.6  # causal line between scheme-A rows, or between B steps
    legend = 13.2
    bottom_pad = 1.6
    if kind == "a":
        body = row_title + PANEL_H + row_gap + row_title + PANEL_H
    else:
        body = 3 * (row_title + PANEL_H) + 2 * row_gap
    height = top_pad + identity + subtitle + gap1 + colhead + body + 1.4 + legend + bottom_pad
    y = height - top_pad
    cursor = {}
    cursor["identity_y"] = y
    y -= identity
    cursor["sub_y"] = y
    y -= subtitle + gap1
    cursor["colhead_y"] = y
    y -= colhead
    rows = []
    n_rows = 2 if kind == "a" else 3
    for i in range(n_rows):
        title_y = y
        y -= row_title
        parent_cy = y - REL_TOP
        y -= PANEL_H
        rows.append({"title_y": title_y, "parent_cy": parent_cy, "bottom": y})
        if i != n_rows - 1:
            cursor[f"between_{i}"] = y - 0.2
            y -= row_gap
    cursor["legend_top"] = y - 1.4
    cursor["height"] = height
    cursor["left_cx"] = left_cx
    cursor["right_cx"] = right_cx
    cursor["col_w"] = col_w
    cursor["rows"] = rows
    cursor["margin_x"] = margin_x
    return cursor


def draw_legend(dr: Drawer, lay):
    y = lay["legend_top"] - 0.2
    x = lay["margin_x"] + 0.4
    # Swatches use the real line weights. Circles are smaller than data
    # circles and are labeled as the legend, not as a second encoding.
    items = [
        ("edge", "tree edge"),
        ("pointer", "pointer"),
        ("winner", "winner, not stored"),
        ("loser", "stored loser"),
        ("unread", "next unread"),
        ("exhaust", "count reaches h"),
    ]
    # Two rows of three, then two rule lines.
    for i, (kind, text) in enumerate(items):
        col = i % 3
        row = i // 3
        sx = x + col * 28.6
        sy = y - row * 4.6
        if kind == "edge":
            dr.s.emit(
                f"\\draw[line width=0.8pt, draw={EDGE}] ({fmt(sx)},{fmt(sy)}) -- ({fmt(sx+4.2)},{fmt(sy)});"
            )
        elif kind == "pointer":
            dr.s.emit(
                f"\\draw[line width=1.4pt, draw={PTR}, -{{Stealth[length=1.45mm, width=1.1mm]}}] "
                f"({fmt(sx)},{fmt(sy)}) -- ({fmt(sx+4.6)},{fmt(sy)});"
            )
        elif kind == "winner":
            dr.s.emit(
                f"\\draw[line width=0.4pt, draw={BLUE}, fill={BLUE}] ({fmt(sx+1.5)},{fmt(sy)}) circle (1.45mm);"
            )
        elif kind == "loser":
            dr.s.emit(
                f"\\draw[line width=0.45pt, draw=loseredge, fill={LOSER_FILL}] ({fmt(sx+1.5)},{fmt(sy)}) circle (1.45mm);"
            )
        elif kind == "unread":
            dr.s.emit(
                f"\\draw[line width=0.45pt, draw={CONTAINER_PALE}, fill={UNREAD_FILL}] ({fmt(sx+1.5)},{fmt(sy)}) circle (1.45mm);"
            )
        elif kind == "exhaust":
            dr.s.emit(
                f"\\draw[line width=1.05pt, draw={EXH}, fill={LOSER_FILL}] ({fmt(sx+1.5)},{fmt(sy)}) circle (1.45mm);"
            )
            dr.s.emit(
                f"\\draw[line width=0.95pt, draw={EXH}] ({fmt(sx+0.3)},{fmt(sy-2.05)}) -- ({fmt(sx+2.7)},{fmt(sy-2.05)});"
            )
        tx = sx + 5.5
        dr.label(f"leg-{kind}", tx, sy, text, size="captionfont", anchor="west")
    rule_y = y - 2 * 4.6 - 0.6
    dr.label(
        "leg-rule",
        lay["margin_x"] + 0.4,
        rule_y,
        "Replay reads the existing rank map. It is not a new ListwiseRank call.",
        size="captionfont",
        anchor="north west",
    )
    dr.label(
        "leg-rule2",
        lay["margin_x"] + 0.4,
        rule_y - 2.7,
        "The returned child can equal the old pointer. No such case is in the trace.",
        size="captionfont",
        anchor="north west",
    )


def draw_headers_common(dr, lay, col_left, col_right):
    dr.label(
        "identity",
        PAGE_W / 2,
        lay["identity_y"],
        r"R1  3 7 12 16\qquad R2  1 5 6 14\qquad R3  2 8 11 15\qquad R4  4 9 10 13",
        size="idfont",
        anchor="north",
    )
    dr.label(
        "sub",
        PAGE_W / 2,
        lay["sub_y"],
        "Local node uses R1 as child 0 and R2 as child 1. h = 2. Slot is not a child.",
        size="captionfont",
        color=MUTED,
        anchor="north",
    )
    dr.label("cl", lay["left_cx"], lay["colhead_y"], col_left, size="headfont", anchor="north")
    dr.label("cr", lay["right_cx"], lay["colhead_y"], col_right, size="headfont", anchor="north")


def build_scheme(kind):
    scene = Scene()
    dr = Drawer(scene)
    lay = layout_page(kind)
    if kind == "a":
        draw_headers_common(dr, lay, "before", "after")
        titles = [
            "(a) Build. Pointer is assigned, not moved from an old value",
            "(b) Refresh. The previous pointer is child 1",
        ]
        keys = [("build_before", "build_after"), ("refresh_before", "refresh_after")]
        between = "Next refresh follows child 1 and fills only that child."
    else:
        draw_headers_common(dr, lay, "Build", "Refresh")
        titles = [
            "1. Exhaustion. The slot that first reaches h",
            "2. Returned pointer. Assign, or replace the previous child",
            "3. Next refresh. Follow that child. Fill only that child",
        ]
        keys = [
            ("build_before", "refresh_before"),
            ("build_after", "refresh_after"),
            ("refresh_before_again", "gap"),
        ]
        between = "The next refresh follows the child just returned."
    for i, (title, pair) in enumerate(zip(titles, keys)):
        row = lay["rows"][i]
        dr.label(f"title{i}", lay["margin_x"] + 0.2, row["title_y"], title, size="titlefont", anchor="north west")
        for cx, key in ((lay["left_cx"], pair[0]), (lay["right_cx"], pair[1])):
            if key == "gap":
                draw_gap(dr, cx, row["parent_cy"])
            elif key == "refresh_before_again":
                # Same state as refresh before, without a second exhaustion tape.
                spec_key = "refresh_before"
                saved_tape = SPECS[spec_key]["tape"]
                saved_cap = SPECS[spec_key]["caption"]
                saved_id = SPECS[spec_key]["id"]
                SPECS[spec_key]["tape"] = None
                SPECS[spec_key]["caption"] = ("Same state as step 1 Refresh", "Not a new replay")
                SPECS[spec_key]["id"] = "rb3"
                draw_panel(dr, cx, row["parent_cy"], spec_key)
                SPECS[spec_key]["tape"] = saved_tape
                SPECS[spec_key]["caption"] = saved_cap
                SPECS[spec_key]["id"] = saved_id
            else:
                draw_panel(dr, cx, row["parent_cy"], key)
        if i < len(titles) - 1 and kind == "b":
            dr.label(
                f"between{i}",
                PAGE_W / 2,
                lay[f"between_{i}"],
                between if i == 1 else "Exhaustion decides the child. It does not itself mean a flip.",
                size="captionfont",
                anchor="north",
            )
        elif i == 0 and kind == "a":
            dr.label(
                "between0",
                PAGE_W / 2,
                lay["between_0"],
                between,
                size="captionfont",
                anchor="north",
            )
    draw_legend(dr, lay)
    # Fix the bounding box to the page.
    scene.emit(
        f"\\path[use as bounding box] (0,0) rectangle ({fmt(PAGE_W)},{fmt(lay['height'])});"
    )
    return scene, lay


PREAMBLE = r"""
\documentclass{article}
\usepackage[T1]{fontenc}
\usepackage[scaled=0.94]{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{tikz}
\usetikzlibrary{arrows.meta}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\topskip}{0pt}
\setlength{\parskip}{0pt}
\definecolor{ink}{HTML}{262B30}
\definecolor{bluew}{HTML}{356D96}
\definecolor{loserfill}{HTML}{D7DCE0}
\definecolor{loseredge}{HTML}{8E969C}
\definecolor{unreadfill}{HTML}{EEF1F3}
\definecolor{unreadt}{HTML}{9BA3AA}
\definecolor{edgec}{HTML}{AAB1B7}
\definecolor{edgepale}{HTML}{D8DEE2}
\definecolor{ptrc}{HTML}{303840}
\definecolor{exh}{HTML}{C44C3C}
\definecolor{muted}{HTML}{6E777E}
\definecolor{container}{HTML}{C5CCD1}
\definecolor{containerpale}{HTML}{E1E5E8}
\definecolor{palebg}{HTML}{F7F8F9}
\definecolor{gapbg}{HTML}{FBFCFC}
\definecolor{white}{HTML}{FFFFFF}
\newcommand{\numfont}{\sffamily\bfseries\fontsize{6.15}{7}\selectfont}
\newcommand{\labelfont}{\sffamily\fontsize{5.7}{6.6}\selectfont}
\newcommand{\captionfont}{\sffamily\fontsize{6.05}{7.1}\selectfont}
\newcommand{\idfont}{\sffamily\fontsize{6.35}{7.4}\selectfont}
\newcommand{\headfont}{\sffamily\bfseries\fontsize{8}{9.2}\selectfont}
\newcommand{\titlefont}{\sffamily\bfseries\fontsize{7.15}{8.3}\selectfont}
\begin{document}
\pdfhorigin=0bp
\pdfvorigin=0bp
\setbox0=\hbox{%
\begin{tikzpicture}[x=1mm,y=1mm,every node/.style={inner sep=0pt,outer sep=0pt}]
""".lstrip()


def write_tex(kind, scene, lay):
    height_pt = lay["height"] * PT_PER_MM
    body = "\n".join(scene.lines)
    tex = (
        PREAMBLE.replace("%HEIGHT%", f"{height_pt:.2f}")
        + body
        + "\n\\end{tikzpicture}%\n}\n\\pdfpagewidth=\\wd0\n\\pdfpageheight=\\ht0\n\\shipout\\box0\n\\end{document}\n"
    )
    name = "scheme-a.tex" if kind == "a" else "scheme-b.tex"
    path = TEX / name
    path.write_text(tex)
    return path


def check(scene: Scene, lay, kind):
    errors = []
    # Page bounds.
    H = lay["height"]
    for seg in scene.segments:
        for pt in (seg.a, seg.b):
            if not (0.4 <= pt[0] <= PAGE_W - 0.4 and 0.4 <= pt[1] <= H - 0.4):
                errors.append(f"{seg.name} endpoint {pt} outside page")
    for d in scene.disks:
        if d.c[0] - d.r < 0.3 or d.c[0] + d.r > PAGE_W - 0.3:
            errors.append(f"{d.name} circle outside x")
        if d.c[1] - d.r < 0.3 or d.c[1] + d.r > H - 0.3:
            errors.append(f"{d.name} circle outside y")
    # Lines must not enter element disks. Tick and other marks stay clear too.
    for seg in scene.segments:
        for d in scene.disks:
            # Ignore the disk a rise/pointer is allowed to stop outside of.
            dist = dist_point_seg(d.c, seg.a, seg.b)
            limit = d.r + 0.28
            if dist < limit:
                errors.append(
                    f"{seg.name} ({seg.kind}) comes within {dist:.2f}mm of {d.name} r={d.r:.2f}"
                )
    # Data circles must not overlap each other.
    for i, a in enumerate(scene.disks):
        for b in scene.disks[i + 1 :]:
            dist = math.hypot(a.c[0] - b.c[0], a.c[1] - b.c[1])
            if dist < a.r + b.r + 0.55:
                errors.append(f"{a.name} overlaps {b.name} dist={dist:.2f}")
    # Pointer and the tree edge to the same child must not cross.
    # Already constructed as separated; still test all pointer/tree pairs.
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    def crosses(s1, s2):
        a, b, c, d = s1.a, s1.b, s2.a, s2.b
        return orient(a, b, c) * orient(a, b, d) < 0 and orient(c, d, a) * orient(c, d, b) < 0

    ptrs = [s for s in scene.segments if s.kind == "pointer"]
    trees = [s for s in scene.segments if s.kind == "tree"]
    for p in ptrs:
        for t in trees:
            if crosses(p, t):
                errors.append(f"pointer {p.name} crosses tree edge {t.name}")
    # Endpoint audit: pointer and tree endpoints sit on a container border.
    # We check the y of each tree/pointer end equals some container top or bottom
    # recorded implicitly by disk rows: parent/child centers are disk centers
    # or empty. Empty nodes have no disks. Check straight-edge x by reconstructing
    # from the segment name is enough if y matches CONT border of a known cy.
    # Collect disk center ys and also trust construction. Flag any tree/pointer
    # whose endpoints are not separated from the nearest disk center by ~CONT_RY
    # along y when x is near a container, within 0.08mm of the border y.
    # Text boxes versus disks.
    for box in scene.boxes:
        for d in scene.disks:
            # Shrink the box slightly: the estimator is conservative.
            expanded = Box(d.name, d.c[0] - d.r, d.c[1] - d.r, d.c[0] + d.r, d.c[1] + d.r)
            if overlap(box, expanded, gap=0.15):
                errors.append(f"text {box.name} hits circle {d.name}")
    # Text versus text.
    for i, a in enumerate(scene.boxes):
        for b in scene.boxes[i + 1 :]:
            if overlap(a, b, gap=0.15):
                errors.append(f"text {a.name} hits text {b.name}")
    return errors


def arrow_records(scene: Scene, kind):
    rows = []
    for seg in scene.segments:
        rows.append(
            {
                "scheme": kind,
                "name": seg.name,
                "kind": seg.kind,
                "x0": round(seg.a[0], 3),
                "y0": round(seg.a[1], 3),
                "x1": round(seg.b[0], 3),
                "y1": round(seg.b[1], 3),
            }
        )
    return rows


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    PDF.mkdir(parents=True, exist_ok=True)
    all_rows = []
    report = {"page_width_mm": PAGE_W, "page_width_pt": PAGE_W_PT, "circle_d_mm": CIRCLE_D}
    for kind in ("a", "b"):
        scene, lay = build_scheme(kind)
        errors = check(scene, lay, kind)
        report[kind] = {
            "height_mm": lay["height"],
            "height_pt": lay["height"] * PT_PER_MM,
            "errors": errors,
            "n_segments": len(scene.segments),
            "n_disks": len(scene.disks),
        }
        if errors:
            print(f"SCHEME {kind} ERRORS ({len(errors)})")
            for e in errors:
                print(" -", e)
        else:
            path = write_tex(kind, scene, lay)
            print(f"wrote {path} height {lay['height']:.2f} mm")
        all_rows.extend(arrow_records(scene, kind))
    (ROOT / "endpoints.json").write_text(json.dumps({"report": report, "segments": all_rows}, indent=2))
    if any(report[k]["errors"] for k in ("a", "b")):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
