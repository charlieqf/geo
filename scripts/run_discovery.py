from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
stdout_reconfigure = getattr(sys.stdout, "reconfigure", None)
if callable(stdout_reconfigure):
    stdout_reconfigure(encoding="utf-8")

from src.config import load_config
from src.pipeline.discovery_run import run_discovery
from src.pipeline.question_generation import generate_question_draft
from src.providers.openai_client import OpenAIAnalysisClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a Qwen discovery experiment.")
    parser.add_argument("--keyword", default="中国 GEO 服务")
    args = parser.parse_args()

    config = load_config()
    if not config.openai_api_key:
        raise SystemExit("OPENAI_API_KEY is required for the discovery run")

    analyzer = OpenAIAnalysisClient(config.openai_api_key, config.openai_model)
    draft = generate_question_draft(
        keyword=args.keyword,
        analyzer=analyzer,
        prompts_dir=config.prompts_dir,
        storage_dir=config.runs_dir / "question_drafts",
    )

    result = run_discovery(
        config=config,
        keyword=args.keyword,
        questions=draft["questions"],
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
