# GEO Weight Distiller Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在本地 Windows PC 上构建一个可演示的 GEO 权重蒸馏机 demo：以 `Doubao` 作为唯一被测回答引擎、以 `OpenAI / GPT-5.4` 作为分析引擎，输出问题池、Doubao 回答、结构化证据、网站信息熵、网站相关性、黄金集合推荐，并在页面上展示和编辑全部 Prompt 及方法学说明。

**Architecture:** 使用多页 `Streamlit` 应用承载整个流程。`OpenAI` 负责问题池生成、单条回答结构化预处理、主题归一、最终说明文案；`Doubao` 负责唯一的被测回答链路。所有原始响应保存为 `JSON`，所有结构化结果和实验索引保存到 `SQLite`。最终分数由代码计算，不由 LLM 直接决定。

**Tech Stack:** Python 3.11, Streamlit, OpenAI Python SDK, SQLite, Plotly, NetworkX, Pydantic, pytest, python-dotenv.

---

## 1. 约束与非目标

### 1.1 固定约束

- 本地先运行在 `Windows PC`
- 后续迁移到公网 `Ubuntu VM`
- 不依赖 `GPU`
- 不使用重数据库；只允许 `SQLite` 或平面文件
- 不做 `PDF 导出`
- `Doubao` 是唯一被测对象；`OpenAI / GPT-5.4` 是分析工具，不是被测引擎
- Prompt 必须在页面中可展示、可编辑、可保存版本
- 页面必须显式展示指标定义与方法学，体现专业性
- 真实优化目标以豆包网页/产品侧搜索问答表现为准，Doubao API 需要通过“网页行为仿真”方式尽量逼近该产品行为

### 1.2 第一版非目标

- 不再把 `Qwen` 作为主动开发或主动验证目标；若保留相关代码，仅作为历史兼容路径
- 不做多租户、登录、权限系统
- 不做付费、订阅、任务队列
- 不做 ROI 预测、AI 引用提升百分比承诺、宣传频率承诺
- 不做真实搜索引擎或浏览器抓取

## 1.3 开发前探索性实验（新增）

在正式开发主流程前，先做一个小型 discovery run，用于反向校准 Prompt、来源提取逻辑和结构化 schema。

固定探索关键词：`中国 GEO 服务`

探索目标：

- 看问题池是否足够自然、多样、可覆盖真实决策意图
- 看 Doubao 回答里是否稳定出现显式来源、URL、域名或可推断出处
- 看回答更像“推荐榜单”“泛泛建议”还是“可抽取结构化主题”的分析文本
- 看哪些 Prompt 变体更容易引出来源、案例、对比理由
- 评估单条结构化预处理 Prompt 是否需要加入更强约束
- 评估主题归一时是否需要先做噪声过滤

推荐探索规模：

- 问题数：`18-24`
- 意图桶：`5`
- Doubao Prompt 变体：`3`
- 重复采样：`1`

探索产出：

- 一个真实的实验 run
- 一份 Prompt 优化结论
- 一份来源提取风险清单
- 一份结构化 schema 修订建议

该 discovery run 不以业务结果为目标，而以“帮助正式开发定 Prompt 和定 schema”为目标。

---

## 2. 核心定义

### 2.0 关键澄清：我们要找的不是“所有来源网站”，而是“可投放信息平台”

本产品里的“信息来源”必须按业务含义理解为：

- 客户可以发文宣传、做品牌露出、沉淀内容、影响 AI 可见语料的 `信息平台`

而不是：

- 任意被模型提到的网站
- 云厂商官网
- 服务提供商自己的产品站点
- 基础设施文档或无运营价值的参考站

因此系统必须显式区分：

- `evidence source`：模型回答中出现的来源线索
- `actionable publish platform`：客户真正可以经营内容的目标平台

最终 `信息熵 / 相关性 / 黄金集合` 的评分对象，应该是 `actionable publish platform`，不是所有原始来源域名。

### 2.1 产品叙事层名词

- `信息熵`：面向页面和客户展示的概念名词
- `相关性`：面向页面和客户展示的概念名词
- `黄金集合`：面向页面和客户展示的最小站点组合

### 2.2 底层实现定义

- `边际贡献 MC`：某信息平台相对当前已选平台集合，新增了多少高价值主题覆盖
- `互证强度 VS`：某信息平台支持的主题中，有多少被其他独立信息平台共同支撑
- `稳定性 ST`：某信息平台在不同问题桶、不同被测 Prompt 变体、不同重复采样中是否稳定出现

### 2.3 评分公式

```text
MC(s | S) = 平台 s 相对当前已选集合 S 的新增主题簇覆盖权重
VS(s)     = 平台 s 的主题簇中，被其他独立信息平台共同支持的权重占比
ST(s)     = 平台 s 在多提示词 / 多轮采样 / 多意图桶中的稳定出现率

信息熵(s | S) = MC(s | S) * (0.7 + 0.3 * ST(s))
相关性(s)     = VS(s)     * (0.7 + 0.3 * ST(s))
最终得分      = 0.6 * 信息熵 + 0.4 * 相关性
```

### 2.4 黄金集合算法

使用贪心覆盖，不做假装严谨的最优解宣传：

1. 初始化已覆盖主题集合 `Covered = {}`
2. 每轮选择对 `Covered` 贡献 `最终边际得分` 最高的信息平台
3. 将其新增主题加入 `Covered`
4. 达到目标覆盖率（默认 `>= 0.85`）后停止

---

## 3. 系统总架构

## 3.1 总流程

