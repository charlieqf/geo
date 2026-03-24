from __future__ import annotations

from pathlib import Path


def app_css() -> str:
    return """
    <style>
      :root {
        --bg: #f4f2ef;
        --ink: #1f1c19;
        --muted: #6f6a64;
        --panel: #fbfaf8;
        --line: #e4dfd8;
        --accent: #8b7355;
        --accent-strong: #5d5145;
        --data-blue: #355c7d;
        --data-green: #3f776c;
        --warn: #a35d3b;
      }

      .stApp {
        background: radial-gradient(1200px 600px at 10% -10%, #efe7dc 0%, transparent 60%),
                    radial-gradient(1000px 500px at 90% 0%, #f0ece6 0%, transparent 55%),
                    var(--bg);
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
        max-width: 1240px;
      }

      [data-testid="stTextInput"] [data-baseweb="base-input"],
      [data-testid="stNumberInput"] [data-baseweb="base-input"] {
        border: 2px solid rgba(139, 115, 85, 0.55);
        border-radius: 14px;
        background: rgba(255,255,255,0.94);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.75), 0 6px 16px rgba(44, 38, 32, 0.05);
        transition: border-color 120ms ease, box-shadow 120ms ease, transform 120ms ease;
      }

      [data-testid="stTextInput"] [data-baseweb="base-input"]:focus-within,
      [data-testid="stNumberInput"] [data-baseweb="base-input"]:focus-within {
        border-color: var(--accent-strong);
        box-shadow: 0 0 0 3px rgba(139, 115, 85, 0.14), 0 10px 22px rgba(44, 38, 32, 0.08);
      }

      [data-testid="stTextInput"] input,
      [data-testid="stNumberInput"] input {
        background: transparent;
      }

      [data-testid="stTabs"] [role="tablist"] {
        gap: 0.35rem;
      }

      [data-testid="stTabs"] [role="tab"] {
        border-radius: 999px;
        border: 1px solid var(--line);
        background: rgba(255,255,255,0.7);
        padding-left: 1rem;
        padding-right: 1rem;
      }

      [data-testid="stTabs"] [aria-selected="true"] {
        border-color: rgba(139, 115, 85, 0.55);
        box-shadow: 0 6px 14px rgba(44, 38, 32, 0.06);
      }

      h1, h2, h3 {
        color: var(--accent-strong);
        letter-spacing: 0.01em;
      }

      .geo-hero, .geo-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.25rem 1.35rem;
        box-shadow: 0 18px 45px rgba(44, 38, 32, 0.08);
        margin-bottom: 1rem;
      }

      .geo-hero h1 {
        margin-bottom: 0.25rem;
      }

      .geo-muted {
        color: var(--muted);
      }

      .geo-kpi {
        background: rgba(255,255,255,0.72);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 0.9rem 1rem;
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
        background: rgba(255,255,255,0.76);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 12px 28px rgba(44, 38, 32, 0.06);
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
        background: rgba(255,255,255,0.72);
        color: var(--accent-strong);
        font-size: 0.88rem;
      }

      .geo-question-card {
        background: rgba(255,255,255,0.82);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        box-shadow: 0 10px 22px rgba(44, 38, 32, 0.05);
        margin-bottom: 0.75rem;
      }

      .geo-form-shell {
        background: linear-gradient(180deg, rgba(255,255,255,0.88) 0%, rgba(255,255,255,0.74) 100%);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1rem 1.1rem 0.35rem;
        box-shadow: 0 12px 28px rgba(44, 38, 32, 0.06);
        margin-bottom: 1rem;
      }

      .geo-question-list-shell {
        height: calc(100vh - 23rem);
        overflow-y: auto;
        overflow-x: hidden;
        padding-right: 0.2rem;
      }

      .geo-question-list-shell::-webkit-scrollbar {
        width: 10px;
      }

      .geo-question-list-shell::-webkit-scrollbar-thumb {
        background: rgba(139, 115, 85, 0.35);
        border-radius: 999px;
      }

      .geo-question-list-shell::-webkit-scrollbar-track {
        background: rgba(228, 223, 216, 0.35);
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

      .geo-status-pending { color: #7d746c; }
      .geo-status-running { color: #355c7d; }
      .geo-status-completed { color: #3f776c; }
      .geo-status-error { color: #a35d3b; }

      .geo-answer-block {
        background: rgba(255,255,255,0.7);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 0.8rem 0.9rem;
        margin-bottom: 0.7rem;
      }

      .geo-answer-label {
        color: var(--accent-strong);
        font-weight: 700;
        margin-bottom: 0.35rem;
      }

      .geo-answer-text {
        color: var(--ink);
        white-space: pre-wrap;
        line-height: 1.7;
      }
    </style>
    """


def default_benchmark_path() -> Path:
    return Path("中国GEO（生成式引擎优化）服务商盘点.txt")
