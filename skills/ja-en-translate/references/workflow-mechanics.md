# Workflow Mechanics

## Materializing the source

| Input | Action |
|---|---|
| Markdown / text file | Use in place |
| Inline text | Save to `translate/{slug}.md` in the working directory |
| URL | Fetch, convert to Markdown, save to `translate/{slug}.md`; keep the URL in frontmatter as `url` |
| .docx | Convert to Markdown (pandoc or equivalent), keep headings, lists, footnotes |
| .pdf | Extract text; if the layout is complex (two columns, footnotes), check the extraction before translating |
| .srt / .vtt | Keep the file as is; translate cue text only (see contexts/subtitle.md) |

`{slug}`: 2–5 words, lowercase ASCII, hyphenated, from the title or first line (romanize Japanese). Add `-2`, `-3` if it exists.

## Output directory

`{source-dir}/{source-basename}-{target-lang}/` — e.g. `report.md` → `report-en/`. If it exists, ask whether to overwrite or create `report-en-2/` (no user present → create a new one).

If the user wants the result in another format (.docx, .srt), produce `translation.md` first, then convert, keeping both.

## Language detection

- Ratio of kana+kanji characters to Latin letters. >30% Japanese characters → Japanese source.
- Code blocks and URLs are excluded from the count.
- Mixed documents (e.g., English quotes in a Japanese paper): translate only the source-language parts; leave embedded target-language passages as they are, and mention it in the analysis.

## Length measurement

`python3 {baseDir}/scripts/chunk.py measure <file>` prints JSON:

```json
{"language": "ja", "ja_chars": 12400, "en_words": 210, "blocks": 86}
```

Use `ja_chars` for Japanese sources and `en_words` for English sources against the thresholds.

## Splitting

`python3 {baseDir}/scripts/chunk.py split <file> --output-dir <out>/chunks`

- Splits on Markdown block boundaries (headings, paragraphs, lists, tables, code fences, quotes).
- Prefers to break before headings.
- A single oversized block is split by sentence (。！？ or . ! ?), then by line.
- YAML frontmatter is written separately to `chunks/frontmatter.md`.
- Output: `chunk-01.md`, `chunk-02.md`, … and `manifest.json` (order, sizes, first heading of each chunk).

Translated chunks: `chunk-NN-draft.md`. Merge in manifest order with a blank line between chunks — except when a chunk has `"continues_previous_paragraph": true` (an oversized paragraph was split mid-way): join it to the previous chunk's last paragraph with no blank line (a space for English), then smooth the seam in the consistency pass.

## Glossary merging

1. Built-in glossary (references/glossary-ja-en.md)
2. EXTEND.md `glossary_files`
3. EXTEND.md inline `glossary`
4. `--glossary` file
5. Session glossary from term extraction (fills gaps only; never overrides 1–4)

Entries with a `context` field apply only when that context is active.
