import time
from spotipy import Spotify, SpotifyOAuth
from spotipy.exceptions import SpotifyException
from fuzzywuzzy import fuzz

import os

from .utils import CACHE_DIR, load_config


MAX_PLAYLIST_SIZE = 10000


def get_client():
    cid = os.getenv("SPOTIPY_CLIENT_ID")
    secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect = os.getenv("SPOTIPY_REDIRECT_URI")
    if not (cid and secret and redirect):
        cfg = load_config()
        cid = cid or cfg.get("SPOTIPY_CLIENT_ID")
        secret = secret or cfg.get("SPOTIPY_CLIENT_SECRET")
        redirect = redirect or cfg.get("SPOTIPY_REDIRECT_URI")
    return Spotify(
        auth_manager=SpotifyOAuth(
            client_id=cid,
            client_secret=secret,
            redirect_uri=redirect,
            scope="playlist-modify-public",
            cache_path=str(CACHE_DIR / "spotify"),
        )
    )


def spotify_request(func, *args, on_wait=None, **kwargs):
    """Wrapper that retries Spotify requests and handles rate limits.

    Parameters
    ----------
    func: callable
        Spotify client function to call.
    on_wait: callable
        Optional callback receiving the remaining seconds while waiting for
        the rate limit to reset.
    """
    while True:
        try:
            return func(*args, **kwargs)
        except SpotifyException as e:
            if e.http_status == 429:
                wait = int(e.headers.get("Retry-After", 1))
                for remaining in range(wait, 0, -1):
                    if on_wait:
                        on_wait(remaining)
                    time.sleep(1)
                continue
            raise


def search(sp, cache, artist, title, on_wait=None):
    key = f"{artist}|{title}".lower()
    if key in cache:
        return {'id': cache[key]}
    query = f"artist:{artist} track:{title}"
    results = spotify_request(sp.search, q=query, type="track", limit=1, on_wait=on_wait)
    items = results.get("tracks", {}).get("items")
    if items:
        cache[key] = items[0]['id']
        return items[0]
    return None


def fuzzy_search(sp, cache, query, on_wait=None):
    results = spotify_request(sp.search, q=query, type="track", limit=5, on_wait=on_wait)
    items = results.get("tracks", {}).get("items", [])
    best = None
    best_score = 0
    for item in items:
        score = fuzz.ratio(query.lower(), f"{item['artists'][0]['name']} {item['name']}".lower())
        if score > best_score:
            best_score = score
            best = item
    if best_score > 67 and best:
        cache[query.lower()] = best['id']
        return best
    return None


def ensure_playlists(sp, user_id, base_name, on_wait=None):
    playlists_data = spotify_request(sp.user_playlists, user_id, on_wait=on_wait)
    relevant = [
        {'id': p['id'], 'name': p['name'], 'count': p['tracks']['total']}
        for p in playlists_data['items'] if p['name'].startswith(base_name)
    ]
    if not relevant:
        p = spotify_request(sp.user_playlist_create, user_id, base_name)
        relevant.append({'id': p['id'], 'name': p['name'], 'count': 0})
    relevant.sort(key=lambda x: x['name'])
    return relevant


def add_to_playlist(sp, playlists, user_id, base_name, track_id, on_wait=None):
    current = playlists[-1]
    if current['count'] >= MAX_PLAYLIST_SIZE:
        index = len(playlists) + 1
        p = spotify_request(sp.user_playlist_create, user_id, f"{base_name} {index}", on_wait=on_wait)
        playlists.append({'id': p['id'], 'name': p['name'], 'count': 0})
        current = playlists[-1]
    spotify_request(sp.playlist_add_items, current['id'], [track_id], on_wait=on_wait)
    current['count'] += 1
