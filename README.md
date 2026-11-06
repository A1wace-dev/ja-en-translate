# ja-en-translate

English | [日本語](README.ja.md) | [中文](README.zh.md)

An agent skill for Japanese⇄English translation that decides **what kind of text it is translating and for whom** before it translates. Works with Claude Code, Codex, and other agents that read `SKILL.md`.

A business email, a course paper, a LINE message, and a subtitle file need different Japanese and different English. This skill picks a context profile for the text (or for each section of it), then applies that profile's rules for register, keigo, restructuring, and translator's notes. It also checks the translation for the failures typical of each direction and for AI-sounding phrasing the source never had.

## Features

- **Eight context profiles:** `academic`, `business`, `technical`, `official`, `literary`, `marketing`, `casual`, `subtitle`. Detected automatically, with the evidence written down; mixed documents get a profile per section.
- **Three modes:** `quick` (translate), `normal` (analyze, then translate), `refined` (analyze, draft, critique, revise, polish). Every step is saved as a file you can read.
- **Direction-specific review.** JA→EN checks omitted subjects, number, tense, implicit logic, 和製英語, and hedging strength. EN→JA checks 翻訳調: pronoun overuse, inanimate subjects, の chains, 〜することができる, mixed 文体, and keigo errors such as 二重敬語.
- **AI-tone guard.** The translation must not add staged contrasts ("not X but Y", 単なる〜ではなく), closer lines (〜と言えるでしょう), inflated significance, or stock vocabulary that the source does not contain. On request (`--humanize rewrite`), it can also tone down AI phrasing that is already in the source, listing every change.
- **Asks instead of guessing.** Subjects, name readings, and referents that the source leaves open are resolved from context and listed under "Please confirm".
- **Long documents.** Japanese is measured in characters and English in words. Long texts are split at Markdown block boundaries and translated in parallel against one shared glossary and brief.
- **Configurable.** Personal glossaries, default context, and per-context overrides in `EXTEND.md`. No dependencies beyond Python 3.9+.

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

After a `normal` run, reply "refine" (or 推敲して / 继续润色) to run the critique and polish steps on the same output.

Output goes to `{source}-{lang}/` next to the source file:

| File | Content |
|---|---|
| `translation.md` | Final translation |
| `01-analysis.md` | Context and evidence, register, term decisions, resolved implicit elements |
| `02-prompt.md` | The brief every translator pass follows |
| `03-draft.md` … `05-revision.md` | Draft, critique (diagnosis only), revision (refined mode) |

## Configuration

On first use the skill asks four questions and writes `~/.ja-en-translate/EXTEND.md`. Add your own terms there:

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
- The built-in glossary is small. Your field's terms belong in your own `EXTEND.md`.
- Inputs other than Markdown and plain text (.docx, .pdf) depend on the conversion tools available to your agent.

## Acknowledgments

- The file-based workflow (modes, numbered intermediate files, `EXTEND.md`, parallel chunk translation) is modeled on [baoyu-translate](https://github.com/JimLiu/baoyu-skills) by Jim Liu (MIT). No text or code is copied.
- The English AI-tone list adapts ideas from Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), rewritten for translation. The Japanese list is original.
- Subtitle limits follow the Netflix Timed Text Style Guides (Japanese; English USA). Legal terminology follows the [Japanese Law Translation](https://www.japaneselawtranslation.go.jp/) database.

## License

[MIT](LICENSE)
