from pathlib import Path

import pytest

from src.config import load_config


def test_load_config_reads_env_and_defaults(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QWEN_API_KEY", "test-qwen-key")
    monkeypatch.delenv("QWEN_BASE_URL", raising=False)
    monkeypatch.delenv("QWEN_MODEL", raising=False)
    monkeypatch.delenv("DOUBAO_API_KEY", raising=False)
    monkeypatch.delenv("DOUBAO_BASE_URL", raising=False)
    monkeypatch.delenv("DOUBAO_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "demo.sqlite3"))
    monkeypatch.setenv("RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.setenv("PROMPTS_DIR", str(tmp_path / "prompts"))

    config = load_config(env_file=None)

    assert config.qwen_api_key == "test-qwen-key"
    assert config.qwen_base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert config.qwen_model == "qwen-max"
    assert config.doubao_api_key is None
    assert config.doubao_base_url == "https://ark.cn-beijing.volces.com/api/v3"
    assert config.doubao_model == "doubao-seed-2-0-pro-260215"
    assert config.openai_api_key is None
    assert config.openai_model == "gpt-5.4"
    assert config.app_db_path == tmp_path / "demo.sqlite3"
    assert config.runs_dir == tmp_path / "runs"
    assert config.prompts_dir == tmp_path / "prompts"


def test_load_config_requires_qwen_api_key(monkeypatch) -> None:
    monkeypatch.delenv("QWEN_API_KEY", raising=False)

    with pytest.raises(ValueError, match="QWEN_API_KEY"):
        load_config(env_file=None)


def test_load_config_reads_optional_doubao_settings(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QWEN_API_KEY", "test-qwen-key")
    monkeypatch.setenv("DOUBAO_API_KEY", "test-doubao-key")
    monkeypatch.setenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    monkeypatch.setenv("DOUBAO_MODEL", "ep-test-model")
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "demo.sqlite3"))
    monkeypatch.setenv("RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.setenv("PROMPTS_DIR", str(tmp_path / "prompts"))

    config = load_config(env_file=None)

    assert config.doubao_api_key == "test-doubao-key"
    assert config.doubao_base_url == "https://ark.cn-beijing.volces.com/api/v3"
    assert config.doubao_model == "ep-test-model"
