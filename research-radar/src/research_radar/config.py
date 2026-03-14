from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict


DEFAULT_CONFIG: Dict[str, Any] = {
    "defaults": {
        "update_window_days": 7,
        "backfill_chunk_days": 30,
    },
    "paper_watch": {
        "topic_ids": [],
    },
    "exports": {
        "recent_limit": 40,
    },
    "sources": {},
    "topics": {
        "other": {
            "label": "Other",
            "priority": 999,
            "include_phrases": [],
            "include_aliases": [],
            "exclude_phrases": [],
        }
    },
}


def _deep_merge(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    result = deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: str) -> Dict[str, Any]:
    config_path = Path(path)
    content = config_path.read_text(encoding="utf-8")

    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        try:
            loaded = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "PyYAML is required to read non-JSON YAML files. Install dependencies with `pip install -e ./research-radar`."
            ) from exc
    else:
        loaded = yaml.safe_load(content) or {}

    config = _deep_merge(DEFAULT_CONFIG, loaded)
    config.setdefault("topics", {})
    config["topics"].setdefault(
        "other",
        {
            "label": "Other",
            "priority": 999,
            "include_phrases": [],
            "include_aliases": [],
            "exclude_phrases": [],
        },
    )
    return config
