# First-Time Setup

Run when no EXTEND.md is found. Ask everything in ONE call, then write the file.

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

Then continue the original translation request.

## No user present

Do not write EXTEND.md. Use SKILL.md defaults, and add one line at the top of `01-analysis.md`: "No EXTEND.md found; defaults used."
