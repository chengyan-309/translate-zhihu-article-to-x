# 成稿示例

首次在新对话执行本 skill 时读取，用于校准语气、信息密度和可复制格式。以下是历史任务的风格样本，不是新文章的事实来源，也不是对模型表现或版本历史的独立背书。新任务必须完整读取自己的指定原文。

学习结构和取舍，不复制标题、开头句式、数字、观点或作者身份。不要把每篇都写成“某个维度大跃进，另一个维度没变”。

## 示例一：模型评测

特点：开头有判断但明确归属；正文保留行为机制和局部数据；负面结果与 harness 变化不省略。约 250 词，3 个信息块。

Post

```markdown
# **DeepSeek Flash 1017: A Bigger Leap for Agents Than for Reasoning**

DeepSeek's biggest gain is in getting work done, not solving harder reasoning problems. In hands-on testing, Zhihu contributor *toyama nao* ranks Flash 1017 ahead of Kimi K3 overall, with more consistent coding performance across technology stacks.

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

这两篇是默认密度的参考，不是要求所有技术文章都只有 240 词。用户要求详细技术版时，应按 SKILL.md 补回必要机制、条件与限制。
