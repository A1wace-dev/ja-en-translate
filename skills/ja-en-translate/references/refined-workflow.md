# Refined Workflow

Six steps; each writes one file and reads the previous one.

## 1. Analyze → `01-analysis.md`

```markdown
# Analysis

## Basics
- Direction: JA → EN
- Source genre and purpose:
- Context(s): academic (body), casual (quoted interview §3) — evidence: …
- Audience:
- Register: 文体 / keigo / English variant
- Notes policy:

## Terminology decisions
| Source | Rendering | Reason / source |

## Names
| Source | Rendering | Reading confirmed? |

## Implicit elements resolved
| Location | Source | Resolved as | Confidence |

## Cultural items
| Item | Strategy (keep / gloss / substitute / explain) |

## Translation challenges
- …

## Assumptions (if no user present)
```

## 2. Brief → `02-prompt.md`

Use Part 1 of subagent-prompt-template.md. Inline the context profile's rules that matter for this text (not the whole file), the merged glossary, register decisions, and challenges.

## 3. Draft → `03-draft.md`

Translate following the brief. Translator's notes per the notes policy. If something is uncertain, keep the best reading in the text and record the question in a `<!-- TN: … -->` HTML comment; comments are removed at polish.

## 4. Critique → `04-critique.md`

First run `scripts/fidelity_check.py <source> 03-draft.md` and `scripts/tone_lint.py 03-draft.md --context <context>`. Every high fidelity finding goes into section A (as an error, or with the reason it is fine); lint findings feed section G.

**Diagnosis only. Do not rewrite here.** Compare draft against source sentence by sentence. Use these sections; cite location and quote the problem briefly.

```markdown
# Critique

## A. Accuracy
Omissions, additions, mistranslations, numbers, names. Then, per references/meaning-checks.md: sentence types that changed (hearsay → assertion, opinion → fact, request → description), six-point test failures on restructured sentences, and any shift in the modality strength table (critical in `technical` and `official`).

## B. Context fit
Does it read as the declared context (academic / business / …)? Violations of that context's rules.

## C. Direction-specific pitfalls
JA→EN: ja-to-en-pitfalls.md items (subjects, number, tense, logic, 和製英語, hedging).
EN→JA: en-to-ja-pitfalls.md items (pronouns, 無生物主語, passive, の連続, 翻訳調, 文体 mixing).

## D. Register and keigo
Consistency; keigo errors from keigo-register.md.

## E. Terminology and 表記
Glossary adherence; 表記ゆれ; style-guide-ja.md.

## F. Readability
Sentences a native reader of this context would stumble on.

## G. AI tone
Per references/ai-tone.md, including the never-inject list (anything the draft *added* to sound natural: an "I", a dramatic dash, fragments, an invented example), for the target language. For each instance: location, the phrase, the matching source sentence, and a verdict: *added by translation* (fix) or *present in source* (keep under `guard`; rewrite under `rewrite`, and say what changes).

## Priority
List the five most important fixes first.
```

Severity tags: **[critical]** meaning error, **[major]** context/register error, **[minor]** style.

## 5. Revise → `05-revision.md`

Apply every critical and major item; apply minor items unless they conflict with the context profile. At the bottom, a short changelog: which critique items were not applied and why.

## 6. Polish → `translation.md`

Read the revision **without the source**, as a native reader in that context. Smooth rhythm and transitions; final 表記 pass; last AI-tone scan (items 1–6 of the target-language list); remove `<!-- TN -->` comments (move unresolved ones to "Please confirm" in the summary). Do not change meaning at this step — if a meaning problem appears, go back and fix it in `05-revision.md` first.