```text
关键词输入
  -> OpenAI 生成问题池
  -> Doubao API 按“网页行为仿真 Prompt 栈”逐条回答
  -> 原始回答保存 JSON
  -> OpenAI 对单条回答做结构化预处理
  -> OpenAI 对全量主题做归一化
  -> Python 代码聚合并计算信息熵 / 相关性 / 黄金集合
  -> OpenAI 生成解释文案
  -> Streamlit 页面展示结果、Prompt、方法学和证据链
```

## 3.2 为什么采用“两段式分析”

不要把所有 Doubao 原始回答一次性丢给 `GPT-5.4` 做最终判断。正确做法是：

- 第一步：逐条回答转结构化 JSON
- 第二步：汇总结构化 JSON，再由代码做聚合计算
- 第三步：只把聚合结果和证据交给 `GPT-5.4` 生成解释文案

好处：

- 单条失败可单独重试
- 结构清晰，便于追溯
- 分数由代码产生，可解释、可复现
- UI 可展示中间层，体现专业性

## 3.3 网页行为仿真模式

不采用浏览器自动化，也不把“粘贴网页回答”作为主方案。

第一版的核心策略是：

- 以豆包网页/产品侧的真实输出作为 benchmark 样本
- 通过 `Doubao API + surrogate prompt stack` 去逼近网页产品行为
- 逆向的不是“精确隐藏 system prompt 文本”，而是“网页产品的可观测行为模式”

网页行为仿真 Prompt 栈建议拆成三层：

1. `Query Rewriter`：把用户问题改写成网页产品更可能理解的查询形式
2. `Behavior System Prompt`：强制模型按网页产品的知识边界、术语理解、来源呈现方式回答
3. `Answer Formatter`：控制输出结构，使其更像网页产品的“盘点 + 来源痕迹 + 选型建议”

进入统一后处理流水线：

- 来源提取
- 单条结构化预处理
- 主题归一
- 信息熵 / 相关性 / 黄金集合

注意：

- 不应宣称“成功逆向出豆包网页产品的真实 system prompt”
- 应宣称“构建了高相似度的网页行为仿真 Prompt 栈”

---

## 4. Prompt 体系设计

Prompt 必须是系统的一等公民。所有 Prompt：

- 作为文件保存在 `prompts/`
- 在 UI 的 `Prompt Lab` 页面可见、可编辑
- 每次运行时保存快照到 `SQLite.prompt_snapshots`
- 支持恢复默认值

## 4.1 Prompt 家族

### A. 问题池生成 Prompt

用途：让 `OpenAI` 基于关键词和品牌背景，生成可覆盖多种用户意图的问题池。

输入变量：

- `{keywords}`
- `{brand}`
- `{region}`
- `{question_count}`
- `{intent_buckets}`

默认意图桶：

- `direct_recommendation`
- `comparison_choice`
- `risk_avoidance`
- `effect_validation`
- `case_reputation`

### B. 被测 Doubao Prompt 变体

用途：模拟网页产品风格下的不同回答策略，用于稳定性计算。

建议保留 3 个变体：

- `web_default`
- `web_ranked_analysis`
- `web_source_emphasis`

### B1. Query Rewriter Prompt

用途：先将用户问题显式改写为 `生成式引擎优化 / AI 引用优化 / AI 推荐结果` 语境，避免 API 将 `GEO` 误解为地理编码、地理围栏、地图服务等。

### C. 单条回答预处理 Prompt

用途：让 `OpenAI` 把一条 Doubao 回答转成结构化 JSON。

附加要求：必须识别回答属于 `API 模式` 还是 `Web Transcript 模式`，并兼容媒体名、裸域名、来源标签行。

### D. 主题归一 Prompt

用途：将全量 provisional topic 合并成 canonical topic。

### E. 最终解释 Prompt

用途：让 `OpenAI` 基于代码计算结果生成网站解释、方法学说明和黄金集合摘要。

## 4.2 Prompt 默认模板

### 4.2.1 问题池生成 System Prompt

```text
You generate a question pool for GEO evaluation.
Return strict JSON only.
Do not answer the questions.
Cover all provided intent buckets evenly.
Avoid duplicates.
Each item must contain: question_id, intent_bucket, question, why_this_question.
Prefer realistic user phrasing, not marketing copy.
```

### 4.2.2 问题池生成 User Template

```text
Keywords: {keywords}
Brand: {brand}
Region: {region}
Question count: {question_count}
Intent buckets: {intent_buckets}

Generate a balanced JSON array of user questions.
```

### 4.2.3 Query Rewriter 模板

```text
请把下面的用户问题改写成一个更清晰的查询版本。
要求：
1. 如果 GEO 有歧义，明确写成“GEO（Generative Engine Optimization，生成式引擎优化）”
2. 明确问题是在问 AI 搜索 / AI 回答 / AI 引用优化相关服务
3. 保留用户原始商业意图
4. 不要回答问题，只输出改写后的问题

原问题：{question}
```

### 4.2.4 Doubao 被测 Prompt 模板 - web_default

```text
你正在模拟中文 AI 搜索问答产品的回答风格。

这里的 GEO 明确指 Generative Engine Optimization（生成式引擎优化），
不是地理编码、地理围栏、地图服务、GIS 或 Earth Observation。

请直接回答下面的问题，优先给出：
1. 分层盘点或推荐
2. 每家的核心优势/适用场景
3. 尽量给出可核查的来源痕迹（媒体名、网站名、域名、公开案例出处）
4. 如果公开信息不足，请明确说信息不足，不要切换到其他行业解释

问题：{question}
```

### 4.2.5 Doubao 被测 Prompt 模板 - web_ranked_analysis

```text
你正在模拟中文 AI 搜索问答产品的“服务商盘点”回答风格。

这里的 GEO 明确指 Generative Engine Optimization（生成式引擎优化），
不是地理编码、地理围栏、地图服务、GIS 或 Earth Observation。

请按以下结构回答：
1. 第一梯队 / 垂直特色 / 预算友好 等分层
2. 每家服务商写：核心优势、适用客户、来源痕迹
3. 最后给出选型建议和风险提醒
4. 如果证据不足，明确写“公开资料不足”

问题：{question}
```

