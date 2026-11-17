"""Replay rule copied from the verified loser_tree.py lines 148–183.

left/right are replay-slot arguments, not run ids. Short slots are padded
to h with virtual +infinity tags. Those tags never enter the listwise call.
The pointer is the child whose slot first reaches count h. Winner and loser
are the real items in the first h and the remaining logical positions.
"""

from __future__ import annotations


def replay_segment(left, right, positions, h, left_child, right_child):
    if h <= 0:
        raise ValueError("h")
    if len(left) > h or len(right) > h:
        raise RuntimeError("segment longer than h")
    tagged = [(item, 0) for item in left] + [(item, 1) for item in right]
    tagged.sort(key=lambda pair: positions[pair[0]])
    left_virtual = h - len(left)
    right_virtual = h - len(right)
    logical = tagged + [(None, 0)] * left_virtual + [(None, 1)] * right_virtual
    counts = [0, 0]
    side = None
    for _item, slot in logical:
        counts[slot] += 1
        side = slot
        if counts[slot] == h:
            break
    winner = [item for item, _slot in logical[:h] if item is not None]
    loser = [item for item, _slot in logical[h:] if item is not None]
    pointer = left_child if side == 0 else right_child
    return {
        "winner": winner,
        "loser": loser,
        "pointer": pointer,
        "pointer_side": "left" if side == 0 else "right",
        "left_virtual": left_virtual,
        "right_virtual": right_virtual,
    }


def legal_surface_triangles(present: set[tuple[int, int]]) -> list[tuple[tuple[int, int], ...]]:
    """Unit squares become two triangles only when all four corners exist."""
    triangles = []
    xs = sorted({k for k, _h in present})
    ys = sorted({h for _k, h in present})
    for k in xs:
        for h in ys:
            corners = [(k, h), (k + 1, h), (k + 1, h + 1), (k, h + 1)]
            if all(corner in present for corner in corners):
                triangles.append((corners[0], corners[1], corners[2]))
                triangles.append((corners[0], corners[2], corners[3]))
    return triangles
