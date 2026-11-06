# EXTEND.md Schema

EXTEND.md is a Markdown file with a YAML block. Only the YAML block is parsed; any text outside it is ignored and can hold your own notes.

```yaml
# --- Core ---
direction: auto              # auto | ja-en | en-ja
default_mode: normal         # quick | normal | refined
default_context: auto        # auto | academic | business | technical | official | literary | marketing | casual | subtitle | "free-text description"
audience: general            # general | academic | business | technical | free text, e.g. "日本の大学教員"

# --- Japanese output ---
ja_style: auto               # auto (by context) | desu-masu | da-dearu
keigo: auto                  # auto | none | teinei | sonkei-kenjo
ja_numbers: arabic           # arabic | kanji (kanji only for literary/official vertical text)
ja_punctuation: "、。"        # "、。" (standard) | "，。" (some academic/science journals)

# --- English output ---
en_variant: US               # US | UK
en_serial_comma: true
name_order_ja_people: family-first   # family-first (Japanese government documents since 2020-01-01) | given-first

# --- Notes ---
notes: auto                  # auto (by context) | none | inline | footnote

# --- AI tone ---
humanize: guard              # guard (never add AI tone) | rewrite (also tone down AI tone in the source) | off

# --- Glossaries ---
glossary:                    # inline entries; highest priority after --glossary
  - ja: 共生
    en: coexistence
    note: "multicultural coexistence (多文化共生) in policy contexts"
  - ja: 同化圧力
    en: pressure to assimilate
glossary_files:              # paths relative to this EXTEND.md
  - glossaries/my-courses.md

# --- Per-context overrides ---
context_overrides:
  academic:
    ja_style: da-dearu
    notes: footnote
  business:
    keigo: sonkei-kenjo
  casual:
    notes: none

# --- Chunking ---
chunk_threshold_ja: 8000     # characters
chunk_threshold_en: 4000     # words
chunk_max_ja: 6000
chunk_max_en: 3000
```

## Glossary file format

External glossary files are Markdown tables. Columns `ja` and `en` are required; `note` and `context` are optional. A `context` value restricts the entry to that context.

```markdown
| ja | en | context | note |
|---|---|---|---|
| 在留資格 | status of residence | official | Immigration Services Agency term |
| 子どもの権利条約 | Convention on the Rights of the Child | | UN CRC |
| 居場所 | a place to belong | academic | keep 居場所 (ibasho) in parentheses on first use |
```

## Precedence

`--flag` > `context_overrides.<context>` > top-level EXTEND.md keys > context profile defaults > SKILL.md defaults.
