# JA→EN Pitfalls

Checklist for analysis, drafting, and critique. Each item: what goes wrong, what to do.

## 1. Omitted subjects and objects

Japanese omits who and whom when context makes them clear. English requires them.

- Resolve from context: the speaker, the author, the company, "we", "people in general".
- Generic statements: 〜すると良い → "It helps to…" / "You should…" (not "One should" unless formal).
- If two readings change the meaning, pick the likelier one and log it in `01-analysis.md` → "Implicit elements resolved".
- Do not insert "I" into academic Japanese where the source avoids self-reference: 〜を検討する → "This paper examines…"

## 2. Topic は vs. subject が

「象は鼻が長い」 → "Elephants have long trunks", not "As for elephants, the nose is long". The は-topic often becomes the English subject; the が-noun becomes an object or modifier.

## 3. Number and definiteness

Japanese has no grammatical number or articles. Decide singular/plural and a/the from context. Common errors: "the students" when the source means students in general ("Students…"); singular "a problem" when 問題 refers to several issues.

## 4. Tense and aspect

- 〜ている: progressive ("is doing"), resultative ("has done / is done"), or habitual ("does"). 結婚している = "is married", not "is marrying".
- た can be completion, not past: 着いたら連絡して = "Let me know when you arrive".
- Narrative mixing of た/る in Japanese → keep a consistent English tense.

## 5. Implicit logic

Japanese often juxtaposes clauses (〜し、〜て、〜が) where English needs explicit relations. Choose the connective from the logic:

| Japanese | Possible relations |
|---|---|
| 〜が、 | contrast ("but") OR mere linking ("and") — check which |
| 〜て、 | sequence, cause, manner |
| 〜ので / 〜から | cause; ので is softer |
| 〜ため | purpose OR cause — check |

Never add "however" where the source only links.

## 6. Long modifiers before nouns

連体修飾 can be very long: 「昨年度から市が実施している外国人住民向けの日本語教室」. English: put the noun first and modifiers after: "the Japanese classes for foreign residents that the city has run since last fiscal year".

## 7. Politeness and keigo

Keigo is not translated as words but as tone. See keigo-register.md. Do not add "humbly" or "respectfully" for 謙譲語.

## 8. Vagueness and hedging stacking

Japanese stacks softeners: 〜ではないかと思われる場合もあるかもしれない. Decide the actual strength and render it once: "may sometimes be the case". In academic context keep the strength exactly (see academic.md).

## 9. Katakana loanwords (和製英語)

Do not back-translate katakana as the English word it resembles.

| Katakana | Means | Not |
|---|---|---|
| マンション | apartment / condo | mansion |
| クレーム | complaint | claim |
| サラリーマン | office worker | salary man |
| スマート | slim | smart |
| テンション | energy / excitement | tension |
| ノートパソコン | laptop | note PC |
| アルバイト | part-time job | arbeit |
| コンセント | outlet / socket | consent |
| ナイーブ | sensitive | naive |
| リフォーム | renovation | reform |

## 10. Onomatopoeia and mimetics

Fold into verbs/adjectives: ペラペラ話す → "speaks fluently"; イライラする → "gets irritated"; ドキドキ → "my heart raced".

## 11. Culture-bound terms

- Institutions with official English: use them (see official.md).
- Concepts without equivalents (先輩/後輩, 世間, 空気を読む, お疲れ様): describe the function ("senior student", "read the room"), or keep romanized with a gloss in academic/literary contexts.
- Food, places, festivals: keep the Japanese name in italics or as a proper noun, add minimal description on first use if needed.

## 12. Names

- Japanese people: order per EXTEND.md `name_order_ja_people` (default family-first: "Yamada Masaru"). Apply consistently.
- Readings of kanji names are often uncertain. Never guess silently: if no reading is given, use the most common reading and list it under "Please confirm".
- Macrons: Ōsaka/Tōkyō only if the user wants Hepburn with macrons; standard practice for well-known places is Osaka, Tokyo.

## 13. Numbers and units

万 = 10,000: 3万人 → 30,000 people; 1億 → 100 million. 年度 → "fiscal year" or "academic year" depending on context. Keep yen as ¥ or "yen".

## 14. Punctuation

「」 → " "; 『』 → italics for titles, or nested quotes; 、 → comma only where English grammar needs it; ・ → "and" / slash / comma as appropriate; …… → "…".
