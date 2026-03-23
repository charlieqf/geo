from src.providers.openai_client import build_responses_input
from src.providers.qwen_client import build_chat_messages, normalize_base_url


def test_build_openai_responses_input_keeps_system_then_user_order() -> None:
    payload = build_responses_input(
        system_prompt="system instruction",
        user_prompt="user content",
    )

    assert payload == [
        {
            "role": "system",
            "content": [{"type": "input_text", "text": "system instruction"}],
        },
        {"role": "user", "content": [{"type": "input_text", "text": "user content"}]},
    ]


def test_qwen_message_builder_and_base_url_normalization() -> None:
    assert normalize_base_url("https://dashscope.aliyuncs.com/compatible-mode/v1/") == (
        "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    messages = build_chat_messages(
        system_prompt="system instruction",
        user_prompt="user content",
    )

    assert messages == [
        {"role": "system", "content": "system instruction"},
        {"role": "user", "content": "user content"},
    ]
