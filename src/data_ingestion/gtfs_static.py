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

    Standard GTFS ``stops.txt`` does not contain a route_id. TransitPulse needs a
    stop-to-route relationship for accessibility scoring, so this loader derives
    it by joining ``stop_times.txt`` to ``trips.txt`` and then attaches route_id
    to each stop. A physical stop may therefore appear once per served route.
    """
    response = requests.get(
        GTFS_URL,
        timeout=timeout,
        headers={"User-Agent": "TransitPulse-Klang-Valley/1.0"},
    )
    response.raise_for_status()

    with zipfile.ZipFile(BytesIO(response.content)) as archive:
        names = set(archive.namelist())
        required = {"stops.txt", "routes.txt", "trips.txt", "stop_times.txt", "shapes.txt"}
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

    # Derive stop -> route membership using stop_times -> trips.
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
