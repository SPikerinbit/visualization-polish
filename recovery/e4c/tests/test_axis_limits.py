"""Off/On axis limits are one range, taken from every mean in that metric."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from layout import point_segment_distance, rect_hits_circle, rects_overlap  # noqa: E402
from limits import (  # noqa: E402
    PAD_FRAC,
    data_occupancy,
    format_quality,
    format_token,
    limits_from_values,
)
from plot_e4c import render_all  # noqa: E402
from sample_means import METHODS, POINTS, points_for  # noqa: E402

PANEL_SPAN_FLOOR = 0.58


class LimitContract(unittest.TestCase):
    def test_one_mean_per_method_and_no_query_points(self):
        self.assertEqual(len(METHODS), 10)
        self.assertEqual(len(POINTS), 80)
        self.assertTrue(all(isinstance(value, tuple) and len(value) == 2 for value in POINTS.values()))
        for metric in ("full", "topk"):
            for dataset in ("DL20", "COVID"):
                for state in ("Off", "On-cold"):
                    rows = points_for(metric, dataset, state)
                    self.assertEqual(sorted(row["method"] for row in rows), sorted(method["id"] for method in METHODS))

    def test_pair_limits_use_every_mean_in_the_metric_only(self):
        for metric in ("full", "topk"):
            rows = points_for(metric)
            xlim = limits_from_values([row["x"] for row in rows], PAD_FRAC)
            ylim = limits_from_values([row["y"] for row in rows], PAD_FRAC)
            self.assertAlmostEqual(data_occupancy([row["x"] for row in rows]), 1 / (1 + 2 * PAD_FRAC), places=6)
            self.assertGreater(data_occupancy([row["y"] for row in rows]), 0.7)
            for dataset in ("DL20", "COVID"):
                for state in ("Off", "On-cold"):
                    panel = points_for(metric, dataset, state)
                    xs = [row["x"] for row in panel]
                    ys = [row["y"] for row in panel]
                    self.assertGreaterEqual((max(xs) - min(xs)) / (xlim[1] - xlim[0]), PANEL_SPAN_FLOOR)
                    self.assertGreaterEqual((max(ys) - min(ys)) / (ylim[1] - ylim[0]), PANEL_SPAN_FLOOR)
                    self.assertLessEqual(max(xs), xlim[1])
                    self.assertGreaterEqual(min(xs), xlim[0])
        full_y = limits_from_values([row["y"] for row in points_for("full")])
        mixed_y = limits_from_values([row["y"] for row in points_for("full")] + [row["y"] for row in points_for("topk")])
        self.assertNotEqual(tuple(round(v, 6) for v in full_y), tuple(round(v, 6) for v in mixed_y))

    def test_rendered_pairs_share_complete_tick_labels(self):
        payload = render_all()
        by_metric = {}
        for report in payload["reports"]:
            by_metric.setdefault(report["metric"], []).append(report)
            panels = list(report["panels"].values())
            self.assertEqual(len(panels), 4)
            limits = report["limits"]
            self.assertGreaterEqual(len(limits["xticklabels"]), 4)
            self.assertGreaterEqual(len(limits["yticklabels"]), 4)
            for label, tick in zip(limits["xticklabels"], limits["xticks"]):
                self.assertEqual(label, format_token(tick))
                self.assertNotIn("e", label.lower())
                self.assertNotIn("+", label)
            for label, tick in zip(limits["yticklabels"], limits["yticks"]):
                self.assertEqual(label, format_quality(tick))
                self.assertRegex(label, r"^\d\.\d\d$")
            for panel in panels:
                self.assertEqual(panel["xticklabels"], limits["xticklabels"])
                self.assertEqual(panel["yticklabels"], limits["yticklabels"])
                self.assertAlmostEqual(panel["xlim"][0], limits["xlim"][0])
                self.assertAlmostEqual(panel["xlim"][1], limits["xlim"][1])
                self.assertAlmostEqual(panel["ylim"][0], limits["ylim"][0])
                self.assertAlmostEqual(panel["ylim"][1], limits["ylim"][1])
                self.assertEqual(panel["n_scatters"], 10)
                self.assertEqual(panel["dashed"], [])
                self._assert_marks_and_labels(panel)
            pdf = Path(report["pdf"]).read_bytes()
            self.assertTrue(pdf.startswith(b"%PDF"))
            self.assertIn(b"/Type /Font", pdf)
            png = Path(report["png"]).read_bytes()
            self.assertTrue(png.startswith(b"\x89PNG"))
        for metric, reports in by_metric.items():
            self.assertEqual(reports[0]["limits"], reports[1]["limits"])
            self.assertEqual({report["style"] for report in reports}, {"numbered", "labeled"})
        saved = json.loads((ROOT / "data" / "synthetic_means.json").read_text(encoding="utf-8"))
        self.assertFalse(saved["per_query_points"])
        self.assertFalse(saved["pareto_line"])
        self.assertEqual(len(saved["points"]), 80)
        self.assertFalse(any("query" in point for point in saved["points"]))

    def _assert_marks_and_labels(self, panel):
        markers = panel["markers"]
        for left in markers:
            for right in markers:
                if left["method"] >= right["method"]:
                    continue
                dist = ((left["x"] - right["x"]) ** 2 + (left["y"] - right["y"]) ** 2) ** 0.5
                self.assertGreater(dist, left["r"] + right["r"] + 0.8, left["method"])
        boxes = [tuple(item["bbox"]) for item in panel["labels"]]
        self.assertEqual(len(boxes), 10)
        for i, box in enumerate(boxes):
            for other in boxes[i + 1 :]:
                self.assertFalse(rects_overlap(box, other, 0.4))
            for marker in markers:
                self.assertFalse(rect_hits_circle(box, marker["x"], marker["y"], marker["r"], 0.4))
        for seg in panel["leaders"]:
            x1, y1, x2, y2 = seg
            owner = min(markers, key=lambda marker: min(
                (marker["x"] - x1) ** 2 + (marker["y"] - y1) ** 2,
                (marker["x"] - x2) ** 2 + (marker["y"] - y2) ** 2,
            ))
            for marker in markers:
                dist = point_segment_distance(marker["x"], marker["y"], x1, y1, x2, y2)
                if marker is owner:
                    self.assertGreaterEqual(dist, marker["r"] - 1.3)
                else:
                    self.assertGreaterEqual(dist, marker["r"] + 0.6)

    def test_includable_tex_is_not_a_display_document(self):
        tex = (ROOT / "tex" / "exp4c.tex").read_text(encoding="utf-8")
        self.assertNotIn(r"\documentclass", tex)
        self.assertIn("No Pareto curve is drawn.", tex)
        self.assertNotIn("Pareto frontier", tex)
        self.assertNotIn("frontier", tex.lower())
        self.assertIn("synthetic", tex.lower())
        self.assertEqual(tex.count("width=178mm"), 4)
        for name in (
            "exp4c-full-numbered.pdf",
            "exp4c-full-labeled.pdf",
            "exp4c-topk-numbered.pdf",
            "exp4c-topk-labeled.pdf",
        ):
            self.assertIn(name, tex)
        self.assertIn(r"\begin{figure*}", tex)


if __name__ == "__main__":
    unittest.main()
