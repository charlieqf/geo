import json
from pathlib import Path

from src.db import get_connection, init_db
from src.pipeline.answer_preprocess import preprocess_answer_record


class StubAnalyzer:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload
        self.calls: list[dict[str, object]] = []

    def generate_text(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        return {
            "text": json.dumps(self.payload, ensure_ascii=False),
            "raw": {"ok": True},
        }


def test_preprocess_answer_record_persists_sources_and_topics(tmp_path: Path) -> None:
    db_path = tmp_path / "geo.sqlite3"
    init_db(db_path)
    connection = get_connection(db_path)
    try:
        connection.execute(
            """
            INSERT INTO runs (
                id, keyword_input, brand_name, region, target_provider, target_model,
                analysis_provider, analysis_model, target_coverage, question_count,
                status, notes, created_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "run_1",
                "中国 GEO 服务",
                "流量玩家",
                "中国",
                "doubao",
                "doubao-seed-2-0-pro-260215",
                "openai",
                "gpt-5.4",
                0.85,
                1,
                "running",
                None,
                "2026-03-22T00:00:00+00:00",
                None,
            ),
        )
        connection.execute(
            """
            INSERT INTO questions (
                id, run_id, display_order, intent_bucket, question_text,
                why_this_question, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "q_1",
                "run_1",
                1,
                "direct_recommendation",
                "中国 GEO 服务哪家强？",
                "测试问题",
                "2026-03-22T00:00:00+00:00",
            ),
        )
        connection.execute(
            """
            INSERT INTO answers (
                id, run_id, question_id, prompt_variant, target_provider,
                target_model, answer_text, raw_response_path, extracted_urls_json,
                latency_ms, finish_reason, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "a_1",
                "run_1",
                "q_1",
                "web_ranked_analysis",
                "doubao",
                "doubao-seed-2-0-pro-260215",
                "知乎、小红书和 IT之家值得关注。参考 https://zhihu.com/question/1 和 https://www.ithome.com/0/1/1.htm 。阿里云官网不是投放平台。",
                "runs/run_1/raw_answers/a_1.json",
                json.dumps(
                    [
                        "https://zhihu.com/question/1",
                        "https://www.ithome.com/0/1/1.htm",
                        "https://www.aliyun.com/",
                    ],
                    ensure_ascii=False,
                ),
                123,
                "stop",
                "2026-03-22T00:00:00+00:00",
            ),
        )
        connection.commit()

        analyzer = StubAnalyzer(
            {
                "question_id": "q_1",
                "domains": ["zhihu.com", "ithome.com", "aliyun.com"],
                "source_labels": ["知乎", "IT之家", "小红书"],
                "interpretation_label": "geo_ai_optimization",
                "brand_grounded": True,
                "source_explicitness_score": 0.82,
                "topic_units": [
                    {
                        "topic_label": "高权重社区渗透",
                        "claim": "知乎和小红书是高价值信息平台。",
                        "supporting_domains": ["zhihu.com"],
                        "confidence": 0.91,
                        "evidence_span": "知乎、小红书和 IT之家值得关注。",
                    }
                ],
                "noise_flags": {
                    "generic_listicle": False,
                    "weak_evidence": False,
                    "self_reference_only": False,
                },
            }
        )

        preprocess_answer_record(
            connection=connection,
            analyzer=analyzer,
            answer_id="a_1",
            run_id="run_1",
            question_id="q_1",
            answer_text="知乎、小红书和 IT之家值得关注。参考 https://zhihu.com/question/1 和 https://www.ithome.com/0/1/1.htm 。阿里云官网不是投放平台。",
            prompt_variant="web_ranked_analysis",
            intent_bucket="direct_recommendation",
            system_prompt="system prompt",
            user_template="Question ID: {question_id}\nIntent bucket: {intent_bucket}\nPrompt variant: {prompt_variant}\nAnswer text: {answer_text}\nCitations: {citations}\nExtracted urls: {extracted_urls}\nExtracted source labels: {source_labels}",
            extracted_urls=[
                "https://zhihu.com/question/1",
                "https://www.ithome.com/0/1/1.htm",
                "https://www.aliyun.com/",
            ],
            extracted_source_labels=["IT之家", "知乎"],
        )

        source_rows = connection.execute(
            "SELECT domain, source_label, source_role, normalized_platform, is_actionable_platform FROM answer_sources ORDER BY normalized_platform, source_label, domain"
        ).fetchall()
        topic_rows = connection.execute(
            "SELECT interpretation_label, brand_grounded, source_explicitness_score, provisional_topic_label, supporting_domains_json FROM answer_topic_units"
        ).fetchall()
    finally:
        connection.close()

    assert analyzer.calls
    assert len(source_rows) >= 4
    assert any(
        row[0] == "zhihu.com"
        and row[2] == "publish_platform"
        and row[3] == "知乎"
        and row[4] == 1
        for row in source_rows
    )
    assert any(
        row[0] == "aliyun.com" and row[2] == "infrastructure_site" and row[4] == 0
        for row in source_rows
    )
    assert any(
        row[1] == "IT之家"
        and row[2] == "publish_platform"
        and row[3] == "IT之家"
        and row[4] == 1
        for row in source_rows
    )
    assert len(topic_rows) == 1
    topic_row = topic_rows[0]
    assert topic_row[0] == "geo_ai_optimization"
    assert topic_row[1] == 1
    assert topic_row[2] == 0.82
    assert topic_row[3] == "高权重社区渗透"
    assert json.loads(topic_row[4]) == ["zhihu.com"]
