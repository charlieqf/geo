from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_QWEN_MODEL = "qwen-max"
DEFAULT_DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DEFAULT_DOUBAO_MODEL = "doubao-seed-2-0-pro-260215"
DEFAULT_OPENAI_MODEL = "gpt-5.4"
DEFAULT_DB_PATH = Path("data") / "geo_weight_distiller.sqlite3"
DEFAULT_RUNS_DIR = Path("runs")
DEFAULT_PROMPTS_DIR = Path("prompts")


@dataclass(frozen=True)
class AppConfig:
    qwen_api_key: str
    qwen_base_url: str
    qwen_model: str
    doubao_api_key: str | None
    doubao_base_url: str
    doubao_model: str
    openai_api_key: str | None
    openai_model: str
    app_db_path: Path
    runs_dir: Path
    prompts_dir: Path


def _expand_path(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is required")
    return value


def load_config(env_file: str | Path | None = ".env") -> AppConfig:
    if env_file is not None:
        load_dotenv(dotenv_path=env_file, override=False)

    return AppConfig(
        qwen_api_key=_require_env("QWEN_API_KEY"),
        qwen_base_url=os.getenv("QWEN_BASE_URL", DEFAULT_QWEN_BASE_URL),
        qwen_model=os.getenv("QWEN_MODEL", DEFAULT_QWEN_MODEL),
        doubao_api_key=os.getenv("DOUBAO_API_KEY") or None,
        doubao_base_url=os.getenv("DOUBAO_BASE_URL", DEFAULT_DOUBAO_BASE_URL),
        doubao_model=os.getenv("DOUBAO_MODEL", DEFAULT_DOUBAO_MODEL),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        app_db_path=_expand_path(os.getenv("APP_DB_PATH", str(DEFAULT_DB_PATH))),
        runs_dir=_expand_path(os.getenv("RUNS_DIR", str(DEFAULT_RUNS_DIR))),
        prompts_dir=_expand_path(os.getenv("PROMPTS_DIR", str(DEFAULT_PROMPTS_DIR))),
    )
