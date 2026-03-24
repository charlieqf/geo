# Findings

- SAFE focuses on sentence-level, in-generation attribution for RAG, with a pre-attribution classifier that predicts 0/1/2+ supporting quotes, then runs a matching attributor.
- SAFE's most pragmatic retrieval/matching choices are lightweight: SC1, SC2, BM25, SPLADE, MMR, fuzzy matching. XGBoost on textual features is their preferred pre-attribution classifier.
- The Source Attribution in RAG paper studies document-level attribution via utility functions over retrieved sets, with Shapley as reference and Kernel SHAP / ContextCite as cheaper approximations.
- Kernel SHAP and ContextCite best approximate Shapley in their experiments, but all utility-based methods struggle with redundancy, complementarity, and especially synergy / multi-hop dependencies.
- `langextract` is a grounded structured extraction library with exact character offsets and visualization.
- `tldextract` and `courlan` are URL/domain hygiene tools for crawling and corpus preparation.
- `splink` and `dedupe` are entity-resolution / record-linkage tools; powerful but mostly for metadata/entity cleanup rather than first-pass citation attribution.
- `OneKE` is a schema-guided multi-agent extraction system for entities/relations/events/triples and knowledge-graph construction.
