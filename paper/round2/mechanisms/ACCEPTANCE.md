# Local check, not a parent acceptance

This note replaces the one that cited `7fe71c8`. That commit is not the current figure. The parent QA of `bed819cdfc20c2df5ed067dbd120119daf74bcc6` is what this revision answers. The SHA of this revision is recorded at the bottom after the commit that contains these files. This note does not say the parent accepted the figures.

## Which PR

Mechanism sources are PR 16, branch `cursor/round2-mechanisms-6f22`. PR 13 is the older numbered framework and does not contain this directory.

## What changed in this pass

Local only. Page size, type size, and the three-state layout are unchanged.

- LT: in all three states the right node points at R3 = [11, 15]. In the updated state the root points at its right child [8, 9]. Numbers are unchanged.
- Pointer: each State draws P once. L and R are shifted off the thick pointer tip. The 2×3 numbers, thick pointers, and shared legend stay.
- Framework: the red request still runs from LIMIT to the root merge. The stop bar is on that path, with the label “stop at K”. The page stays 178 × 42 mm.
- Preview: each column figure and its caption are one minipage, so the LT caption cannot move onto the pointer.

## What was rendered and opened

`framework.pdf` is 504.394 × 119.054 bp (178.0 × 42.0 mm). `sw.pdf` is 240 × 96 bp. `lt.pdf` is 240 × 124 bp. `pointer.pdf` is 240 × 150 bp.

SW titles are 7 bp and the other SW text is 6.5 bp. LT text is 6.5 bp. Pointer column titles are 7 bp and the other pointer text is 6.5 bp. Those sizes were already accepted and were not edited.

Opened the rebuilt `framework.png`, `lt.png`, `pointer.png`, and preview page 2.

## Not claimed

No formula, because `finite.py` is absent. This note does not say the parent accepted the figures.

## SHA

The three fixes and the rebuilt PDFs are commit `859a6fea272855eaf6976e23b199aea9557c04b9`. This paragraph is the following commit on the same branch, so the branch HEAD is one commit later and the PDF bytes are the same. `7fe71c8` and `bed819cdfc20c2df5ed067dbd120119daf74bcc6` are earlier and are not these files.
