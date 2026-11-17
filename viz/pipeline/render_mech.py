"""Mechanism figures aligned to the five verified files.

Blue fill is an item yielded to the output. Blue stroke is a transient
winner that has not been yielded. Red dash is one listwise call and covers
only real items. A stored loser is gray. Unread run items are hollow.
Virtual +infinity is a dotted mark outside the call. Tree edges are thin;
pointer(v) is a separate thick arrow.
"""

from __future__ import annotations

from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

from .style import BLUE, FIG, GRAY, INK, MUTED, RED, plt

FIG.mkdir(parents=True, exist_ok=True)


def _save(fig, name):
    fig.savefig(FIG / name, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def _pill(ax, x, y, text, face, edge, text_color=INK, w=0.42, h=0.28):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=face, edgecolor=edge, linewidth=0.8, mutation_aspect=0.6))
    ax.text(x, y, text, ha="center", va="center", fontsize=7, color=text_color)


def _row(ax, x, y, items, face, edge, text_color=INK, w=0.62):
    step = w + 0.22
    for i, item in enumerate(items):
        _pill(ax, x + i * step, y, str(item), face, edge, text_color, w=w, h=0.36)


def _call(ax, x, y, w, h, number):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05",
                                facecolor="none", edgecolor=RED, linewidth=1.0, linestyle=(0, (2, 1.2))))
    ax.add_patch(Circle((x + 0.16, y + h - 0.16), 0.11, facecolor="white", edgecolor=INK, lw=0.6))
    ax.text(x + 0.16, y + h - 0.16, str(number), ha="center", va="center", fontsize=6, color=INK)


def _panel(ax, title):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=8, color=INK, pad=2)


