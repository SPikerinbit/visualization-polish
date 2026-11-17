"""Unrounded ranks for the layout tables.

Quality: higher mean is better. Inside one equal-mean group, a smaller
permutation std is used only when every member of that group has one.
Token and latency: lower mean is better. A legal repeat variance
(n_repeats >= 2 and variance is not None) is used only when every member
of the equal-mean group has one. A single run never creates a std.
If variance is not used, a higher quality mean breaks the tie when every
member has one. Anything still tied keeps the average of the ranks those
positions would have occupied. Missing means are omitted, not filled.
The cross-dataset rank is the equal-weight mean of the dataset ranks a
method actually received.
"""

from __future__ import annotations

from collections import defaultdict


def _average_ranks(groups: list[list[str]]) -> dict[str, float]:
    ranks: dict[str, float] = {}
    pos = 1
    for group in groups:
        width = len(group)
        value = (pos + (pos + width - 1)) / 2
        for name in group:
            ranks[name] = value
        pos += width
    return ranks


def _quality_groups(ids: list[str], quality: dict[str, float | None]) -> list[list[str]]:
    if ids and all(quality.get(name) is not None for name in ids):
        buckets: dict[float, list[str]] = defaultdict(list)
        for name in ids:
            buckets[float(quality[name])].append(name)
        return [sorted(buckets[key]) for key in sorted(buckets, reverse=True)]
    return [sorted(ids)]


def rank_quality(cells: dict[str, dict]) -> dict[str, float]:
    present = {name: cell for name, cell in cells.items() if cell.get("mean") is not None}
    by_mean: dict[float, list[str]] = defaultdict(list)
    for name, cell in present.items():
        by_mean[float(cell["mean"])].append(name)
    groups: list[list[str]] = []
    for mean in sorted(by_mean, reverse=True):
        ids = by_mean[mean]
        stds = [present[name].get("permutation_std") for name in ids]
        if ids and all(std is not None for std in stds):
            by_std: dict[float, list[str]] = defaultdict(list)
            for name in ids:
                by_std[float(present[name]["permutation_std"])].append(name)
            for std in sorted(by_std):
                groups.append(sorted(by_std[std]))
        else:
            groups.append(sorted(ids))
    return _average_ranks(groups)


def rank_cost(cells: dict[str, dict], quality: dict[str, float | None]) -> dict[str, float]:
    present = {name: cell for name, cell in cells.items() if cell.get("mean") is not None}
    by_mean: dict[float, list[str]] = defaultdict(list)
    for name, cell in present.items():
        by_mean[float(cell["mean"])].append(name)
    groups: list[list[str]] = []
    for mean in sorted(by_mean):
        ids = by_mean[mean]
        legal = []
        for name in ids:
            cell = present[name]
            variance = cell.get("repeat_variance")
            repeats = int(cell.get("n_repeats") or 1)
            legal.append(variance is not None and repeats >= 2)
        if ids and all(legal):
            by_var: dict[float, list[str]] = defaultdict(list)
            for name in ids:
                by_var[float(present[name]["repeat_variance"])].append(name)
            for variance in sorted(by_var):
                groups.extend(_quality_groups(by_var[variance], quality))
        else:
            groups.extend(_quality_groups(ids, quality))
    return _average_ranks(groups)


def emphasis(ranks: dict[str, float]) -> dict[str, str]:
    if not ranks:
        return {}
    best = min(ranks.values())
    rest = [value for value in ranks.values() if value != best]
    second = min(rest) if rest else None
    marks = {}
    for name, value in ranks.items():
        if value == best:
            marks[name] = "first"
        elif second is not None and value == second:
            marks[name] = "second"
        else:
            marks[name] = "none"
    return marks


def average_rank(per_dataset: dict[str, dict[str, float]], method: str) -> float | None:
    values = [ranks[method] for ranks in per_dataset.values() if method in ranks]
    if not values:
        return None
    return sum(values) / len(values)
