"""Deterministic synthetic E1 sheets.

The numbers are layout fuel for the declared ranking rule. They are not
measurements. A later measured sheet replaces this module's output; it does
not edit the TeX by hand.
"""

from __future__ import annotations

from decimal import Decimal

from ranking import DATASETS, D

METHOD_IDS = (
    "pointwise",
    "ext_pointwise",
    "bubble",
    "merge",
    "listk",
    "tournament",
    "lotus",
    "setwise",
    "sw",
    "lt",
)
MODELS = ("Qwen3.5-9B", "Qwen3.5-27B")
DEMANDS = ("full", "limit10")

# Strict places before the planted DL20 tie between SW and LT.
# Pointwise sums to 9 (average 1.5) and is still the unique best average,
# so its integer place is 1. Rounding 1.5 would not produce 1.
STRICT_PLACES = {
    "Q9": (2, 1, 3, 4, 5, 6, 7, 8, 9, 10),
    "DL20": (2, 1, 3, 4, 5, 6, 7, 8, 10, 9),
    "DL22": (2, 1, 3, 4, 5, 6, 7, 8, 9, 10),
    "COVID": (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
    "DBpedia": (1, 2, 4, 3, 5, 6, 7, 8, 9, 10),
    "Robust04": (1, 3, 2, 4, 5, 6, 7, 8, 9, 10),
}

# ListK wins the first three token columns by a small margin and loses the
# last three by a large one, so its six-dataset mean is worse than Tournament
# while it wins two of the three benchmark group sums.
_LISTK_TOKENS = (1400, 1500, 1600, 2000, 2000, 2000)
_TOURNAMENT_TOKENS = (1410, 1510, 1610, 1700, 1700, 1700)
_CHEAP_TOKENS = {
    "pointwise": 1000,
    "ext_pointwise": 1100,
    "bubble": 1200,
    "merge": 1300,
}
_DEAR_TOKENS = {
    "lotus": 3000,
    "setwise": 3100,
    "sw": 3200,
    "lt": 3300,
}


def _require_permutation(places):
    if tuple(sorted(places)) != tuple(range(1, 11)):
        raise ValueError(places)


def quality_shift(model_index: int, demand_index: int) -> Decimal:
    return Decimal("0.020") * model_index - Decimal("0.040") * demand_index


def quality_mean(method_index: int, dataset: str, shift: Decimal) -> Decimal:
    if dataset == "DL20" and METHOD_IDS[method_index] in {"sw", "lt"}:
        return Decimal("0.670") + shift
    place = STRICT_PLACES[dataset][method_index]
    return Decimal("0.860") - Decimal("0.020") * place + shift


def quality_std(method_index: int, dataset: str) -> Decimal:
    method = METHOD_IDS[method_index]
    if dataset == "DL20" and method == "sw":
        return Decimal("0.030")
    if dataset == "DL20" and method == "lt":
        return Decimal("0.011")
    return Decimal("0.012") + Decimal("0.001") * method_index


def token_mean(method: str, dataset_index: int, model_index: int, demand_index: int) -> Decimal:
    shift = 4000 * model_index + 700 * demand_index
    if method == "listk":
        base = _LISTK_TOKENS[dataset_index]
    elif method == "tournament":
        base = _TOURNAMENT_TOKENS[dataset_index]
    elif method in _CHEAP_TOKENS:
        base = _CHEAP_TOKENS[method] + 10 * dataset_index
    else:
        base = _DEAR_TOKENS[method] + 10 * dataset_index
    return Decimal(shift + base)


def latency_mean(method_index: int, dataset_index: int, model_index: int, demand_index: int) -> Decimal:
    return (
        Decimal("1.5")
        + Decimal("0.4") * method_index
        + Decimal("0.1") * dataset_index
        + Decimal("0.5") * model_index
        + Decimal("0.3") * demand_index
    )


# Display sheets no longer copy SW latency onto LT. The copy made Qwen3.5-9B
# Full print place 9 twice and skip 10. Both vectors were the SW formula,
# [4.7, 4.8, 4.9, 5.0, 5.1, 5.2]. The display now keeps the generator:
# SW (method index 8) stays on that vector; LT (index 9) is
# [5.1, 5.2, 5.3, 5.4, 5.5, 5.6]. The identical vector still exists only as
# a test input. Sharing an integer there is the ranker's result, not a
# measured difference and not a check that this figure is correct.
EXAMPLE_INPUT_LABEL = "示例输入为覆盖tie-break测试而构造"
LATENCY_COPY = {
    "sheet": "Qwen3.5-9B full",
    "before": {
        "sw": ["4.7", "4.8", "4.9", "5.0", "5.1", "5.2"],
        "lt": ["4.7", "4.8", "4.9", "5.0", "5.1", "5.2"],
        "integers": {"sw": 9, "lt": 9},
    },
    "after": {
        "sw": ["4.7", "4.8", "4.9", "5.0", "5.1", "5.2"],
        "lt": ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6"],
    },
    "reason": (
        "The copy was a layout example of exact equality. "
        "The display requirement is places 1 through 10 with no shared integer. "
        "Removing the copy uses the predeclared generator, not a new measured gap."
    ),
}


def build_sheet(model: str, demand: str) -> dict:
    if model not in MODELS or demand not in DEMANDS:
        raise ValueError((model, demand))
    for places in STRICT_PLACES.values():
        _require_permutation(places)
    model_index = MODELS.index(model)
    demand_index = DEMANDS.index(demand)
    shift = quality_shift(model_index, demand_index)
    cells = {}
    for method_index, method in enumerate(METHOD_IDS):
        cells[method] = {}
        for dataset_index, dataset in enumerate(DATASETS):
            cells[method][dataset] = {
                "quality": {
                    "mean": str(quality_mean(method_index, dataset, shift)),
                    "permutation_std": str(quality_std(method_index, dataset)),
                    "n_permutations": 10,
                },
                "tokens": {
                    "mean": str(token_mean(method, dataset_index, model_index, demand_index)),
                    "n_repeats": 1,
                    "repeat_variance": None,
                },
                "latency": {
                    "mean": str(latency_mean(method_index, dataset_index, model_index, demand_index)),
                    "n_repeats": 1,
                    "repeat_variance": None,
                },
            }
    metric = "spearman" if demand == "full" else "ndcg@10"
    sheet = {
        "schema": "sema.exp1.sheet.v2",
        "synthetic": True,
        "example_input_label": EXAMPLE_INPUT_LABEL,
        "disclosure": (
            f"{EXAMPLE_INPUT_LABEL} "
            "Every mean, permutation std, token count, and latency is a constructed example, "
            "not a measurement. "
            "Permutation std is an independent stored decimal with n_permutations=10. "
            "It is not the standard deviation across datasets and not a significance claim. "
            "Token and latency cells are single synthetic dataset means (n_repeats=1); "
            "a stored variance is ignored at that repeat count. "
            "Qwen3.5-9B Full no longer copies SW latency onto LT; "
            "the identical vector is a test input only. See LATENCY_COPY."
        ),
        "model": model,
        "demand": demand,
        "quality_metric": metric,
        "datasets": list(DATASETS),
        "methods": list(METHOD_IDS),
        "cells": cells,
    }
    _bounds(sheet)
    return sheet


def _bounds(sheet):
    metric = sheet["quality_metric"]
    for method in sheet["methods"]:
        for dataset in DATASETS:
            value = D(sheet["cells"][method][dataset]["quality"]["mean"])
            if metric == "spearman":
                if value < -1 or value > 1:
                    raise ValueError((method, dataset, value))
            elif value < 0 or value > 1:
                raise ValueError((method, dataset, value))


def build_sheets() -> dict:
    return {
        (model, demand): build_sheet(model, demand) for model in MODELS for demand in DEMANDS
    }
