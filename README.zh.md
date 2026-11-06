# ja-en-translate

[English](README.md) | [日本語](README.ja.md) | 中文

ja-en-translate 是一个用于日英互译的 Agent Skill。它在动笔之前先判断**手上是什么文本、读者是谁**，再按相应语境的规则来翻译。Claude Code、Codex 等能读取 `SKILL.md` 的工具都可以使用。

商务邮件、课程报告、LINE 消息和字幕文件，要求的日语和英语各不相同。这个 Skill 会为整篇文本或其中的每一节指定一种“语境”，由语境决定文体、敬语级别、句子可以调整到什么程度，以及是否允许加译注。译完之后，它会针对翻译方向检查常见错误，并检查译文有没有混入原文里没有的 AI 腔。

## 特点

- **8 种语境**：`academic`（论文、课程报告）、`business`（商务邮件、给教授的邮件）、`technical`（技术文档）、`official`（法令、居留等行政手续）、`literary`（文学、随笔）、`marketing`（广告、SNS）、`casual`（聊天）、`subtitle`（字幕、幻灯片）。Skill 会自动判断并记录理由，同一篇文档也可以分段使用不同语境。
- **3 种模式**：`quick`（直接翻译）、`normal`（先分析再翻译）、`refined`（分析→初稿→批评→修订→润色）。每一步都保存成文件。
- **按方向审校**：日→英检查主语省略、单复数、时态、没有明说的逻辑关系、和製英語（日式英语），以及断言的强弱；英→日检查翻译调（代词滥用、无生物主语、の连用、〜することができる、文体混用）和二重敬语等敬语错误。
- **防止 AI 腔**：不会在译文里加入原文没有的内容，比如“不是……而是……”式的对比、「〜と言えるでしょう」式的收尾句、夸大其词的评价和套话。如果你提出要求（`--humanize rewrite`），它也会淡化原文本身的 AI 腔，并列出每一处改动。
- **补全必有交代**：原文没有写明的主语、人名读音和指代对象，会根据上下文作出判断，并逐条列在“Please confirm”中请你确认。
- **长文处理**：日文按字数、英文按词数计算长度，按 Markdown 块切分后并行翻译，各部分遵循同一份术语表和翻译说明。
- **可配置**：可以在 `EXTEND.md` 中设置个人术语表、默认语境，以及针对各语境的单独设置。运行只需要 Python 3.10 或更高版本。

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
翻成英文，顺便去掉 AI 味 --humanize rewrite
```

normal 模式译完后，回复“继续润色”“推敲して”或“refine”，就会对同一份译文继续进行批评和润色。

## 配置示例

第一次使用时会询问 4 个问题，并据此生成 `~/.ja-en-translate/EXTEND.md`：

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

术语也可以写在单独的 Markdown 表格文件里，通过 `glossary_files` 引用。表格中的 `context` 列可以指定某个术语只在特定语境下使用。

## 局限

- 这些规则只是给语言模型的指引，并不能保证译文准确。可能产生法律、学术或经济后果的文本，请务必自行核对；公文以日语原文为准。
- 内置术语表只收录了少量词条，你所在领域的专业术语请加入自己的 `EXTEND.md`。

## 致谢与许可

工作流程的设计参考了 [baoyu-translate](https://github.com/JimLiu/baoyu-skills)（MIT 许可），但没有复制其中的文字或代码。英文 AI 腔清单借鉴了维基百科“Signs of AI writing”的思路，并针对翻译场景重新编写；日文清单为原创。

[MIT License](LICENSE)
