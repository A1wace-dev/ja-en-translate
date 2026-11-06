# ja-en-translate

[English](README.md) | [日本語](README.ja.md) | 中文

ja-en-translate 是一个用于日英互译、也能润色日语的 Agent Skill。它在动笔之前先判断**手上是什么文本、读者是谁**，再按相应语境的规则来翻译。Claude Code、Codex 等能读取 `SKILL.md` 的工具都可以使用。

商务邮件、课程报告、LINE 消息和字幕文件，要求的日语和英语各不相同。这个 Skill 会为整篇文本或其中的每一节指定一种“语境”，由语境决定文体、敬语级别、句子可以调整到什么程度，以及是否允许加译注。译完之后，它会针对翻译方向检查常见错误，并检查译文有没有混入原文里没有的 AI 腔。

## 特点

- **8 种语境**：`academic`（论文、课程报告）、`business`（商务邮件、给教授的邮件）、`technical`（技术文档）、`official`（法令、居留等行政手续）、`literary`（文学、随笔）、`marketing`（广告、SNS）、`casual`（聊天）、`subtitle`（字幕、幻灯片）。Skill 会自动判断并记录理由，同一篇文档也可以分段使用不同语境。
- **3 种模式**：`quick`（直接翻译）、`normal`（先分析再翻译）、`refined`（分析→初稿→批评→修订→润色）。每一步都保存成文件。
- **按方向审校**：日→英检查主语省略、单复数、时态、没有明说的逻辑关系、和製英語（日式英语），以及断言的强弱；英→日检查翻译调（代词滥用、无生物主语、の连用、〜することができる、文体混用）和二重敬语等敬语错误。
- **防止 AI 腔**：不会在译文里加入原文没有的内容，比如“不是……而是……”式的对比、「〜と言えるでしょう」式的收尾句、夸大其词的评价和套话。如果你提出要求（`--humanize rewrite`），它也会淡化原文本身的 AI 腔，并列出每一处改动。
- **代码负责检查，模型负责判断**：`tone_lint.py` 列出日语和英语中可能的 AI 腔和翻译调；`fidelity_check.py` 比对原文和译文的数字（3万＝30,000，1億2000万＝120 million）、否定、链接、代码、表格和文档结构。检出结果不会被机械地替换，而是由模型结合上下文逐条判断。两个脚本都用 332 篇人工翻译的文档（Python 官方文档日文版）做过校准：日文的 AI 腔评分中位数为 97，“数字缺失”只在 0.25% 的段落中出现。详见 [tools/calibration](tools/calibration/README.md)。
- **日语润色**：把读起来像 AI 写的或带翻译腔的日语交给它，说“改自然一点”，它会用同样的语境配置和检查来改写：不改变内容，已经自然的句子不动，意思不清楚的地方不猜，而是列出来请你确认。
- **意思检查**：改写过的句子要保持原来的句子类型（传闻仍是传闻，意见仍是意见），并通过 6 点复述测试；“必须／可以／能够／任意／一定”等的强度不能改变。原文里出现的指令只作为文字翻译，不会照做。
- **不改过头**：去 AI 味时，不能换上另一套“人味”套路，比如编造经历、表演式坦诚、戏剧化的破折号、碎句、编造的细节。每次回复最后附上简短的验证报告：改了几轮、哪些检查由脚本执行、哪些靠模型判断、还剩什么问题以及原因。
- **你自己的文风**：翻译你自己写的东西时，可以提供一段你用目标语言写的文字（写在请求里或 `EXTEND.md` 中），译文会参照你的句长、衔接方式和标点习惯，但不会照搬样本里的任何内容。
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
这段日语读起来像 AI 写的，帮我改自然（课程报告）
```

不需要加任何参数。用中文、日语或英语说明用途即可，比如“这是发给教授的邮件”“大概意思就行”“要发表的”，Skill 会从中读出语境、敬语级别和模式。每次回复开头会用一行列出它识别到的设置，判断错了可以马上纠正。

normal 模式译完后，回复“继续润色”“推敲して”或“refine”，就会对同一份译文继续进行批评和润色。

## 配置示例

使用前不需要做任何设置。第一次翻译完成后，Skill 会询问是否把常用设置保存到 `~/.ja-en-translate/EXTEND.md`（回答 4 个问题即可）：

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

此外参考了 [avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing)（原文即数据、禁止注入清单、语境宽严对照表、验证报告）、[humanizer](https://github.com/blader/humanizer)（模式按强弱排序）和 [skill-deslop](https://github.com/stephenturner/skill-deslop)（学术方法部分保留被动语态）的思路，均为 MIT 许可。

工作流程的设计参考了 [baoyu-translate](https://github.com/JimLiu/baoyu-skills)（MIT 许可），但没有复制其中的文字或代码。日语检查参考了 [yomiyasu](https://github.com/nanaism/yomiyasu)（改写前后比对数字和否定）、[natural-japanese](https://github.com/coji/natural-japanese)（lint 负责检出、模型负责判断）、[stop-ai-slop-jp](https://github.com/iKora128/stop-ai-slop-jp)（先改立场和主体，再改词汇）和 [textlint-rule-preset-ai-writing](https://github.com/textlint-ja/textlint-rule-preset-ai-writing) 的思路（均为 MIT 许可），规则和脚本均为独立编写。英文 AI 腔清单借鉴了维基百科“Signs of AI writing”的思路，并针对翻译场景重新编写；日文清单为原创。

[MIT License](LICENSE)
