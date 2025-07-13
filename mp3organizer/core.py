import os
from pathlib import Path
from typing import Optional

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

from .utils import load_cache, save_cache, sanitize_filename
from .spotify import (
    get_client,
    search,
    fuzzy_search,
    ensure_playlists,
    add_to_playlist,
)
from .audd import recognize
from .report import write_html_report


def process(src: Path, dst: Path, window: Optional[object] = None):
    cache = load_cache()
    sp = get_client()
    user_id = sp.me()['id']
    playlists = ensure_playlists(sp, user_id, 'Spotify')

    spotify_dir = dst / 'Spotify'
    napster_dir = dst / 'Napster'
    spotify_dir.mkdir(parents=True, exist_ok=True)
    napster_dir.mkdir(parents=True, exist_ok=True)
    napster_playlist = napster_dir / 'Napster.m3u'

    files = [f for f in src.iterdir() if f.suffix.lower() == '.mp3']
    total = len(files)

    entries = []
    added_tracks = set()

    for i, file in enumerate(files, 1):
        if window:
            window['PROG'].update(current_count=i, max=total)
            window['STATUS'].update(f'Processing {file.name} ({i}/{total})')

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
            match = search(sp, cache, artist, title)
            if not match:
                match = fuzzy_search(sp, cache, f'{artist} {title}')
        if not match:
            api_key = os.getenv('AUDD_API_KEY')
            if api_key:
                ra, rt = recognize(str(file), api_key)
                if ra and rt:
                    match = search(sp, cache, ra, rt)
                    if not match:
                        match = fuzzy_search(sp, cache, f'{ra} {rt}')
                    artist = ra
                    title = rt

        if match:
            track_id = match['id']
            if track_id not in added_tracks:
                add_to_playlist(sp, playlists, user_id, 'Spotify', track_id)
                added_tracks.add(track_id)
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

        if window:
            window.refresh()

    write_html_report(entries, dst / 'report.html')
    save_cache(cache)
