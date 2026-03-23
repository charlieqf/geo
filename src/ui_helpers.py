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

      .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1240px;
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
