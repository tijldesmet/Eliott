# MP3 Playlist Organizer

This tool scans a directory for MP3 files, matches them with Spotify tracks, and
organizes files into playlists. Unmatched tracks are moved to a "Napster"
folder with a local playlist.

The GUI is implemented in Python with PySimpleGUI in a dark theme.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables for API credentials:
   - `SPOTIPY_CLIENT_ID`
   - `SPOTIPY_CLIENT_SECRET`
   - `SPOTIPY_REDIRECT_URI`
   - `AUDD_API_KEY`

3. Run the program:
   ```bash
   python src/main.py
   ```

## Features

- Choose source and output folders.
- Creates `Spotify` and `Napster` subfolders in the output folder if they do not
  exist.
- Adds tracks to Spotify playlists with automatic splitting after 10,000 items.
- Falls back to audD for audio recognition when no match is found.
- Uses fuzzy matching for approximate matches.
- Generates a simple HTML report listing processed files.

This is a minimal proof-of-concept implementation and does not include all
error handling or optimizations.
