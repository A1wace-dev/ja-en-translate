"""Structural checks: frontmatter is valid and every referenced file exists."""
import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills" / "ja-en-translate"
REF = re.compile(r"(?<![\w{}-])(?:references/)?(?:contexts/|config/)?[a-z0-9-]+\.md")


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


class SkillFileTests(unittest.TestCase):
    def test_frontmatter(self):
        fm = frontmatter((SKILL / "SKILL.md").read_text(encoding="utf-8"))
        self.assertEqual(fm.get("name"), "ja-en-translate")
        desc = fm.get("description", "")
        self.assertTrue(0 < len(desc) <= 1024, len(desc))
        self.assertNotIn("<", desc)

    def test_references_exist(self):
        names = {p.name for p in SKILL.rglob("*.md")}
        missing = set()
        for md in SKILL.rglob("*.md"):
            for ref in REF.findall(md.read_text(encoding="utf-8")):
                name = ref.rsplit("/", 1)[-1]
                if name in {"SKILL.md", "EXTEND.md", "translation.md", "my-courses.md", "report.md", "polished.md", "my-english-essay.md", "my-report-ja.md"}:
                    continue
                if name.startswith(("chunk-", "0")) or name in {"frontmatter.md", "src.md"}:
                    continue
                if name not in names:
                    missing.add(f"{md.relative_to(SKILL)} -> {ref}")
        self.assertEqual(missing, set())

    def test_every_context_has_a_profile(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for ctx in re.findall(r"\| `([a-z]+)` \| contexts/\1\.md", text):
            self.assertTrue((SKILL / "references" / "contexts" / f"{ctx}.md").is_file(), ctx)


if __name__ == "__main__":
    unittest.main()
