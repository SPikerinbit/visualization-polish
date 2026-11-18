"""Synthetic E4c means for layout only.

Each coordinate is one method's equal-weight mean. Query-level values are not
stored and must not be plotted. These numbers are not measurements.
"""

from __future__ import annotations

METHODS = [
    {"id": "pointwise", "number": 1, "legend": "Pointwise", "short": "PW", "e1_name": "OrderByLLM Pointwise", "color": "#0072B2", "marker": "o"},
    {"id": "ext_pointwise", "number": 2, "legend": "Ext. Pointwise", "short": "ExtPW", "e1_name": "Ext. Pointwise", "color": "#E69F00", "marker": "s"},
    {"id": "bubble", "number": 3, "legend": "External Bubble", "short": "Bubble", "e1_name": "External Bubble", "color": "#009E73", "marker": "D"},
    {"id": "merge", "number": 4, "legend": "External Merge", "short": "Merge", "e1_name": "External Merge", "color": "#D55E00", "marker": "^"},
    {"id": "listk", "number": 5, "legend": "ListK", "short": "ListK", "e1_name": "ListK Sort (Full) / ListK Select (LIMIT 10)", "color": "#CC79A7", "marker": "v"},
    {"id": "tournament", "number": 6, "legend": "Tournament", "short": "Tourn", "e1_name": "Tournament", "color": "#6A3D9A", "marker": "P"},
    {"id": "lotus", "number": 7, "legend": "Lotus Quick", "short": "Lotus", "e1_name": "Lotus Quick", "color": "#A6761D", "marker": "X"},
    {"id": "setwise", "number": 8, "legend": "Setwise Heap", "short": "SetH", "e1_name": "Setwise Heap", "color": "#882255", "marker": "h"},
    {"id": "sw", "number": 9, "legend": "SW", "short": "SW", "e1_name": "SW", "color": "#E7298A", "marker": "p"},
    {"id": "lt", "number": 10, "legend": "LT", "short": "LT", "e1_name": "LT", "color": "#332288", "marker": "<"},
]

