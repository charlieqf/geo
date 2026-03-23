from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_prompt_meta(meta_path: Path) -> dict[str, Any]:
    return json.loads(meta_path.read_text(encoding="utf-8"))
