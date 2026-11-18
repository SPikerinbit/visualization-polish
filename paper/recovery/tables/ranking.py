"""Unrounded ranks for one E1 sheet.

Quality: higher unrounded mean ranks better. A tied mean is split by
permutation std only when every member of that tie has a numeric std.
If any of those cells records n_permutations, every member must have
n_permutations >= 2; otherwise the std is not used. Smaller std ranks
better. Whatever remains tied takes the average of the places it occupies.

Cost (tokens and latency): lower unrounded mean ranks better. A
repeated-run variance is legal only when n_repeats >= 2 and
repeat_variance is a number. It is used only when every member of the
tied-mean group has a legal variance. Smaller variance ranks better.
That case does not also break the remaining tie by quality. When the
variance is not legal for the whole group, a higher quality mean breaks
the tie, and only when every member has a quality mean. A single run
never supplies a variance, even if a number is stored on the cell.
Anything still tied takes the average rank.

A missing mean is omitted from that column and from the equal-weight
cross-dataset average of the ranks the method did receive.
"""

from __future__ import annotations

from collections import defaultdict


def _average_ranks(groups):
    ranks = {}
    pos = 1
    for group in groups:
        width = len(group)
        value = (pos + (pos + width - 1)) / 2.0
        for name in group:
            ranks[name] = value
        pos += width
    return ranks


def _perm_std_usable(cells, ids):
    if not ids:
        return False
    stds = [cells[name].get("permutation_std") for name in ids]
    if any(std is None for std in stds):
        return False
    recorded = [cells[name].get("n_permutations") for name in ids]
    if any(value is not None for value in recorded):
        if any(value is None or int(value) < 2 for value in recorded):
            return False
    return True


def _variance_usable(cells, ids):
    if not ids:
        return False
    for name in ids:
        cell = cells[name]
        variance = cell.get("repeat_variance")
        repeats = int(cell.get("n_repeats") or 1)
        if variance is None or repeats < 2:
            return False
    return True


def _quality_groups(ids, quality):
    if ids and all(quality.get(name) is not None for name in ids):
        buckets = defaultdict(list)
        for name in ids:
            buckets[float(quality[name])].append(name)
        return [sorted(buckets[key]) for key in sorted(buckets, reverse=True)]
    return [sorted(ids)]


def rank_quality(cells):
    present = {name: cell for name, cell in cells.items() if cell.get("mean") is not None}
    by_mean = defaultdict(list)
    for name, cell in present.items():
        by_mean[float(cell["mean"])].append(name)
    groups = []
    for mean in sorted(by_mean, reverse=True):
        ids = by_mean[mean]
        if _perm_std_usable(present, ids):
            by_std = defaultdict(list)
            for name in ids:
                by_std[float(present[name]["permutation_std"])].append(name)
            for std in sorted(by_std):
                groups.append(sorted(by_std[std]))
        else:
            groups.append(sorted(ids))
    return _average_ranks(groups)


def rank_cost(cells, quality):
    present = {name: cell for name, cell in cells.items() if cell.get("mean") is not None}
    by_mean = defaultdict(list)
    for name, cell in present.items():
        by_mean[float(cell["mean"])].append(name)
    groups = []
    for mean in sorted(by_mean):
        ids = by_mean[mean]
        if _variance_usable(present, ids):
            by_var = defaultdict(list)
            for name in ids:
                by_var[float(present[name]["repeat_variance"])].append(name)
            for variance in sorted(by_var):
                groups.append(sorted(by_var[variance]))
        else:
            groups.extend(_quality_groups(ids, quality))
    return _average_ranks(groups)


def emphasis(ranks):
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


def average_rank(per_dataset, method):
    values = [ranks[method] for ranks in per_dataset.values() if method in ranks]
    if not values:
        return None
    return sum(values) / len(values)


def rank_sheet(sheet):
    methods = sheet["methods"]
    per = {metric: {} for metric in ("quality", "tokens", "latency")}
    marks = {metric: {} for metric in ("quality", "tokens", "latency")}
    for dataset in sheet["datasets"]:
        quality_cells = {method: sheet["cells"][method][dataset]["quality"] for method in methods}
        quality_means = {method: quality_cells[method].get("mean") for method in methods}
        token_cells = {method: sheet["cells"][method][dataset]["tokens"] for method in methods}
        latency_cells = {method: sheet["cells"][method][dataset]["latency"] for method in methods}
        per["quality"][dataset] = rank_quality(quality_cells)
        per["tokens"][dataset] = rank_cost(token_cells, quality_means)
        per["latency"][dataset] = rank_cost(latency_cells, quality_means)
        for metric in per:
            marks[metric][dataset] = emphasis(per[metric][dataset])
    average = {
        metric: {method: average_rank(per[metric], method) for method in methods}
        for metric in per
    }
    average_marks = {
        metric: emphasis({method: value for method, value in values.items() if value is not None})
        for metric, values in average.items()
    }
    return {"per": per, "marks": marks, "avg": average, "avg_marks": average_marks}
