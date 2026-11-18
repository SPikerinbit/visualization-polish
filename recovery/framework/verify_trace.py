#!/usr/bin/env python3
"""Check the 16-element example: inputs, runs, Q, and Pi are permutations of 1..16."""

from __future__ import annotations

EXPECTED = {
    "chunks": [[12, 3, 16, 7], [5, 14, 1, 6], [11, 2, 15, 8], [9, 13, 4, 10]],
    "runs": [[3, 7, 12, 16], [1, 5, 6, 14], [2, 8, 11, 15], [4, 9, 10, 13]],
    "q1": [1, 3, 5, 6, 7, 12, 14, 16],
    "q2": [2, 4, 8, 9, 10, 11, 13, 15],
    "pi": list(range(1, 17)),
}


def assert_perm(name: str, values: list[int]) -> None:
    if sorted(values) != list(range(1, 17)):
        raise SystemExit(f"{name}: not a permutation of 1..16: {values}")
    if len(values) != len(set(values)):
        raise SystemExit(f"{name}: duplicate values: {values}")


def main() -> None:
    flat_in = [x for c in EXPECTED["chunks"] for x in c]
    assert_perm("input chunks (flat)", flat_in)
    flat_runs = [x for r in EXPECTED["runs"] for x in r]
    assert_perm("runs (flat)", flat_runs)
    merged_q = sorted(EXPECTED["q1"] + EXPECTED["q2"])
    if merged_q != list(range(1, 17)):
        raise SystemExit("Q1 union Q2 is not 1..16")
    assert_perm("Pi", EXPECTED["pi"])
    print("ok: all node groups are permutations of 1..16")


if __name__ == "__main__":
    main()