"""Write the two E1 tables and the recompute audit from the synthetic sheets."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from ranking import DATASETS, group_token_sums, latency_average, rank_sheet, six_mean
from synthetic import EXAMPLE_INPUT_LABEL, LATENCY_COPY, MODELS, build_sheets

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "tex" / "generated"

LABELS = {
    "pointwise": "Pointwise",
    "ext_pointwise": "Ext.\\ Pointwise",
    "bubble": "Ext.\\ Bubble",
    "merge": "Ext.\\ Merge",
    "tournament": "Tournament",
    "lotus": "Lotus Quick",
    "setwise": "Setwise Heap",
    "sw": "SW",
    "lt": r"LT($h$)",
}
BREAK_BEFORE = {"listk", "lotus", "setwise", "sw"}


def row_label(method: str, demand: str) -> str:
    if method == "listk":
        return "ListK Sort" if demand == "full" else "ListK Select"
    return LABELS[method]


def _exact(value, places: int) -> str:
    quantum = Decimal("1").scaleb(-places)
    number = Decimal(value)
    shown = number.quantize(quantum)
    if shown != number:
        raise ValueError(f"{value} is not exact to {places} decimal places")
    return f"{shown:.{places}f}"


def _thousands(total: Decimal) -> str:
    shown = (total / Decimal(1000)).quantize(Decimal("0.01"))
    if shown * Decimal(1000) != total:
        raise ValueError(f"token sum {total} is not exact in thousandths to 0.01")
    return f"{shown:.2f}"


def _qpm(mean: str, std: str) -> str:
    return rf"\qpm{{{_exact(mean, 3)}}}{{{_exact(std, 3)}}}"


def _sheet_rows(sheet):
    traced = rank_sheet(sheet)
    rows = []
    for method in sheet["methods"]:
        quality = []
        for dataset in DATASETS:
            cell = sheet["cells"][method][dataset]["quality"]
            quality.append(
                {
                    "dataset": dataset,
                    "mean": cell["mean"],
                    "permutation_std": cell["permutation_std"],
                    "n_permutations": cell["n_permutations"],
                    "midrank": traced["quality"]["per_dataset_midrank"][dataset][method],
                }
            )
        tokens = [sheet["cells"][method][dataset]["tokens"]["mean"] for dataset in DATASETS]
        groups = {name: str(total) for name, total in group_token_sums(sheet, method).items()}
        rows.append(
            {
                "method": method,
                "label": row_label(method, sheet["demand"]),
                "quality": quality,
                "token_means": tokens,
                "token_group_sums": groups,
                "token_six_mean": str(six_mean(tokens)),
                "latency_means": [
                    sheet["cells"][method][dataset]["latency"]["mean"] for dataset in DATASETS
                ],
                "latency_six_mean": str(latency_average(sheet, method)),
                "average_rank": {metric: traced[metric]["average_rank"][method] for metric in traced},
                "integer": {metric: traced[metric]["integer"][method] for metric in traced},
            }
        )
    return {
        "model": sheet["model"],
        "demand": sheet["demand"],
        "synthetic": True,
        "quality_metric": sheet["quality_metric"],
        "rows": rows,
    }


def build_audit(sheets) -> dict:
    by_demand = {}
    for demand in ("full", "limit10"):
        by_demand[demand] = {
            model: _sheet_rows(sheets[(model, demand)]) for model in MODELS
        }
    return {
        "schema": "sema.exp1.audit.v2",
        "synthetic": True,
        "datasets": list(DATASETS),
        "rule": [
            "Per dataset, rank unrounded means. Quality is higher-better; tokens and latency are lower-better. Exact ties use midrank.",
            "The primary key is the unweighted mean of the six midranks. The displayed integer is the competition place in that order, not a rounded average.",
            "A tied primary key uses, for quality, the mean of Spearman (rho+1)/2 or of nDCG kept in [0,1], higher better; for tokens and latency, the mean of the six dataset means, lower better.",
            "The three token columns sum dataset means inside Q9, TREC, and BEIR. They are not three equal votes, and a missing dataset makes the method ineligible instead of reweighting the rest.",
            "The next key is the six raw means in dataset order, in the metric direction. Only if those vectors match, and every tied method has a legal repeat count on all six datasets, a smaller mean permutation std or repeat variance splits them. A missing count is not legal. This key is not a significance test.",
            "Identical remaining evidence shares one integer and the next integer is skipped. Method name, display rounding, and random order are not keys. A place is not a significance claim.",
        ],
        "example_input_label": EXAMPLE_INPUT_LABEL,
        "latency_fixture": LATENCY_COPY,
        "demands": by_demand,
    }


def _model_header(metric_name: str) -> str:
    return (
        rf"& \multicolumn{{6}}{{c}}{{{metric_name}}}"
        r" & \multicolumn{3}{c}{Tokens $\times 10^{3}$}"
        r" & Lat."
        r" & \multicolumn{3}{c}{Place}"
    )


def _model_names() -> str:
    return " & ".join(
        rf"\multicolumn{{13}}{{c}}{{\fontsize{{7}}{{8}}\selectfont\textbf{{{model}}}}}" for model in ["Qwen3.5-9B", "Qwen3.8-27B"]
    )


def _subheads() -> str:
    names = " & ".join(
        [
            "Q9",
            "DL20",
            "DL22",
            "COVID",
            "DBP",
            "R04",
            "Q9",
            "TREC",
            "BEIR",
            "s",
            "$Q$",
            "$T$",
            "$L$",
        ]
    )
    return f"& {names} & {names}"


def _rules_models() -> str:
    return r"\cmidrule(lr){2-14}\cmidrule(lr){15-27}"


def _rules_blocks() -> str:
    return (
        r"\cmidrule(lr){2-7}\cmidrule(lr){8-10}\cmidrule(lr){12-14}"
        r"\cmidrule(lr){15-20}\cmidrule(lr){21-23}\cmidrule(lr){25-27}"
    )


def _emphasis(value, values, rendered, *, higher=False):
    # Competition place on exact displayed-column source values, never std.
    place = 1 + sum(v > value if higher else v < value for v in values)
    return (r"\textbf{" + rendered + "}" if place == 1 else
            r"\underline{" + rendered + "}" if place == 2 else rendered)


def _body(audit_demand, demand: str) -> str:
    lines = []
    methods = audit_demand[MODELS[0]]["rows"]
    other = {row["method"]: row for row in audit_demand[MODELS[1]]["rows"]}
    for row in methods:
        if row["method"] in BREAK_BEFORE:
            lines.append(r"\midrule")
        label = row_label(row["method"], demand).replace(r"\ ", " ")
        label = " ".join(label.replace("\\", "").split())
        cells = [label]
        for model in MODELS:
            source = row if model == MODELS[0] else other[row["method"]]
            peers = audit_demand[model]["rows"]
            for i, item in enumerate(source["quality"]):
                cells.append(_emphasis(Decimal(item["mean"]), [Decimal(r["quality"][i]["mean"]) for r in peers], _qpm(item["mean"], item["permutation_std"]), higher=True))
            for name in ("Q9", "TREC", "BEIR"):
                cells.append(_emphasis(Decimal(source["token_group_sums"][name]), [Decimal(r["token_group_sums"][name]) for r in peers], _thousands(Decimal(source["token_group_sums"][name]))))
            cells.append(_emphasis(Decimal(source["latency_six_mean"]), [Decimal(r["latency_six_mean"]) for r in peers], _exact(source["latency_six_mean"], 2)))
            for metric in ("quality", "tokens", "latency"):
                place = source["integer"][metric]
                cells.append("---" if place is None else (r"\textbf{1}" if place == 1 else r"\underline{2}" if place == 2 else str(place)))
        lines.append(" & ".join(cells) + r" \\")
    return "\n".join(lines)


def full_tex(audit) -> str:
    demand = audit["demands"]["full"]
    return rf"""% Generated by src/emit.py. Do not edit numbers by hand.
