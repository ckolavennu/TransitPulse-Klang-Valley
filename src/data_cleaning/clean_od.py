"""Clean Rapid Rail daily origin-destination ridership data.

Input:
    data/raw/rapidrail_2026_daily.parquet

Outputs:
    data/processed/rapidrail_od_clean.parquet
    data/processed/station_summary.parquet
    data/processed/station_pair_summary.parquet
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from config import PROCESSED_DATA_DIR, RAW_DATA_DIR, ensure_directories  # noqa: E402


RAW_FILE = RAW_DATA_DIR / "rapidrail_2026_daily.parquet"
CLEAN_FILE = PROCESSED_DATA_DIR / "rapidrail_od_clean.parquet"
STATION_SUMMARY_FILE = PROCESSED_DATA_DIR / "station_summary.parquet"
PAIR_SUMMARY_FILE = PROCESSED_DATA_DIR / "station_pair_summary.parquet"

STATION_PATTERN = re.compile(r"^\s*([^:]+):\s*(.+?)\s*$")


def split_station(value: object) -> tuple[str | None, str]:
    """Split station string such as 'KJ15: KL Sentral' into code and name."""
    text = str(value).strip()
    match = STATION_PATTERN.match(text)
    if not match:
        return None, text
    return match.group(1).strip(), match.group(2).strip()


def main() -> None:
    ensure_directories()

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Missing {RAW_FILE}. Run: python src/data_ingestion/download_data.py"
        )

    df = pd.read_parquet(RAW_FILE)

    expected_columns = {"date", "origin", "destination", "ridership"}
    missing_columns = expected_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(f"Missing expected columns: {sorted(missing_columns)}")

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["ridership"] = pd.to_numeric(df["ridership"], errors="coerce").fillna(0).astype(int)

    origin_split = df["origin"].apply(split_station)
    destination_split = df["destination"].apply(split_station)

    df["origin_code"] = origin_split.apply(lambda x: x[0])
    df["origin_name"] = origin_split.apply(lambda x: x[1])
    df["destination_code"] = destination_split.apply(lambda x: x[0])
    df["destination_name"] = destination_split.apply(lambda x: x[1])

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["day_name"] = df["date"].dt.day_name()
    df["is_weekend"] = df["day_name"].isin(["Saturday", "Sunday"])

    df.to_parquet(CLEAN_FILE, index=False)

    origin_summary = (
        df.groupby(["origin_code", "origin_name"], dropna=False)["ridership"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "origin_code": "station_code",
                "origin_name": "station_name",
                "ridership": "outbound_trips",
            }
        )
    )

    destination_summary = (
        df.groupby(["destination_code", "destination_name"], dropna=False)["ridership"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "destination_code": "station_code",
                "destination_name": "station_name",
                "ridership": "inbound_trips",
            }
        )
    )

    station_summary = origin_summary.merge(
        destination_summary,
        on=["station_code", "station_name"],
        how="outer",
    ).fillna(0)

    station_summary["total_station_activity"] = (
        station_summary["outbound_trips"] + station_summary["inbound_trips"]
    )
    station_summary = station_summary.sort_values(
        "total_station_activity", ascending=False
    ).reset_index(drop=True)

    station_summary.to_parquet(STATION_SUMMARY_FILE, index=False)

    pair_summary = (
        df.groupby(
            [
                "origin_code",
                "origin_name",
                "destination_code",
                "destination_name",
            ],
            dropna=False,
        )["ridership"]
        .sum()
        .reset_index()
        .sort_values("ridership", ascending=False)
        .reset_index(drop=True)
    )

    pair_summary.to_parquet(PAIR_SUMMARY_FILE, index=False)

    print(f"Saved cleaned OD data: {CLEAN_FILE}")
    print(f"Saved station summary: {STATION_SUMMARY_FILE}")
    print(f"Saved station pair summary: {PAIR_SUMMARY_FILE}")
    print(f"Rows in OD data: {len(df):,}")


if __name__ == "__main__":
    main()
