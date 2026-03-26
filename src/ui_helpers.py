from __future__ import annotations

from pathlib import Path


def app_css() -> str:
    return """
    <style>
      :root {
        --bg: #0F171A;
        --panel: #162028;
        --ink: #E2E8F0;
        --muted: #64748B;
        --line: #334155;
        --accent: #3B82F6;
        --accent-strong: #2563EB;
        --data-green: #10B981;
        --data-blue: #38BDF8;
        --warn: #F59E0B;
      }

      .stApp {
        background: linear-gradient(160deg, #0F1F2A 0%, #0F171A 60%);
        color: var(--ink);
      }

      [data-testid="stSidebar"],
      [data-testid="stSidebar"] > div:first-child {
        background: #111B22 !important;
        border-right: 1px solid var(--line);
      }

      [data-testid="stSidebarNav"] {
        background: transparent;
      }

      [data-testid="stSidebarNav"] a {
        color: var(--ink) !important;
        border: 1px solid transparent;
        border-radius: 8px;
        transition: background 120ms ease, border-color 120ms ease, color 120ms ease;
      }

      [data-testid="stSidebarNav"] a p,
      [data-testid="stSidebarNav"] a span,
      [data-testid="stSidebarNav"] a [data-testid="stMarkdownContainer"] {
        color: var(--ink) !important;
        opacity: 1 !important;
      }

      [data-testid="stSidebarNav"] a:hover {
        background: rgba(59, 130, 246, 0.12) !important;
        border-color: rgba(59, 130, 246, 0.28);
      }

      [data-testid="stSidebarNavLink"][aria-current="page"] {
        background: rgba(59, 130, 246, 0.18) !important;
        border-color: rgba(59, 130, 246, 0.36);
        box-shadow: inset 3px 0 0 var(--accent);
      }

      [data-testid="stSidebarNavLink"][aria-current="page"] p,
      [data-testid="stSidebarNavLink"][aria-current="page"] span {
        color: #F8FAFC !important;
        font-weight: 600 !important;
      }

      [data-testid="stButton"] button,
      [data-testid="baseButton-secondary"] {
        background: var(--panel) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.22);
      }

      [data-testid="stButton"] button:hover,
      [data-testid="baseButton-secondary"]:hover {
        background: rgba(59, 130, 246, 0.12) !important;
        border-color: rgba(59, 130, 246, 0.32) !important;
        color: #F8FAFC !important;
      }

      [data-testid="stButton"] button p,
      [data-testid="baseButton-secondary"] p,
      [data-testid="stButton"] button span,
      [data-testid="baseButton-secondary"] span {
        color: inherit !important;
      }

      [data-testid="stExpander"] details {
        background: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
        overflow: hidden;
      }

      [data-testid="stExpander"] summary {
        background: rgba(51, 65, 85, 0.45) !important;
        color: var(--ink) !important;
        border-bottom: 1px solid rgba(51, 65, 85, 0.35) !important;
      }

      [data-testid="stExpander"] summary p,
      [data-testid="stExpander"] summary span,
      [data-testid="stExpander"] summary svg,
      [data-testid="stExpander"] details p,
      [data-testid="stExpander"] details span,
      [data-testid="stExpander"] details label {
        color: var(--ink) !important;
      }

      [data-testid="stExpanderDetails"] {
        background: transparent !important;
      }

      .stApp,
      .stApp .stMarkdown,
      .stApp .stCaption,
      .stApp p,
      .stApp li,
      .stApp label,
      .stApp span {
        color: var(--ink);
      }

      [data-testid="stToolbar"],
      [data-testid="stMainMenu"],
      [data-testid="stAppDeployButton"],
      [data-testid="stHeaderActionElements"],
      [data-testid="stStatusWidget"],
      [data-testid="stDecoration"],
      footer,
      #MainMenu,
      .viewerBadge_container__1QSob,
      .viewerBadge_link__1S137,
      .viewerBadge_text__1JaDK {
        display: none;
      }

      [data-testid="stHeader"] {
        height: 0;
        min-height: 0;
        background: transparent;
      }

      .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1600px;
      }

      [data-testid="stTextInput"] [data-baseweb="base-input"],
      [data-testid="stNumberInput"] [data-baseweb="base-input"] {
        border: 1px solid var(--line);
        border-radius: 6px;
        background: rgba(15, 23, 26, 0.88);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.02), 0 4px 12px rgba(0, 0, 0, 0.35);
        transition: border-color 120ms ease, box-shadow 120ms ease, transform 120ms ease;
      }

      [data-testid="stTextInput"] [data-baseweb="base-input"]:focus-within,
      [data-testid="stNumberInput"] [data-baseweb="base-input"]:focus-within {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.18), 0 8px 18px rgba(0, 0, 0, 0.35);
      }

      [data-testid="stTextInput"] input,
      [data-testid="stNumberInput"] input {
        background: transparent;
        color: var(--ink);
      }

      [data-testid="stTabs"] [role="tablist"] {
        gap: 0.4rem;
        border-bottom: 1px solid var(--line);
        padding-bottom: 0.2rem;
      }

      [data-testid="stTabs"] [role="tab"] {
        border-radius: 8px 8px 0 0;
        border: 1px solid var(--line);
        border-bottom: none;
        background: rgba(22, 32, 40, 0.94);
        padding-left: 1rem;
        padding-right: 1rem;
        color: var(--muted);
      }

      [data-testid="stTabs"] [aria-selected="true"] {
        color: var(--ink);
        border-color: var(--line);
        box-shadow: inset 0 -3px 0 var(--accent);
      }

      h1, h2, h3 {
        color: var(--ink);
        letter-spacing: 0.01em;
      }

      a,
      a:visited {
        color: var(--data-blue);
      }

      a:hover {
        color: var(--accent);
      }

      .geo-hero, .geo-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1.25rem 1.35rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
        margin-bottom: 1rem;
      }

      .geo-hero {
        border-left: 3px solid var(--accent);
      }

      .geo-hero h1 {
        margin-bottom: 0.25rem;
      }

      .geo-muted {
        color: var(--muted);
      }

      .geo-kpi {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.9rem 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
      }

      .geo-kpi-label {
        color: var(--muted);
        font-size: 0.8rem;
        letter-spacing: 0.04em;
      }

      .geo-kpi-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--ink);
      }

      .geo-section-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem 1.1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
        margin-bottom: 1rem;
      }

      .geo-list {
        margin: 0;
        padding-left: 1.2rem;
        line-height: 1.8;
      }

      .geo-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
      }

      .geo-chip {
        display: inline-flex;
        align-items: center;
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 0.35rem 0.7rem;
        background: rgba(15, 23, 26, 0.72);
        color: var(--muted);
        font-size: 0.88rem;
      }

      .geo-question-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.9rem 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
        margin-bottom: 0.75rem;
      }

      .geo-form-shell {
        background: linear-gradient(180deg, rgba(22, 32, 40, 0.96) 0%, rgba(15, 23, 26, 0.92) 100%);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem 1.1rem 0.35rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
        margin-bottom: 1rem;
      }

      .geo-question-list-shell {
        height: clamp(400px, calc(100vh - 16rem), 900px);
        overflow-y: auto;
        overflow-x: hidden;
        padding-right: 0.2rem;
      }

      .geo-question-list-shell::-webkit-scrollbar {
        width: 4px;
      }

      .geo-question-list-shell::-webkit-scrollbar-thumb {
        background: var(--line);
        border-radius: 999px;
      }

      .geo-question-list-shell::-webkit-scrollbar-track {
        background: rgba(51, 65, 85, 0.18);
        border-radius: 999px;
      }

      .geo-question-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 0.55rem;
      }

      .geo-question-title {
        color: var(--ink);
        font-weight: 700;
        line-height: 1.55;
        margin-bottom: 0.4rem;
      }

      .geo-question-reason {
        color: var(--muted);
        font-size: 0.92rem;
        line-height: 1.65;
      }

      .geo-status {
        width: 2rem;
        text-align: center;
        font-size: 1.05rem;
        font-weight: 700;
      }

      .geo-status-pending { color: var(--muted); }
      .geo-status-running { color: var(--data-blue); }
      .geo-status-completed { color: var(--data-green); }
      .geo-status-error { color: var(--warn); }

      .geo-answer-block {
        background: #0A1A20;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.8rem 0.9rem;
        margin-bottom: 0.7rem;
      }

      .geo-answer-label {
        color: var(--data-blue);
        font-weight: 700;
        margin-bottom: 0.35rem;
      }

      .geo-answer-text {
        color: var(--data-green);
        white-space: pre-wrap;
        line-height: 1.7;
      }

      [data-testid="stAlert"] {
        border-radius: 8px;
        border: 1px solid var(--line);
        color: var(--ink);
      }

      [data-testid="stAlert"] [data-testid^="stMarkdownContainer"] p {
        color: var(--ink);
      }

      [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) {
        background: rgba(59, 130, 246, 0.12);
        border-color: rgba(59, 130, 246, 0.3);
      }

      [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) {
        background: rgba(16, 185, 129, 0.12);
        border-color: rgba(16, 185, 129, 0.3);
      }

      [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) {
        background: rgba(245, 158, 11, 0.12);
        border-color: rgba(245, 158, 11, 0.3);
      }

      [data-testid="stAlert"]:has([data-testid="stAlertContentError"]) {
        background: rgba(239, 68, 68, 0.12);
        border-color: rgba(239, 68, 68, 0.3);
      }

      [data-testid="stCodeBlock"] pre,
      .stCodeBlock pre {
        background: #0A1A20 !important;
        color: var(--ink) !important;
        border: 1px solid var(--line);
        border-radius: 8px;
      }

      [data-baseweb="popover"] {
        background: var(--panel);
        border: 1px solid var(--line);
        color: var(--ink);
      }

      div[data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        overflow: hidden;
        background: var(--panel);
      }

      div[data-testid="stDataFrame"] [role="grid"] {
        background: var(--panel);
        color: var(--ink);
      }

      div[data-testid="stDataFrame"] [role="columnheader"] {
        background: #101920 !important;
        color: var(--ink) !important;
        border-bottom: 1px solid var(--line) !important;
      }

      div[data-testid="stDataFrame"] [role="gridcell"] {
        background: var(--panel) !important;
        color: var(--ink) !important;
        border-color: rgba(51, 65, 85, 0.35) !important;
      }

      div[data-testid="stDataFrame"] [role="row"]:hover [role="gridcell"] {
        background: rgba(59, 130, 246, 0.08) !important;
      }

      div[data-testid="stDataFrame"] a {
        color: var(--data-blue) !important;
      }

      div[data-testid="stDataFrame"] a:hover {
        color: var(--accent) !important;
      }

      div[data-testid="stDataFrame"] a:visited {
        color: #93C5FD !important;
      }

      div[data-testid="stDataFrame"] ::-webkit-scrollbar {
        width: 4px;
        height: 4px;
      }

      div[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb {
        background: var(--line);
      }

      div[data-testid="stDataFrame"] ::-webkit-scrollbar-track {
        background: rgba(51, 65, 85, 0.18);
      }
    </style>
    """


def default_benchmark_path() -> Path:
    return Path("中国GEO（生成式引擎优化）服务商盘点.txt")
