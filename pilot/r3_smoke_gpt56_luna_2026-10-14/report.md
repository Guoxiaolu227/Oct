# R3 GPT-5.6-Luna 复现实验：Assessment 分析报告

## 1. 实验结果与分析边界

本实验使用 `gpt-5.6-luna`，在 Prompt、五个 Skill、Rubric、Verifier、Schema、
输入论文和执行限制不变的条件下复现 DeepSeek R3 Pilot。正式执行前已提交冻结配置和
协议。三篇计划输入中，前两篇完整执行并通过逐篇工程门控；根据第二篇观察到的
token/字符比，第三篇预计需要 300,265 input tokens，超过预注册的 300,000 门槛，
因此没有启动。

本次是开发集上的模型行为复现。结果可用于分析模型输出、证据契约和成本，不能用于
计算 precision/recall，也不能证明 Luna 或 DeepSeek 更优。

每条 assessment 分三层读取：

1. `assessment_emitted`：Skill 初始状态；
2. `deterministic_valid`：所有引用和位置是否通过确定性契约；
3. 最终状态：模型 Verifier 处理后的 `AuditResult.status`。

这三层在本轮出现明显冲突：Luna 的 11 条 assessment 中只有 1 条
`deterministic_valid=true`，但模型 Verifier 对 11 条全部给出 `accept`，最终状态因而
原样保留。报告将确定性无效的条目视为“不可作为最终 finding 的候选”，即使当前
AuditResult 仍显示 `reporting_gap` 或 `plausible_risk`。

## 2. 执行和成本

| Paper | 请求 | Input tokens | Output tokens | 模型延迟 | Assessment | 确定性无效 |
|---|---:|---:|---:|---:|---:|---:|
| `2CxkRDMIG4` | 10 | 114,184 | 9,617 | 642.34 s | 5 | 5 |
| `UyNXMqnN3c` | 11 | 195,333 | 13,477 | 282.75 s | 6 | 5 |
| `I1quoTXZzc` | 0 | 0 | 0 | 0 | 0 | 0 |
| **合计** | **21** | **309,517** | **23,094** | **925.09 s** | **11** | **10** |

第三篇停止不是 API 失败。第二篇完成后的线性预测为 300,265，超过门槛 265 tokens；
协议要求在付费请求前停止。DeepSeek 当时对第三篇的预测为 284,820，虽允许启动，实际
却使用了 399,295 input tokens。这再次说明 assessment 数量和 Verifier 次数会使简单
字符比例低估成本。

## 3. 输出漏斗与 DeepSeek 对照

在共同完成的前两篇上，两种模型都产生 11 条 assessment，但内部行为差异很大：

| 指标 | DeepSeek | GPT-5.6-Luna | 解释 |
|---|---:|---:|---|
| Verifier 前候选 finding | 3 | 10 | Luna 更倾向输出可报告状态 |
| 确定性无效 assessment | 4 | 10 | Luna 的证据对象稳定性显著更差 |
| Verifier accept | 6 | 11 | Luna Verifier 没有执行任何 downgrade/reject |
| Verifier downgrade / reject | 2 / 3 | 0 / 0 | Luna 缺少保守收敛 |
| 最终 `reporting_gap` | 0 | 8 | 多数没有通过确定性契约 |
| 最终 `plausible_risk` | 0 | 2 | 两条也均为确定性无效 |
| 最终 `insufficient_evidence` | 10 | 0 | 两模型的状态校准方向相反 |
| 最终 `not_applicable` | 1 | 1 | 两者都识别了控制实验不适用案例 |

Luna 相比 DeepSeek 使用了约 4.7% 更多 input tokens、84.4% 更多 output tokens、7.9%
更多总 tokens，记录的模型延迟约为 8.45 倍。输出变长没有改善 assessment 级别的
证据有效率：DeepSeek 前两篇为 7/11，Luna 为 1/11。

因此，本轮不能把“10 个最终 finding”解释为召回提升。更准确的描述是：Luna 产生了
更多、内容更详细的缺陷假设，但 quote/位置错误和全接受式 Verifier 使当前最终状态失去
证据闸门意义。

## 4. `2CxkRDMIG4` 的五条 Assessment

| ID | 机制 | 初始 → 最终 | 确定性 / Verifier | 分析 |
|---|---|---|---|---|
| `574aedc9` | FM-R3-01 | reporting gap → reporting gap | 无效 / accept | 质疑 fold 内训练、预处理和阈值选择是否隔离。假设保持条件式，没有断言泄漏，但至少一个证据对象定位失败。 |
| `4004c0c9` | FM-R3-02 | reporting gap → reporting gap | 无效 / accept | 将医疗数据的采样框架、纳排标准和划分单位连接到患者或机构泛化。方向合理，但证据包未通过。 |
| `c2fd5dd4` | FM-R3-03 | reporting gap → reporting gap | 无效 / accept | 指出当前 PRC/RRC 与外部 ARC 结果可能不在相同 split、预处理和调参协议下。与 DeepSeek 的同机制输出相近，但证据更不稳定。 |
| `c6f0f19a` | FM-R3-04 | plausible risk → plausible risk | 无效 / accept | 指出 RRC 在 accepted subset 内计算 recall，拒绝的正例不进入分母，因而可能与总体 positive-case capture 不一致。这是有价值的新假设，但尚无有效 evidence package。 |
| `04bc964c` | FM-R3-05 | not applicable → not applicable | 无效 / accept | 正确识别论文贡献是评价曲线而非组件归因；语义判断合理，但该 assessment 仍带有确定性错误，说明 `not_applicable` 也需要干净证据。 |