### 4.2.6 Doubao 被测 Prompt 模板 - web_source_emphasis

```text
你正在模拟中文 AI 搜索问答产品的“来源增强”回答风格。

这里的 GEO 明确指 Generative Engine Optimization（生成式引擎优化），
不是地理编码、地理围栏、地图服务、GIS 或 Earth Observation。

请回答下面的问题，并尽量：
1. 把“来自公开来源的信息”和“归纳判断”分开
2. 能写媒体名就写媒体名，能写网站名就写网站名，能写域名就写域名
3. 如果没有明确来源，不要伪造来源，直接说明“未找到足够公开来源”

问题：{question}
```

### 4.2.6 单条回答预处理 System Prompt

```text
You convert one model answer into strict JSON.
Use only the provided answer text and citation metadata.
Do not score websites.
Do not invent hidden facts.
Extract domains, topic units, claims, and noise flags.
Return strict JSON only.
```

### 4.2.7 单条回答预处理 User Template

```text
Question ID: {question_id}
Intent bucket: {intent_bucket}
Prompt variant: {prompt_variant}
Answer text: {answer_text}
Citations: {citations}
Extracted urls: {extracted_urls}
Extracted source labels: {source_labels}

Return:
{
  "question_id": "...",
  "domains": ["..."],
  "source_labels": ["..."],
  "interpretation_label": "geo_ai_optimization | geo_geocoding | geo_geofencing | geo_earth_observation | unknown",
  "brand_grounded": true,
  "source_explicitness_score": 0.0,
  "topic_units": [
    {
      "topic_label": "...",
      "claim": "...",
      "supporting_domains": ["..."],
      "confidence": 0.0,
      "evidence_span": "..."
    }
  ],
  "noise_flags": {
    "generic_listicle": false,
    "weak_evidence": false,
    "self_reference_only": false
  }
}
```

### 4.2.8 主题归一 System Prompt

```text
You normalize many provisional topic labels into a compact canonical topic taxonomy.
Merge synonyms.
Do not merge clearly different ideas.
Return strict JSON only.
```

### 4.2.9 最终解释 System Prompt

```text
You explain computed GEO site metrics to a professional audience.
Do not recalculate scores.
Use provided metrics and evidence only.
Be precise, concise, and non-hype.
Return markdown sections only.
```

## 4.3 Prompt 展示要求

`Prompt Lab` 页面必须展示：

- Prompt 名称
- System Prompt
- User Template
- 可用变量列表
- 当前默认参数（temperature, max_tokens）
- 最近一次运行时保存的快照版本
- “渲染后预览”功能
- “恢复默认”按钮
- “保存为新版本”按钮

---

## 5. 数据流与处理逻辑

## 5.1 问题池生成

1. 用户输入关键词组、品牌名、目标地区、问题数
2. `OpenAI` 返回结构化问题池 JSON
3. 程序校验 JSON 结构
4. 问题写入 `questions`

注意：问题池不应只有“推荐哪家”这一个桶，必须覆盖不同意图。

## 5.2 Doubao 回答采集

对每个问题：

1. 先用 `Query Rewriter` 改写用户问题
2. 套用 3 个网页行为仿真 Doubao Prompt 变体（默认可配置为 1 或 3）
3. 调用 Doubao OpenAI-compatible 接口
3. 保存原始响应 JSON 到 `runs/{run_id}/raw_answers/`
4. 记录 `answers`
5. 尝试提取 citations / urls / domain mentions

提取优先级：

1. API 返回的结构化 citation
2. 回答文本中的 URL
3. 回答文本中的显式域名
4. 由 `OpenAI` 在单条预处理时做补充识别

## 5.2B 来源分层与平台过滤

所有来源都必须先分类，再决定是否进入评分。

建议分类：

- `publish_platform`：客户可以实际运营内容的平台，如知乎、小红书、新闻媒体站、论坛、博客、公众号、垂直社区、品牌官网
- `official_vendor_site`：服务商自己的官网或产品页
- `infrastructure_site`：云厂商、基础设施、开发平台、文档站
- `reference_only`：只具参考价值但不具投放价值的来源
- `unknown`

评分规则：

- `publish_platform` 进入最终评分
- `official_vendor_site` 只保留作证据，不进入最终黄金集合
- `infrastructure_site` 默认剔除
- `reference_only` 默认降权或剔除

## 5.2A 网页行为校准

为了逼近豆包网页/产品侧行为：

1. 收集少量网页 benchmark 输出样本
2. 将样本中的结构特征抽象成评分维度：
   - 术语理解是否正确
   - 是否出现分层盘点
   - 是否出现来源痕迹
   - 是否出现选型建议与风险提醒
3. 比较不同 surrogate prompt stack 的输出表现
4. 选择最接近网页行为的 prompt 栈作为默认实验模式

## 5.3 单条回答结构化预处理

对每条 `answer`：

1. 将问题信息、Doubao 回答、提取到的 URL/域名输入 `OpenAI`
2. 返回严格 JSON
3. 校验 JSON 结构
4. 落库 `answer_sources` 和 `answer_topic_units`

## 5.4 主题归一

1. 汇总所有 provisional `topic_label`
2. 送给 `OpenAI` 归一成 canonical topics
3. 将映射关系写入 `normalized_topics` 和 `topic_memberships`

## 5.5 代码聚合与评分

1. 构建 `site_topic_support`
2. 计算 `MC / VS / ST`
3. 写入 `site_scores`
4. 使用贪心法生成 `golden_set_items`

