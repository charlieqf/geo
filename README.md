# GEO Weight Distiller

本仓库是一个本地优先的 GEO 平台发现与权重分析系统，围绕“批量问题蒸馏 -> 多变体回答采样 -> 结构化证据提取 -> 平台评分 -> 小平台机会排序”这条主链路构建。

## 当前系统范围

- 目标回答引擎：豆包
- 分析与结构化层：OpenAI
- 运行产物：按 run 写入 `runs/` 下的 JSON 文件
- 结果重点：`baseline_platforms`、`niche_opportunities`、`niche_golden_set`
- 对外口径：这是已上线系统，不再使用“demo”表述

## 页面结构

- `Home.py`：系统首页
- `pages/2_蒸馏问题生成.py`：生成问题池与查看问题池生成 Prompt
- `pages/3_运行蒸馏.py`：顶部问题池预览，下方运行状态 / 运行控制
- `pages/4_结果分析.py`：小平台机会榜、头部基线平台、小平台黄金集合、回答追踪
- `pages/5_方法学说明.py`：读取 `docs/methodology/03-system-methodology.md`

## 必读文档

- `docs/handover/current-state.md`：当前系统状态、最近关键决策、接手建议
- `docs/methodology/01-current-system-method.md`：当前系统方法梳理
- `docs/methodology/02-advanced-methods-review.md`：先进方法与工具综述
- `docs/methodology/03-system-methodology.md`：对外统一口径的方法学白皮书

## 本地技能

- `.claude/skills/geo-system-handoff/SKILL.md`

这个本地 skill 用来帮助后续接手者快速理解：

- 当前产品定位
- 关键页面与代码入口
- 最近 UI / 方法学 / 小平台逻辑的关键决策
- 修改前后的验证方式

## 快速启动

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```

## 快速验证

```bash
python -m pytest tests/unit/test_platform_registry.py tests/unit/test_scoring.py tests/unit/test_ui_presenters.py tests/unit/test_ui_copy.py tests/unit/test_discovery_pipeline.py tests/unit/test_question_generation.py tests/unit/test_question_prompt_meta.py tests/integration/test_answer_preprocess_pipeline.py
python -m py_compile pages/2_蒸馏问题生成.py pages/3_运行蒸馏.py pages/4_结果分析.py pages/5_方法学说明.py src/platform_registry.py src/pipeline/scoring.py src/pipeline/discovery_run.py src/ui_helpers.py src/ui_copy.py src/ui_presenters.py
```

## 备注

- `docs/research/` 下的论文 PDF 当前未纳入版本控制
- `runs/` 目录默认忽略，不会随 Git 提交
- 如果继续做产品化增强，优先看 `docs/methodology/02-advanced-methods-review.md` 里对 `langextract`、`tldextract`、`courlan`、SAFE、Source Attribution in RAG 的建议顺序
