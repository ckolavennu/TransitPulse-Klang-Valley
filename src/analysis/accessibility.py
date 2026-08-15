"""Accessibility and demand-access modelling for TransitPulse Klang Valley."""

from __future__ import annotations

import numpy as np
import pandas as pd


def normalize_station_name(value: object) -> str:
    text = str(value).lower().strip()
    keep = [char if char.isalnum() else " " for char in text]
    return " ".join("".join(keep).split())


def haversine_distances_km(
    lat: float,
    lon: float,
    target_lats: pd.Series | np.ndarray,
    target_lons: pd.Series | np.ndarray,
) -> np.ndarray:
    radius = 6371.0088
    lat1 = np.radians(float(lat))
    lon1 = np.radians(float(lon))
    lat2 = np.radians(np.asarray(target_lats, dtype=float))
    lon2 = np.radians(np.asarray(target_lons, dtype=float))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )
    return radius * 2 * np.arcsin(np.sqrt(a))


def percentile_score(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce").fillna(0)
    if numeric.nunique() <= 1:
        return pd.Series(np.full(len(numeric), 50.0), index=numeric.index)
    return numeric.rank(method="average", pct=True) * 100


def clean_hex(value: object, fallback: str = "2563EB") -> str:
    text = str(value).strip().replace("#", "")
    if len(text) == 6 and all(c in "0123456789abcdefABCDEF" for c in text):
        return text.upper()
    return fallback


def build_station_metrics(
    stops: pd.DataFrame,
    routes: pd.DataFrame,
    station_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Build station access, demand percentile and demand-access gap metrics."""
    stops = stops.copy()
    routes = routes.copy()

    stops["station_code"] = stops["stop_id"].astype(str).str.strip().str.upper()
    stops["station_name"] = stops["stop_name"].astype(str).str.strip()
    stops["route_id"] = stops["route_id"].astype(str).str.strip()

    stations = (
        stops.groupby(["station_code", "station_name"], as_index=False)
        .agg(stop_lat=("stop_lat", "mean"), stop_lon=("stop_lon", "mean"))
        .dropna(subset=["stop_lat", "stop_lon"])
    )

    route_label: dict[str, str] = {}
    for _, row in routes.iterrows():
        route_id = str(row.get("route_id", "")).strip()
        short = str(row.get("route_short_name", "")).strip()
        long = str(row.get("route_long_name", "")).strip()
        label = short if short and short.lower() != "nan" else long
        route_label[route_id] = label if label and label.lower() != "nan" else route_id

    code_routes = (
        stops.groupby("station_code")["route_id"]
        .apply(lambda s: sorted({str(x) for x in s.dropna() if str(x).strip()}))
        .to_dict()
    )
    route_stations = (
        stops.groupby("route_id")["station_code"]
        .apply(lambda s: set(s.dropna().astype(str)))
        .to_dict()
    )

    lats = stations["stop_lat"].to_numpy(float)
    lons = stations["stop_lon"].to_numpy(float)

    line_counts: list[int] = []
    direct_reach: list[int] = []
    nearby_800: list[int] = []
    nearby_1500: list[int] = []
    route_ids_out: list[list[str]] = []
    route_labels_out: list[list[str]] = []

    for _, row in stations.iterrows():
        distances = haversine_distances_km(
            float(row["stop_lat"]), float(row["stop_lon"]), lats, lons
        )
        codes_250 = set(stations.loc[distances <= 0.25, "station_code"].astype(str))
        codes_800 = set(stations.loc[distances <= 0.8, "station_code"].astype(str))
        codes_1500 = set(stations.loc[distances <= 1.5, "station_code"].astype(str))

        accessible_routes: set[str] = set()
        for code in codes_250:
            accessible_routes.update(code_routes.get(code, []))
        if not accessible_routes:
            accessible_routes.update(code_routes.get(str(row["station_code"]), []))

        reachable: set[str] = set()
        for route_id in accessible_routes:
            reachable.update(route_stations.get(route_id, set()))

        route_ids = sorted(accessible_routes)
        line_counts.append(len(route_ids))
        direct_reach.append(max(0, len(reachable) - 1))
        nearby_800.append(max(0, len(codes_800) - 1))
        nearby_1500.append(max(0, len(codes_1500) - 1))
        route_ids_out.append(route_ids)
        route_labels_out.append([route_label.get(r, r) for r in route_ids])

    stations["line_count"] = line_counts
    stations["direct_reach"] = direct_reach
    stations["nearby_stations_800m"] = nearby_800
    stations["nearby_stations_1500m"] = nearby_1500
    stations["route_ids"] = route_ids_out
    stations["route_labels"] = route_labels_out

    line_score = np.clip(stations["line_count"] / 3.0 * 100, 0, 100)
    reach_score = percentile_score(stations["direct_reach"])
    density_score = np.clip(stations["nearby_stations_800m"] / 4.0 * 100, 0, 100)
    stations["accessibility_score"] = (
        0.35 * line_score + 0.45 * reach_score + 0.20 * density_score
    ).round(1)
    stations["access_percentile"] = percentile_score(
        stations["accessibility_score"]
    ).round(1)

    demand = station_summary.copy()
    if not demand.empty:
        demand["station_code"] = demand["station_code"].astype(str).str.strip().str.upper()
        demand["station_name_key"] = demand["station_name"].map(normalize_station_name)
        stations["station_name_key"] = stations["station_name"].map(normalize_station_name)

        stations = stations.merge(
            demand[
                [
                    "station_code",
                    "outbound_trips",
                    "inbound_trips",
                    "total_station_activity",
                ]
            ],
            on="station_code",
            how="left",
        )

        name_lookup = (
            demand.sort_values("total_station_activity", ascending=False)
            .drop_duplicates("station_name_key")
            .set_index("station_name_key")
        )
        for col in ["outbound_trips", "inbound_trips", "total_station_activity"]:
            fallback = stations["station_name_key"].map(name_lookup[col])
            stations[col] = stations[col].fillna(fallback)
    else:
        for col in ["outbound_trips", "inbound_trips", "total_station_activity"]:
            stations[col] = 0

    for col in ["outbound_trips", "inbound_trips", "total_station_activity"]:
        stations[col] = pd.to_numeric(stations[col], errors="coerce").fillna(0)

    positive = stations["total_station_activity"] > 0
    stations["demand_score"] = 0.0
    if positive.any():
        stations.loc[positive, "demand_score"] = percentile_score(
            stations.loc[positive, "total_station_activity"]
        )

    stations["gap_score"] = np.maximum(
        0, stations["demand_score"] - stations["access_percentile"]
    ).round(1)

    stations["quadrant"] = np.select(
        [
            (stations["demand_score"] >= 50) & (stations["access_percentile"] < 50),
            (stations["demand_score"] >= 50) & (stations["access_percentile"] >= 50),
            (stations["demand_score"] < 50) & (stations["access_percentile"] >= 50),
        ],
        [
            "High demand / lower access",
            "High demand / strong access",
            "Lower demand / strong access",
        ],
        default="Lower demand / lower access",
    )
    stations["station_label"] = (
        stations["station_code"].astype(str) + ": " + stations["station_name"].astype(str)
    )

    return stations.sort_values("demand_score", ascending=False).reset_index(drop=True)


def score_location(lat: float, lon: float, stations: pd.DataFrame) -> dict[str, object]:
    """Calculate a commuter-facing accessibility score for an arbitrary map point."""
    ranked = stations.copy()
    ranked["distance_km"] = haversine_distances_km(
        lat, lon, ranked["stop_lat"], ranked["stop_lon"]
    )
    ranked = ranked.sort_values("distance_km").reset_index(drop=True)
    nearest = ranked.iloc[0]

    within_800 = ranked[ranked["distance_km"] <= 0.8].copy()
    within_1500 = ranked[ranked["distance_km"] <= 1.5].copy()
    access_set = within_800 if not within_800.empty else ranked.head(1)

    route_ids: set[str] = set()
    route_labels: set[str] = set()
    for values in access_set["route_ids"]:
        route_ids.update(values if isinstance(values, list) else [])
    for values in access_set["route_labels"]:
        route_labels.update(values if isinstance(values, list) else [])

    max_reach = max(float(stations["direct_reach"].max()), 1.0)
    best_reach = float(access_set["direct_reach"].max()) if not access_set.empty else 0.0

    proximity_score = float(
        np.clip(100 * (1 - float(nearest["distance_km"]) / 2.0), 0, 100)
    )
    line_score = float(np.clip(len(route_ids) / 3.0 * 100, 0, 100))
    reach_score = float(np.clip(best_reach / max_reach * 100, 0, 100))
    density_score = float(np.clip(len(within_800) / 5.0 * 100, 0, 100))

    access_score = round(
        0.45 * proximity_score
        + 0.20 * line_score
        + 0.25 * reach_score
        + 0.10 * density_score,
        1,
    )

    return {
        "accessibility_score": access_score,
        "nearest": nearest,
        "nearest_distance_km": float(nearest["distance_km"]),
        "within_800": within_800,
        "within_1500": within_1500,
        "line_count": len(route_ids),
        "route_labels": sorted(route_labels),
        "direct_reach": int(best_reach),
        "ranked": ranked,
    }


def route_shape_data(
    routes: pd.DataFrame,
    trips: pd.DataFrame,
    shapes: pd.DataFrame,
) -> list[tuple[str, str, list[tuple[float, float]]]]:
    """Return route label, colour and shape coordinates for Folium."""
    route_meta = routes.copy()
    route_meta["route_id"] = route_meta["route_id"].astype(str)
    route_meta["route_color_clean"] = route_meta["route_color"].apply(clean_hex)
    route_meta["route_label"] = route_meta["route_short_name"].fillna(
        route_meta["route_long_name"]
    )
    route_meta["route_label"] = route_meta["route_label"].fillna(route_meta["route_id"])

    shape_routes = (
        trips[["shape_id", "route_id"]].dropna().astype(str).drop_duplicates()
    ).merge(
        route_meta[["route_id", "route_color_clean", "route_label"]],
        on="route_id",
        how="left",
    )

    shape_lookup = (
        shapes.sort_values(["shape_id", "shape_pt_sequence"])
        .groupby("shape_id", sort=False)
    )

    output: list[tuple[str, str, list[tuple[float, float]]]] = []
    for _, row in shape_routes.iterrows():
        shape_id = str(row["shape_id"])
        if shape_id not in shape_lookup.groups:
            continue
        group = shape_lookup.get_group(shape_id)
        coords = list(
            zip(
                group["shape_pt_lat"].astype(float),
                group["shape_pt_lon"].astype(float),
            )
        )
        if len(coords) >= 2:
            output.append(
                (
                    str(row.get("route_label", row["route_id"])),
                    f"#{clean_hex(row.get('route_color_clean', '2563EB'))}",
                    coords,
                )
            )
    return output
