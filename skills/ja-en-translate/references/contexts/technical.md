# Context: technical

Documentation, READMEs, API references, specs, release notes, UI strings, error messages, technical blog posts.

## Defaults

| Setting | Value |
|---|---|
| Japanese style | です・ます for docs and tutorials; だ・である or 体言止め for specs, tables, changelogs |
| Keigo | `teinei` |
| English | Plain, imperative for instructions ("Run…", "Set…"); present tense |
| Notes | `inline`, only when a term would block understanding |
| Restructuring | Low. Accuracy and consistency over elegance |

## Modality is the specification

In specs, READMEs, and API docs, 〜してよい (may), 〜できる (can), 〜しなければならない (must), 任意 (optional), 必ず (always), and 〜場合がある (may sometimes) define behavior. Map them with the table in references/meaning-checks.md; any shift is a critical error.

## Never translate

- Code blocks, inline code, commands, file paths, environment variables, URLs, config keys
- Identifiers inside prose: `chunk_threshold` stays as is
- Product and library names (Claude Code, Ollama, PyTorch)
- Error message strings that users will search for — keep the original and add a translation in parentheses if helpful

## Terminology

- Prefer the term used in the official localized docs of the ecosystem (Microsoft, Apple, Google, MDN Japanese).
- Keep widely used katakana/English terms: API, SDK, CLI, デプロイ, コミット, リポジトリ.
- One concept, one term, document-wide. Record choices in the analysis.

| English | Japanese (preferred) | Avoid |
|---|---|---|
| deploy | デプロイ | 展開 (ambiguous) |
| repository | リポジトリ | 貯蔵庫 |
| issue (GitHub) | Issue / イシュー | 問題 |
| pull request | プルリクエスト / PR | |
| default | デフォルト / 既定 (Microsoft style) | pick one |
| user | ユーザー (with ー, per JIS Z 8301 / Microsoft) | ユーザ (choose one per document) |
| optional | 任意 / オプション | |
| deprecated | 非推奨 | |

## JA→EN

- Japanese docs often omit the actor ("〜を設定します"): English instructions use the imperative ("Set …").
- 〜してください → imperative, not "please do" every time.
- 〜できます → "You can …" or rephrase to imperative when it is actually an instruction.
- Keep sentences short; one action per step.

## EN→JA

- Imperative steps → 〜します (description) or 〜してください (instruction); keep consistent across a list.
- Do not translate "you" (あなたは ✗).
- UI labels: follow the actual localized UI if it exists; otherwise translate and keep the English label in parentheses: 「設定（Settings）」.
- Half-width space between Japanese and alphanumerics is a style choice — follow the document's existing practice (see style-guide-ja.md).

## UI strings

- Respect length limits; if the target is longer than ~130% of source, offer a shorter alternative.
- Keep placeholders exactly: `{count}`, `%s`, `{{name}}`. Reordering placeholders is allowed only if the format supports it.
- Japanese buttons: verb stem or noun (保存, キャンセル); not 保存してください.

## Critique focus

- Is every code element untouched?
- Is terminology identical across the document?
- Can the reader execute each step without ambiguity?
