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
URL = re.compile(r"https?://[^\s)>\]」』]+")
INLINE_CODE = re.compile(r"`[^`\n]+`")
LINK_TARGET = re.compile(r"\]\(([^)\s]+)")
FOOTNOTE = re.compile(r"\[\^[^\]]+\]")
HEADING = re.compile(r"^#{1,6}\s", re.M)
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s", re.M)

FW = str.maketrans("０１２３４５６７８９．，％", "0123456789.,%")
KANJI_DIGIT = {"〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
EN_SCALE = {"thousand": 1e3, "million": 1e6, "billion": 1e9, "trillion": 1e12}

NEG_JA = re.compile(
    r"(?<![少危汚幼切])な(い|かった|く(?!て)|しで)|ません|ませんでした|ず[、。にとも]|ぬ[。、]|"
    r"(?<![一-鿿])(不|非|未|無)[一-鿿]")
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
    for m in re.finditer(r"([〇一二三四五六七八九十百千]+)(?=[人件年月日回歳つ個名社校万億%パ])", text):
        k = kanji_number(m.group(1))
        if k is not None and m.group(1) not in {"一"}:
            vals.append(float(k))
    return Counter(round(v, 4) for v in vals)


def paragraphs(prose):
    return [p.strip() for p in re.split(r"\n\s*\n", prose) if p.strip()]


def negations(text, lang):
    rx = NEG_JA if lang == "ja" else NEG_EN
    return len(rx.findall(text))


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

    for name, rx in [("urls", URL), ("inline-code", INLINE_CODE),
                     ("link-targets", LINK_TARGET), ("footnotes", FOOTNOTE)]:
        a, b = Counter(rx.findall(s_prose)), Counter(rx.findall(o_prose))
        missing, extra = a - b, b - a
        if name == "inline-code" and mode == "translate":
            # Identifiers must survive; translated prose in backticks is rare
            pass
        if missing:
            add("high", name, "Missing in output: " + ", ".join(list(missing)[:8]))
        if extra:
            add("medium", name, "Not in source: " + ", ".join(list(extra)[:8]))

    for name, rx in [("headings", HEADING), ("list-items", LIST_ITEM)]:
        a, b = len(rx.findall(s_prose)), len(rx.findall(o_prose))
        if a != b:
            add("medium", name, f"{a} in source, {b} in output.")

    # Numbers: whole document
    sn, on = numbers(s_prose), numbers(o_prose)
    miss, extra = sn - on, on - sn
    if miss:
        add("high", "numbers", "In source, not found in output: " + ", ".join(fmt_num(v) for v in sorted(miss.elements())))
    if extra:
        add("medium", "numbers", "In output, not in source: " + ", ".join(fmt_num(v) for v in sorted(extra.elements())))

    # Paragraph-level checks when the structure lines up
    sp, op = paragraphs(s_prose), paragraphs(o_prose)
    aligned = len(sp) == len(op)
    if not aligned:
        add("low", "paragraphs", f"{len(sp)} paragraphs in source, {len(op)} in output; "
            "paragraph-level checks skipped.")
    else:
        for i, (a, b) in enumerate(zip(sp, op), 1):
            na, nb = numbers(a), numbers(b)
            if na != nb and (na - nb):
                add("high", "numbers-paragraph",
                    "Numbers differ: " + ", ".join(fmt_num(v) for v in sorted((na - nb).elements())), f"paragraph {i}")
            ga, gb = negations(a, s_lang), negations(b, o_lang)
            if (ga == 0) != (gb == 0) or (mode == "rewrite" and ga != gb):
                add("medium", "negation", f"Negation count {ga} in source, {gb} in output; check polarity.",
                    f"paragraph {i}")

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
