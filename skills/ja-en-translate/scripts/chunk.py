#!/usr/bin/env python3
"""Measure and split Markdown for JA<->EN translation.

Japanese is measured in characters (kana, kanji, full-width forms),
English in words, so thresholds work for both languages.

Usage:
  chunk.py measure <file>
  chunk.py split <file> --output-dir DIR [--max-ja-chars N] [--max-en-words N]

Standard library only. Python 3.9+.
"""
import argparse
import json
import re
import sys
from pathlib import Path

JA_CHAR = re.compile(
    r"[぀-ゟ"   # hiragana
    r"゠-ヿ"    # katakana
    r"㐀-䶿"    # CJK ext A
    r"一-鿿"    # CJK unified
    r"豈-﫿"    # CJK compatibility
    r"ｦ-ﾟ"    # half-width katakana
    r"　-〿"    # CJK punctuation
    r"！-｠]"   # full-width forms
)
EN_WORD = re.compile(r"[A-Za-z][A-Za-z'’\-]*")
FENCE = re.compile(r"^(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
URL = re.compile(r"https?://\S+")
SENTENCE_END = re.compile(r"(?<=[。！？!?])|(?<=\.)\s+")


def strip_noise(text: str) -> str:
    """Remove code and URLs so they don't count toward language length."""
    out, in_fence = [], False
    for line in text.splitlines():
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    t = "\n".join(out)
    t = INLINE_CODE.sub(" ", t)
    return URL.sub(" ", t)


def measure_text(text: str) -> dict:
    clean = strip_noise(text)
    ja = len(JA_CHAR.findall(clean))
    en = len(EN_WORD.findall(clean))
    # Language: share of Japanese characters among (JA chars + EN letters)
    en_letters = sum(1 for c in clean if c.isascii() and c.isalpha())
    total = ja + en_letters
    lang = "ja" if total and ja / total > 0.3 else "en"
    return {"language": lang, "ja_chars": ja, "en_words": en}


def size_of(text: str, lang: str) -> int:
    m = measure_text(text)
    return m["ja_chars"] if lang == "ja" else m["en_words"]


def split_frontmatter(text: str):
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            close = text.find("\n", end + 4)
            close = len(text) if close == -1 else close + 1
            return text[:close], text[close:]
    return "", text


def parse_blocks(body: str):
    """Split Markdown into blocks: fenced code kept whole, others split on blank lines."""
    blocks, buf, in_fence = [], [], False
    for line in body.splitlines():
        if FENCE.match(line.strip()):
            if not in_fence and buf:
                blocks.append("\n".join(buf))
                buf = []
            buf.append(line)
            in_fence = not in_fence
            if not in_fence:
                blocks.append("\n".join(buf))
                buf = []
            continue
        if in_fence:
            buf.append(line)
            continue
        if line.strip() == "":
            if buf:
                blocks.append("\n".join(buf))
                buf = []
        elif line.lstrip().startswith("#") and buf:
            # heading starts a new block even without a blank line
            blocks.append("\n".join(buf))
            buf = [line]
        else:
            buf.append(line)
    if buf:
        blocks.append("\n".join(buf))
    return [b for b in blocks if b.strip()]


def split_oversized(block: str, lang: str, limit: int):
    """Split one block by sentence, then by line, keeping each piece <= limit when possible."""
    if FENCE.match(block.strip()):
        return [block]  # never split code
    units = [u for u in SENTENCE_END.split(block) if u and u.strip()]
    if len(units) <= 1:
        units = block.splitlines()
    pieces, cur = [], ""
    for u in units:
        cand = cur + u if lang == "ja" else (cur + " " + u).strip()
        if cur and size_of(cand, lang) > limit:
            pieces.append(cur)
            cur = u
        else:
            cur = cand
    if cur:
        pieces.append(cur)
    return pieces


def build_chunks(blocks, lang, limit):
    chunks, cur, cur_size = [], [], 0
    continuations = set()
    for b in blocks:
        bsize = size_of(b, lang)
        parts = split_oversized(b, lang, limit) if bsize > limit else [b]
        for idx, p in enumerate(parts):
            psize = size_of(p, lang)
            is_heading = p.lstrip().startswith("#")
            # Prefer to start a new chunk at a heading once the current one is half full
            only_headings = all(x.lstrip().startswith("#") for x in cur)
            # Never leave a heading alone at the end of a chunk
            if cur and not only_headings and (
                    cur_size + psize > limit or (is_heading and cur_size > limit * 0.5)):
                carry = []
                while cur and cur[-1].lstrip().startswith("#"):
                    carry.insert(0, cur.pop())
                chunks.append(cur)
                cur = carry
                cur_size = sum(size_of(x, lang) for x in carry)
            if idx > 0 and not cur:
                continuations.add(len(chunks))  # chunk starts mid-paragraph
            cur.append(p)
            cur_size += psize
    if cur:
        chunks.append(cur)
    return ["\n\n".join(c) + "\n" for c in chunks], continuations


def first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            return line.lstrip("# ").strip()
    return ""


def cmd_measure(path: Path):
    text = path.read_text(encoding="utf-8")
    _, body = split_frontmatter(text)
    result = measure_text(body)
    result["blocks"] = len(parse_blocks(body))
    print(json.dumps(result, ensure_ascii=False))


def cmd_split(path: Path, out: Path, max_ja: int, max_en: int):
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    lang = measure_text(body)["language"]
    limit = max_ja if lang == "ja" else max_en
    out.mkdir(parents=True, exist_ok=True)
    if fm:
        (out / "frontmatter.md").write_text(fm, encoding="utf-8")
    chunks, continuations = build_chunks(parse_blocks(body), lang, limit)
    manifest = {"source": str(path), "language": lang,
                "unit": "ja_chars" if lang == "ja" else "en_words",
                "limit": limit, "has_frontmatter": bool(fm), "chunks": []}
    for i, c in enumerate(chunks, 1):
        name = f"chunk-{i:02d}.md"
        (out / name).write_text(c, encoding="utf-8")
        manifest["chunks"].append({"file": name, "size": size_of(c, lang),
                                   "first_heading": first_heading(c),
                                   "continues_previous_paragraph": (i - 1) in continuations})
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"language": lang, "chunks": len(chunks),
                      "output_dir": str(out)}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure")
    m.add_argument("file", type=Path)
    s = sub.add_parser("split")
    s.add_argument("file", type=Path)
    s.add_argument("--output-dir", type=Path, required=True)
    s.add_argument("--max-ja-chars", type=int, default=6000)
    s.add_argument("--max-en-words", type=int, default=3000)
    a = ap.parse_args()
    if not a.file.is_file():
        sys.exit(f"File not found: {a.file}")
    if a.cmd == "measure":
        cmd_measure(a.file)
    else:
        cmd_split(a.file, a.output_dir, a.max_ja_chars, a.max_en_words)


if __name__ == "__main__":
    main()
