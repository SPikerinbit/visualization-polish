"""Write the synthetic layout table for the E3 scale figure.

The y values are a drawing scaffold so five fixed series stay separated.
They are not costs, not model output, and not a ranking of (k, h).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SW_FIXED = ((4, 5), (5, 4), (10, 2), (8, 1), (10, 1))
LT_FIXED = ((50, 2), (16, 4), (32, 3), (50, 1), (20, 1))
SIZES = (1000, 5000, 10000)

# Print colors, assigned in the confirmed list order. Hue is not a scale
# of k or h. SW and LT each have their own five colors so one shared legend
# can name all ten pairs without repeating a swatch.
SW_COLORS = {
    (4, 5): "#004488",
    (5, 4): "#C47B00",
    (10, 2): "#228833",
    (8, 1): "#D1495B",
    (10, 1): "#AA3377",
}
LT_COLORS = {
    (50, 2): "#1686A8",
    (16, 4): "#882255",
    (32, 3): "#5B4B8A",
    (50, 1): "#8C5A2C",
    (20, 1): "#2A6F4E",
}

SUPPLEMENTS = (
    {"n": 5000, "family": "LT", "k": 250, "h": 2, "mode": "Full"},
    {"n": 5000, "family": "LT", "k": 250, "h": 1, "mode": "LIMIT10"},
    {"n": 10000, "family": "LT", "k": 500, "h": 2, "mode": "Full"},
    {"n": 10000, "family": "LT", "k": 500, "h": 1, "mode": "LIMIT10"},
)

# Identical slope and a constant prediction offset: the picture shows the
# line-style contract, not a comparison among parameters.
SERIES_GAP = 9.0
BASE = 14.0
SLOPE_PER_THOUSAND = 0.9
PREDICTION_OFFSET = 3.4
SUPPLEMENT_Y = 69.0


def _measured(index: int, n: int) -> float:
    return round(BASE + index * SERIES_GAP + (n / 1000.0) * SLOPE_PER_THOUSAND, 1)


def _series(index: int) -> dict:
    measured = [_measured(index, n) for n in SIZES]
    predicted = [round(y + PREDICTION_OFFSET, 1) for y in measured]
    return {"measured": measured, "predicted": predicted}


def _panel(family: str, mode: str, pairs: tuple, colors: dict) -> dict:
    series = []
    for index, (k, h) in enumerate(pairs):
        row = _series(index)
        row.update({"k": k, "h": h, "color": colors[(k, h)]})
        series.append(row)
    supplements = []
    for item in SUPPLEMENTS:
        if item["family"] == family and item["mode"] == mode:
            supplements.append(
                {
                    "n": item["n"],
                    "k": item["k"],
                    "h": item["h"],
                    "y": SUPPLEMENT_Y,
                    "joined": False,
                }
            )
    return {"family": family, "mode": mode, "series": series, "supplements": supplements}


def build() -> dict:
    panels = [
        _panel("SW", "Full", SW_FIXED, SW_COLORS),
        _panel("LT", "Full", LT_FIXED, LT_COLORS),
        _panel("SW", "LIMIT10", SW_FIXED, SW_COLORS),
        _panel("LT", "LIMIT10", LT_FIXED, LT_COLORS),
    ]
    return {
        "kind": "synthetic_layout_only",
        "warning": (
            "Not measured costs. Not a performance result. "
            "Do not cite these y values."
        ),
        "setting_labels": {
            "model": "Qwen3.5-9B",
            "query": "DL20 representative",
            "note": (
                "Names of the confirmed setting only. "
                "No run produced these y values."
            ),
        },
        "x": {
            "name": "n",
            "values": list(SIZES),
            "tick_labels": ["1k", "5k", "10k"],
            "scale": "linear",
            "scale_status": (
                "Linear versus logarithmic was unset. "
                "This file places 1000, 5000, and 10000 on a linear axis."
            ),
        },
        "y": {
            "name": "layout_units",
            "meaning": (
                "Vertical stack for legibility. Not equivalent-input tokens "
                "and not a measured cost. Off versus on-cache is not split."
            ),
        },
        "layout_rule": {
            "series_gap": SERIES_GAP,
            "base": BASE,
            "slope_per_thousand": SLOPE_PER_THOUSAND,
            "prediction_offset": PREDICTION_OFFSET,
            "supplement_y": SUPPLEMENT_Y,
            "statement": (
                "Every fixed series uses the same slope. "
                "The dashed series is the solid scaffold plus a constant offset. "
                "Vertical order follows the confirmed list, not a ranking. "
                "Supplement points are not members of the five series and are not optima."
            ),
        },
        "panels": panels,
    }


def validate(payload: dict) -> None:
    panels = payload["panels"]
    assert [p["family"] + " " + p["mode"] for p in panels] == [
        "SW Full",
        "LT Full",
        "SW LIMIT10",
        "LT LIMIT10",
    ]
    sw = panels[0]["series"]
    lt = panels[1]["series"]
    assert [(s["k"], s["h"]) for s in sw] == list(SW_FIXED)
    assert [(s["k"], s["h"]) for s in lt] == list(LT_FIXED)
    assert panels[2]["series"] == [
        {**s} for s in sw
    ]
    for left, right in zip(panels[0]["series"], panels[2]["series"]):
        assert left == right
    for left, right in zip(panels[1]["series"], panels[3]["series"]):
        assert left["k"] == right["k"] and left["h"] == right["h"]
        assert left["color"] == right["color"]
    assert panels[0]["supplements"] == []
    assert panels[2]["supplements"] == []
    got = []
    fixed = {(s["k"], s["h"]) for s in lt}
    for panel in panels:
        for star in panel["supplements"]:
            assert star["joined"] is False
            assert (star["k"], star["h"]) not in fixed
            assert star["y"] > max(y for s in panel["series"] for y in s["predicted"])
            got.append((star["n"], panel["family"], star["k"], star["h"], panel["mode"]))
    assert got == [
        (5000, "LT", 250, 2, "Full"),
        (10000, "LT", 500, 2, "Full"),
        (5000, "LT", 250, 1, "LIMIT10"),
        (10000, "LT", 500, 1, "LIMIT10"),
    ]
    colors = [s["color"] for p in panels for s in p["series"]]
    assert len(set(colors)) == 10


def main() -> None:
    payload = build()
    validate(payload)
    path = ROOT / "e3_layout_data.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
