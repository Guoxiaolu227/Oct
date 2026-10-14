# GPT-5.6-Luna Assessment 与人工 Weakness 对照报告

## 1. 对照范围与口径

本报告比较 Luna 在两篇已完成论文上生成的 11 条 assessment，与 `sea_selected` 中的
人工 review weaknesses。第三篇 `I1quoTXZzc` 因预注册 token 门控未启动，不纳入 Luna
人工对照，也不以 DeepSeek 旧结果代替。

分类沿用 DeepSeek 对照报告：

- **直接相符且证据有效**：对象、失效路径和后果与人工一致，且确定性契约通过；
- **语义直接相符但证据失败**：机器抓到人工的具体问题，但 quote/位置契约失败；
- **历史相符但当前已补充**：人工指出的是早期版本问题，当前 MMD 已补充；
- **部分相符**：同一实验区域存在交集，但具体机制或因果结论不同；
- **无直接对应**：人工 weakness 没有支持机器的具体问题；
- **合理 `not_applicable`**：人工没有要求该机制，机器也正确说明不适用。

人工 review 不是完备真值；“无直接对应”不等于机器一定错误。另一方面，本轮只有一条
assessment 通过确定性校验，因此不能用模型 Verifier 的 11 次 accept 代替证据有效性。

## 2. 总体映射

| 类别 | Luna | DeepSeek（同两篇） | 解释 |
|---|---:|---:|---|
| 直接相符且证据有效 | 0 | 2 | Luna 没有同时满足人工一致与证据契约的条目 |
| 语义直接相符但证据失败 | 3 | 1 | Luna 找到更多人工主题，但无法交付合格引用 |
| 历史相符但当前已补充 | 0 | 0 | 两篇没有明确版本修复案例 |
| 部分相符 | 5 | 5 | 两模型都产生较多主题交集但因果链不同的条目 |
| 无直接对应 | 2 | 2 | 主要是 evaluation reuse 等机器新增假设 |
| 合理 `not_applicable` | 1 | 1 | 两模型均正确识别评价曲线不要求组件消融 |

Luna 的主题覆盖并不差：它直接触及 DreamGaussian 的评测样本、速度比较和 text-to-3D
评价不足。但这些对应项全部确定性无效。DeepSeek 在同两篇中至少有两条既与人工直接
相符、又通过证据契约。因此当前证据只支持“Luna 提出了更多相关候选”，不能支持
“Luna 更好地复现人工 weakness”。

## 3. `2CxkRDMIG4`

人工评审的 R3 相关重点是：仅四个小数据集、数据并不高度不平衡、没有系统改变不平衡
率、缺少 F1 和 local reject option、以及 PRC/RRC 与标准 precision-recall curve 的
关系不清楚。

| Luna ID | 机制 | 人工对应 | 判断 |
|---|---|---|---|
| `574aedc9` | FM-R3-01 | 人工没有提出 fold 内预处理、模型选择或阈值泄漏 | 无直接对应 |
| `4004c0c9` | FM-R3-02 | 人工批评数据集小、覆盖不足；Luna 更具体地追问医疗样本来源和 split unit | 部分相符 |
| `c2fd5dd4` | FM-R3-03 | 人工认为比较和基线不充分；Luna 关注外部 ARC 与当前协议是否一致 | 部分相符 |
| `c6f0f19a` | FM-R3-04 | 人工质疑 rejection 下 precision/recall 行为、F1 和标准 PR curve；Luna 关注 accepted-set recall 分母 | 部分相符 |
| `04bc964c` | FM-R3-05 | 人工没有要求模型组件消融；论文贡献是评价曲线 | 合理 `not_applicable` |

本篇没有 Luna 的直接人工命中。它没有复现 DeepSeek 曾经提出的 F1 缺失，而是生成了
更窄的 conditional recall 问题。这个问题可能有独立方法学价值，但人工并未提出相同
因果链，而且 Luna 的 evidence package 无效。

DeepSeek 在本篇的优势是：其 Sampling/Split assessment 直接覆盖“四个小数据集能否
支撑宽泛结论”，并通过确定性校验；Luna 将问题收窄到医疗数据的患者、机构和划分单位，
使其与人工评价只剩部分重合。

## 4. `UyNXMqnN3c`

