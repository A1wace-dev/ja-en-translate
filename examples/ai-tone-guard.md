# AI-tone guard

With the default `humanize: guard`, the skill must not add the stock voice of machine-written text. The left column shows the kind of output a language model often produces without the guard. These examples were written for this repository.

## JA → EN

**Source**

> 地域の日本語教室は、外国人住民にとって言葉を学ぶ場であると同時に、近所の人と知り合う場でもある。

| Unguarded (typical) | Guarded |
|---|---|
| Community Japanese classes are not just places to learn a language — they play a crucial role in fostering meaningful connections with neighbors, serving as a vibrant hub of community life. | For foreign residents, community Japanese classes are a place to learn the language and also a place to meet people from the neighborhood. |

What the critique step (section G) records:

| Phrase | Source | Verdict |
|---|---|---|
| "not just … —" | 〜であると同時に (both/and, no contrast) | added by translation: fix |
| "crucial role", "fostering", "vibrant hub" | none | added by translation: fix |
| "serving as" | none | added by translation: fix |

## EN → JA

**Source**

> The library extended its opening hours on weekdays.

| Unguarded (typical) | Guarded |
|---|---|
| 図書館は平日の開館時間を延長しました。これは、地域住民の学びを支えるうえで重要な一歩と言えるでしょう。 | 図書館は平日の開館時間を延長しました。 |

The second sentence of the unguarded version is a 締めの一文 that the source never wrote. The guard removes it; it is not the translator's job to interpret the news.

## When the source itself has AI tone

**Source** (a press release that already reads like this)

> 本プロジェクトは、単なる翻訳支援ではなく、多文化共生社会の実現に向けた重要な一歩です。

- `guard` (default): translate faithfully. "This project is more than a translation aid: it is an important step toward a society where people of different cultures live together." The contrast and the claim of importance are the author's.
- `rewrite` (user asked to reduce AI tone): "This project supports translation and is meant to help people of different cultures live together." The summary lists the change: *"単なる〜ではなく contrast and 重要な一歩 removed at user request; no facts changed."*
