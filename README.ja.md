# ja-en-translate

[English](README.md) | 日本語 | [中文](README.zh.md)

日英・英日翻訳のためのエージェント用スキルです。翻訳の前に、**どんな文章を、誰に向けて訳すのか**を判断します。Claude Code、Codex など、`SKILL.md` を読み込めるエージェントで使えます。

ビジネスメール、授業のレポート、LINE のメッセージ、字幕ファイルでは、求められる日本語も英語も違います。このスキルは文章（または節ごと）に「文脈プロファイル」を割り当て、文体・敬語・構成の変え方・訳注の扱いをそのルールに従って決めます。さらに、翻訳の方向ごとに起きやすい誤りと、原文にないAIっぽい言い回しが混ざっていないかを点検します。

## 特徴

- **8つの文脈プロファイル**：`academic`（論文・レポート）、`business`（ビジネス・教員宛てメール）、`technical`（技術文書）、`official`（法令・行政手続き）、`literary`（文芸・随筆）、`marketing`（広告・SNS）、`casual`（チャット）、`subtitle`（字幕・スライド）。自動判定し、根拠を記録します。
- **3つのモード**：`quick`（すぐ訳す）、`normal`（分析してから訳す）、`refined`（分析→下訳→批評→修正→仕上げ）。各ステップはファイルとして残ります。
- **方向別のチェック**：日→英では主語の省略、単複、時制、暗黙の論理関係、和製英語、ぼかし表現の強さ。英→日では翻訳調（代名詞の多用、無生物主語、「の」の連続、「〜することができる」、文体の混在）と、二重敬語などの敬語の誤り。
- **AI調ガード**：「単なる〜ではなく」「〜と言えるでしょう」「重要な役割を果たす」など、原文にない決まり文句を訳文に持ち込みません。依頼があれば（`--humanize rewrite`）原文自体のAI調も抑え、変更点をすべて報告します。
- **推測で埋めない**：原文が明示していない主語や人名の読みは文脈から判断し、「Please confirm」として確認を求めます。
- **長文対応**：日本語は文字数、英語は語数で長さを測り、Markdown のブロック単位で分割して、共通の用語集と指示書のもとで並行翻訳します。
- **カスタマイズ**：用語集や既定の文脈を `EXTEND.md` で設定できます。必要なのは Python 3.10 以上だけです。

例：[examples/context-switching.md](examples/context-switching.md)、[examples/ai-tone-guard.md](examples/ai-tone-guard.md)

## インストール

```bash
npx skills add A1wace-dev/ja-en-translate --agent claude-code   # 他のエージェントは skills CLI のドキュメント参照
```

手動の場合：

```bash
git clone https://github.com/A1wace-dev/ja-en-translate.git
cp -R ja-en-translate/skills/ja-en-translate ~/.claude/skills/   # Claude Code
cp -R ja-en-translate/skills/ja-en-translate ~/.codex/skills/    # Codex
```

## 使い方

```text
report.md を英訳して
精翻 abstract.md --context academic
ざっくり訳して：The meeting has been moved to 3 p.m. tomorrow.
この英文メールを日本語にして。取引先の部長宛てです
lecture.srt を日本語字幕にして --context subtitle
```

`normal` モードの後に「推敲して」と返すと、同じ訳文に批評と仕上げをかけます。

## 注意

- ルールは言語モデルへの指針であり、正確さを保証するものではありません。法的・学術的に重要な文書は必ずご自身で確認してください。公的文書は日本語の原文が正本です。
- 内蔵の用語集は最小限です。専門用語はご自身の `EXTEND.md` に追加してください。

## 謝辞・ライセンス

ワークフローの設計は [baoyu-translate](https://github.com/JimLiu/baoyu-skills)（MIT）を参考にしています（文章・コードの流用はありません）。英語のAI調リストは Wikipedia「Signs of AI writing」の考え方を翻訳向けに書き直したもので、日本語のリストは独自に作成しました。

[MIT License](LICENSE)
