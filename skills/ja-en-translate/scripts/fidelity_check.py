#!/usr/bin/env python3
"""Compare a source and its translation (or rewrite) for things that must not change.

Checks numbers (with 万/億 and million/billion normalized), negation, URLs,
inline code, code blocks, link targets, footnote markers, and Markdown
structure. Paragraphs are aligned when both files have the same number of
paragraphs, so findings can point to a location.

Findings are signals for the agent to inspect, not proof of an error: a
translation may legitimately turn "30,000" into "3万", or express a negation
with an antonym.

Usage:
  fidelity_check.py <source> <output> [--mode translate|rewrite] [--format json|text]

Standard library only. Python 3.10+.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

FENCE = re.compile(r"^\s*(```|~~~)")
URL = re.compile(r"https?://[^\s)>\]」』`]+?(?=[.,;:!?、。]*(?:[\s)>\]」』`]|$))")
INLINE_CODE = re.compile(r"`[^`\n]+`")
LINK_TARGET = re.compile(r"\]\(([^)\s]+)")
FOOTNOTE = re.compile(r"\[\^[^\]]+\]")
HEADING = re.compile(r"^#{1,6}\s", re.M)
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s", re.M)

FW = str.maketrans("０１２３４５６７８９．，％", "0123456789.,%")
KANJI_DIGIT = {"〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
EN_WORD_NUM = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
               "ten": 10, "eleven": 11, "twelve": 12, "twenty": 20, "hundred": 100}
EN_SCALE = {"thousand": 1e3, "million": 1e6, "billion": 1e9, "trillion": 1e12}

# Grammatical negation only. Lexical negation (不/非/未/無, un-/non-) is skipped because
# the two languages often express it differently (未知 = "unknown", no "not").
NEG_JA = re.compile(
    r"(?<![少危汚幼切])な(い(?!し)|かった|く(?!て)|しで)|ません|ませんでした|ず[、。にとも]|ぬ[。、]")
# Forms that contain ない but are not negation: obligation, possibility, conjecture
NEG_JA_FALSE = re.compile(
    r"(?:なければ|なくては|ないと|ねば)(?:なら|なり|いけ)(?:ない|ず|ぬ|なかった|ません(?:でした)?)|"
    r"(?:かもしれ|かも知れ|に違い|に他なら|かね|しか|ほか|ざるを得)(?:ない|ません|ず)|"
    r"ではないでしょうか|ではないか|じゃないか|"
    # Contrastive "not A but B" negates a framing, not the predicate; counting it would let an
    # added contrast hide a lost negation elsewhere
    r"(?:では|じゃ|だけで|のみで|ばかりで)なく")
NEG_EN_FALSE = re.compile(r"(?i)\bnot (?:just|only|merely|simply)\b|\bno longer than\b|\bnot to mention\b")
# Wider net used only to ask "does the output express negation at all?": conditional and
# lexical forms a translator may legitimately use for a source "not".
NEG_JA_WIDE = re.compile(r"なけれ|なくて|ないと|以外|未満|以下|満たず|めったに|ほとんど|わずか|未[\u4E00-\u9FFF]|不[\u4E00-\u9FFF]|非[\u4E00-\u9FFF]|無[\u4E00-\u9FFF]|ぬき|抜き|欠")
NEG_EN_WIDE = re.compile(r"(?i)\b(fewer than|less than|below|at most|hardly|barely|rarely|seldom|unless|except|other than|instead of|fails? to|lacks?|absent|missing|un[a-z]{3,}|non-?[a-z]{3,}|in(?:valid|correct|complete|active|compatible))\b")
NEG_EN = re.compile(r"(?i)\b(not|no|never|none|nobody|nothing|neither|nor|without|cannot)\b|n't\b")


def split_code(text):
    """Return (prose, code_blocks)."""
    prose, code, buf, in_fence = [], [], [], False
    for line in text.splitlines():
        if FENCE.match(line):
            if in_fence:
                buf.append(line)
                code.append("\n".join(buf))
                buf = []
            else:
                buf = [line]
            in_fence = not in_fence
            continue
        (buf if in_fence else prose).append(line)
    return "\n".join(prose), code


def strip_frontmatter(text):
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[text.find("\n", end + 4) + 1:]
    return text


def kanji_number(s):
    """Small kanji numerals like 三, 十二, 二十五 (up to 9999); returns None if not one."""
    if not s or any(c not in "〇一二三四五六七八九十百千" for c in s):
        return None
    total, cur = 0, 0
    for c in s:
        if c in KANJI_DIGIT:
            cur = KANJI_DIGIT[c]
        else:
            mult = {"十": 10, "百": 100, "千": 1000}[c]
            total += (cur or 1) * mult
            cur = 0
    return total + cur


def numbers(text):
    """Extract numeric values, normalizing 万/億 and English scale words."""
    t = text.translate(FW)
    t = URL.sub(" ", INLINE_CODE.sub(" ", t))
    t = FOOTNOTE.sub(" ", t)
    t = re.sub(r"^\s*\d+[.)]\s", " ", t, flags=re.M)  # ordered-list markers
    vals = []
    # Japanese compound: 1億2000万, 3万5000, 2.5万
    for m in re.finditer(r"(?:(\d+(?:\.\d+)?)億)?(?:(\d+(?:\.\d+)?)万)?(\d+(?:,\d{3})*(?:\.\d+)?)?", t):
        oku, man, rest = m.group(1), m.group(2), m.group(3)
        if not (oku or man or rest):
            continue
        if oku or man:
            v = float(oku or 0) * 1e8 + float(man or 0) * 1e4 + float((rest or "0").replace(",", ""))
            vals.append(v)
        else:
            v = float(rest.replace(",", ""))
            tail = t[m.end():m.end() + 12].lower()
            sm = re.match(r"\s*(thousand|million|billion|trillion)\b", tail)
            if sm:
                v *= EN_SCALE[sm.group(1)]
            vals.append(v)
    # Kanji numerals followed by a counter (三人, 十二月, 二十五年)
    for m in re.finditer(r"([〇一二三四五六七八九十百千]+)(?=[人件年月日回歳つ個名社校%パ週時分秒倍冊枚台か])", text):
        k = kanji_number(m.group(1))
        if k is not None:
            vals.append(float(k))
    # "one" only before a unit ("one-week", "one hour"); elsewhere it is usually a pronoun
    for m in re.finditer(r"(?i)\bone[- ](?=(?:week|day|month|year|hour|minute|second|time|page|person|item)s?\b)", t):
        vals.append(1.0)
    return Counter(round(v, 4) for v in vals)


def tables(prose):
    """Return [(rows, cols, numbers)] for each Markdown table (separator row excluded)."""
    out, cur = [], []
    for line in prose.splitlines() + [""]:
        if line.strip().startswith("|"):
            cur.append(line.strip())
            continue
        if cur:
            body = [r for r in cur if not re.fullmatch(r"\|?(\s*:?-+:?\s*\|)+\s*:?-*:?\s*\|?", r)]
            cols = max(len([c for c in r.strip("|").split("|")]) for r in body) if body else 0
            out.append((len(body), cols, numbers("\n".join(body))))
            cur = []
    return out


def word_numbers(text):
    """English number words. They satisfy digits on the other side ("2つの教室" → "two classes",
    "three" → 3回) but are never required, because translators also render them as 両方, 数個, etc."""
    return {float(EN_WORD_NUM[m.group(1).lower()]) for m in re.finditer(
        r"(?i)\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|hundred)\b", text)}


def paragraphs(prose):
    return [p.strip() for p in re.split(r"\n\s*\n", prose) if p.strip()]


def expresses_negation(text, lang):
    """True if the text contains grammatical or lexical/conditional negation."""
    if negations(text, lang):
        return True
    text = INLINE_CODE.sub(" ", text)
    return bool((NEG_JA_WIDE if lang == "ja" else NEG_EN_WIDE).search(text))


def negations(text, lang):
    text = INLINE_CODE.sub(" ", text)
    if lang == "ja":
        text = NEG_JA_FALSE.sub(" ", text)
        return len(NEG_JA.findall(text))
    return len(NEG_EN.findall(NEG_EN_FALSE.sub(" ", text)))


def lang_of(text):
    ja = len(re.findall(r"[぀-ヿ一-鿿]", text))
    en = sum(1 for c in text if c.isascii() and c.isalpha())
    return "ja" if ja and ja / (ja + en) > 0.3 else "en"


def fmt_num(v):
    return str(int(v)) if v == int(v) else str(v)


def check(src_text, out_text, mode="translate"):
    src_text, out_text = strip_frontmatter(src_text), strip_frontmatter(out_text)
    s_prose, s_code = split_code(src_text)
    o_prose, o_code = split_code(out_text)
    s_lang, o_lang = lang_of(s_prose), lang_of(o_prose)
    findings = []

    def add(sev, rule, msg, where=None):
        findings.append({"severity": sev, "rule": rule, "where": where, "message": msg})

    # Code blocks must be identical (comments inside may be translated: compare non-comment lines)
    def code_core(block):
        out = []
        for ln in block.splitlines()[1:-1]:  # skip the fence lines
            if not ln.strip() or re.match(r"^\s*(#|//|--|/\*|\*)", ln):
                continue  # whole-line comment: may be translated
            ln = re.sub(r"\s+(#|//)\s.*$", "", ln)  # trailing comment
            out.append(ln.strip())
        return out
    if len(s_code) != len(o_code):
        add("high", "code-blocks", f"{len(s_code)} code blocks in source, {len(o_code)} in output.")
    else:
        for i, (a, b) in enumerate(zip(s_code, o_code), 1):
            if code_core(a) != code_core(b):
                add("high", "code-changed", "Code changed (outside comments).", f"code block {i}")

    def identifier_like(tok):
        inner = tok.strip("`")
        return bool(inner) and " " not in inner and not re.search(r"[\u3040-\u30FF\u4E00-\u9FFF]", inner)

    for name, rx in [("urls", URL), ("inline-code", INLINE_CODE),
                     ("link-targets", LINK_TARGET), ("footnotes", FOOTNOTE)]:
        a, b = set(rx.findall(s_prose)), set(rx.findall(o_prose))
        missing, extra = sorted(a - b), sorted(b - a)
        if name == "inline-code":
            # Identifiers (no spaces, no Japanese) must survive; a phrase in backticks may be translated
            hard = [t for t in missing if identifier_like(t)]
            soft = [t for t in missing if not identifier_like(t)]
            if hard:
                add("high", name, "Missing in output: " + ", ".join(hard[:8]))
            if soft:
                add("low", name, "Phrase in backticks not found verbatim (translated?): " + ", ".join(soft[:8]))
            if extra:
                add("medium", name, "Not in source: " + ", ".join(extra[:8]))
            continue
        if missing:
            add("high", name, "Missing in output: " + ", ".join(missing[:8]))
        if extra:
            add("medium", name, "Not in source: " + ", ".join(extra[:8]))

    for name, rx in [("headings", HEADING), ("list-items", LIST_ITEM)]:
        a, b = len(rx.findall(s_prose)), len(rx.findall(o_prose))
        if a != b:
            add("medium", name, f"{a} in source, {b} in output.")

    # Tables: same number of tables, rows, columns, and the same numbers in each
    st, ot = tables(s_prose), tables(o_prose)
    if len(st) != len(ot):
        add("high", "tables", f"{len(st)} tables in source, {len(ot)} in output.")
    else:
        for i, ((sr, sc, sn_), (orr, oc, on_)) in enumerate(zip(st, ot), 1):
            if (sr, sc) != (orr, oc):
                add("high", "table-shape", f"{sr}×{sc} in source, {orr}×{oc} in output.", f"table {i}")
            if sn_ - on_:
                add("high", "table-numbers",
                    "Numbers missing: " + ", ".join(fmt_num(v) for v in sorted((sn_ - on_).elements())), f"table {i}")

    # Numbers: whole document
    sn, on = numbers(s_prose), numbers(o_prose)
    gone = set(sn) - set(on) - word_numbers(o_prose)
    new = set(on) - set(sn) - word_numbers(s_prose)
    if gone:
        add("high", "numbers", "In source, not found in output: " + ", ".join(fmt_num(v) for v in sorted(gone)))
    if new:
        add("medium", "numbers", "In output, not in source: " + ", ".join(fmt_num(v) for v in sorted(new)))
    recount = [v for v in set(sn) & set(on) if sn[v] != on[v]]
    if recount:
        add("low", "number-count", "Same value, different number of mentions (often a pronoun such as それ): "
            + ", ".join(fmt_num(v) for v in sorted(recount)))

    # Paragraph-level checks when the structure lines up
    sp, op = paragraphs(s_prose), paragraphs(o_prose)
    aligned = len(sp) == len(op)
    if not aligned:
        add("low", "paragraphs", f"{len(sp)} paragraphs in source, {len(op)} in output; "
            "negation is compared for the whole document instead of per paragraph.")
        # Letters and emails gain or lose greeting paragraphs, so compare totals instead
        ga, gb = negations(s_prose, s_lang), negations(o_prose, o_lang)
        if ga and not expresses_negation(o_prose, o_lang):
            add("high", "negation", f"Source has {ga} negation(s), output has none; check polarity.")
        elif ga > gb:
            add("medium", "negation", f"Source has {ga} negation(s), output has {gb}; find the one that was "
                "lost or rephrased.")
    else:
        for i, (a, b) in enumerate(zip(sp, op), 1):
            gone = set(numbers(a)) - set(numbers(b)) - word_numbers(b)
            if gone:
                add("high", "numbers-paragraph",
                    "Numbers missing: " + ", ".join(fmt_num(v) for v in sorted(gone)), f"paragraph {i}")
            ga, gb = negations(a, s_lang), negations(b, o_lang)
            if ga and not gb and not expresses_negation(b, o_lang):
                add("medium", "negation", f"Source has {ga} negation(s), output has none; check polarity.",
                    f"paragraph {i}")
            elif gb and not ga and not expresses_negation(a, s_lang):
                add("low", "negation-added", f"Output has {gb} negation(s), source has none; usually a "
                    "rephrasing (e.g. 'only' → 〜しか〜ない), check if unsure.", f"paragraph {i}")
            elif mode == "rewrite" and ga != gb:
                add("medium", "negation", f"Negation count {ga} → {gb}; check polarity.", f"paragraph {i}")

    # Rewrite mode: same language, so names and Latin terms should survive
    if mode == "rewrite":
        terms = re.compile(r"[A-Za-z][A-Za-z0-9.+#-]{1,}|[゠-ヿ]{3,}")
        a, b = Counter(terms.findall(s_prose)), Counter(terms.findall(o_prose))
        lost = [t for t in a if t not in b]
        if lost:
            add("medium", "terms", "Terms in source not in output: " + ", ".join(lost[:12]))

    order = {"high": 0, "medium": 1, "low": 2}
    findings.sort(key=lambda f: order[f["severity"]])
    return {"mode": mode, "source_language": s_lang, "output_language": o_lang,
            "paragraphs_aligned": aligned,
            "counts": {k: sum(1 for f in findings if f["severity"] == k) for k in order},
            "findings": findings}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--mode", choices=["translate", "rewrite"], default="translate")
    ap.add_argument("--format", choices=["json", "text"], default="json")
    a = ap.parse_args()
    for p in (a.source, a.output):
        if not p.is_file():
            sys.exit(f"File not found: {p}")
    r = check(a.source.read_text(encoding="utf-8"), a.output.read_text(encoding="utf-8"), a.mode)
    if a.format == "json":
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"mode={r['mode']} {r['source_language']}→{r['output_language']} "
              f"aligned={r['paragraphs_aligned']} counts={r['counts']}")
        for f in r["findings"]:
            where = f" ({f['where']})" if f["where"] else ""
            print(f"[{f['severity']}] {f['rule']}{where}: {f['message']}")


if __name__ == "__main__":
    main()
