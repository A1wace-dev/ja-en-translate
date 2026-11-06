"""Tests for tone_lint.py and fidelity_check.py (standard library only)."""
import importlib.util
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "ja-en-translate" / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tone = load("tone_lint")
fid = load("fidelity_check")


def rules(result):
    return {f["rule"] for f in result["findings"]}


class ToneLintJapanese(unittest.TestCase):
    AI = ("本稿では、日本語教室について検討を行います。日本語教室は単なる学習の場ではなく、"
          "地域社会において重要な役割を果たしています。交流が生まれることができます。"
          "これこそが共生の本質なのです。いかがでしたか？\n")
    NATURAL = ("本稿では、地域の日本語教室が外国人住民にとってどのような場になっているかを検討する。\n\n"
               "教室には毎週30人ほどが集まる。授業の後、近所の人と話す時間も設けられている。\n")

    def test_flags_ai_patterns(self):
        r = tone.lint(self.AI, "ja")
        for rule in ["ja-staged-contrast", "ja-inflated", "ja-dekiru", "ja-closer", "ja-chat-residue"]:
            self.assertIn(rule, rules(r))

    def test_natural_text_is_clean(self):
        r = tone.lint(self.NATURAL, "ja")
        self.assertEqual(r["findings"], [])
        self.assertEqual(r["score"], 100)

    def test_mixed_style(self):
        text = "これはペンです。それは本である。あれは机です。机は大きい。椅子もあります。\n"
        self.assertIn("ja-mixed-style", rules(tone.lint(text, "ja")))

    def test_context_relaxes_rules(self):
        text = "新商品が登場！ぜひお試しください🎉\n"
        self.assertIn("ja-cta", rules(tone.lint(text, "ja")))
        self.assertNotIn("ja-cta", rules(tone.lint(text, "ja", "marketing")))

    def test_code_is_ignored(self):
        text = "説明する。\n\n```\n# これは重要な役割を果たします\n```\n"
        self.assertEqual(tone.lint(text, "ja")["findings"], [])


class ToneLintNewRules(unittest.TestCase):
    def test_bold_not_rendered(self):
        self.assertIn("bold-not-rendered", rules(tone.lint("次に**「立場」**を決める。\n", "ja")))
        self.assertNotIn("bold-not-rendered", rules(tone.lint("次に「**立場**」を決める。\n", "ja")))
        self.assertIn("bold-not-rendered", rules(tone.lint("これは**必須です。**詳しくは下。\n", "ja")))

    def test_colon_before_list(self):
        text = "設定は次のとおりです：\n\n- A\n- B\n\n日時：10時\n"
        found = [f for f in tone.lint(text, "ja")["findings"] if f["rule"] == "ja-colon-list"]
        self.assertEqual(len(found), 1)

    def test_pause_comma_is_density_based(self):
        one = "本稿は、地域の教室を扱う。教室には毎週人が集まる。授業のあとに話す時間もある。\n" * 3
        dense = "本稿は、教室を扱う。資料を、配る。人は、集まる。会は、続く。私は、行く。彼らも、来る。冬は、寒い。\n"
        self.assertNotIn("ja-pause-comma", rules(tone.lint(one, "ja")))
        self.assertIn("ja-pause-comma", rules(tone.lint(dense, "ja")))

    def test_tolerance_skip_and_relax(self):
        text = "新商品が登場！ぜひお試しください🎉\n"
        self.assertNotIn("ja-cta", rules(tone.lint(text, "ja", "marketing")))
        relaxed = tone.apply_tolerance([{"rule": "ja-cta", "severity": "medium"}], "business")
        self.assertEqual(relaxed[0]["severity"], "low")
        self.assertIn("ja-cta", rules(tone.lint(text, "ja")))

    def test_matrix_in_docs_matches_code(self):
        doc = (SCRIPTS.parent / "references" / "ai-tone.md").read_text(encoding="utf-8")
        start = doc.index("<!-- tolerance-matrix:start -->") + len("<!-- tolerance-matrix:start -->")
        end = doc.index("<!-- tolerance-matrix:end -->")
        self.assertEqual(doc[start:end].strip(), tone.matrix_markdown().strip())


class ToneLintEnglish(unittest.TestCase):
    def test_flags_ai_patterns(self):
        text = ("Classes are not just places to learn, but they play a crucial role, "
                "highlighting community life. I hope this helps!\n")
        r = tone.lint(text, "en")
        for rule in ["en-staged-contrast", "en-inflated", "en-ing-rider", "en-chat-residue"]:
            self.assertIn(rule, rules(r))

    def test_plain_text_is_clean(self):
        r = tone.lint("The library extended its weekday opening hours.\n", "en")
        self.assertEqual(r["findings"], [])


class FidelityCheck(unittest.TestCase):
    SRC = ("2026年度の調査には3万人が参加した。予算は1億2000万円で、回答率は45.5%だった。\n\n"
           "参加者の多くは日本語教室に通っていない。詳しくは https://example.jp/r を参照。\n")
    GOOD = ("In fiscal 2026, 30,000 people took part. The budget was 120 million yen, "
            "and the response rate was 45.5%.\n\n"
            "Most participants do not attend Japanese classes. See https://example.jp/r for details.\n")
    BAD = ("In fiscal 2026, 3,000 people took part. The budget was 120 million yen, "
           "and the response rate was 45%.\n\n"
           "Most participants attend Japanese classes. See the report for details.\n")

    def test_good_translation_is_clean(self):
        r = fid.check(self.SRC, self.GOOD)
        self.assertEqual(r["counts"]["high"], 0, r["findings"])
        self.assertEqual(r["counts"]["medium"], 0, r["findings"])

    def test_bad_translation_is_caught(self):
        r = fid.check(self.SRC, self.BAD)
        found = rules(r)
        self.assertIn("numbers", found)
        self.assertIn("urls", found)
        self.assertIn("negation", found)

    def test_number_normalization(self):
        self.assertEqual(fid.numbers("3万5000人"), fid.numbers("35,000 people"))
        self.assertEqual(fid.numbers("1億2000万円"), fid.numbers("120 million yen"))
        self.assertEqual(fid.numbers("３０人"), fid.numbers("30 people"))

    def test_negation_false_friends(self):
        self.assertEqual(fid.negations("少ない人数で危ない作業をした。", "ja"), 0)
        self.assertEqual(fid.negations("行かない。", "ja"), 1)

    def test_code_comment_translation_allowed(self):
        src = "```python\nx = 1  # 人数\n```\n"
        out = "```python\nx = 1  # headcount\n```\n"
        self.assertNotIn("code-changed", rules(fid.check(src, out)))
        self.assertIn("code-changed", rules(fid.check(src, "```python\nx = 2  # headcount\n```\n")))

    def test_tables(self):
        src = "| 項目 | 値 |\n|---|---|\n| 人数 | 3万 |\n| 割合 | 45% |\n"
        good = "| Item | Value |\n|---|---|\n| People | 30,000 |\n| Share | 45% |\n"
        bad = "| Item | Value |\n|---|---|\n| People | 3,000 |\n"
        self.assertEqual(fid.check(src, good)["counts"]["high"], 0)
        found = rules(fid.check(src, bad))
        self.assertIn("table-shape", found)
        self.assertIn("table-numbers", found)

    def test_rewrite_mode_terms(self):
        r = fid.check("Claude Code を使って検討を行った。\n", "検討した。\n", "rewrite")
        self.assertIn("terms", rules(r))


if __name__ == "__main__":
    unittest.main()
