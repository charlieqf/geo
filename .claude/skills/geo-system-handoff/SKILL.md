---
name: geo-system-handoff
description: Use when resuming work on the GEO Weight Distiller system, onboarding a new teammate, or needing a fast project handoff. Covers current product positioning, key pages, pipeline files, niche-opportunity logic, UI decisions, verification commands, and important docs to read first.
---

# GEO System Handoff

## Purpose

Use this skill when you need to quickly resume work on this repository without rediscovering the current product positioning and recent implementation decisions.

## Read First

1. `README.md`
2. `docs/methodology/03-system-methodology.md`
3. `docs/handover/current-state.md`

## Current Product Positioning

- This is an already-launched internal system, not a demo.
- The core value is finding `niche_opportunities`, not re-proving that head platforms are useful.
- Head platforms are kept as `baseline_platforms`.
- The page-level “golden set” users should see is `niche_golden_set`, not the legacy all-platform `golden_set`.

## Most Important Files

### Pages

- `pages/2_蒸馏问题生成.py`
- `pages/3_运行蒸馏.py`
- `pages/4_结果分析.py`
- `pages/5_方法学说明.py`

### Pipeline

- `src/pipeline/question_generation.py`
- `src/pipeline/discovery_run.py`
- `src/pipeline/answer_preprocess.py`
- `src/pipeline/scoring.py`
- `src/pipeline/golden_set.py`

### Evidence / Platform Classification

- `src/platform_registry.py`
- `src/utils/url_utils.py`

### UI Layer

- `src/ui_helpers.py`
- `src/ui_copy.py`
- `src/ui_presenters.py`

## Critical UI Decisions

### Question Generation Page

- Prompt display is a tab, not a popover.
- The question list must use internal scroll and should not force the whole page to scroll.
- The question list is rendered with `st.html()`. Do not switch it back to `st.markdown(..., unsafe_allow_html=True)` or raw HTML may leak into the visible page.

### Distillation Page

- `问题池预览` belongs above the lower control/status area.
- The page no longer shows the benchmark file input.
- The preview area uses `distillation_preview_height()` and should remain taller than generic list areas.
- Lower layout is split into `运行状态` on the left and `运行控制` on the right.

### Results Page

- `总览` should prioritize `niche_opportunities`.
- `评分详情` should show `小平台机会评分` + `小平台黄金集合` + `头部基线参考`.
- Avoid regressing to a head-platform-first presentation.

### Methodology Page

- `pages/5_方法学说明.py` reads `docs/methodology/03-system-methodology.md`.
- User-facing methodology content should not use “demo” wording.

## Critical Scoring Decisions

- `build_platform_analysis()` now outputs:
  - `platform_scores`
  - `baseline_platforms`
  - `niche_opportunities`
  - `niche_golden_set`
- `niche_opportunity_score` is a business-facing ranking layer on top of the general platform score.
- The legacy `golden_set` remains in `summary.json`, but it is no longer the primary user-facing collection.

## Verification Commands

Run these before saying the system is in a good state:

```bash
python -m pytest tests/unit/test_platform_registry.py tests/unit/test_scoring.py tests/unit/test_ui_presenters.py tests/unit/test_ui_copy.py tests/unit/test_discovery_pipeline.py tests/unit/test_question_generation.py tests/unit/test_question_prompt_meta.py tests/integration/test_answer_preprocess_pipeline.py
python -m py_compile pages/2_蒸馏问题生成.py pages/3_运行蒸馏.py pages/4_结果分析.py pages/5_方法学说明.py src/platform_registry.py src/pipeline/scoring.py src/pipeline/discovery_run.py src/ui_helpers.py src/ui_copy.py src/ui_presenters.py
```

## Recommended Next Work

1. Generate a new question pool explicitly optimized for small-platform discovery.
2. Improve evidence grounding with `langextract`.
3. Improve URL/domain hygiene with `tldextract` and `courlan`.
4. Keep tightening the separation between head-platform baselines and niche opportunities.

## Handoff Rule

If you make a major change to product positioning, methodology wording, or page structure, update all three:

- `README.md`
- `docs/handover/current-state.md`
- `.claude/skills/geo-system-handoff/SKILL.md`
