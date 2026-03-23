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
  domain TEXT,
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
