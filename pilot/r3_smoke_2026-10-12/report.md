# R3 Progressive Pilot 实验报告

## 1. 实验目的与边界

本实验使用真实 DeepSeek API，对三篇 UTF-8 MMD 论文顺序运行 R3
progressive Agent，检查工程闭环、Skill 调用追踪、确定性证据校验、Verifier、
token/延迟观测和脱敏导出。实验协议已在首次 API 调用前提交，执行期间没有修改
输入、Prompt、Skill、模型配置或判定门槛。

本实验没有人工真值，不能据此计算 precision、recall，也不能证明 Skills 优于
baseline。三篇论文已经用于 Prompt/Agent pilot，后续不应再把它们当作未见过的
最终效果测试集。

## 2. 执行结果

| Paper ID | 字符数 | 请求 | Input tokens | Output tokens | 模型延迟 | Assessment | 门控 |
|---|---:|---:|---:|---:|---:|---:|---|
| `2CxkRDMIG4` | 36,387 | 10 | 110,469 | 5,780 | 50.03 s | 5 | 通过 |
| `UyNXMqnN3c` | 54,502 | 11 | 185,286 | 6,743 | 59.44 s | 6 | 通过 |
| `I1quoTXZzc` | 83,780 | 15 | 399,295 | 12,217 | 133.96 s | 10 | token 门控失败 |
| **合计** | **174,669** | **36** | **695,050** | **24,740** | **243.43 s** | **21** | **2/3 全部门控通过** |

三篇 API 运行本身均完成，没有请求失败或重试耗尽。每篇都完整记录了五个 Skill
的 `considered`、`invoked`、资源加载、模型请求、assessment 和终态事件；全部
AuditResult 均通过 Schema 校验，事件序号连续，脱敏导出没有发现 `prompt`、
`content`、`quote` 或 `manuscript` 字段。

第 3 篇在预测阶段为 284,820 input tokens，低于 300,000 的启动门槛，因此按协议
启动；实际产生 10 个 assessment 和满额 15 次请求，最终达到 399,295 input
tokens。该运行没有发出第 16 次请求，但超过冻结的总 input-token 门槛，因此实验
总体状态记为 `completed_with_gate_failure`，不事后修改阈值。

## 3. 输出漏斗

21 个最终 assessment 的状态为：

- `confirmed_flaw`: 1
- `insufficient_evidence`: 19
- `not_applicable`: 1

确定性校验发现 9 个 assessment 无效；Verifier 最终给出 10 次 accept、3 次
downgrade 和 8 次 reject。唯一保留的 `confirmed_flaw` 来自长论文的
`FM-R3-03`，这里只能说明它通过了当前机器契约和 Verifier，不能在没有人工复核
的情况下断言该问题在科学上为真。

Skill 初始输出中共有 8 个 finding 状态，但多数在确定性校验或 Verifier 后变成
`insufficient_evidence`。这表明防止无证据指控的防线确实生效，同时也暴露出当前
模型在逐字引用、行号或因果链契约上的通过率偏低。

## 4. 按 Skill 的资源消耗

| Skill | 请求 | Input tokens | Output tokens | 模型延迟 | Verifier 前候选 finding |
|---|---:|---:|---:|---:|---:|
| Data leakage | 6 | 108,903 | 3,019 | 38.75 s | 0 |
| Sampling/split | 8 | 161,603 | 4,831 | 47.93 s | 0 |
| Baseline fairness | 8 | 162,030 | 5,274 | 53.20 s | 2 |
| Metric alignment | 8 | 153,287 | 7,536 | 66.77 s | 4 |
| Control/ablation | 6 | 109,227 | 4,080 | 36.77 s | 2 |

Metric alignment 产生最多候选 finding 和最多输出 token；长论文中的 baseline 与
sampling Skill 各产生三个 assessment，使 Verifier 调用数和输入成本明显增加。
成本并不只由论文长度决定，还受每个 Skill 返回的 assessment 数量影响。

## 5. 工程结论

1. 真实 DeepSeek API、五 Skill、Verifier、逐字引用校验、私有运行存储和 telemetry
   导出可以完整闭环运行。
2. 15 次请求硬上限有效：最长论文正好达到 15 次，没有发生第 16 次调用。
3. 仅按字符数线性预测 token 不够可靠，因为 Verifier 次数随 assessment 数量变化。
4. 当前最终输出非常保守：21 个 assessment 中只有 1 个保留为 confirmed flaw。
5. `trace_summary.finding_count` 统计的是 `assessment_emitted` 时的 Verifier 前状态，
   不能直接当作最终 finding 数量；最终统计必须以 AuditResult 为准。
6. 本次只证明工程可运行并揭示成本与契约问题，不构成效果证据。

## 6. 后续建议

- 在下一轮优先分析 9 个确定性无效 assessment 的失败原因，区分引用文本、行号、
  claim 绑定和因果链问题。
- 在实验 Runner 中同时报告 candidate finding 和 final finding，避免观测口径混淆。
- 为单个 Skill 增加 assessment 数量上限，或在调用 Verifier 前进行确定性预筛选，
  降低长论文成本。
- 真正比较 general review、checklist 与 Skills 前，另选未参与开发的论文并建立独立
  人工标注与仲裁协议。

原始 AuditResult、引文、Prompt 和模型响应保存在本机 ignored 的
`Agent/runs/private/<review_run_id>/`；本目录仅保存脱敏统计与事件。
