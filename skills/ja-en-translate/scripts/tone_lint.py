#!/usr/bin/env python3
"""Flag AI tone and translationese in Japanese or English text.

The output is a list of *candidates*, not verdicts. The agent reads each
finding in context and decides whether to change it (a finding inside a
quotation, a term of art, or a pattern the source itself uses stays).

Usage:
  tone_lint.py <file> [--lang ja|en|auto] [--context NAME] [--format json|text]

Standard library only. Python 3.10+.
"""
import argparse
import json
import re
import sys
from pathlib import Path

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
URL = re.compile(r"https?://\S+")
JA_CHAR = re.compile(r"[぀-ヿ一-鿿]")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐✅]")

# --- Japanese rules: (id, category, severity, regex, hint) -----------------
# severity: high = almost always worth fixing; medium = check in context;
# low = only a problem when dense.
JA_RULES = [
    ("ja-chat-residue", "ai-tone", "high",
     r"いかがでしたか|お役に立てれば幸い|以下に(翻訳|まとめ)を示します|ご参考になれば",
     "Chatbot residue; never belongs in the output."),
    ("ja-staged-contrast", "ai-tone", "medium",
     r"単なる[^。]{1,30}ではなく|ただの[^。]{1,30}ではなく",
     "Staged contrast. Keep only if the source draws this contrast."),
    ("ja-closer", "ai-tone", "medium",
     r"(と言えるでしょう|ではないでしょうか|と言っても過言ではありません|と言っても過言ではない|これこそが[^。]{1,20})。",
     "Closing flourish. Keep only if the source ends this way."),
    ("ja-inflated", "ai-tone", "medium",
     r"重要な役割を果たし|欠かせない存在|鍵を握|鍵となる|大きな転換点|新たな可能性を(切り|拓)|象徴と言え|画期的な|革新的な",
     "Inflated significance. Match the source's actual strength."),
    ("ja-stock-word", "ai-tone", "low",
     r"さまざまな|様々な|多様な|包括的な|シームレスな|において|を通じて|に関して",
     "Stock word; a problem when dense."),
    ("ja-cta", "ai-tone", "medium",
     r"ぜひ[^。]{0,20}(ください|みてください)",
     "Call to action added by the writer? Fine in marketing if the source has it."),
    ("ja-dekiru", "translationese", "medium",
     r"ことができ(る|ます|た|ました|ない|ません)",
     "〜することができる → 〜できる; 〜ことができる → potential form (生まれる → 生まれうる / 生まれる)"),
    ("ja-okonau", "translationese", "low",
     r"を行(う|い|います|いました|った)",
     "〜を行う → verb form (調査を行う → 調査する) unless formal register needs it."),
    ("ja-natteiru", "translationese", "low",
     r"となっています|となっている",
     "〜となっている where no change of state is meant → 〜だ / 〜です"),
    ("ja-no-chain", "translationese", "medium",
     r"[^\s。、「」]{1,8}の[^\s。、「」]{1,8}の[^\s。、「」]{1,8}の",
     "Three or more の in a row; restructure."),
    ("ja-pronoun", "translationese", "medium",
     r"あなたは|あなたが|あなたの|彼女は|彼女が|彼は|彼が",
     "Pronoun likely calqued from English; use a name, a role, or omit."),
    ("ja-dash", "symbols", "medium", r"——|—|―",
     "Dash as a connector; use 、 or split the sentence."),
    ("ja-halfwidth-punct", "symbols", "medium",
     r"[぀-ヿ一-鿿][,.!?:;](?=\s|$|[぀-ヿ一-鿿])",
     "Half-width punctuation after Japanese text."),
    ("ja-fullwidth-digit", "symbols", "low", r"[０-９]+",
     "Full-width digits in horizontal text → half-width."),
]

EN_RULES = [
    ("en-chat-residue", "ai-tone", "high",
     r"(?i)\b(I hope this helps|here is the translation|let me know if|feel free to)\b",
     "Chatbot residue; never belongs in the output."),
    ("en-staged-contrast", "ai-tone", "medium",
     r"(?i)\bnot (just|only|merely) [^.]{1,60}?\bbut\b|\bit'?s not [^.]{1,40}?, it'?s\b",
     "Staged contrast. Keep only if the source draws this contrast."),
    ("en-inflated", "ai-tone", "medium",
     r"(?i)\b(pivotal|crucial role|plays? a (key|vital|crucial) role|a testament to|"
     r"marks? a turning point|enduring legacy|reflects a broader)\b",
     "Inflated significance. Match the source's actual strength."),
    ("en-stock-word", "ai-tone", "low",
     r"(?i)\b(delve|delves|tapestry|landscape|underscore[sd]?|showcas(e|es|ing)|foster(s|ing)?|"
     r"seamless(ly)?|vibrant|meticulous(ly)?|additionally|robust)\b",
     "Stock word; a problem when dense or when the source is plain."),
    ("en-ing-rider", "ai-tone", "medium",
     r"(?i), (highlighting|underscoring|reflecting|showcasing|emphasizing|symbolizing|fostering) ",
     "-ing rider bolted onto a fact; split into a sentence with a real verb."),
    ("en-copula-avoid", "ai-tone", "low",
     r"(?i)\b(serves as|stands as|boasts)\b",
     "Use is / has."),
    ("en-dash", "symbols", "low", r"—|–| -- ",
     "Dash as a connector; fine if the source motivates it."),
]

