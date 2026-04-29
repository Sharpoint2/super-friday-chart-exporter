#!/usr/bin/env python3
"""Export all entries from the current Super Friday Chart into a text document."""

from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

BASE_URL = "https://www.superfridaychart.com/"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


@dataclass
class ChartEntry:
    rank: int
    track: str
    artists: str
    playlists: str
    followers: str
    page: int


def fetch_html(url: str, timeout: float) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def strip_tags(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text)
    return " ".join(text.split())


def discover_last_page(first_page_html: str) -> int:
    page_numbers = [int(value) for value in re.findall(r"[?&]page=(\d+)", first_page_html)]
    return max(page_numbers, default=1)


def extract_entries(page_html: str, page_number: int) -> list[ChartEntry]:
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", page_html, flags=re.DOTALL | re.IGNORECASE)
    entries: list[ChartEntry] = []

    for row_html in rows:
        if "/track/" not in row_html:
            continue

        rank_match = re.search(r"font-bold[^>]*>(\d+)\s*<", row_html)
        track_matches = re.findall(
            r'href="https://www\.superfridaychart\.com/track/[^"]+"[^>]*>(.*?)</a>',
            row_html,
            flags=re.DOTALL | re.IGNORECASE,
        )
        track_name = ""
        for candidate in track_matches:
            candidate_text = strip_tags(candidate)
            if candidate_text:
                track_name = candidate_text
                break

        if not rank_match or not track_name:
            continue

        artist_matches = re.findall(
            r'href="https://www\.superfridaychart\.com/artist/[^"]+"[^>]*>(.*?)</a>',
            row_html,
            flags=re.DOTALL | re.IGNORECASE,
        )

        cells = re.findall(r"<td[^>]*>(.*?)</td>", row_html, flags=re.DOTALL | re.IGNORECASE)
        if len(cells) < 4:
            continue

        playlists_match = re.search(r"(\d[\d,]*)", strip_tags(cells[2]))
        followers_match = re.search(r"(\d[\d,]*)", strip_tags(cells[3]))

        entries.append(
            ChartEntry(
                rank=int(rank_match.group(1)),
                track=track_name,
                artists=", ".join(strip_tags(value) for value in artist_matches) if artist_matches else "Unknown",
                playlists=playlists_match.group(1) if playlists_match else "N/A",
                followers=followers_match.group(1) if followers_match else "N/A",
                page=page_number,
            )
        )

    return entries


def dedupe_entries(entries: Iterable[ChartEntry]) -> list[ChartEntry]:
    seen: set[tuple[int, str, str]] = set()
    deduped: list[ChartEntry] = []

    for entry in entries:
        key = (entry.rank, entry.track, entry.artists)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(entry)

    return deduped


def write_output(output_path: Path, source_url: str, last_page: int, entries: list[ChartEntry]) -> None:
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "Super Friday Chart - Full Export",
        f"Source: {source_url}",
        f"Generated: {timestamp}",
        f"Pages scraped: {last_page}",
        f"Total entries: {len(entries)}",
        "",
    ]

    for entry in entries:
        lines.append(
            f"#{entry.rank} | {entry.track} | {entry.artists} | playlists: {entry.playlists} | followers: {entry.followers} | page: {entry.page}"
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_names_only_output(output_path: Path, entries: list[ChartEntry]) -> None:
    lines = [
        "Super Friday Chart - Song + Artist Export",
        f"Total entries: {len(entries)}",
        "",
    ]

    for entry in entries:
        lines.append(f"{entry.track} | {entry.artists}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(
    base_url: str,
    output_file: Path,
    names_only_output_file: Path | None,
    timeout: float,
    delay_seconds: float,
) -> int:
    first_page_url = base_url
    first_page_html = fetch_html(first_page_url, timeout=timeout)
    last_page = discover_last_page(first_page_html)

    all_entries: list[ChartEntry] = []

    for page_number in range(1, last_page + 1):
        page_url = first_page_url if page_number == 1 else urljoin(base_url, f"?page={page_number}")
        print(f"Scraping page {page_number}/{last_page}: {page_url}")

        try:
            page_html = fetch_html(page_url, timeout=timeout)
        except (HTTPError, URLError) as exc:
            print(f"Failed to fetch page {page_number}: {exc}", file=sys.stderr)
            return 1

        entries = extract_entries(page_html, page_number)
        all_entries.extend(entries)

        if delay_seconds > 0 and page_number < last_page:
            time.sleep(delay_seconds)

    deduped_entries = dedupe_entries(all_entries)
    deduped_entries.sort(key=lambda item: item.rank)

    write_output(output_file, base_url, last_page, deduped_entries)
    names_only_output = names_only_output_file or output_file.with_name(
        f"{output_file.stem}_song_artist_only{output_file.suffix}"
    )
    write_names_only_output(names_only_output, deduped_entries)

    print(f"Wrote {len(deduped_entries)} entries to {output_file}")
    print(f"Wrote {len(deduped_entries)} entries to {names_only_output}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export every entry from the current chart on superfridaychart.com into a text file."
    )
    parser.add_argument(
        "--url",
        default=BASE_URL,
        help="Chart base URL (default: https://www.superfridaychart.com/)",
    )
    parser.add_argument(
        "--output",
        default="super_friday_chart_all_entries.txt",
        help="Output text file path (default: super_friday_chart_all_entries.txt)",
    )
    parser.add_argument(
        "--names-only-output",
        default=None,
        help=(
            "Optional names-only output file path. "
            "Default: <output_stem>_song_artist_only<output_suffix>"
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="Request timeout in seconds (default: 20)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Delay between page requests in seconds (default: 0.1)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_file = Path(args.output).expanduser().resolve()
    names_only_output_file = (
        Path(args.names_only_output).expanduser().resolve()
        if args.names_only_output
        else None
    )

    try:
        return run(
            base_url=args.url,
            output_file=output_file,
            names_only_output_file=names_only_output_file,
            timeout=args.timeout,
            delay_seconds=args.delay,
        )
    except KeyboardInterrupt:
        print("Interrupted by user.", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
