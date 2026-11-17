"""Layout figures. Every numeric height is synthetic."""

from __future__ import annotations

import math

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Rectangle

from .exp3 import LT_FIXED, SIZES, SUPPLEMENT, SW_FIXED
from .replay import legal_surface_triangles
from .style import BLUE, FIG, GRAY, GRID, INK, LT, METHOD_NAME, METHOD_STYLE, MUTED, SW, plt

FIG.mkdir(parents=True, exist_ok=True)


def _save(fig, name):
    fig.savefig(FIG / name, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def _surface(family, seed, missing):
    ks = list(range(2, 9))
    hs = list(range(1, 6))
    measured, predicted = {}, {}
    rng = np.random.default_rng(seed)
    for k in ks:
        for h in hs:
            legal = not (k >= 7 and h >= 4) and not (family == "SW" and h > 3 and k > 5)
            if not legal:
                continue
            if (k, h) in missing:
                predicted[(k, h)] = 80 + 4 * k + 6 * h
                continue
            base = 90 + 7 * math.sin(k / 2) + 5 * math.cos(h) + (8 if family == "LT" else -3)
            measured[(k, h)] = base + float(rng.normal(0, 1.5))
            predicted[(k, h)] = base + 6 * math.sin(h + seed) - 2
    return measured, predicted


def _draw_surface(ax, measured, predicted, coincide):
    present = set(measured)
    triangles = legal_surface_triangles(present)
    for tri in triangles:
        xs = [p[0] for p in tri]
        ys = [p[1] for p in tri]
        ax.plot_trisurf(xs, ys, [measured[p] for p in tri], color=BLUE, alpha=0.35, linewidth=0.2, edgecolor=BLUE, shade=False)
    pred_present = set(predicted) & present
    for tri in legal_surface_triangles(pred_present):
        xs = [p[0] for p in tri]
        ys = [p[1] for p in tri]
        ax.plot_trisurf(xs, ys, [predicted[p] for p in tri], color="#E09A3E", alpha=0.22, linewidth=0.2, edgecolor="#E09A3E", shade=False)
    mx, my, mz = [], [], []
    for (k, h), z in measured.items():
        mx.append(k); my.append(h); mz.append(z)
    ax.scatter(mx, my, mz, s=8, c=BLUE, depthshade=False, zorder=4)
    if not measured:
        return
    best = min(measured, key=measured.get)
    pred_choice = min(predicted, key=predicted.get)
    if pred_choice not in measured:
        pred_choice = best if coincide else max(measured, key=measured.get)
    if coincide:
        pred_choice = best
    ax.scatter([best[0]], [best[1]], [measured[best]], marker="*", s=70, c=BLUE, depthshade=False, zorder=6)
    ax.scatter([pred_choice[0]], [pred_choice[1]], [measured[pred_choice]], marker="D", s=28, facecolors="none", edgecolors="#E09A3E", linewidths=1.1, depthshade=False, zorder=7)
    ax.set_xlabel("k")
    ax.set_ylabel("h")
    ax.set_zlabel("input tokens, synthetic")
    ax.view_init(elev=26, azim=-54)
    ax.set_proj_type("ortho")
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.fill = False
        axis.pane.set_edgecolor(GRID)


def render_surfaces():
    specs = [
        ("exp2-2x2.pdf", [("SW", "Full", 1, False), ("LT", "Full", 2, True), ("SW", "LIMIT10", 3, False), ("LT", "LIMIT10", 4, False)], (2, 2), (7.16, 6.3)),
        ("exp2-2x3.pdf", [("SW", "short slot", 5, False), ("SW", "mid slot", 6, True), ("SW", "long slot", 7, False), ("LT", "short slot", 8, False), ("LT", "mid slot", 9, False), ("LT", "long slot", 10, False)], (2, 3), (7.16, 5.4)),
    ]
    for name, panels, shape, size in specs:
        fig = plt.figure(figsize=size)
        for index, (family, mode, seed, coincide) in enumerate(panels, start=1):
            ax = fig.add_subplot(shape[0], shape[1], index, projection="3d")
            missing = {(6, 2)} if index == 1 else set()
            measured, predicted = _surface(family, seed, missing)
            _draw_surface(ax, measured, predicted, coincide)
            ax.set_title(f"{family}, {mode}", color=INK, fontsize=8, pad=0)
        fig.legend(handles=[
            Line2D([0], [0], color=BLUE, lw=4, alpha=0.5, label="Measured placeholder"),
            Line2D([0], [0], color="#E09A3E", lw=4, alpha=0.6, label="Predicted placeholder"),
            Line2D([0], [0], marker="*", color=BLUE, lw=0, label="Measured minimum"),
            Line2D([0], [0], marker="D", markerfacecolor="none", markeredgecolor="#E09A3E", lw=0, label="Predicted pick at its measured height"),
        ], loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.02), fontsize=7)
        fig.tight_layout(rect=(0, 0, 1, 0.94))
        _save(fig, name)