% Synthetic layout, not experimental results.
\begin{{table*}}[t]
\centering
\caption{{Full ranking (Spearman $\rho$). Synthetic layout fixture, not measurements.
Quality is mean $\pm$ permutation std, not significance.
Tokens denote logical end-to-end Total (input + output), not the framework's merge-input-only objective;
columns sum dataset means: Q9; TREC = DL20 + DL22; BEIR = COVID + DBP + R04.
Latency is the equal-weight mean over six datasets, in seconds.
$Q,T,L$ are six-dataset competition places (\texttt{{STATS.md}}).
Bold/underline mark first/second competition place within each displayed column; ties share emphasis.
Model labels are requested labels; deployment manifests remain unverified.}}
\label{{tab:exp1-full}}
\begingroup
\fontsize{{6.4}}{{8.2}}\fontfamily{{qhv}}\fontseries{{c}}\selectfont
\renewcommand{{\qpm}}[2]{{\mbox{{\IfBeginWith{{#1}}{{0.}}{{\StrGobbleLeft{{#1}}{{1}}}}{{#1}}{{\fontsize{{5.8}}{{6.5}}\selectfont\textpm\IfBeginWith{{#2}}{{0.}}{{\StrGobbleLeft{{#2}}{{1}}}}{{#2}}}}}}}}
\setlength{{\tabcolsep}}{{0.4pt}}
\renewcommand{{\arraystretch}}{{1.18}}
\begin{{tabular*}}{{\textwidth}}{{@{{\extracolsep{{\fill}}}}l!{{\hspace{{1.5pt}}}}c*{{5}}{{!{{\hspace{{2.4pt}}}}c}}!{{\hspace{{2pt}}}}c*{{4}}{{!{{\hspace{{1.2pt}}}}c}}*{{2}}{{@{{\hspace{{1.75pt}}}}c}}!{{\hspace{{3pt}}}}c*{{5}}{{!{{\hspace{{2.4pt}}}}c}}!{{\hspace{{2pt}}}}c*{{4}}{{!{{\hspace{{1.2pt}}}}c}}*{{2}}{{@{{\hspace{{1.75pt}}}}c}}@{{}}}}
\toprule
& {_model_names()} \\
{_rules_models()}
Method {_model_header(r"Quality $\rho$")} {_model_header(r"Quality $\rho$")} \\
{_rules_blocks()}
{_subheads()} \\
\midrule
{_body(demand, "full")}
\bottomrule
\end{{tabular*}}
\endgroup
\end{{table*}}
"""


def limit_tex(audit) -> str:
    demand = audit["demands"]["limit10"]
    return rf"""% Generated by src/emit.py. Do not edit numbers by hand.
% Synthetic layout, not experimental results.
\begin{{table*}}[t]
\centering
\caption{{LIMIT $K{{=}}10$ (nDCG@10). Synthetic layout fixture, not measurements.
Quality is mean $\pm$ permutation std, not significance.
Tokens denote logical end-to-end Total (input + output), not the framework's merge-input-only objective;
columns sum dataset means: Q9; TREC = DL20 + DL22; BEIR = COVID + DBP + R04.
Latency is the equal-weight mean over six datasets, in seconds.
$Q,T,L$ are six-dataset competition places (\texttt{{STATS.md}}).
Bold/underline mark first/second competition place within each displayed column; ties share emphasis.
Model labels are requested labels; deployment manifests remain unverified. The ListK row is ListK Select.}}
\label{{tab:exp1-limit}}
\begingroup
\fontsize{{6.4}}{{8.2}}\fontfamily{{qhv}}\fontseries{{c}}\selectfont
\renewcommand{{\qpm}}[2]{{\mbox{{\IfBeginWith{{#1}}{{0.}}{{\StrGobbleLeft{{#1}}{{1}}}}{{#1}}{{\fontsize{{5.8}}{{6.5}}\selectfont\textpm\IfBeginWith{{#2}}{{0.}}{{\StrGobbleLeft{{#2}}{{1}}}}{{#2}}}}}}}}
\setlength{{\tabcolsep}}{{0.4pt}}
\renewcommand{{\arraystretch}}{{1.18}}
\begin{{tabular*}}{{\textwidth}}{{@{{\extracolsep{{\fill}}}}l!{{\hspace{{1.5pt}}}}c*{{5}}{{!{{\hspace{{2.4pt}}}}c}}!{{\hspace{{2pt}}}}c*{{4}}{{!{{\hspace{{1.2pt}}}}c}}*{{2}}{{@{{\hspace{{1.75pt}}}}c}}!{{\hspace{{3pt}}}}c*{{5}}{{!{{\hspace{{2.4pt}}}}c}}!{{\hspace{{2pt}}}}c*{{4}}{{!{{\hspace{{1.2pt}}}}c}}*{{2}}{{@{{\hspace{{1.75pt}}}}c}}@{{}}}}
\toprule
& {_model_names()} \\
{_rules_models()}
Method {_model_header("nDCG@10")} {_model_header("nDCG@10")} \\
{_rules_blocks()}
{_subheads()} \\
\midrule
{_body(demand, "limit10")}
\bottomrule
\end{{tabular*}}
\endgroup
\end{{table*}}
"""


def write(sheets=None) -> dict:
    sheets = sheets if sheets is not None else build_sheets()
    audit = build_audit(sheets)
    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / "exp1-full.tex").write_text(full_tex(audit))
    (GENERATED / "exp1-limit.tex").write_text(limit_tex(audit))
    (GENERATED / "exp1-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    return audit


if __name__ == "__main__":
    write()
