"""Ranking and TeX checks. Passing these is not a visual acceptance."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import emit
import ranking
import synthetic
from catalog import DATASETS, METHOD_IDS, METRICS


class RankingTests(unittest.TestCase):
    def test_quality_uses_unrounded_mean_before_perm_std(self):
        ranks = ranking.rank_quality({
            "a": {"mean": 0.5014, "permutation_std": 0.02, "n_permutations": 10},
            "b": {"mean": 0.5006, "permutation_std": 0.01, "n_permutations": 10},
            "c": {"mean": 0.40, "permutation_std": 0.0, "n_permutations": 10},
        })
        self.assertLess(ranks["a"], ranks["b"])
        self.assertLess(ranks["b"], ranks["c"])
        self.assertEqual(f"{0.5014:.3f}", f"{0.5006:.3f}")
        marks = ranking.emphasis(ranks)
        self.assertEqual(marks["a"], "first")
        self.assertEqual(marks["b"], "second")

    def test_exact_quality_tie_averages_the_places(self):
        ranks = ranking.rank_quality({
            "sw": {"mean": 0.62, "permutation_std": 0.03, "n_permutations": 10},
            "lt": {"mean": 0.62, "permutation_std": 0.03, "n_permutations": 10},
            "bubble": {"mean": 0.61, "permutation_std": 0.02, "n_permutations": 10},
        })
        self.assertEqual(ranks["sw"], 1.5)
        self.assertEqual(ranks["lt"], 1.5)
        self.assertEqual(ranks["bubble"], 3)
        marks = ranking.emphasis(ranks)
        self.assertEqual(marks["sw"], "first")
        self.assertEqual(marks["lt"], "first")
        self.assertEqual(marks["bubble"], "second")

    def test_perm_std_requires_every_member(self):
        ranks = ranking.rank_quality({
            "a": {"mean": 0.5, "permutation_std": 0.01, "n_permutations": 10},
            "b": {"mean": 0.5, "permutation_std": None, "n_permutations": None},
        })
        self.assertEqual(ranks["a"], 1.5)
        self.assertEqual(ranks["b"], 1.5)

    def test_single_permutation_does_not_unlock_std(self):
        ranks = ranking.rank_quality({
            "a": {"mean": 0.5, "permutation_std": 0.01, "n_permutations": 1},
            "b": {"mean": 0.5, "permutation_std": 0.20, "n_permutations": 10},
        })
        self.assertEqual(ranks["a"], 1.5)
        self.assertEqual(ranks["b"], 1.5)

    def test_smaller_perm_std_wins_an_exact_mean_tie(self):
        ranks = ranking.rank_quality({
            "lotus": {"mean": 0.455, "permutation_std": 0.012, "n_permutations": 10},
            "tournament": {"mean": 0.455, "permutation_std": 0.040, "n_permutations": 10},
            "other": {"mean": 0.400, "permutation_std": 0.001, "n_permutations": 10},
        })
        self.assertEqual(ranks["lotus"], 1)
        self.assertEqual(ranks["tournament"], 2)
        self.assertEqual(ranking.emphasis(ranks)["tournament"], "second")

    def test_negative_spearman_ranks_downward(self):
        ranks = ranking.rank_quality({
            "a": {"mean": -0.1, "permutation_std": 0.2, "n_permutations": 10},
            "b": {"mean": -0.2, "permutation_std": 0.0, "n_permutations": 10},
        })
        self.assertLess(ranks["a"], ranks["b"])

    def test_single_run_variance_is_ignored_and_quality_breaks_the_tie(self):
        cells = {
            "bubble": {"mean": 10.0, "n_repeats": 1, "repeat_variance": 0.01},
            "merge": {"mean": 10.0, "n_repeats": 1, "repeat_variance": 99.0},
        }
        ranks = ranking.rank_cost(cells, {"bubble": 0.2, "merge": 0.9})
        self.assertLess(ranks["merge"], ranks["bubble"])

    def test_legal_variance_beats_quality_and_equal_variance_stays_tied(self):
        cells = {
            "a": {"mean": 10.0, "n_repeats": 3, "repeat_variance": 2.0},
            "b": {"mean": 10.0, "n_repeats": 3, "repeat_variance": 1.0},
        }
        ranks = ranking.rank_cost(cells, {"a": 0.9, "b": 0.1})
        self.assertLess(ranks["b"], ranks["a"])
        tied = ranking.rank_cost(
            {
                "a": {"mean": 10.0, "n_repeats": 4, "repeat_variance": 1.0},
                "b": {"mean": 10.0, "n_repeats": 4, "repeat_variance": 1.0},
            },
            {"a": 0.9, "b": 0.1},
        )
        self.assertEqual(tied["a"], 1.5)
        self.assertEqual(tied["b"], 1.5)

    def test_variance_must_be_legal_for_every_member(self):
        cells = {
            "a": {"mean": 10.0, "n_repeats": 3, "repeat_variance": 1.0},
            "b": {"mean": 10.0, "n_repeats": 1, "repeat_variance": 5.0},
        }
        ranks = ranking.rank_cost(cells, {"a": 0.2, "b": 0.8})
        self.assertLess(ranks["b"], ranks["a"])

    def test_missing_quality_does_not_partially_break_a_cost_tie(self):
        cells = {
            "a": {"mean": 10.0, "n_repeats": 1, "repeat_variance": None},
            "b": {"mean": 10.0, "n_repeats": 1, "repeat_variance": None},
        }
        ranks = ranking.rank_cost(cells, {"a": 0.9, "b": None})
        self.assertEqual(ranks["a"], 1.5)
        self.assertEqual(ranks["b"], 1.5)

    def test_missing_mean_is_omitted_from_the_average(self):
        per = {"d1": {"a": 1.0, "b": 2.0}, "d2": {"b": 1.0}}
        self.assertEqual(ranking.average_rank(per, "a"), 1.0)
        self.assertEqual(ranking.average_rank(per, "b"), 1.5)
        ranks = ranking.rank_quality({
            "a": {"mean": None, "permutation_std": None},
            "b": {"mean": 0.2, "permutation_std": 0.1, "n_permutations": 10},
        })
        self.assertNotIn("a", ranks)

    def test_cost_direction_is_ascending(self):
        ranks = ranking.rank_cost(
            {
                "a": {"mean": 3.0, "n_repeats": 1, "repeat_variance": None},
                "b": {"mean": 1.0, "n_repeats": 1, "repeat_variance": None},
            },
            {"a": 0.1, "b": 0.1},
        )
        self.assertLess(ranks["b"], ranks["a"])


class SheetTests(unittest.TestCase):
    def setUp(self):
        self.sheets = { (s["model"], s["demand"]): s for s in synthetic.build_all() }

    def test_nine_full_plants(self):
        sheet = self.sheets[("Qwen3.5-9B", "full")]
        ranked = ranking.rank_sheet(sheet)
        q9 = ranked["per"]["quality"]["Q9"]
        self.assertLess(q9["pointwise"], q9["ext_pointwise"])
        self.assertEqual(f"{sheet['cells']['pointwise']['Q9']['quality']['mean']:.3f}", "0.501")
        self.assertEqual(f"{sheet['cells']['ext_pointwise']['Q9']['quality']['mean']:.3f}", "0.501")
        self.assertEqual(ranked["per"]["quality"]["DL20"]["sw"], 1.5)
        self.assertEqual(ranked["per"]["quality"]["DL20"]["lt"], 1.5)
        self.assertEqual(ranked["marks"]["quality"]["DL20"]["bubble"], "second")
        db = ranked["per"]["quality"]["DBpedia"]
        self.assertLess(db["lotus"], db["tournament"])
        tokens = ranked["per"]["tokens"]["COVID"]
        self.assertLess(tokens["lt"], tokens["sw"])
        self.assertEqual(emit.fmt_token(12000), "12")
        latency = ranked["per"]["latency"]["DL22"]
        self.assertLess(latency["lt"], latency["sw"])
        self.assertEqual(emit.fmt_latency(2.24), "2.2")
        self.assertEqual(emit.fmt_latency(2.16), "2.2")
        self.assertNotIn("setwise", ranked["per"]["quality"]["Robust04"])
        self.assertEqual(ranked["avg"]["quality"]["setwise"] is not None, True)
        covered = sum(method in ranked["per"]["quality"][d] for d in DATASETS for method in ["setwise"])
        self.assertEqual(covered, 5)

    def test_illegal_stored_variance_does_not_win(self):
        sheet = self.sheets[("Qwen3.8-27B", "full")]
        ranked = ranking.rank_sheet(sheet)
        self.assertEqual(sheet["cells"]["bubble"]["Q9"]["tokens"]["n_repeats"], 1)
        self.assertEqual(sheet["cells"]["bubble"]["Q9"]["tokens"]["repeat_variance"], 9.0)
        self.assertLess(ranked["per"]["tokens"]["Q9"]["bubble"], ranked["per"]["tokens"]["Q9"]["merge"])

    def test_no_cell_prints_a_cost_std(self):
        for sheet in self.sheets.values():
            for method in sheet["methods"]:
                for dataset in sheet["datasets"]:
                    for metric in ("tokens", "latency"):
                        cell = sheet["cells"][method][dataset][metric]
                        if cell["mean"] is None:
                            continue
                        shown = emit.fmt_token(cell["mean"]) if metric == "tokens" else emit.fmt_latency(cell["mean"])
                        self.assertNotIn("pm", shown)
                        self.assertNotIn("±", shown)
                        if cell["n_repeats"] == 1:
                            self.assertTrue(cell["repeat_variance"] is None or cell["n_repeats"] < 2)

    def test_json_roundtrip_keeps_ranks(self):
        sheet = self.sheets[("Qwen3.5-9B", "limit10")]
        again = json.loads(json.dumps(sheet))
        self.assertEqual(ranking.rank_sheet(sheet), ranking.rank_sheet(again))

    def test_limit_names_and_std_tie(self):
        sheet = self.sheets[("Qwen3.5-9B", "limit10")]
        ranked = ranking.rank_sheet(sheet)
        db = ranked["per"]["quality"]["DBpedia"]
        self.assertLess(db["sw"], db["lt"])
        self.assertEqual(emit.row_name_for("listk", "limit10"), "ListK Select")


class EmitTests(unittest.TestCase):
    def setUp(self):
        self.sheets = synthetic.build_all()

    def test_row_names(self):
        from catalog import row_name
        self.assertEqual(row_name("listk", "full"), "ListK Sort")
        self.assertEqual(row_name("listk", "limit10"), "ListK Select")
        self.assertEqual(row_name("lt", "full"), "LT")

    def test_main_tex_contract(self):
        full = "\n".join(emit.emit_stacked(s) for s in self.sheets if s["demand"] == "full")
        limit = "\n".join(emit.emit_stacked(s) for s in self.sheets if s["demand"] == "limit10")
        one = emit.emit_stacked(next(s for s in self.sheets if s["model"] == "Qwen3.5-9B" and s["demand"] == "full"))
        for tex, name in ((full, "ListK Sort"), (limit, "ListK Select")):
            self.assertIn(name, tex)
            self.assertIn("Synthetic layout numbers, not experimental results.", tex)
            self.assertIn("awaits contract sign-off", tex)
            self.assertIn("table*", tex)
            self.assertNotIn("SLT", tex)
            self.assertNotIn("Segmented", tex)
            self.assertNotIn("Movies", tex)
            self.assertIn("Q9", tex)
            self.assertIn("Robust04", tex)
            self.assertIn("Avg.\\ Rank", tex)
        self.assertEqual(one.count(r"\begin{tabular}"), 2)
        self.assertNotIn(r"\makebox[\textwidth]", one)
        self.assertIn(r"0.105\textwidth", one)
        self.assertIn(r"\small", one)
        self.assertNotIn(r"\footnotesize", one)
        self.assertIn(r"\cmidrule", one)
        self.assertIn("Spearman", full)
        self.assertIn("NDCG@10", limit)
        self.assertNotIn("nDCG@10", full)
        self.assertIn(r"\label{tab:exp1-full}", full)
        self.assertIn(r"\label{tab:exp1-topk}", limit)
        nine = next(s for s in self.sheets if s["model"] == "Qwen3.5-9B" and s["demand"] == "full")
        wide = emit.emit_wide(nine, "inline")
        self.assertIn("PROBE, not for inclusion", wide)
        self.assertGreater(wide.count("Q9"), 0)
        self.assertGreater(wide.count("&"), full.count("&") / 4)

    def test_static_tables_do_not_invent_results(self):
        datasets = emit.datasets_tex()
        self.assertIn("Not experimental.", datasets)
        self.assertIn("DBpedia-Entity", datasets)
        self.assertIn("Robust04", datasets)
        data_rows = datasets.split(r"\begin{tabular}")[1]
        self.assertNotIn("FiQA", data_rows)
        self.assertNotIn("Movies", data_rows)
        self.assertNotIn("FiQA", data_rows)
        algs = emit.algorithms_tex()
        self.assertIn("ListK Sort/Select", algs)
        self.assertIn("LT($h$)", algs)
        self.assertNotIn("Segmented Loser", algs)
        self.assertIn("---", algs)
        params = emit.params_tex()
        self.assertIn("tab:params-full", params)
        self.assertIn("disabled", params)
        self.assertIn("$h{=}1$", params)
        self.assertEqual(params.count("mathrm{bin}"), 1)
        self.assertIn("not two algorithms", params)
        validation = emit.validation_tex()
        self.assertNotIn("4.78", validation)
        self.assertNotIn("13.14", validation)
        self.assertNotIn("Binary", validation.split(r"\begin{tabular}")[1])
        self.assertIn("---", validation)
        dormant = emit.symbols_dormant_tex()
        self.assertTrue(dormant.strip().startswith("%"))
        self.assertIn(r"\iffalse", dormant)
        self.assertIn(r"\label{tab:params}", dormant)
        self.assertNotIn(r"\label{tab:params-full}", dormant)

    def test_checkpoint_writer_and_real_caption_hook(self):
        root = Path(__file__).resolve().parents[1]
        emit.write_checkpoint(root)
        self.assertTrue((root / "tex" / "exp1-full.tex").exists())
        self.assertTrue((root / "data" / "Qwen3.5-9B-full.json").exists())
        measured = json.loads((root / "data" / "Qwen3.5-9B-full.json").read_text())
        measured["synthetic"] = False
        tex = emit.emit_stacked(measured)
        self.assertNotIn("Synthetic layout numbers", tex)
        self.assertIn("permutation std", tex)
        with self.assertRaises(ValueError):
            bad = json.loads(json.dumps(measured))
            bad["methods"] = ["slt"] + bad["methods"][1:]
            emit.check_sheet(bad)

    def test_json_to_tex_marks_match_ranker(self):
        mismatches = []
        for sheet in self.sheets:
            ranked = ranking.rank_sheet(sheet)
            for dataset in DATASETS:
                for metric in METRICS:
                    marks = ranked["marks"][metric][dataset]
                    for method in sheet["methods"]:
                        cell = sheet["cells"][method][dataset][metric]
                        if cell.get("mean") is None:
                            continue
                        expected = marks.get(method, "none")
                        tex = emit.metric_tex(sheet, ranked, method, dataset, metric, "inline")
                        has_bold = "\\textbf" in tex or "\\boldmath" in tex
                        has_under = "\\underline" in tex
                        if expected == "first" and not has_bold:
                            mismatches.append((sheet["model"], sheet["demand"], dataset, metric, method, "first", tex))
                        if expected == "second" and not has_under:
                            mismatches.append((sheet["model"], sheet["demand"], dataset, metric, method, "second", tex))
            for metric in METRICS:
                marks = ranked["avg_marks"][metric]
                for method in sheet["methods"]:
                    if ranked["avg"][metric][method] is None:
                        continue
                    expected = marks.get(method, "none")
                    tex = emit.avg_tex(ranked, method, metric)
                    has_bold = "\\textbf" in tex
                    has_under = "\\underline" in tex
                    if expected == "first" and not has_bold:
                        mismatches.append((sheet["model"], sheet["demand"], "avg", metric, method, "first", tex))
                    if expected == "second" and not has_under:
                        mismatches.append((sheet["model"], sheet["demand"], "avg", metric, method, "second", tex))
        self.assertEqual(mismatches, [], msg=f"{len(mismatches)} mark mismatches")

    def test_printed_cost_ties_are_only_the_plants(self):
        allowed = {
            ("Qwen3.5-9B", "full", "COVID", "tokens", frozenset({"sw", "lt"})),
            ("Qwen3.5-9B", "full", "DL22", "latency", frozenset({"sw", "lt"})),
            ("Qwen3.8-27B", "full", "Q9", "tokens", frozenset({"bubble", "merge"})),
            ("Qwen3.5-9B", "limit10", "DL20", "latency", frozenset({"bubble", "merge"})),
            ("Qwen3.8-27B", "limit10", "DL20", "tokens", frozenset({"pointwise", "ext_pointwise"})),
        }
        found = set()
        for sheet in self.sheets:
            ranked = ranking.rank_sheet(sheet)
            for dataset in sheet["datasets"]:
                for metric in ("tokens", "latency"):
                    groups = {}
                    for method in sheet["methods"]:
                        cell = sheet["cells"][method][dataset][metric]
                        if cell["mean"] is None:
                            continue
                        shown = emit.fmt_token(cell["mean"]) if metric == "tokens" else emit.fmt_latency(cell["mean"])
                        groups.setdefault(shown, []).append(method)
                    for names in groups.values():
                        if len(names) < 2:
                            continue
                        ranks = {ranked["per"][metric][dataset][name] for name in names}
                        if len(ranks) > 1:
                            found.add((sheet["model"], sheet["demand"], dataset, metric, frozenset(names)))
        self.assertEqual(found, allowed)


class RowNameTests(unittest.TestCase):
    def test_alias_used_above(self):
        self.assertEqual(METHOD_IDS.count("listk"), 1)
        self.assertEqual(METHOD_IDS.count("lt"), 1)
        self.assertNotIn("slt", METHOD_IDS)


def row_name_for(method, demand):
    from catalog import row_name
    return row_name(method, demand)


emit.row_name_for = row_name_for


if __name__ == "__main__":
    unittest.main()
