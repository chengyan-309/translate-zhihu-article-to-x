---
name: translate-x-platform-article
description: "当用户说‘翻译X平台外放文章’并提供知乎文章或回答链接时触发。读取且仅读取目标内容，将中文技术文章提炼、核验并重写成适合 Zhihu Frontier 在 X 发布的 English-native 技术解读稿。适用于 AI、模型、Agent、AI Infra、芯片、科研、机器人、网络安全等主题；支持仅翻译 highlights、按比例精简、强调指定侧重点、保留关键链接等单篇要求。"
---

# 翻译 X 平台外放文章

## 目标

把一篇知乎中文文章或回答，重写为适合海外 tech / AI 受众在 X 阅读的英文长帖。

这不是逐句翻译，也不是摘要生成。目标是：

- 忠实保留原文核心观点、机制、证据和结论。
- 删除重复铺垫、口语赘述和不影响理解的细节。
- 按 English-native tech explainer 的逻辑重组。
- 让读者快速理解：发生了什么、真正新在哪里、机制如何工作、证据是什么、为什么重要。
- 保持短段落、清晰层级和可直接复制到 X 编辑器的 Markdown 格式。

## 触发条件

用户出现以下任一表达并提供知乎链接时使用本 Skill：

- `翻译X平台外放文章：...`
- `翻译 x 平台外放文章：...`
- 要求把某篇知乎文章改写为适合 X / Twitter 发布的英文稿。
- 在已开始的翻译任务中要求重新翻译、精简、扩写、调整开头或重新排版。

不要把普通中英翻译任务、X 搬运到知乎任务或纯英文润色任务误触发为本 Skill。

## 优先级

执行时按以下优先级处理要求：

1. 用户对当前这篇文章提出的单篇要求。
2. 本 Skill 的事实忠实、安全和输出硬规则。
3. 本 Skill 的默认长度、结构和风格偏好。

用户明确说“仅针对这篇”时，该要求只影响当前文章，不自动变成全局规则。

## 完整工作流

### Step 1：读取并隔离目标原文

只读取目标知乎文章或回答的：

- 标题
- 作者昵称
- 正文
- 正文内对论证必要的链接、图表数据和注释

禁止混入：

- 问题页摘要或其他回答
- `更多回答` 之后的内容
- 评论区
- 广告、推荐卡片、侧栏热榜
- 相关文章、搜索摘要和自动生成的页面模块

知乎问题页可能把多个回答拼在同一抓取结果中。必须以目标回答的作者、正文开头和正文结束位置为边界；看到 `更多回答`、另一位作者、另一套论证或明显无关内容时立即停止。

不要把搜索引擎 snippet 当作完整原文。优先使用：

1. 能读取正文的知乎连接器或网页阅读工具。
2. 用户已登录的浏览器页面。
3. 其他可靠网页读取工具。
4. 若仍无法取得正文，请用户粘贴原文或上传附件。

如果文章关键结论只存在于图表中，应读取图表标题、坐标、图例和关键数字；不要凭模糊图片猜测数据。

### Step 2：建立事实边界

在动笔前，把素材在内部区分为三类：

- **原文事实或引用结果**：论文结果、benchmark、产品参数、发布时间、公开数据。
- **原作者观点**：评价、预测、类比、推断和价值判断。
- **外部近期背景**：官方公告、当事人公开发言、近期争议或新闻。

写作时必须保持边界：

- 不把作者猜测写成已经证实的事实。
- 不把相关性写成因果关系。
- 不把行为相似性写成模型来源、记忆或蒸馏的证明。
- 不把外部热点伪装成原文内容。
- 不添加“最大的故事”“历史性突破”“首次证明”等主观判断，除非原文或可靠一手来源明确支持。
- 对尚未独立验证的 benchmark 使用 `the company reports`、`in the author's comparison` 等限定语。

模型名、论文名、机构名、人物身份、数字、单位和时间必须核对拼写。外部核验优先使用官方公告、论文、项目仓库、技术文档或当事人原帖。

### Step 3：做一次快速近期热点检查

每篇译文开始前，对主题做一次短而定向的近期检查，判断是否有自然的新闻切口。

热点必须同时满足：

- 时间足够近，通常优先最近几天；研究节奏较慢的主题可放宽到数周。
- 与文章主题直接相关，而非仅仅同属 AI。
- 来源可信，优先官方公告、论文、当事人原帖或公开采访。
- 能回答“为什么这篇内容现在值得看”。

