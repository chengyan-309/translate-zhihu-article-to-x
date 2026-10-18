# Translate Zhihu Article to X

将指定知乎内容编译成 Zhihu Frontier 风格的英文 X 技术解读。当前编辑规范：**2026-10-18**。

## 触发方式

发给支持 Skills 的 agent：**翻译X平台外放文章 + 原文链接**。

```text
翻译X平台外放文章：https://www.zhihu.com/question/.../answer/...
```

也支持文章、想法链接和明确提供的 Markdown/PDF/截图正文。新对话不需要复制旧聊天记录，但 agent 必须实际加载 `SKILL.md` 和其中指定的风格示例。

## 这版的风格

- 完整读取指定原文后编译，不能根据标题或搜索摘要猜写。
- 第一屏放最强结论或反差，保留证据、技术机制和关键限制。
- 普通评测通常 180–280 英文词；技术稿通常 250–400 词。用户要求展开时可以更长，不再套用旧版 1500 字符上限。
- 短段落、自然英文，不堆参数，不机械排比，不把“精简”变成只有结论。
- 总标题使用 `# **标题**`，小标题加粗，作者为 `Zhihu contributor *原文昵称*`。
- 不使用 emoji、hashtags、em dash 或表格。全部链接放评论。
- 输出两个可分别复制的 Markdown 块：`Post` 和 `Comment`。富文本能否保留取决于目标编辑器。

## 安装

将**整个仓库**安装到 agent 支持的 Skills 目录，不能只复制 `SKILL.md`，因为风格样本和细则也需要加载。

Codex 示例（目录不存在时）：

```bash
git clone https://github.com/chengyan-309/translate-zhihu-article-to-x.git ~/.codex/skills/translate-x-platform-article
```

也可显式调用：

```text
使用 $translate-x-platform-article 翻译这篇内容为 X 英文帖：[原文链接]
```

其他 agent 使用它们实际支持的 Skills 目录，不需要沿用 Codex 的本机路径。若仓库为 private，安装和更新者需要仓库访问权限。

## 更新与多 Agent 使用

已通过 Git 安装且本地没有未处理改动时：

```bash
git -C ~/.codex/skills/translate-x-platform-article pull --ff-only
```

有本地改动时先检查并保留，不要强制覆盖。若是通过下载 ZIP 或安装器复制的版本，应重新更新整个文件夹。

同一台电脑可让多个 agent 的 Skills 入口软链接到同一个受 Git 管理的文件夹；更新共享文件夹即可让它们读取同一版本。已开启的对话可能缓存旧规则，需要重读或新开对话。

**GitHub 与本地不会自行后台同步。** 修改后需要提交并推送；同事的独立副本也需拉取。此仓库提供可移植的规则与样本，不能保证不同模型、工具权限和原文可访问性下逐字一致。

## 文件说明

- `SKILL.md`：完整执行入口与交付约定。
- `references/editorial-guide.md`：不同文章类型的编辑判断和特殊任务。
- `references/examples.md`：两篇历史成稿的风格样本，不是新文章事实来源。
- `references/evaluation.md`：新对话回归测试及人工验收标准。
- `scripts/check_output.py`：仅使用 Python 标准库的输出格式检查器。
- `agents/openai.yaml`：Codex 的技能展示信息。

检查保存好的成稿：

```bash
python3 scripts/check_output.py /path/to/draft.md
python3 scripts/check_output.py --self-test
```

本次更新重点：解除过紧的字符限制，固化最近成稿的篇幅与语气，保留技术因果链和评测 caveat，增加跨对话示例与回归测试。它取代旧版 emoji 排版规则。
