"""Low-memory helpers for Prasarana Rapid Rail KL GTFS Static data."""

from __future__ import annotations

from io import BytesIO
import zipfile

import pandas as pd
import requests

GTFS_URL = "https://api.data.gov.my/gtfs-static/prasarana?category=rapid-rail-kl"
USER_AGENT = "TransitPulse-Klang-Valley/1.0"


def _download(timeout: int = 20) -> bytes:
    response = requests.get(
        GTFS_URL,
        timeout=timeout,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response.content


def _read_csv(archive: zipfile.ZipFile, name: str, **kwargs) -> pd.DataFrame:
    if name not in archive.namelist():
        raise ValueError(f"GTFS feed is missing required file: {name}")
    return pd.read_csv(archive.open(name), **kwargs)


def fetch_rapid_rail_core(
    timeout: int = 20,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return only stops and routes.

    This is the lightweight path used by the commuter and planning views.
    Malaysia's current Rapid Rail feed exposes ``route_id`` in ``stops.txt``.
    If a future feed removes it, we fall back to the standard
    ``stop_times.txt -> trips.txt`` relationship.
    """
    payload = _download(timeout)
    with zipfile.ZipFile(BytesIO(payload)) as archive:
        stops = _read_csv(
            archive,
            "stops.txt",
            dtype={"stop_id": str, "stop_code": str, "parent_station": str, "route_id": str},
        )
        routes = _read_csv(
            archive,
            "routes.txt",
            dtype={
                "route_id": str,
                "route_short_name": str,
                "route_long_name": str,
                "route_color": str,
            },
        )

        if "route_id" not in stops.columns or stops["route_id"].isna().all():
            trips = _read_csv(
                archive,
                "trips.txt",
                usecols=["trip_id", "route_id"],
                dtype={"trip_id": str, "route_id": str},
            )
            stop_times = _read_csv(
                archive,
                "stop_times.txt",
                usecols=["trip_id", "stop_id"],
                dtype={"trip_id": str, "stop_id": str},
            )
            stop_routes = (
                stop_times.merge(
                    trips.dropna().drop_duplicates(),
                    on="trip_id",
                    how="left",
                )[["stop_id", "route_id"]]
                .dropna()
                .drop_duplicates()
            )
            stops = stops.drop(columns=["route_id"], errors="ignore").merge(
                stop_routes,
                on="stop_id",
                how="left",
            )

    stops["stop_lat"] = pd.to_numeric(stops["stop_lat"], errors="coerce")
    stops["stop_lon"] = pd.to_numeric(stops["stop_lon"], errors="coerce")
    stops = stops.dropna(subset=["stop_lat", "stop_lon"]).copy()
    stops["route_id"] = stops["route_id"].astype("string")

    if stops.empty:
        raise ValueError("GTFS stops feed returned no usable station coordinates")

    return stops, routes


def fetch_rapid_rail_geometry(
    timeout: int = 25,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return routes, trips and shapes for optional line geometry rendering."""
    payload = _download(timeout)
    with zipfile.ZipFile(BytesIO(payload)) as archive:
        routes = _read_csv(
            archive,
            "routes.txt",
            dtype={
                "route_id": str,
                "route_short_name": str,
                "route_long_name": str,
                "route_color": str,
            },
        )
        trips = _read_csv(
            archive,
            "trips.txt",
            dtype={"route_id": str, "trip_id": str, "shape_id": str},
        )
        shapes = _read_csv(
            archive,
            "shapes.txt",
            dtype={"shape_id": str},
        )

    shapes["shape_pt_lat"] = pd.to_numeric(shapes["shape_pt_lat"], errors="coerce")
    shapes["shape_pt_lon"] = pd.to_numeric(shapes["shape_pt_lon"], errors="coerce")
    shapes["shape_pt_sequence"] = pd.to_numeric(
        shapes["shape_pt_sequence"], errors="coerce"
    )
    shapes = shapes.dropna(
        subset=["shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"]
    ).copy()
    return routes, trips, shapes


def fetch_rapid_rail_gtfs(
    timeout: int = 25,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compatibility wrapper returning stops, routes, trips and shapes."""
    stops, routes = fetch_rapid_rail_core(timeout=timeout)
    _, trips, shapes = fetch_rapid_rail_geometry(timeout=timeout)
    return stops, routes, trips, shapes