COMMON_RULES = [
    ("bold-label", "symbols", "medium", r"^\s*[-*+]\s+\*\*[^*]+?(\*\*\s*[:：]|[:：]\s*\*\*)",
     "Bold label on a list item; follow the source's formatting."),
    ("emoji", "symbols", "medium", EMOJI.pattern,
     "Emoji; keep only if the source has them."),
]

# Contexts where some rules are expected rather than suspicious
RELAXED = {
    "marketing": {"ja-cta", "emoji", "ja-stock-word", "en-stock-word"},
    "casual": {"emoji", "ja-cta", "ja-dash"},
    "technical": {"ja-okonau", "bold-label"},
    "official": {"ja-okonau", "ja-natteiru", "ja-stock-word"},
    "subtitle": {"ja-dash"},
}

JA_POLITE = re.compile(r"(です|ます|ました|でした|ません|でしょう|ください)[。！？]?$")
JA_PLAIN = re.compile(r"(である|だ|だった|であった|ではない|のだ|[たるうい])[。！？]$")


def prose_lines(text):
    """Yield (line_no, line) for prose, skipping code fences, tables, and frontmatter."""
    in_fence = False
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break
    for i, line in enumerate(lines[start:], start + 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or line.lstrip().startswith("|"):
            continue
        clean = URL.sub(" ", INLINE_CODE.sub(" ", line))
        yield i, line, clean


def detect_lang(text):
    ja = len(JA_CHAR.findall(text))
    en = sum(1 for c in text if c.isascii() and c.isalpha())
    return "ja" if ja and ja / (ja + en) > 0.3 else "en"


def split_ja_sentences(lines):
    out = []
    for no, line, clean in lines:
        s = clean.strip()
        if not s or s.startswith("#") or re.match(r"^[-*+>]|\d+\.", s):
            continue
        for sent in re.findall(r"[^。！？]+[。！？]?", s):
            sent = sent.strip()
            if len(sent) > 1:
                out.append((no, sent))
    return out


def lint(text, lang="auto", context=None):
    if lang == "auto":
        lang = detect_lang(text)
    rules = (JA_RULES if lang == "ja" else EN_RULES) + COMMON_RULES
    relaxed = RELAXED.get(context or "", set())
    lines = list(prose_lines(text))
    findings = []

    for rid, cat, sev, pat, hint in rules:
        if rid in relaxed:
            continue
        rx = re.compile(pat, re.M)
        for no, raw, clean in lines:
            target = raw if rid == "bold-label" else clean
            for m in rx.finditer(target):
                findings.append({"line": no, "rule": rid, "category": cat,
                                 "severity": sev, "match": m.group(0)[:60], "hint": hint})

    if lang == "ja":
        sents = split_ja_sentences(lines)
        # Long sentences
        for no, s in sents:
            if len(s) > 100:
                findings.append({"line": no, "rule": "ja-long-sentence", "category": "readability",
                                 "severity": "medium", "match": s[:40] + "…",
                                 "hint": f"{len(s)} characters; consider splitting."})
        # Mixed 文体
        polite = sum(1 for _, s in sents if JA_POLITE.search(s))
        plain = sum(1 for _, s in sents if not JA_POLITE.search(s) and JA_PLAIN.search(s))
        if polite and plain and min(polite, plain) / (polite + plain) > 0.15:
            findings.append({"line": 0, "rule": "ja-mixed-style", "category": "register",
                             "severity": "high", "match": f"です・ます {polite} / だ・である {plain}",
                             "hint": "Mixed 文体 in body text; pick one (quotes excepted)."})
        # Same ending three times in a row
        ends = [(no, s[-4:]) for no, s in sents]
        for i in range(2, len(ends)):
            if ends[i][1] == ends[i - 1][1] == ends[i - 2][1]:
                findings.append({"line": ends[i][0], "rule": "ja-same-ending", "category": "readability",
                                 "severity": "low", "match": ends[i][1],
                                 "hint": "Same sentence ending three times in a row."})

    # Density rules: low-severity hits only matter when frequent
    size = max(len(text), 1)
    per_k = {}
    for f in findings:
        if f["severity"] == "low":
            per_k[f["rule"]] = per_k.get(f["rule"], 0) + 1
    dense = {r for r, n in per_k.items() if n * 1000 / size >= (6 if lang == "ja" else 3)}
    findings = [f for f in findings if f["severity"] != "low" or f["rule"] in dense]

    weights = {"high": 8, "medium": 3, "low": 1}
    penalty = sum(weights[f["severity"]] for f in findings) * 1000 / max(size, 1000)
    score = max(0, round(100 - penalty))
    findings.sort(key=lambda f: (f["line"], f["rule"]))
    return {"language": lang, "context": context, "score": score,
            "counts": {s: sum(1 for f in findings if f["severity"] == s) for s in weights},
            "findings": findings}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", type=Path)
    ap.add_argument("--lang", choices=["ja", "en", "auto"], default="auto")
    ap.add_argument("--context")
    ap.add_argument("--format", choices=["json", "text"], default="json")
    a = ap.parse_args()
    if not a.file.is_file():
        sys.exit(f"File not found: {a.file}")
    r = lint(a.file.read_text(encoding="utf-8"), a.lang, a.context)
    if a.format == "json":
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"language={r['language']} score={r['score']} counts={r['counts']}")
        for f in r["findings"]:
            print(f"L{f['line']:>4} [{f['severity']}] {f['rule']}: {f['match']}  ({f['hint']})")


if __name__ == "__main__":
    main()