def render_intro():
    fig, ax = plt.subplots(figsize=(7.16, 2.7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.2, 3.5), 3.2, 1.4, boxstyle="round,pad=0.04", facecolor="#F7F4EE", edgecolor=INK, lw=0.8))
    ax.text(1.8, 4.45, "prepare_merge_plan", ha="center", fontsize=8, color=INK)
    ax.text(1.8, 3.95, "select (k, h) before merge", ha="center", fontsize=7, color=MUTED)
    ax.annotate("", xy=(5.0, 4.2), xytext=(3.5, 4.2), arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
    ax.text(4.2, 4.45, "then", fontsize=6, color=MUTED, ha="center")
    ax.text(0.3, 3.05, "Phase 1  ListwiseRank on each chunk of at most m", fontsize=8, color=INK)
    chunks = [("12 3 16 7", "3 7 12 16"), ("5 14 1 6", "1 5 6 14"), ("11 2 15 8", "2 8 11 15"), ("9 13 4 10", "4 9 10 13")]
    for i, (raw, run) in enumerate(chunks):
        x = 0.3 + i * 3.4
        _call(ax, x, 1.35, 3.0, 1.35, i + 1)
        ax.text(x + 1.5, 2.35, "ListwiseRank", ha="center", fontsize=6, color=RED)
        ax.text(x + 0.4, 1.85, raw, fontsize=6, color=MUTED)
        ax.text(x + 0.4, 1.5, "run " + run, fontsize=6, color=INK)
    ax.annotate("", xy=(12.6, 0.7), xytext=(6.5, 1.3), arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
    ax.text(10.2, 0.85, "MergeGroup(k, h)", fontsize=7, color=INK)
    _pill(ax, 12.7, 0.45, "Π", BLUE, BLUE, "white", w=0.7)
    _save(fig, "mech-intro.pdf")


def _lanes(ax, items, y, face, edge, text_color=INK, x0=1.7, per=4):
    rows = [items[i : i + per] for i in range(0, max(len(items), 1), per)]
    if not items:
        rows = [["—"]]
        face, edge, text_color = "white", GRAY, MUTED
    for r, row in enumerate(rows):
        _row(ax, x0, y - r * 0.48, row, face, edge, text_color, w=0.7)
    return 0.48 * (len(rows) - 1)


def render_sw():
    rounds = [
        (1, [[3, 7], [1, 5], [2, 8], [4, 9]], [1, 2, 3, 4, 5], [7, 8, 9], [12, 16, 6, 14, 11, 15, 10, 13]),
        (2, [[7, 12], [6, 14], [8, 11], [9, 10]], [6, 7, 8, 9, 10], [11, 12, 14], [16, 15, 13]),
        (3, [[12, 16], [14], [11, 15], [13]], [11, 12, 13, 14, 15, 16], [], []),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(7.16, 4.6))
    for ax, (number, windows, emit, retained, unread) in zip(axes, rounds):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8.2)
        ax.axis("off")
        ax.set_title(f"({chr(96 + number)}) same four runs", loc="left", fontsize=8, color=INK, pad=1)
        ax.add_patch(Circle((0.42, 7.55), 0.24, facecolor="white", edgecolor=INK, lw=0.8, zorder=3))
        ax.text(0.42, 7.55, str(number), ha="center", va="center", fontsize=8, color=INK, zorder=4)
        ax.text(1.15, 7.55, "ListwiseRank", va="center", fontsize=8, color=RED)
        ax.add_patch(FancyBboxPatch((0.25, 4.55), 9.4, 2.55, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor="none", edgecolor=RED, linewidth=1.0, linestyle=(0, (2, 1.2))))
        y = 6.55
        for run, window in enumerate(windows, start=1):
            ax.text(0.55, y, f"R{run}", fontsize=7, color=MUTED, va="center")
            _row(ax, 1.7, y, window, "white", GRAY, w=0.78)
            y -= 0.55
        ax.text(0.15, 3.85, "out", fontsize=7, color=BLUE, va="center")
        _lanes(ax, emit, 3.85, BLUE, BLUE, "white", x0=2.3, per=4)
        ax.text(0.15, 2.55, "keep", fontsize=7, color=MUTED, va="center")
        _lanes(ax, retained, 2.55, "#D5D8DC", GRAY, x0=2.3, per=4)
        ax.text(0.15, 1.25, "unread", fontsize=7, color=MUTED, va="center")
        _lanes(ax, unread, 1.25, "white", GRAY, x0=2.8, per=4)
    _save(fig, "mech-sw.pdf")


def _tree(ax, pointer, winner, loser, gutter_left, gutter_right, filled_right=None):
    ax.plot([5, 3.1], [3.55, 2.35], color=GRAY, lw=0.8, zorder=1)
    ax.plot([5, 6.9], [3.55, 2.35], color=GRAY, lw=0.8, zorder=1)
    ax.text(3.1, 1.95, "child 0", ha="center", fontsize=6, color=MUTED)
    ax.text(6.9, 1.95, "child 1", ha="center", fontsize=6, color=MUTED)
    if pointer == "child1":
        ax.annotate("", xy=(6.75, 2.4), xytext=(5.2, 3.4), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3))
    elif pointer == "child0":
        ax.annotate("", xy=(3.25, 2.4), xytext=(4.8, 3.4), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3))
    if winner:
        _row(ax, 4.55, 4.55, winner, "white", BLUE, BLUE)
    if loser:
        _row(ax, 4.55, 3.85, loser, "#D5D8DC", GRAY)
    ax.text(1.6, 1.15, "unread 0", fontsize=6, color=MUTED, ha="center")
    _row(ax, 1.15, 0.65, gutter_left or ["—"], "white", GRAY)
    ax.text(8.2, 1.15, "unread 1", fontsize=6, color=MUTED, ha="center")
    _row(ax, 7.7, 0.65, gutter_right or ["—"], "white", GRAY)
    if filled_right:
        ax.text(5, 1.55, "fill " + " ".join(map(str, filled_right)), fontsize=6, color=INK, ha="center")


def _band(ax, title):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=7.5, color=INK, pad=2)
    ax.plot([3.2, 2.0], [3.3, 2.15], color="#C5CED4", lw=0.9, zorder=0)
    ax.plot([3.2, 4.4], [3.3, 2.15], color="#C5CED4", lw=0.9, zorder=0)
    ax.text(2.0, 1.75, "child 0", ha="center", fontsize=6.5, color=MUTED)
    ax.text(4.4, 1.75, "child 1", ha="center", fontsize=6.5, color=MUTED)


def _arrow(ax, side, color=INK, lw=1.6):
    if side == 1:
        ax.annotate("", xy=(4.25, 2.2), xytext=(3.35, 3.15), arrowprops=dict(arrowstyle="-|>", color=color, lw=lw))
    elif side == 0:
        ax.annotate("", xy=(2.15, 2.2), xytext=(3.05, 3.15), arrowprops=dict(arrowstyle="-|>", color=color, lw=lw))


def _gutter(ax, left, right):
    ax.text(7.1, 2.35, "unread 0", fontsize=6, color=MUTED)
    _row(ax, 7.1, 1.85, left, "white", GRAY, w=0.62)
    ax.text(7.1, 1.15, "unread 1", fontsize=6, color=MUTED)
    _row(ax, 7.1, 0.65, right, "white", GRAY, w=0.62)