使用方式：

- 最多选择一个最强热点。
- 只写 1-3 个短句。
- 必要时保留一个一手来源链接。
- 随后立即转入知乎原文。

以下情况直接跳过热点：

- 只有弱相关事件。
- 需要翻找很久以前的旧闻。
- 事件真实性或原意无法确认。
- 热点会盖过原文核心。

不要硬蹭，不要把普通产品更新写成 `BREAKING`。

### Step 4：提炼原文主线

先用一句内部工作句概括全文：

> This article argues that [core claim], because [mechanism/evidence], which matters for [implication].

然后筛选信息。优先保留：

- 最核心的判断或反常识点
- 关键机制及其为什么有效
- 能支撑观点的关键数字和对比
- 生产实践、真实使用或实验结果
- 限制、失败条件和作者明确保留意见
- 开源、论文、项目、历史成绩等关键链接
- 对 AI Infra、Agents、training、inference、robotics、AI for Science 或开发者工作流的实际意义

优先删除或合并：

- 重复表达同一观点的段落
- 过长的个人经历和聊天铺垫
- 多个作用相同的例子
- 不能强化观点的 benchmark 与参数堆砌
- 逐步复述但不影响机制理解的操作细节
- 面向中文语境的口头禅、反问和情绪重复
- 与 Zhihu Frontier 的 AI / tech 定位关系较弱的专业展开

若原文是跨学科内容，例如数学、科研或产业史，优先提炼 AI、AI for Science、研究智能体、开源生态和技术路线相关部分。用户明确要求保留专业细节时除外。

### Step 5：决定压缩强度

默认明显压缩原文，不按中文段落比例翻译。总原则是宁短勿长，严格控制字数：

- 普通技术文章：约 **500-800 English words**。
- 信息密度很高且机制复杂：最多约 **900-1000 words**。
- 原文较短：可低于 500 words。
- 用户说“只翻 highlights / 不用全文”：约 **400-600 words**，只保留 3-5 个最强观点。
- 用户说“精简到原文的 70% / 当前版本的 60%”：以信息量和英文成稿长度执行，而不是机械按字符裁切。
- 用户说“不要太精简”：补回解释机制所需的上下文，不补回重复铺垫。

宁可少保留一个次要 benchmark，也不要让正文成为数字清单。写完后自查：每一段是否都在推进主线，不能推进的直接删。

### Step 6：重组为 English-native X explainer

默认叙事顺序：

1. **Title / hook**：发生了什么，真正新在哪里。
2. **Strongest conclusion first**：第一屏必须直接放出全文最强的结论或判断。
3. **Optional news context**：为什么此刻值得读。
4. **Contributor intro**：谁在知乎解释了这件事。
5. **Core judgment**：用 1-2 句给出全文主线。
6. **Mechanism blocks**：问题、方法、结果、意义。
7. **Limitations / nuance**：哪些结论尚不能推出。
8. **Broader implication**：回到工程、研究或行业影响。
9. **Links and hashtags**。

**第一屏硬规则：** 读者只看标题和开头两三行，就必须拿到全文最强的结论。禁止用背景介绍、定义铺垫或新闻复述把最强判断推到第二屏。如果开头在解释「这是什么」而不是给出「最重要的判断是什么」，重写开头。

钩子的优先级：**最强结论 > 关键数据 > 核心争议 > 时效新闻**。新闻只有在足够新鲜时才配当钩子；如果事件已发生多日、受众早已知晓（例如模型发布超过一周），新闻不再提供信息增量，必须从开头删掉或压缩成从属半句，改用最强结论、关键数据或核心争议开篇。

不必机械沿用中文段落顺序，但不能改变原文论证方向。重组是为了让英文读者更容易理解，不是为了加入新的故事。

## 标题规则

第一行必须是 Markdown 一级标题，并整句加粗：

`# **🤖 Robotics Is Still Waiting for Its GPT Moment**`

硬规则：

