"""Utilities for loading Prasarana Rapid Rail KL GTFS Static data."""

from __future__ import annotations

from io import BytesIO
import zipfile

import pandas as pd
import requests

GTFS_URL = "https://api.data.gov.my/gtfs-static/prasarana?category=rapid-rail-kl"


def fetch_rapid_rail_gtfs(
    timeout: int = 35,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return stops, routes, trips and shapes from the official Rapid Rail KL GTFS feed.

    data.gov.my currently includes a non-standard ``route_id`` column in
    ``stops.txt``. TransitPulse uses that lightweight relationship when present.
    For standard GTFS feeds that omit it, the loader falls back to deriving
    stop-to-route membership from ``stop_times.txt -> trips.txt``.

    Avoiding ``stop_times.txt`` on the normal data.gov.my path substantially
    reduces startup memory on Streamlit Community Cloud.
    """
    response = requests.get(
        GTFS_URL,
        timeout=timeout,
        headers={"User-Agent": "TransitPulse-Klang-Valley/1.0"},
    )
    response.raise_for_status()

    with zipfile.ZipFile(BytesIO(response.content)) as archive:
        names = set(archive.namelist())
        required = {"stops.txt", "routes.txt", "trips.txt", "shapes.txt"}
        missing = required.difference(names)
        if missing:
            raise ValueError(f"GTFS feed is missing required files: {sorted(missing)}")

        stops_base = pd.read_csv(
            archive.open("stops.txt"),
            dtype={
                "stop_id": str,
                "stop_code": str,
                "parent_station": str,
                "route_id": str,
            },
        )
        routes = pd.read_csv(
            archive.open("routes.txt"),
            usecols=lambda c: c
            in {"route_id", "route_short_name", "route_long_name", "route_color"},
            dtype={
                "route_id": str,
                "route_short_name": str,
                "route_long_name": str,
                "route_color": str,
            },
        )
        trips = pd.read_csv(
            archive.open("trips.txt"),
            usecols=lambda c: c in {"route_id", "trip_id", "shape_id"},
            dtype={"route_id": str, "trip_id": str, "shape_id": str},
        )
        shapes = pd.read_csv(
            archive.open("shapes.txt"),
            usecols=lambda c: c
            in {"shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"},
            dtype={"shape_id": str},
        )

        if "route_id" in stops_base.columns and stops_base["route_id"].notna().any():
            # Malaysia-specific extension: keep only the columns used downstream.
            keep = [
                c
                for c in ["stop_id", "stop_code", "stop_name", "stop_lat", "stop_lon", "route_id"]
                if c in stops_base.columns
            ]
            stops = stops_base[keep].copy()
        else:
            if "stop_times.txt" not in names:
                raise ValueError(
                    "GTFS stops do not contain route_id and stop_times.txt is unavailable"
                )
            stop_times = pd.read_csv(
                archive.open("stop_times.txt"),
                usecols=["trip_id", "stop_id"],
                dtype={"trip_id": str, "stop_id": str},
            )
            stop_routes = (
                stop_times.merge(
                    trips[["trip_id", "route_id"]].dropna().drop_duplicates(),
                    on="trip_id",
                    how="left",
                )[["stop_id", "route_id"]]
                .dropna()
                .drop_duplicates()
            )
            stops_base = stops_base.drop(columns=["route_id"], errors="ignore")
            stops = stops_base.merge(stop_routes, on="stop_id", how="left")

    if "route_id" not in stops.columns:
        raise ValueError("Could not determine route_id for GTFS stops")

    stops["stop_lat"] = pd.to_numeric(stops["stop_lat"], errors="coerce")
    stops["stop_lon"] = pd.to_numeric(stops["stop_lon"], errors="coerce")
    shapes["shape_pt_lat"] = pd.to_numeric(shapes["shape_pt_lat"], errors="coerce")
    shapes["shape_pt_lon"] = pd.to_numeric(shapes["shape_pt_lon"], errors="coerce")
    shapes["shape_pt_sequence"] = pd.to_numeric(
        shapes["shape_pt_sequence"], errors="coerce"
    )

    stops = stops.dropna(subset=["stop_lat", "stop_lon", "route_id"]).copy()
    shapes = shapes.dropna(
        subset=["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"]
    ).copy()

    return stops, routes, trips, shapes
