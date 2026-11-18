"""Draw E3, E4a, E4b, E4c, and E5 into this directory."""

from __future__ import annotations

from pathlib import Path

import e3
import e4a
import e4b
import e4c
import e5
import contact

ROOT = Path(__file__).resolve().parent


def main() -> None:
    e3.build(ROOT / "figures" / "e3")
    e4a.build(ROOT / "figures" / "e4a")
    e4b.build(ROOT / "figures" / "e4b")
    e4c.build(ROOT / "figures" / "e4c")
    e5.build(ROOT / "figures" / "e5")
    contact.build(ROOT)
    print("wrote", ROOT / "figures")


if __name__ == "__main__":
    main()