人工评审的 R3 相关重点包括：15 个输入的用户研究统计信息有限、资源和复杂度披露不足、
text-to-3D 结果与比较较弱、annealing 在 text-to-3D 上缺少对应实验，以及 texture
refinement 和多阶段后处理缺少充分对照。

| Luna ID | 机制 | 人工对应 | 判断 |
|---|---|---|---|
| `98450c17` | FM-R3-01 | 人工没有声称评价图参与开发或调参 | 无直接对应；证据有效 |
| `dc5cb8bb` | FM-R3-02 | 人工明确认为 15 个输入使用户研究统计有效性有限；Luna 同时追问 30 个图像的采样框架 | 语义直接相符，但证据失败 |
| `07ce7998` | FM-R3-03 | 人工要求比较披露资源使用、模型复杂度和 pipeline bottleneck；Luna 追问基线硬件和 timing boundary | 语义直接相符，但证据失败 |
| `3f3cac86` | FM-R3-04 | 人工质疑用户研究规模和若干视觉失败，但没有明确提出 CLIP 与 3D 几何的指标错配 | 部分相符 |
| `8833ffb4` | FM-R3-04 | 人工明确说 text-to-3D 结果有限、比较较弱，并要求对应 annealing 实验 | 语义直接相符，但证据失败 |
| `b2d95855` | FM-R3-05 | 人工要求解释 Stage 3、比较 texture refinement，并质疑多步后处理；Luna要求组件隔离 | 部分相符 |

`8833ffb4` 是 Luna 相对 DeepSeek 最有价值的新增候选。它把论文同时声称 image-to-3D
和 text-to-3D fidelity，与只有 image-to-3D 量化指标的评价结构连接起来，和人工
“text-to-3D 比较弱”高度一致。但是该条至少一个引用定位失败，当前不能计为有效命中。

`07ce7998` 也比 DeepSeek 的宽泛 baseline fairness 问题更贴近人工资源披露意见。它
注意到论文提供统一 V100 声明和分阶段时间，因此没有确认硬件不公平，而是要求说明各
baseline 的 timing boundary。科学状态保持谨慎，但证据契约仍失败。

## 5. DeepSeek 与 Luna 的人机一致性差异

两模型在主题上存在稳定交集：

- 都关注 DreamGaussian 的小规模评价样本；
- 都关注速度/质量 baseline 的协议可比性；
- 都认为 CLIP 不能覆盖全部 3D 质量维度；
- 都正确判定 PRC/RRC 论文的组件消融机制不适用。

差异主要在状态和证据：

1. DeepSeek 更常输出 `insufficient_evidence`，其 Verifier 会 downgrade 或 reject；
2. Luna 更常输出 `reporting_gap`，并由同模型 Verifier 全部接受；
3. Luna 新增了 text-to-3D 无量化指标和 accepted-set recall 两个较具体的问题；
4. Luna 的 10/11 assessment 级证据失败，使新增覆盖无法转换为可信 finding；
5. DeepSeek 同两篇有两条直接、证据有效的人工匹配；Luna 为零。

这说明“是否想到人工问题”和“是否形成可复核 assessment”必须分别评价。若只看主题，
Luna 的覆盖有吸引力；若执行当前科研证据合同，DeepSeek 在这两篇上更可靠。但样本只有
两篇，且两次均是单次随机运行，不能据此形成模型优劣结论。

## 6. 对下一步实验的含义

本轮最先需要修复的不是 Prompt 内容，而是 verifier precedence：

1. `deterministic_valid=false` 时，不再调用模型 Verifier，或无条件把最终状态设为
   `insufficient_evidence`；
2. 模型 Verifier 只能评估 entailment、反证和状态强度，不能推翻本地 quote/位置校验；
3. 统计同时报告 topical human overlap 和 evidence-valid human match；
4. 把 `8833ffb4`、`07ce7998` 和 `c6f0f19a` 保留为回归案例，检查证据 resolver 修复后
   是否能获得有效引用；
5. 继续将 `98450c17` 视为“证据合规但人工未覆盖”的候选，交由独立标注者判断，而不是
   自动计为 false positive。

第三篇没有运行，因此 RandInt、外部 ProbCBM、class accuracy 和已补充消融等案例没有
Luna 结果。不得根据 DeepSeek 的旧输出推测 Luna 在这些问题上的表现。
