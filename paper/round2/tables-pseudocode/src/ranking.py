"""E1 integer places from the declared rule.

Smaller keys are better. Equality is exact decimal equality of the stored
values, not a rounded display and not a binary float. See STATS.md.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction

DATASETS = ("Q9", "DL20", "DL22", "COVID", "DBpedia", "Robust04")
BENCHMARKS = (
    ("Q9", ("Q9",)),
    ("TREC", ("DL20", "DL22")),
    ("BEIR", ("COVID", "DBpedia", "Robust04")),
)
METRICS = ("quality", "tokens", "latency")


def D(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        raise TypeError("floats are not an original precision; pass a decimal string")
    return Decimal(str(value))


def quality_unit(value, metric: str) -> Decimal:
    """Map one dataset mean onto its declared [0, 1] unit.

    Spearman uses (rho+1)/2. nDCG is already on [0, 1] and is kept.
    The map is only a secondary key. It does not equate the two metrics.
    """
    number = D(value)
    if metric == "spearman":
        return (number + 1) / 2
    if metric.startswith("ndcg"):
        if number < 0 or number > 1:
            raise ValueError(f"{metric} value {number} is outside [0, 1]")
        return number
    raise ValueError(f"no declared quality transform for {metric!r}")


def midranks(means: dict, *, higher_better: bool) -> dict:
    """Average the places occupied by an exact tie. Names do not break it."""
    ordered = sorted(means.items(), key=lambda item: item[1], reverse=higher_better)
    groups = []
    for name, value in ordered:
        if groups and groups[-1][0] == value:
            groups[-1][1].append(name)
        else:
            groups.append([value, [name]])
    ranks = {}
    place = 1
    for _value, names in groups:
        width = len(names)
        rank = Fraction(place + place + width - 1, 2)
        for name in names:
            ranks[name] = rank
        place += width
    return ranks


def six_mean(values) -> Decimal:
    values = list(values)
    if len(values) != 6:
        raise ValueError(f"a six-dataset mean needs 6 values, got {len(values)}")
    return sum((D(value) for value in values), Decimal(0)) / 6


def _cell(sheet, method, dataset, metric):
    return sheet["cells"][method][dataset][metric]


def _mean(sheet, method, dataset, metric):
    raw = _cell(sheet, method, dataset, metric).get("mean")
    if raw is None:
        return None
    return D(raw)


def _quality_std_key(sheet, method):
    """Smaller mean permutation std. Absent or single-run counts are not evidence.

    Every dataset must carry a permutation std and ``n_permutations >= 2``.
    A sheet that stores stds but leaves every count missing does not get this key.
    The key breaks an exact residual tie. It is not a significance test.
    """
    stds = []
    counts = []
    for dataset in DATASETS:
        cell = _cell(sheet, method, dataset, "quality")
        stds.append(cell.get("permutation_std"))
        counts.append(cell.get("n_permutations"))
    if any(std is None for std in stds):
        return None
    if any(count is None or int(count) < 2 for count in counts):
        return None
    return six_mean(stds)


def _variance_key(sheet, method, metric):
    variances = []
    for dataset in DATASETS:
        cell = _cell(sheet, method, dataset, metric)
        repeats = cell.get("n_repeats")
        variance = cell.get("repeat_variance")
        if repeats is None or int(repeats) < 2 or variance is None:
            return None
        variances.append(variance)
    return six_mean(variances)


def _quaternary(sheet, method, metric):
    if metric == "quality":
        return _quality_std_key(sheet, method)
    return _variance_key(sheet, method, metric)


def _competition(groups):
    ranks = {}
    place = 1
    for group in groups:
        for name in group:
            ranks[name] = place
        place += len(group)
    return ranks


def rank_metric(sheet, metric: str) -> dict:
    if tuple(sheet["datasets"]) != DATASETS:
        raise ValueError("dataset order is fixed; it is the lexicographic key")
    if metric not in METRICS:
        raise ValueError(metric)
    higher = metric == "quality"
    methods = list(sheet["methods"])
    present = {method: True for method in methods}
    per_dataset = {}
    for dataset in DATASETS:
        means = {}
        for method in methods:
            value = _mean(sheet, method, dataset, metric)
            if value is None:
                present[method] = False
            else:
                means[method] = value
        per_dataset[dataset] = midranks(means, higher_better=higher)

    def average(method):
        return sum(per_dataset[dataset][method] for dataset in DATASETS) / 6

    def secondary(method):
        raw = [_mean(sheet, method, dataset, metric) for dataset in DATASETS]
        if metric == "quality":
            units = [quality_unit(value, sheet["quality_metric"]) for value in raw]
            return -six_mean(units)
        return six_mean(raw)

    def tertiary(method):
        raw = tuple(_mean(sheet, method, dataset, metric) for dataset in DATASETS)
        if metric == "quality":
            return tuple(-value for value in raw)
        return raw

    eligible = [method for method in methods if present[method]]
    decorated = sorted(
        ((average(method), secondary(method), tertiary(method), method) for method in eligible),
        key=lambda row: (row[0], row[1], row[2]),
    )
    clusters = []
    for avg, second, third, method in decorated:
        key = (avg, second, third)
        if clusters and clusters[-1][0] == key:
            clusters[-1][1].append(method)
        else:
            clusters.append((key, [method]))

    groups = []
    split_notes = []
    for key, names in clusters:
        quarters = {method: _quaternary(sheet, method, metric) for method in names}
        if len(names) > 1 and all(value is not None for value in quarters.values()):
            ordered = sorted(names, key=lambda method: quarters[method])
            bucket = []
            current = None
            for method in ordered:
                value = quarters[method]
                if current is None or value != current:
                    if bucket:
                        groups.append(bucket)
                    bucket = [method]
                    current = value
                else:
                    bucket.append(method)
            groups.append(bucket)
            if len(groups) and any(len(group) != len(names) for group in groups[-len(ordered) :]):
                split_notes.append(
                    {"methods": list(names), "by": "quaternary", "metric": metric}
                )
        else:
            groups.append(list(names))
            if len(names) > 1:
                split_notes.append(
                    {
                        "methods": list(names),
                        "by": "identical-evidence",
                        "metric": metric,
                        "quaternary_available": {
                            method: quarters[method] is not None for method in names
                        },
                    }
                )

    integers = _competition(groups)
    for method in methods:
        if not present[method]:
            integers[method] = None
    return {
        "per_dataset_midrank": {
            dataset: {method: str(rank) for method, rank in ranks.items()}
            for dataset, ranks in per_dataset.items()
        },
        "average_rank": {
            method: (str(average(method)) if present[method] else None) for method in methods
        },
        "secondary_key_smaller_better": {
            method: (str(secondary(method)) if present[method] else None) for method in methods
        },
        "integer": integers,
        "ineligible": [method for method in methods if not present[method]],
        "residual_groups": split_notes,
    }


def group_token_sums(sheet, method) -> dict:
    sums = {}
    for name, members in BENCHMARKS:
        parts = [_mean(sheet, method, dataset, "tokens") for dataset in members]
        if any(part is None for part in parts):
            sums[name] = None
        else:
            sums[name] = sum(parts, Decimal(0))
    return sums


def latency_average(sheet, method):
    parts = [_mean(sheet, method, dataset, "latency") for dataset in DATASETS]
    if any(part is None for part in parts):
        return None
    return six_mean(parts)


def forbidden_benchmark_rank_average(sheet, metric="tokens") -> dict:
    """What the contract forbids: average the three group-sum ranks.

    Group sums partition the six datasets, but ranking those three sums and
    averaging the three ranks gives Q9, TREC, and BEIR equal votes.
    """
    if metric != "tokens":
        raise ValueError("the forbidden display reweight is defined for token groups")
    methods = [
        method
        for method in sheet["methods"]
        if all(_mean(sheet, method, dataset, "tokens") is not None for dataset in DATASETS)
    ]
    per_group = {}
    for name, _members in BENCHMARKS:
        means = {method: group_token_sums(sheet, method)[name] for method in methods}
        per_group[name] = midranks(means, higher_better=False)
    return {
        method: sum(per_group[name][method] for name, _members in BENCHMARKS) / 3
        for method in methods
    }


def rank_sheet(sheet) -> dict:
    return {metric: rank_metric(sheet, metric) for metric in METRICS}
