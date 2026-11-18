"""The printed sheets and the tie rule, checked from the stored decimals."""

from __future__ import annotations

import copy
import sys
import unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ranking import (  # noqa: E402
    DATASETS,
    forbidden_benchmark_rank_average,
    quality_unit,
    rank_metric,
    rank_sheet,
    six_mean,
)
from synthetic import (  # noqa: E402
    EXAMPLE_INPUT_LABEL,
    LATENCY_COPY,
    METHOD_IDS,
    build_sheet,
    build_sheets,
)


def _put(sheet, method, dataset, metric, mean, **extra):
    cell = sheet["cells"][method][dataset][metric]
    cell["mean"] = str(mean)
    cell.update(extra)


class RuleTests(unittest.TestCase):
    def test_spearman_and_ndcg_units_are_not_min_max(self):
        self.assertEqual(quality_unit("-1", "spearman"), Decimal("0"))
        self.assertEqual(quality_unit("1", "spearman"), Decimal("1"))
        self.assertEqual(quality_unit("0.5", "ndcg@10"), Decimal("0.5"))
        with self.assertRaises(ValueError):
            quality_unit("1.1", "ndcg@10")
        with self.assertRaises(ValueError):
            quality_unit("0.5", "mystery")

    def test_std_does_not_split_a_dataset_tie(self):
        sheet = build_sheet("Qwen3.5-9B", "full")
        traced = rank_metric(sheet, "quality")
        self.assertEqual(
            traced["per_dataset_midrank"]["DL20"]["sw"],
            traced["per_dataset_midrank"]["DL20"]["lt"],
        )
        self.assertNotEqual(
            sheet["cells"]["sw"]["DL20"]["quality"]["permutation_std"],
            sheet["cells"]["lt"]["DL20"]["quality"]["permutation_std"],
        )

    def test_pointwise_integer_is_not_the_rounded_average(self):
        sheet = build_sheet("Qwen3.5-9B", "full")
        traced = rank_metric(sheet, "quality")
        self.assertEqual(Fraction(traced["average_rank"]["pointwise"]), Fraction(3, 2))
        self.assertEqual(traced["integer"]["pointwise"], 1)
        self.assertNotEqual(traced["integer"]["pointwise"], 2)

    def test_token_tie_uses_six_mean_not_benchmark_votes(self):
        sheet = build_sheet("Qwen3.5-9B", "full")
        traced = rank_metric(sheet, "tokens")
        self.assertEqual(
            Fraction(traced["average_rank"]["listk"]),
            Fraction(traced["average_rank"]["tournament"]),
        )
        self.assertLess(traced["integer"]["tournament"], traced["integer"]["listk"])
        forbidden = forbidden_benchmark_rank_average(sheet)
        self.assertLess(forbidden["listk"], forbidden["tournament"])

    def test_identical_latency_vector_shares_the_integer(self):
        """The old display copy, kept only as an input. Equal evidence stays tied."""
        sheet = build_sheet("Qwen3.5-9B", "full")
        for dataset, mean in zip(DATASETS, LATENCY_COPY["before"]["sw"]):
            _put(sheet, "sw", dataset, "latency", mean, n_repeats=1, repeat_variance=None)
            _put(sheet, "lt", dataset, "latency", mean, n_repeats=1, repeat_variance=None)
        traced = rank_metric(sheet, "latency")
        self.assertEqual(traced["integer"]["sw"], traced["integer"]["lt"])
        self.assertEqual(traced["integer"]["sw"], 9)
        self.assertNotIn(10, set(traced["integer"].values()))
        self.assertEqual(
            traced["residual_groups"][-1]["by"],
            "identical-evidence",
        )

    def test_display_sheets_print_latency_places_1_through_10(self):
        sheet = build_sheet("Qwen3.5-9B", "full")
        self.assertEqual(sheet["example_input_label"], EXAMPLE_INPUT_LABEL)
        sw = [sheet["cells"]["sw"][dataset]["latency"]["mean"] for dataset in DATASETS]
        lt = [sheet["cells"]["lt"][dataset]["latency"]["mean"] for dataset in DATASETS]
        self.assertEqual(sw, LATENCY_COPY["after"]["sw"])
        self.assertEqual(lt, LATENCY_COPY["after"]["lt"])
        self.assertNotEqual(sw, lt)
        for (_model, _demand), printed in build_sheets().items():
            traced = rank_metric(printed, "latency")
            self.assertEqual(sorted(traced["integer"].values()), list(range(1, 11)))

    def test_missing_dataset_is_ineligible_not_reweighted(self):
        sheet = build_sheet("Qwen3.5-9B", "full")
        before = rank_metric(sheet, "quality")["integer"]["ext_pointwise"]
        sheet["cells"]["pointwise"]["Q9"]["quality"]["mean"] = None
        traced = rank_metric(sheet, "quality")
        self.assertIsNone(traced["integer"]["pointwise"])
        self.assertIsNotNone(traced["integer"]["ext_pointwise"])
        self.assertEqual(len(traced["per_dataset_midrank"]["Q9"]), 9)
        self.assertNotEqual(traced["integer"]["ext_pointwise"], before)

    def test_names_do_not_order_identical_evidence(self):
        sheet = build_sheet("Qwen3.5-9B", "full")
        for dataset in DATASETS:
            for metric in ("quality", "tokens", "latency"):
                _copy_cell(sheet, "bubble", "merge", dataset, metric)
        forward = rank_metric(sheet, "quality")
        flipped = copy.deepcopy(sheet)
        flipped["methods"] = list(reversed(sheet["methods"]))
        backward = rank_metric(flipped, "quality")
        self.assertEqual(forward["integer"]["bubble"], forward["integer"]["merge"])
        self.assertEqual(forward["integer"], backward["integer"])

    def test_single_run_variance_does_not_split(self):
        sheet = build_sheet("Qwen3.5-9B", "full")
        for dataset in DATASETS:
            _copy_cell(sheet, "bubble", "merge", dataset, "tokens")
            sheet["cells"]["bubble"][dataset]["tokens"]["repeat_variance"] = "1"
            sheet["cells"]["merge"][dataset]["tokens"]["repeat_variance"] = "9"
        traced = rank_metric(sheet, "tokens")
        self.assertEqual(traced["integer"]["bubble"], traced["integer"]["merge"])

    def test_std_splits_only_after_the_vectors_match(self):
        sheet = build_sheet("Qwen3.5-9B", "full")
        for dataset in DATASETS:
            _copy_cell(sheet, "bubble", "merge", dataset, "quality")
            sheet["cells"]["bubble"][dataset]["quality"]["permutation_std"] = "0.040"
            sheet["cells"]["merge"][dataset]["quality"]["permutation_std"] = "0.010"
        traced = rank_metric(sheet, "quality")
        self.assertLess(traced["integer"]["merge"], traced["integer"]["bubble"])

    def test_all_missing_permutation_counts_do_not_use_std(self):
        sheet = build_sheet("Qwen3.5-9B", "full")
        for dataset in DATASETS:
            _copy_cell(sheet, "bubble", "merge", dataset, "quality")
            sheet["cells"]["bubble"][dataset]["quality"]["permutation_std"] = "0.040"
            sheet["cells"]["merge"][dataset]["quality"]["permutation_std"] = "0.010"
            sheet["cells"]["bubble"][dataset]["quality"]["n_permutations"] = None
            sheet["cells"]["merge"][dataset]["quality"]["n_permutations"] = None
        traced = rank_metric(sheet, "quality")
        self.assertEqual(traced["integer"]["bubble"], traced["integer"]["merge"])

    def test_missing_repeat_count_does_not_use_latency_variance(self):
        sheet = build_sheet("Qwen3.5-9B", "full")
        for dataset in DATASETS:
            _copy_cell(sheet, "bubble", "merge", dataset, "latency")
            for method, variance in (("bubble", "4"), ("merge", "1")):
                cell = sheet["cells"][method][dataset]["latency"]
                cell["n_repeats"] = None
                cell["repeat_variance"] = variance
        traced = rank_metric(sheet, "latency")
        self.assertEqual(traced["integer"]["bubble"], traced["integer"]["merge"])

    def test_incomplete_repeat_count_blocks_the_std_key(self):
        sheet = build_sheet("Qwen3.5-9B", "full")
        for dataset in DATASETS:
            _copy_cell(sheet, "bubble", "merge", dataset, "quality")
            sheet["cells"]["bubble"][dataset]["quality"]["permutation_std"] = "0.040"
            sheet["cells"]["merge"][dataset]["quality"]["permutation_std"] = "0.010"
            sheet["cells"]["bubble"][dataset]["quality"]["n_permutations"] = 10
            sheet["cells"]["merge"][dataset]["quality"]["n_permutations"] = 1
        traced = rank_metric(sheet, "quality")
        self.assertEqual(traced["integer"]["bubble"], traced["integer"]["merge"])

    def test_repeat_variance_can_split_when_legal_for_every_member(self):
        sheet = build_sheet("Qwen3.5-9B", "full")
        for dataset in DATASETS:
            _copy_cell(sheet, "bubble", "merge", dataset, "latency")
            for method, variance in (("bubble", "4"), ("merge", "1")):
                cell = sheet["cells"][method][dataset]["latency"]
                cell["n_repeats"] = 3
                cell["repeat_variance"] = variance
        traced = rank_metric(sheet, "latency")
        self.assertLess(traced["integer"]["merge"], traced["integer"]["bubble"])

    def test_printed_sheets_stay_inside_the_declared_ranges(self):
        sheets = build_sheets()
        self.assertEqual(len(sheets), 4)
        for (model, demand), sheet in sheets.items():
            self.assertTrue(sheet["synthetic"])
            self.assertEqual(
                sheet["quality_metric"],
                "spearman" if demand == "full" else "ndcg@10",
            )
            traced = rank_sheet(sheet)
            for metric in traced:
                places = [value for value in traced[metric]["integer"].values() if value]
                self.assertEqual(min(places), 1)
                self.assertLessEqual(max(places), 10)
            for method in METHOD_IDS:
                tokens = [
                    Decimal(sheet["cells"][method][dataset]["tokens"]["mean"])
                    for dataset in DATASETS
                ]
                self.assertEqual(len(tokens), 6)
                self.assertEqual(
                    six_mean(tokens),
                    sum(tokens, Decimal(0)) / 6,
                )


def _copy_cell(sheet, source, dest, dataset, metric):
    sheet["cells"][dest][dataset][metric] = copy.deepcopy(
        sheet["cells"][source][dataset][metric]
    )


if __name__ == "__main__":
    unittest.main()
