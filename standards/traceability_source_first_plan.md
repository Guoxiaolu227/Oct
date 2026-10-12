# 来源优先的 Rubric 与 Mechanism 追溯计划

状态：未来工作计划

版本：`traceability-plan-v0.1`

更新时间：2026-10-09

## 1. 核心原则

当前的 5 个 rubric 和 25 个 failure mechanism 只是初始候选假设，不是已经被 guideline 或科学方法学资料证明的最终标准。

未来的正确流程应当是：

```text
guideline / 方法学资料
→ 原始评审标准和 failure mechanism
→ rubric 与 mechanism 归并
→ 与当前候选清单比较
→ 保留、合并、拆分、删除或新增
```

因此，当前文件中的 rubric、mechanism 和 synthetic example 只能作为工作起点，不能直接作为最终 Agent 的事实标准。

## 2. 当前状态

当前已经存在的相关文件包括：

```text
rubrics_v0.1.json
failure_mechanisms_v0.1.jsonl
examples_v0.1.jsonl
source_matrix.csv
```

它们当前的定位如下：

- `rubrics_v0.1.json`：初始候选 rubric；
- `failure_mechanisms_v0.1.jsonl`：初始候选 failure mechanism；
- `examples_v0.1.jsonl`：结构草稿，其中的 synthetic examples 不是专家 gold；
- `source_matrix.csv`：已有来源线索和资料目录；
- 当前的 `source_ids` 只是来源线索，不代表已经完成严格的章节级、段落级或论证级追溯；
- 当前版本不能直接被视为最终 Agent 标准。

## 3. 未来的来源优先流程

### 第一步：独立阅读 guideline，抽取原始评审标准

先从公开会议、期刊和行业 reviewer guideline 中记录原始 criterion、评分问题、评分锚点、来源位置和短摘录。

这一阶段应尽量独立于当前的 5 个 rubric，避免为了证明已有分类而选择性抽取资料。

### 第二步：阅读科学方法学资料，抽取 failure mechanism

从数据泄漏、统计不确定性、采样偏差、可复现性、实验设计、因果推断等方法学资料中抽取：

- 失败发生的条件；
- 被违反的科学标准；
- 可以在论文中观察到的信号；
- 从失败到结论失效的因果链；
- 不构成问题的反例或边界条件；
- 来源的章节、页码或段落定位。

### 第三步：从来源抽取结果归并 rubric

将来源中的原始 criterion 按科学论证链归并成较稳定的顶层 rubric。

当前的 5 个 rubric 可以作为比较对象，但不应被预设为最终结果。来源审计后允许：

- 保留当前 rubric；
- 合并两个当前 rubric；
- 将一个当前 rubric 拆分为多个维度；
- 删除来源无法支持且区分度不足的 rubric；
- 新增来源中明确出现、但当前体系没有覆盖的 rubric。

### 第四步：把来源机制与当前候选机制进行对照

当前 25 个 mechanism 只作为候选清单。每个候选机制需要与来源抽取结果进行比较，并记录最终决策。

允许的决策包括：

```text
keep
merge
split
revise
drop
new_source_derived
```

明确禁止：

```text
为了给现有 mechanism 找出处而强行挂上不相关文献。
```

如果当前机制找不到真正相关的 guideline 或方法学资料，应记录为 unsupported 或 unresolved，而不是伪造支持关系。

## 4. 三类来源的不同作用

### Guideline

规定审稿人应该检查什么，以及哪些方面会影响审稿评价。

例如：

```text
论文的主要 claim 是否由方法和实验充分支持？
实验是否足够严谨？
贡献是否具有意义和新颖性？
```

### Scientific methodology

解释为什么某种失败会破坏科学结论，以及这种失败通常通过什么机制产生影响。

例如：

```text
测试集参与调参
→ 测试集信息进入模型开发
→ 测试结果出现乐观偏差
→ 泛化结论可信度下降
```

### Expert review

展示真实审稿人在具体论文中如何发现、描述和评价一个问题。

三类资料不能相互替代：

- guideline 不能单独证明具体论文确实存在某个 failure；
- methodology 不能直接代表专家在真实论文中的表达方式；
- expert review 也不能代替系统的方法学解释。

## 5. 未来需要新增的文件

后续来源优先审计可以新增以下文件：

```text
source_derived_criteria_v0.1.jsonl
source_derived_mechanisms_v0.1.jsonl
candidate_audit_matrix_v0.1.csv
traceability_edges_v0.1.jsonl
traceability_map.drawio
traceability_map.mmd
```

文件用途如下：

- `source_derived_criteria_v0.1.jsonl`：保存从 guideline 原文独立抽取的评审标准；
- `source_derived_mechanisms_v0.1.jsonl`：保存从方法学资料抽取的 failure mechanism；
- `candidate_audit_matrix_v0.1.csv`：对照来源抽取结果与当前候选 rubric/mechanism；
- `traceability_edges_v0.1.jsonl`：保存 mechanism 与来源之间的具体关系；
- `traceability_map.drawio`：可编辑的来源、机制和 rubric 关系图；
- `traceability_map.mmd`：可版本管理的 Mermaid 图源。

## 6. 正式来源关系的记录要求

每条正式来源关系最终应至少包含：

```text
mechanism_id
source_id
source_role
source_locator
short_excerpt
mapping_rationale
relation_strength
verification_status
```

其中：

```text
source_role = guideline | methodology
relation_strength = direct | supporting | contextual
```

每个来源关系都应能够回答：

```text
来源是哪份资料？
位于哪个章节、页码或段落？
原文具体说了什么？
为什么能支持这个 mechanism？
这个关系是否经过核验？
```

`relation_strength` 的含义：

- `direct`：来源明确讨论了该问题或标准；
- `supporting`：来源没有使用完全相同的名称，但明确支持该方法学原则；
- `contextual`：只能提供背景，不能单独证明该机制。

## 7. 专家 review example 的后续处理

本阶段暂不系统补充真实专家 review example。

当前 synthetic example 继续标记为：

```text
source_type = synthetic_draft
verification_status = draft_not_gold
```

不能把 synthetic example 当成真实专家证据，也不能用 synthetic example 证明某个 mechanism 合理。

未来收集真实专家 review example 时，应单独记录：

```text
paper_id
review_id
review_source
review_location
original_review_text
paper_evidence_chunk_ids
human_verification_status
```

## 8. 未来正式审计的验收方向

正式审计不要求当前 25 个机制全部被强行保留，而要求：

```text
所有候选 rubric 和 mechanism 都完成 source audit
来源抽取出的标准和机制都有来源定位
保留、合并、拆分、删除和新增都有明确理由
没有把 unsupported candidate 当成最终 truth
```

最终报告应统计：

```text
保留数量
合并数量
拆分数量
删除数量
新增数量
尚未解决数量
同时有 guideline 和 methodology 支持的数量
只有 guideline 支持的数量
只有 methodology 支持的数量
```

## 9. 本次不做的内容

本计划文件只记录未来工作，不立即执行来源审计。因此本次不做：

- 不重新修改当前 5 个 rubric；
- 不重新修改当前 25 个 mechanism；
- 不立即补齐所有来源关系；
- 不系统寻找真实专家 review example；
- 不建立正式 JSON Schema；
- 不运行 5 篇论文 pilot；
- 不生成最终 rubric 或 mechanism 版本。

后续正式版本应在来源优先审计完成后，从：

```text
rubrics_v0.1
failure_mechanisms_v0.1
```

升级为：

```text
rubrics_v0.2
failure_mechanisms_v0.2
```

并保留 v0.1，确保标准演化过程可追溯。
