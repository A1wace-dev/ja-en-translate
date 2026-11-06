# Calibration

How often do `tone_lint.py` and `fidelity_check.py` fire on text that a person wrote and translated? If a rule fires constantly on human work, it is noise, not a signal.

## Corpus

The Japanese translation of the Python documentation ([python/python-docs-ja](https://github.com/python/python-docs-ja), branch `3.8`, translated mostly before 2022 by volunteers). Each `.po` file gives aligned English source and Japanese translation. No corpus text is stored in this repository.

```bash
git clone --depth 1 --branch 3.8 https://github.com/python/python-docs-ja py38
python3 tools/calibration/extract_po.py py38 /tmp/calib-docs
python3 tools/calibration/measure.py /tmp/calib-docs technical
python3 tools/calibration/paragraph_rates.py /tmp/calib-docs
```

This corpus is technical documentation only. It says nothing about false-positive rates for literary, business, or casual text.

## Results (2026-11-06, 332 documents, 2.5M Japanese characters, 25,062 aligned paragraphs)

### tone_lint, context `technical`

| | Japanese (human translation) | English (human source) |
|---|---|---|
| Median score | 97 | 100 |
| 10th percentile | 93 | 100 |

AI-tone rules almost never fire on human text: `ja-closer` 5 times, `ja-inflated` 2, `en-staged-contrast` 9, in the whole corpus. The rules that fire most are ones that human translators also produce and that are worth fixing in new translations: `ja-long-sentence` (0.54 per 1,000 characters) and `ja-dekiru` 〜ことができる (0.54).

### fidelity_check, English source → human Japanese translation

| Finding | Rate |
|---|---|
| Numbers missing from a paragraph (high) | 0.25% of paragraphs |
| Negation in source, none in output (medium) | 1.24% of paragraphs |
| Negation added (low) | 2.68% of paragraphs |

Sampled high-severity number findings were mostly real deviations in the human translation, for example "higher than 255" rendered as 「256よりも大きな」, and "2-tuple" losing the 2.

## End-to-end trial

A normal-mode run of SKILL.md on two texts written for the purpose (an academic JA paragraph with hearsay, 万 numbers, a quoted request, and a limitation; an EN email to a professor) found four more problems, all fixed: number words ("two classes" for 2つの教室) were reported as missing numbers; 「重要な役割を果たす」 was not matched; "one-week" → 「2週間」 was only medium; and a lost negation ("have not finished" → 「終わりました」) was missed because the email's paragraphs did not align. `tone_lint.py --source` was added so that a contrast the source itself makes is not reported as added AI tone.

## Changes made from this calibration

- `ja-no-chain` now needs four の in a row; three is common in good human prose (1,482 → 168 hits).
- `ja-halfwidth-punct` is relaxed in `technical`; half-width `:` before examples is a house style in many Japanese technical documents.
- `en-chat-residue` no longer includes "feel free to" and "let me know if", which people write.
- Negation ignores obligation (〜なければならない), possibility (〜かもしれない), and rhetorical forms; in the output it also accepts conditional and lexical negation (〜なければ, 未知, 以外) as expressing a source "not". Lost-negation hits fell from 3,995 to 312 paragraphs. Contrastive "not A but B" (〜ではなく, not only) no longer counts as predicate negation, so an added contrast cannot hide a lost negation; comparatives (fewer than, 未満) count as expressing negation in the output.
- Numbers: a value missing entirely is high; the same value mentioned a different number of times (often replaced by それ) is low. English number words satisfy digits on the other side (2つの教室 → "two classes", "three" → 3回) but are never required.
- When paragraphs do not align (letters and emails gain or lose greeting paragraphs), negation is compared for the whole document instead of being skipped.
- "one" before a unit (one-week) and 一 before a counter (一週間) are counted as numbers.
- URLs no longer swallow trailing punctuation; inline code is compared as a set, and only identifier-like spans (no spaces, no Japanese) are required verbatim.
