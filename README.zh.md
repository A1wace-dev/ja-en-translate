# ja-en-translate

[English](README.md) | [日本語](README.ja.md) | 中文

一个面向日英双向翻译的 Agent Skill。翻译之前先判断**这是什么样的文本、写给谁看**，再按对应语境的规则翻译。适用于 Claude Code、Codex 等能读取 `SKILL.md` 的工具。

商务邮件、课程レポート、LINE 消息、字幕文件，需要的日语和英语都不一样。这个 Skill 会给整篇文本（或其中每一节）分配一个"语境配置"，由它决定文体、敬语级别、结构调整的幅度，以及能否加译注。它还会按翻译方向检查典型错误，并检查译文里有没有混进原文没有的 AI 腔。

## 特点

- **8 种语境**：`academic`（论文、课程レポート）、`business`（商务邮件、给教授的邮件）、`technical`（技术文档）、`official`（法令、在留手续）、`literary`（文学、随笔）、`marketing`（广告、SNS）、`casual`（聊天）、`subtitle`（字幕、幻灯片）。自动判断并记录依据，一篇文档可以分段使用不同语境。
- **3 种模式**：`quick`（直接翻译）、`normal`（先分析再翻译）、`refined`（分析→初稿→批评→修订→润色）。每一步都保存成文件。
- **按方向审校**：日→英检查主语省略、单复数、时态、隐含逻辑、和製英語、语气强弱；英→日检查翻译调（代词滥用、无生物主语、の连用、〜することができる、文体混用）和二重敬语等敬语错误。
- **AI 腔防护**：不在译文里加入原文没有的「不是……而是……」式对比、「〜と言えるでしょう」式收尾句、夸大的意义和套话。用户要求时（`--humanize rewrite`）也可以弱化原文自带的 AI 腔，并列出每一处改动。
- **不擅自补全**：原文没说清的主语、人名读音、指代对象，会根据上下文判断，并列入「Please confirm」请你确认。
- **长文处理**：日文按字符、英文按词计算长度，按 Markdown 块切分，在同一份术语表和翻译说明下并行翻译。
- **可配置**：在 `EXTEND.md` 里设置个人术语表、默认语境、各语境的覆盖项。只依赖 Python 3.9+。

示例：[examples/context-switching.md](examples/context-switching.md)、[examples/ai-tone-guard.md](examples/ai-tone-guard.md)

## 安装

```bash
npx skills add A1wace-dev/ja-en-translate --agent claude-code   # 其他工具见 skills CLI 文档
```

手动安装：

```bash
git clone https://github.com/A1wace-dev/ja-en-translate.git
cp -R ja-en-translate/skills/ja-en-translate ~/.claude/skills/   # Claude Code
cp -R ja-en-translate/skills/ja-en-translate ~/.codex/skills/    # Codex
```

Claude 应用：把 `skills/ja-en-translate` 文件夹压缩成 zip，在设置的 Skills 部分上传。

## 用法

```text
把 report.md 翻成英文
精翻 abstract.md --context academic
快翻：明日の会議は15時からに変更になりました
把这封邮件翻成日语，发给合作公司的部长
把 lecture.srt 翻成日语字幕 --context subtitle
英訳して、AI味也去掉 --humanize rewrite
```

normal 模式完成后，回复「继续润色」/「推敲して」/「refine」即可对同一份译文继续做批评和润色。

## 配置示例

首次使用会问 4 个问题，并生成 `~/.ja-en-translate/EXTEND.md`：

```yaml
default_context: academic
humanize: guard
glossary:
  - ja: 多文化共生
    en: multicultural coexistence
context_overrides:
  academic:
    notes: footnote
```

术语也可以放在单独的 Markdown 表格文件里，用 `glossary_files` 引用；表格中的 `context` 列可以限定某个术语只在特定语境下生效。

## 局限

- 这些规则是给语言模型的指引，不能保证译文一定正确。涉及法律、学术、金钱后果的文本请自己核对；公文以日语原文为准。
- 内置术语表很小，专业术语请写进自己的 `EXTEND.md`。

## 致谢与许可

工作流设计参考了 [baoyu-translate](https://github.com/JimLiu/baoyu-skills)（MIT），没有复制其文本或代码。英文 AI 腔清单改编自维基百科「Signs of AI writing」的思路，并针对翻译重写；日文清单为原创。

[MIT License](LICENSE)
