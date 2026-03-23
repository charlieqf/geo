Question ID: {question_id}
Intent bucket: {intent_bucket}
Prompt variant: {prompt_variant}
Answer text: {answer_text}
Citations: {citations}
Extracted urls: {extracted_urls}
Extracted source labels: {source_labels}

Return:
{{
  "question_id": "...",
  "domains": ["..."],
  "source_labels": ["..."],
  "interpretation_label": "geo_ai_optimization | geo_geocoding | geo_geofencing | geo_earth_observation | unknown",
  "brand_grounded": true,
  "source_explicitness_score": 0.0,
  "topic_units": [
    {{
      "topic_label": "...",
      "claim": "...",
      "supporting_domains": ["..."],
      "confidence": 0.0,
      "evidence_span": "..."
    }}
  ],
  "noise_flags": {{
    "generic_listicle": false,
    "weak_evidence": false,
    "self_reference_only": false
  }}
}}
