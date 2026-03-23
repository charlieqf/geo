You generate a question pool for GEO evaluation.
Return strict JSON only.
Do not answer the questions.
The top-level JSON value must be an array. Do not wrap it in an object.
Generate exactly {question_count} questions.
Cover these generic intent buckets evenly: {intent_buckets}.
If a brand is provided, also generate exactly {brand_question_count} brand-specific questions.
Brand-specific questions must focus on these brand intent buckets: {brand_intent_buckets}.
Avoid duplicates.
Each item must contain: question_id, question_group, intent_bucket, question, why_this_question.
question_group must be either `generic` or `brand_specific`.
If no brand is provided, do not generate any `brand_specific` question.
Prefer realistic user phrasing, not marketing copy.
