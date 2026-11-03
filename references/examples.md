# 成稿示例

首次在新对话执行本 skill 时读取。版本：2026-11-02。短帖与 Thread 使用明确标注的合成来源，技术解读保留历史样本；它们只校准形式和语气，不是新任务的事实来源或对产品表现的独立背书。新任务必须完整读取自己的指定原文。

学习结构和取舍，不复制标题、开头句式、数字、观点或作者身份。不要把每篇都写成“某个维度大跃进，另一个维度没变”。

## 示例零：短帖，不加标题、不强制问句

合成来源：昵称为求职者丁；两次面试被拒后整理了没答好的系统设计问题，第三次面试前用真实项目重讲设计取舍，表达更清楚。没有博士身份、最终录用结果或公开链接。此例不凑最低词数，不用群体心理制造共鸣。

Post

```markdown
After two rejections, Zhihu contributor *求职者丁* revisited the system design questions they had struggled to answer.

Before a third interview, they practiced explaining the trade-offs in a real project. Practicing those trade-offs made their explanation clearer.
```

Comment

```markdown
Source: the author-provided document.
```

## 示例一：单篇技术解读，可选标题

特点：适合用户需要完整评测解读时参考。开头有判断但明确归属；正文保留行为机制和局部数据；负面结果与 harness 变化不省略。这不是要求所有帖子都写成长文。

Post

```markdown
# **DeepSeek Flash 1017: A Bigger Leap for Agents Than for Reasoning**

In hands-on testing by Zhihu contributor *toyama nao*, DeepSeek Flash 1017 showed more consistent coding across technology stacks, while difficult reasoning tasks saw smaller gains. The testing harness also changed, so the results do not isolate the model update's contribution.

**Better coding, fewer wasted steps**

On familiar frontend tasks, Flash increasingly separates implementation from validation instead of repeatedly switching between testing and patching. One animation task took just **20% of the previous version's steps**, largely through more efficient validation.

The gains are smaller outside frontend development. Its visual design also transfers better across stacks, though crowded layouts and rough details still need cleanup before production.

**Better inspection, but uneven efficiency**

More frequent screenshot checks and automated scripts help catch overlapping UI elements, texture issues and other previously missed details.

Strong instruction following makes detailed specifications useful. But the model can still spend too much effort polishing things that barely matter.

**Fewer hallucinations, not a reasoning breakthrough**

Tasks requiring close attention to details show fewer hallucinations, sometimes using half as many tokens or less.

Tasks demanding extensive exploration and reflection tell a different story: token use can rise **30-40% without better scores**. The author sees greater promise in more reliable work with long documents than in a fundamentally higher reasoning ceiling.

One testing caveat: this round used **DeepSeek Harness 0.2.1 in standard mode**; September's tests did not. The comparison therefore includes a harness change, not just a model update.
```

Comment

```markdown
Original Zhihu answer:
https://www.zhihu.com/question/2094773240036061683/answer/2094921111226136015

Test methodology and full leaderboard:
https://zhuanlan.zhihu.com/p/2088618441074909185
```

## 示例二：系统工程技术史

特点：省略逐版本日志，但保留架构变化的原因。没有把异步调度、策略陈旧、教师监督混为一个概念。约 225 词，4 个信息块，展示技术稿可以选择主线而不堆所有特性。

Post

```markdown
# **Why veRL Had to Rebuild Its RL Stack**

A synchronized PPO loop cannot efficiently handle thousands of agents that pause for tools and finish at different times. That shift helps explain veRL's repeated redesigns.

Zhihu contributor *万理的探求者* traces the engineering logic behind them.

**GRPO moved the bottleneck to generation**

HybridFlow separated algorithm orchestration from distributed model execution. GRPO removed the separately trained critic, but required multiple responses per prompt. Rollout throughput and balancing variable-length sequences became central concerns.

**AgentLoop made sessions independent**

An agent rollout is more than one generate call. AgentLoop manages tool calls, observations and stopping conditions, while inference servers handle token generation and dynamic batching.

Sessions can progress independently instead of waiting for the slowest tool call.

**Async RL made policy versions matter**

Model Engine unified training interfaces across backends. TransferQueue separated data movement from trainer control, while the V1 Trainer consolidated synchronous and asynchronous execution.

Overlapping sampling and training improves utilization, but produces stale trajectories. The system must track policy versions, control how far samples lag behind and synchronize weights efficiently.

**OPD added feedback beyond final rewards**

A failed coding task may return only zero reward. On-policy distillation adds token-level teacher guidance on trajectories the student actually generates, alongside task rewards.

The larger change: veRL is evolving from a PPO training loop into infrastructure for continuously running, learning agents.
```

Comment

```markdown
Source: 万理的探求者 on Zhihu (in Chinese)
https://zhuanlan.zhihu.com/p/2093791385761626099

veRL:
https://github.com/verl-project/verl
```

这两篇是单篇技术解读的参考，不是默认篇幅目标。用户要求详细技术版时，应按 SKILL.md 补回必要机制、条件与限制；简单来源应选择更短形式。

## 示例三：Thread，首帖独立有用且保留限定

合成来源：测试员甲比较新旧模型。新版在多个编程任务中更稳定；一个动画任务的步骤数为旧版的 20%，但 harness 同时从 1.0 换到 2.0。复杂推理任务 token 增加 30–40%，得分未提高。没有公开链接。首帖提供一个真实信息单元，后续展开其他观察；没有机械拆句或重复提问。

Post 1

```markdown
In one animation task, Zhihu contributor *测试员甲* found that a new model used 20% of the previous version's steps.

The harness also changed from 1.0 to 2.0, so the result does not isolate the model's contribution. Fewer steps alone do not establish a speedup.
```

Post 2

```markdown
Across the author's coding tasks, the new model behaved more consistently. The author sees it as more useful for day-to-day project delivery.

These are observations from the author's tasks, rather than an industry-wide ranking.
```

Post 3

```markdown
Harder reasoning tasks showed a different pattern: token use rose 30–40% without higher scores. The author did not see a comparable improvement in complex reasoning.

When evaluating an agent update, how do you separate model gains from changes to the harness?
```

Comment

```markdown
Source: the author-provided document.
```

## 钩子边界：学习结构，不照搬断言

- 来源只解释 Super 表示上层时，不能写 `isn't actually smarter`。可围绕来源支持的管理层设计开场，不额外判断智能水平。
- 来源只有个人求职经历时，不能写 `Most PhDs think rejection means they're not good enough`。没有群体调查或博士身份，就写作者实际做过的复盘。
- 不把 `What is your biggest pain with AI?` 当通用结尾。围绕具体经验可问 `When an agent moves to a new task, what context do you most often have to repeat?`，前提是正文确实讨论该问题。
- 无问句的短帖与技术解读同样合格；不要把示例问题复制到无关文章。
