import json
from pathlib import Path

from src.services.draft_service import list_question_drafts, load_question_draft


def test_list_and_load_question_drafts(tmp_path: Path) -> None:
    drafts_dir = tmp_path / "drafts"
    drafts_dir.mkdir(parents=True)
    draft_path = drafts_dir / "draft-1.json"
    draft_path.write_text(
        json.dumps(
            {
                "draft_id": "draft-1",
                "keyword": "中国 GEO 服务",
                "brand": "流量玩家",
                "question_count": 2,
                "questions": [{"question_id": "q1", "question": "test"}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    drafts = list_question_drafts(drafts_dir)
    loaded = load_question_draft(draft_path)

    assert len(drafts) == 1
    assert drafts[0]["draft_id"] == "draft-1"
    assert drafts[0]["keyword"] == "中国 GEO 服务"
    assert drafts[0]["brand"] == "流量玩家"
    assert loaded["questions"] == [{"question_id": "q1", "question": "test"}]
