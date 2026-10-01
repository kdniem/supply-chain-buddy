"""Shared helpers for repository tooling (standard library only)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
SHARED_DIR = REPO_ROOT / "shared"
PLUGINS_DIR = REPO_ROOT / "plugins"
SHARED_SUBDIR = Path("references") / "_shared"
GENERATED_MARKER = "<!-- GENERATED from shared/{name} by tools/sync_shared.py. Do not edit; edit shared/{name} instead. -->"


def skill_dirs() -> List[Path]:
    """All skill folders (containing SKILL.md) across plugins, sorted."""
    return sorted(p.parent for p in PLUGINS_DIR.glob("*/skills/*/SKILL.md"))


def shared_files() -> List[Path]:
    return sorted(p for p in SHARED_DIR.glob("*.md") if p.is_file())


def generated_content(shared_file: Path) -> str:
    body = shared_file.read_text(encoding="utf-8")
    return GENERATED_MARKER.format(name=shared_file.name) + "\n\n" + body


def split_frontmatter(text: str) -> Tuple[str, str]:
    """Return (frontmatter, body). Frontmatter is '' if absent."""
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 4 :].lstrip("\n")


def parse_frontmatter(fm: str) -> Dict[str, object]:
    """Minimal YAML subset parser: top-level `key: value`, block scalars (`>-`, `>`, `|`, `|-`),
    one level of nested mappings, and inline lists `[a, b]`. Enough for SKILL.md and eval files."""
    result: Dict[str, object] = {}
    lines = fm.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, value = m.group(1), m.group(2).strip()
        if value in (">-", ">", "|", "|-"):
            block: List[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            joiner = " " if value.startswith(">") else "\n"
            result[key] = joiner.join(b for b in block if b).strip()
            continue
        if value == "":
            nested: Dict[str, str] = {}
            i += 1
            while i < len(lines) and lines[i].startswith(" "):
                nm = re.match(r"^\s+([A-Za-z_][\w-]*):\s*(.*)$", lines[i])
                if nm:
                    nested[nm.group(1)] = _scalar(nm.group(2).strip())
                i += 1
            result[key] = nested
            continue
        result[key] = _scalar(value)
        i += 1
    return result


def _scalar(value: str):
    if value.startswith("[") and value.endswith("]"):
        return [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
    return value.strip("'\"")


CITATION_RE = re.compile(r"\[([A-Z]{2,6}-(?:\d{4}|DS|DICT))\]")
LIBRARY_KEY_RE = re.compile(r"^\|\s*`\[([A-Z]{2,6}-(?:\d{4}|DS|DICT))\]`\s*\|", re.MULTILINE)


def library_keys() -> set:
    text = (SHARED_DIR / "methods-library.md").read_text(encoding="utf-8")
    return set(LIBRARY_KEY_RE.findall(text))
