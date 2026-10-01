#!/usr/bin/env python3
"""Scaffold a new skill from templates/skill and sync shared content into it.

Usage:
    python3 tools/new_skill.py <skill-name> [--plugin supply-chain-buddy]
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PLUGINS_DIR, REPO_ROOT  # noqa: E402

TEMPLATE_DIR = REPO_ROOT / "templates" / "skill"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("name", help="kebab-case skill name, e.g. inventory-policy")
    parser.add_argument("--plugin", default="supply-chain-buddy")
    args = parser.parse_args(argv)

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.name) or len(args.name) > 64:
        sys.exit("Skill name must be kebab-case (a-z, 0-9, '-') and at most 64 characters.")
    target = PLUGINS_DIR / args.plugin / "skills" / args.name
    if target.exists():
        sys.exit(f"Already exists: {target.relative_to(REPO_ROOT)}")

    shutil.copytree(TEMPLATE_DIR, target)
    template = target / "SKILL.md.template"
    skill_md = target / "SKILL.md"
    skill_md.write_text(template.read_text(encoding="utf-8").replace("name: skill-name", f"name: {args.name}"), encoding="utf-8")
    template.unlink()
    (target / "scripts" / "example_script.py").unlink()

    subprocess.run([sys.executable, str(REPO_ROOT / "tools" / "sync_shared.py")], check=True)
    print(f"Created {target.relative_to(REPO_ROOT)}. Next: fill in every TODO in SKILL.md and references/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
