import os
import requests

from .utils import load_config


def recognize(path: str, api_key: str | None = None):
    api_key = api_key or os.getenv("AUDD_API_KEY")
    if not api_key:
        cfg = load_config()
        api_key = cfg.get("AUDD_API_KEY")
    if not api_key:
        return None, None
    files = {"file": open(path, "rb")}
    data = {"api_token": api_key}
    r = requests.post('https://api.audd.io/', data=data, files=files)
    if r.status_code == 200:
        result = r.json().get('result')
        if result:
            return result.get('artist'), result.get('title')
    return None, None
