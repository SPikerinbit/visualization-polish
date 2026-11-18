"""E4b: one single-column beta sweep. No color bands and no inset.

U and Q are the existing synthetic slice, copied unchanged. Costs are
U-(1-beta)Q. Markers sit on that measured cost. This slice is not an
n=100 sample: (8, 1) and (8, 2) are legal only when the run count is at
least 8 (n=500, m=20 gives 25 runs).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from legal import is_legal
from pdfutil import configure_matplotlib, overflow_labels, overlapping_tick_labels
from style import COLUMN_PT, GRID_RGB, TABLEAU, pt_to_in, printed

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[1] / "recovery" / "e4b" / "e4b_beta.json"

LINE_PT = printed(1.6, 0.33)
GRID_PT = printed(0.765, 0.33)
SPINE_PT = printed(1.36, 0.33)
TICK_W = printed(0.8, 0.33)
TICK_LEN = max(printed(2.2, 0.33), 2.0)
STAR_PT = printed(10.2, 0.33)
DIAMOND_PT = printed(9.49, 0.33)
TICK_FONT = 6.4
LABEL_FONT = 7.2

BETAS = (0.0, 0.25, 0.5, 0.75, 1.0)
LINESTYLES = ("-", "--", "-.", (0, (1.2, 0.9)), (0, (3.2, 1.0, 0.7, 1.0)))


def load() -> dict:
    payload = json.loads(SOURCE.read_text())
    if payload["status"] != "synthetic_layout_sample":
        raise RuntimeError("unexpected E4b status")
    configs = [(c["k"], c["h"], c["U"], c["Q"]) for c in payload["configs"]]
    if [c[:2] for c in configs] != [(2, 1), (2, 2), (4, 1), (4, 2), (4, 3), (8, 1), (8, 2)]:
        raise RuntimeError("E4b categories changed")
    for k, h, _u, _q in configs:
        if not is_legal("SW", k, h, n=500) or not is_legal("LT", k, h, n=500):
            raise RuntimeError(f"E4b category {(k, h)} is illegal at n=500")
        if is_legal("SW", k, h, n=100) and k >= 8:
            raise RuntimeError("k=8 must not be described as legal at n=100")
    return payload


def costs(payload) -> dict[float, np.ndarray]:
    out = {}
    for beta in BETAS:
        values = []
        for config in payload["configs"]:
            values.append(config["U"] - (1.0 - beta) * config["Q"])
        out[beta] = np.asarray(values, dtype=float)
    for beta, key in ((0.0, "0"), (0.25, "0.25"), (0.5, "0.5"), (0.75, "0.75"), (1.0, "1")):
        measured = payload["expected_measured"][key]
        labels = [(c["k"], c["h"]) for c in payload["configs"]]
        idx = labels.index((measured["k"], measured["h"]))
        if int(np.argmin(out[beta])) != idx:
            raise RuntimeError(f"beta {beta} minimum is not the recorded measured role")
    return out


def draw(payload, series: dict[float, np.ndarray]) -> plt.Figure:
    labels = [(c["k"], c["h"]) for c in payload["configs"]]
    values = np.concatenate(list(series.values()))
    pad = 0.08 * (values.max() - values.min())
    ylim = (values.min() - pad, values.max() + pad)
    fig = plt.figure(figsize=(pt_to_in(COLUMN_PT), pt_to_in(168)))
    ax = fig.add_axes([0.16, 0.20, 0.80, 0.62])
    ax.set_xlim(-0.4, len(labels) - 0.6)
    ax.set_ylim(*ylim)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([f"({k},{h})" for k, h in labels])
    ax.set_axisbelow(True)
    ax.grid(True, color=GRID_RGB, linewidth=GRID_PT, zorder=0)
    ax.set_facecolor("white")
    for spine in ax.spines.values():
        spine.set_linewidth(SPINE_PT)
    ax.tick_params(length=TICK_LEN, width=TICK_W, labelsize=TICK_FONT, pad=1.5)
    ax.set_xlabel(r"configuration $(k,h)$", fontsize=LABEL_FONT)
    ax.set_ylabel(r"synthetic $U-(1-\beta)Q$", fontsize=LABEL_FONT)
    handles = []
    for beta, color, linestyle in zip(BETAS, TABLEAU, LINESTYLES):
        y = series[beta]
        ax.plot(
            range(len(labels)),
            y,
            color=color,
            linestyle=linestyle,
            linewidth=LINE_PT,
            zorder=3,
        )
        key = str(beta).rstrip("0").rstrip(".") if beta not in (0.0, 1.0) else str(int(beta) if beta == 1.0 else 0)
        # JSON keys are "0", "0.25", "0.5", "0.75", "1".
        json_key = {0.0: "0", 0.25: "0.25", 0.5: "0.5", 0.75: "0.75", 1.0: "1"}[beta]
        pred = payload["predicted"][json_key]
        meas = payload["expected_measured"][json_key]
        pred_i = labels.index((pred["k"], pred["h"]))
        meas_i = labels.index((meas["k"], meas["h"]))
        if pred_i == meas_i:
            ax.plot([meas_i], [y[meas_i]], ls="none", marker="D", markersize=DIAMOND_PT * 0.62,
                    markerfacecolor=color, markeredgecolor="black", markeredgewidth=0.4, zorder=4)
            ax.plot([pred_i], [y[pred_i]], ls="none", marker="*", markersize=STAR_PT,
                    markerfacecolor=color, markeredgecolor="black", markeredgewidth=0.4, zorder=5)
        else:
            ax.plot([pred_i], [y[pred_i]], ls="none", marker="*", markersize=STAR_PT,
                    markerfacecolor=color, markeredgecolor="black", markeredgewidth=0.4, zorder=5)
            ax.plot([meas_i], [y[meas_i]], ls="none", marker="D", markersize=DIAMOND_PT * 0.62,
                    markerfacecolor=color, markeredgecolor="black", markeredgewidth=0.4, zorder=4)
        handles.append(
            Line2D([0], [0], color=color, lw=LINE_PT, ls=linestyle, label=rf"$\beta={json_key}$")
        )
    handles.extend(
        [
            Line2D([0], [0], color="black", lw=0, marker="*", markersize=7.0, label="Predicted"),
            Line2D([0], [0], color="black", lw=0, marker="D", markersize=4.4, label="Measured"),
        ]
    )
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.55, 0.985),
        ncol=4,
        frameon=False,
        fontsize=6.5,
        handlelength=1.8,
        columnspacing=0.8,
        borderaxespad=0.0,
    )
    if len(fig.axes) != 1:
        raise RuntimeError("E4b drew an extra axes (inset or band axis)")
    problems = overflow_labels(fig) + overlapping_tick_labels(fig)
    if problems:
        raise RuntimeError(f"E4b labels: {problems}")
    return fig


def build(out: Path) -> dict:
    configure_matplotlib()
    out.mkdir(parents=True, exist_ok=True)
    payload = load()
    series = costs(payload)
    fig = draw(payload, series)
    fig.savefig(out / "e4b-beta.pdf")
    fig.savefig(out / "e4b-beta.png", dpi=300)
    plt.close(fig)
    facts = {
        "source": str(SOURCE),
        "betas_drawn": [0, 0.25, 0.5, 0.75, 1],
        "betas_not_drawn": payload["betas_in_contract_not_drawn"],
        "inset": False,
        "color_bands": False,
        "n100_k8": "not used; this slice is not an n=100 sample",
        "values_unchanged": True,
        "line_pt": LINE_PT,
    }
    (out / "e4b-facts.json").write_text(json.dumps(facts, indent=2) + "\n")
    return facts
