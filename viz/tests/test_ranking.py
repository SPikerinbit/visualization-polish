from pipeline.exp3 import SUPPLEMENT, fixed_keys, supplement_is_outside_fixed
from pipeline.ranking import average_rank, emphasis, rank_cost, rank_quality
from pipeline.replay import legal_surface_triangles, replay_segment
from pipeline.tables import rank_sheet, sheet


def test_quality_uses_unrounded_mean_then_perm_std():
    ranks = rank_quality({
        "a": {"mean": 0.5014, "permutation_std": 0.02},
        "b": {"mean": 0.5006, "permutation_std": 0.01},
        "c": {"mean": 0.40, "permutation_std": 0.0},
    })
    assert ranks["a"] < ranks["b"] < ranks["c"]
    assert f"{0.5014:.3f}" == f"{0.5006:.3f}"
    assert emphasis(ranks)["a"] == "first"
    assert emphasis(ranks)["b"] == "second"


def test_exact_quality_tie_uses_average_rank_and_shared_mark():
    ranks = rank_quality({
        "sw": {"mean": 0.62, "permutation_std": 0.03},
        "lt": {"mean": 0.62, "permutation_std": 0.03},
        "bubble": {"mean": 0.61, "permutation_std": 0.02},
    })
    assert ranks["sw"] == ranks["lt"] == 1.5
    assert ranks["bubble"] == 3
    marks = emphasis(ranks)
    assert marks["sw"] == marks["lt"] == "first"
    assert marks["bubble"] == "second"


def test_perm_std_ignored_unless_the_whole_tied_group_has_it():
    ranks = rank_quality({
        "a": {"mean": 0.5, "permutation_std": 0.01},
        "b": {"mean": 0.5, "permutation_std": None},
    })
    assert ranks["a"] == ranks["b"] == 1.5


def test_negative_spearman_ranks_downward():
    ranks = rank_quality({
        "a": {"mean": -0.1, "permutation_std": 0.2},
        "b": {"mean": -0.2, "permutation_std": 0.0},
    })
    assert ranks["a"] < ranks["b"]


def test_single_run_variance_is_not_legal_and_quality_breaks_the_tie():
    cells = {
        "sw": {"mean": 10.0, "n_repeats": 1, "repeat_variance": 0.01},
        "lt": {"mean": 10.0, "n_repeats": 1, "repeat_variance": 99.0},
    }
    ranks = rank_cost(cells, {"sw": 0.2, "lt": 0.9})
    assert ranks["lt"] < ranks["sw"]


def test_legal_repeat_variance_breaks_a_cost_tie_before_quality():
    cells = {
        "a": {"mean": 10.0, "n_repeats": 3, "repeat_variance": 2.0},
        "b": {"mean": 10.0, "n_repeats": 3, "repeat_variance": 1.0},
    }
    ranks = rank_cost(cells, {"a": 0.9, "b": 0.1})
    assert ranks["b"] < ranks["a"]


def test_missing_mean_is_omitted_from_the_average():
    per = {"d1": {"a": 1.0, "b": 2.0}, "d2": {"b": 1.0}}
    assert average_rank(per, "a") == 1.0
    assert average_rank(per, "b") == 1.5
    assert "a" not in rank_quality({"a": {"mean": None}, "b": {"mean": 0.2, "permutation_std": 0.1}})


def test_fixture_rounding_tie_and_hole():
    ranked = rank_sheet(sheet("Qwen3.5-9B", "full"))
    assert ranked["marks"]["quality"]["Q9"]["pointwise"] == "first"
    assert ranked["per"]["quality"]["Q9"]["pointwise"] < ranked["per"]["quality"]["Q9"]["ext_pointwise"]
    assert ranked["per"]["quality"]["DL20"]["sw"] == ranked["per"]["quality"]["DL20"]["lt"] == 1.5
    assert "setwise" not in ranked["per"]["quality"]["Robust04"]
    assert ranked["coverage"]["setwise"] == 5
    assert ranked["per"]["tokens"]["COVID"]["lt"] < ranked["per"]["tokens"]["COVID"]["sw"]
    for method in ranked["per"]["latency"]["Q9"]:
        assert sheet("Qwen3.5-9B", "full")["latency"][method]["Q9"]["n_repeats"] == 1


def test_surface_does_not_bridge_a_missing_corner():
    present = {(0, 0), (1, 0), (0, 1)}
    assert legal_surface_triangles(present) == []
    present.add((1, 1))
    assert len(legal_surface_triangles(present)) == 2


def test_replay_matches_the_full_slot_example_and_virtual_pad():
    positions = {1: 0, 3: 1, 5: 2, 7: 3}
    built = replay_segment([3, 7], [1, 5], positions, 2, "child0", "child1")
    assert built["pointer"] == "child1"
    assert built["winner"] == [1, 3]
    assert built["loser"] == [5, 7]
    positions = {5: 0, 6: 1, 7: 2, 14: 3}
    refreshed = replay_segment([5, 7], [6, 14], positions, 2, "child0", "child1")
    assert refreshed["pointer"] == "child0"
    assert refreshed["winner"] == [5, 6]
    assert refreshed["loser"] == [7, 14]
    padded = replay_segment([3], [1], {1: 0, 3: 1}, 2, "child0", "child1")
    assert padded["left_virtual"] == 1 and padded["right_virtual"] == 1
    assert padded["pointer"] == "child0"
    assert padded["winner"] == [1, 3]
    assert padded["loser"] == []


def test_exp3_supplements_are_not_fixed_series():
    assert supplement_is_outside_fixed()
    assert len(fixed_keys("SW")) == 5 and len(fixed_keys("LT")) == 5
    assert all(row["family"] == "LT" for row in SUPPLEMENT)
