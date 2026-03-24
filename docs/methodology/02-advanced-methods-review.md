# 已搜集先进方法整理

## 1. 资料来源

本轮整理基于两类资料：

### 已下载论文

- `docs/research/safe-2505.12621.pdf`
- `docs/research/source-attribution-rag-2507.04480.pdf`

### 已检索的 GitHub / 工具线索

- `google/langextract`
- `john-kurkowski/tldextract`
- `adbar/courlan`
- `moj-analytical-services/splink`
- `dedupeio/dedupe`
- `zjunlp/OneKE`

## 2. SAFE

### 核心思想

SAFE 的重点不是“回答完之后再补引文”，而是在生成阶段就做句子级 attribution：

- 先判断某一句话需要几个支持来源
- 再把这句话绑定到具体支撑句或支撑文档片段

### 对我们最有价值的点

- 非常适合处理“claim 是否有证据”这个问题
- 比“整段回答打一个 source score”更细
- 可以把“有支撑”和“无支撑”显式区分开

### 对当前系统的意义

SAFE 最适合补当前系统的短板：

- 现在我们能抽 topic、claim、domain
- 但还不能稳定证明“某一句话到底是被哪段来源支撑的”

所以 SAFE 更像一个“证据绑定层”的方法论来源。

## 3. Source Attribution in RAG

### 核心思想

这篇方法更关注文档级 attribution：

- 某个最终回答到底受哪些检索文档影响
- 每篇文档的贡献度有多大

它讨论了：

- Shapley-style attribution
- Kernel SHAP 等近似方法
- ContextCite 等更实用的近似路径

### 对我们最有价值的点

- 适合解释“哪些来源真正推动了最终结论”
- 适合做 offline attribution，而不是直接做实时产品链路

### 对当前系统的意义

它不太适合作为当前系统的在线主流程，但非常适合作为：

- 评估层
- 调试层
- 检查 retrieval / source weighting 是否合理的离线分析层

## 4. google/langextract

### 核心能力

- LLM 驱动的结构化抽取
- 输出带 source span grounding
- 强调 extraction 结果的可审阅性

### 为什么和本系统高度相关

我们当前已经有：

- answer -> structured JSON
- topic / claim / domain

但缺的是：

- 更严格的 source grounding
- 更稳定的 span-level extraction

`langextract` 是目前最适合直接嵌入本系统的“结构化抽取增强件”。

## 5. tldextract

### 核心能力

- 基于 Public Suffix List 做域名拆分
- 解决复杂子域名 / 后缀问题

### 为什么相关

当前系统里 domain normalization 已经修过几轮，但还是会有边界问题，例如：

- 子域名污染
- suffix 判断不稳
- 同站点不同 host 聚合不准

`tldextract` 是最容易接入、收益很明确的工程增强项。

## 6. courlan

### 核心能力

- URL 清洗
- URL 规范化
- 去 tracking 参数
- URL 过滤与采样

### 为什么相关

当前系统的 URL 提取和清洗主要是自写启发式逻辑。`courlan` 能明显提升：

- URL cleanliness
- source quality
- domain aggregation 的稳定性

## 7. Splink / dedupe

### 核心能力

- 结构化实体归并
- fuzzy matching
- record linkage

### 为什么目前不是最高优先级

它们适合在以下阶段再上：

- 来源规模更大
- 服务商别名 / 平台别名越来越多
- 需要跨 run 做 canonical entity 归并

对当前系统来说，它们不是最关键的短板。

## 8. OneKE

### 核心能力

- schema-guided IE
- 多任务、多模态信息抽取
- 适合构建结构化知识库或知识图谱

### 为什么当前不宜直接接入

它更像一个完整的抽取系统，不是小组件。

当前系统的主任务是：

- 问题蒸馏
- 回答采样
- 平台发掘
- 小平台排序

OneKE 更适合未来扩展成“供应商图谱 / 平台图谱 / 证据图谱”时再引入。

## 9. 按与当前系统的适配度排序

### 第一梯队：短期可整合，收益直接

1. `google/langextract`
2. `tldextract`
3. `courlan`

### 第二梯队：适合作为中期增强

4. `SAFE` 的句子级 attribution 思路
5. `Source Attribution in RAG` 的文档贡献度分析

### 第三梯队：后续扩展再考虑

6. `Splink`
7. `dedupe`
8. `OneKE`

## 10. 对当前系统的建议栈

### 短期建议

- 输入清洗层：`courlan + tldextract`
- 结构化证据层：`langextract`
- 产品理念层：借鉴 `SAFE` 的 claim-level grounding 思路

### 中期建议

- 用 `Source Attribution in RAG` 的思路做离线 attribution 分析
- 让系统能回答“是哪些来源推动了这个平台上榜”

### 暂不建议进入主链路

- `Splink`
- `dedupe`
- `OneKE`

## 11. 结论

如果只考虑“最能增强当前系统的先进方法”，优先级应当是：

1. `langextract`：增强结构化抽取与 source grounding
2. `tldextract + courlan`：增强 URL / domain / source hygiene
3. `SAFE`：作为 claim-level attribution 的设计原则
4. `Source Attribution in RAG`：作为离线评估与解释层

最不该做的，是直接把复杂 attribution 或大型 IE 框架整套搬进当前产品主链路。当前更正确的方向是“先补证据层，再补解释层，最后补复杂 attribution”。