## 5.6 最终文案解释

将以下输入给 `OpenAI`：

- Top 网站得分
- 每个网站的新增主题
- 每个网站的互证来源
- 黄金集合结果
- 方法学定义

输出：

- Top 网站解释卡片
- 黄金集合解释
- 局限性说明

---

## 6. SQLite 数据库设计

原则：

- 原始长文本和原始响应走 `JSON`
- 结构化和可聚合的数据进入 `SQLite`
- 不使用 ORM，直接 `sqlite3` + 小型 repository 封装

## 6.1 表清单

### `runs`

记录一次完整实验。

### `prompt_snapshots`

记录某次实验实际使用的 prompt 快照。

### `questions`

记录问题池。

### `answers`

记录每个问题在每个 Doubao Prompt 变体下的回答元数据。

增加字段：采集模式（当前默认 `api_emulated_web`）。

### `answer_sources`

记录单条回答提取出的域名 / URL / 来源类型，并完成“是否属于可投放信息平台”的判定。

### `answer_topic_units`

记录单条回答预处理得到的 provisional 主题单元。

### `normalized_topics`

记录 canonical topic。

### `topic_memberships`

记录 provisional topic 到 canonical topic 的映射关系。

### `site_topic_support`

记录每个候选信息平台对每个 canonical topic 的支持强度。

### `site_scores`

记录每个候选信息平台的 MC / VS / ST / 信息熵 / 相关性 / 最终得分。

### `golden_set_items`

记录黄金集合的贪心选站结果。

## 6.2 建表 SQL

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS runs (
  id TEXT PRIMARY KEY,
  keyword_input TEXT NOT NULL,
  brand_name TEXT,
  region TEXT,
  target_provider TEXT NOT NULL,
  target_model TEXT NOT NULL,
  analysis_provider TEXT NOT NULL,
  analysis_model TEXT NOT NULL,
  target_coverage REAL NOT NULL DEFAULT 0.85,
  question_count INTEGER NOT NULL,
  status TEXT NOT NULL,
  notes TEXT,
  created_at TEXT NOT NULL,
  completed_at TEXT
);

