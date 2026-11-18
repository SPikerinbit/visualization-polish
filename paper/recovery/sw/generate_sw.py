#!/usr/bin/env python3
"""Sliding-window mechanism figure.

States are produced by walking the paper pseudocode (framework.tex,
Algorithm sliding_window_kway_group_merge): one ListwiseRank per round,
emit through the first window exhaustion that still has an unseen item.
The walk is checked against validated_states.json. It is not a live
ranker run. Listwise order is the numeric identity used by the example.

The wide board is the v1 three-column frame at sigconf textwidth.
The stack board is the same grammar reflowed to 0.95 columnwidth.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent

RUNS = (
    (3, 7, 12, 16),
    (1, 5, 6, 14),
    (2, 8, 11, 15),
    (4, 9, 10, 13),
)
M = 8

# Measured from viz/tex/vendor/acmart.cls, \documentclass[sigconf,review],
# after \maketitle (the class becomes twocolumn there):
#   textwidth   = 506.295pt = 177.96mm
#   columnwidth = 241.14749pt = 84.78mm
#   0.95\linewidth inside figure   = 80.54mm
#   \linewidth inside figure*      = 177.96mm
TEXTWIDTH_MM = 506.295 * 25.4 / 72.27
COLUMN_SLOT_MM = 0.95 * (241.14749 * 25.4 / 72.27)


def walk_rounds():
    """Paper rule: stop when e_t = b_t and the run still has unseen items.

    The completing item is emitted. Runs with no unseen tail do not stop
    the scan, so the last round emits its whole window.
    """
    p = [0, 0, 0, 0]
    rounds = []
    for _ in range(3):
        active = [i for i in range(4) if p[i] < len(RUNS[i])]
        if len(active) <= 1:
            raise SystemExit("example unexpectedly hit the single-run fast path")
        h = M // len(active)
        windows = {}
        unread = {}
        b = {}
        for i in active:
            rest = RUNS[i][p[i] :]
            windows[i] = list(rest[:h])
            b[i] = len(windows[i])
            unread[i] = list(rest[b[i] :])
        ordered = sorted(
            ((value, i) for i in active for value in windows[i]),
            key=lambda item: item[0],
        )
        emitted_pairs = []
        counts = {i: 0 for i in active}
        for value, i in ordered:
            emitted_pairs.append((value, i))
            counts[i] += 1
            if counts[i] == b[i] and p[i] + b[i] < len(RUNS[i]):
                break
        emitted = [value for value, _i in emitted_pairs]
        emitted_set = set(emitted)
        retained = [value for value, _i in ordered if value not in emitted_set]
        rounds.append(
            {
                "positions": list(p),
                "h": h,
                "b": [b[i] for i in range(4)],
                "windows": [list(windows[i]) for i in range(4)],
                "unread": [list(unread[i]) for i in range(4)],
                "candidates": [value for value, _i in ordered],
                "emit": emitted,
                "retained": retained,
                "priorRetained": list(rounds[-1]["retained"]) if rounds else [],
                "batch_assembly": [v for i in range(4) for v in windows[i]],
            }
        )
        for i in active:
            p[i] += counts[i]
    return rounds


EXPECTED = {
    "positions": [[0, 0, 0, 0], [1, 2, 1, 1], [2, 3, 2, 3]],
    "windows": [
        [[3, 7], [1, 5], [2, 8], [4, 9]],
        [[7, 12], [6, 14], [8, 11], [9, 10]],
        [[12, 16], [14], [11, 15], [13]],
    ],
    "emit": [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15, 16]],
    "retained": [[7, 8, 9], [11, 12, 14], []],
    "unread": [
        [[12, 16], [6, 14], [11, 15], [10, 13]],
        [[16], [], [15], [13]],
        [[], [], [], []],
    ],
    "candidates": [
        [1, 2, 3, 4, 5, 7, 8, 9],
        [6, 7, 8, 9, 10, 11, 12, 14],
        [11, 12, 13, 14, 15, 16],
    ],
    "batch": [
        [3, 7, 1, 5, 2, 8, 4, 9],
        [7, 12, 6, 14, 8, 11, 9, 10],
        [12, 16, 14, 11, 15, 13],
    ],
}


def check_rounds(rounds):
    for i, rnd in enumerate(rounds):
        assert rnd["positions"] == EXPECTED["positions"][i], rnd
        assert rnd["windows"] == EXPECTED["windows"][i], rnd["windows"]
        assert rnd["emit"] == EXPECTED["emit"][i]
        assert rnd["retained"] == EXPECTED["retained"][i]
        assert rnd["unread"] == EXPECTED["unread"][i]
        assert rnd["candidates"] == EXPECTED["candidates"][i]
        assert rnd["batch_assembly"] == EXPECTED["batch"][i]
        assert sum(rnd["b"]) == len(rnd["candidates"])
        assert rnd["h"] == 2
    assert [len(r["emit"]) for r in rounds] == [5, 5, 6]
    # Every retained id re-enters the next window, and no emitted id does.
    for i in range(2):
        nxt = {v for w in rounds[i + 1]["windows"] for v in w}
        for value in rounds[i]["retained"]:
            assert value in nxt
        for value in rounds[i]["emit"]:
            assert value not in nxt
    flat = [v for run in RUNS for v in run]
    assert sorted(flat) == list(range(1, 17))


# ---------------------------------------------------------------------------
# Geometry


@dataclass
class Circle:
    x: float
    y: float  # y increases upward
    r: float
    value: int
    kind: str  # emitted, retained, new, unread
    run: int
    slot: int
    rnd: int

    def dist(self, x, y):
        return math.hypot(self.x - x, self.y - y)


@dataclass
class Rect:
    x0: float
    y0: float
    x1: float
    y1: float
    rnd: int
    run: int

    def contains(self, x, y, eps=0.0):
        return self.x0 - eps <= x <= self.x1 + eps and self.y0 - eps <= y <= self.y1 + eps

    def inset_of_boundary(self, x, y):
        """Negative if outside. Distance outside the rectangle, signed."""
        dx = max(self.x0 - x, 0.0, x - self.x1)
        dy = max(self.y0 - y, 0.0, y - self.y1)
        if dx == 0 and dy == 0:
            return -min(x - self.x0, self.x1 - x, y - self.y0, self.y1 - y)
        return math.hypot(dx, dy)


@dataclass
class Poly:
    pts: list
    role: str
    target: int | None = None
    rnd: int = 0


@dataclass
class Board:
    name: str
    w: float
    h: float
    circles: list = field(default_factory=list)
    rects: list = field(default_factory=list)
    polys: list = field(default_factory=list)
    texts: list = field(default_factory=list)  # (x, y, tex, size, weight, color, anchor)
    extras: list = field(default_factory=list)  # raw tikz lines


def sample_poly(pts, step=0.25):
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        length = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(math.ceil(length / step)))
        for i in range(n + 1):
            t = i / n
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, length * (1 - t)))
            # third value is distance-to-tip along this segment only; recomputed later
    # recompute distance-to-tip along the whole path
    tip = pts[-1]
    return [(x, y, math.hypot(x - tip[0], y - tip[1])) for x, y in
            {(round(p[0], 3), round(p[1], 3)) for p in out} | {(round(tip[0], 3), round(tip[1], 3))}]


def validate(board: Board):
    errors = []
    # circles do not overlap each other
    for i, a in enumerate(board.circles):
        for b in board.circles[i + 1 :]:
            need = a.r + b.r + 0.45
            if a.dist(b.x, b.y) < need:
                errors.append(
                    f"circles {a.value}@{a.rnd}/r{a.run} and {b.value}@{b.rnd}/r{b.run} "
                    f"gap {a.dist(b.x, b.y) - a.r - b.r:.2f}"
                )
    # window rects do not overlap and do not cover non-window circles
    for i, a in enumerate(board.rects):
        for b in board.rects[i + 1 :]:
            overlap = not (a.x1 < b.x0 - 0.3 or b.x1 < a.x0 - 0.3 or a.y1 < b.y0 - 0.3 or b.y1 < a.y0 - 0.3)
            if overlap:
                errors.append(f"window rects overlap r{a.run} and r{b.run} round {a.rnd}")
        for c in board.circles:
            if c.rnd != a.rnd or c.run != a.run:
                continue
            inside = a.contains(c.x, c.y, eps=-0.2)
            if c.kind in ("new", "retained") and not inside:
                errors.append(f"window item {c.value} outside its box")
            if c.kind in ("unread", "emitted") and a.contains(c.x, c.y, eps=0.05):
                errors.append(f"{c.kind} item {c.value} inside window box")
    # arrows
    for poly in board.polys:
        samples = []
        pts = poly.pts
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            length = math.hypot(x1 - x0, y1 - y0)
            n = max(1, int(math.ceil(length / 0.2)))
            for i in range(n + 1):
                t = i / n
                samples.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        tip = pts[-1]
        for x, y in samples:
            to_tip = math.hypot(x - tip[0], y - tip[1])
            for c in board.circles:
                d = c.dist(x, y)
                # the tip may approach the target circle but must stay outside it
                limit = c.r + (0.28 if (poly.target == c.value and to_tip < 1.6) else 0.55)
                if d < limit:
                    errors.append(
                        f"{poly.role} passes circle {c.value} (d={d:.2f}, r={c.r:.2f}) "
                        f"at ({x:.1f},{y:.1f})"
                    )
                    break
        if poly.target is not None:
            targets = [
                c
                for c in board.circles
                if c.value == poly.target
                and c.rnd == poly.rnd
                and c.run >= 0
                and c.kind in ("retained", "new")
            ]
            if len(targets) != 1:
                errors.append(f"{poly.role} window target {poly.target} count={len(targets)}")
            else:
                c = targets[0]
                nearest = min(board.circles, key=lambda o: o.dist(tip[0], tip[1]))
                if nearest is not c:
                    errors.append(
                        f"{poly.role} tip nearer to {nearest.value} {nearest.kind} "
                        f"r{nearest.run} than window {poly.target}"
                    )
                rects = [r for r in board.rects if r.rnd == poly.rnd and r.run == c.run]
                if not rects:
                    errors.append(f"{poly.role} missing window rect")
                else:
                    outside = rects[0].inset_of_boundary(tip[0], tip[1])
                    if outside < -0.05 or outside > 0.55:
                        errors.append(
                            f"{poly.role} tip not on window edge (signed {outside:.2f}) target {poly.target}"
                        )
        # The underline is the only path whose start must sit under retained output.
        if poly.role.startswith("under"):
            start = pts[0]
            outs = [c for c in board.circles if c.run == -1]
            if outs:
                nearest = min(outs, key=lambda o: o.dist(start[0], start[1]))
                if nearest.kind != "retained":
                    errors.append(f"{poly.role} starts nearer {nearest.kind} {nearest.value}")
    errors.extend(text_hits(board))
    if errors:
        print(f"\n{board.name}: {len(errors)} geometry errors")
        for e in errors[:40]:
            print(" -", e)
        raise SystemExit(1)
    print(f"{board.name}: geometry ok, {len(board.circles)} circles, {len(board.polys)} paths")


def text_box(item):
    x, y, tex, size, _weight, _color, anchor = item
    plain = tex
    for tok in ("$", r"\quad", r"\,", "{", "}", "\\varphi", "\\emptyset", "\\"):
        plain = plain.replace(tok, "")
    plain = plain.replace("_", "")
    width = max(3.2, len(plain) * size * 0.3528 * 0.50)
    height = size * 0.3528
    if anchor == "west":
        x0, x1 = x, x + width
    elif anchor == "east":
        x0, x1 = x - width, x
    else:
        x0, x1 = x - width / 2, x + width / 2
    return x0 - 0.3, y - 0.35 * height, x1 + 0.3, y + 0.85 * height


def text_hits(board: Board):
    errors = []
    boxes = [(text_box(t), t[2]) for t in board.texts]
    for (x0, y0, x1, y1), label in boxes:
        for c in board.circles:
            # closest point of the box to the circle center
            cx = min(max(c.x, x0), x1)
            cy = min(max(c.y, y0), y1)
            if c.dist(cx, cy) < c.r + 0.25:
                errors.append(f"text {label!r} hits circle {c.value} ({c.kind})")
                break
        for poly in board.polys:
            for (ax, ay), (bx, by) in zip(poly.pts, poly.pts[1:]):
                # sample
                length = math.hypot(bx - ax, by - ay)
                n = max(1, int(length / 0.4))
                for i in range(n + 1):
                    t = i / n
                    x = ax + (bx - ax) * t
                    y = ay + (by - ay) * t
                    if x0 <= x <= x1 and y0 <= y <= y1:
                        errors.append(f"text {label!r} hits {poly.role}")
                        break
                else:
                    continue
                break
    return errors


def tex_escape_text(s):
    return s


def circle_node(c: Circle):
    if c.kind == "emitted":
        fill, stroke, sw, text = "emit", "emit", "0.4pt", "white"
    elif c.kind == "retained":
        fill, stroke, sw, text = "keep", "keep", "0.4pt", "white"
    elif c.kind == "new":
        fill, stroke, sw, text = "white", "ink", "0.85pt", "ink"
    else:
        fill, stroke, sw, text = "white", "unread", "0.55pt", "ink"
    size = 6.3 if c.r < 3.05 else 7.1
    if c.value >= 10 and c.r < 3.05:
        size = 5.9
    return (
        f"\\fill[{fill}] ({c.x:.3f},{c.y:.3f}) circle ({c.r:.3f});"
        f"\\draw[{stroke}, line width={sw}] ({c.x:.3f},{c.y:.3f}) circle ({c.r:.3f});"
        f"\\node[text={text}, font=\\sffamily\\bfseries\\fontsize{{{size}}}{{{size+0.8}}}\\selectfont]"
        f" at ({c.x:.3f},{c.y:.3f}) {{{c.value}}};"
    )


def build(mode: str) -> Board:
    wide = mode == "wide"
    page_w = TEXTWIDTH_MM if wide else COLUMN_SLOT_MM
    margin_x = 1.6 if wide else 1.3
    gutter = 4.4 if wide else 0.0
    ncols = 3 if wide else 1
    col_w = (page_w - 2 * margin_x - (ncols - 1) * gutter) / ncols
    T_R = 3.22 if wide else 2.95
    T_PITCH = 9.05 if wide else 8.15
    U_R = 2.75 if wide else 2.45
    ROW = 11.35 if wide else 8.9
    O_R = 2.78 if wide else 2.55
    O_PITCH = 6.15 if wide else 6.55
    O_GAP = 3.55 if wide else 2.9
    badge_r = 3.25 if wide else 2.85
    label_w = 6.6 if wide else 6.2
    box_pad = 0.48

    rounds = walk_rounds()
    check_rounds(rounds)

    # vertical layout, y-up, top of the round blocks computed after height known
    # measure one round block height first
    # Title baseline, then a clear band for the re-entry arrow, then the R1 box.
    # The circle radius sits below header_h, so the band must include it.
    header_h = (2.6 + 3.0 + 1.6 + box_pad + T_R)
    below_windows = 4.6 if wide else 3.05  # box bottom to badge top
    after_badge = 1.6 if wide else 0.85
    label_h = 3.3 if wide else 2.45
    o_block = label_h + 2 * O_R + 2.3
    rows_span = 3 * ROW  # R1 center to R4 center
    block_h = header_h + T_R + rows_span + T_R + box_pad + below_windows + 2 * badge_r + after_badge + o_block
    inter = 0.0 if wide else 1.15
    pi_h = 19.2 if wide else 6.2
    legend_h = 13.5 if wide else 13.2
    margin_y = 1.7 if wide else 1.15
    if wide:
        page_h = margin_y + block_h + 3.2 + pi_h + legend_h + margin_y
    else:
        page_h = margin_y + 3 * block_h + 2 * inter + pi_h + legend_h + margin_y

    board = Board(mode, page_w, page_h)
    rounds_geom = []

    def place_round(index, left, top):
        rnd = rounds[index]
        title_y = top - 2.6
        r1_center = top - header_h
        centers_y = [r1_center - row * ROW for row in range(4)]
        slot0 = left + label_w + T_R
        # output row
        badge_top = centers_y[3] - T_R - box_pad - below_windows
        badge_y = badge_top - badge_r
        label_y = badge_y - badge_r - after_badge - 1.6
        o_y = label_y - 1.5 - O_R
        # O centers
        emit = rnd["emit"]
        keep = rnd["retained"]
        o_left = left + 0.7 + O_R
        # fit check
        span = (len(emit) + len(keep) - 1) * O_PITCH + (O_GAP if keep else 0) + 2 * O_R
        if len(emit) + len(keep) == 1:
            span = 2 * O_R
        if o_left - O_R + span > left + col_w - 0.45:
            raise SystemExit(f"O row overflows column in {mode} round {index+1}: {span:.2f} > {col_w:.2f}")
        xs = []
        x = o_left
        for _ in emit:
            xs.append(x)
            x += O_PITCH
        if keep:
            x += O_GAP - 0  # O_PITCH already applied by the loop's last increment; add extra only
            # The loop added O_PITCH after the last emit. Extra gap is O_GAP on top of that pitch.
            # Wait: after last emit, x is last+O_PITCH. We want last+O_PITCH+O_GAP.
            # So the first keep is at x + O_GAP, but x already includes one pitch. Yes add O_GAP.
            x += O_GAP
            # BUG check below in a comment: I added O_GAP twice in the span formula vs here.
        # Recalculate cleanly
        xs = []
        cursor_x = o_left
        for i, _v in enumerate(emit):
            xs.append(cursor_x)
            cursor_x += O_PITCH
        if keep:
            cursor_x += O_GAP  # cursor_x is already one pitch past the last emit
            for _v in keep:
                xs.append(cursor_x)
                cursor_x += O_PITCH
        values_o = emit + keep
        kinds_o = ["emitted"] * len(emit) + ["retained"] * len(keep)
        for x_i, value, kind in zip(xs, values_o, kinds_o):
            board.circles.append(Circle(x_i, o_y, O_R, value, kind, -1, -1, index))
        # separator between emit and keep
        if keep:
            gap_left = xs[len(emit) - 1] + O_R
            gap_right = xs[len(emit)] - O_R
            sep_x = (gap_left + gap_right) / 2
            board.extras.append(
                f"\\draw[ink, line width=0.45pt] ({sep_x:.3f},{o_y-O_R+0.15:.3f}) -- ({sep_x:.3f},{o_y+O_R-0.15:.3f});"
            )
            board.texts.append((sum(xs[: len(emit)]) / len(emit), label_y, "out", 6.4, "bf", "emit", "mid"))
            board.texts.append((sum(xs[len(emit) :]) / len(keep), label_y, "keep", 6.4, "bf", "keep", "mid"))
        else:
            board.texts.append((sum(xs) / len(xs), label_y, "out", 6.4, "bf", "emit", "mid"))
            board.texts.append((xs[-1] + O_R + 4.2, label_y, r"keep $\emptyset$", 6.4, "md", "keep", "mid"))

        # tapes
        prior = set(rnd["priorRetained"])
        window_circles = []
        for run in range(4):
            cy = centers_y[run]
            board.texts.append(
                (left + 0.2, cy, f"$R_{run+1}$", 7.4 if wide else 7.0, "md", "ink", "west")
            )
            cursor = rnd["positions"][run]
            b_i = rnd["b"][run]
            for slot, value in enumerate(RUNS[run]):
                cx = slot0 + slot * T_PITCH
                if slot < cursor:
                    kind, rad = "emitted", T_R
                elif slot < cursor + b_i:
                    kind, rad = ("retained" if value in prior else "new"), T_R
                else:
                    kind, rad = "unread", U_R
                c = Circle(cx, cy, rad, value, kind, run, slot, index)
                board.circles.append(c)
                if kind in ("new", "retained"):
                    window_circles.append(c)
            if not rnd["unread"][run]:
                empty_x = slot0 + 3 * T_PITCH + T_R + 3.15
                board.texts.append((empty_x, cy, r"$\emptyset$", 7.2 if wide else 6.6, "md", "muted", "mid"))
            # window rectangle around the window slots only
            w0 = cursor
            w1 = cursor + b_i - 1
            x0 = slot0 + w0 * T_PITCH - T_R - box_pad
            x1 = slot0 + w1 * T_PITCH + T_R + box_pad
            y0 = cy - T_R - box_pad
            y1 = cy + T_R + box_pad
            board.rects.append(Rect(x0, y0, x1, y1, index, run))

        # badge under the windows, centered on the tape
        tape_cx = slot0 + 1.5 * T_PITCH
        board.extras.append(
            f"\\fill[call] ({tape_cx:.3f},{badge_y:.3f}) circle ({badge_r:.3f});"
            f"\\node[text=white, font=\\sffamily\\bfseries\\fontsize{{9}}{{10}}\\selectfont] "
            f"at ({tape_cx:.3f},{badge_y:.3f}) {{{index+1}}};"
        )
        board.texts.append(
            (tape_cx + badge_r + 1.3, badge_y, f"$|B|={len(rnd['candidates'])}$", 8.0 if wide else 7.4, "bf", "ink", "west")
        )
        # flow arrow from below the lowest window boxes down to the badge
        lowest = min(r.y0 for r in board.rects if r.rnd == index)
        flow_top = lowest - 0.7
        flow_bot = badge_y + badge_r + 0.55
        board.polys.append(Poly([(tape_cx, flow_top), (tape_cx, flow_bot)], f"flow-{index+1}", None, index))

        # One header line. A second line sat on the R1 circles.
        if index < 2:
            btex = f"Round {index+1}, $b_i=2$"
        else:
            btex = r"Round 3, $b_2=b_4=1$"
        board.texts.append(
            (left + col_w / 2, title_y, btex, 8.6 if wide else 7.5, "bf", "ink", "mid")
        )

        # Arrow into R1 travels in the band reserved under the title.
        r1_box_top = centers_y[0] + T_R + box_pad
        header_branch_y = r1_box_top + 1.6
        return {
            "left": left,
            "top": top,
            "slot0": slot0,
            "centers_y": centers_y,
            "o_y": o_y,
            "o_xs": xs,
            "emit_n": len(emit),
            "keep": keep,
            "badge": (tape_cx, badge_y, badge_r),
            "header_branch_y": header_branch_y,
            "window_by_value": {c.value: c for c in window_circles},
        }

    if wide:
        top = page_h - margin_y
        for i in range(3):
            left = margin_x + i * (col_w + gutter)
            rounds_geom.append(place_round(i, left, top))
        content_bottom = rounds_geom[0]["o_y"] - O_R - 2.4
    else:
        top = page_h - margin_y
        for i in range(3):
            rounds_geom.append(place_round(i, margin_x, top))
            top -= block_h + inter
        content_bottom = rounds_geom[-1]["o_y"] - O_R - 2.0

    # keep arrows
    def add_keep(src, dst, trunk_x, direction):
        """direction +1: branches leave the trunk toward +x (wide).
        direction -1: branches leave toward -x (stack).
        The path starts on the underline under the source keep circles.
        """
        keep_vals = src["keep"]
        if not keep_vals:
            return
        xs = src["o_xs"][src["emit_n"] :]
        y_under = src["o_y"] - O_R - 1.05
        x_a = xs[0] - O_R + 0.15
        x_b = xs[-1] + O_R - 0.15
        # underline is the start. It is not an arrow. Stored as a poly so the
        # collision check sees it, role 'under'.
        board.polys.append(Poly([(x_a, y_under), (x_b, y_under)], f"under-{src['top']:.0f}", None, -1))
        # trunk from the underline end on the gutter side
        if direction > 0:
            start = (x_b, y_under)
        else:
            start = (x_b, y_under)  # still the east end; channel is to the east
        # rise/fall in the channel
        board.polys.append(Poly([start, (trunk_x, y_under)], f"keep-join-{dst['top']:.0f}", None, -1))
        # branches, one per retained item, tip on that item's window box
        branch_ys = []
        tips = []
        for value in keep_vals:
            c = dst["window_by_value"][value]
            if c.run == 0:
                by = dst["header_branch_y"]
            else:
                # gap above this row: midway between this center and the row above,
                # but below the upper window box and above this window box
                upper = dst["centers_y"][c.run - 1]
                by = (c.y + T_R + box_pad + upper - T_R - box_pad) / 2
            rect = next(r for r in board.rects if r.rnd == c.rnd and r.run == c.run)
            tip_y = rect.y1 + 0.22  # just outside the top edge
            branch_ys.append(by)
            tips.append((value, c, by, tip_y))
        # vertical trunk spans the join y and all branch ys
        ys = [y_under] + branch_ys
        board.polys.append(
            Poly([(trunk_x, max(ys)), (trunk_x, min(ys))], f"keep-trunk-{dst['top']:.0f}", None, -1)
        )
        for value, c, by, tip_y in tips:
            board.polys.append(
                Poly(
                    [(trunk_x, by), (c.x, by), (c.x, tip_y)],
                    f"keep-{value}",
                    target=value,
                    rnd=c.rnd,
                )
            )

    if wide:
        for i in range(2):
            trunk_x = margin_x + (i + 1) * col_w + i * gutter + gutter / 2
            add_keep(rounds_geom[i], rounds_geom[i + 1], trunk_x, +1)
    else:
        trunk_x = page_w - margin_x - 0.15

        def add_group(src, dst_index):
            """One margin arrow. The column is too narrow for a line per item."""
            xs = src["o_xs"][src["emit_n"] :]
            y_under = src["o_y"] - O_R - 1.05
            x_a = xs[0] - O_R + 0.15
            x_b = xs[-1] + O_R - 0.15
            board.polys.append(Poly([(x_a, y_under), (x_b, y_under)], f"under-g{dst_index}", None, -1))
            circles = [c for c in board.circles if c.rnd == dst_index and c.run >= 0]
            rects = [r for r in board.rects if r.rnd == dst_index]
            right = max(c.x + c.r for c in circles)
            bracket_x = right + 7.8
            if bracket_x > trunk_x - 2.4:
                raise SystemExit("stack bracket meets the arrow channel")
            y_hi = max(r.y1 for r in rects)
            y_lo = min(r.y0 for r in rects)
            meet_y = (rounds_geom[dst_index]["centers_y"][1] + rounds_geom[dst_index]["centers_y"][2]) / 2
            board.polys.append(Poly([(bracket_x, y_lo), (bracket_x, y_hi)], f"bracket-{dst_index}", None, dst_index))
            board.polys.append(
                Poly(
                    [(x_b, y_under), (trunk_x, y_under), (trunk_x, meet_y), (bracket_x + 0.15, meet_y)],
                    f"keep-group-{dst_index}",
                    None,
                    dst_index,
                )
            )

        for i in range(2):
            add_group(rounds_geom[i], i + 1)

    # Pi row. The column reflow is not wide enough for 16 readable chips,
    # so it states the same partition in text. The wide board draws the chips.
    pi_top = content_bottom - (1.2 if wide else 0.4)
    if wide:
        pi_y = pi_top - 5.6
        pi_r = 3.05
        pi_pitch = 8.55
        pi_span = 15 * pi_pitch + 2 * pi_r
        pi_x0 = (page_w - pi_span) / 2 + pi_r
        for i, value in enumerate(range(1, 17)):
            cx = pi_x0 + i * pi_pitch
            board.circles.append(Circle(cx, pi_y, pi_r, value, "emitted", -2, i, -1))
        board.texts.append((pi_x0 - pi_r - 1.3, pi_y, r"$\Pi=$", 8.0, "bf", "ink", "east"))
        groups = [(0, 5, "5"), (5, 10, "5"), (10, 16, "6")]
        brace_y = pi_y - pi_r - 0.7
        for a, b, lab in groups:
            x_l = pi_x0 + a * pi_pitch - pi_r + 0.3
            x_r = pi_x0 + (b - 1) * pi_pitch + pi_r - 0.3
            y1 = brace_y
            y2 = brace_y - 1.15
            board.extras.append(
                f"\\draw[ink, line width=0.4pt] ({x_l:.3f},{y1:.3f}) -- ({x_l:.3f},{y2:.3f}) -- ({x_r:.3f},{y2:.3f}) -- ({x_r:.3f},{y1:.3f});"
            )
            board.texts.append(((x_l + x_r) / 2, y2 - 1.7, lab, 6.6, "bf", "ink", "mid"))
        sum_y = brace_y - 6.5
        board.texts.append((page_w / 2, sum_y, r"$5+5+6=16$", 7.6, "bf", "ink", "mid"))
    else:
        sum_y = pi_top - 3.2
        board.texts.append(
            (
                page_w / 2,
                sum_y,
                r"$\Pi=(1..5)\,(6..10)\,(11..16),\ 5+5+6=16$",
                6.7,
                "bf",
                "ink",
                "mid",
            )
        )

    # legend, flowed
    legend_top = sum_y - 3.4
    items = [
        ("box", r"window $W_i$"),
        ("badge", r"one ListwiseRank$(B,\varphi)$"),
        ("emit", "emitted"),
        ("keep", "retained, re-enters"),
        ("new", r"new in $W_i$"),
        ("unread", "unread"),
    ]
    # manual two or three rows
    if wide:
        rows = [items[:3], items[3:]]
    else:
        rows = [items[:2], items[2:4], items[4:]]
    y = legend_top
    for row in rows:
        # estimate widths and center the row
        widths = []
        for kind, label in row:
            widths.append(8.5 + len(label) * (1.45 if wide else 1.28))
        gap = 4.2 if wide else 2.6
        total = sum(widths) + gap * (len(row) - 1)
        x = (page_w - total) / 2
        for (kind, label), w in zip(row, widths):
            board.extras.append(legend_sample(kind, x, y))
            board.texts.append((x + 7.2, y, label, 6.5 if wide else 5.9, "md", "ink", "west"))
            x += w + gap
        y -= 4.6 if wide else 4.2

    # shift nothing: coordinates already in page space. Check bottom margin.
    lowest_text = y
    if lowest_text < 0.8:
        raise SystemExit(f"{mode} legend falls off the page at y={lowest_text:.2f}, page_h={page_h:.2f}")
    board.h = page_h
    board.w = page_w
    return board


def legend_sample(kind, x, y):
    if kind == "box":
        return (
            f"\\draw[call, line width=0.7pt, dash pattern=on 1.15mm off 0.7mm, rounded corners=0.4mm] "
            f"({x:.3f},{y-1.5:.3f}) rectangle ({x+5.2:.3f},{y+1.5:.3f});"
        )
    if kind == "badge":
        return (
            f"\\fill[call] ({x+2.3:.3f},{y:.3f}) circle (1.7);"
            f"\\node[text=white, font=\\sffamily\\bfseries\\fontsize{{6.5}}{{7}}\\selectfont] at ({x+2.3:.3f},{y:.3f}) {{1}};"
        )
    if kind == "emit":
        return (
            f"\\fill[emit] ({x+2.3:.3f},{y:.3f}) circle (1.7);"
            f"\\node[text=white, font=\\sffamily\\bfseries\\fontsize{{6}}{{7}}\\selectfont] at ({x+2.3:.3f},{y:.3f}) {{5}};"
        )
    if kind == "keep":
        return (
            f"\\fill[keep] ({x+2.3:.3f},{y:.3f}) circle (1.7);"
            f"\\node[text=white, font=\\sffamily\\bfseries\\fontsize{{6}}{{7}}\\selectfont] at ({x+2.3:.3f},{y:.3f}) {{7}};"
        )
    if kind == "new":
        return (
            f"\\draw[ink, line width=0.7pt, fill=white] ({x+2.3:.3f},{y:.3f}) circle (1.7);"
            f"\\node[text=ink, font=\\sffamily\\bfseries\\fontsize{{6}}{{7}}\\selectfont] at ({x+2.3:.3f},{y:.3f}) {{6}};"
        )
    return (
        f"\\draw[unread, line width=0.45pt, fill=white] ({x+2.3:.3f},{y:.3f}) circle (1.55);"
        f"\\node[text=ink, font=\\sffamily\\bfseries\\fontsize{{5.6}}{{6.4}}\\selectfont] at ({x+2.3:.3f},{y:.3f}) {{16}};"
    )


def emit_tex(board: Board, path: Path):
    lines = [
        "% Sliding-window merge, generated by generate_sw.py.",
        "% Do not edit by hand; rerun the generator. States are the checked walk.",
        r"\documentclass[tikz,border=0pt]{standalone}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage{tgheros}",
        r"\renewcommand{\familydefault}{\sfdefault}",
        r"\usepackage{sansmath}",
        r"\usepackage{amsmath,amssymb}",
        r"\usetikzlibrary{arrows.meta}",
        r"\definecolor{ink}{HTML}{1C2126}",
        r"\definecolor{emit}{HTML}{2F6294}",
        r"\definecolor{keep}{HTML}{4A5560}",
        r"\definecolor{call}{HTML}{C44536}",
        r"\definecolor{unread}{HTML}{8E969C}",
        r"\definecolor{muted}{HTML}{5C656C}",
        r"\begin{document}",
        r"\begin{sansmath}",
        r"\begin{tikzpicture}[x=1mm,y=1mm, every node/.style={inner sep=0pt, outer sep=0pt}]",
        f"\\fill[white] (0,0) rectangle ({board.w:.3f},{board.h:.3f});",
        "% window boxes",
    ]
    for r in board.rects:
        lines.append(
            f"\\draw[call, line width=0.72pt, dash pattern=on 1.25mm off 0.78mm, rounded corners=0.55mm] "
            f"({r.x0:.3f},{r.y0:.3f}) rectangle ({r.x1:.3f},{r.y1:.3f});"
        )
    lines.append("% circles")
    # draw unread and emitted first, then window items, so strokes stay crisp
    for c in board.circles:
        lines.append(circle_node(c))
    lines.append("% paths")
    for poly in board.polys:
        pts = " -- ".join(f"({x:.3f},{y:.3f})" for x, y in poly.pts)
        arrow = poly.target is not None or poly.role.startswith("keep-group") or poly.role.startswith("flow")
        if arrow:
            width = "0.5pt" if poly.role.startswith("flow") else "0.62pt"
            length = "1.35mm" if poly.role.startswith("flow") else "1.5mm"
            lines.append(
                f"\\draw[ink, line width={width}, line cap=round, line join=round, "
                f"-{{Stealth[length={length}, width=1.15mm, inset=0.15mm]}}] {pts};"
            )
        else:
            weight = "0.9pt" if poly.role.startswith("bracket") else "0.62pt"
            lines.append(
                f"\\draw[ink, line width={weight}, line cap=round, line join=round] {pts};"
            )
    lines.extend(board.extras)
    lines.append("% text")
    for x, y, text, size, weight, color, anchor in board.texts:
        font = r"\sffamily\bfseries" if weight == "bf" else r"\sffamily"
        anch = "" if anchor == "mid" else f", anchor={anchor}"
        lines.append(
            f"\\node[text={color}, font={font}\\fontsize{{{size}}}{{{size+0.9}}}\\selectfont{anch}] "
            f"at ({x:.3f},{y:.3f}) {{{text}}};"
        )
    lines += [
        r"\end{tikzpicture}",
        r"\end{sansmath}",
        r"\end{document}",
        "",
    ]
    path.write_text("\n".join(lines))


def arrow_record(board: Board):
    rows = []
    for poly in board.polys:
        rows.append(
            {
                "role": poly.role,
                "target": poly.target,
                "round": poly.rnd,
                "points_mm": [[round(x, 2), round(y, 2)] for x, y in poly.pts],
                "start_mm": [round(poly.pts[0][0], 2), round(poly.pts[0][1], 2)],
                "end_mm": [round(poly.pts[-1][0], 2), round(poly.pts[-1][1], 2)],
            }
        )
    return rows


def main():
    rounds = walk_rounds()
    check_rounds(rounds)
    (HERE / "verified-states.json").write_text(json.dumps(rounds, indent=2) + "\n")
    print("state walk matches validated_states / paper example")
    print(f"textwidth {TEXTWIDTH_MM:.2f} mm; 0.95 columnwidth {COLUMN_SLOT_MM:.2f} mm")
    for mode, name in (("wide", "sw-wide.tex"), ("stack", "sw-stack.tex")):
        board = build(mode)
        # underlines and trunks are not "keep-<id>" so target checks skip them.
        # Rename join/trunk/under roles so validate does not require a target,
        # and so keep-start check only applies to the arrow that leaves the underline.
        validate(board)
        emit_tex(board, HERE / name)
        (HERE / f"arrow-endpoints-{mode}.json").write_text(
            json.dumps(arrow_record(board), indent=2) + "\n"
        )
        print(f"wrote {name}  {board.w:.2f} x {board.h:.2f} mm")


if __name__ == "__main__":
    main()
