# UI Overhaul Plan — "Carbon & Slate" Analytical Dark Theme

**目标：** 将 GEO Weight Distiller 的视觉风格从当前暖色浅色方案（米白/棕褐）切换为专业数据科研感的深色主题（Carbon & Slate），强调数据密度与精准感，同时修复各页面存在的间距拥挤、列表未充分利用视口宽高导致的不必要滚动问题。

---

## 视觉规格

### 主题名：Carbon & Slate（精炭石板）

| 用途 | 变量名 | 值 |
|---|---|---|
| 页面底色 | `--bg` | `#0F171A` |
| 卡片/面板表面 | `--panel` | `#162028` |
| 主文字 | `--ink` | `#E2E8F0` |
| 次要文字/标注 | `--muted` | `#64748B` |
| 边框 | `--line` | `#334155` |
| 品牌蓝（核心交互） | `--accent` | `#3B82F6` |
| 深品牌蓝 | `--accent-strong` | `#2563EB` |
| 成功/置信绿 | `--data-green` | `#10B981` |
| 数据蓝（图表辅助） | `--data-blue` | `#38BDF8` |
| 警告/错误 | `--warn` | `#F59E0B` |

### 设计原则
- **圆角：** 统一降至 8px（卡片）/ 6px（输入框），强调精准感而非柔和
- **边框：** 1px 实线 `var(--line)`，不使用模糊毛玻璃（Streamlit iframe 结构下 `backdrop-filter` 兼容性差，改用实色半透明）
- **阴影：** 深色主题下阴影使用 `rgba(0,0,0,0.35)` 而非暖褐色
- **排版：** 沿用 Streamlit 默认字体栈（Inter/系统字体），不引入外部字体依赖
- **宽度：** `max-width` 从 1240px 扩至 1600px（不完全移除，防止超宽屏文字过度拉伸）
- **transitions：** 保持 120ms ease，不增加额外复杂动效

---

## 改动范围

### 第一步：`src/ui_helpers.py`（核心，独立可验证）

重写 `app_css()` 函数中的全部 CSS，要点：

**基础变量与布局**
1. 重定义所有 `:root` 变量为上表深色值
2. `.stApp` 背景改为深色线性渐变：
   ```css
   background: linear-gradient(160deg, #0F1F2A 0%, #0F171A 60%);
   ```
3. `.block-container`：`max-width` 扩至 1600px

**自定义组件**
4. 输入框（`stTextInput` / `stNumberInput`）：深色表面 + 1px `--line` 边框，focus 时 accent 蓝色高亮
5. Tabs：去掉 `border-radius: 999px`，改为 8px 矩形风格，选中态用 3px accent 蓝下划线
6. `.geo-hero`：去掉大圆角，改为左侧 3px `var(--accent)` border-left 作为标识
7. `.geo-card / .geo-kpi / .geo-section-card / .geo-question-card`：统一 `var(--panel)` 背景 + 1px `var(--line)` 边框 + `box-shadow: 0 4px 12px rgba(0,0,0,0.35)`
8. `.geo-question-list-shell` 高度：改用 `clamp()` 替代 magic number，更稳健：
   ```css
   height: clamp(400px, calc(100vh - 16rem), 900px);
   ```
9. 滚动条：细化至 4px，thumb 用 `var(--line)` 色

**状态色**
10. pending → `var(--muted)`，running → `var(--data-blue)`，completed → `var(--data-green)`，error → `var(--warn)`

**Streamlit 原生组件深色覆盖**（必须显式覆盖，否则会出现深色卡片 + 浅色提示框的视觉割裂）
11. `st.info / st.success / st.warning / st.error`：覆盖背景色和边框，使用对应语义色的深色变体（如 info → `rgba(59,130,246,0.12)` + `1px solid rgba(59,130,246,0.3)`）
12. `st.code`：背景改为 `#0A1A20`（比面板更深），文字用 `var(--ink)`，单色字体保留
13. `st.popover`：背景 `var(--panel)`，边框 `var(--line)`
14. `st.dataframe`：覆盖表头背景（`var(--panel)`）、行悬停色、滚动条、空状态文字色
15. Live log（`.geo-answer-block`）：背景 `#0A1A20`，文字用 `var(--data-green)`；**不使用 `text-shadow` glow**（高频刷新组件性能代价高）

---

### 第二步：`pages/4_结果分析.py`（布局重排）

当前页面已包含网址链接校验（`LinkColumn`）和评分明细字段（信息熵、相关性、证据质量、综合得分、机会分），plan 需明确覆盖这些字段的布局。

**Overview tab**（布局逻辑：主结论优先，辅助信息后置）
- **第一行（全宽）：** 小平台机会榜（`niche_opportunities`，含网址链接列和评分列），确保 URL 和评分列不被截断
- **第二行（双列）：** 左 — 原始来源域名（`top_domains`）；右 — 网页风格相似度（`benchmark_summary`）
- **第三行（全宽或独立区块）：** 头部基线平台（`baseline_platforms`），作为对比参考而非主推内容
- 当前代码中 `baseline_platforms` 还在 Overview 右侧（与 `niche_opportunities` 并列），需改为后置