CREATE TABLE IF NOT EXISTS prompt_snapshots (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  prompt_group TEXT NOT NULL,
  prompt_name TEXT NOT NULL,
  version_label TEXT NOT NULL,
  system_prompt TEXT,
  user_template TEXT NOT NULL,
  parameters_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_prompt_snapshots_run_id
  ON prompt_snapshots(run_id);

CREATE TABLE IF NOT EXISTS questions (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  display_order INTEGER NOT NULL,
  intent_bucket TEXT NOT NULL,
  question_text TEXT NOT NULL,
  why_this_question TEXT,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_questions_run_id
  ON questions(run_id);

CREATE TABLE IF NOT EXISTS answers (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  question_id TEXT NOT NULL,
  collection_mode TEXT NOT NULL DEFAULT 'api_emulated_web',
  prompt_variant TEXT NOT NULL,
  target_provider TEXT NOT NULL,
  target_model TEXT NOT NULL,
  answer_text TEXT NOT NULL,
  raw_response_path TEXT NOT NULL,
  extracted_urls_json TEXT,
  latency_ms INTEGER,
  finish_reason TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE,
  FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_answers_run_question
  ON answers(run_id, question_id);

CREATE TABLE IF NOT EXISTS answer_sources (
  id TEXT PRIMARY KEY,
  answer_id TEXT NOT NULL,
  run_id TEXT NOT NULL,
  domain TEXT NOT NULL,
  source_url TEXT,
  source_label TEXT,
  source_type TEXT NOT NULL,
  source_role TEXT NOT NULL DEFAULT 'unknown',
  normalized_platform TEXT,
  is_actionable_platform INTEGER NOT NULL DEFAULT 0,
  occurrence_order INTEGER,
  extracted_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (answer_id) REFERENCES answers(id) ON DELETE CASCADE,
  FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_answer_sources_run_domain
  ON answer_sources(run_id, domain);

CREATE TABLE IF NOT EXISTS answer_topic_units (
  id TEXT PRIMARY KEY,
  answer_id TEXT NOT NULL,
  run_id TEXT NOT NULL,
  interpretation_label TEXT NOT NULL DEFAULT 'unknown',
  brand_grounded INTEGER NOT NULL DEFAULT 0,
  source_explicitness_score REAL NOT NULL DEFAULT 0,
  provisional_topic_label TEXT NOT NULL,
  claim_text TEXT NOT NULL,
  evidence_span TEXT,
  supporting_domains_json TEXT NOT NULL,
  confidence REAL NOT NULL,
  generic_listicle INTEGER NOT NULL DEFAULT 0,
  weak_evidence INTEGER NOT NULL DEFAULT 0,
  self_reference_only INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  FOREIGN KEY (answer_id) REFERENCES answers(id) ON DELETE CASCADE,
  FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_answer_topic_units_run_id
  ON answer_topic_units(run_id);

CREATE TABLE IF NOT EXISTS normalized_topics (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  canonical_topic_key TEXT NOT NULL,
  canonical_topic_label TEXT NOT NULL,
  canonical_description TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_normalized_topics_unique
  ON normalized_topics(run_id, canonical_topic_key);

CREATE TABLE IF NOT EXISTS topic_memberships (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  answer_topic_unit_id TEXT NOT NULL,
  normalized_topic_id TEXT NOT NULL,
  mapping_confidence REAL NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE,
  FOREIGN KEY (answer_topic_unit_id) REFERENCES answer_topic_units(id) ON DELETE CASCADE,
  FOREIGN KEY (normalized_topic_id) REFERENCES normalized_topics(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_topic_memberships_run_topic
  ON topic_memberships(run_id, normalized_topic_id);

CREATE TABLE IF NOT EXISTS site_topic_support (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  domain TEXT NOT NULL,
  normalized_topic_id TEXT NOT NULL,
  supporting_answer_count INTEGER NOT NULL,
  supporting_question_count INTEGER NOT NULL,
  intent_bucket_count INTEGER NOT NULL,
  prompt_variant_count INTEGER NOT NULL,
  mean_confidence REAL NOT NULL,
  evidence_examples_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE,
  FOREIGN KEY (normalized_topic_id) REFERENCES normalized_topics(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_site_topic_support_unique
  ON site_topic_support(run_id, domain, normalized_topic_id);

CREATE TABLE IF NOT EXISTS site_scores (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  domain TEXT NOT NULL,
  topic_coverage_weight REAL NOT NULL,
  marginal_contribution REAL NOT NULL,
  corroboration_strength REAL NOT NULL,
  stability_score REAL NOT NULL,
  info_entropy_score REAL NOT NULL,
  correlation_score REAL NOT NULL,
  final_score REAL NOT NULL,
  supporting_topics_json TEXT NOT NULL,
  corroborated_by_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_site_scores_unique
  ON site_scores(run_id, domain);

CREATE TABLE IF NOT EXISTS golden_set_items (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  selection_order INTEGER NOT NULL,
  domain TEXT NOT NULL,
  incremental_coverage REAL NOT NULL,
  cumulative_coverage REAL NOT NULL,
  selected_for_reason_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_golden_set_items_run_id
  ON golden_set_items(run_id, selection_order);
```

注意：当前计划中的 `site_*` 命名是历史残留。真正业务含义应理解为“最终保留的可投放信息平台”。后续实现可视情况重命名为 `platform_*`。

## 6.3 存储策略

- `runs/{run_id}/raw_answers/*.json`：保存每次 Doubao 原始 API 响应
- `runs/{run_id}/analysis/*.json`：保存 OpenAI 结构化 JSON 原始输出
- `SQLite`：保存所有可查询、可聚合、可展示的数据

---

## 7. 文件结构设计

```text
.
├─ Home.py
├─ pages/
│  ├─ 1_Prompt_Lab.py
│  ├─ 2_Run_Experiment.py
│  ├─ 3_Results.py
│  └─ 4_Methodology.py
├─ prompts/
│  ├─ question_pool_system.md
│  ├─ question_pool_user.md
│  ├─ qwen_natural.md
│  ├─ qwen_decision.md
│  ├─ qwen_source_seeking.md
│  ├─ answer_structurer_system.md
│  ├─ answer_structurer_user.md
│  ├─ topic_normalizer_system.md
│  ├─ topic_normalizer_user.md
│  ├─ report_narrator_system.md
│  └─ report_narrator_user.md
├─ src/
│  ├─ config.py
│  ├─ db.py
│  ├─ schema.sql
│  ├─ prompt_registry.py
│  ├─ providers/
│  │  ├─ qwen_client.py
│  │  └─ openai_client.py
│  ├─ pipeline/
│  │  ├─ question_pool.py
│  │  ├─ answer_collection.py
│  │  ├─ answer_preprocess.py
│  │  ├─ topic_normalization.py
│  │  ├─ scoring.py
│  │  └─ golden_set.py
│  ├─ repos/
│  │  ├─ run_repo.py
│  │  ├─ prompt_repo.py
│  │  ├─ question_repo.py
│  │  ├─ answer_repo.py
│  │  └─ result_repo.py
│  ├─ services/
│  │  ├─ run_service.py
│  │  └─ report_service.py
│  └─ utils/
│     ├─ json_io.py
│     ├─ time_utils.py
│     ├─ url_utils.py
│     └─ validation.py
├─ runs/
├─ tests/
│  ├─ unit/
│  │  ├─ test_prompt_registry.py
│  │  ├─ test_url_utils.py
│  │  ├─ test_scoring.py
│  │  └─ test_golden_set.py
│  └─ integration/
│     ├─ test_schema_init.py
│     ├─ test_question_pool_pipeline.py
│     ├─ test_answer_preprocess_pipeline.py
│     └─ test_run_service.py
├─ .env.example
├─ requirements.txt
└─ README.md
```

---

## 8. 视觉风格与页面设计

## 8.1 风格方向

参考页面 `https://www.goldenstand.cn/live-bot/mini2/task/128` 的风格有明显可取之处，但不应原样照搬。

可取之处：

- `暖中性色底色`：比纯白后台更有质感，能降低“廉价数据看板”的感觉
- `衬线标题 + 无衬线正文`：适合强调“研究工具 / 方法论 / 专业判断”
- `轻纸感面板 + 柔和阴影`：能让复杂信息看起来更克制、更可信
- `圆角卡片 + 细边框`：适合实验记录、Prompt 卡片、方法学说明

不足之处：

- 该风格更偏“任务详情页”，数据可视化层次不够强
- 单一暖灰配色不适合承载大量图表状态
- 结果页如果完全沿用该风格，会显得偏静态，缺少“分析仪表盘”的锐度

因此本项目建议采用：`Warm Editorial Research Lab`。

即：

- 外层沿用暖中性、纸感、编辑部式排版
- 内层图表和指标使用更明确的数据色
- 整体气质是“研究所工作台”，不是“黑客屏”也不是“营销落地页”

## 8.2 设计系统

### 字体

- 标题字体：`Newsreader`
- 正文字体：`Manrope`
- 数据/编号/Prompt 版本号：`IBM Plex Mono` 或系统等宽字体

### 色板

```text
背景底色      #f4f2ef
卡片底色      #fbfaf8
正文主色      #1f1c19
辅助文字      #6f6a64
分隔线        #e4dfd8
品牌强调      #8b7355
深强调        #5d5145
数据蓝        #355c7d
数据青        #3f776c
警示橙        #a35d3b
成功橄榄      #6c7a45
```

### 样式原则

- 外层页面保持暖色、留白、柔和阴影
- 数据图表颜色使用 `数据蓝 / 数据青 / 警示橙`，不要只用米色系
- Prompt 编辑器与方法学卡片使用更高对比度，方便阅读长文本
- 表格行高、字重、边框要更偏“研究报告”，避免过度 SaaS 化

## 8.3 页面层级

- `Home`：像研究所封面页，强调方法和流程
- `Prompt Lab`：像实验室控制台，强调可编辑、可版本化
- `Run Experiment`：像采样台，突出过程、进度、当前采集到的域名
- `Results`：像分析报告页，强调网站得分、互证网络、黄金集合
- `Methodology`：像白皮书页，强调公式、定义、局限性

## 8.4 `Home.py`

展示：

- 产品简介
- 流程图
- 当前约束说明（Doubao 被测、OpenAI 分析、无 GPU）
- 最近运行实验列表

## 8.5 `pages/1_Prompt_Lab.py`

展示：

- 所有 Prompt 卡片
- Prompt 编辑器
- 参数编辑器（temperature / max_tokens）
- 变量清单
- 渲染后预览
- 保存新版本

## 8.6 `pages/2_Run_Experiment.py`

输入：

- 关键词组
- 品牌名
- 地区
- 问题数量
- 是否使用 1 / 3 个 Doubao Prompt 变体
- 是否做重复采样

输出：

- 实时进度
- 已完成问题数
- 已抓到的域名数

## 8.7 `pages/3_Results.py`

必须展示：

- Top 网站排行表
- 网站权重分布图
- 互证网络图
- 黄金集合表
- 每个网站的 `Why this site`
- 证据链追溯（问题 -> 回答 -> topic -> 网站）

## 8.8 `pages/4_Methodology.py`

必须展示：

- 信息熵定义
- 相关性定义
- 稳定性定义
- 黄金集合选择逻辑
- 评分公式
- 局限性说明

---

## 9. 关键算法设计

## 9.1 主题权重

对每个 canonical topic `t` 计算主题权重 `W(t)`：

```text
W(t) = 0.5 * 问题覆盖率 + 0.3 * 意图桶覆盖率 + 0.2 * 平均置信度
```

三个值统一归一化到 `0..1`。

## 9.2 边际贡献 MC

```text
MC(s | S) = sum(W(t)) for topics supported by s and not yet covered by S
```

如果某网站支持的主题都已经被已选集合覆盖，则其 MC 下降。

## 9.3 互证强度 VS

对网站 `s` 支持的每个主题 `t`：

- 若还有 `>= 1` 个独立域名支持同一主题，则视为被互证
- 支持域名越多，互证强度越高，但应设置上限，避免大站垄断

```text
topic_corroboration(t, s) = min(1.0, 0.5 + 0.25 * other_supporting_domain_count)

VS(s) = weighted average of topic_corroboration over supported topics
```

## 9.4 稳定性 ST

```text
ST(s) = 0.5 * PromptVariantConsistency
      + 0.3 * IntentBucketBreadth
      + 0.2 * RepeatRunConsistency
```

如果未启用重复运行，则 `RepeatRunConsistency` 取中性值 `0.5`。

## 9.5 黄金集合

每轮选择网站时使用：

```text
MarginalFinal(s | S) = 0.6 * 信息熵(s | S) + 0.4 * 相关性(s)
```

直到 `主题覆盖率 >= target_coverage`。

---

## 10. 实施任务拆解

### Task 0: Discovery Run - `中国 GEO 服务`

**Files:**
- Create: `docs/findings/2026-03-22-qwen-discovery-notes.md`
- Reuse: `prompts/*`
- Reuse: `src/providers/qwen_client.py`
- Reuse: `src/providers/openai_client.py`

**Step 1: 生成探索问题池**

使用 `OpenAI` 为关键词 `中国 GEO 服务` 生成 `18-24` 个问题，覆盖：

- 直接推荐
- 对比选择
- 避坑风险
- 效果验证
- 案例口碑

**Step 2: 运行网页行为仿真采样**

对每个问题先做 Query Rewrite，再使用 3 个网页行为仿真 Doubao Prompt 变体执行回答采样。

**Step 3: 抽样检查来源与文本形态**

手工或代码辅助检查：

- 是否返回 citation
- 是否出现 URL
- 是否出现可规范化域名
- 是否存在明显榜单噪声
- 是否有足够的主题颗粒度

**Step 4: 用 OpenAI 做单条结构化预处理试验**

抽样选取 `6-10` 条回答，验证单条结构化 Prompt 的 JSON 稳定性和 topic 粒度。

**Step 5: 产出 discovery 结论文档**

记录：

- 哪个问题池 Prompt 更有效
- 哪个网页行为仿真 Prompt 变体更接近豆包网页产品行为
- 哪些字段必须进入结构化 schema
- 哪些字段应删除或降级
- 哪些页面说明要提前告诉用户

**Step 6: 将结论反哺正式实现**

根据 discovery 结果再微调：

- `prompts/`
- 单条结构化 schema
- 来源提取优先级
- 方法学页中的局限性说明

### Task 1: 项目脚手架与配置

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `README.md`
- Create: `src/config.py`
- Create: `src/utils/time_utils.py`

**Step 1: 定义依赖清单**

写入 `requirements.txt`：`streamlit`, `openai`, `python-dotenv`, `pydantic`, `plotly`, `networkx`, `pytest`。

**Step 2: 定义环境变量样例**

写入 `.env.example`，包含：

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `QWEN_API_KEY`
- `QWEN_BASE_URL`
- `QWEN_MODEL`
- `APP_DB_PATH`
- `RUNS_DIR`

**Step 3: 编写配置加载器**

在 `src/config.py` 中用 `pydantic` 或 dataclass 做环境变量读取与校验。

**Step 4: 写配置单测**

Create: `tests/unit/test_config.py`

**Step 5: 运行测试**

Run: `pytest tests/unit/test_config.py -q`

Expected: `1 passed`

### Task 2: SQLite 初始化与 Repository 层

**Files:**
- Create: `src/schema.sql`
- Create: `src/db.py`
- Create: `src/repos/run_repo.py`
- Create: `src/repos/prompt_repo.py`
- Create: `src/repos/question_repo.py`
- Create: `src/repos/answer_repo.py`
- Create: `src/repos/result_repo.py`
- Create: `tests/integration/test_schema_init.py`

**Step 1: 写入完整建表 SQL**

使用本计划中的 SQL。

**Step 2: 实现 DB 初始化器**

`src/db.py` 提供：

- `get_connection()`
- `init_db()`
- `row_factory`

**Step 3: 实现最小 repository CRUD**

只实现当前 demo 需要的方法，不做通用 ORM。

**Step 4: 写建库集成测试**

验证表存在、索引存在、外键正常。

**Step 5: 运行测试**

Run: `pytest tests/integration/test_schema_init.py -q`

Expected: `1 passed`

### Task 3: Prompt Registry 与默认 Prompt 文件

**Files:**
- Create all files under `prompts/`
- Create: `src/prompt_registry.py`
- Create: `tests/unit/test_prompt_registry.py`

**Step 1: 新建默认 Prompt 文件**

把本计划中的默认模板拆成 `.md` 文件。

**Step 2: 实现 Prompt Registry**

支持：

- 读取默认 Prompt
- 列出 Prompt 元数据
- 渲染变量
- 保存实验快照到 `prompt_snapshots`

**Step 3: 写单测**

测试 Prompt 渲染、变量校验、缺失 Prompt 报错。

**Step 4: 运行测试**

Run: `pytest tests/unit/test_prompt_registry.py -q`

Expected: `3 passed`

### Task 4: Provider Adapter - Doubao 与 OpenAI

**Files:**
- Create: `src/providers/qwen_client.py`
- Create: `src/providers/openai_client.py`
- Create: `tests/unit/test_provider_payloads.py`

**Step 1: 封装 OpenAI 分析客户端**

用于问题池生成、结构化预处理、主题归一、最终解释。

**Step 2: 封装 Doubao 被测客户端**

基于 OpenAI-compatible API 调用 Doubao。

**Step 3: 统一返回结构**

封装成统一字典，包含：文本、原始响应、延迟、finish_reason。

**Step 4: 写 payload 单测**

验证 base_url、模型名、消息数组构造。

**Step 5: 运行测试**

Run: `pytest tests/unit/test_provider_payloads.py -q`

Expected: `2 passed`

### Task 5: 问题池生成流水线

**Files:**
- Create: `src/pipeline/question_pool.py`
- Create: `tests/integration/test_question_pool_pipeline.py`

**Step 1: 定义问题池 JSON schema**

必须校验字段：`question_id`, `intent_bucket`, `question`, `why_this_question`。

**Step 2: 调用 OpenAI 生成问题池**

失败时自动重试一次；再失败则提示用户修 Prompt。

**Step 3: 将问题写入 `questions`**

**Step 4: 写集成测试（可 mock OpenAI）**

**Step 5: 运行测试**

Run: `pytest tests/integration/test_question_pool_pipeline.py -q`

Expected: `1 passed`

### Task 6: Doubao 回答采集流水线

**Files:**
- Create: `src/pipeline/answer_collection.py`
- Create: `src/utils/json_io.py`
- Create: `src/utils/url_utils.py`
- Create: `tests/unit/test_url_utils.py`

**Step 1: 实现单题单变体调用**

返回标准化 `answer` 结构。

**Step 2: 实现 URL / 域名提取逻辑**

优先读 API citation，其次 regex URL，其次文本域名。

**Step 3: 保存原始 JSON 到 `runs/` 目录**

**Step 4: 将结构化元数据写入 `answers` / `answer_sources`**

**Step 5: 写 URL 工具单测**

Run: `pytest tests/unit/test_url_utils.py -q`

Expected: `3 passed`

### Task 7: 单条回答结构化预处理

**Files:**
- Create: `src/pipeline/answer_preprocess.py`
- Create: `src/utils/validation.py`
- Create: `tests/integration/test_answer_preprocess_pipeline.py`

**Step 1: 定义预处理输出 schema**

字段包括：`domains`, `topic_units`, `noise_flags`。

**Step 2: 调用 OpenAI 进行单条结构化**

严格要求 JSON 输出。

**Step 3: 落库 `answer_topic_units` 与补充 `answer_sources`**

**Step 4: 写集成测试（mock OpenAI）**

**Step 5: 运行测试**

Run: `pytest tests/integration/test_answer_preprocess_pipeline.py -q`

Expected: `1 passed`

### Task 8: 主题归一与聚合表生成

**Files:**
- Create: `src/pipeline/topic_normalization.py`
- Modify: `src/repos/result_repo.py`
- Create: `tests/unit/test_topic_normalization.py`

**Step 1: 汇总 provisional topics**

**Step 2: 调用 OpenAI 归一化**

**Step 3: 写入 `normalized_topics` 和 `topic_memberships`**

**Step 4: 生成 `site_topic_support`**

**Step 5: 写单测**

Run: `pytest tests/unit/test_topic_normalization.py -q`

Expected: `2 passed`

### Task 9: 信息熵、相关性、稳定性与黄金集合

**Files:**
- Create: `src/pipeline/scoring.py`
- Create: `src/pipeline/golden_set.py`
- Create: `tests/unit/test_scoring.py`
- Create: `tests/unit/test_golden_set.py`

**Step 1: 实现 topic 权重计算**

**Step 2: 实现 `MC / VS / ST` 计算**

**Step 3: 实现 `信息熵 / 相关性 / 最终得分`**

**Step 4: 实现贪心黄金集合**

**Step 5: 写单测，覆盖边界条件**

Run: `pytest tests/unit/test_scoring.py tests/unit/test_golden_set.py -q`

Expected: `6 passed`

### Task 10: 报告解释服务

**Files:**
- Create: `src/services/report_service.py`
- Create: `tests/unit/test_report_service.py`

**Step 1: 定义输入载荷**

只传代码算出的结果和证据，不传原始长上下文。

**Step 2: 调用 OpenAI 生成网站说明与黄金集合摘要**

**Step 3: 写单测**

Run: `pytest tests/unit/test_report_service.py -q`

Expected: `1 passed`

### Task 11: Streamlit 页面实现

**Files:**
- Create: `Home.py`
- Create: `pages/1_Prompt_Lab.py`
- Create: `pages/2_Run_Experiment.py`
- Create: `pages/3_Results.py`
- Create: `pages/4_Methodology.py`
- Create: `src/services/run_service.py`
- Create: `tests/integration/test_run_service.py`

**Step 1: 实现 Prompt Lab**

支持查看、编辑、保存 Prompt。

**Step 2: 实现 Run 页面**

支持输入关键词并执行实验。

**Step 3: 实现 Results 页面**

展示图表、表格、证据链。

**Step 4: 实现 Methodology 页面**

直接展示指标定义、公式、局限性。

**Step 5: 写运行服务集成测试**

Run: `pytest tests/integration/test_run_service.py -q`

Expected: `1 passed`

### Task 12: 本地验证与 Ubuntu 迁移准备

**Files:**
- Modify: `README.md`
- Create: `scripts/run_local.ps1`
- Create: `scripts/run_local.sh`
- Create: `scripts/init_db.py`

**Step 1: 写本地启动脚本**

Windows 使用 `PowerShell`，Ubuntu 使用 `bash`。

**Step 2: 写数据库初始化脚本**

**Step 3: 补充 README**

包含本地 Windows 启动与 Ubuntu VM 部署说明。

**Step 4: 手工验证**

Run: `streamlit run Home.py`

Expected: 首页可打开、Prompt Lab 可编辑、可跑通一个小实验。

---

## 11. 测试策略

### 单元测试

- `Prompt 渲染`
- `URL / 域名标准化`
- `评分公式`
- `黄金集合贪心逻辑`

### 集成测试

- `SQLite 建库`
- `问题池生成 -> questions`
- `单条回答预处理 -> answer_topic_units`
- `完整 run_service` 小样本跑通

### 手工验证

使用一个 12 问题、1 个 Prompt 变体的 smoke test：

- 是否能成功生成问题池
- 是否能成功调用 Doubao
- 是否能生成网站排行
- 是否能在 Results 页面看到证据链

---

## 12. 本地 Windows 与 Ubuntu VM 部署方案

## 12.1 Windows 本地

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_db.py
streamlit run Home.py
```

## 12.2 Ubuntu VM

推荐方式：

- 同一代码库
- 同一 `SQLite` 模式
- 用 `systemd` 保活 Streamlit 或用反向代理暴露
- 使用 `nginx` 反代到 Streamlit 端口

后续若需要升级：

- 保持 `src/` 逻辑不动
- 仅增加 `systemd service` 和反向代理

---

## 13. 风险与缓解

### 风险 1：Doubao API 不稳定返回 citation

缓解：

- 优先读取 API metadata
- 次选 regex URL 提取
- 再次选 OpenAI 结构化补抽域名

### 风险 2：LLM 结构化 JSON 格式漂移

缓解：

- 所有 LLM 输出必须经 schema 校验
- 失败则自动重试 1 次
- 再失败则标记该 answer 为待人工检查

### 风险 3：Prompt 改动导致结果不可追溯

缓解：

- 每次 run 必须保存 prompt snapshot
- Results 页面必须显示 prompt version

### 风险 4：SQLite 被写成黑箱缓存

缓解：

- 保持表结构小而清晰
- 原始响应和结构化索引分离

---

## 14. 验收标准

- 能在 `Windows` 本地 CPU 环境跑通
- 一次实验至少能处理 `12-24` 个问题
- Prompt Lab 可以查看和编辑全部 Prompt
- Results 页面能展示：
  - Top 网站得分
  - 信息熵图
  - 相关性网络图
  - 黄金集合
  - 证据链
  - 方法学说明
- 所有结构化中间结果已写入 `SQLite`
- 所有原始响应已保存到 `JSON`
- 不需要 GPU、不需要 PDF、不需要重数据库

---

## 15. 建议的第一批实现顺序

如果只做最小可演示版本，优先顺序如下：

1. `Task 0` Discovery Run - `中国 GEO 服务`
2. `Task 1` 项目脚手架与配置
3. `Task 2` SQLite 初始化与 Repository 层
4. `Task 3` Prompt Registry
5. `Task 4` Provider Adapter
6. `Task 5` 问题池生成
7. `Task 6` 回答采集
8. `Task 7` 单条预处理
9. `Task 9` 评分与黄金集合
10. `Task 11` 页面实现
11. `Task 10` 最终解释服务

`Task 8` 主题归一可以在 `Task 7` 跑通后立即补上。

---

Plan complete and saved to `docs/plans/2026-03-22-geo-weight-distiller-implementation.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