- 只有文章总标题使用 `# **...**`。
- 标题必须是英文，允许在开头放一个贴合主题的 emoji。
- 不机械直译中文标题。
- 优先包含海外读者最在意的项目、公司、学校、模型或技术关键词。
- 标题直接表达事件、核心变化或关键判断。
- 避免空泛标题，如 `Some Thoughts on...`、`A Deep Dive into...`，除非确实最自然。
- 避免无依据的夸张词，如 `revolutionary`、`game-changing`、`historic`。
- 避免拟人化、故事化的标题，如 `X Won by...`、`How X Conquered...`、`The Rise of...`；标题应像 tech X 上的技术判断句，直接陈述机制、原因或对比，例如 `Almost No Priors, Infinitely Parallel: Why the Transformer Reshaped Deep Learning`。

## 作者引入规则

统一使用：

`Zhihu contributor *作者昵称* ...`

禁止：

- `Zhihu author`
- 作者名前加 `@`
- 把作者昵称加粗

作者昵称只使用斜体。句式可以变化，例如：

- `Zhihu contributor *酱紫君* argues that...`
- `Zhihu contributor *苏剑林* offers a concise explanation of...`
- `Zhihu contributor *知乎科技* spoke with...`

只有当用户或原文明确提供作者身份、与受访者关系或相关经历时，才在开头加入。身份若可能变化，应通过一手来源核验。

若用户要求在文中体现作者所属公司或其 X 账号（如招聘、品宣需求），必须把提及自然融入正文：在作者介绍处交代 affiliation，在结尾随作者的 closing thought 顺带带出账号（如 `His team at X (@handle) is one of the groups working on exactly this.`）。若原文本身以开放邀请收尾（如「欢迎加入我们」），结尾应保留这种邀请语气并附上原文提供的联系方式（邮箱等），不要改写成 `he notes they are hiring` 这类旁观陈述。禁止单列一个生硬的推广/招聘 section（如 `The invitation` / `A pitch`），也不要写成广告口号。

## Section 与段落格式

正文通常重组为 4-7 个主要信息块。

每个主要小标题必须整句加粗，但不能使用 `#`：

- `**1️⃣ Why long-horizon RL breaks binary rewards**`
- `**⚙ The bottleneck moved to the sandbox**`
- `**🔄 Vision plans slowly. Touch reacts quickly**`

小标题必须与对应段落内容紧密相关，直接概括该段的核心信息或判断，是 English-native tech 读者会自然使用的表达。

- 禁止 `Verdict`、`Conclusion`、`Summary`、`Final thoughts`、`Why it matters` 这类与具体内容无强关联的通用标签。
- 收尾段也要用具体判断作标题，例如作者认为智谱仍是国产第一，就写 `**5️⃣ Zhipu is still the team to beat**`，而不是 `**5️⃣ Verdict**`。
- 写完后自查：只看小标题能否猜到这一段讲什么。猜不到就重写。

技术长文、多机制或多发现内容优先使用 `1️⃣/2️⃣/3️⃣`。语义更自然时可使用 `⚙/🔄/📊/🔓/🧠/🚀`。

Section 内可使用：

- `🔹`：二级任务、能力维度、并列观点或短对比。
- `✅`：关键结果、明确收益或验证结论。
- `🟢/🔵`：两组对照。
- `👉`：最终 distilled takeaway，最多少量使用。
- `🔷/🔸`：较长 section 中的短分块。

每个符号必须承担结构作用，不作为纯装饰。

段落要求：

- 通常 1-3 句。
- 通常约 20-55 English words。
- 复杂机制段最多约 70 words；超过时拆分。
- 一个段落只讲一个中心意思。
- 段内避免密集加粗。
- 不连续堆叠 4-6 个句式相同的短句。
- 不用多个反问句制造节奏。
- 不把普通解释强行拆成 bullet。

**段落瘦身硬规则（防止文字堆砌）：**

- 一个 section 内若有 2-4 个并列要点，不要揉成一个 50-70 词的大段落，必须用「短引导句 + `🔹` 分条」拆开。
- 引导句要短，通常以冒号结尾，如 `Verification combines:`、`The fix has three parts:`。
- 每条 `🔹` 只保留一行、一个信息点；超过两行的条目继续压缩。
- 同一 section 内连续两个长段落覆盖不同要点时，优先把其中一个改写为分条结构。
- 参考样式：

`**3️⃣ Redwood automates the development loop**`

`When a design misses its targets, results return for another iteration. Verification combines:`

`🔹 UVM simulation for concrete and randomized scenarios`

`🔹 Formal methods for state and timing properties`

`🔹 Hardware-in-the-loop testing with real firmware`

## 空行硬规则

