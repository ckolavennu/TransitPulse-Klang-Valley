"""Project configuration for TransitPulse Klang Valley."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

DATA_SOURCES = {
    "ridership_headline": {
        "description": "Daily public transport ridership across Malaysia.",
        "url": "https://storage.data.gov.my/transportation/ridership_headline.parquet",
        "filename": "ridership_headline.parquet",
    },
    "rapidrail_od_2026": {
        "description": "Daily origin-destination ridership for Rapid Rail Klang Valley, 2026.",
        "url": "https://storage.data.gov.my/transportation/rail/rapidrail_2026_daily.parquet",
        "filename": "rapidrail_2026_daily.parquet",
    },
}


def ensure_directories() -> None:
    """Create project data and output directories if they do not exist."""
    for path in [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        EXTERNAL_DATA_DIR,
        OUTPUTS_DIR,
        OUTPUTS_DIR / "charts",
        OUTPUTS_DIR / "maps",
        OUTPUTS_DIR / "reports",
    ]:
        path.mkdir(parents=True, exist_ok=True)
