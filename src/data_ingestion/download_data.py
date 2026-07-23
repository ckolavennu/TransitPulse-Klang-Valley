"""Download the initial official datasets for TransitPulse Klang Valley.

Usage:
    python src/data_ingestion/download_data.py

The script downloads files into data/raw/.
"""

from __future__ import annotations

import sys
from pathlib import Path

import requests
from tqdm import tqdm

# Allow running this file directly from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from config import DATA_SOURCES, RAW_DATA_DIR, ensure_directories  # noqa: E402


CHUNK_SIZE = 1024 * 1024


def download_file(url: str, destination: Path, overwrite: bool = False) -> None:
    """Download a file from a URL to a local path."""
    if destination.exists() and not overwrite:
        print(f"Already exists, skipping: {destination}")
        return

    print(f"Downloading: {url}")
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    progress = tqdm(total=total_size, unit="B", unit_scale=True, desc=destination.name)

    with destination.open("wb") as file:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                file.write(chunk)
                progress.update(len(chunk))

    progress.close()
    print(f"Saved to: {destination}")


def main() -> None:
    ensure_directories()

    for source_name, source in DATA_SOURCES.items():
        destination = RAW_DATA_DIR / source["filename"]
        try:
            download_file(source["url"], destination)
        except requests.HTTPError as error:
            print(f"Failed to download {source_name}: {error}")
        except requests.RequestException as error:
            print(f"Network error while downloading {source_name}: {error}")


if __name__ == "__main__":
    main()