主题不同的主要段落或信息块之间必须多空一行。

为防止复制到 Word、飞书、Notion、Google Docs 等编辑器后空行被吞掉，在空白行中放入一个全角空格：`　`

占位空行只用于不同主题块之间。Section 标题与其正文属于同一块，标题行与正文之间不使用占位空行，直接换行衔接：

`**1️⃣ Why long-horizon RL breaks binary rewards**`

`Binary rewards collapse once...`

上一块正文结束、下一块标题开始前才使用占位空行：

`...end of section one.`

`　`

`**2️⃣ Next section**`

同一小块内部不要滥用占位空行。

## 英文写作规则

目标语气：清楚、克制、自然、有技术判断，像 English tech X 上的人在解释问题。

必须做到：

- 先理解，再用自然英文重写。
- 优先短句和中短句。
- 技术术语准确，普通说明轻量。
- 主语清晰，避免一条句子塞入多个从句。
- 把中文连续反问改写为自然陈述。
- 把中文排比改写为一个完整段落或真正的结构化列表。
- 类比最多保留一个，并立即回到技术机制。
- 对预测使用 `may`、`could`、`the author expects` 等限定。
- 对公司自报结果使用 `reports`、`claims` 或明确说明评测来源。

避免：

- 中文语序和逐词对应
- 新闻通稿腔或营销口号
- 论文摘要式长句
- 模板化重复 `The key is... / The result is... / The deeper insight is...`
- 生硬所有格和不自然搭配
- 过度使用破折号、冒号或括号
- 连续使用否定式排比
- 每段结尾都空泛拔高

写完后做一次 native pass：检查英语母语使用者是否会自然地这样表达，而不仅仅检查语法是否正确。

native pass 时专项排查中式直译措辞，尤其是小标题和分类标签：

- 不要把中文分类词直译为名词短语作标题：`缺点` → `The weak spot`（生硬）；更 native 的写法是用动作或画面感的表达，如 `Where 0915 still stumbles`、`The Achilles' heel: hallucination`、`Where it falls short`。
- 常见中式英语替换：`a middle seat` → `caught in the middle`；`hard flaws` → `visible flaws`；`no better than same-tier models` → `on par with peers`。
- 判断标准：这句话能否原样出现在 The Pragmatic Engineer、Latent Space 或技术博主的 X 帖里。不能就重写。

### 视角转换：中文中心用词必须改写

成稿面向 X 上的国际读者，中文原文里的中国中心视角词必须转换，不能直译：

- `国内 / 国产 / 国模` → `Chinese` / `China's` / `in China`，**禁止用 `domestic`**（对国际读者来说 domestic 指他们自己的国家，指代不明）。
- 例：国产芯片 → `Chinese chips` 或 `China-made chips`；国产大模型 → `Chinese models` / `Chinese LLMs`；国产算力 → `Chinese compute`；国内厂商 → `Chinese labs` / `Chinese companies`。
- `海外 / 外网` → `outside China` / `international`，慎用 `overseas`。
- `这边 / 咱们 / 国人` 等口语视角词直接删除或改写为中性陈述。
- 其他以中文读者为默认视角的表达（如不解释就使用的中文社区梗、昵称）同样要转换为国际读者能理解的写法。

写完后专项自查一遍：全文不应残留 `domestic`、`overseas` 等中文中心视角词。

## Benchmark、参数与表格

只保留能强化观点或帮助理解的数字。

**公式处理：** 默认不把细节公式搬入译文（KL 表达式、指数加权、梯度式等），用一两句自然语言说明这个公式在做什么、为什么重要。只有极简且本身承载核心论点的表达式可以保留，如 `RL = Local Optimum Construction + Projection`。X 读者不需要在正文里读推导。

默认规则：

- 一篇文章通常保留 2-5 组最有解释力的数字。
- 数字后要说明它证明了什么，而不是单独陈列。
- 区分官方 benchmark、作者自测、用户体感和推测。
- 不把榜单排名等同于全面能力。

禁止 Markdown 表格。X 编辑器难以维护表格，应改写为短 bullet：

`🔹 DeepSWE: **66.9** vs. 62.7`

`🔹 CyberGym: **84.5** vs. 83.3`

如果文章本身是月榜或模型横评，至少保留参评模型名称和最关键结果；不要把全部 benchmark、参数和链接无差别搬入。

## 链接规则

