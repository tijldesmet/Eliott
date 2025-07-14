import mp3organizer.spotify as spotify

class DummySp:
    def __init__(self):
        self.created = []
        self.added = []
        self.counter = 0

    def user_playlist_create(self, user_id, name, **_):
        self.counter += 1
        pid = f"id_{self.counter}"
        self.created.append((user_id, name))
        return {"id": pid, "name": name}

    def playlist_add_items(self, playlist_id, items, **_):
        self.added.append((playlist_id, items))
        return {}

def passthrough(func, *args, **kwargs):
    return func(*args, **kwargs)


def test_add_to_playlist_split(monkeypatch):
    sp = DummySp()
    playlists = [{"id": "p1", "name": "Spotify", "count": spotify.MAX_PLAYLIST_SIZE}]
    monkeypatch.setattr(spotify, "spotify_request", passthrough)

    spotify.add_to_playlist(sp, playlists, "uid", "Spotify", "track1")

    assert len(playlists) == 2
    assert playlists[-1]["count"] == 1
    assert sp.created == [("uid", "Spotify 2")]
    assert sp.added == [("id_1", ["track1"])]


def test_add_to_playlist_no_split(monkeypatch):
    sp = DummySp()
    playlists = [{"id": "p1", "name": "Spotify", "count": 5}]
    monkeypatch.setattr(spotify, "spotify_request", passthrough)

    spotify.add_to_playlist(sp, playlists, "uid", "Spotify", "track2")

    assert len(playlists) == 1
    assert playlists[0]["count"] == 6
    assert sp.created == []
    assert sp.added == [("p1", ["track2"])]
