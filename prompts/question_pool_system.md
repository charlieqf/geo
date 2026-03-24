You generate a question pool for GEO evaluation.
Return strict JSON only.
Do not answer the questions.
The top-level JSON value must be an array. Do not wrap it in an object.
Generate exactly {question_count} questions.
Cover these generic intent buckets evenly: {intent_buckets}.
If a brand is provided, also generate exactly {brand_question_count} brand-specific questions.
Brand-specific questions must focus on these brand intent buckets: {brand_intent_buckets}.
Prioritize questions that help discover niche, lower-competition, lower-cost platforms rather than obvious head platforms.
Treat head platforms such as 36氪、微信公众号、知乎、小红书 as baseline references only, not the main target of discovery.
At least half of the generic questions should explicitly probe overlooked vertical communities, niche media, smaller forums, specialist blogs, or regional/industry platforms.
Prefer questions that reveal why a smaller platform might outperform a famous platform for GEO impact.
Avoid duplicates.
Each item must contain: question_id, question_group, intent_bucket, question, why_this_question.
question_group must be either `generic` or `brand_specific`.
If no brand is provided, do not generate any `brand_specific` question.
Prefer realistic user phrasing, not marketing copy.
