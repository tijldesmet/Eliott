import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mp3organizer import core

class DummySpotify:
    def me(self):
        return {'id': 'user'}

def dummy_get_client():
    return DummySpotify()

def dummy_ensure_playlists(sp, user_id, base_name, on_wait=None):
    return [{'id': 'id', 'name': base_name, 'count': 0}]

def dummy_add_to_playlist(sp, playlists, user_id, base_name, track_id, on_wait=None):
    pass

def dummy_search(sp, cache, artist, title, on_wait=None):
    return None

def dummy_fuzzy_search(sp, cache, query, on_wait=None):
    return None

def dummy_recognize(path, api_key):
    return None, None

def dummy_load_cache():
    return {}

def dummy_save_cache(cache):
    pass


def test_unique_renaming(tmp_path, monkeypatch):
    src = tmp_path / 'src'
    dst = tmp_path / 'dst'
    src.mkdir()
    dst.mkdir()
    # create files that sanitize to the same name
    (src / 'artist - title.mp3').write_bytes(b'a')
    (src / 'Artist - Title.mp3').write_bytes(b'b')

    monkeypatch.setattr(core, 'get_client', dummy_get_client)
    monkeypatch.setattr(core, 'ensure_playlists', dummy_ensure_playlists)
    monkeypatch.setattr(core, 'add_to_playlist', dummy_add_to_playlist)
    monkeypatch.setattr(core, 'search', dummy_search)
    monkeypatch.setattr(core, 'fuzzy_search', dummy_fuzzy_search)
    monkeypatch.setattr(core, 'recognize', dummy_recognize)
    monkeypatch.setattr(core, 'load_cache', dummy_load_cache)
    monkeypatch.setattr(core, 'save_cache', dummy_save_cache)

    core.process(src, dst)

    napster_dir = dst / 'Napster'
    mp3s = sorted(f.name for f in napster_dir.iterdir() if f.suffix == '.mp3')
    assert mp3s == ['Artist - Title.mp3', 'Artist - Title_1.mp3']

