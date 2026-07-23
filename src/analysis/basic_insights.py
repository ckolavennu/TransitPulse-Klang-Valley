"""Generate first summary tables for TransitPulse Klang Valley.

Inputs:
    data/processed/daily_ridership_long.parquet
    data/processed/rapidrail_od_clean.parquet
    data/processed/station_summary.parquet
    data/processed/station_pair_summary.parquet

Outputs:
    data/processed/monthly_ridership_summary.csv
    data/processed/service_summary.csv
    data/processed/top_origin_stations.csv
    data/processed/top_destination_stations.csv
    data/processed/top_station_pairs.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from config import PROCESSED_DATA_DIR, ensure_directories  # noqa: E402


RIDERSHIP_LONG_FILE = PROCESSED_DATA_DIR / "daily_ridership_long.parquet"
OD_FILE = PROCESSED_DATA_DIR / "rapidrail_od_clean.parquet"
STATION_SUMMARY_FILE = PROCESSED_DATA_DIR / "station_summary.parquet"
PAIR_SUMMARY_FILE = PROCESSED_DATA_DIR / "station_pair_summary.parquet"


def require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Run the data cleaning scripts before this analysis step."
        )


def main() -> None:
    ensure_directories()

    for path in [
        RIDERSHIP_LONG_FILE,
        OD_FILE,
        STATION_SUMMARY_FILE,
        PAIR_SUMMARY_FILE,
    ]:
        require_file(path)

    ridership = pd.read_parquet(RIDERSHIP_LONG_FILE)
    od = pd.read_parquet(OD_FILE)
    stations = pd.read_parquet(STATION_SUMMARY_FILE)
    pairs = pd.read_parquet(PAIR_SUMMARY_FILE)

    monthly_ridership = (
        ridership.groupby(["month", "service"], as_index=False)["ridership"]
        .sum()
        .sort_values(["month", "ridership"], ascending=[True, False])
    )
    monthly_ridership.to_csv(
        PROCESSED_DATA_DIR / "monthly_ridership_summary.csv", index=False
    )

    service_summary = (
        ridership.groupby("service", as_index=False)["ridership"]
        .agg(total_trips="sum", average_daily_trips="mean", max_daily_trips="max")
        .sort_values("total_trips", ascending=False)
    )
    service_summary.to_csv(PROCESSED_DATA_DIR / "service_summary.csv", index=False)

    top_origins = (
        od.groupby(["origin_code", "origin_name"], as_index=False)["ridership"]
        .sum()
        .rename(columns={"ridership": "outbound_trips"})
        .sort_values("outbound_trips", ascending=False)
        .head(50)
    )
    top_origins.to_csv(PROCESSED_DATA_DIR / "top_origin_stations.csv", index=False)

    top_destinations = (
        od.groupby(["destination_code", "destination_name"], as_index=False)["ridership"]
        .sum()
        .rename(columns={"ridership": "inbound_trips"})
        .sort_values("inbound_trips", ascending=False)
        .head(50)
    )
    top_destinations.to_csv(
        PROCESSED_DATA_DIR / "top_destination_stations.csv", index=False
    )

    top_pairs = pairs.head(100)
    top_pairs.to_csv(PROCESSED_DATA_DIR / "top_station_pairs.csv", index=False)

    print("Generated summary files:")
    print("- monthly_ridership_summary.csv")
    print("- service_summary.csv")
    print("- top_origin_stations.csv")
    print("- top_destination_stations.csv")
    print("- top_station_pairs.csv")

    print("\nFirst quick findings:")
    if not service_summary.empty:
        top_service = service_summary.iloc[0]
        print(
            f"Top service by total trips: {top_service['service']} "
            f"({top_service['total_trips']:,.0f} trips)"
        )
    if not stations.empty:
        top_station = stations.iloc[0]
        print(
            f"Top station by total activity: {top_station['station_name']} "
            f"({top_station['total_station_activity']:,.0f} trips)"
        )
    if not pairs.empty:
        top_pair = pairs.iloc[0]
        print(
            f"Top station pair: {top_pair['origin_name']} → {top_pair['destination_name']} "
            f"({top_pair['ridership']:,.0f} trips)"
        )


if __name__ == "__main__":
    main()
