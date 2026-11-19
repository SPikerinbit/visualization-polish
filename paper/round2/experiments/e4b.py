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

LINE_PT = 1.0
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
    colors=['#648D9B','#507F90','#3E7185','#2D6077','#204D65']
    marks=['o','s','^','v','+']
    fig=plt.figure(figsize=(pt_to_in(COLUMN_PT),pt_to_in(168)))
    ax=fig.add_axes([.155,.19,.815,.57]);x=np.arange(7)
    labels=[(r['k'],r['h']) for r in payload['configs']]
    vals=np.concatenate(list(series.values()));pad=.08*np.ptp(vals)
    ax.set_ylim(vals.min()-pad,vals.max()+pad);ax.set_xlim(-.4,6.4)
    ax.set_yticks([60,80,100,120,140,160]);ax.set_xticks(x,[f'({k},{h})' for k,h in labels]);ax.tick_params(labelsize=7,width=.5,length=2,pad=2,color='#62727C')
    ax.set_xlabel(r'configuration $(k,h)$',fontsize=7.5,labelpad=4)
    ax.set_ylabel('Synthetic cost (layout units)',fontsize=7.5,labelpad=4)
    ax.set_axisbelow(True);ax.grid(axis='y',color='#E0E4E6',lw=.35)
    for side,s in ax.spines.items():s.set_color('#A1ADB5');s.set_linewidth(.45)
    handles=[];roles=[]
    for beta,c,ls,m in zip(BETAS,colors,LINESTYLES,marks):
     y=series[beta];key=f'{beta:g}'
     ax.plot(x,y,color=c,ls=ls,lw=.9,marker=m,ms=3.0,mfc='white',mec=c,mew=.6,zorder=3)
     pred=payload['predicted'][key];meas=payload['expected_measured'][key]
     pi=labels.index((pred['k'],pred['h']));mi=labels.index((meas['k'],meas['h']))
     # Large open diamond stays visible around the star when both roles coincide.
     ax.plot(pi,y[pi],marker='D',ms=6.2,ls='',mfc='white',mec=c,mew=.85,zorder=5)
     ax.plot(mi,y[mi],marker='*',ms=6,ls='',mfc=c,mec='white',mew=.3,zorder=6)
     handles.append(Line2D([],[],color=c,ls=ls,lw=.9,marker=m,ms=3.0,mfc='white',label=rf'$\beta={key}$'))
     roles.append(dict(beta=beta,predicted_index=pi,minimum_index=mi,predicted_height=float(y[pi]),minimum_height=float(y[mi])))
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.55,.995),ncol=5,fontsize=6.3,frameon=False,handlelength=1.45,columnspacing=.75,handletextpad=.35)
    fig.legend(handles=[Line2D([],[],color='#24495D',marker='D',ms=4,mfc='white',lw=0,label='Predicted config. (placeholder)'),Line2D([],[],color='#24495D',marker='*',ms=6,lw=0,label='Curve minimum')],loc='upper center',bbox_to_anchor=(.55,.90),ncol=2,fontsize=6.1,frameon=False,columnspacing=1.1,handletextpad=.4)
    problems=overflow_labels(fig)+overlapping_tick_labels(fig)
    assert not problems,problems
    return fig


def build(out: Path) -> dict:
    configure_matplotlib()
    out.mkdir(parents=True, exist_ok=True)
    payload = load()
    series = costs(payload)
    fig = draw(payload, series)
    fig.savefig(out / "e4b-beta.pdf")
    fig.savefig(out / "e4b-beta.png", dpi=300)
    fig.savefig(out / "e4b-beta.svg")
    fig.text(.5, -.018, "Synthetic layout sample — not measured", ha="center", fontsize=6.7, color="#59616A")
    fig.savefig(out / "e4b-beta-standalone.pdf", bbox_inches="tight", pad_inches=.03)
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
