from pathlib import Path

from src.config import AppConfig
from src.pipeline.discovery_run import build_target_client_settings


def test_build_target_client_settings_uses_doubao_only() -> None:
    config = AppConfig(
        qwen_api_key="qwen-key",
        qwen_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        qwen_model="qwen-max",
        doubao_api_key="doubao-key",
        doubao_base_url="https://ark.cn-beijing.volces.com/api/v3",
        doubao_model="doubao-seed-2-0-pro-260215",
        openai_api_key="openai-key",
        openai_model="gpt-5.4",
        app_db_path=Path("data/demo.sqlite3"),
        runs_dir=Path("runs"),
        prompts_dir=Path("prompts"),
    )

    settings = build_target_client_settings(config)

    assert settings == {
        "provider": "doubao",
        "api_key": "doubao-key",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-seed-2-0-pro-260215",
    }
