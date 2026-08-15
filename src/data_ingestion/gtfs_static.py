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

    The Malaysia feed currently includes a non-standard ``route_id`` column in
    ``stops.txt`` as well as the standard trip/stop relationships. TransitPulse
    derives stop-to-route membership from ``stop_times.txt -> trips.txt`` so the
    app remains compatible with standard GTFS feeds too. Any pre-existing
    ``route_id`` in ``stops.txt`` is removed before that derived relationship is
    attached, avoiding pandas creating ``route_id_x``/``route_id_y`` columns.
    """
    response = requests.get(
        GTFS_URL,
        timeout=timeout,
        headers={"User-Agent": "TransitPulse-Klang-Valley/1.0"},
    )
    response.raise_for_status()

    with zipfile.ZipFile(BytesIO(response.content)) as archive:
        names = set(archive.namelist())
        required = {
            "stops.txt",
            "routes.txt",
            "trips.txt",
            "stop_times.txt",
            "shapes.txt",
        }
        missing = required.difference(names)
        if missing:
            raise ValueError(f"GTFS feed is missing required files: {sorted(missing)}")

        stops_base = pd.read_csv(
            archive.open("stops.txt"),
            dtype={"stop_id": str, "stop_code": str, "parent_station": str},
        )
        routes = pd.read_csv(
            archive.open("routes.txt"),
            dtype={
                "route_id": str,
                "route_short_name": str,
                "route_long_name": str,
                "route_color": str,
            },
        )
        trips = pd.read_csv(
            archive.open("trips.txt"),
            dtype={"route_id": str, "trip_id": str, "shape_id": str},
        )
        stop_times = pd.read_csv(
            archive.open("stop_times.txt"),
            usecols=["trip_id", "stop_id"],
            dtype={"trip_id": str, "stop_id": str},
        )
        shapes = pd.read_csv(
            archive.open("shapes.txt"),
            dtype={"shape_id": str},
        )

    expected_trip_columns = {"trip_id", "route_id"}
    missing_trip_columns = expected_trip_columns.difference(trips.columns)
    if missing_trip_columns:
        raise ValueError(
            f"GTFS trips.txt is missing required columns: {sorted(missing_trip_columns)}"
        )

    # Some Malaysia GTFS feeds include route_id directly in stops.txt. Remove it
    # before merging the standard-derived relationship so the output always has
    # one canonical `route_id` column rather than route_id_x/route_id_y.
    stops_base = stops_base.drop(columns=["route_id"], errors="ignore")

    stop_routes = (
        stop_times.merge(
            trips[["trip_id", "route_id"]].dropna().drop_duplicates(),
            on="trip_id",
            how="left",
        )[["stop_id", "route_id"]]
        .dropna()
        .drop_duplicates()
    )

    stops = stops_base.merge(stop_routes, on="stop_id", how="left")

    if "route_id" not in stops.columns:
        raise ValueError("Could not derive route_id for GTFS stops")

    stops["stop_lat"] = pd.to_numeric(stops["stop_lat"], errors="coerce")
    stops["stop_lon"] = pd.to_numeric(stops["stop_lon"], errors="coerce")
    shapes["shape_pt_lat"] = pd.to_numeric(shapes["shape_pt_lat"], errors="coerce")
    shapes["shape_pt_lon"] = pd.to_numeric(shapes["shape_pt_lon"], errors="coerce")
    shapes["shape_pt_sequence"] = pd.to_numeric(
        shapes["shape_pt_sequence"], errors="coerce"
    )

    stops = stops.dropna(subset=["stop_lat", "stop_lon"]).copy()
    shapes = shapes.dropna(
        subset=["shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"]
    ).copy()

    return stops, routes, trips, shapes
