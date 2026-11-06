"""Extract msgid/msgstr pairs from a Sphinx .po translation into per-file EN and JA texts.

Usage: extract_po.py <python-docs-ja checkout> <output dir>
RST markup is stripped roughly; fuzzy entries and very short strings are skipped.
"""
import re, sys, json
from pathlib import Path

def unquote(lines):
    return "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', "\n".join(lines)))

def parse(path):
    pairs, cur, key = [], {"msgid": [], "msgstr": []}, None
    fuzzy = False
    for line in path.read_text(encoding="utf-8").splitlines() + [""]:
        if line.startswith("#,") and "fuzzy" in line:
            fuzzy = True
        if line.startswith("msgid "):
            if cur["msgid"] and cur["msgstr"]:
                pairs.append((unquote(cur["msgid"]), unquote(cur["msgstr"]), fuzzy0))
            cur, key = {"msgid": [line[6:]], "msgstr": []}, "msgid"
            fuzzy0 = fuzzy; fuzzy = False
        elif line.startswith("msgstr "):
            cur["msgstr"], key = [line[7:]], "msgstr"
        elif line.startswith('"') and key:
            cur[key].append(line)
        elif not line.strip():
            key = None
    if cur["msgid"] and cur["msgstr"]:
        pairs.append((unquote(cur["msgid"]), unquote(cur["msgstr"]), False))
    return pairs

def clean(t):
    t = t.replace("\\n", " ").replace('\\"', '"')
    t = re.sub(r":[a-z:]+:`[^`]*`", "X", t)          # roles
    t = re.sub(r"``([^`]*)``", r"`\1`", t)             # inline literals → backticks
    t = re.sub(r"`([^`<]*)\s*<[^>]*>`_+", r"\1", t)    # links
    t = re.sub(r"\*\*?([^*]+)\*\*?", r"\1", t)
    return t.strip()

root = Path(sys.argv[1]); out = Path(sys.argv[2]); out.mkdir(exist_ok=True)
n = 0
for sub in ["tutorial", "faq", "howto", "library", "using", "reference", "glossary.po", "whatsnew"]:
    for po in sorted((root / sub).rglob("*.po") if (root / sub).is_dir() else [root / sub]):
        if not po.exists():
            continue
        pairs = [(clean(a), clean(b)) for a, b, fz in parse(po) if a and b and not fz]
        pairs = [(a, b) for a, b in pairs if len(a) > 40 and re.search(r"[぀-ヿ]", b)]
        if len(pairs) < 5:
            continue
        name = str(po.relative_to(root)).replace("/", "__")[:-3]
        (out / f"{name}.en.md").write_text("\n\n".join(a for a, _ in pairs) + "\n", encoding="utf-8")
        (out / f"{name}.ja.md").write_text("\n\n".join(b for _, b in pairs) + "\n", encoding="utf-8")
        n += 1
print(n, "documents")
