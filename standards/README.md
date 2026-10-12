# Weakness Reviewer 标准 v0.1

本目录是本周的第一版标准资产，不是最终 gold 数据集。

## 当前完成内容

- `rubrics_v0.1.json`：5 个固定顶层 rubric。
- `failure_mechanisms_v0.1.jsonl`：每个 rubric 5 个，共 25 个候选 failure mechanism。
- `examples_v0.1.jsonl`：先为 5 个机制写了正例和 non-issue 反例，共 10 条；它们明确标记为 `synthetic_draft`，目前不能当作人工 gold。
- `source_matrix.csv`：记录公开 reviewer guideline、方法学论文和 review 数据源。
- `rubric_mechanism_map.drawio`：可在 diagrams.net/draw.io 中编辑的图。
- `rubric_mechanism_map.mmd`：可在 Mermaid 编辑器、VS Code 或 Obsidian 中编辑的图源。

## 本周使用方式

1. 先看 `rubrics_v0.1.json`，确认 5 个顶层维度是否符合你的研究范围。
2. 再看 `failure_mechanisms_v0.1.jsonl`，每次修改只改一个 mechanism，并升级版本号。
3. 用公开专家 review 或论文原文替换 `examples_v0.1.jsonl` 中的 synthetic draft。
4. 下一步再建立 `weakness.schema.v0.1.json`，目前示例已经约定字段，但还没有把 schema 作为正式输出约束。

## 缺失型证据的规则

缺失型证据不能写成“论文没有说明”就结束。必须同时记录：

- `expected_item`：本来应该说明什么；
- `searched_sections`：搜索了哪些章节、附录或 artifact；
- `searched_chunk_ids`：实际检索了哪些 chunk；
- `why_expected`：为什么这项信息对当前 claim 必要；
- `status`：只能先写 `suspected_missing`，人工核查后才改为 `verified_missing`。

Agent 没找到信息，不等于论文没有信息。

## 可视化工具建议

### 首选：diagrams.net / draw.io

打开 `rubric_mechanism_map.drawio`，可以直接拖动节点、改颜色、增加机制和连接关系。它适合你当前的“rubric → mechanism → evidence”结构，也能导出 SVG、PNG、PDF 或 PPT 使用。

### 轻量版本：Mermaid

打开 `rubric_mechanism_map.mmd`，修改文本就能改变图。适合记录版本、放进 Markdown、Git 或论文草稿。可使用 Mermaid Live Editor、VS Code Mermaid 插件或 Obsidian 预览。

### 后续数据量变大：Gephi

当一个 weakness 同时属于多个 rubric，或者 mechanism、evidence、example 形成多对多关系时，再考虑把 JSONL 导入 Gephi。现在不需要引入 Gephi，因为它对 25 个机制来说偏重。

## 版本规则

如果只是改错别字，不升级版本；如果修改 rubric 定义、mechanism 的适用范围或 non-issue 条件，就从 `v0.1` 升级为 `v0.2`，避免后续实验无法追溯。
