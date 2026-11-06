# Japanese Output Style Guide (表記)

Apply to all Japanese output unless the context profile or EXTEND.md says otherwise. Based on common practice (JTF 日本語標準スタイルガイド, 公用文作成の考え方 2022) — when a document already has a house style, follow the document.

## Characters and width

- Japanese text, punctuation, and brackets: full-width (、。「」（）？！).
- Alphanumerics: half-width (ABC, 123). Never full-width digits except in vertical text.
- Katakana: always full-width (ｶﾀｶﾅ ✗).
- Spaces between Japanese and alphanumerics: either way is acceptable; follow the source document or EXTEND.md. Default: no space in prose, space allowed in technical docs.

## Punctuation

| Element | Rule |
|---|---|
| Comma / period | 、。 (or ，。 if `ja_punctuation` says so) |
| Quotation | 「」; nested 『』 |
| Book / film / journal titles | 『』 |
| Article / chapter / song titles | 「」 |
| Parentheses | （） full-width around Japanese; (half-width) acceptable around pure alphanumerics in technical text |
| Ellipsis | …… (two 3-dot leaders) |
| Dash | ―― (two em-dash-like characters) or remove |
| ! ? | Avoid in academic/official text; full-width ！？ elsewhere, followed by a full-width space mid-paragraph |
| Middle dot | ・ for katakana name separation and parallel lists |

## Numbers

- Horizontal text: Arabic numerals (2026年, 3人).
- Kanji numerals for fixed expressions: 一つ, 一般, 一部, 三権分立, 四季.
- Large numbers in prose: 3万人, 1億2000万円. Tables: 30,000.
- Dates: 2026年11月6日. Era names only when the source uses them or in official forms.

## 表記ゆれ (consistency)

Pick one per document and record in the analysis:

- ユーザー / ユーザ, サーバー / サーバ (default: with ー, per current JIS/Microsoft practice)
- 下さい (verb) vs. ください (auxiliary): 〜してください (hiragana as auxiliary)
- 事 / こと, 時 / とき, 物 / もの as formal nouns → hiragana (公用文ルール)
- 出来る → できる; 有る → ある; 為 → ため (in most contexts)
- 子供 / 子ども: follow the source field (子ども is standard in education/child-rights writing)

## Commas (読点)

- Do not put a comma after a short topic, subject, or object only to make a pause: 本稿は地域の教室を扱う (not 本稿は、地域の…), 資料を全員に配る. Keep it when it marks a scene frame (会議では、担当者が…), a change of actor, a long subject or clause, a list, or prevents misreading.
- `tone_lint.py` flags candidates as `ja-pause-comma`; decide each in context.

## Colons

Do not end a sentence with ： before a list, code block, or table (設定は次のとおりです：). End it with 。 (設定は次のとおりです。) or use a noun label. Label–value pairs (日時：10時) are fine.

## Bold in Markdown

CommonMark (GitHub, most renderers) does not render `**` when it touches a letter on one side and a bracket or 。 on the other: `次に**「立場」**を決める` shows the asterisks. In order of preference:
1. Bold inside the brackets: `次に「**立場**」を決める`
2. Move 。 outside: `これは**必須です**。`
3. Otherwise add a half-width space outside the `**`.

## Headings and lists

- Headings: 体言止め, no 。
- List items: either all 体言止め or all full sentences; full sentences end with 。
- Table cells: no 。 unless multiple sentences
