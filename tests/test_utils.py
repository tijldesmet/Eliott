import json
from pathlib import Path
import eliott.utils as utils


def test_sanitize_filename():
    assert utils.sanitize_filename('test! file@name') == 'Test Filename'
    assert utils.sanitize_filename('hello_world-123') == 'Hello_World-123'


def test_load_save_cache(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    cache_file = cache_dir / "cache.json"
    monkeypatch.setattr(utils, "CACHE_DIR", cache_dir)
    monkeypatch.setattr(utils, "CACHE_FILE", cache_file)

    # Loading when file does not exist returns empty dict
    assert utils.load_cache() == {}

    data = {"a": 1, "b": 2}
    utils.save_cache(data)
    assert cache_file.exists()

    loaded = utils.load_cache()
    assert loaded == data


def test_unique_path(tmp_path):
    orig = tmp_path / "song.mp3"
    orig.touch()

    path1 = utils.unique_path(orig)
    assert path1.name == "song_1.mp3"
    path1.touch()

    path2 = utils.unique_path(orig)
    assert path2.name == "song_2.mp3"