def render_pointer():
    fig_a, ax_a = plt.subplots(2, 2, figsize=(7.16, 5.6))
    fig_b, ax_b = plt.subplots(2, 2, figsize=(7.16, 5.6))
    axes = list(ax_a.ravel()) + list(ax_b.ravel())
    specs = [
        "(a) slots seated",
        "(b) call 1 order",
        "(c) slot 1 reaches h",
        "(d) write pointer = 1",
        "(e) fill child 1 only",
        "(f) call 2 order",
        "(g) slot 0 reaches h",
        "(h) write pointer = 0",
    ]
    for ax, title in zip(axes, specs):
        _band(ax, title)
    a, b, c, d, e, f, g, h = axes
    a.text(0.3, 5.5, "slot 0", fontsize=6.5, color=MUTED)
    _row(a, 0.3, 4.9, [3, 7], "white", INK)
    a.text(0.3, 4.2, "slot 1", fontsize=6.5, color=MUTED)
    _row(a, 0.3, 3.6, [1, 5], "white", INK)
    _gutter(a, [12, 16], [6, 14])
    b.text(0.25, 5.3, "ListwiseRank", fontsize=7, color=RED)
    _row(b, 0.3, 4.6, [1, 3, 5, 7], "white", RED)
    b.text(0.3, 3.9, "real items only", fontsize=6, color=MUTED)
    _gutter(b, [12, 16], [6, 14])
    c.text(0.25, 5.35, "count on slot 1 hits h at 5", fontsize=6.5, color=RED)
    _row(c, 0.3, 4.6, [1, 3], "white", GRAY)
    _pill(c, 2.15, 4.6, "5", "#F8E8E6", RED, RED, w=0.62, h=0.36)
    ax_tick = c
    ax_tick.plot([2.15, 2.15], [4.28, 4.05], color=RED, lw=1.2)
    ax_tick.text(2.15, 3.8, "exhaust", ha="center", fontsize=6, color=RED)
    _row(c, 2.95, 4.6, [7], "white", GRAY)
    c.text(0.3, 3.2, "pointer still unset", fontsize=6.5, color=MUTED)
    _gutter(c, [12, 16], [6, 14])
    _arrow(d, 1)
    d.text(0.25, 5.45, "was unset", fontsize=6.5, color=MUTED)
    d.text(0.25, 5.05, "now child 1", fontsize=6.5, color=INK)
    _row(d, 0.3, 4.35, [1, 3], "white", BLUE, BLUE)
    _row(d, 0.3, 3.7, [5, 7], "#D5D8DC", GRAY)
    _gutter(d, [12, 16], [6, 14])
    _arrow(e, 1, color=GRAY, lw=1.0)
    e.text(0.25, 5.4, "only run 1 is filled", fontsize=6.5, color=INK)
    _row(e, 0.3, 4.6, [6, 14], "white", INK)
    e.text(0.3, 4.0, "run 0 stays unread", fontsize=6.5, color=MUTED)
    _gutter(e, [12, 16], ["—"])
    f.text(0.25, 5.35, "ListwiseRank", fontsize=7, color=RED)
    f.text(0.25, 4.9, "slot0 5 7   slot1 6 14", fontsize=6.5, color=MUTED)
    _row(f, 0.3, 4.2, [5, 6, 7, 14], "white", RED)
    _arrow(f, 1, color=GRAY, lw=1.0)
    _gutter(f, [12, 16], ["—"])
    g.text(0.25, 5.4, "count on slot 0 hits h at 7", fontsize=6.5, color=RED)
    _row(g, 0.3, 4.6, [5, 6], "white", GRAY)
    _pill(g, 2.15, 4.6, "7", "#F8E8E6", RED, RED, w=0.62, h=0.36)
    g.plot([2.15, 2.15], [4.28, 4.05], color=RED, lw=1.2)
    g.text(2.15, 3.8, "exhaust", ha="center", fontsize=6, color=RED)
    _row(g, 2.95, 4.6, [14], "white", GRAY)
    _arrow(g, 1, color=GRAY, lw=1.0)
    g.text(5.3, 5.2, "old pointer\nstill child 1", fontsize=6, color=MUTED)
    _gutter(g, [12, 16], ["—"])
    _arrow(h, 0)
    h.text(0.25, 5.45, "was child 1", fontsize=6.5, color=MUTED)
    h.text(0.25, 5.05, "now child 0", fontsize=6.5, color=INK)
    _row(h, 0.3, 4.35, [5, 6], "white", BLUE, BLUE)
    _row(h, 0.3, 3.7, [7, 14], "#D5D8DC", GRAY)
    _gutter(h, [12, 16], ["—"])
    _save(fig_a, "mech-pointer-a.pdf")
    _save(fig_b, "mech-pointer-b.pdf")


