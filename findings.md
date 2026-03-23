# Findings

## Documents
- `C:\work\code\geo\1.idea.md`
- `C:\work\code\geo\2.plan.md`

## Potential Issues
- The core premise treats model citation outputs as a stable proxy for real-world GEO effectiveness, but citation behavior varies by model, search backend, freshness, region, prompt phrasing, and product configuration.
- Several claims overstate certainty or outcomes, including "80%+ AI引用权重", "10分钟出结果", and ROI / lift predictions without a validated measurement framework.
- The plan assumes search-enabled APIs will reliably return structured source lists, which is product-specific and not guaranteed across ordinary LLM APIs.
- The entropy / independent-contribution method is underspecified and likely invalid: embedding similarity does not equal fact extraction or attributable source contribution.
- Co-citation / PageRank-style correlation is not reliable evidence of mutual verification or business value.
- Set-cover optimization only makes sense after building a trustworthy fact-to-site attribution matrix, which the docs do not define.
- Filtering out large "public sea" sites biases the result and conflicts with the claimed goal of understanding actual model citation behavior.
- Free-tier deployment and the 10-day delivery estimate are optimistic relative to the proposed search, storage, analytics, visualization, and reporting scope.

## Demo-Only Feasibility View
- Step 1 question generation is technically straightforward for a demo.
- Step 2 batch Q&A is also straightforward, but only if the chosen provider exposes either source URLs or machine-readable citations; otherwise the demo must fall back to regex/domain extraction from answer text.
- Domain-frequency charts, simple co-occurrence graphs, and top-site ranking are easy to demo.
- "Information entropy" can only be demoed as a heuristic score unless there is a real fact-extraction and attribution pipeline.
- "Correlation / mutual verification" can be demoed as co-citation strength, but should not be presented as rigorous causality.
- "Minimal site set" can be demoed using greedy coverage over domains or topic clusters, but not as a mathematically trustworthy optimal recommendation.
- ROI uplift, estimated citation gain, and recommendation frequency are not demo-safe unless backed by historical labeled data.

## Open Questions
- Which target AI products are being optimized for: specific APIs, chat products with search, or a broader GEO outcome across multiple engines?
- Is the intended output a sales demo, a directional research prototype, or a decision-grade optimization product for paying customers?

## Deployment Notes
- Initial deployment target is a local Windows PC.
- Future deployment target may be a public Ubuntu VM.
- This favors a cross-platform Python stack, minimal native dependencies, environment-variable configuration, and avoiding Windows-only service/process assumptions.
- For phase 1 demo hosting, Streamlit remains acceptable; for later Ubuntu exposure, add a reverse proxy and process supervisor or containerize the same app.

## Updated Constraints
- No GPU dependency.
- Prefer OpenAI models only.
- Avoid heavy databases; `SQLite` or flat files are acceptable.
- No PDF export.
- The page should visibly present the metric definitions and evaluation logic to signal rigor and professionalism.
- OpenAI serves as the analysis layer, not the measured target engine.
- The measured target engine for phase 1 is Qwen; Doubao can be added later through the same provider adapter pattern.
- Secret handling must use environment variables only; no API keys in source, logs, screenshots, or committed files.

## Prompt Architecture Notes
- Prompts should be first-class configuration objects, visible and editable in the UI.
- Separate prompt families are needed for: question-pool generation, single-answer preprocessing, aggregation analysis, and final narrative reporting.
- Raw scoring should be computed in code from structured records; GPT-5.4 should be used mainly for structured extraction, normalization, clustering hints, and human-readable interpretation.
- The safest pipeline is two-stage: preprocess each answer into structured evidence first, then aggregate across all evidence for site-level scoring.
- Prompt templates should expose variables such as `{keywords}`, `{brand}`, `{intent_buckets}`, `{question_count}`, `{answer_text}`, `{citations}`, `{topic_schema}`, and `{site_summaries}`.
