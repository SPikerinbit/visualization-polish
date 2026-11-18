"""Synthetic E1 sheets.

The numbers are layout fuel for the ranking rules and the column widths.
They are not measurements. build_sheet() is deterministic. A real run
replaces the JSON; it does not edit the TeX by hand.
"""

from __future__ import annotations

from catalog import DATASETS, DEMANDS, METHOD_IDS, MODELS

# Exact mean ties that the plants put on purpose.
ALLOWED_EXACT = {
    ("Qwen3.5-9B", "full", "DL20", "quality", frozenset({"sw", "lt"})),
    ("Qwen3.5-9B", "full", "DBpedia", "quality", frozenset({"lotus", "tournament"})),
    ("Qwen3.5-9B", "full", "COVID", "tokens", frozenset({"sw", "lt"})),
    ("Qwen3.8-27B", "full", "DL22", "quality", frozenset({"sw", "lt"})),
    ("Qwen3.8-27B", "full", "Q9", "tokens", frozenset({"bubble", "merge"})),
    ("Qwen3.5-9B", "limit10", "DBpedia", "quality", frozenset({"sw", "lt"})),
    ("Qwen3.8-27B", "limit10", "COVID", "quality", frozenset({"lotus", "setwise"})),
    ("Qwen3.8-27B", "limit10", "DL20", "tokens", frozenset({"pointwise", "ext_pointwise"})),
}


def _quality(mean, std, permutations=10):
    if mean is None:
        return {"mean": None, "permutation_std": None, "n_permutations": None}
    return {"mean": mean, "permutation_std": std, "n_permutations": permutations}


def _cost(mean, repeats=1, variance=None):
    if mean is None:
        return {"mean": None, "n_repeats": None, "repeat_variance": None}
    return {"mean": float(mean), "n_repeats": repeats, "repeat_variance": variance}


def _base_quality(method_index, dataset_index, model_index, mode_index):
    millis = 360 + 13 * method_index + 7 * dataset_index + 19 * model_index + 31 * mode_index
    return millis / 1000.0, 0.015 + method_index / 1000.0


def _base_tokens(method_index, dataset_index, model_index, mode_index):
    return float(20000 + 3000 * method_index + 1000 * dataset_index + 40000 * model_index + 20000 * mode_index)


def _base_latency(method_index, dataset_index, model_index, mode_index):
    return (30 + 4 * method_index + 3 * dataset_index + 5 * model_index + 7 * mode_index) / 10.0


def _blank_sheet(model, demand):
    cells = {}
    model_index = MODELS.index(model)
    mode_index = DEMANDS.index(demand)
    for method_index, method in enumerate(METHOD_IDS):
        cells[method] = {}
        for dataset_index, dataset in enumerate(DATASETS):
            mean, std = _base_quality(method_index, dataset_index, model_index, mode_index)
            cells[method][dataset] = {
                "quality": _quality(mean, std),
                "tokens": _cost(_base_tokens(method_index, dataset_index, model_index, mode_index)),
                "latency": _cost(_base_latency(method_index, dataset_index, model_index, mode_index)),
            }
    return {
        "schema": "sema.exp1.sheet.v1",
        "synthetic": True,
        "model": model,
        "demand": demand,
        "quality_metric": "spearman" if demand == "full" else "ndcg@10",
        "token_unit": "logical_total_input_plus_output",
        "token_display": "nearest_integer_of_mean_over_1000",
        "latency_unit": "isolated_single_run_seconds",
        "datasets": list(DATASETS),
        "methods": list(METHOD_IDS),
        "cells": cells,
    }


def _put_quality(sheet, dataset, values):
    for method, spec in values.items():
        if spec is None:
            sheet["cells"][method][dataset]["quality"] = _quality(None, None)
        else:
            mean, std = spec
            sheet["cells"][method][dataset]["quality"] = _quality(mean, std)


def _descending(start, step=0.02):
    """Ten distinct quality pairs, already sorted best to worst."""
    order = list(METHOD_IDS)
    return {method: (round(start - step * index, 3), round(0.010 + 0.001 * index, 3)) for index, method in enumerate(order)}


