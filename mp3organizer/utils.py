import json
import os
from pathlib import Path

CACHE_DIR = Path(os.path.expanduser("~")) / ".cache_mp3"
CACHE_DIR.mkdir(exist_ok=True)
CACHE_FILE = CACHE_DIR / "cache.json"
CONFIG_PATH = Path(os.path.expanduser("~")) / ".mp3organizer_config"


def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f)


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f)


def sanitize_filename(name: str) -> str:
    return ''.join(c for c in name if c.isalnum() or c in (' ', '-', '_')).title()

