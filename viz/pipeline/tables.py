"""Synthetic exp1 sheets and LaTeX. Numbers are layout fuel, not results."""

from __future__ import annotations

import hashlib

from .ranking import average_rank, emphasis, rank_cost, rank_quality

METHODS = [
    ("pointwise", "OrderByLLM Pointwise", "OrderByLLM Pointwise"),
    ("ext_pointwise", "Ext. Pointwise", "Ext. Pointwise"),
    ("bubble", "External Bubble", "External Bubble"),
    ("merge", "External Merge", "External Merge"),
    ("listk", "ListK Sort", "ListK Select"),
    ("tournament", "Tournament", "Tournament"),
    ("lotus", "Lotus Quick", "Lotus Quick"),
    ("setwise", "Setwise Heap", "Setwise Heap"),
    ("sw", "SW", "SW"),
    ("lt", "LT", "LT"),
]
DATASETS = ["Q9", "DL20", "DL22", "COVID", "DBpedia", "Robust04"]
MODELS = ["Qwen3.5-9B", "Qwen3.8-27B"]


def _unit(*parts: object) -> float:
    digest = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return int.from_bytes(digest[:4], "big") / 2**32


def sheet(model: str, mode: str) -> dict:
    """One synthetic model/mode sheet. Overrides plant ties, a rounding trap, and a hole."""
    quality = {}
    tokens = {}
    latency = {}
    for method, _full, _limit in METHODS:
        quality[method] = {}
        tokens[method] = {}
        latency[method] = {}
        for dataset in DATASETS:
            quality[method][dataset] = {
                "mean": round(0.30 + 0.45 * _unit(model, mode, method, dataset, "q"), 6),
                "permutation_std": round(0.008 + 0.04 * _unit(model, mode, method, dataset, "s"), 6),
            }
            tokens[method][dataset] = {
                "mean": 15000 + 200000 * _unit(model, mode, method, dataset, "t"),
                "n_repeats": 1,
                "repeat_variance": None,
            }
            latency[method][dataset] = {
                "mean": 0.8 + 40 * _unit(model, mode, method, dataset, "l"),
                "n_repeats": 1,
                "repeat_variance": None,
            }
    if model == "Qwen3.5-9B" and mode == "full":
        quality["pointwise"]["Q9"] = {"mean": 0.5014, "permutation_std": 0.020}
        quality["ext_pointwise"]["Q9"] = {"mean": 0.5006, "permutation_std": 0.010}
        for method, _full_name, _limit_name in METHODS:
            if method not in {"pointwise", "ext_pointwise"}:
                quality[method]["Q9"]["mean"] = min(quality[method]["Q9"]["mean"], 0.42)
        quality["sw"]["DL20"] = {"mean": 0.620, "permutation_std": 0.030}
        quality["lt"]["DL20"] = {"mean": 0.620, "permutation_std": 0.030}
        quality["bubble"]["DL20"] = {"mean": 0.610, "permutation_std": 0.020}
        for method, _a, _b in METHODS:
            if method not in {"sw", "lt", "bubble"}:
                quality[method]["DL20"]["mean"] = min(quality[method]["DL20"]["mean"], 0.50)
        tokens["sw"]["COVID"]["mean"] = 88000.0
        tokens["lt"]["COVID"]["mean"] = 88000.0
        quality["lt"]["COVID"]["mean"] = max(quality["lt"]["COVID"]["mean"], quality["sw"]["COVID"]["mean"] + 0.05)
        quality["setwise"]["Robust04"] = {"mean": None, "permutation_std": None}
    return {"model": model, "mode": mode, "quality": quality, "tokens": tokens, "latency": latency}


