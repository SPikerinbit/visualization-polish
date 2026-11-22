# R8: print-size visual review

Working checkpoint based on R7 8df3e62. Working branch only, no publication. Five independent visual reviews compared actual typeset pages with renders from original papers. These are design references, not experimental evidence.

| Figure | Original visual comparison | Decision at R8 |
| --- | --- | --- |
| 1 | [Spark SQL, Fig. 3](https://people.csail.mit.edu/matei/papers/2015/sigmod_spark_sql.pdf#page=6); [Morsel-driven parallelism, Figs. 2–3](https://db.in.tum.de/~leis/papers/morsels.pdf#page=3) | Route the decision to one clear junction, then to Full and LIMIT K. B stays a reference example, no output arrow from B. Make the layer-wide dependency distinct from the narrow local push/pull arrows. No all-to-all dependency added. |
| 2 | [WiscSort, Fig. 3](https://arxiv.org/pdf/2307.06476#page=6) | Keep the pass names and 4→2→1 fan-in, no extra phase box. |
| 3 | [RankGPT, Fig. 3](https://aclanthology.org/2023.emnlp-main.923.pdf#page=3) | Clarify by-run call and emitted prefix legend labels, do not import fixed-stride window semantics. |
| 4 | [SGLang, Fig. 3](https://arxiv.org/pdf/2312.07104#page=5) | Make the central rank-vector easier to read. Same before/after nodes, one call and two local replay steps. |
| 5 | [Adaptive Radix Tree, Figs. 4–5](https://db.in.tum.de/~leis/papers/ART.pdf#page=4) | Prefer centering over the numeric spine to centering over the widest annotation. Equal strip pitch, bottom edges flush with the left leaf frames, separator after rank 2. Keep rank 3 marked as first exhausted. |
| 6, 7, 9 | [Picasso, Fig. 1](https://www.vldb.org/conf/2005/papers/p1228-reddy.pdf#page=2); [Visualizing the Loss Landscape, Fig. 1](https://arxiv.org/pdf/1712.09913#page=1); [Fort and Jastrzębski, Fig. 1](https://papers.nips.cc/paper_files/paper/2019/file/48042b1dae4950fef2bd2aafa0b971a1-Paper.pdf#page=2) | Separate the glyph groups in Fig. 6's legend. Keep all chosen coordinates and inset locations; the user's in-axes placement overrides suggestions to move them outside. |
| 8 | [Akasiadis et al., Fig. 13](https://openproceedings.org/2024/conf/edbt/paper-97.pdf#page=12); [Khalil et al., Fig. 8](https://link.springer.com/content/pdf/10.1186/s12870-024-04906-y.pdf#page=14) | Darken only the hatch, give the key a real cell-size swatch, and match scale numerals to panel ticks. Cells, signed clipping endpoints and palette are unchanged. Sign is still encoded by hue, not readable from grayscale alone. |
| 10 | [DistServe, Fig. 8](https://www.usenix.org/system/files/osdi24-zhong-yinmin.pdf#page=11) | Keep independent K bins, distinct dots/triangles, tie glyph and separate Full endpoint. No change to E5. |
| E1 tables | [RankGPT, Table 1](https://aclanthology.org/2023.emnlp-main.923.pdf#page=6) | A rank-key note can be considered with manuscript edits, not part of this art pass. |

Validation: actual pdfTeX in TeX Live 2026, 13 pages, no undefined references or overfull boxes; independent final-size image review of Figs. 1, 3, 4, 5, 6 and 8. Fig. 5 build R:2/2 on item 5 and refresh L:2/2 on item 7. Reproducible vector sources in the two multi-reference-r8 directories and the active heatmap tile directory. No change to text, experiment data, or scientific claims.
