# R19 print typography audit

Baseline: R18 fc1c196 in compiled manuscript; upgrade baseline is exact
GitHub main a288db90974714c651c396603456909b8e71a2a1. Sizes below are
printed PDF points (1 bp = 1/72 in), not generator settings. Font sizes
were extracted after placement in LaTeX or scaled to the same printed
width; original proceedings diagrams were also compared as native crops
at physical scale. Details reflect the scope of each figure, not a
minimum font standard claimed for the venue. Running example rows and
data have not changed.

| Fig. / assignment | Printed typography, main → R18 | R19 decision |
| --- | --- | --- |
| 1 / framework | Stage heads 7.20 → 10.01; execution headers 6.50 → 9.81; supporting details ~5.85–6.05 → 7.01–7.51 | Keep the hierarchy. Five labels use 7.5 bp upright prose, with math variables italic, to separate them cleanly. |
| 2 / merge trace | Stage 6.10 → 7.59; row digits 5.50 → 7.50; run label 5.40 → 6.44; subscript 3.78 → 4.71; key 5.65 → 6.39 | Enlarge only run labels and suffixes to 6.92 / 5.38 bp, and stage counts/key to 6.65. Center the complete key again. |
| 3 / SW | Row digits 5.49 → 7.15; run labels 5.35 → 6.35; key 5.65 → 5.90 | No broad type change; per-run pair pitch 7.90 → 8.75 bp so two two-digit IDs do not run together. |
| 4 / LT | Stage heads 6.10 → 7.20; row digits 5.50 → 6.00; key 5.65 → 6.15 | Keep hierarchy; more digit growth would crowd the unread pairs. Retain R18 pointers and path cues. |
| 5 / pointer | Stage heads 6.10 → 8.70; row digits 5.50 → 6.75–6.80; state/count 5.35 → 6.65; key 5.65 → 6.35 | Keep the callouts and legend; don't enlarge Replay order into the dashed frame. |
| 6 / E2 | Same approx. 6.15 ticks, 6.57 Tokens, 6.83 k/h, 6.97 subcaptions; key ~6.30 → 7.15 | Keep R18's twelve one-line subcaptions; do not shrink or enlarge all axes or keys. |
| 7 / E3 | Ticks unchanged at 5.74; Tokens 6.19; k/h 6.34; inset pairs 6.19 → 6.79; key 6.30 → 6.45 | Harmonize ticks and axis titles to ~6.09 / 6.49 bp. Leave the existing optima and keys. |
| 8 / E4a | Axis values 7.00 in both; R18 key 6.60–7.00 and 6.97 subcaptions; reference Liu repeated ticks ~4.58–5.09 | Keep typography, center SW captions within the actual matrix footprint, and add 1.25 bp above the bottom captions. |
| 9 / E4b | Ticks 6.10, k/h 6.70, z-title 6.65 in both; inset ~6.15 → 6.65–6.90 | Improve cue hierarchy: z-title 7 bp and 2 bp higher, to distinguish from the beta key. |
| 10 / E5 | Axis 6.10 and legend 6.30; panel assets and key byte-identical | Frozen; no edit. |

Original proceedings figures separately inspected: [Self-RAG Fig. 1, ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/file/25f7be9694d7b32d5cc670927b8091e1-Paper-Conference.pdf#page=2),
[SIEVE Fig. 4, PVLDB](https://www.vldb.org/pvldb/vol18/p4723-li.pdf#page=4),
[CrocSort Fig. 3, PVLDB](https://www.vldb.org/pvldb/vol19/p2978-otaki.pdf#page=4),
[Inoue and Taura Fig. 2, PVLDB](https://www.vldb.org/pvldb/vol8/p1274-inoue.pdf#page=3),
[LongLoRA Fig. 3, ICLR 2024](https://openreview.net/pdf?id=6PmJoRfdaK),
[HOT Fig. 7, SIGMOD 2018](https://15721.courses.cs.cmu.edu/spring2020/papers/07-oltpindexes2/p521-binna.pdf#page=9),
[FedRoad Fig. 6, ICDE 2025](https://dbgroup.cs.tsinghua.edu.cn/ligl/papers/ICDE25-FedRoad.pdf#page=9),
[FiBA Fig. 2, PVLDB](https://www.vldb.org/pvldb/vol16/p3227-hirzel.pdf#page=5),
[OtterTune Figs. 1 and 5, SIGMOD 2017](https://db.cs.cmu.edu/papers/2017/tuning-sigmod2017.pdf),
[Liu et al. Fig. 9, PVLDB](https://www.vldb.org/pvldb/vol18/p4616-liu.pdf#page=8),
and [ConnectIt Fig. 3, PVLDB](https://www.vldb.org/pvldb/vol14/p653-dhulipala.pdf#page=9).
