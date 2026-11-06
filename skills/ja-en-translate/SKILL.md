---
name: ja-en-translate
description: Context-aware Japanese↔English translation with three modes (quick/normal/refined), eight context profiles (academic, business, technical, official, literary, marketing, casual, subtitle), keigo/register control, and glossary consistency. Use when the user asks to translate between Japanese and English — "翻訳して", "英訳", "和訳", "日本語にして", "英語にして", "日英翻译", "英日翻译", "翻成日文", "翻成英文", "translate to Japanese", "translate to English", "精翻", "快翻", "refined translation", "proofread translation", "去掉AI味", "AIっぽさを消して" — or provides a Japanese/English file or URL with translation intent.
version: 1.1.0
---

# JA⇄EN Context-Aware Translator

Japanese↔English translation that first decides **what kind of text this is and who it is for (the context)**, then translates under that context's rules. Built on the same file-based pipeline as baoyu-translate: every step leaves a file, so the reasoning behind each choice can be inspected.

Four things set it apart from a generic translation prompt:

1. **Context profiles** decide register, keigo level, how much to restructure, and whether translator's notes are allowed. One document may contain several contexts (e.g., an academic paper quoting an interview).
2. **Direction-specific review.** JA→EN and EN→JA fail in different ways (subject omission vs. 翻訳調), so the critique step uses a checklist for the actual direction.
3. **AI-tone guard.** The translation must not add the stock voice of machine-written text (staged contrasts, inflated significance, 「〜と言えるでしょう」 closers) that the source does not have. Optionally, AI tone already in the source can be reduced on request.
4. **CJK-aware length measurement.** Japanese is measured in characters, English in words, so long Japanese texts are chunked correctly.

## User Input Tools

When this skill asks the user something, choose the tool in this order:

1. **Prefer the runtime's built-in input tool** — `AskUserQuestion`, `request_user_input`, `ask_user`, or equivalent.
2. **Fallback**: a numbered plain-text message; ask the user to reply with the number for each question.
3. **Batching**: put all pending questions into one call when the tool allows it.

If no user is present (scheduled or headless run), never block: take the most reasonable reading, state it at the top of `01-analysis.md`, and continue.

## Script Directory

`{baseDir}` = this SKILL.md's directory. Scripts run with Python 3.10+ and the standard library only.

| Script | Purpose |
|---|---|
| `scripts/chunk.py` | Measure length (JA chars / EN words) and split Markdown into chunks at block boundaries |

```
python3 {baseDir}/scripts/chunk.py measure <file>
python3 {baseDir}/scripts/chunk.py split <file> --output-dir <dir> [--max-ja-chars 6000] [--max-en-words 3000]
```

## Preferences (EXTEND.md)

Check these paths in order; the first found wins:

| Priority | Path | Scope |
|---|---|---|
| 1 | `.ja-en-translate/EXTEND.md` | Project |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/ja-en-translate/EXTEND.md` | XDG |
| 3 | `$HOME/.ja-en-translate/EXTEND.md` | User home |

| Result | Action |
|---|---|
| Found | Read and apply. On first use in a session, say once: "Using preferences from [path]." |
| Not found | Run first-time setup (references/config/first-time-setup.md). Ask all questions in ONE call, write EXTEND.md, confirm the path, then continue. If no user is present, use Defaults and say so. |

Schema: references/config/extend-schema.md

## Defaults

EXTEND.md overrides these; flags in the request override EXTEND.md.

| Setting | Default | EXTEND.md key | Flag | Notes |
|---|---|---|---|---|
| Direction | auto | `direction` | `--to ja` / `--to en` | Auto: JA source → EN, EN source → JA |
| Mode | normal | `default_mode` | `--mode` | quick / normal / refined |
| Context | auto | `default_context` | `--context` | See Context Profiles |
| Japanese style (文体) | by context | `ja_style` | `--ja-style` | `desu-masu` / `da-dearu` |
| Keigo level | by context | `keigo` | `--keigo` | `none` / `teinei` / `sonkei-kenjo` |
| English variant | US | `en_variant` | `--en` | `US` / `UK` |
| Audience | general | `audience` | `--audience` | Free text accepted |
| Translator's notes | by context | `notes` | `--notes` | `none` / `inline` / `footnote` |
| AI-tone handling | guard | `humanize` | `--humanize` | `guard` / `rewrite` / `off` — see references/ai-tone.md |
| Chunk threshold | 8000 JA chars / 4000 EN words | `chunk_threshold_ja`, `chunk_threshold_en` | — | |
| Chunk max size | 6000 JA chars / 3000 EN words | `chunk_max_ja`, `chunk_max_en` | — | |

## Modes

| Mode | Steps | When |
|---|---|---|
| Quick | Translate | Short texts, chat messages, getting the gist |
| Normal (default) | Analyze → Translate | Articles, reports, coursework, emails that matter |
| Refined | Analyze → Draft → Critique → Revise → Polish | Publication, submission, anything formal or public |

Auto-detection from the request:
- "快翻", "ざっくり", "quick", "直接翻译", "とりあえず" → quick
- "精翻", "丁寧に", "提出用", "publication", "proofread", "refined" → refined
- otherwise → normal

After normal mode, end with: "Translation saved. Reply **继续润色 / 推敲して / refine** to run critique and polish." If the user does, continue with refined Steps 4–6 on the existing output.

## Context Profiles

The context decides *how* to translate. Load the matching file from `references/contexts/` during analysis — only the ones needed.

| Context | File | Typical source | Core stance |
|---|---|---|---|
| `academic` | contexts/academic.md | Papers, theses, course reports, abstracts | Fidelity to argument and hedging; field-standard terms; だ・である |
| `business` | contexts/business.md | Business email, proposals, meeting notes | Relationship and politeness first; conventional formulas over literal wording |
| `technical` | contexts/technical.md | Docs, READMEs, specs, UI strings | Precision and consistency; keep code untouched; terse |
| `official` | contexts/official.md | Government, legal, notices, forms | Established official renderings; no paraphrase; flag ambiguity instead of resolving it |
| `literary` | contexts/literary.md | Fiction, essays, poetry, film dialogue | Voice, rhythm, implication; preserve what is left unsaid |
| `marketing` | contexts/marketing.md | Ads, product pages, slogans, SNS posts | Effect over wording; transcreation allowed; offer alternatives |
| `casual` | contexts/casual.md | Chat, LINE, social replies, personal messages | Natural spoken register; match the relationship |
| `subtitle` | contexts/subtitle.md | Subtitles, transcripts, slides, speech | Reading-speed limits; compress; spoken naturalness |

**Detection.** Judge from genre markers, register, layout, and stated purpose. Record the decision and the evidence in `01-analysis.md`. If two contexts are equally plausible and the choice changes the output (e.g., a report to a professor: `academic` vs. `business` keigo), ask once. Custom contexts are accepted: `--context "求職用エントリーシート"` → use the nearest profile as a base and record the adjustments.

**Mixed documents.** Assign contexts per section (e.g., body `academic`, quoted interview `casual`, cited statute `official`) and list them in the analysis.

## Workflow

### Step 1: Load Preferences

1.1 Load EXTEND.md (see Preferences).

1.2 Load glossaries and merge, later entries overriding earlier ones:
built-in `references/glossary-ja-en.md` → EXTEND.md `glossary_files` → EXTEND.md inline `glossary` → `--glossary` file.

### Step 2: Materialize Source & Output Directory

- File input: use as is. Inline text or URL: save to `translate/{slug}.md` first. For .docx/.pdf, convert to Markdown with available tools, keeping headings and footnotes.
- Detect source language unless `--from` given. If the source is mixed JA/EN, translate only the source-language portions and leave the rest unchanged.
- Create `{source-dir}/{source-basename}-{target-lang}/`.

Details: references/workflow-mechanics.md

| File | Mode | Content |
|---|---|---|
| `translation.md` | All | Final translation (always this name) |
| `01-analysis.md` | Normal, Refined | Context, audience, register, terms, challenges |
| `02-prompt.md` | Normal, Refined | Assembled translation brief |
| `03-draft.md` | Refined | First draft |
| `04-critique.md` | Refined | Diagnosis only — no rewriting |
| `05-revision.md` | Refined | Draft revised per critique |
| `chunks/` | Chunked | Source and translated chunks |

### Step 3: Measure Length

Run `chunk.py measure`. Japanese counts characters (kana + kanji + full-width); English counts words.

| Mode | Under threshold | Over threshold |
|---|---|---|
| Quick | Translate in one pass | Warn once that normal mode keeps terminology consistent; proceed unless the user switches |
| Normal / Refined | Single unit | Chunked (3.1) |

**3.1 Long content**
1. Extract terms across the whole document: proper nouns, people's names (with readings), institutions, recurring concepts, quoted titles.
2. Build a session glossary; merge with loaded glossaries. Decide name order (references/glossary-ja-en.md §Names) once for the whole document.
3. Split: `chunk.py split <file> --output-dir <out>/chunks`
4. Write `02-prompt.md` from Part 1 of references/subagent-prompt-template.md (context rules, register, glossary, challenges).
5. If an Agent/subagent tool exists, spawn one subagent per chunk in parallel using Part 2; each saves `chunks/chunk-NN-draft.md`. Otherwise translate chunks in order yourself, re-reading `02-prompt.md` before each.
6. Merge in `manifest.json` order (prepend `chunks/frontmatter.md` if present; rejoin chunks flagged `continues_previous_paragraph` without a paragraph break) → `03-draft.md` (refined) or `translation.md` (normal).
7. Run a consistency pass across chunk boundaries: same terms, same 文体, same name forms, no dangling connectives.

Subagents only draft. Critique, revision and polish stay with the main agent.

### Step 4: Analyze, Translate, Refine

**Universal principles (all modes, all contexts)**

- **Meaning before form.** Facts, numbers, logic, modality (certainty vs. hedging), and who-did-what must match the source exactly. Fluency never overrides this.
- **Translate to the context, not to a default voice.** The context profile wins over general "natural writing" instincts. An academic text that sounds like a blog post is a mistranslation.
- **Recover what Japanese leaves implicit, but never invent it.** When JA→EN requires a subject, agent, number, or tense the source does not state, choose from context; if the choice is genuinely uncertain, mark it in the analysis (normal) or critique (refined) — not in the translation body.
- **Don't import what English makes explicit.** EN→JA: drop pronouns, "you", and causal scaffolding that Japanese would leave unsaid, unless the context profile says otherwise.
- **Terminology.** One concept, one rendering, unless the source itself varies. First occurrence of a specialist term: follow the context's rule for showing the original.
- **Format.** Keep Markdown, links, images, code, tables, footnote markers. Apply references/style-guide-ja.md for Japanese output.
- **No added AI tone.** Do not introduce staged contrasts, closer lines, inflated significance, stock vocabulary, or decorative formatting that the source does not have (references/ai-tone.md). With `humanize: rewrite` (user request only; confirm first for academic, official, literary), also tone down such patterns already in the source, never changing facts, numbers, names, claims, or citations, and list every change.
- **Frontmatter.** Rename source metadata with a `source` prefix (`title`→`sourceTitle`, `url`→`sourceUrl`), add translated values as top-level fields (skip `title` if the body has an H1), keep other fields.

Direction checklists — load the one for the current direction:
- JA→EN: references/ja-to-en-pitfalls.md
- EN→JA: references/en-to-ja-pitfalls.md
- Keigo and register mapping (both directions): references/keigo-register.md
- AI-tone patterns for the target language: references/ai-tone.md

#### Quick
Detect context silently, translate, save `translation.md`. No analysis file. Apply the context profile's core stance and the universal principles, then scan the output once for AI-tone items 1–6 of the target language (references/ai-tone.md).

#### Normal
1. **Analyze** → `01-analysis.md`: direction; context(s) with evidence; audience; 文体 / keigo / English variant; terms and decisions; names; implicit elements that had to be resolved (subject, number, tense); cultural items; challenges.
2. **Brief** → `02-prompt.md`.
3. **Translate** → `translation.md`. Uncertain spots get a `<!-- TN: … -->` comment while drafting; before saving, remove them and carry the questions to "Please confirm" in the summary. Finish with one AI-tone scan of the output (references/ai-tone.md §Where it runs).

#### Refined
Steps and files: see references/refined-workflow.md.
1. Analyze → `01-analysis.md`
2. Brief → `02-prompt.md`
3. Draft → `03-draft.md`
4. Critique → `04-critique.md` (diagnosis only: accuracy, context fit, direction-specific pitfalls, register consistency, terminology, AI tone)
5. Revise → `05-revision.md`
6. Polish → `translation.md` (read as a native reader of the target in that context; final 表記 / style pass)

Each step reads the previous file.

### Step 5: Output

Final translation: `translation.md`. Then:

1. **Image text check.** List images likely containing source-language text (screenshots, charts, slides, covers). Reminder list only; never edit images unless asked.
2. **Open questions.** If the analysis or critique recorded unresolved assumptions (e.g., unstated subject, ambiguous referent, name readings), list at most five under "Please confirm".

Summary:

```
**Translation complete** ({mode} mode)

Source: {source-path}
Direction: {from} → {to}
Context: {context(s)} · Register: {文体 / keigo / variant}
Output: {output-dir}/translation.md
Glossary terms applied: {count}
```

## Extension

Everything is configurable through EXTEND.md — personal glossaries, default contexts, and per-context overrides (`context_overrides`). See references/config/extend-schema.md.
