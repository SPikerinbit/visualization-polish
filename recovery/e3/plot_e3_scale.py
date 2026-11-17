"""Draw the E3 fixed-(k, h) scale figure from the synthetic layout table.

Page width is the double-column measure, 178 mm. The file is a vector figure
for \\includegraphics, not a compiled paper and not a standalone exhibit.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "e3_layout_data.json"
PDF = ROOT / "e3-scale.pdf"
PNG = ROOT / "e3-scale.png"

WIDTH_MM = 178.0
HEIGHT_MM = 136.0
INK = "#1A1A1A"
SPINE = "#222222"
MUTED = "#333333"

font_manager.fontManager.addfont(
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
)
font_manager.fontManager.addfont(
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
)

plt.rcParams.update(
    {
        "font.family": "Liberation Serif",
        "font.size": 8,
        "axes.labelsize": 8.5,
        "axes.titlesize": 8.5,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "axes.edgecolor": SPINE,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "axes.spines.top": True,
        "axes.spines.right": True,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    }
)


def _load() -> dict:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    if payload.get("kind") != "synthetic_layout_only":
        raise SystemExit("refusing to draw: layout table is not marked synthetic")
    return payload


def _style_handles() -> list:
    return [
        Line2D(
            [0],
            [0],
            color=INK,
            lw=1.45,
            marker="o",
            ms=4.2,
            label="Measured layout",
        ),
        Line2D(
            [0],
            [0],
            color=INK,
            lw=1.15,
            ls=(0, (4, 2)),
            label="Predicted layout",
        ),
        Line2D(
            [0],
            [0],
            color=INK,
            lw=0,
            marker="*",
            ms=9,
            markerfacecolor="white",
            markeredgecolor=INK,
            markeredgewidth=0.8,
            label="Supplement, not a fixed series",
        ),
    ]


def _series_handles(series: list) -> list:
    handles = []
    for row in series:
        handles.append(
            Line2D(
                [0],
                [0],
                color=row["color"],
                lw=1.45,
                marker="o",
                ms=3.6,
                label=f"({row['k']}, {row['h']})",
            )
        )
    return handles


def _draw_panel(ax, panel: dict, sizes: list) -> None:
    for row in panel["series"]:
        color = row["color"]
        ax.plot(
            sizes,
            row["predicted"],
            color=color,
            lw=1.15,
            ls=(0, (4, 2)),
            solid_capstyle="round",
            zorder=1,
        )
        ax.plot(
            sizes,
            row["measured"],
            color=color,
            lw=1.45,
            ls="-",
            marker="o",
            ms=4.2,
            markerfacecolor=color,
            markeredgecolor=color,
            markeredgewidth=0.4,
            zorder=3,
        )
    for star in panel["supplements"]:
        if star.get("joined"):
            raise SystemExit("refusing to draw a joined supplement")
        ax.scatter(
            [star["n"]],
            [star["y"]],
            marker="*",
            s=86,
            facecolors="white",
            edgecolors=INK,
            linewidths=0.8,
            zorder=5,
        )
        # 10k sits on the right spine; keep that label inside the axes.
        if star["n"] >= 10000:
            offset = (-8, 4)
            align = "right"
        else:
            offset = (8, 4)
            align = "left"
        ax.annotate(
            f"({star['k']}, {star['h']})",
            (star["n"], star["y"]),
            textcoords="offset points",
            xytext=offset,
            ha=align,
            va="bottom",
            fontsize=7.5,
            color=INK,
            zorder=6,
        )
    mode = "LIMIT 10" if panel["mode"] == "LIMIT10" else "Full"
    ax.set_title(f"{panel['family']}, {mode}", pad=3.5, fontweight="regular")
    ax.set_xlim(400, 11200)
    ax.set_xticks(sizes)
    ax.set_xticklabels(["1k", "5k", "10k"])
    ax.set_ylim(8, 82)
    ax.set_yticks([20, 40, 60])
    ax.tick_params(length=3.0, width=0.6, pad=2)
    ax.grid(False)


def _overlaps(fig) -> list[tuple[str, str, float]]:
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    items = []
    seen = set()
    for text in fig.findobj(plt.Text):
        if id(text) in seen:
            continue
        seen.add(id(text))
        content = text.get_text().strip()
        if not content:
            continue
        box = text.get_window_extent(renderer).expanded(1.0, 1.0)
        if box.width < 2 or box.height < 2:
            continue
        items.append((content, box))
    hits = []
    for i, (left, a) in enumerate(items):
        for right, b in items[i + 1 :]:
            if not a.overlaps(b):
                continue
            width = min(a.x1, b.x1) - max(a.x0, b.x0)
            height = min(a.y1, b.y1) - max(a.y0, b.y0)
            area = max(0.0, width) * max(0.0, height)
            if area >= 8:
                hits.append((left, right, round(area, 1)))
    return hits


def draw() -> None:
    payload = _load()
    sizes = payload["x"]["values"]
    if payload["x"]["scale"] != "linear":
        raise SystemExit("refusing to draw: x scale is not the linear checkpoint")
    width = WIDTH_MM / 25.4
    height = HEIGHT_MM / 25.4
    fig = plt.figure(figsize=(width, height))
    grid = fig.add_gridspec(
        2,
        2,
        left=0.078,
        right=0.985,
        bottom=0.095,
        top=0.690,
        wspace=0.20,
        hspace=0.38,
    )
    first = fig.add_subplot(grid[0, 0])
    axes = [
        first,
        fig.add_subplot(grid[0, 1], sharex=first, sharey=first),
        fig.add_subplot(grid[1, 0], sharex=first, sharey=first),
        fig.add_subplot(grid[1, 1], sharex=first, sharey=first),
    ]
    for ax, panel in zip(axes, payload["panels"]):
        _draw_panel(ax, panel, sizes)
        ax.tick_params(labelbottom=True, labelleft=True)
    axes[0].set_ylabel("Layout units")
    axes[2].set_ylabel("Layout units")
    axes[2].set_xlabel("Input size n")
    axes[3].set_xlabel("Input size n")

    fig.text(
        0.50,
        0.985,
        "Synthetic layout only. Not a measured result.",
        ha="center",
        va="top",
        fontsize=9,
        fontweight="bold",
        color=INK,
    )
    legend_kw = dict(
        loc="upper center",
        frameon=False,
        fontsize=8,
        borderaxespad=0.0,
        borderpad=0.15,
        labelspacing=0.25,
    )
    style = fig.legend(
        handles=_style_handles(),
        bbox_to_anchor=(0.53, 0.955),
        ncol=3,
        handlelength=2.6,
        columnspacing=1.15,
        **legend_kw,
    )
    sw = fig.legend(
        handles=_series_handles(payload["panels"][0]["series"]),
        bbox_to_anchor=(0.53, 0.900),
        ncol=5,
        title="SW  (k, h)",
        title_fontsize=8,
        handlelength=1.8,
        columnspacing=0.9,
        **legend_kw,
    )
    lt = fig.legend(
        handles=_series_handles(payload["panels"][1]["series"]),
        bbox_to_anchor=(0.53, 0.815),
        ncol=5,
        title="LT  (k, h)",
        title_fontsize=8,
        handlelength=1.8,
        columnspacing=0.9,
        **legend_kw,
    )
    for legend in (style, sw, lt):
        legend.get_title().set_color(INK)
        for text in legend.get_texts():
            text.set_color(INK)

    hits = _overlaps(fig)
    if hits:
        for left, right, area in hits:
            print(f"OVERLAP {area}: {left!r} x {right!r}")
        raise SystemExit(f"{len(hits)} label overlaps")
    renderer = fig.canvas.get_renderer()
    for ax in axes:
        box = ax.get_window_extent(renderer)
        for text in ax.texts:
            label_box = text.get_window_extent(renderer)
            if not box.contains(label_box.x0, label_box.y0) or not box.contains(
                label_box.x1, label_box.y1
            ):
                raise SystemExit(f"label outside axes: {text.get_text()!r}")

    fig.savefig(PDF, format="pdf")
    fig.savefig(PNG, format="png", dpi=300)
    plt.close(fig)
    print(PDF)
    print(PNG)


if __name__ == "__main__":
    draw()
