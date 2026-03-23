# Qwen Discovery Notes - 中国 GEO 服务

- Question count: `4`
- Prompt variants tested: `web_default, web_ranked_analysis, web_source_emphasis`

## Variant Summary

- `web_default`: answers=4, with_urls=0, with_domains=0, with_source_labels=0, avg_web_benchmark_score=0.575
- `web_ranked_analysis`: answers=4, with_urls=4, with_domains=4, with_source_labels=2, avg_web_benchmark_score=0.900
- `web_source_emphasis`: answers=4, with_urls=0, with_domains=0, with_source_labels=1, avg_web_benchmark_score=0.500

## Top Domains

- `cloud.baidu.com`: 3
- `aliyun.com`: 2
- `alibabacloud.com`: 1
- `cloud.tencent.com`: 1
- `liuliangwanjia.com`: 1
- `wezhuiyi.com`: 1
- `xiaoi.com`: 1

## Top Actionable Platforms

- `小红书`: 12
- `知乎`: 12
- `微信公众号`: 10
- `论坛`: 10
- `CSDN`: 9
- `品牌官网`: 5
- `36氪`: 4
- `博客/专栏`: 4
- `SegmentFault`: 3
- `虎嗅`: 3
- `Bilibili`: 1
- `IT之家`: 1
- `V2EX`: 1
- `百度贴吧`: 1

## Initial Assessment

- 这一轮 discovery 已经能稳定让模型单独产出“潜在高价值信息平台”板块，方向上更接近产品真正需要的输出。
- `web_ranked_analysis` 仍是当前最优变体：显式来源最好、网页样本相似度最高、同时最容易产出平台级推荐。
- `web_default` 与 `web_source_emphasis` 都不如“盘点结构 + 信息来源块 + 潜在高价值信息平台 + 风险提醒”的组合有效。
- 当前平台结果已经开始对准真正要找的对象：知乎、小红书、公众号、论坛、科技媒体、博客/专栏，而不再只是云厂商站点。
- 但这些平台更多是模型的“推荐型披露/推断型披露”，不等于模型真实检索日志，因此后处理必须继续区分 `evidence source` 和 `actionable publish platform`。

## What Improved

- `GEO = 生成式引擎优化` 的消歧已经比较稳，不再大面积漂移到 GIS / 地理编码语义。
- 输出开始出现固定的 `信息来源` 板块，便于后续解析。
- 输出开始出现固定的 `潜在高价值信息平台` 板块，且内容明显偏向知乎、小红书、公众号、论坛等可运营平台。
- `web_ranked_analysis` 现在可以同时给出一些显式来源链接和平台建议，适合作为默认实验变体。

## Remaining Gaps

- 真实网页样本里的媒体型来源（如 `IT之家`、`界面新闻`）仍不够丰富。
- `潜在高价值信息平台` 板块带有明显 prompt 引导痕迹，不能直接等同于真实检索来源。
- 对 `流量玩家` 这样的品牌，模型仍经常回到“公开资料不足”，说明品牌 groundedness 还是弱。
- 即使给出来源，也未必能证明来源与对应判断逐点匹配，因此仍需要 `source_explicitness_score` 与来源类型分层。

## Critical Product Clarification

- 当前抽到的 `aliyun.com`、`cloud.baidu.com`、`cloud.tencent.com` 这类站点，虽然属于回答里的来源线索，但不是产品真正要推荐给客户去运营内容的平台。
- 产品真正要找的是：客户应该去哪些信息平台发内容，才更有机会进入 AI 的有效可见语料池。
- 因此后续必须把来源拆成两层：
  - `evidence source`：回答里出现的来源痕迹
  - `actionable publish platform`：客户能实际发文宣传的平台
- 只有 `actionable publish platform` 才应该进入 `信息熵 / 相关性 / 黄金集合` 的最终评分。

## Prompt Revision Recommendations

- 保留 `web_ranked_analysis` 作为当前默认回答变体。
- 继续要求：`至少给出 2-3 条第三方公开来源；如果只有官网信息，也必须明确标注“官网来源”`。
- 把来源块格式再收紧为类似：`[来源类型] 名称 - 链接/域名`，提升解析成功率。
- 在 `潜在高价值信息平台` 板块中，继续显式排除云厂商官网、基础设施站点、开发文档站点。
- 对品牌提及时增加约束：`如果品牌公开资料不足，不要把它写进第一梯队，只能放入“待验证对象”或“公开资料不足”`。

## Schema Revision Suggestions

- Add `source_role` and `is_actionable_platform` to each extracted source/platform signal.
- Add `normalized_platform` so `知乎`、`zhihu.com`、`知乎专栏` 这类信号能归并到统一平台实体。
- Keep `interpretation_label` to detect any future drift back into GIS / geocoding semantics.
- Keep `brand_grounded` and only mark true when the answer ties the brand to at least one explicit source or verifiable claim.
- Add `source_explicitness_score` and use it to downweight vague source lines like `官方介绍页面`.

## Development Implication

- 默认 discovery 与后续评分应从 `web_ranked_analysis` 开始。
- 下一批实现重点应转向：`source block parsing + source type classification + actionable platform extraction + brand groundedness`。
- 不能假设 `有来源` 等于 `来源可靠`，也不能假设 `被推荐的平台` 等于 `真实检索使用的平台`；两者都要分层处理。
