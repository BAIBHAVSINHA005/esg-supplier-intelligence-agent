# app/schemas/loader.py

import json
from pathlib import Path

_SCHEMA_DIR = Path(__file__).parent
_cache: dict = {}


def load_schema(framework_id: str = "brsr_v2023") -> dict:
    if framework_id in _cache:
        return _cache[framework_id]
    path = _SCHEMA_DIR / f"{framework_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Schema not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    _cache[framework_id] = schema
    return schema


def get_indicators(schema: dict, principle_id: str) -> dict:
    return schema["principles"][principle_id]["indicators"]