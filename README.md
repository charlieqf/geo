# GEO Weight Distiller

Local-first discovery and analysis demo for GEO site selection.

## Current scope

- Qwen is the target model under test.
- OpenAI is the analysis layer for prompt generation and structured extraction.
- Raw responses are stored as JSON.
- Structured experiment data is stored in SQLite.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest tests/unit/test_config.py tests/integration/test_schema_init.py tests/unit/test_prompt_registry.py -q
```
