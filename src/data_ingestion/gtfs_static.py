"""Utilities for loading Prasarana Rapid Rail KL GTFS Static data."""

from __future__ import annotations

from io import BytesIO
import zipfile

import pandas as pd
import requests

GTFS_URL = "https://api.data.gov.my/gtfs-static/prasarana?category=rapid-rail-kl"


def fetch_rapid_rail_gtfs(timeout: int = 35) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return stops, routes, trips and shapes from the official Rapid Rail KL GTFS feed."""
    response = requests.get(
        GTFS_URL,
        timeout=timeout,
        headers={"User-Agent": "TransitPulse-Klang-Valley/1.0"},
    )
    response.raise_for_status()

    with zipfile.ZipFile(BytesIO(response.content)) as archive:
        stops = pd.read_csv(
            archive.open("stops.txt"),
            dtype={"stop_id": str, "route_id": str},
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
        shapes = pd.read_csv(
            archive.open("shapes.txt"),
            dtype={"shape_id": str},
        )

    stops["stop_lat"] = pd.to_numeric(stops["stop_lat"], errors="coerce")
    stops["stop_lon"] = pd.to_numeric(stops["stop_lon"], errors="coerce")
    shapes["shape_pt_lat"] = pd.to_numeric(shapes["shape_pt_lat"], errors="coerce")
    shapes["shape_pt_lon"] = pd.to_numeric(shapes["shape_pt_lon"], errors="coerce")
    shapes["shape_pt_sequence"] = pd.to_numeric(shapes["shape_pt_sequence"], errors="coerce")

    stops = stops.dropna(subset=["stop_lat", "stop_lon"]).copy()
    shapes = shapes.dropna(
        subset=["shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"]
    ).copy()

    return stops, routes, trips, shapes
