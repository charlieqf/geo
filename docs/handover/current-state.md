# 当前系统交接说明

## 1. 当前产品定位

这个系统当前的主价值不是证明头部平台有用，而是把头部平台降为基线参考，然后尽可能稳定地找出：

- 哪些小平台更可能以更低的竞争和成本带来 GEO 影响力机会
- 这些小平台为什么值得做
- 应该怎么进入
- 有哪些风险需要人工复核

对外口径统一按“已上线系统”表达，不再用“demo”字样。

## 2. 最近一轮关键决策

### 2.1 小平台优先

- 结果页已切换为：`niche_opportunities` 为主、`baseline_platforms` 为辅
- 页面展示的黄金集合已切换到 `niche_golden_set`
- `golden_set` 仍保留在 `summary.json` 中作为 legacy 字段，但不再作为主要展示口径

### 2.2 方法学页面口径统一

- `pages/5_方法学说明.py` 现在读取 `docs/methodology/03-system-methodology.md`
- 页面和文档不再使用“Demo”措辞
- 当前目标文风是“产品方法论白皮书”，而不是演示说明或内部 demo 讲解稿

### 2.3 问题生成页 UX 决策

- Prompt 不再放在 popover 里，而是作为 `生成 Prompt` 标签页
- 问题池列表采用页面内固定高度 + 列表内部滚动
- 这块必须使用 `st.html()` 渲染问题卡片，不能回退到 `st.markdown(..., unsafe_allow_html=True)`，否则会出现原始 HTML 泄露到页面正文的问题

### 2.4 运行蒸馏页 UX 决策

- `问题池预览` 必须位于按钮/控制区上方
- `网页基准样本文本文件` 已从页面移除
- 当前页面结构为：
  - 上：问题池预览
  - 下左：运行状态
  - 下右：运行控制 + 运行日志
- 问题池预览必须使用更高的专用高度函数 `distillation_preview_height()`，不要复用普通列表的 `question_table_height()`

### 2.5 最新 20题小平台 run 结论

- 最新已复核 run：`runs/discovery-中国-GEO-服务-2026-03-24T21-44-06+00-00`
- 这一轮已经证明：新问题池确实能在回答正文里逼出更多具体小平台
- 但系统下游抽取/归一化仍然明显低估了这些小平台，导致 `top_actionable_platforms` 仍偏头部平台
- 详细复核文档见：`docs/handover/2026-03-24-20q-run-review.md`

## 3. 最重要的代码入口

### 页面

- `Home.py`
- `pages/2_蒸馏问题生成.py`
- `pages/3_运行蒸馏.py`
- `pages/4_结果分析.py`
- `pages/5_方法学说明.py`

### 核心逻辑

- `src/pipeline/question_generation.py`
- `src/pipeline/discovery_run.py`
- `src/pipeline/answer_preprocess.py`
- `src/pipeline/scoring.py`
- `src/pipeline/golden_set.py`
- `src/platform_registry.py`
- `src/utils/url_utils.py`

### UI / 文案

- `src/ui_helpers.py`
- `src/ui_copy.py`
- `src/ui_presenters.py`

### 方法学与研究

- `docs/methodology/01-current-system-method.md`
- `docs/methodology/02-advanced-methods-review.md`
- `docs/methodology/03-system-methodology.md`

## 4. 当前验证方式

建议优先跑这一组：

```bash
python -m pytest tests/unit/test_platform_registry.py tests/unit/test_scoring.py tests/unit/test_ui_presenters.py tests/unit/test_ui_copy.py tests/unit/test_discovery_pipeline.py tests/unit/test_question_generation.py tests/unit/test_question_prompt_meta.py tests/integration/test_answer_preprocess_pipeline.py
python -m py_compile pages/2_蒸馏问题生成.py pages/3_运行蒸馏.py pages/4_结果分析.py pages/5_方法学说明.py src/platform_registry.py src/pipeline/scoring.py src/pipeline/discovery_run.py src/ui_helpers.py src/ui_copy.py src/ui_presenters.py
```

如果涉及页面布局，建议再做一次 Playwright 烟测，重点看：

- 顶部 Streamlit 工具条是否隐藏
- 页面是否整体滚动
- 列表是否改为内部滚动
- 标签页与标题顺序是否符合当前设计

## 5. 当前遗留问题 / 下一步建议

### 优先级高

- 生成一套真正偏“小平台发现”的新问题池，不要继续沿用旧 8 题问题池
- 按 `docs/handover/2026-03-24-20q-run-review.md` 的顺序修 4 个问题：平台注册表覆盖、actionable_platforms 生成逻辑、域名提取、弱证据降权
- 把 `langextract`、`tldextract`、`courlan` 列为短期集成候选
- 继续降低“抽象平台”如 `论坛`、`博客/专栏` 在中间层中的噪音影响

### 优先级中

- 让 `niche_golden_set` 在页面上显示得更像“建议组合”而不是纯技术字段
- 提高 `运行蒸馏` 页的问题池预览密度和状态感
- 对结果页增加更多“为什么值得做 / 如何进入 / 风险”的解释卡片

### 优先级低

- 离线引入更强 attribution / source contribution 评估
- 做更细的实体归并（如 `Splink` / `dedupe`）

## 6. 继续接手时的建议顺序

1. 先读 `README.md`
2. 再读 `docs/methodology/03-system-methodology.md`
3. 再读这个交接文件
4. 如果要进入代码，优先看页面文件和 `src/pipeline/scoring.py`
5. 如果要继续做产品增强，优先看 `docs/methodology/02-advanced-methods-review.md`

## 7. Git 与仓库状态提醒

- 当前远端仓库：`https://github.com/charlieqf/geo`
- `runs/` 默认不入库
- `docs/research/` 下的论文 PDF 默认不入库
- 如果未来要继续让别的同事接手，建议每次大改完都同步更新：
  - `README.md`
  - `docs/handover/current-state.md`
  - `.claude/skills/geo-system-handoff/SKILL.md`