def _series(kh, family, mode):
    k, h = kh
    values = []
    for n in SIZES:
        raw = (n / 1000) * (40 + (k % 7) * 3 - h) + (12 if family == "LT" else 0) + (5 if mode == "LIMIT10" else 0)
        values.append(raw + (8 if n == 5000 and k % 2 == 0 else -4))
    return values


def render_exp3():
    panels = [("SW", "Full", SW_FIXED), ("LT", "Full", LT_FIXED), ("SW", "LIMIT10", SW_FIXED), ("LT", "LIMIT10", LT_FIXED)]
    for name, shape, size in (("exp3-2x2.pdf", (2, 2), (7.16, 5.2)), ("exp3-row.pdf", (1, 4), (7.16, 2.5))):
        fig, axes = plt.subplots(*shape, figsize=size, sharex=True)
        flat = axes.ravel()
        for ax, (family, mode, pairs) in zip(flat, panels):
            for index, kh in enumerate(pairs):
                ys = _series(kh, family, mode)
                pred = [y * (0.92 + 0.03 * index) for y in ys]
                ax.plot(SIZES, pred, color=plt.cm.tab10(index), lw=1.0, ls="--")
                ax.plot(SIZES, ys, color=plt.cm.tab10(index), lw=1.1, marker="o", ms=3, label=f"({kh[0]},{kh[1]})")
            if family == "LT":
                for row in SUPPLEMENT:
                    if row["mode"] != mode:
                        continue
                    y = _series(row["kh"], "LT", mode)[SIZES.index(row["n"])] * 0.75
                    ax.scatter([row["n"]], [y], marker="*", s=40, c=INK, zorder=5)
                    ax.annotate(f"sup {row['kh'][0]},{row['kh'][1]}", (row["n"], y), textcoords="offset points", xytext=(3, 3), fontsize=6, color=INK)
            ax.set_title(f"{family} {mode}", color=INK, fontsize=8)
            ax.set_xticks(SIZES)
            ax.set_xticklabels(["1k", "5k", "10k"])
            ax.grid(color=GRID, lw=0.4)
            ax.legend(frameon=False, fontsize=5.5, ncol=2, loc="upper left")
        flat[0].set_ylabel("synthetic input tokens")
        fig.tight_layout()
        _save(fig, name)


def render_exp4a():
    labels = ["(2,1)", "(2,2)", "(4,1)", "(4,3)", "(8,1)", "(8,2)"]
    groups = [(0, 2, "k=2"), (2, 4, "k=4"), (4, 6, "k=8")]
    x = np.arange(len(labels))
    off = np.array([120, 110, np.nan, 90, 130, 100], dtype=float)
    on = np.array([100, 95, 80, 88, 110, 92], dtype=float)
    fig, axes = plt.subplots(2, 2, figsize=(7.16, 4.6), sharex=True)
    roles = {"Off pred": (1, off[1]), "Off measured": (5, off[5]), "On pred": (3, on[3]), "On measured": (2, on[2])}
    for ax, title in zip(axes.ravel(), ["SW Full n=100", "SW LIMIT10 n=100", "LT Full n=500", "LT LIMIT10 n=500"]):
        ax.plot(x, off, color=SW, marker="o", lw=1.1, label="Off = U")
        ax.plot(x, on, color=LT, marker="s", lw=1.1, label="On-cold = U−Q")
        ax.scatter([roles["Off pred"][0]], [roles["Off pred"][1]], marker="D", c=SW, s=28, zorder=4)
        ax.scatter([roles["Off measured"][0]], [roles["Off measured"][1]], marker="*", c=SW, s=50, zorder=4)
        ax.scatter([roles["On pred"][0], roles["On measured"][0]], [roles["On pred"][1], roles["On measured"][1]], marker="D", facecolors="none", edgecolors=LT, s=36, zorder=4)
        ax.scatter([roles["On measured"][0]], [roles["On measured"][1]], marker="*", c=LT, s=36, zorder=5)
        for start, end, text in groups:
            ax.axvspan(start - 0.5, end - 0.5, color=GRID, alpha=0.35, lw=0)
            ax.text((start + end - 1) / 2, ax.get_ylim()[0] if False else 70, text, ha="center", fontsize=6, color=MUTED)
        ax.set_title(title, fontsize=8, color=INK)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.grid(axis="y", color=GRID, lw=0.4)
    axes[0, 0].legend(frameon=False, fontsize=6)
    axes[0, 0].set_ylabel("synthetic equivalent input")
    axes[1, 0].set_ylabel("synthetic equivalent input")
    fig.tight_layout()
    _save(fig, "exp4a.pdf")


