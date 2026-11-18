"""Place short labels next to mean markers.

Coordinates are display pixels, y upward. A leader is drawn only when the
label sits far enough from its marker that the pairing is no longer obvious.
Leaders stop on the marker edge and are rejected if they pass through any
other marker.
"""

from __future__ import annotations

import math

LEADER_GAP_PT = 5.5
CLEAR_PT = 2.2


def point_segment_distance(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    seg2 = vx * vx + vy * vy
    if seg2 <= 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, (wx * vx + wy * vy) / seg2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def rects_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float], pad: float) -> bool:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 + pad <= bx0 or bx1 + pad <= ax0 or ay1 + pad <= by0 or by1 + pad <= ay0)


def rect_hits_circle(rect: tuple[float, float, float, float], cx: float, cy: float, radius: float, pad: float) -> bool:
    x0, y0, x1, y1 = rect
    qx = min(max(cx, x0), x1)
    qy = min(max(cy, y0), y1)
    return math.hypot(qx - cx, qy - cy) < radius + pad


def _closest_on_rect(rect: tuple[float, float, float, float], cx: float, cy: float) -> tuple[float, float]:
    x0, y0, x1, y1 = rect
    return (min(max(cx, x0), x1), min(max(cy, y0), y1))


def _on_circle(cx: float, cy: float, radius: float, px: float, py: float) -> tuple[float, float]:
    dx, dy = px - cx, py - cy
    dist = math.hypot(dx, dy)
    if dist < 1e-9:
        return (cx + radius, cy)
    scale = radius / dist
    return (cx + dx * scale, cy + dy * scale)


def _rect(cx: float, cy: float, w: float, h: float) -> tuple[float, float, float, float]:
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def _inside(rect: tuple[float, float, float, float], bounds: tuple[float, float, float, float], margin: float) -> bool:
    x0, y0, x1, y1 = rect
    b0, b1, b2, b3 = bounds
    return x0 >= b0 + margin and y0 >= b1 + margin and x1 <= b2 - margin and y1 <= b3 - margin


def _away_angle(marker: dict, others: list[dict]) -> float:
    sx = sy = 0.0
    for other in others:
        dx = marker["x"] - other["x"]
        dy = marker["y"] - other["y"]
        dist2 = dx * dx + dy * dy
        if dist2 < 1e-6:
            continue
        sx += dx / dist2
        sy += dy / dist2
    if sx == 0.0 and sy == 0.0:
        return 50.0
    return math.degrees(math.atan2(sy, sx))


def _leader_segment(rect, marker):
    start = _closest_on_rect(rect, marker["x"], marker["y"])
    end = _on_circle(marker["x"], marker["y"], marker["r"], start[0], start[1])
    return start, end


def _leader_clear(rect, marker, markers, clear: float) -> bool:
    start, end = _leader_segment(rect, marker)
    for other in markers:
        if other["id"] == marker["id"]:
            continue
        gap = point_segment_distance(other["x"], other["y"], start[0], start[1], end[0], end[1])
        if gap < other["r"] + clear:
            return False
    return True


def _gap_px(rect, marker) -> float:
    qx, qy = _closest_on_rect(rect, marker["x"], marker["y"])
    return math.hypot(qx - marker["x"], qy - marker["y"]) - marker["r"]


def place_labels(
    markers: list[dict],
    label_sizes: dict[str, tuple[float, float]],
    bounds: tuple[float, float, float, float],
    *,
    dpi: float,
) -> list[dict]:
    """Return one placement per marker. `markers` use display pixels."""
    gap_limit = LEADER_GAP_PT * dpi / 72.0
    clear = CLEAR_PT * dpi / 72.0
    nearest = []
    for marker in markers:
        others = [other for other in markers if other["id"] != marker["id"]]
        if not others:
            nearest.append((math.inf, marker["id"]))
            continue
        dist = min(math.hypot(marker["x"] - other["x"], marker["y"] - other["y"]) for other in others)
        nearest.append((dist, marker["id"]))
    order = [marker_id for _dist, marker_id in sorted(nearest, key=lambda item: (item[0], item[1]))]
    by_id = {marker["id"]: marker for marker in markers}
    placed: list[dict] = []
    placed_rects: list[tuple[float, float, float, float]] = []

    for marker_id in order:
        marker = by_id[marker_id]
        others = [other for other in markers if other["id"] != marker_id]
        width, height = label_sizes[marker_id]
        base = _away_angle(marker, others)
        radii_pt = (9, 13, 17, 22, 28, 35)
        angles = [base + delta for delta in (0, 18, -18, 38, -38, 62, -62, 95, -95, 140, -140, 180)]
        feasible: list[tuple[float, dict]] = []
        fallback: tuple[float, dict] | None = None
        for radius_pt in radii_pt:
            radius = radius_pt * dpi / 72.0
            for angle in angles:
                rad = math.radians(angle)
                cx = marker["x"] + radius * math.cos(rad)
                cy = marker["y"] + radius * math.sin(rad)
                rect = _rect(cx, cy, width, height)
                outside = not _inside(rect, bounds, 1.5)
                hit_marker = any(rect_hits_circle(rect, item["x"], item["y"], item["r"], clear) for item in markers)
                hit_label = any(rects_overlap(rect, prev, clear) for prev in placed_rects)
                need_leader = _gap_px(rect, marker) > gap_limit
                hit_leader = need_leader and not _leader_clear(rect, marker, markers, clear)
                penalty = 0
                if outside:
                    penalty += 80
                if hit_marker:
                    penalty += 40
                if hit_label:
                    penalty += 25
                if hit_leader:
                    penalty += 30
                turn = abs((angle - base + 180) % 360 - 180)
                score = penalty * 10 + radius_pt + turn / 40.0
                record = {
                    "id": marker_id,
                    "cx": cx,
                    "cy": cy,
                    "rect": rect,
                    "need_leader": need_leader and not outside,
                }
                if fallback is None or score < fallback[0]:
                    fallback = (score, record)
                if penalty == 0:
                    feasible.append((score, record))
        chosen = min(feasible, key=lambda item: item[0])[1] if feasible else fallback[1]
        if chosen["need_leader"] and _leader_clear(chosen["rect"], marker, markers, clear):
            chosen["leader"] = _leader_segment(chosen["rect"], marker)
        else:
            chosen["leader"] = None
            chosen["need_leader"] = False
        placed.append(chosen)
        placed_rects.append(chosen["rect"])
    return placed
