# ja-en-translate

[English](README.md) | 日本語 | [中文](README.zh.md)

日英・英日翻訳と、日本語の推敲のためのエージェント用スキルです。訳し始める前に、**どんな種類の文章を、誰に向けて訳すのか**を判断します。Claude Code や Codex など、`SKILL.md` を読み込めるエージェントで利用できます。

ビジネスメール、授業のレポート、LINE のメッセージ、字幕ファイルでは、ふさわしい日本語も英語もそれぞれ異なります。このスキルは文章全体、または節ごとに「文脈プロファイル」を割り当て、その規則に従って文体、敬語のレベル、文の組み替えの度合い、訳注の有無を決めます。訳し終えたあとは、翻訳の方向ごとに起きやすい誤りがないか、原文にはないAIっぽい言い回しが紛れ込んでいないかを点検します。

## 特徴

- **8つの文脈プロファイル**：`academic`（論文・レポート）、`business`（ビジネス・教員宛てメール）、`technical`（技術文書）、`official`（法令・行政手続き）、`literary`（文芸・随筆）、`marketing`（広告・SNS）、`casual`（チャット）、`subtitle`（字幕・スライド）。自動で判定し、その根拠を記録します。一つの文書の中で、節ごとに使い分けることもできます。
- **3つのモード**：`quick`（すぐ訳す）、`normal`（分析してから訳す）、`refined`（分析→下訳→批評→修正→仕上げ）。各ステップはファイルとして残ります。
- **方向別のチェック**：日→英では主語の省略、単数・複数、時制、明示されていない論理関係、和製英語、断定の強さ（ヘッジ表現）を確認します。英→日では翻訳調（代名詞の多用、無生物主語、「の」の連続、「〜することができる」、文体の混在）や、二重敬語などの敬語の誤りを確認します。
- **AIっぽさの防止**：「単なる〜ではなく」「〜と言えるでしょう」「重要な役割を果たす」など、原文にない決まり文句を訳文に持ち込みません。指定すれば（`--humanize rewrite`）原文にもともとあるAIっぽい表現も和らげ、変更箇所をすべて報告します。
- **チェックはコード、判断はモデル**：`tone_lint.py` が日本語・英語のAIっぽい表現や翻訳調の候補を挙げ、`fidelity_check.py` が原文と訳文の数値（3万＝30,000、1億2000万＝120 million）、否定、リンク、コード、構成を照合します。指摘は機械的に直さず、文脈を見て一つずつ判断します。
- **日本語の推敲**：AIが書いたような日本語や翻訳調の日本語を渡して「自然にして」と頼むと、同じ文脈プロファイルとチェックを使って書き直します。内容は変えず、すでに自然な文には手を入れず、意味が曖昧な箇所は推測で埋めずに確認を求めます。
- **推測は必ず報告**：原文に書かれていない主語や、人名の読み方などは文脈から判断し、その判断を「Please confirm」の欄に挙げて確認を求めます。
- **長文対応**：日本語は文字数、英語は語数で長さを測ります。長い文章は Markdown のブロック単位で分割し、すべての部分を同じ用語集と指示書に基づいて並行翻訳します。
- **カスタマイズ可能**：独自の用語集や既定の文脈は `EXTEND.md` で設定できます。動作に必要なのは Python 3.10 以上のみです。

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

Claude アプリでは、`skills/ja-en-translate` フォルダを zip に圧縮し、設定の Skills の項目からアップロードしてください。

## 使い方

```text
report.md を英訳して
abstract.md を提出用に丁寧に英訳して --context academic
ざっくり訳して：The meeting has been moved to 3 p.m. tomorrow.
この英文メールを日本語にして。取引先の部長宛てです
lecture.srt を日本語字幕にして --context subtitle
この文章、AIっぽいので自然な日本語にして（社内報告書）
```

パラメータは不要です。「先生に送るメール」「ざっくりでいい」「論文に載せる」のように、用途を日本語・英語・中国語で書けば、文脈、敬語のレベル、モードをそこから読み取ります。返信の冒頭には読み取った設定が一行で表示されるので、違っていればすぐに訂正できます。

`normal` モードで訳し終えたあとに「推敲して」と返信すると、同じ訳文に対して批評と仕上げを行います。

## 注意

- 各ルールは言語モデルに向けた指針であり、訳文の正確さを保証するものではありません。法律、学術、金銭に関わる文書は、必ずご自身でも確認してください。公的文書については、日本語の原文が正式なものです。
- 内蔵の用語集は最小限のものです。ご自身の分野の専門用語は `EXTEND.md` に追加してください。

## 謝辞・ライセンス

ワークフローは [baoyu-translate](https://github.com/JimLiu/baoyu-skills)（MIT ライセンス）の設計を参考にしています。文章やコードは流用していません。日本語のチェックは [yomiyasu](https://github.com/nanaism/yomiyasu)（書き換え前後の数値・否定の照合）、[natural-japanese](https://github.com/coji/natural-japanese)（lint が候補を挙げ、モデルが判断する分担）、[stop-ai-slop-jp](https://github.com/iKora128/stop-ai-slop-jp)（語彙より先に立場と主体を直す順序）、[textlint-rule-preset-ai-writing](https://github.com/textlint-ja/textlint-rule-preset-ai-writing) の考え方を参考にしました（いずれも MIT ライセンス）。ルールとスクリプトは独自に作成しています。英語のAIっぽい表現のリストは、Wikipedia の「Signs of AI writing」の考え方を翻訳向けに書き直したものです。日本語のリストは独自に作成しました。

[MIT License](LICENSE)