def build_sheet(model, demand):
    if model not in MODELS or demand not in DEMANDS:
        raise ValueError((model, demand))
    sheet = _blank_sheet(model, demand)
    if model == "Qwen3.5-9B" and demand == "full":
        _put_quality(sheet, "Q9", {
            "pointwise": (0.5014, 0.020),
            "ext_pointwise": (0.5006, 0.010),
            "bubble": (0.420, 0.018),
            "merge": (0.400, 0.015),
            "listk": (0.380, 0.012),
            "tournament": (0.360, 0.011),
            "lotus": (0.340, 0.014),
            "setwise": (0.330, 0.016),
            "sw": (0.310, 0.013),
            "lt": (0.300, 0.017),
        })
        _put_quality(sheet, "DL20", {
            "sw": (0.620, 0.030),
            "lt": (0.620, 0.030),
            "bubble": (0.610, 0.020),
            "pointwise": (0.500, 0.010),
            "ext_pointwise": (0.480, 0.011),
            "merge": (0.460, 0.012),
            "listk": (0.440, 0.013),
            "tournament": (0.430, 0.014),
            "lotus": (0.410, 0.015),
            "setwise": (0.390, 0.016),
        })
        _put_quality(sheet, "DBpedia", {
            "lotus": (0.455, 0.012),
            "tournament": (0.455, 0.040),
            "pointwise": (0.400, 0.010),
            "ext_pointwise": (0.390, 0.011),
            "bubble": (0.380, 0.012),
            "merge": (0.370, 0.013),
            "listk": (0.360, 0.014),
            "setwise": (0.350, 0.015),
            "sw": (0.340, 0.016),
            "lt": (0.330, 0.017),
        })
        _put_quality(sheet, "COVID", {
            "lt": (0.520, 0.010),
            "sw": (0.400, 0.011),
            "pointwise": (0.380, 0.012),
            "ext_pointwise": (0.360, 0.013),
            "bubble": (0.340, 0.014),
            "merge": (0.320, 0.015),
            "listk": (0.300, 0.016),
            "tournament": (0.280, 0.017),
            "lotus": (0.260, 0.018),
            "setwise": (0.240, 0.019),
        })
        # Lowest tokens, so the quality tie-break is visible as bold versus underline.
        sheet["cells"]["sw"]["COVID"]["tokens"] = _cost(12000)
        sheet["cells"]["lt"]["COVID"]["tokens"] = _cost(12000)
        sheet["cells"]["sw"]["DL22"]["latency"] = _cost(2.24)
        sheet["cells"]["lt"]["DL22"]["latency"] = _cost(2.16)
        sheet["cells"]["setwise"]["Robust04"]["quality"] = _quality(None, None)
    elif model == "Qwen3.8-27B" and demand == "full":
        column = _descending(0.450)
        column["sw"] = (0.510, 0.025)
        column["lt"] = (0.510, 0.025)
        column["bubble"] = (0.470, 0.010)
        _put_quality(sheet, "DL22", column)
        sheet["cells"]["bubble"]["Q9"]["quality"] = _quality(0.700, 0.010)
        sheet["cells"]["merge"]["Q9"]["quality"] = _quality(0.650, 0.010)
        # Variances point the other way from quality, and n_repeats is 1,
        # so a ranker that trusted them would prefer merge. It must not.
        sheet["cells"]["bubble"]["Q9"]["tokens"] = _cost(10000, repeats=1, variance=9.0)
        sheet["cells"]["merge"]["Q9"]["tokens"] = _cost(10000, repeats=1, variance=1.0)
        sheet["cells"]["pointwise"]["COVID"]["quality"] = _quality(None, None)
    elif model == "Qwen3.5-9B" and demand == "limit10":
        column = _descending(0.440)
        column["sw"] = (0.470, 0.008)
        column["lt"] = (0.470, 0.030)
        _put_quality(sheet, "DBpedia", column)
        sheet["cells"]["merge"]["DL20"]["latency"] = _cost(4.24)
        sheet["cells"]["bubble"]["DL20"]["latency"] = _cost(4.16)
        sheet["cells"]["setwise"]["Q9"]["tokens"] = _cost(None)
    elif model == "Qwen3.8-27B" and demand == "limit10":
        column = _descending(0.490)
        column["lotus"] = (0.530, 0.020)
        column["setwise"] = (0.530, 0.020)
        _put_quality(sheet, "COVID", column)
        sheet["cells"]["pointwise"]["DL20"]["tokens"] = _cost(51000)
        sheet["cells"]["ext_pointwise"]["DL20"]["tokens"] = _cost(51000)
        sheet["cells"]["pointwise"]["Robust04"]["latency"] = _cost(None)
    audit_exact_ties(sheet)
    return sheet


def exact_tie_groups(sheet):
    found = []
    for dataset in sheet["datasets"]:
        for metric in ("quality", "tokens", "latency"):
            buckets = {}
            for method in sheet["methods"]:
                mean = sheet["cells"][method][dataset][metric].get("mean")
                if mean is None:
                    continue
                buckets.setdefault(float(mean), []).append(method)
            for names in buckets.values():
                if len(names) > 1:
                    found.append((dataset, metric, frozenset(names)))
    return found


def audit_exact_ties(sheet):
    identity = (sheet["model"], sheet["demand"])
    allowed = set()
    for model, demand, dataset, metric, names in ALLOWED_EXACT:
        if (model, demand) == identity:
            allowed.add((dataset, metric, names))
    found = set(exact_tie_groups(sheet))
    if found != allowed:
        raise AssertionError(f"unexpected exact ties for {identity}: extra={found - allowed} missing={allowed - found}")


def build_all():
    return [build_sheet(model, demand) for model in MODELS for demand in DEMANDS]