# (metric, dataset, state, method) -> (equivalent tokens, quality)
POINTS = {
    ("full", "DL20", "Off", "pointwise"): (49500, 0.47),
    ("full", "DL20", "Off", "ext_pointwise"): (44500, 0.70),
    ("full", "DL20", "Off", "bubble"): (40500, 0.42),
    ("full", "DL20", "Off", "lotus"): (36800, 0.57),
    ("full", "DL20", "Off", "merge"): (33200, 0.63),
    ("full", "DL20", "Off", "listk"): (28500, 0.76),
    ("full", "DL20", "Off", "tournament"): (25000, 0.68),
    ("full", "DL20", "Off", "setwise"): (22500, 0.58),
    ("full", "DL20", "Off", "sw"): (19000, 0.82),
    ("full", "DL20", "Off", "lt"): (21000, 0.50),
    ("full", "DL20", "On-cold", "pointwise"): (47000, 0.49),
    ("full", "DL20", "On-cold", "ext_pointwise"): (43000, 0.66),
    ("full", "DL20", "On-cold", "bubble"): (39000, 0.44),
    ("full", "DL20", "On-cold", "lotus"): (35500, 0.52),
    ("full", "DL20", "On-cold", "merge"): (30500, 0.57),
    ("full", "DL20", "On-cold", "listk"): (26000, 0.74),
    ("full", "DL20", "On-cold", "setwise"): (28800, 0.69),
    ("full", "DL20", "On-cold", "tournament"): (24000, 0.63),
    ("full", "DL20", "On-cold", "sw"): (18200, 0.79),
    ("full", "DL20", "On-cold", "lt"): (21500, 0.55),
    ("full", "COVID", "Off", "pointwise"): (52000, 0.45),
    ("full", "COVID", "Off", "ext_pointwise"): (47500, 0.68),
    ("full", "COVID", "Off", "bubble"): (42500, 0.50),
    ("full", "COVID", "Off", "lotus"): (38000, 0.56),
    ("full", "COVID", "Off", "merge"): (34000, 0.60),
    ("full", "COVID", "Off", "listk"): (28200, 0.73),
    ("full", "COVID", "Off", "tournament"): (24800, 0.77),
    ("full", "COVID", "Off", "setwise"): (25200, 0.63),
    ("full", "COVID", "Off", "sw"): (23500, 0.66),
    ("full", "COVID", "Off", "lt"): (19800, 0.58),
    ("full", "COVID", "On-cold", "pointwise"): (50000, 0.46),
    ("full", "COVID", "On-cold", "ext_pointwise"): (45500, 0.70),
    ("full", "COVID", "On-cold", "bubble"): (40800, 0.43),
    ("full", "COVID", "On-cold", "lotus"): (37800, 0.58),
    ("full", "COVID", "On-cold", "merge"): (34200, 0.63),
    ("full", "COVID", "On-cold", "listk"): (29500, 0.72),
    ("full", "COVID", "On-cold", "tournament"): (25000, 0.76),
    ("full", "COVID", "On-cold", "setwise"): (22500, 0.63),
    ("full", "COVID", "On-cold", "sw"): (20000, 0.70),
    ("full", "COVID", "On-cold", "lt"): (18000, 0.55),
    ("topk", "DL20", "Off", "pointwise"): (47000, 0.36),
    ("topk", "DL20", "Off", "ext_pointwise"): (43000, 0.50),
    ("topk", "DL20", "Off", "bubble"): (39000, 0.62),
    ("topk", "DL20", "Off", "lotus"): (35500, 0.41),
    ("topk", "DL20", "Off", "merge"): (31800, 0.56),
    ("topk", "DL20", "Off", "listk"): (27500, 0.71),
    ("topk", "DL20", "Off", "tournament"): (24200, 0.66),
    ("topk", "DL20", "Off", "setwise"): (21000, 0.58),
    ("topk", "DL20", "Off", "sw"): (18500, 0.75),
    ("topk", "DL20", "Off", "lt"): (23000, 0.45),
    ("topk", "DL20", "On-cold", "pointwise"): (44500, 0.39),
    ("topk", "DL20", "On-cold", "ext_pointwise"): (40000, 0.52),
    ("topk", "DL20", "On-cold", "bubble"): (48000, 0.60),
    ("topk", "DL20", "On-cold", "lotus"): (36500, 0.43),
    ("topk", "DL20", "On-cold", "merge"): (33000, 0.55),
    ("topk", "DL20", "On-cold", "listk"): (29000, 0.73),
    ("topk", "DL20", "On-cold", "tournament"): (25500, 0.68),
    ("topk", "DL20", "On-cold", "setwise"): (22000, 0.61),
    ("topk", "DL20", "On-cold", "sw"): (17500, 0.76),
    ("topk", "DL20", "On-cold", "lt"): (20000, 0.48),
    ("topk", "COVID", "Off", "pointwise"): (51000, 0.34),
    ("topk", "COVID", "Off", "ext_pointwise"): (46500, 0.47),
    ("topk", "COVID", "Off", "bubble"): (42500, 0.58),
    ("topk", "COVID", "Off", "lotus"): (38800, 0.40),
    ("topk", "COVID", "Off", "merge"): (35200, 0.55),
    ("topk", "COVID", "Off", "listk"): (30500, 0.69),
    ("topk", "COVID", "Off", "tournament"): (26000, 0.74),
    ("topk", "COVID", "Off", "setwise"): (23500, 0.62),
    ("topk", "COVID", "Off", "sw"): (20500, 0.66),
    ("topk", "COVID", "Off", "lt"): (19000, 0.50),
    ("topk", "COVID", "On-cold", "pointwise"): (49000, 0.37),
    ("topk", "COVID", "On-cold", "ext_pointwise"): (45200, 0.42),
    ("topk", "COVID", "On-cold", "bubble"): (41000, 0.54),
    ("topk", "COVID", "On-cold", "lotus"): (37500, 0.48),
    ("topk", "COVID", "On-cold", "merge"): (33800, 0.60),
    ("topk", "COVID", "On-cold", "listk"): (29500, 0.71),
    ("topk", "COVID", "On-cold", "tournament"): (25000, 0.75),
    ("topk", "COVID", "On-cold", "setwise"): (23000, 0.57),
    ("topk", "COVID", "On-cold", "sw"): (19500, 0.65),
    ("topk", "COVID", "On-cold", "lt"): (17800, 0.70),
}

META = {
    "status": "synthetic-layout-only",
    "not_a_measurement": True,
    "per_query_points": False,
    "n_queries_represented_by_each_mean": 3,
    "aggregation": "equal-weight mean; query-level values are omitted",
    "model_context": "Qwen3.5-9B is the contract setting; coordinates are not model output",
    "initial_permutation": 0,
    "beta": 0,
    "output_weight": 1,
    "x_definition": "equivalent tokens U-(1-beta)Q+O",
    "currency": False,
    "pareto_line": False,
    "datasets": ["DL20", "COVID"],
    "states": ["Off", "On-cold"],
    "metrics": {
        "full": {"y": "Spearman", "y_definition": "full-ranking Spearman"},
        "topk": {"y": "NDCG@10", "y_definition": "LIMIT 10 NDCG@10"},
    },
}


def points_for(metric: str, dataset: str | None = None, state: str | None = None) -> list[dict]:
    rows = []
    for (met, dat, st, method), (x, y) in POINTS.items():
        if met != metric:
            continue
        if dataset is not None and dat != dataset:
            continue
        if state is not None and st != state:
            continue
        rows.append({"metric": met, "dataset": dat, "state": st, "method": method, "x": x, "y": y})
    return rows
