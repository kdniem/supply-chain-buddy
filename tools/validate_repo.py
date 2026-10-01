#!/usr/bin/env python3
"""Repository quality gate for Supply Chain Buddy.

Checks:
  - marketplace.json / plugin.json parse and carry required fields; names match
  - every skill: frontmatter (name == folder, kebab-case, description length),
    no TODO markers, SKILL.md <= 300 lines, required sections present
  - shared content synced into every skill (references/_shared/)
  - every citation key [KEY-YYYY] used anywhere resolves in shared/methods-library.md
  - eval cases: prompt.md or case.yaml, at least one grader; >= 3 cases per skill
    (warning while a skill is `maturity: draft`, error otherwise)
  - skill scripts have a matching unit test file (warning)
  - every installed skill is listed in the sc-buddy orchestrator

Usage:
    python3 tools/validate_repo.py
Exit code 1 on any error. Warnings are printed but do not fail.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    CITATION_RE,
    PLUGINS_DIR,
    REPO_ROOT,
    SHARED_DIR,
    library_keys,
    parse_frontmatter,
    skill_dirs,
    split_frontmatter,
)
import sync_shared  # noqa: E402

MAX_SKILL_LINES = 300
MAX_DESCRIPTION = 1024
MIN_EVAL_CASES = 3
REQUIRED_SECTIONS = [
    "Operating contract",
    "Session modes",
    "Workflow",
    "Data requirements",
    "Methods",
    "Outputs",
    "Handoffs",
    "Guardrails",
]
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class Report:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def rel(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT))


def check_manifests(r: Report) -> None:
    mp_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
    try:
        mp = json.loads(mp_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        r.error(f"{rel(mp_path)}: cannot parse ({exc})")
        return
    for field in ("name", "owner", "plugins"):
        if field not in mp:
            r.error(f"{rel(mp_path)}: missing '{field}'")
    for entry in mp.get("plugins", []):
        src = REPO_ROOT / entry.get("source", "")
        manifest = src / ".claude-plugin" / "plugin.json"
        if not manifest.exists():
            r.error(f"marketplace entry '{entry.get('name')}': {rel(manifest)} not found")
            continue
        try:
            pj = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            r.error(f"{rel(manifest)}: cannot parse ({exc})")
            continue
        if pj.get("name") != entry.get("name"):
            r.error(f"name mismatch: marketplace entry '{entry.get('name')}' vs plugin.json '{pj.get('name')}'")
        for field in ("version", "description", "author", "license"):
            if field not in pj:
                r.warn(f"{rel(manifest)}: missing recommended field '{field}'")


def check_skill(skill: Path, r: Report, keys: set) -> str:
    """Validate one skill; return its maturity."""
    skill_md = skill / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(text)
    if not fm_text:
        r.error(f"{rel(skill_md)}: missing YAML frontmatter")
        return "draft"
    fm = parse_frontmatter(fm_text)
    name = fm.get("name")
    if name != skill.name:
        r.error(f"{rel(skill_md)}: frontmatter name '{name}' != folder '{skill.name}'")
    if not KEBAB.match(skill.name) or len(skill.name) > 64:
        r.error(f"{rel(skill)}: folder name must be kebab-case, max 64 chars")
    desc = str(fm.get("description", ""))
    if not desc:
        r.error(f"{rel(skill_md)}: missing description")
    elif len(desc) > MAX_DESCRIPTION:
        r.error(f"{rel(skill_md)}: description has {len(desc)} chars (max {MAX_DESCRIPTION})")
    metadata = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    maturity = metadata.get("maturity", "draft")

    lines = text.count("\n") + 1
    if lines > MAX_SKILL_LINES:
        r.error(f"{rel(skill_md)}: {lines} lines (max {MAX_SKILL_LINES}); move depth into references/")

    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^##\s+{re.escape(section)}\b", body, re.MULTILINE):
            r.error(f"{rel(skill_md)}: missing section '## {section}'")

    for path in skill.rglob("*"):
        if path.is_file() and "_shared" not in path.parts and path.suffix in {".md", ".py", ".csv"}:
            content = path.read_text(encoding="utf-8", errors="ignore")
            if "TODO" in content:
                (r.warn if maturity == "draft" else r.error)(f"{rel(path)}: contains TODO")
            for key in set(CITATION_RE.findall(content)):
                if key not in keys:
                    r.error(f"{rel(path)}: citation [{key}] not in shared/methods-library.md")

    for script in (skill / "scripts").glob("*.py") if (skill / "scripts").exists() else []:
        expected = REPO_ROOT / "tests" / f"test_{skill.name.replace('-', '_')}_{script.stem}.py"
        if not expected.exists():
            r.warn(f"{rel(script)}: no unit test at {rel(expected)}")
    return str(maturity)


def check_evals(r: Report, maturities: dict) -> None:
    for plugin in sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir()):
        evals = plugin / "evals"
        cases = []
        if evals.exists():
            for case in sorted(d for d in evals.iterdir() if d.is_dir() and d.name not in {"results", "mocks"}):
                cases.append(case)
                if not ((case / "prompt.md").exists() or (case / "case.yaml").exists()):
                    r.error(f"{rel(case)}: needs prompt.md or case.yaml")
                graders = list((case / "graders").glob("*.md")) if (case / "graders").exists() else []
                if not graders and not (case / "case.yaml").exists():
                    r.error(f"{rel(case)}: no graders")
                for g in graders:
                    if "TODO" in g.read_text(encoding="utf-8"):
                        r.error(f"{rel(g)}: contains TODO")
        for skill_name, maturity in maturities.items():
            n = sum(1 for c in cases if c.name.startswith(f"{skill_name}-"))
            if n < MIN_EVAL_CASES:
                msg = f"skill '{skill_name}': {n} eval case(s) (min {MIN_EVAL_CASES}, named '{skill_name}-<nn>-<slug>')"
                (r.warn if maturity == "draft" else r.error)(msg)


def check_routing(r: Report) -> None:
    """Every installed skill must appear in the sc-buddy orchestrator (routing table / coverage)."""
    buddy = next((d for d in skill_dirs() if d.name == "sc-buddy"), None)
    if buddy is None:
        return
    text = (buddy / "SKILL.md").read_text(encoding="utf-8")
    for skill in skill_dirs():
        if skill.name != "sc-buddy" and f"`{skill.name}`" not in text:
            r.error(f"skill '{skill.name}' is not listed in sc-buddy/SKILL.md (routing table / coverage)")


def check_shared(r: Report, keys: set) -> None:
    for path in sorted(SHARED_DIR.glob("*.md")):
        for key in set(CITATION_RE.findall(path.read_text(encoding="utf-8"))):
            if key not in keys:
                r.error(f"{rel(path)}: citation [{key}] not in methods-library.md")
    for action, path, _ in sync_shared.plan():
        r.error(f"shared content out of sync ({action}): {rel(path)}; run tools/sync_shared.py")


def main() -> int:
    r = Report()
    keys = library_keys()
    if not keys:
        r.error("shared/methods-library.md: no citation keys found")
    check_manifests(r)
    check_shared(r, keys)
    maturities = {}
    for skill in skill_dirs():
        maturities[skill.name] = check_skill(skill, r, keys)
    check_evals(r, maturities)
    check_routing(r)

    for w in r.warnings:
        print(f"WARN  {w}")
    for e in r.errors:
        print(f"ERROR {e}")
    print(f"\n{len(skill_dirs())} skill(s), {len(keys)} citation key(s): {len(r.errors)} error(s), {len(r.warnings)} warning(s)")
    return 1 if r.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
