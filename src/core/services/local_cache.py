import json
import os
from pathlib import Path
from typing import Any

_DEFAULT_DIR = Path(__file__).resolve().parents[3] / "local_cache"
cache_path = Path(os.getenv("CACHE_DIR", _DEFAULT_DIR)) / "cache.json"


def _load() -> dict:
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data: dict) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_to_cache(key: str, value) -> bool:
    try:
        data = _load()
        data[key] = value
        _save(data)
        return True
    except Exception as e:
        print(f"Failed to write cache: {e}")
        return False


def get_from_cache(key: str) -> Any | None:
    return _load().get(key)


def get_from_cache_save_on_not_exist(key: str, value) -> Any:
    data = _load()
    if key in data:
        return data[key]
    save_to_cache(key, value)
    return value