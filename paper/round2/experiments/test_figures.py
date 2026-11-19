"""Data and stroke checks for the round-2 experiment figures."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from legal import initial_runs, is_legal, upper_k
from pdfutil import assert_has_width, media_box
from style import COLUMN_PT, TEXT_PT, printed

ROOT = Path(__file__).resolve().parent


class LegalDomainTest(unittest.TestCase):
    def test_n100_rejects_k8_and_n500_accepts_it(self):
        self.assertEqual(initial_runs(100, 20), 5)
        self.assertEqual(initial_runs(500, 20), 25)
        self.assertLess(upper_k("SW", 100), 8)
        self.assertLess(upper_k("LT", 100), 8)
        self.assertFalse(is_legal("SW", 8, 1, 100))
        self.assertFalse(is_legal("LT", 8, 2, 100))
        self.assertTrue(is_legal("SW", 8, 1, 500))
        self.assertTrue(is_legal("SW", 8, 2, 500))
        self.assertTrue(is_legal("LT", 8, 2, 500))
        self.assertTrue(is_legal("SW", 5, 2, 100))


class FigureContractTest(unittest.TestCase):
    def test_e3_box_and_split(self):
        facts = json.loads((ROOT / "figures" / "e3" / "e3-facts.json").read_text())
        self.assertEqual(len(facts["panels"]), 8)
        kinds = [p["kind"] for p in facts["panels"]]
        self.assertEqual(kinds[:4], ["predicted"] * 4)
        self.assertEqual(kinds[4:], ["measured"] * 4)
        width, height = media_box(ROOT / "figures" / "e3" / "e3-sw-full-measured.pdf")
        self.assertAlmostEqual(width, printed(133.2, 0.25), delta=0.8)
        self.assertAlmostEqual(height, 62.0, delta=0.01)  # intentional E3 compact redesign
        assert_has_width(ROOT / "figures" / "e3" / "e3-sw-full-measured.pdf", facts["line_pt"])
        self.assertTrue(facts["supplements_not_drawn"])

    def test_e4a_n100_has_no_k8_and_n500_keeps_it(self):
        facts = json.loads((ROOT / "figures" / "e4a" / "e4a-facts.json").read_text())
        self.assertNotIn([8, 1], facts["n100_axis"])
        self.assertNotIn([8, 2], facts["n100_axis"])
        self.assertIn([8, 1], facts["n500_axis"])
        for panel in facts["panels"]:
            for role in ("off_measured", "off_predicted", "on_measured", "on_predicted"):
                k, h = panel[role]
                self.assertTrue(is_legal(panel["family"], k, h, panel["n"]))
        width, _height = media_box(ROOT / "figures" / "e4a" / "e4a-dl20-n100.pdf")
        self.assertAlmostEqual(width, COLUMN_PT, delta=1.0)
        assert_has_width(ROOT / "figures" / "e4a" / "e4a-dl20-n100.pdf", facts["line_pt"])

    def test_e4b_is_one_column_and_keeps_five_betas(self):
        facts = json.loads((ROOT / "figures" / "e4b" / "e4b-facts.json").read_text())
        self.assertEqual(facts["betas_drawn"], [0, 0.25, 0.5, 0.75, 1])
        self.assertFalse(facts["inset"])
        self.assertFalse(facts["color_bands"])
        width, _height = media_box(ROOT / "figures" / "e4b" / "e4b-beta.pdf")
        self.assertAlmostEqual(width, COLUMN_PT, delta=1.0)

    def test_e4c_average_and_frontier_vertices(self):
        facts = json.loads((ROOT / "figures" / "e4c" / "e4c-facts.json").read_text())
        for row in facts["means"]:
            self.assertAlmostEqual(row["x"], 0.5 * (row["x_dl20"] + row["x_covid"]))
            self.assertAlmostEqual(row["y"], 0.5 * (row["y_dl20"] + row["y_covid"]))
        self.assertEqual(len(facts["fronts"]), 4)
        for front in facts["fronts"]:
            vertices = front["vertices"]
            xs = [v["x"] for v in vertices]
            self.assertEqual(xs, sorted(xs))
            self.assertEqual(front["methods_in_order"], [v["method"] for v in vertices])
            if front["line_drawn"]:
                self.assertGreaterEqual(len(vertices), 2)
        width, _height = media_box(ROOT / "figures" / "e4c" / "e4c-quality-cost.pdf")
        self.assertAlmostEqual(width, COLUMN_PT, delta=1.0)

    def test_e5_is_full_width(self):
        facts = json.loads((ROOT / "figures" / "e5" / "e5-facts.json").read_text())
        self.assertFalse(facts["full_joined"])
        self.assertEqual(len(facts["columns"]), 4)
        width, _height = media_box(ROOT / "figures" / "e5" / "e5-limit-sweep.pdf")
        self.assertAlmostEqual(width, TEXT_PT, delta=1.0)
        assert_has_width(ROOT / "figures" / "e5" / "e5-limit-sweep.pdf", facts["line_pt"])


if __name__ == "__main__":
    unittest.main()