def render_lt():
    fig, ax = plt.subplots(figsize=(7.16, 2.6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    ax.text(0.2, 4.2, "One LT procedure for every h ≥ 1.  h = 1 is the same generator, one real item per segment.", fontsize=8, color=INK)
    ax.plot([1.6, 0.7], [2.5, 1.3], color=GRAY, lw=0.8)
    ax.plot([1.6, 2.5], [2.5, 1.3], color=INK, lw=1.6)
    _pill(ax, 1.6, 3.15, "3  4", "white", BLUE, BLUE, w=0.8)
    _pill(ax, 1.6, 2.45, "5  6", "#D5D8DC", GRAY, w=0.8)
    ax.text(0.2, 0.55, "ListwiseRank of the real path items", fontsize=7, color=RED)
    ax.add_patch(FancyBboxPatch((0.15, 0.35), 3.6, 0.55, boxstyle="round,pad=0.02", facecolor="none", edgecolor=RED, lw=0.8, linestyle=(0, (2, 1.2))))
    ax.annotate("", xy=(2.4, 1.35), xytext=(1.75, 2.2), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3))
    ax.text(5.2, 3.3, "h = 2 segment", fontsize=7, color=INK)
    _row(ax, 5.2, 2.7, [3, 4], "white", BLUE, BLUE)
    ax.text(8.6, 3.3, "h = 1, same chrome", fontsize=7, color=INK)
    _pill(ax, 9.2, 2.7, "3", "white", BLUE, BLUE)
    ax.text(5.2, 1.8, "Thick edge: path being refreshed.", fontsize=7, color=MUTED)
    ax.text(5.2, 1.3, "Blue stroke: transient winner. Blue fill would mean yielded to Π.", fontsize=7, color=MUTED)
    ax.text(5.2, 0.8, "Pointer arrow is not a tree edge.", fontsize=7, color=MUTED)
    _save(fig, "mech-lt.pdf")


def render_virtual():
    fig, ax = plt.subplots(figsize=(7.16, 1.8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 3)
    ax.axis("off")
    ax.text(0.2, 2.6, "Short slot: virtual +∞ counts toward h and is not sent to ListwiseRank", fontsize=8, color=INK)
    ax.text(0.3, 1.9, "slot 0 real", fontsize=6, color=MUTED)
    _pill(ax, 1.5, 1.4, "3", "white", INK)
    ax.text(2.5, 1.4, "+∞", fontsize=8, color=GRAY)
    ax.plot([2.2, 2.8], [1.15, 1.15], color=GRAY, lw=0.8, linestyle=(0, (1, 1)))
    ax.text(4.0, 1.9, "slot 1 real", fontsize=6, color=MUTED)
    _pill(ax, 5.0, 1.4, "1", "white", INK)
    _call(ax, 0.7, 0.9, 4.8, 0.9, 1)
    ax.text(7.0, 1.5, "pointer → child 0\nwinner 1, 3\nloser empty", fontsize=7, color=INK, va="center")
    _save(fig, "mech-virtual.pdf")


def render_limit():
    fig, ax = plt.subplots(figsize=(7.16, 1.9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 3.2)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.3, 1.5), 3.3, 1.2, boxstyle="round,pad=0.03", facecolor="#F7F4EE", edgecolor=INK, lw=0.7))
    ax.text(1.95, 2.1, "mode buffer\nlimit = K", ha="center", va="center", fontsize=7, color=INK)
    ax.annotate("", xy=(5.2, 2.1), xytext=(3.7, 2.1), arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
    ax.add_patch(FancyBboxPatch((5.2, 1.5), 3.6, 1.2, boxstyle="round,pad=0.03", facecolor="white", edgecolor=BLUE, lw=0.9))
    ax.text(7.0, 2.1, "yield until K\nthen stop pulling", ha="center", va="center", fontsize=7, color=BLUE)
    ax.annotate("", xy=(10.4, 2.1), xytext=(8.9, 2.1), arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
    ax.text(10.5, 2.1, "Π_K\nnot Full", fontsize=7, color=INK, va="center")
    ax.text(0.3, 0.7, "SW stops appending at K. LT returns before the next refresh.", fontsize=7, color=MUTED)
    ax.text(0.3, 0.25, "materialize_producer always aclose() in finally, including this early stop.", fontsize=7, color=MUTED)
    _save(fig, "mech-limit.pdf")


def render_all():
    render_intro()
    render_sw()
    render_lt()
    render_pointer()
    render_virtual()
    render_limit()


if __name__ == "__main__":
    render_all()
