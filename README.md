# Super Friday Chart Exporter

A lightweight Python script that exports the full current chart from [superfridaychart.com](https://www.superfridaychart.com) across every paginated page, then writes results to text files.

## What It Does

- Scrapes all pages of the current chart (not only the first 50 entries)
- Creates a detailed export file with rank and stats
- Creates a second names-only export file with song + artist
- Supports custom output filenames from the command line

## Requirements

- Python 3.9+
- Internet access
- No third-party Python packages required

## Project Files

- `export_super_friday_chart.py`: main exporter script
- `super_friday_chart_all_entries.txt`: default detailed output
- `super_friday_chart_all_entries_song_artist_only.txt`: default names-only output

## Quick Start

From this folder, run:

```bash
/usr/bin/python3 export_super_friday_chart.py
```

This generates:

- `super_friday_chart_all_entries.txt`
- `super_friday_chart_all_entries_song_artist_only.txt`

## Usage

```bash
/usr/bin/python3 export_super_friday_chart.py [options]
```

### Options

- `--url`: Base chart URL (default: `https://www.superfridaychart.com/`)
- `--output`: Detailed output path (default: `super_friday_chart_all_entries.txt`)
- `--names-only-output`: Names-only output path (default: derived from `--output`)
- `--timeout`: Request timeout in seconds (default: `20`)
- `--delay`: Delay between page requests in seconds (default: `0.1`)

## Examples

Generate defaults:

```bash
/usr/bin/python3 export_super_friday_chart.py
```

Custom detailed file:

```bash
/usr/bin/python3 export_super_friday_chart.py --output full_chart.txt
```

Custom names-only file:

```bash
/usr/bin/python3 export_super_friday_chart.py --names-only-output song_artist_list.txt
```

Custom both files:

```bash
/usr/bin/python3 export_super_friday_chart.py --output full_chart.txt --names-only-output song_artist_list.txt
```

Slower crawl to be extra polite to the site:

```bash
/usr/bin/python3 export_super_friday_chart.py --delay 0.3
```

## Output Format

Detailed file line format:

```text
#<rank> | <track> | <artists> | playlists: <count> | followers: <count> | page: <page_number>
```

Names-only file line format:

```text
<track> | <artists>
```

## Notes

- The script auto-detects the last page using pagination links.
- Output reflects the chart state at the time of execution.
- If the site markup changes, parser updates may be needed.

---

## Spotify Playlist Creator

`create_spotify_playlist.py` takes a names-only export and automatically creates a Spotify playlist with every matched song.

### One-time Setup

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) and create a new app.
2. In the app's **Settings → Redirect URIs**, add exactly:
   ```
   http://localhost:8888/callback
   ```
3. Copy your **Client ID** and **Client Secret**.

### Usage

```bash
/usr/bin/python3 create_spotify_playlist.py \
  --input super_friday_chart_all_entries_song_artist_only.txt \
  --playlist-name "Super Friday Chart" \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_CLIENT_SECRET
```

Or export credentials as environment variables:

```bash
export SPOTIFY_CLIENT_ID=your_id
export SPOTIFY_CLIENT_SECRET=your_secret
/usr/bin/python3 create_spotify_playlist.py
```

### Options

- `--input`: Names-only file to read (default: `super_friday_chart_all_entries_song_artist_only.txt`)
- `--playlist-name`: Name for the new Spotify playlist (default: `Super Friday Chart`)
- `--client-id`: Spotify app Client ID
- `--client-secret`: Spotify app Client Secret
- `--delay`: Delay between search requests in seconds (default: `0.05`)

### What Happens

1. A browser tab opens asking you to authorize the app.
2. Each song is searched on Spotify by track and artist name.
3. A new public playlist is created on your account.
4. All matched tracks are added in batches.
5. Any songs not found on Spotify are written to a `_not_found_on_spotify.txt` file alongside the input.

---

## Disclaimer

Use responsibly and respect both the website's and Spotify's terms of use and rate limits.