相较 DeepSeek，Luna 保留了同样的 leakage、sampling、baseline 和不适用主题，但把前三者
从 `insufficient_evidence` 改为 `reporting_gap`。这种变化主要反映状态偏好，而不是
证据改善。Metric Alignment 则从 DeepSeek 对 precision/recall/F1 的宽泛疑问，转为
更具体的 conditional recall 分母问题；后者方法学上更尖锐，却仍需有效引用和人工确认。

## 5. `UyNXMqnN3c` 的六条 Assessment

| ID | 机制 | 初始 → 最终 | 确定性 / Verifier | 分析 |
|---|---|---|---|---|
| `98450c17` | FM-R3-01 | reporting gap → reporting gap | **有效 / accept** | 本轮唯一完全通过确定性契约的条目。它指出评测图和用户研究样本是否参与开发或调参未说明，状态保持为报告缺失而非泄漏确认。 |
| `dc5cb8bb` | FM-R3-02 | reporting gap → reporting gap | 无效 / accept | 质疑 30 个图像样本的来源、筛选与代表性；与人工对小样本用户研究的担忧相近，但至少一个 counterevidence 定位失败。 |
| `07ce7998` | FM-R3-03 | reporting gap → reporting gap | 无效 / accept | 质疑十倍加速比较是否统一硬件、实现和 timing boundary。论文提供 V100 和阶段时长等反证，Luna 有讨论但证据包无效。 |
| `3f3cac86` | FM-R3-04 | plausible risk → plausible risk | 无效 / accept | 指出 CLIP reference-view similarity 不能直接测量几何、多视角和纹理质量，并考虑了用户研究；结论比 DeepSeek 更强，但确定性校验失败。 |
| `8833ffb4` | FM-R3-04 | reporting gap → reporting gap | 无效 / accept | 发现 image-to-3D 有量化指标，而 text-to-3D 主要是定性比较；与人工“text-to-3D 比较弱”直接相关，但引用契约失败。 |
| `b2d95855` | FM-R3-05 | reporting gap → reporting gap | 无效 / accept | 认为 Stage 2 同时加入 mesh extraction、初始化和 refinement，整体对比不能隔离各组件贡献；考虑了已有目标函数图，但证据定位失败。 |

Luna 比 DeepSeek 多发现一条独立的 text-to-3D 评价缺失，并将 Stage 2 归因问题描述得更
贴近人工对 texture refinement 和 post-processing 的担忧。与此同时，它把 DeepSeek
已经降级的 CLIP 问题保留为 `plausible_risk`，说明 Luna Verifier 没有形成与生成模型
相互独立的审查倾向。

## 6. 三个典型案例

### 6.1 唯一证据有效的谨慎发现：`98450c17`

该 assessment 绑定到 DreamGaussian 的图像评价与用户研究，提出一个可证伪问题：这些
样本是否与方法设计或超参数选择保持独立。它没有从“论文没写”推导出“发生泄漏”，而是
要求补充开发集与最终评价集的关系。

它的优势是 claim、条件式假设、因果后果和逐字证据均通过契约。局限也很明显：人工
review 并没有提出 evaluation-set reuse，因此它是一个合规的新核查项，而非人工确认的
weakness。

### 6.2 内容有价值但不应通过证据闸门：`3f3cac86`

这一条把 CLIP 指标与 3D 几何、多视角一致性、纹理质量区分开，并主动考虑用户研究和
论文承认的失败模式。科学论证比单纯说“CLIP 不好”更完整。

但是，assessment 的 counterevidence 未通过确定性定位。模型 Verifier 随后声称相关
文本存在并选择 accept，却不能推翻本地确定性校验。当前系统仍把它保留为
`plausible_risk`，暴露了两层 verifier 的优先级错误：模型判断覆盖了机器可判定的证据
失败。研究统计中应将它归为 invalid candidate，而非最终 finding。

### 6.3 语义正确但契约仍失败的弃权：`04bc964c`

控制实验 Skill 正确判断，PRC/RRC 是评价方法贡献，没有模型组件增益归因，因此组件
消融不适用。DeepSeek 对同一机制也给出 `not_applicable`。

Luna 的版本包含无效 counterevidence 元数据，所以 assessment 级 deterministic validity
仍为 false。这个案例说明，正确状态不等于合格输出；即使是弃权，也应能准确说明为何
该机制不适用，并避免生成不存在或错位的反证对象。

## 7. 工程与方法学结论

1. OpenAI-compatible endpoint、`gpt-5.6-luna`、五 Skill、Verifier、trace 和脱敏导出
   在两篇论文上完整闭环，没有请求失败。
2. 预注册成本门控正常工作，并在第三篇付费调用前停止。
3. Luna 比 DeepSeek 更愿意输出 `reporting_gap` 和 `plausible_risk`，也生成更长解释，
   但没有表现出更好的引用可靠性。
4. Luna Verifier 11/11 accept，与 deterministic validity 1/11 严重冲突。当前最终状态
   不能作为可靠 finding funnel。
5. 模型 Verifier 不能覆盖确定性失败；确定性无效 assessment 应在调用 Verifier 前直接
   终止或强制降为 `insufficient_evidence`。
6. 本轮没有出现“Verifier 成功拦截过强判断”的 Luna 案例；这本身是关键结果，而不是
   报告缺项。
7. 第三篇没有运行，任何 Luna 与 DeepSeek 的模型比较都只适用于共同完成的前两篇。
