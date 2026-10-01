#!/usr/bin/env python3
"""Copy /shared/*.md into every skill's references/_shared/ folder.

Skills must be self-contained (shareable one by one), so each skill carries a
generated copy of the shared content. /shared is the single source of truth.

Usage:
    python3 tools/sync_shared.py          # write copies
    python3 tools/sync_shared.py --check  # exit 1 if any copy is missing, stale or orphaned
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO_ROOT, SHARED_SUBDIR, generated_content, shared_files, skill_dirs  # noqa: E402


def plan() -> List[tuple]:
    """Return a list of (action, path, content) needed to bring all skills in sync."""
    actions = []
    sources = shared_files()
    expected_names = {s.name for s in sources}
    for skill in skill_dirs():
        target_dir = skill / SHARED_SUBDIR
        for src in sources:
            target = target_dir / src.name
            content = generated_content(src)
            if not target.exists():
                actions.append(("create", target, content))
            elif target.read_text(encoding="utf-8") != content:
                actions.append(("update", target, content))
        if target_dir.exists():
            for existing in target_dir.iterdir():
                if existing.is_file() and existing.name not in expected_names:
                    actions.append(("delete", existing, None))
    return actions


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="Only check; exit 1 if out of sync")
    args = parser.parse_args(argv)

    actions = plan()
    if args.check:
        for action, path, _ in actions:
            print(f"out of sync ({action}): {path.relative_to(REPO_ROOT)}")
        if actions:
            print("Run: python3 tools/sync_shared.py")
            return 1
        print(f"shared content in sync ({len(skill_dirs())} skill(s))")
        return 0

    for action, path, content in actions:
        if action == "delete":
            path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print(f"{action}: {path.relative_to(REPO_ROOT)}")
    print(f"done: {len(actions)} change(s) across {len(skill_dirs())} skill(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
