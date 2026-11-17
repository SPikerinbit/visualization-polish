from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
INK = "#262b30"
RED = "#B23A2F"
BLUE = "#1F6F8B"
GRAY = "#8E99A4"
GRID = "#E3E8EC"
MUTED = "#5C6B76"

plt.rcParams.update({
    "font.family": "TeX Gyre Termes",
    "font.size": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "axes.edgecolor": "#C5CED4",
    "axes.labelcolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.unicode_minus": False,
})

SW = "#1F6F8B"
LT = "#C47B2B"
METHOD_STYLE = {
    "pointwise": ("#4C5B66", "o"),
    "ext_pointwise": ("#6E7C86", "s"),
    "bubble": ("#8A6A4F", "D"),
    "merge": ("#3E6B5A", "v"),
    "listk": ("#3D5A80", "^"),
    "tournament": ("#7A5C8A", "P"),
    "lotus": ("#8C4A4A", "X"),
    "setwise": ("#4F6F4A", "h"),
    "sw": (SW, "o"),
    "lt": (LT, "D"),
}
METHOD_NAME = {
    "pointwise": "Pointwise",
    "ext_pointwise": "Ext. Pointwise",
    "bubble": "Ext. Bubble",
    "merge": "Ext. Merge",
    "listk": "ListK",
    "tournament": "Tournament",
    "lotus": "Lotus Quick",
    "setwise": "Setwise Heap",
    "sw": "SW",
    "lt": "LT",
}