正文中出现以下链接时必须保留，属于关键链接：

- 论文原文
- 官方项目或代码仓库
- 模型卡、技术报告或官方公告
- 数据集和 benchmark 页面
- 重要榜单、排行榜和历史成绩查询网站
- 对理解结论不可替代的原始材料和关键网站

不要保留广告、推荐内容或无关跳转。

关键链接统一收集到文章末尾，不在正文段落中内嵌。在正文末尾、`🔗 Full Reading` 之前设置一个链接区：

`**🔗 Key links:**`

其下用短 bullet 逐条列出，格式为 `简述: URL`：

`- Technical report: https://...`

`- Monthly logic benchmark: https://...`

规则：

- 通常 2-6 个，只收“缺了会影响理解或验证”的链接，宁缺毋滥。
- 每个 bullet 的简述保持 2-6 个英文单词，不写长句。
- 正文提到某链接对应的材料时，用自然文字指代即可（如 `in the author's monthly logic evaluation`），不再放 URL。
- 若全文没有任何关键链接，整个链接区省略，不要硬凑。

近期热点或外部核验链接只使用直接的一手 URL，不要暴露搜索结果内部引用 ID。热点来源链接放在开头热点句中或 Key links 区均可，只出现一次。

结尾必须包含：

`🔗 Full Reading:`

下一行放用户提供的知乎原文链接。

也可在更偏研究解读时使用 `🔗 Full analysis:`，但默认优先 `Full Reading`。

## 加粗规则

正文应主动使用加粗引导视线，让读者扫读时快速抓住关键词与关键数据，优化阅读体验。但必须严格控制数量：加粗越少越有效，越多越贬值。

可以加粗：

- 机制名、模型名和关键概念（仅在首次出现且承担信息重心时）
- 关键数字与指标（如 **40%**、**$0.24**、**1/10**）
- 对比双方的关键差异
- 一句中的核心判断短语（只加粗短词组，不加粗整句）

数量硬上限：

- 每个 section 最多 2-3 处加粗。
- 全文正文（不含总标题和 section 标题）通常不超过 10-15 处。
- 同一段落最多 1-2 处，且两处不相邻。
- 不要连续每段都加粗；没有信息重心的段落可以完全没有加粗。

不要整句加粗，不要整段加粗，不要为了对称或装饰而加粗。Section 标题整句加粗是固定例外，不计入上述配额。

## Emoji 规则

Emoji 用于建立视觉层级，不用于装饰。

- 标题最多一个主题 emoji。
- 每个主要 section heading 使用一个编号或语义 emoji。
- 每个自然段最多一个 emoji。
- `🔹/✅/🟢/🔵` 只用于真实列表、对比和结果。
- 不用过多不同种类 emoji 制造花哨感。

## 特殊内容处理

### 用户要求只翻 highlights

- 不翻全文。
- 保留 3-5 个最强观点。
- 删除完整履历、长背景、全部案例和次要 benchmark。
- 仍需形成完整的标题、开头、正文逻辑和结尾链接。

### 用户要求突出指定侧重点

例如“突出国产算力与大模型适配”“侧重 AI 与科研”：

- 优先选择与该侧重点直接相关的原文信息。
- 可以大幅压缩其他部分。
- 不能为了满足侧重点添加原文没有的事实或判断。

### 数学、论文与 AI for Science

- 面向 Zhihu Frontier 时，优先讲 AI 如何参与科研、验证、工具使用和研究范式变化。
- 只有在理解 AI 意义所必需时，才展开具体数学证明或专业细节。
- 不虚构“AI 是事件最大亮点”等判断。

### 网络安全与漏洞研究

- 可以解释研究机制、威胁模型、实验结果、影响和修复状态。
- 不复制可直接滥用的 exploit prompt、攻击脚本、凭证或逐步入侵流程。
- 明确区分漏洞发现训练、能力涌现和未经证明的现实攻击能力。
- 若供应商已修复或方法已失效，必须保留这一限制。

### 争议、蒸馏与模型来源

- `behavioral compatibility`、低 perplexity、风格相似或 n-gram overlap 都不是来源证明。
- 使用 `suggestive but inconclusive`、`does not establish provenance` 等准确表达。
- 不把作者情绪化判断改写成事实标题。

## 输出硬格式

最终成稿必须满足：

