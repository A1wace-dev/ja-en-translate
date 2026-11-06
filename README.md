# ja-en-translate

English | [日本語](README.ja.md) | [中文](README.zh.md)

An agent skill for Japanese⇄English translation. Before it translates, it works out **what kind of text it has and who will read it**. It runs in Claude Code, Codex, and any other agent that reads `SKILL.md`.

A business email, a course paper, a LINE message, and a subtitle file each call for different Japanese and different English. The skill assigns a context profile to the whole text or to each section, and that profile sets the register, the level of keigo, how freely sentences may be restructured, and whether translator's notes are allowed. It then checks the result for the mistakes typical of each translation direction, and for AI-sounding phrasing that is not in the source.

## Features

- **Eight context profiles:** `academic`, `business`, `technical`, `official`, `literary`, `marketing`, `casual`, `subtitle`. The skill chooses one automatically and records why. A mixed document can use a different profile for each section.
- **Three modes:** `quick` (translate), `normal` (analyze, then translate), `refined` (analyze, draft, critique, revise, polish). Every step is saved as a file you can read.
- **Direction-specific review.** For JA→EN it checks omitted subjects, singular and plural, tense, unstated logical links, 和製英語 (Japanese-made English), and how strongly claims are hedged. For EN→JA it checks for 翻訳調 (translationese): pronoun overuse, inanimate subjects, の chains, 〜することができる, mixed 文体, and keigo errors such as 二重敬語.
- **AI-tone guard.** The skill keeps out phrasing the source does not use: contrasts the source never draws ("not X but Y", 単なる〜ではなく), tacked-on closing lines (〜と言えるでしょう), inflated claims of importance, or stock phrases. If you ask (`--humanize rewrite`), it will also tone down AI-sounding phrasing that is already in the source and list every change.
- **Flags its assumptions.** When the source leaves a subject, a name reading, or a referent unstated, the skill decides from context and lists each decision under "Please confirm".
- **Long documents.** Japanese is measured in characters and English in words. Long texts are split at Markdown block boundaries and translated in parallel, with every part following the same glossary and brief.
- **Configurable.** Set personal glossaries, a default context, and per-context overrides in `EXTEND.md`. Requires only Python 3.10 or later.

See [examples/context-switching.md](examples/context-switching.md) and [examples/ai-tone-guard.md](examples/ai-tone-guard.md).

## Install

With the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add A1wace-dev/ja-en-translate --agent claude-code   # other agents: see the skills CLI docs
```

Manually:

```bash
git clone https://github.com/A1wace-dev/ja-en-translate.git
cp -R ja-en-translate/skills/ja-en-translate ~/.claude/skills/   # Claude Code
cp -R ja-en-translate/skills/ja-en-translate ~/.codex/skills/    # Codex
```

In the Claude app, zip the `skills/ja-en-translate` folder and upload it in the Skills section of settings.

## Usage

```text
Translate report.md into English
精翻 abstract.md --context academic
快翻：明日の会議は15時からに変更になりました
この英文メールを日本語にして。取引先の部長宛てです
Translate lecture.srt into Japanese --context subtitle
英訳して、AIっぽさも消して --humanize rewrite
```

No flags are needed: describe the purpose in your own words ("this goes to my professor", "just the gist", "for publication") in English, Japanese, or Chinese, and the skill reads the context, keigo level, and mode from it. Each reply opens with one line showing what it understood, so you can correct it right away.

After a `normal` run, reply "refine" (or 推敲して / 继续润色) to run the critique and polish steps on the same output.

Output goes to `{source}-{lang}/` next to the source file:

| File | Content |
|---|---|
| `translation.md` | Final translation |
| `01-analysis.md` | Chosen context and why, register, terminology decisions, and what was filled in where the source left it unstated |
| `02-prompt.md` | Translation brief shared by every pass |
| `03-draft.md` … `05-revision.md` | Draft, critique (diagnosis only), revision (refined mode) |

## Configuration

Nothing needs to be set up first. After your first translation, the skill offers to save your usual settings to `~/.ja-en-translate/EXTEND.md` (four questions). Add your own terms there:

```yaml
default_context: academic
humanize: guard
glossary:
  - ja: 多文化共生
    en: multicultural coexistence
context_overrides:
  academic:
    notes: footnote
```

Full schema: [extend-schema.md](skills/ja-en-translate/references/config/extend-schema.md).

## Repository layout

```text
skills/ja-en-translate/
├── SKILL.md                    workflow
├── scripts/chunk.py            length measurement and chunking
└── references/
    ├── contexts/               eight context profiles
    ├── ja-to-en-pitfalls.md    JA→EN checklist
    ├── en-to-ja-pitfalls.md    EN→JA checklist
    ├── ai-tone.md              AI-tone patterns (EN and JA)
    ├── keigo-register.md       keigo and register mapping
    ├── style-guide-ja.md       Japanese 表記 rules
    ├── glossary-ja-en.md       built-in glossary
    └── …                       refined workflow, subagent brief, config
examples/                       illustrative before/after tables
tests/                          unit tests (python -m unittest discover -s tests)
```

## Limits

- The rules are guidance for a language model, not a guarantee. Check anything with legal, academic, or financial consequences yourself; for official documents, the Japanese original is authoritative.
- The built-in glossary is small. Add the terms of your own field to `EXTEND.md`.
- For inputs other than Markdown and plain text (.docx, .pdf), results depend on the conversion tools your agent has.

## Acknowledgments

- The file-based workflow (modes, numbered intermediate files, `EXTEND.md`, parallel chunk translation) is modeled on [baoyu-translate](https://github.com/JimLiu/baoyu-skills) by Jim Liu (MIT). No text or code is copied.
- The English AI-tone list adapts ideas from Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), rewritten for translation. The Japanese list is original.
- Subtitle limits follow the Netflix Timed Text Style Guides (Japanese; English USA). Legal terminology follows the [Japanese Law Translation](https://www.japaneselawtranslation.go.jp/) database.

## License

[MIT](LICENSE)
