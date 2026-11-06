# Context: subtitle

Subtitles (SRT/VTT), transcripts, speech scripts, presentation slides and speaker notes, interpreting prep.

## Defaults

| Setting | Value |
|---|---|
| Japanese style | Spoken; です・ます or plain by speaker |
| Keigo | Reproduce the speaker's level |
| English | Spoken, contractions |
| Notes | `none` |
| Restructuring | High: compression is the norm |

## Length and reading-speed limits

Default: the Netflix Timed Text Style Guides (Japanese; English USA). If the user names another platform or spec, follow that instead.

| Target | Per line | Lines | Reading speed (adult) | Reading speed (children) |
|---|---|---|---|---|
| Japanese subtitles | 13 full-width characters (horizontal); 11 (vertical) | 2 | 4 characters/second | — |
| Japanese SDH (closed captions) | 16 full-width characters | 2 | 7 characters/second | — |
| English | 42 characters | 2 | 20 characters/second | 17 characters/second |

Japanese counting: a full-width character, space, or punctuation mark counts as 1; a half-width one counts as 0.5. Japanese at 4 characters/second is very tight — expect heavy compression.

## Rules

- **Never change timestamps or cue numbers** in SRT/VTT. Translate text only; one cue in → one cue out.
- Compress: drop fillers (えーと, あの, you know, like), repetitions, and redundant addressing, unless they carry character or meaning.
- Line breaks at natural syntactic boundaries; never split a name or a particle from its noun.
- Japanese subtitles: no 「。」 or 「、」. Replace 、 with a half-width space and a sentence-ending 。 with a full-width space (exception: official titles that contain punctuation). Use full-width ？！, followed by a full-width space when another sentence follows on the same line.
- On-screen text (signs, captions) only if the user asks; mark as [sign: …].
- Slides: keep bullet parallelism; noun phrases in Japanese (体言止め) and English (fragments).
- Speech scripts: optimize for being said aloud — shorter sentences, natural pauses.

## Critique focus

- Within length limits?
- Cue count and timestamps identical?
- Readable at speed — could a viewer take it in at a glance?
