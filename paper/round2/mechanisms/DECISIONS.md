# Decisions already fixed by the user

These are the instructions for this directory. They are not a new design round.

- Work only in `paper/round2/mechanisms/`. Do not edit public TeX, do not merge.
- Four figures: framework, SW, unified LT(h), pointer. No separate LIMIT figure and no split between LT and segmented LT.
- Framework is a flat full-width drawing, 178 × 42 mm. Runs stay abstract, with no element numbers. Groups of runs merge in layers. A side cost model applies the chosen `(k,h)` to that organization. Full and LIMIT are the two outputs. The request line runs from LIMIT back to the root merge. The stop is a bar on that path, labeled “stop at K”, not a tick standing in a gap.
- SW, LT(h), and pointer keep the user v2 states, topology, and numbers. They are single-column figures. Do not take the wide v2 page and scale it down. Compress whitespace inside the drawing and enlarge type relative to the nodes.
- Target about 6.5–7 pt for labels on the 240 bp column. If a label cannot reach that, write the measured size and the constraint.
- Pointer stays two rows by three columns. Keep L/R and the thick pointer. Winner, loser, and the exhaustion words go in one shared legend. Color and a short mark replace the repeated words. The exhausted side stays identifiable. The state label P is drawn once. L and R sit off the thick pointer tip.
- LT pointers match the approved v2: in all three states the right node points at the left leaf R3, and in the updated state the root points at its right child. Numbers and the three states stay.
- Palette already approved: warm paper, softened blue, call red, pale yellow merge nodes. Do not start a new palette.
- `finite.py` is not in this tree. Do not draw a formula.
- This file records the user’s decisions. It is not a claim that a parent review has accepted the drawings.
