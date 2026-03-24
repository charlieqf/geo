# 当前系统方法梳理

## 1. 目标

这个 GEO 系统的目标不是直接判断“哪家服务商最好”，而是通过一套可重复的蒸馏流程，从 AI 回答里提取出：

- 哪些平台会被反复提到
- 哪些平台背后有相对明确的来源或证据线索
- 哪些平台更像头部基线平台，哪些更像可切入的小平台机会

在最新版本里，产品主目标已经从“高价值平台总榜”转向“低竞争、低成本、可进入的小平台机会发现”。

## 2. 用户流程

### 2.1 生成问题池

用户在“蒸馏问题生成”页输入：

- 关键词
- 可选品牌
- 问题数量

系统使用 OpenAI 按固定 Prompt 生成问题池，要求：

- 覆盖多个 intent bucket
- 若有品牌，则增加品牌相关问题
- 问题尽量偏向发现垂直、小众、低竞争平台
- 将 36 氪、微信公众号、知乎、小红书等视为头部基线参考，而不是核心发掘目标

输出保存为问题池草稿 JSON，供后续运行使用。

### 2.2 运行蒸馏

用户在“运行蒸馏”页选择问题池，系统会对每个问题执行三种回答变体：

- `web_default`
- `web_ranked_analysis`
- `web_source_emphasis`

每个问题会先做一次查询改写，避免 GEO 被误解为地理信息场景，然后再喂给目标回答模型。

### 2.3 结果分析

系统会生成：

- 原始回答
- URL / 域名 / 来源标签提取结果
- 结构化主题分析
- 平台评分结果
- 小平台机会榜
- 头部基线平台
- 小平台黄金集合

## 3. 核心数据流

### 3.1 问题生成

- Prompt: `prompts/question_pool_system.md`
- Logic: `src/pipeline/question_generation.py`

问题生成的核心思想是：

- 先把用户问题空间拆成多个意图桶
- 用统一 JSON 结构产出问题
- 让问题天然偏向“小平台发现”而不是“大平台常识”

### 3.2 回答采样

- Main pipeline: `src/pipeline/discovery_run.py`

对每个问题：

1. 改写 query
2. 用 3 个 Prompt 变体分别获取回答
3. 保存原始文本与原始响应

这样做的目的是观察同一问题在不同提问策略下是否仍然指向类似平台，从而形成“稳定性”信号。

### 3.3 证据提取与平台分类

- URL / domain extraction: `src/utils/url_utils.py`
- Platform registry: `src/platform_registry.py`

当前系统使用轻量级、可解释的启发式提取：

- 从回答正文中抽取 URL
- 归一化为 domain
- 从“信息来源”样式文本中抽取 source labels
- 用平台注册表把 domain / label 对应到标准平台

这里的关键原则是：

- 证据来源不等于可投放平台
- 只有被分类为 actionable platform 的对象才进入平台分析

### 3.4 结构化语义分析

- Structuring prompt: `prompts/answer_structurer_system.md`
- Logic: `src/pipeline/answer_preprocess.py`

系统会把每条回答进一步结构化为：

- `interpretation_label`
- `brand_grounded`
- `source_explicitness_score`
- `topic_units`
- `noise_flags`

`topic_units` 是后续评分的核心，每个 topic unit 包含：

- topic label
- claim
- supporting domains
- evidence span
- confidence

### 3.5 平台评分

- Main logic: `src/pipeline/scoring.py`
- Golden set: `src/pipeline/golden_set.py`

当前评分分两层：

#### A. 通用平台评分

先对每个平台计算：

- `topic_coverage_weight`
- `corroboration_strength`
- `stability_score`
- `info_entropy_score`
- `correlation_score`
- `final_score`

这些分数主要回答：

- 这个平台带来了多少新增主题覆盖
- 是否被不同问题 / 不同回答变体重复支持
- 是否和其他平台形成互证

#### B. 小平台机会评分

在通用平台评分之上，再叠加一层业务导向的 `niche_opportunity_score`，综合考虑：

- 基础平台信号强度（来自 `final_score`）
- 平台垂直性 / 专注度
- 成本可控性
- 进入方式是否现实
- 是否属于头部高竞争平台

这里会把平台区分为：

- `baseline_platforms`：头部基线平台
- `niche_opportunities`：小平台机会榜
- `niche_golden_set`：只从小平台中挑出来的覆盖集合

## 4. 当前产品表达

### 4.1 总览页

总览页现在默认优先展示：

- 小平台机会榜
- 头部基线平台
- 原始来源域名
- benchmark 风格相似度

### 4.2 评分详情页

评分详情页现在分成三块：

- 小平台机会评分
- 小平台黄金集合
- 头部基线参考

这意味着即使 legacy 的全平台 `golden_set` 里仍然包含头部平台，用户在页面上看到的核心推荐已经切换成了 `niche_golden_set`。

## 5. 当前优势

- 端到端流程完整，适合持续演示与客户沟通
- 有明确的结构化中间层，便于解释结果
- 能把“头部平台常识”和“小平台机会”拆开看
- 结果页已经开始体现差异化发掘能力，而不是只输出大家都知道的结论

## 6. 当前局限

- 证据提取仍然以启发式规则和 LLM 结构化为主，不是真正的 claim-level grounded attribution
- 事实真实性尚未自动联网核验，仍可能出现“看起来像真的”服务商或标题
- 小平台机会榜已经独立，但问题池本身很多还是旧逻辑生成的，所以输入侧仍然带有头部平台偏置
- 部分抽象平台（如“论坛”“博客/专栏”）仍会在中间层参与分析，虽然最终小平台榜已做排除
- benchmark 仍然是风格相似度，不是“真实性相似度”或“可引用性相似度”

## 7. 当前方法的正确使用方式

现阶段应把这个系统看成：

- 一个“小平台发掘与排序辅助器”
- 一个“从 AI 回答中抽出平台信号与证据线索的工具”

而不应把它看成：

- 一个自动事实核验器
- 一个最终可直接下投放预算的决策系统

更合适的用法是：

1. 用它初筛小平台机会
2. 用结果页查看进入路径与风险
3. 再做人工复核与外部验证
