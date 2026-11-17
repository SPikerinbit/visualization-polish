"""Confirmed experiment-3 configuration labels.

Heights are not defined here. Supplement points are a different role from
the five fixed-(k, h) series and must not be drawn as those series.
"""

SW_FIXED = ((4, 5), (5, 4), (10, 2), (8, 1), (10, 1))
LT_FIXED = ((50, 2), (16, 4), (32, 3), (50, 1), (20, 1))
SIZES = (1000, 5000, 10000)
SUPPLEMENT = (
    {"n": 5000, "family": "LT", "kh": (250, 2), "mode": "Full"},
    {"n": 5000, "family": "LT", "kh": (250, 1), "mode": "LIMIT10"},
    {"n": 10000, "family": "LT", "kh": (500, 2), "mode": "Full"},
    {"n": 10000, "family": "LT", "kh": (500, 1), "mode": "LIMIT10"},
)


def fixed_keys(family: str) -> set[tuple[int, int]]:
    return set(SW_FIXED if family == "SW" else LT_FIXED)


def supplement_is_outside_fixed() -> bool:
    for row in SUPPLEMENT:
        if row["kh"] in fixed_keys(row["family"]):
            return False
    return True