1. 全文放在一个带 `markdown` 标记的代码块中，便于一键复制。
2. 代码块外默认不写解释、总结或客套话。
3. 外层代码块内部禁止再使用三反引号，避免破坏复制。
4. 第一行是 `# **English title**`。
5. 主题块之间用仅含全角空格 `　` 的占位行；section 标题与其正文之间不加占位行，直接换行衔接。
6. 正文不使用 Markdown 表格。
7. 结尾依次是：`🔗 Key links` 链接区（无关键链接时省略）、`🔗 Full Reading`、知乎链接、占位空行、hashtags。
8. Hashtags 使用英文，控制在 5-8 个。
9. Hashtags 优先选择项目名、模型名、公司名、技术领域及 AI/infra/agents 等高相关词。

## 推荐输出模板

    # **[emoji + English-native title]**
    　
    [Optional recent context, 1-3 short sentences with at most one primary-source link.]
    　
    Zhihu contributor *作者昵称* [explains / argues / shares / spoke with...].

    [Core judgment in 1-2 short sentences.]
    　
    **1️⃣ [Specific, content-tied section heading]**

    [Problem or mechanism.]

    [Necessary evidence or result.]
    　
    **2️⃣ [Specific, content-tied section heading]**

    [Next core idea.]

    🔹 [Real comparison or subtopic]

    ✅ [Key result, only when appropriate]
    　
    **3️⃣ [Limit, implication, or next mechanism — still specific, no generic labels]**

    [Nuance and why it matters.]
    　
    **🔗 Key links:**

    - Technical report: https://...
    - Benchmark / leaderboard: https://...
    　
    🔗 Full Reading:

    https://www.zhihu.com/...
    　
    #Project #Model #AIInfra #AIAgents #OpenSource

## 最终质量检查

发送前逐项检查：

### Source integrity

- [ ] 只使用目标文章或回答，没有混入其他回答、评论、广告或推荐。
- [ ] 作者昵称正确，使用 `Zhihu contributor`。
- [ ] 核心观点、机制和结论与原文一致。
- [ ] 外部热点与原文观点明确分开。
- [ ] 数字、模型名、论文名、人物身份和时间已核对。
- [ ] 作者观点、事实和推断没有混写。
- [ ] 未加入原文没有且无法验证的主观判断。

### Editorial quality

- [ ] 第一屏（标题+开头两三行）直接给出全文最强结论，无背景铺垫抢位。
- [ ] 字数符合档位：普通文章 500-800 words，高密度不超过 1000 words。
- [ ] 标题不是机械直译，并包含海外读者关心的关键信息。
- [ ] 开头直接给信息，不写泛泛背景。
- [ ] 正文只保留能强化观点或帮助理解的信息。
- [ ] Benchmark 和参数没有堆砌。
- [ ] 每个 section 只讲一个中心点。
- [ ] 结尾回到实际意义，没有空泛拔高。

### English quality

- [ ] 没有长难句或中文语序。
- [ ] 没有连续排比式短句。
- [ ] 没有不自然搭配、模板化过渡或营销腔。
- [ ] 段落通常为 1-3 句、20-55 words。
- [ ] 英文读起来像 tech X explainer，而不是论文摘要。
- [ ] 无中文中心视角词残留：`国内/国产` 已译为 `Chinese`，未使用 `domestic` / `overseas`。

### Formatting

- [ ] 总标题为 `# **...**`。
- [ ] 所有段落小标题整句加粗且不带 `#`，且具体概括该段内容；无 `Verdict`/`Conclusion`/`Summary` 等通用标签。
- [ ] Section 标题与其正文之间无占位空行；占位空行只出现在不同主题块之间。
- [ ] 无文字堆砌：并列要点已用「短引导句 + 🔹 分条」拆开，无 50-70 词以上的密集大段落。
- [ ] 正文加粗符合配额：每 section ≤2-3 处，全文 ≤10-15 处，无整句加粗。
- [ ] Emoji 有结构作用且不过量。
- [ ] 没有 Markdown 表格。
- [ ] 关键链接（论文、官方仓库、榜单等）统一收在文末 `🔗 Key links` 区，正文不内嵌 URL；无关键链接时该区省略。
- [ ] 全文在一个 `markdown` 代码块中，内部没有嵌套代码块。
- [ ] 原文链接位于 hashtags 前。
- [ ] Hashtags 为 5-8 个。

若任何一项不通过，先修正再输出。
