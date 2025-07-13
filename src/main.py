import os
import sys
import time
import json
import html
import requests
import PySimpleGUI as sg
from pathlib import Path
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError
from spotipy import Spotify, SpotifyOAuth
from fuzzywuzzy import fuzz

# Constants
MAX_PLAYLIST_SIZE = 10000
CACHE_PATH = os.path.join(os.path.expanduser("~"), ".cache_mp3")


def get_spotify_client():
    return Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-public", cache_path=CACHE_PATH))


def search_spotify(sp, artist, title):
    query = f"artist:{artist} track:{title}"
    results = sp.search(q=query, type="track", limit=1)
    items = results.get("tracks", {}).get("items")
    if items:
        return items[0]
    return None


def fuzzy_search_spotify(sp, query):
    results = sp.search(q=query, type="track", limit=5)
    items = results.get("tracks", {}).get("items", [])
    best = None
    best_score = 0
    for item in items:
        score = fuzz.ratio(query.lower(), f"{item['artists'][0]['name']} {item['name']}".lower())
        if score > best_score:
            best_score = score
            best = item
    if best_score > 67:
        return best
    return None


def audd_recognize(path, api_key):
    files = {'file': open(path, 'rb')}
    data = {'api_token': api_key}
    r = requests.post('https://api.audd.io/', data=data, files=files)
    if r.status_code == 200:
        result = r.json().get('result')
        if result:
            return result.get('artist'), result.get('title')
    return None, None


def sanitize_filename(name: str) -> str:
    return ''.join(c for c in name if c.isalnum() or c in (' ', '-', '_')).title()


def ensure_playlist(sp, user_id, base_name):
    playlists = sp.user_playlists(user_id)
    existing = [p for p in playlists['items'] if p['name'].startswith(base_name)]
    index = 1
    while True:
        name = f"{base_name} {index}" if index > 1 else base_name
        match = next((p for p in existing if p['name'] == name), None)
        if match and sp.playlist(match['id'])['tracks']['total'] < MAX_PLAYLIST_SIZE:
            return match['id']
        if not match:
            playlist = sp.user_playlist_create(user_id, name)
            return playlist['id']
        index += 1


def add_to_playlist(sp, playlist_id, track_id):
    sp.playlist_add_items(playlist_id, [track_id])


def write_html_report(entries, out_path):
    rows = []
    for idx, e in enumerate(entries, 1):
        rows.append(f"<tr><td>{idx}</td><td>{html.escape(e['artist'])}</td><td>{html.escape(e['title'])}</td><td>{e['dest']}</td></tr>")
    html_content = """
    <html><body><table border='1'>
    <tr><th>#</th><th>Artist</th><th>Title</th><th>Destination</th></tr>
    {rows}
    </table></body></html>
    """.format(rows='\n'.join(rows))
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def process_files(values):
    src = Path(values['SRC'])
    out = Path(values['DST'])
    spotify_dir = out / 'Spotify'
    napster_dir = out / 'Napster'
    spotify_dir.mkdir(parents=True, exist_ok=True)
    napster_dir.mkdir(parents=True, exist_ok=True)

    sp = get_spotify_client()
    user_id = sp.me()['id']
    playlist_id = ensure_playlist(sp, user_id, 'Spotify')

    napster_playlist = napster_dir / 'Napster.m3u'
    entries = []

    files = list(src.glob('*.mp3'))
    total = len(files)

    for i, file in enumerate(files, 1):
        window['PROG'].update(current_count=i, max=total)
        window['STATUS'].update(f"Processing {file.name} ({i}/{total})")
        try:
            tags = EasyID3(file)
            artist = tags.get('artist', [None])[0]
            title = tags.get('title', [None])[0]
        except ID3NoHeaderError:
            artist = title = None

        if not artist or not title:
            parts = file.stem.split('-')
            if len(parts) >= 2:
                artist = artist or parts[0].strip()
                title = title or parts[1].strip()

        match = None
        if artist and title:
            match = search_spotify(sp, artist, title)
            if not match:
                query = f"{artist} {title}"
                match = fuzzy_search_spotify(sp, query)
        if not match:
            api_key = os.getenv('AUDD_API_KEY')
            if api_key:
                ra, rt = audd_recognize(str(file), api_key)
                if ra and rt:
                    match = search_spotify(sp, ra, rt)
                    if not match:
                        match = fuzzy_search_spotify(sp, f"{ra} {rt}")
                    artist = ra
                    title = rt
        if match:
            track_id = match['id']
            add_to_playlist(sp, playlist_id, track_id)
            dest = spotify_dir / file.name
            dest = dest.with_name(sanitize_filename(dest.stem) + dest.suffix)
            file.rename(dest)
            entries.append({'artist': artist or '', 'title': title or '', 'dest': 'Spotify'})
        else:
            dest = napster_dir / file.name
            file.rename(dest)
            with open(napster_playlist, 'a', encoding='utf-8') as m3u:
                m3u.write(dest.name + '\n')
            entries.append({'artist': artist or '', 'title': title or '', 'dest': 'Napster'})
        window.refresh()

    report = out / 'report.html'
    write_html_report(entries, report)
    sg.popup('Done', title='Finished')


layout = [
    [sg.Text('Source Folder'), sg.Input(key='SRC'), sg.FolderBrowse()],
    [sg.Text('Output Folder'), sg.Input(key='DST'), sg.FolderBrowse()],
    [sg.Button('Start')],
    [sg.ProgressBar(max_value=1, orientation='h', size=(40, 20), key='PROG')],
    [sg.Text('', size=(60, 1), key='STATUS')]
]

window = sg.Window('MP3 Organizer', layout, finalize=True, theme='DarkGrey13')

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Start':
        process_files(values)

window.close()
