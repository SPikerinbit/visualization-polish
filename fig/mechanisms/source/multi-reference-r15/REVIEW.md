# R15: author feedback on mechanisms

Keep the approved R14 sliding-window layout (pinned `visual-history/r14-fig3-approved`), only remove transfer arrows. Its 55 numeric IDs, stop rows 5/R2 and 10/R4, order, colors, and footprint are unchanged. A caption-hidden reader recovered both stop buffers at manuscript width. Main and R14 were compared with LongLoRA Fig. 3.

Fig. 4 restores two complete R13-style tree snapshots at single-column width. The center reads three explicit input pairs in one rank call. Track R2's [6,14] and the carry [5,6] during bottom-up replay; distinguish prior [1,2] from next [3,4], current from next pointers. A figure-only reader decoded both tree states, output, call and all three arrow roles. Same width, no rank/leaf overlaps. Comparison: actual main/R13 and FedRoad ICDE Fig. 6 / HOT SIGMOD Fig. 7.

Fig. 5 restores actual before and after trees in both cases, not just a value relay. Pointer absent→R and R→L are drawn on the relevant branches. Replay still identifies row 5 on R and row 7 on L as the first to reach 2/2. After independent reading, the refresh subtitle explicitly maps old P [5,7] to the replay L slot, dashed title clearance increased, and redundant tree divider removed. Single legend line and ~94.16 bp original height retained. Comparison: actual main/R13 and same HOT/FedRoad originals. Fig. 2 and all other figures remain unchanged from R14; its approved R13 original stays archived.

This is a local trial; no publication or synchronization.
