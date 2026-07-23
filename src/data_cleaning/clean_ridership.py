"""Clean the Daily Public Transport Ridership dataset.

Input:
    data/raw/ridership_headline.parquet

Output:
    data/processed/daily_ridership_clean.parquet
    data/processed/daily_ridership_long.parquet
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from config import PROCESSED_DATA_DIR, RAW_DATA_DIR, ensure_directories  # noqa: E402


RAW_FILE = RAW_DATA_DIR / "ridership_headline.parquet"
CLEAN_FILE = PROCESSED_DATA_DIR / "daily_ridership_clean.parquet"
LONG_FILE = PROCESSED_DATA_DIR / "daily_ridership_long.parquet"


def clean_service_name(column_name: str) -> str:
    """Convert raw service column names into readable labels."""
    return (
        column_name.replace("rail_", "")
        .replace("bus_", "bus_")
        .replace("_", " ")
        .title()
    )


def main() -> None:
    ensure_directories()

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Missing {RAW_FILE}. Run: python src/data_ingestion/download_data.py"
        )

    df = pd.read_parquet(RAW_FILE)

    if "date" not in df.columns:
        raise ValueError("Expected a 'date' column in ridership_headline dataset.")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Save cleaned wide-format file.
    df.to_parquet(CLEAN_FILE, index=False)

    # Convert to long format for charts and filters.
    service_columns = [column for column in df.columns if column != "date"]
    long_df = df.melt(
        id_vars="date",
        value_vars=service_columns,
        var_name="service_raw",
        value_name="ridership",
    )

    long_df["service"] = long_df["service_raw"].apply(clean_service_name)
    long_df["ridership"] = pd.to_numeric(long_df["ridership"], errors="coerce").fillna(0)
    long_df["year"] = long_df["date"].dt.year
    long_df["month"] = long_df["date"].dt.to_period("M").astype(str)
    long_df["day_name"] = long_df["date"].dt.day_name()
    long_df["is_weekend"] = long_df["day_name"].isin(["Saturday", "Sunday"])

    long_df.to_parquet(LONG_FILE, index=False)

    print(f"Saved cleaned wide data: {CLEAN_FILE}")
    print(f"Saved cleaned long data: {LONG_FILE}")
    print(f"Rows in long data: {len(long_df):,}")


if __name__ == "__main__":
    main()
