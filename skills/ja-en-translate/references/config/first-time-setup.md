# First-Time Setup

Run when no EXTEND.md is found, **after** the first translation has been delivered, never before it. The user came to translate; setup must not stand in the way.

Offer it in one line at the end of that reply, in the user's language, for example: "要把这次的设置保存为默认吗？只需回答 4 个问题。" If the user agrees, ask everything in ONE call, then write the file. If they decline or ignore it, do not offer again in the same session.

Pre-fill the recommended answers from what the first request showed (e.g., if it was an academic EN→JA translation, mark Academic as recommended).

## Questions

1. **Main direction**
   - Auto by source language (Recommended)
   - Mostly Japanese → English
   - Mostly English → Japanese

2. **Default mode**
   - Normal: analyze then translate (Recommended)
   - Quick: translate directly
   - Refined: full critique and polish every time

3. **What do you translate most?** (multi-select allowed; becomes `default_context` if exactly one is picked, otherwise `auto`)
   - Academic (papers, course reports)
   - Business (email, documents)
   - Technical (docs, code, UI)
   - Mixed / let the skill decide

4. **Save location**
   - User-level `~/.ja-en-translate/EXTEND.md` (Recommended)
   - Project-level `.ja-en-translate/EXTEND.md`

## After answers

Write EXTEND.md with the answers plus defaults for every other key (copy the schema block, then set answered keys). Leave `glossary: []` and `glossary_files: []` empty, with a comment pointing to extend-schema.md.

Confirm: "Preferences saved to [path]. Add your own terms under `glossary:` to keep them consistent across translations."

No translation is pending at this point; simply confirm and stop.

## No user present

Do not write EXTEND.md. Use SKILL.md defaults, and add one line at the top of `01-analysis.md`: "No EXTEND.md found; defaults used."
