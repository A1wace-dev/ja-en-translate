"""Tests for skills/ja-en-translate/scripts/chunk.py (standard library only)."""
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "ja-en-translate" / "scripts" / "chunk.py"

spec = importlib.util.spec_from_file_location("chunk", SCRIPT)
chunk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chunk)

JA_PARA = "本稿は、地域の日本語教室が果たしてきた役割を検討するものである。"
EN_PARA = "This paper examines the role of community Japanese classes. "


def strip_ws(s):
    return re.sub(r"\s", "", s)


def run(*args):
    out = subprocess.run([sys.executable, str(SCRIPT), *args],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


class MeasureTests(unittest.TestCase):
    def test_japanese_counts_characters(self):
        m = chunk.measure_text("日本語の文章です。")
        self.assertEqual(m["language"], "ja")
        self.assertEqual(m["ja_chars"], 9)

    def test_english_counts_words(self):
        m = chunk.measure_text("This is a short English sentence.")
        self.assertEqual(m["language"], "en")
        self.assertEqual(m["en_words"], 6)

    def test_code_and_urls_are_ignored(self):
        text = "Short text.\n\n```\n日本語日本語日本語日本語日本語日本語日本語\n```\nSee https://例え.jp/日本語"
        m = chunk.measure_text(text)
        self.assertEqual(m["ja_chars"], 0)
        self.assertEqual(m["language"], "en")

    def test_japanese_with_english_terms_is_japanese(self):
        m = chunk.measure_text("Claude Code と Codex で使える翻訳スキルを作成した。")
        self.assertEqual(m["language"], "ja")


class SplitTests(unittest.TestCase):
    def split(self, text, **limits):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        src = Path(tmp.name) / "src.md"
        src.write_text(text, encoding="utf-8")
        out = Path(tmp.name) / "chunks"
        args = ["split", str(src), "--output-dir", str(out)]
        for k, v in limits.items():
            args += [f"--{k.replace('_', '-')}", str(v)]
        run(*args)
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        parts = [(out / c["file"]).read_text(encoding="utf-8") for c in manifest["chunks"]]
        return out, manifest, parts

    def test_round_trip_japanese(self):
        body = "# 第1章\n\n" + JA_PARA * 80 + "\n\n## 第2章\n\n" + JA_PARA * 80 + "\n"
        _, manifest, parts = self.split(body, max_ja_chars=1000)
        self.assertEqual(manifest["unit"], "ja_chars")
        self.assertGreater(len(parts), 2)
        self.assertEqual(strip_ws(body), strip_ws("".join(parts)))
        for c in manifest["chunks"]:
            self.assertLessEqual(c["size"], 1000)

    def test_round_trip_english(self):
        body = "# Intro\n\n" + EN_PARA * 400 + "\n\n## Next\n\nEnd.\n"
        _, manifest, parts = self.split(body, max_en_words=500)
        self.assertEqual(manifest["unit"], "en_words")
        self.assertEqual(strip_ws(body), strip_ws("".join(parts)))

    def test_frontmatter_written_separately(self):
        text = "---\ntitle: テスト\n---\n\n" + JA_PARA * 3 + "\n"
        out, manifest, parts = self.split(text)
        self.assertTrue(manifest["has_frontmatter"])
        self.assertIn("title: テスト", (out / "frontmatter.md").read_text(encoding="utf-8"))
        self.assertNotIn("title:", "".join(parts))

    def test_code_block_never_split(self):
        code = "```python\n" + "\n".join(f"x{i} = '{JA_PARA}'" for i in range(60)) + "\n```"
        body = JA_PARA * 5 + "\n\n" + code + "\n\n" + JA_PARA * 5 + "\n"
        _, _, parts = self.split(body, max_ja_chars=200)
        holders = [p for p in parts if "```python" in p]
        self.assertEqual(len(holders), 1)
        self.assertEqual(holders[0].count("```"), 2)

    def test_heading_not_left_at_chunk_end(self):
        body = ""
        for i in range(6):
            body += f"## 節{i}\n\n" + JA_PARA * 20 + "\n\n"
        _, _, parts = self.split(body, max_ja_chars=700)
        for p in parts:
            last = [ln for ln in p.strip().splitlines() if ln.strip()][-1]
            self.assertFalse(last.startswith("#"), f"chunk ends with heading: {last}")

    def test_oversized_paragraph_marks_continuation(self):
        body = JA_PARA * 100 + "\n"
        _, manifest, _ = self.split(body, max_ja_chars=600)
        flags = [c["continues_previous_paragraph"] for c in manifest["chunks"]]
        self.assertFalse(flags[0])
        self.assertTrue(all(flags[1:]))


class CliTests(unittest.TestCase):
    def test_missing_file_exits_nonzero(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "measure", "/no/such/file.md"],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
