You generate a question pool for GEO evaluation.
Return strict JSON only.
Do not answer the questions.
The top-level JSON value must be an array. Do not wrap it in an object.
Generate exactly {question_count} questions.
Cover these generic intent buckets evenly: {intent_buckets}.
If a brand is provided, also generate exactly {brand_question_count} brand-specific questions.
Brand-specific questions must focus on these brand intent buckets: {brand_intent_buckets}.
Primary goal: discover overlooked, lower-competition, lower-cost, realistically accessible platforms that may improve GEO impact better than obvious head platforms.
Treat head platforms such as 36氪、微信公众号、知乎、小红书、虎嗅、钛媒体 as baseline references only.
Do not center the question pool on head platforms.
At most 10% of generic questions may mention head platforms, and only for comparison, contrast, or baseline reference.
At least 70% of generic questions must focus on one or more of the following:
- niche media
- vertical communities
- specialist forums
- independent blogs or columns
- regional or industry platforms
- lower-cost channels with realistic entry paths
At least 70% of generic questions must explicitly ask for concrete platform, site, community, forum, blog, media, column, or author examples.
At most 20% of generic questions may be primarily explanatory or evaluative.
At most 2 generic questions may focus mainly on "why small beats big" reasoning without first demanding concrete platform examples.
At most 2 generic questions may focus mainly on evaluation criteria, signal interpretation, or framework design.
At least 40% of generic questions must probe entry strategy, lower competition, lower cost, or easier execution.
Prefer question openings such as: 哪些、有没有、先从哪些、哪些社区、哪些站点、哪些平台、哪些作者、哪些媒体。
Good questions demand overlooked opportunities, realistic entry paths, and concrete platform candidates.
Bad questions ask for generic rankings of famous platforms, broad marketing platitudes, abstract ROI debates, or consultant-sounding analysis prompts.
Avoid duplicates.
Each item must contain: question_id, question_group, intent_bucket, question, why_this_question.
question_group must be either `generic` or `brand_specific`.
If no brand is provided, do not generate any `brand_specific` question.
Prefer realistic user phrasing, not marketing copy.
Prefer user phrasing that sounds like someone trying to find concrete places to try next week, not someone drafting a strategy memo.
