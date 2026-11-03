# Translate Zhihu Article to X

将指定知乎内容编译成 Zhihu Frontier 风格的英文 X 短帖、技术解读或 Thread。当前编辑规范：**2026-11-02**。

## 触发方式

发给支持 Skills 的 agent：**翻译X平台外放文章 + 原文链接**。

```text
翻译X平台外放文章：https://www.zhihu.com/question/.../answer/...
```

也支持文章、想法链接和明确提供的 Markdown/PDF/截图正文。新对话不需要复制旧聊天记录，但 agent 必须实际加载 `SKILL.md` 和其中指定的风格示例。

## 这版的风格

- 完整读取指定原文后编译，不能根据标题或搜索摘要猜写。
- 围绕一个核心问题，优先呈现作者独有的证据、经验和技术判断；保留机制和关键限制。
- 单独审校前两句，降低理解门槛，不扩大结论范围或制造悬念。
- 按信息结构选择短帖、单篇技术解读或 Thread，不用参考词数凑篇幅。Thread 首帖独立有用，后续每帖推进一个问题，必要限定不能全部后置。
- 自然时提出一个具体的讨论问题，没有合适问题就省略；不承诺早期互动或推荐效果。
- 短段落、自然英文，不堆参数，不机械排比，不把“精简”变成只有结论。
- 默认直接进入内容，标题可选；需要标题时使用 `# **标题**`，小标题按需加粗，作者为 `Zhihu contributor *原文昵称*`。
- 不使用 emoji、hashtags、em dash 或表格。全部链接放评论。
- 原文链接引导语在 `Original Zhihu article`、`Read the full article by 作者 on Zhihu (CN)`、`Source: 作者 on Zhihu (in Chinese)` 三种格式间随机交替；替换为实际作者，回答用 `answer`。
- 单帖输出 `Post` 和 `Comment`；Thread 输出连续编号的 `Post 1`、`Post 2` … 和最后一个 `Comment` 来源块。各块独立可复制，富文本能否保留取决于目标编辑器。

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

同一台电脑可让多个 agent 的 Skills 入口软链接到同一个受 Git 管理的文件夹；更新共享文件夹即可让它们读取同一版本。新对话首次调用必须实际读取当前 SKILL.md 与示例；已开启的对话在明确更新后也要重读，不用聊天记忆代替文件。Codex 自动检测技能更新，若界面未刷新可重启应用，见 [官方说明](https://learn.chatgpt.com/docs/build-skills)。

**GitHub 与本地不会自行后台同步。** 修改后需要提交并推送；同事的独立副本也需拉取。此仓库提供可移植的规则与样本，不能保证不同模型、工具权限和原文可访问性下逐字一致。

## 文件说明

- `SKILL.md`：完整执行入口与交付约定。
- `references/editorial-guide.md`：不同文章类型的编辑判断和特殊任务。
- `references/examples.md`：短帖、技术解读、Thread 和钩子边界的风格样本，不是新文章事实来源。
- `references/evaluation.md`：新对话回归测试及人工验收标准。
- `scripts/check_output.py`：仅使用 Python 标准库的输出格式检查器。
- `agents/openai.yaml`：Codex 的技能展示信息。

检查保存好的成稿：

```bash
python3 scripts/check_output.py /path/to/draft.md
python3 scripts/check_output.py --self-test
```

本次更新重点：取消强制标题、单独审校开头、增加形式选择、分层管理篇幅、自然讨论入口、围绕来源独有价值选材。
