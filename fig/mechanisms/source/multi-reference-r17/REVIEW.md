# R17 visual review

Private cloud candidate on top of R16 445e673. Scope: Fig. 1, Fig. 2,
Fig. 4 (the two-tree loser-tree diagram), Fig. 5, and Fig. 8. Fig. 3
(sliding window) and all other experimental plots are unchanged.
Baselines: exact GitHub main a288db90974714c651c396603456909b8e71a2a1
(verified assets in R16), and the 13-page compiled R16.

* Fig. 1: vertically ordered three-line output list with a downward direction
  cue, distinct in silhouette from the four horizontally arranged capacity slots.
  No changes to execution, formulas, or refresh-path nodes.
* Fig. 2: centered the colored swatch and text as one unit. Keep 'Rows from C₂':
  Algorithm 1 and section 3.1 call them rows, not necessarily documents, and
  the color tracks provenance through the intermediate runs. Review compared
  CrocSort Fig. 3 and Inoue/Taura Fig. 2.
* Fig. 4: compact side trees with glyph sizes balanced against ListwiseRank.
  Use 'Collect top-down' and 'Replay bottom-up'. Preserve two full tree states.
  Don't mark global rank-list adjacency as if it were a distinct local replay
  partition. Move [5,6] and [3,4] carry/output to the caption while retaining
  teal edges. Reference review: HOT Fig. 7 and FedRoad Fig. 6.
* Fig. 5: both initial 1/2 counts are neutral. Threshold and pointer state stay
  distinct: only the decisive 2/2 positions (#5 and #7) get the restrained shadow.
  Two reviewers checked FIBA Fig. 2, Fu et al. Fig. 9, HOT and FedRoad. Retain
  arrow establishment and change at their exact before/after branches.
* Fig. 8: keep the 6×10 grid for each of four diagrams and one common Savings
  (%) vertical key. Use actual TeX subfigures with bottom captions modeled on
  Fig. 7, independent vector assets, and shared aligned axis ticks. All fixture
  colors/locations and the infeasible mask unchanged.

TeX Live 2026 pdfLaTeX two-pass complete, 13 pages. Native-scale A/B of
pp. 2, 3, 4, 5 and 9; checked exact subfigure numbering and data palettes.
No repo remotes, Overleaf, Windows, or experimental data updated.
