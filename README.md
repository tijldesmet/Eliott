# MP3 Playlist Organizer

This project helps organize a collection of MP3 files and create Spotify playlists. Files that cannot be matched are moved to a `Napster` folder with a local playlist.

The application uses a dark themed PySimpleGUI interface and can be turned into a Windows executable with PyInstaller.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Provide API credentials via environment variables or the GUI settings dialog:
   - `SPOTIPY_CLIENT_ID`
   - `SPOTIPY_CLIENT_SECRET`
   - `SPOTIPY_REDIRECT_URI`
   - `AUDD_API_KEY`

3. Run the program:
   ```bash
   python src/main.py
   ```
   Use the **Settings** button in the GUI to enter credentials if you have not
   set the environment variables. Values are saved to `~/.mp3organizer_config`.

To build a standalone executable on Windows:
```bash
pyinstaller --onefile -w src/main.py
```
The resulting `dist/main.exe` can be used directly.

## Project Structure

```
mp3organizer/
    __init__.py
    audd.py          # audD.io helper
    core.py          # file processing logic
    gui.py           # PySimpleGUI interface
    report.py        # HTML report generation
    spotify.py       # Spotify API helpers
    utils.py         # cache and filename helpers
src/
    main.py          # entry point
```

## Features

- Choose source and output folders.
- Creates `Spotify` and `Napster` subfolders if needed.
- Automatically splits Spotify playlists after 10,000 items.
- Fuzzy matching and audD fallback for track recognition.
- Caches Spotify search results and handles API rate limits with a visible
  countdown while waiting.
- Duplicate tracks are skipped and Spotify playlists split every 10,000 songs.
- ID3 tags and filenames are corrected when recognized through audD.
- A progress bar shows percentage and estimated remaining time.

- Generates an HTML report of processed files including album, year and genre
  metadata, and allows audio preview directly in the browser.

### HTML Report

After processing, a `report.html` file is created in the output folder. It lists
each track with artist, title, album, year, genre and the destination folder.
Every row also contains an embedded audio player so the resulting files can be
played without leaving the browser.

- Generates an HTML report of processed files.

## Running Tests

Install the dependencies and execute `pytest` from the project root:

```bash
pip install -r requirements.txt
pytest
```

