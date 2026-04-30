# Super Friday Chart Exporter

A lightweight Python script that exports the full current chart from <a href="https://www.superfridaychart.com" target="_blank" rel="noopener noreferrer">superfridaychart.com</a> across every paginated page, then writes results to text files.

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

## Disclaimer

Use responsibly and respect the website's terms of use and rate limits.