def rank_sheet(data: dict) -> dict:
    per_q, per_t, per_l = {}, {}, {}
    marks = {"quality": {}, "tokens": {}, "latency": {}}
    for dataset in DATASETS:
        q_cells = {m: data["quality"][m][dataset] for m, _a, _b in METHODS}
        q_ranks = rank_quality(q_cells)
        q_means = {m: data["quality"][m][dataset]["mean"] for m, _a, _b in METHODS}
        t_ranks = rank_cost({m: data["tokens"][m][dataset] for m, _a, _b in METHODS}, q_means)
        l_ranks = rank_cost({m: data["latency"][m][dataset] for m, _a, _b in METHODS}, q_means)
        per_q[dataset] = q_ranks
        per_t[dataset] = t_ranks
        per_l[dataset] = l_ranks
        marks["quality"][dataset] = emphasis(q_ranks)
        marks["tokens"][dataset] = emphasis(t_ranks)
        marks["latency"][dataset] = emphasis(l_ranks)
    methods = [m for m, _a, _b in METHODS]
    avg = {
        "quality": {m: average_rank(per_q, m) for m in methods},
        "tokens": {m: average_rank(per_t, m) for m in methods},
        "latency": {m: average_rank(per_l, m) for m in methods},
    }
    avg_marks = {key: emphasis({m: v for m, v in values.items() if v is not None}) for key, values in avg.items()}
    coverage = {m: sum(m in per_q[d] for d in DATASETS) for m in methods}
    return {"per": {"quality": per_q, "tokens": per_t, "latency": per_l}, "marks": marks, "avg": avg, "avg_marks": avg_marks, "coverage": coverage}


def _wrap(text: str, mark: str) -> str:
    if mark == "first":
        return r"\textbf{" + text + "}"
    if mark == "second":
        return r"\underline{" + text + "}"
    return text


def _qtext(cell: dict, style: str) -> str | None:
    if cell["mean"] is None:
        return None
    mean = f"{cell['mean']:.3f}"
    std = cell.get("permutation_std")
    if std is None:
        return mean
    if style == "inline":
        return f"${mean}\\pm{std:.3f}$"
    return f"${mean}_{{\\pm{std:.3f}}}$"


def _num(value: float, kind: str) -> str:
    if kind == "tokens":
        return f"{value / 1000:.1f}"
    return f"{value:.1f}"


def _rank_text(value: float | None) -> str:
    if value is None:
        return "--"
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.1f}"


def latex_table(data: dict, ranked: dict, style: str, datasets: list[str] | None = None, with_ranks: bool = True) -> str:
    datasets = datasets or DATASETS
    mode = data["mode"]
    lines = [
        r"\begin{tabular}{@{}l" + "r" * (3 * len(datasets) + (3 if with_ranks else 0)) + "@{}}",
        r"\toprule",
    ]
    header = ["Method"]
    for dataset in datasets:
        header.append(r"\multicolumn{3}{c}{" + dataset + "}")
    if with_ranks:
        header.append(r"\multicolumn{3}{c}{Avg.\ rank}")
    lines.append(" & ".join(header) + r" \\")
    spans = []
    col = 2
    for _dataset in datasets:
        spans.append(rf"\cmidrule(lr){{{col}-{col+2}}}")
        col += 3
    if with_ranks:
        spans.append(rf"\cmidrule(lr){{{col}-{col+2}}}")
    lines.append(" ".join(spans))
    sub = [""]
    metric = r"$\rho$" if mode == "full" else "NDCG@10"
    for _dataset in datasets:
        sub.extend([metric, r"Tok.", "Lat."])
    if with_ranks:
        sub.extend(["Q", "Tok.", "Lat."])
    lines.append(" & ".join(sub) + r" \\")
    lines.append(r"\midrule")
    for method, full_name, limit_name in METHODS:
        name = full_name if mode == "full" else limit_name
        cells = [name.replace("_", r"\_")]
        for dataset in datasets:
            q = _qtext(data["quality"][method][dataset], style)
            cells.append("--" if q is None else _wrap(q, ranked["marks"]["quality"][dataset].get(method, "none")))
            cells.append(_wrap(_num(data["tokens"][method][dataset]["mean"], "tokens"), ranked["marks"]["tokens"][dataset].get(method, "none")))
            cells.append(_wrap(_num(data["latency"][method][dataset]["mean"], "latency"), ranked["marks"]["latency"][dataset].get(method, "none")))
        if with_ranks:
            for key in ("quality", "tokens", "latency"):
                cells.append(_wrap(_rank_text(ranked["avg"][key][method]), ranked["avg_marks"][key].get(method, "none")))
        lines.append(" & ".join(cells) + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    return "\n".join(lines)
