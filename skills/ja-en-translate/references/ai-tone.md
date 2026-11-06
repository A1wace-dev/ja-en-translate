# AI Tone in Translation

Machine translation by language models has a recognizable voice: inflated significance, staged contrasts, stock vocabulary, and decorative formatting. This file lists those patterns for English and Japanese output and says what to do about them **without breaking fidelity to the source**.

Idea source: Wikipedia, ["Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) (WikiProject AI Cleanup). The lists below are written for this skill and adapted to translation; the Japanese list is original.

## The rule that comes first

A translator does not edit the author. So there are two different jobs:

| Setting | Job | What may change |
|---|---|---|
| `humanize: guard` (default) | **Do not add** AI tone the source does not have | Only the translator's own word choices |
| `humanize: rewrite` | Also reduce AI tone that is **already in the source** | Wording and structure of AI-tone passages; never facts, numbers, names, claims, or citations |
| `humanize: off` | No AI-tone check | — |

`guard` applies in every context. `rewrite` is allowed only when the user asks for it (`--humanize rewrite`, or "去掉AI味", "AIっぽさを消して", "make it sound less AI") and is refused for `academic`, `official`, and `literary` contexts unless the user confirms, because there the author's wording is the content. When `rewrite` changes something the source says, list each change in `04-critique.md` (refined) or in the summary (normal).

**Test for guard:** for each flagged pattern in the translation, look at the matching source sentence. If the source has the same move (a real contrast, a real emphasis, a list of three real items), it stays. If the translator added it, remove it.

## English output: patterns to watch

Strongest first. One sighting of 1–6 justifies a fix; the rest need several in the same passage.

1. **Staged contrast.** "not X but Y", "not just X — it's Y", "This doesn't mean X. It means Y." Japanese 〜ではなく〜 often triggers it in JA→EN. Keep a contrast only if the source makes one and both halves carry information.
2. **Closer lines.** A short final sentence that repeats the paragraph ("That's what matters."), or a line that interprets an example the reader just saw. Japanese paragraphs ending in 〜のである / 〜と言えよう tempt translators into this; translate the claim, not a flourish.
3. **Inflated significance.** pivotal, crucial, plays a key role, a testament to, marks a turning point, reflects a broader trend, enduring legacy. Japanese 重要な / 大きな意味を持つ / 象徴する are often weaker than these; match the source's actual strength.
4. **Stock vocabulary.** delve, tapestry, landscape (figurative), underscore, showcase, foster, robust (figurative), seamless, vibrant, meticulous, additionally. Use plain words unless the source is itself ornate.
5. **Shallow -ing riders.** ", highlighting…", ", reflecting…", ", underscoring…" attached to a fact. Japanese 〜しており、〜を示している chains invite this; split into sentences with real verbs.
6. **Chatbot residue.** "Here is the translation:", "I hope this helps", notes to the reader inside `translation.md`. Never allowed.
7. **Forced triads.** Lists of three that the source does not have.
8. **Dashes.** Em dashes as an all-purpose connector. Japanese ―― may map to a dash; elsewhere use commas, colons, parentheses, or new sentences. In `guard`, do not add dashes the source does not motivate.
9. **Avoiding is/has.** "serves as", "stands as", "boasts", "features" for 〜である / 〜がある.
10. **Stacked hedges.** "could potentially", "may arguably". Map the source's hedge once (see academic.md).
11. **Decoration.** Bold on every list label, Title Case headings, emoji. Follow the source's formatting; do not add bold.

## Japanese output: patterns to watch

LLM-generated Japanese has its own voice. Strongest first.

1. **単なる〜ではなく / 〜だけでなく〜も (staged contrast).** Often produced from English "not just X but Y". Keep only when the source contrast is real; otherwise state the positive claim.
2. **締めの一文.** 「これこそが〜なのです。」「〜と言えるでしょう。」「〜ではないでしょうか。」 added at paragraph ends. Do not add; if the source ends with a flat statement, end flat.
3. **大げさな意義づけ.** 重要な役割を果たす, 欠かせない存在, 大きな転換点, 〜の鍵を握る, 新たな可能性を切り拓く, 〜の象徴と言える. Use the plain claim the source makes.
4. **定番語の多用.** さまざまな, 多様な, 〜において, 〜を通じて, 〜に関して, 包括的な, シームレスな, 革新的な, 重要です, 大切です, 〜することが求められます. Each is normal alone; the tell is density.
5. **チャットの残り.** 「以下に翻訳を示します」「いかがでしたか？」「お役に立てれば幸いです」「ぜひ参考にしてください」. Never allowed in `translation.md`.
6. **体言止めの連発.** Three or more noun-ending sentences in prose, used for rhythm the source does not have. Fine in headings, slides, and marketing copy.
7. **ダッシュ「——」と「：」の多用.** Often a calque of English em dashes and colons. Use 、 or split sentences.
8. **三点セット.** 〜、〜、そして〜 lists that the source does not have.
9. **〜することができます / 〜となっています / 〜を行います.** Also translationese; see en-to-ja-pitfalls.md §5.
10. **見出しの飾り.** 【】 or emoji on every heading, bold on every list label. Follow the source.

## Where it runs

- **Draft (all modes):** write without these patterns; the brief (`02-prompt.md`) lists the ones most likely for this text.
- **Script:** `scripts/tone_lint.py` lists candidates for both languages. It is a first pass, not a verdict; triage every finding against the source.
- **Critique (refined):** section G "AI tone" in `04-critique.md`: each flagged instance with its source sentence and a verdict, *added by translation* (fix) or *present in source* (keep in `guard`; rewrite in `rewrite`).
- **Polish (refined) / final check (normal):** one last scan of the output for items 1–6 of the target language's list.

## When not to act

- Inside quotations, titles, proper names, and terms of art (a "robust estimator" in statistics is not AI tone).
- When the source author really writes this way. In `guard`, a faithful translation of an ornate author stays ornate.
- Letters: salutations and sign-offs (よろしくお願いいたします, Best regards) are conventions, not chatbot residue.
- Marketing copy legitimately uses emphasis and 体言止め; judge by the marketing profile, not this list alone.
