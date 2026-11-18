"""Print geometry and stroke sizes taken from the original panel PDFs.

The panels in ``paper/tex/fig/panels`` are Matplotlib canvases of 133.2 pt.
``exp.tex`` includes most of them at ``0.33\\columnwidth`` and Fig. 8
(``fig:exp4-topk``) at ``0.25\\columnwidth``. Stroke widths below are the
raw PDF ``w`` operands on that 133.2 pt canvas. Printed widths scale by
``include_width / 133.2``.

Column width 241.1475 pt is the TeX Live measurement recorded for this
acmart sigconf + pvldb template (``paper/recovery/pseudocode/structure.md``).
``textwidth = 2 * columnwidth + 24 pt``.
"""

from __future__ import annotations

NATIVE_PT = 133.2
COLUMN_PT = 241.1475
COLUMNSEP_PT = 24.0
TEXT_PT = 2 * COLUMN_PT + COLUMNSEP_PT  # 506.295

# Measured from exp3/exp4/exp5 panel content streams (same on each panel).
NATIVE_LINE_PT = 1.6
NATIVE_MARKER_PT = 4.8
NATIVE_MARKER_EDGE_PT = 1.0
NATIVE_GRID_PT = 0.765
NATIVE_SPINE_PT = 1.36
NATIVE_TICK_PT = 0.8
NATIVE_TICK_LEN_PT = 2.2
NATIVE_STAR_PT = 10.2
NATIVE_DIAMOND_PT = 9.49
NATIVE_TICK_FONT_PT = 9.0
NATIVE_LABEL_FONT_PT = 11.05

GRID_RGB = (176 / 255, 176 / 255, 176 / 255)  # #B0B0B0
SW_RGB = (0.839, 0.153, 0.157)  # #D62728
LT_RGB = (0.122, 0.467, 0.706)  # #1F77B4
SLT_RGB = (0.173, 0.627, 0.173)  # #2CA02C

# Tableau colors that actually occur as fills in the original panels,
# plus the rest of the Tableau 10 set for series that need extra hues.
TABLEAU = (
    "#1F77B4",
    "#FF7F0E",
    "#2CA02C",
    "#D62728",
    "#9467BD",
    "#8C564B",
    "#E377C2",
    "#17BECF",
    "#BCBD22",
    "#CC79A7",
)

FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"


def printed(native_pt: float, column_fraction: float) -> float:
    """Width in pt after ``\\includegraphics[width=f\\columnwidth]``."""
    return native_pt * (column_fraction * COLUMN_PT) / NATIVE_PT


def pt_to_in(pt: float) -> float:
    return pt / 72.0


def mm_to_pt(mm: float) -> float:
    return mm * 72.0 / 25.4
