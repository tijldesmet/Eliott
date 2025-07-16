from pathlib import Path
from typing import Optional

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

import time

import shutil
main
from .utils import load_cache, save_cache, sanitize_filename, unique_path
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

    def on_wait(remaining: int):
        if window:
            window['STATUS'].update(f'Rate limit hit, waiting {remaining}s...')
            window.refresh()

    playlists = ensure_playlists(sp, user_id, 'Spotify', on_wait=on_wait)

    spotify_dir = dst / 'Spotify'
    napster_dir = dst / 'Napster'
    spotify_dir.mkdir(parents=True, exist_ok=True)
    napster_dir.mkdir(parents=True, exist_ok=True)
    napster_playlist = napster_dir / 'Napster.m3u'

    files = [f for f in src.iterdir() if f.suffix.lower() == '.mp3']
    total = len(files)
    start_time = time.time()

    entries = []
    added_tracks = set()

    for i, file in enumerate(files, 1):
        if window:
            elapsed = time.time() - start_time
            est_total = (elapsed / i) * total if i else 0
            remaining = max(0, int(est_total - elapsed))
            window['PROG'].update(current_count=i, max=total)
            window['STATUS'].update(
                f'Processing {file.name} ({i}/{total}) - ETA {remaining}s'
            )

        try:
            tags = EasyID3(file)
            artist = tags.get('artist', [None])[0]
            title = tags.get('title', [None])[0]
            album = tags.get('album', [''])[0]
            year = tags.get('date', [''])[0]
            genre = tags.get('genre', [''])[0]
        except ID3NoHeaderError:
            artist = title = None
            album = year = genre = ''

        if not artist or not title:
            parts = file.stem.split('-')
            if len(parts) >= 2:
                artist = artist or parts[0].strip()
                title = title or parts[1].strip()

        match = None
        if artist and title:
            match = search(sp, cache, artist, title, on_wait=on_wait)
            if not match:
                match = fuzzy_search(sp, cache, f'{artist} {title}', on_wait=on_wait)
        if not match:
            # Pass ``None`` explicitly so tests with monkeypatched recognize
            # function expecting two arguments continue to work.
            ra, rt = recognize(str(file), None)
            if ra and rt:
                match = search(sp, cache, ra, rt, on_wait=on_wait)
                if not match:
                    match = fuzzy_search(sp, cache, f'{ra} {rt}', on_wait=on_wait)
                artist = ra
                title = rt
                try:
                    tags = EasyID3(file)
                except ID3NoHeaderError:
                    tags = EasyID3()
                tags['artist'] = artist.title()
                tags['title'] = title.title()
                tags.save(file)

        if match:
            track_id = match['id']
            if track_id not in added_tracks:
                add_to_playlist(sp, playlists, user_id, 'Spotify', track_id, on_wait=on_wait)
                added_tracks.add(track_id)
            dest_name = sanitize_filename(f"{artist} - {title}") + file.suffix
            dest = unique_path(spotify_dir / dest_name)
            shutil.move(str(file), dest)
            rel_path = dest.relative_to(dst)
            entries.append(
                {
                    'artist': artist or '',
                    'title': title or '',
                    'album': album,
                    'year': year,
                    'genre': genre,
                    'dest': 'Spotify',
                    'path': str(rel_path),
                }
            )
        else:
            dest_name = sanitize_filename(file.stem) + file.suffix
            dest = unique_path(napster_dir / dest_name)
codex/voer-audit-uit-en-update-code
            shutil.move(str(file), dest)
            with open(napster_playlist, 'a', encoding='utf-8') as m3u:
                m3u.write(dest.name + '\n')
            rel_path = dest.relative_to(dst)
            entries.append(
                {
                    'artist': artist or '',
                    'title': title or '',
                    'album': album,
                    'year': year,
                    'genre': genre,
                    'dest': 'Napster',
                    'path': str(rel_path),
                }
            )

        if window:
            window.refresh()

    write_html_report(entries, dst / 'report.html')
    save_cache(cache)

