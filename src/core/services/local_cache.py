import json
from importlib.resources import files
from typing import Any

package_root = str(files("my_project"))
cache_path = f"{package_root}/local_cache/cache.json"


def save_to_cache(key: str, value) -> bool:
    try:
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            cache_data = {}

        cache_data[key] = value

        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Failed to write cache: {e}")
        return False


def get_from_cache(key: str) -> Any | None:
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

            return cache_data.get(key)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_from_cache_save_on_not_exist(key: str, value) -> Any:
    try:
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            cache_data = {}

        if key in cache_data.keys():
            return cache_data[key]
        else:
            cache_data[key] = value
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, indent=2, ensure_ascii=False)


    except Exception as e:
        print(f"Failed to write cache: {e}")
        return False
