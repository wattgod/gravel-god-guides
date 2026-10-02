"""Apply and verify Motoren AE-6.3 wording in delivered Gravel God guides.

The 15 legacy guide pages and one guide template also carry the same retired
claim, so keep them aligned with the 1,030 athlete delivery pages.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD_ITEM = b"Can even train fasted if under 90 minutes"
NEW_ITEM = b"Eat normally before easy rides; plan fueling for the ride's duration and your recovery needs."
OLD_RULE = b"Hard sessions need fuel. Easy sessions are flexible."
NEW_RULE = b"Fuel hard and easy sessions; adjust intake to the ride's duration and demands."


def candidates() -> list[Path]:
    return sorted(
        list((ROOT / "athletes").glob("*/index.html"))
        + list((ROOT / "docs/guides").glob("**/*.html"))
        + [ROOT / "templates/guide_template_full.html"]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = 0
    files = candidates()
    for path in files:
        original = path.read_bytes()
        old_count = original.count(OLD_ITEM)
        rule_count = original.count(OLD_RULE)
        if old_count not in (0, 1) or rule_count != old_count:
            raise SystemExit(f"Unexpected fueling block in {path}: {old_count=} {rule_count=}")
        if args.check:
            if old_count:
                raise SystemExit(f"Retired advice remains in {path}")
            continue
        if old_count:
            path.write_bytes(original.replace(OLD_ITEM, NEW_ITEM).replace(OLD_RULE, NEW_RULE))
            changed += 1
    if args.check:
        remaining = [p for p in files if b"fasted" in p.read_bytes().lower()]
        if remaining:
            raise SystemExit(f"Fasted text remains in {len(remaining)} guide files")
    print(f"files={len(files)} changed={changed} check={args.check}")


if __name__ == "__main__":
    main()