def render_exp4b():
    configs = [("2,1", 100, 40), ("2,2", 90, 20), ("4,1", 80, 55), ("4,3", 110, 10), ("8,1", 70, 30)]
    betas = [0, 0.25, 0.5, 0.75, 1]
    fig, ax = plt.subplots(figsize=(7.16, 3.3))
    xs = np.arange(len(configs))
    colors = ["#1F6F8B", "#3E8C6E", "#C47B2B", "#8C4A4A", "#3D5A80"]
    for beta, color in zip(betas, colors):
        ys = [u - (1 - beta) * q for _name, u, q in configs]
        ax.plot(xs, ys, marker="o", ms=3, lw=1.1, color=color, label=f"β={beta}")
        best = int(np.argmin(ys))
        pred = (best + 1) % len(ys)
        ax.scatter([best], [ys[best]], marker="*", s=40, c=color, zorder=4)
        ax.scatter([pred], [ys[pred]], marker="D", s=18, facecolors="none", edgecolors=color, zorder=4)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"({name})" for name, _u, _q in configs])
    ax.set_ylabel("U−(1−β)Q, synthetic")
    ax.grid(color=GRID, lw=0.4)
    ax.legend(frameon=False, ncol=5, fontsize=7, loc="upper right")
    inset = fig.add_axes([0.62, 0.52, 0.28, 0.32])
    for beta, color in zip(betas, colors):
        ys = [u - (1 - beta) * q for _name, u, q in configs]
        inset.plot(xs[2:4], ys[2:4], color=color, marker="o", ms=3, lw=1)
    inset.set_title("local", fontsize=6, color=MUTED)
    inset.tick_params(labelsize=6)
    fig.tight_layout()
    _save(fig, "exp4b.pdf")


def render_exp4c():
    rng = np.random.default_rng(4)
    methods = list(METHOD_STYLE)
    for mode, ylabel, name in (("Full", "synthetic Spearman", "exp4c-full.pdf"), ("LIMIT10", "synthetic NDCG@10", "exp4c-limit.pdf")):
        fig, axes = plt.subplots(2, 2, figsize=(7.16, 5.4), sharex=True, sharey=True)
        for row, dataset in enumerate(("DL20 slot", "COVID slot")):
            base = {method: (20 + 8 * i + float(rng.normal(0, 1)), 0.35 + 0.04 * ((i * 3) % 7) / 6) for i, method in enumerate(methods)}
            for col, (state, shift) in enumerate((("Off", 0), ("On-cold", -6))):
                ax = axes[row, col]
                for method in methods:
                    x, y = base[method]
                    x = x + shift + (2 if state == "On-cold" and method == "lt" else 0)
                    y = y + (0.02 if state == "On-cold" and method == "sw" else -0.01)
                    color, marker = METHOD_STYLE[method]
                    ax.scatter([x], [y], c=color, marker=marker, s=28, zorder=3)
                    ax.annotate(METHOD_NAME[method], (x, y), textcoords="offset points", xytext=(4, 3), fontsize=5.5, color=INK)
                ax.set_title(f"{dataset}, {state}, {mode}", fontsize=8, color=INK)
                ax.grid(color=GRID, lw=0.4)
                ax.set_xlim(10, 110)
                ax.set_ylim(0.25, 0.85)
        axes[1, 0].set_xlabel("equivalent tokens, β=0, output weight 1")
        axes[1, 1].set_xlabel("equivalent tokens, β=0, output weight 1")
        axes[0, 0].set_ylabel(ylabel)
        axes[1, 0].set_ylabel(ylabel)
        fig.tight_layout()
        _save(fig, name)


def render_exp5():
    labels = ["10", "20", "50", "100", "200", "300", "400", "490", "L500", "Full"]
    x = np.arange(len(labels))
    limit_x = x[:-1]
    for state, name in (("Off", "exp5-off.pdf"), ("On-cold", "exp5-on.pdf")):
        fig, axes = plt.subplots(2, 2, figsize=(7.16, 4.8), sharex=True)
        for col, dataset in enumerate(("DL20 slot", "COVID slot")):
            for family, color, sign in (("SW", SW, 1), ("LT", LT, -1)):
                cost = 30 + sign * 4 + np.linspace(0, 18, len(limit_x)) + (3 if state == "On-cold" else 0) * sign
                if dataset.startswith("COVID"):
                    cost = cost[::-1] * 0.8 + 20
                ndcg = 0.45 + sign * 0.04 + np.linspace(0, 0.08, len(limit_x))
                axc, axq = axes[0, col], axes[1, col]
                axc.plot(limit_x, cost, color=color, marker="o", ms=3, lw=1.1, label=family)
                axc.scatter([x[-1]], [cost[-1] + 6 * sign], color=color, marker="s", s=22, zorder=4)
                axq.plot(limit_x, ndcg, color=color, marker="o", ms=3, lw=1.1)
                axq.scatter([x[-1]], [min(0.9, ndcg[-1] + 0.03)], color=color, marker="s", s=22)
            for ax in (axes[0, col], axes[1, col]):
                ax.axvline(8.5, color=GRAY, lw=0.6, ls="--")
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=6)
                ax.grid(color=GRID, lw=0.4)
            axes[0, col].set_title(f"{state}, {dataset}", fontsize=8, color=INK)
        axes[0, 0].set_ylabel("synthetic equivalent input")
        axes[1, 0].set_ylabel("synthetic NDCG@10")
        axes[0, 0].legend(frameon=False, fontsize=7)
        fig.tight_layout()
        _save(fig, name)


def render_all():
    render_surfaces()
    render_exp3()
    render_exp4a()
    render_exp4b()
    render_exp4c()
    render_exp5()


if __name__ == "__main__":
    render_all()