**Scores tab**
- 评分详情（`platform_scores`，含信息熵/相关性/证据质量/综合得分/机会分）改为**全宽或至少左侧 2/3 宽度**
- golden set 放右侧 1/3 或改为独立区块
- `st.columns([1.5, 1])` → `st.columns([2, 1])`

**Trace tab**
- 无结构改动，颜色跟随 CSS 变量

---

### 第三步：`pages/2_蒸馏问题生成.py`（高度微调）

- 问题列表通过 `st.html()` 渲染（不能改回 `st.markdown`，见 current-state.md:31），高度完全由 CSS 控制
- `geo-question-list-shell` 高度在第一步已改为 `clamp()`，此页面 Python 代码无需改动

---

### 第四步：`pages/3_运行蒸馏.py`（高度公式调整 + 列比例）

> **注意：** 按 current-state.md:41，`distillation_preview_height()` 是专用函数，必须保留，不得删除或合并到普通列表高度函数。

**高度公式调整（`src/ui_presenters.py`）**

当前公式：`360 + row_count * 48`，上限 980px。20 题时计算值 1320px，被截断到 980px 仍会产生内滚。

修改方向：提高基础值和上限，让常用问题数量（10–20 题）尽量不触发内滚：
```python
# 建议公式（可按实际测量微调）
estimated = 200 + row_count * 72   # 每行给更多空间
return min(max(estimated, 420), 1400)  # 上限从 980 提到 1400
```

**列比例调整（`pages/3_运行蒸馏.py`）**

进度列表每行当前 `[0.7, 6.5, 1.5]`，status 图标列 0.7 过窄：
- 改为 `[1, 8, 2]`，比例关系相近但绝对宽度更宽松

---

### 第五步：`Home.py`（正式检查范围，非选做）

首页大量依赖 `.geo-kpi` 等 CSS 组件，与第一步 CSS 改动强相关，需人工验证：
- KPI 卡片（`.geo-kpi`）在深色背景下对比度和数值可读性
- workflow 区块（`.geo-section-card`）与 latest runs（`.geo-card`）层次感
- 若视觉检查发现 KPI 过于扁平，在 HTML 内联 style 补 `border-top: 2px solid var(--accent)` 作为装饰条

---

## 执行顺序

```
1. src/ui_helpers.py          → 深色主题 CSS 全量重写（含原生组件覆盖）
2. pages/4_结果分析.py        → 核心表格改全宽，Scores tab 列比调整
3. pages/2_蒸馏问题生成.py    → 验证 clamp() 高度是否生效（预期 Python 无需改动）
4. src/ui_presenters.py       → 调整 distillation_preview_height() 公式，上限提高
   pages/3_运行蒸馏.py        → 调整行列比例 [1, 8, 2]
5. Home.py                    → 人工视觉检查，按需补装饰
6. 逐页截图检查 + pytest
```

---

## 验证检查清单

**功能回归**
- [ ] `pytest tests/unit/test_ui_presenters.py` 全部通过（重点：`distillation_preview_height` 改后单测仍通过）
- [ ] `python -m py_compile pages/2_蒸馏问题生成.py pages/3_运行蒸馏.py pages/4_结果分析.py src/ui_helpers.py src/ui_presenters.py` 无报错

**视觉检查（逐页）**
- [ ] Home：KPI 数值可读，workflow / latest runs 深色下层次清晰
- [ ] 页面 2：问题卡片列表高度充分利用视口，无过多空白也无不必要内滚；`clamp()` 在不同分辨率下行为正常
- [ ] 页面 3：10–20 题场景下进度列表的无意义内滚**显著减少**（不承诺完全消除，Streamlit 容器高度、浏览器窗口、题目长度均不稳定）；status 图标列不被挤压；状态色语义正确（pending灰 / running蓝 / completed绿 / error黄）
- [ ] 页面 3：st.info / st.code（job log）在深色下对比度正常
- [ ] 页面 4：niche opportunities 表格含网址链接列全宽展示；评分明细字段（信息熵等）不被截断
- [ ] 页面 4：st.dataframe 细项检查（Streamlit 版本间样式容易漂移）：
  - 表头背景对比度（深色下不能与行背景混淆）
  - 行 hover 高亮色可见
  - `LinkColumn` 链接色在深色背景下清晰可读
  - `LinkColumn` 访问态（visited）和悬停态（hover）有明显区分（业务依赖链接可信度判断）
  - 空状态文字色不消失于背景
- [ ] 所有页面：st.info / st.warning / st.success / st.error 不出现浅色背景孤岛
- [ ] 超宽屏（>1600px）内容居中而非无限拉伸

---

## 不在本次范围内

- 深色/浅色双主题切换
- Plotly 图表配色同步更新（单独任务，不阻塞本次）
- 响应式移动端适配
