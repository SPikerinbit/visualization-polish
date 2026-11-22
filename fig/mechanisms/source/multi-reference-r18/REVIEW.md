# R18: Fig. 4 pointer hierarchy and Fig. 6 panel captions

The review branch starts from R17 a56f4f7. The comparison baseline is the
pinned GitHub main a288db90974714c651c396603456909b8e71a2a1, not the older
locally named main review. R18 contains no data or algorithm updates.

- Fig. 4: retain two snapshots and the common ListwiseRank. One downward
  tree-pointer treatment represents stored pointers before and after
  refresh; replay connections are not arrow-headed. Restore main's dashed
  selection grammar around [3,4], [5,7], and [6,14]; the off-path subtree is
  unselected. Output is green and named once in the aligned legend. The
  before/after example and replay order are unchanged. Primary design
  comparisons: [FedRoad, ICDE 2025, Fig. 6](https://dbgroup.cs.tsinghua.edu.cn/ligl/papers/ICDE25-FedRoad.pdf#page=9),
  [HOT, SIGMOD 2018, Fig. 7](https://15721.courses.cs.cmu.edu/spring2020/papers/07-oltpindexes2/p521-binna.pdf#page=9),
  and [FiBA, PVLDB 16, Fig. 2](https://www.vldb.org/pvldb/vol16/p3227-hirzel.pdf#page=5).
- Fig. 6: remove the four duplicate group headers at the top of the charts.
  Each of the twelve native LaTeX subcaptions now carries the same scenario
  ID plus the family and demand, on one centered line. The original chart
  PDFs, best labels, legend, and data remain unchanged. Comparison:
  [OtterTune, SIGMOD 2017, Figs. 1 and 5](https://db.cs.cmu.edu/papers/2017/tuning-sigmod2017.pdf#page=9).
- Fig. 7 and Fig. 8 are visual grammar references only, and are untouched.
  The 6 × 10 Fig. 8 proof is not the full-domain heatmap on main.
