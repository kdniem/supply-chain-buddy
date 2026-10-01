"""Unit tests for repository tooling."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from common import CITATION_RE, library_keys, parse_frontmatter, split_frontmatter  # noqa: E402


class FrontmatterTests(unittest.TestCase):
    def test_parses_block_scalar_nested_map_and_list(self):
        text = (
            "---\n"
            "name: inventory-policy\n"
            "description: >-\n"
            "  Sizes safety stock.\n"
            "  Use when asked about reorder points.\n"
            "license: MIT\n"
            "metadata:\n"
            "  version: 0.1.0\n"
            "  maturity: draft\n"
            "tags: [a, b]\n"
            "---\n"
            "# Body\n"
        )
        fm_text, body = split_frontmatter(text)
        fm = parse_frontmatter(fm_text)
        self.assertEqual(fm["name"], "inventory-policy")
        self.assertEqual(fm["description"], "Sizes safety stock. Use when asked about reorder points.")
        self.assertEqual(fm["metadata"], {"version": "0.1.0", "maturity": "draft"})
        self.assertEqual(fm["tags"], ["a", "b"])
        self.assertTrue(body.startswith("# Body"))

    def test_no_frontmatter(self):
        self.assertEqual(split_frontmatter("# Just a body"), ("", "# Just a body"))


class CitationTests(unittest.TestCase):
    def test_pattern_matches_keys_but_not_labels(self):
        text = "See [SPT-2017] and [SCOR-DS]. Labels like [Data] or [KEY] are not citations."
        self.assertEqual(sorted(CITATION_RE.findall(text)), ["SCOR-DS", "SPT-2017"])

    def test_library_has_core_keys(self):
        keys = library_keys()
        for key in ("SPT-2017", "HA-2021", "KRA-1983", "SCOR-DS", "MIN-1987"):
            self.assertIn(key, keys)


if __name__ == "__main__":
    unittest.main()
