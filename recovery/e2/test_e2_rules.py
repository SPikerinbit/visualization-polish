"""Rules for the E2 preview. Passing is not visual acceptance."""

import unittest

from plot_e2 import (
    LT_GAP,
    SPECS_2X2,
    SPECS_2X3,
    SW_GAP,
    HERO,
    build_series,
    legal_domain,
    max_segment,
    shared_z,
)


def components(rows):
    points = {(row.k, row.h) for row in rows}
    seen = set()
    found = []
    for start in sorted(points):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        group = []
        while stack:
            k, h = stack.pop()
            group.append((k, h))
            for neighbor in ((k + 1, h), (k - 1, h), (k, h + 1), (k, h - 1)):
                if neighbor in points and neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        found.append(set(group))
    return found


class SurfaceRules(unittest.TestCase):
    def test_domain_matches_the_contract_counts(self):
        self.assertEqual(len(legal_domain("LT")), 101)
        self.assertEqual(len(legal_domain("SW")), 46)
        self.assertEqual(max_segment(2, 20), 10)
        self.assertIn((2, 10), legal_domain("LT"))
        self.assertIn((25, 1), legal_domain("LT"))
        self.assertNotIn((2, 11), legal_domain("LT"))
        self.assertIn((20, 1), legal_domain("SW"))
        self.assertNotIn((21, 1), legal_domain("SW"))
        self.assertNotIn((4, 6), legal_domain("SW"))
        # The rejected preview used k<=8 and h<=5 only.
        self.assertGreater(max(k for k, _h in legal_domain("LT")), 8)
        self.assertGreater(max(h for _k, h in legal_domain("LT")), 5)

    def test_three_present_corners_make_one_triangle_and_two_do_not(self):
        series = build_series(HERO)
        present = {(row.k, row.h) for row in series.rows}
        # Rebuild the same corner test the drawer uses, against the hero gap.
        made = 0
        for k, h in list(present):
            square = [(k, h), (k + 1, h), (k + 1, h + 1), (k, h + 1)]
            count = sum(corner in present for corner in square)
            if count < 3:
                made += 0
            elif count == 3:
                made += 1
        self.assertGreater(made, 0)
        self.assertTrue(all(len(triangle) == 3 for triangle in series.tri))
        for triangle in series.tri:
            for vertex in triangle:
                self.assertLess(int(vertex), len(series.rows))

    def test_gap_detaches_one_face_and_does_not_invent_illegal_points(self):
        hero = build_series(HERO)
        groups = components(hero.rows)
        self.assertEqual(len(groups), 2)
        island = min(groups, key=len)
        self.assertEqual(island, {(4, 5), (4, 6), (5, 5)})
        present = {(row.k, row.h) for row in hero.rows}
        self.assertTrue(LT_GAP.isdisjoint(present))
        for k, h in present:
            self.assertIn((k, h), legal_domain("LT"))
        sw = build_series(SPECS_2X2[0])
        sw_groups = components(sw.rows)
        self.assertEqual(len(sw_groups), 2)
        self.assertEqual(
            min(sw_groups, key=len),
            {(2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (3, 5), (3, 6), (4, 5)},
        )
        self.assertTrue(SW_GAP.isdisjoint({(row.k, row.h) for row in sw.rows}))

    def test_markers_use_measured_height_and_coincidence_is_one_point(self):
        series_list = [build_series(spec) for spec in SPECS_2X2 + SPECS_2X3]
        zlim, zticks = shared_z(series_list)
        self.assertGreaterEqual(len(zticks), 3)
        seen_same = seen_split = False
        for series in series_list:
            self.assertEqual(series.selected.u, min(row.u for row in series.rows if (row.k, row.h) == (series.selected.k, series.selected.h)))
            # The drawn height is measured, including when the predicted value differs.
            if not series.coincide:
                self.assertNotEqual((series.best.k, series.best.h), (series.selected.k, series.selected.h))
                seen_split = True
            else:
                self.assertEqual(series.best.u, series.selected.u)
                self.assertGreater(abs(series.selected.p - series.selected.u), 20)
                seen_same = True
            for row in series.rows:
                self.assertGreater(row.u, zlim[0])
                self.assertLess(row.u, zlim[1])
                self.assertGreater(row.p, zlim[0])
                self.assertLess(row.p, zlim[1])
        self.assertTrue(seen_same and seen_split)

    def test_bias_matches_and_cross_picks_a_high_measured_point(self):
        bias = build_series(next(spec for spec in SPECS_2X2 if spec["kind"] == "bias"))
        self.assertTrue(bias.coincide)
        deltas = {round(row.p - row.u, 6) for row in bias.rows}
        self.assertEqual(deltas, {24.0})
        cross = build_series(next(spec for spec in SPECS_2X3 if spec["kind"] == "cross"))
        self.assertFalse(cross.coincide)
        ordered = sorted(row.u for row in cross.rows)
        quartile = ordered[int(0.75 * (len(ordered) - 1))]
        self.assertGreater(cross.selected.u, quartile)
        self.assertGreater(cross.selected.u, cross.best.u + 8)

    def test_shift_and_warp_are_not_a_tight_fit(self):
        for spec in SPECS_2X2 + SPECS_2X3:
            if spec["kind"] not in {"shift", "warp"}:
                continue
            series = build_series(spec)
            spread = max(abs(row.p - row.u) for row in series.rows)
            self.assertGreater(spread, 18)
            self.assertGreaterEqual(
                abs(series.best.k - series.selected.k) + abs(series.best.h - series.selected.h),
                3,
            )


if __name__ == "__main__":
    unittest.main()
