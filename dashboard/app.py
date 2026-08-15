"""TransitPulse Klang Valley: commuter and network accessibility explorer."""

from __future__ import annotations

from html import escape
from pathlib import Path
import sys

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from analysis.accessibility import (  # noqa: E402
    build_station_metrics,
    haversine_distances_km,
    normalize_station_name,
    route_shape_data,
    score_location,
)
from data_ingestion.gtfs_static import GTFS_URL, fetch_rapid_rail_gtfs  # noqa: E402

RIDERSHIP_SOURCE = "https://data.gov.my/data-catalogue/ridership_headline"
OD_SOURCE = "https://data.gov.my/data-catalogue/ridership_od_rapidrail_daily"
GTFS_DOCS = "https://developer.data.gov.my/realtime-api/gtfs-static"

ACCENT = "#2563EB"
CYAN = "#06B6D4"
INK = "#0F172A"
PALETTE = ["#2563EB", "#06B6D4", "#8B5CF6", "#F59E0B", "#10B981", "#EF4444"]
QUADRANT_COLORS = {
    "High demand / lower access": "#F97316",
    "High demand / strong access": "#2563EB",
    "Lower demand / strong access": "#10B981",
    "Lower demand / lower access": "#94A3B8",
}

st.set_page_config(
    page_title="TransitPulse Klang Valley",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
:root{--ink:#0F172A;--muted:#64748B;--border:#E2E8F0;--bg:#F6F8FC}
.stApp{background:radial-gradient(circle at 88% 3%,rgba(37,99,235,.08),transparent 28rem),var(--bg)}
.block-container{max-width:1460px;padding-top:1.2rem;padding-bottom:4rem}
header[data-testid="stHeader"]{background:rgba(246,248,252,.8);backdrop-filter:blur(12px)}
.tp-hero{padding:2.4rem 2.5rem;border-radius:26px;background:radial-gradient(circle at 88% 20%,rgba(34,211,238,.26),transparent 20rem),linear-gradient(135deg,#081426,#102A56 55%,#164E63);box-shadow:0 24px 70px rgba(15,23,42,.14);color:#fff;margin-bottom:1.2rem}
.tp-hero .eyebrow{display:inline-block;padding:.34rem .68rem;border:1px solid rgba(255,255,255,.22);border-radius:999px;background:rgba(255,255,255,.08);color:#BAE6FD;font-size:.76rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin-bottom:.9rem}
.tp-hero h1{max-width:930px;font-size:clamp(2.35rem,5vw,4.7rem);line-height:.98;letter-spacing:-.055em;margin:0 0 1rem;color:#fff}
.tp-hero p{max-width:820px;font-size:1.08rem;line-height:1.65;color:#CBD5E1;margin:0}
.tp-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;margin:.2rem 0 1.25rem}
.tp-purpose,.tp-metric{background:rgba(255,255,255,.96);border:1px solid var(--border);border-radius:19px;box-shadow:0 8px 26px rgba(15,23,42,.04)}
.tp-purpose{padding:1.2rem 1.3rem}.tp-purpose .k{color:#2563EB;font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em}.tp-purpose .t{font-size:1.15rem;font-weight:850;color:var(--ink);margin:.3rem 0}.tp-purpose .c{font-size:.92rem;color:var(--muted);line-height:1.55}
.tp-kicker{color:#2563EB;font-weight:800;text-transform:uppercase;font-size:.73rem;letter-spacing:.08em;margin-top:.6rem}.tp-title{font-size:1.72rem;font-weight:850;letter-spacing:-.025em;color:var(--ink);margin:.18rem 0}.tp-copy{color:var(--muted);line-height:1.55;margin-bottom:.9rem}
.tp-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.8rem;margin:.8rem 0 1rem}.tp-metric{padding:1rem 1.05rem;min-height:108px}.tp-metric .l{color:var(--muted);font-size:.75rem;font-weight:750;text-transform:uppercase;letter-spacing:.055em}.tp-metric .v{color:var(--ink);font-size:1.65rem;font-weight:850;line-height:1.08;margin-top:.42rem}.tp-metric .n{color:var(--muted);font-size:.75rem;line-height:1.35;margin-top:.4rem}
.tp-insight{border:1px solid #BFDBFE;background:linear-gradient(135deg,#EFF6FF,#ECFEFF);border-radius:16px;padding:.92rem 1rem;color:#1E3A5F;line-height:1.55;margin:.55rem 0 .9rem}.tp-note{border:1px solid var(--border);background:rgba(255,255,255,.75);border-radius:15px;padding:.82rem .95rem;color:var(--muted);line-height:1.5;font-size:.88rem}.pill{display:inline-block;padding:.2rem .5rem;margin:.12rem .18rem .12rem 0;border-radius:999px;background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;font-size:.75rem;font-weight:760}
div[data-testid="stDataFrame"]{border:1px solid var(--border);border-radius:14px;overflow:hidden}
@media(max-width:850px){.tp-hero{padding:1.6rem 1.25rem}.tp-grid,.tp-metrics{grid-template-columns:1fr}}
</style>
""",
    unsafe_allow_html=True,
)


def section(kicker: str, title: str, copy: str) -> None:
    st.markdown(
        f'<div class="tp-kicker">{escape(kicker)}</div>'
        f'<div class="tp-title">{escape(title)}</div>'
        f'<div class="tp-copy">{escape(copy)}</div>',
        unsafe_allow_html=True,
    )


def metrics(items: list[tuple[str, str, str]]) -> None:
    html = "".join(
        f'<div class="tp-metric"><div class="l">{escape(a)}</div>'
        f'<div class="v">{escape(b)}</div><div class="n">{escape(c)}</div></div>'
        for a, b, c in items
    )
    st.markdown(f'<div class="tp-metrics">{html}</div>', unsafe_allow_html=True)


def compact(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "0"
    value = float(value)
    if abs(value) >= 1e9:
        return f"{value/1e9:.2f}B"
    if abs(value) >= 1e6:
        return f"{value/1e6:.2f}M"
    if abs(value) >= 1e3:
        return f"{value/1e3:.1f}K"
    return f"{value:,.0f}"


def style_chart(fig, height: int = 430) -> None:
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=52, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK),
        legend_title_text="",
        hoverlabel=dict(bgcolor="white"),
    )
    fig.update_xaxes(gridcolor="#EAEFF5", zeroline=False)
    fig.update_yaxes(gridcolor="#EAEFF5", zeroline=False)


@st.cache_data(show_spinner=False)
def load_parquet(name: str) -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / name
    return pd.read_parquet(path) if path.exists() else pd.DataFrame()


@st.cache_data(ttl=86_400, show_spinner=False)
def gtfs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return fetch_rapid_rail_gtfs()


def add_routes(
    fmap: folium.Map,
    routes: pd.DataFrame,
    trips: pd.DataFrame,
    shapes: pd.DataFrame,
    opacity: float = 0.5,
) -> None:
    for label, color, coords in route_shape_data(routes, trips, shapes):
        folium.PolyLine(
            coords, color=color, weight=3, opacity=opacity, tooltip=label
        ).add_to(fmap)


def add_stations(fmap: folium.Map, stations: pd.DataFrame, compact_markers: bool = False) -> None:
    for _, row in stations.iterrows():
        color = QUADRANT_COLORS.get(str(row["quadrant"]), "#64748B")
        radius = 4 if compact_markers else 4 + min(float(row["demand_score"]) / 28, 4)
        lines = ", ".join(row["route_labels"]) if isinstance(row["route_labels"], list) else ""
        popup = (
            f"<b>{escape(str(row['station_label']))}</b><br>"
            f"Lines: {escape(lines or '—')}<br>"
            f"Accessibility: <b>{float(row['accessibility_score']):.0f}/100</b><br>"
            f"Demand percentile: <b>{float(row['demand_score']):.0f}</b><br>"
            f"2026 activity: <b>{compact(row['total_station_activity'])} trips</b>"
        )
        folium.CircleMarker(
            [float(row["stop_lat"]), float(row["stop_lon"])],
            radius=radius,
            color="white",
            weight=1.1,
            fill=True,
            fill_color=color,
            fill_opacity=.88,
            tooltip=str(row["station_label"]),
            popup=folium.Popup(popup, max_width=290),
        ).add_to(fmap)


def commuter_map(
    stations: pd.DataFrame,
    routes: pd.DataFrame,
    trips: pd.DataFrame,
    shapes: pd.DataFrame,
    location: tuple[float, float] | None,
    station_code: str | None = None,
) -> folium.Map:
    center = location or (3.13, 101.69)
    fmap = folium.Map(
        location=list(center),
        zoom_start=13 if location else 10,
        tiles="CartoDB positron",
        control_scale=True,
    )
    add_routes(fmap, routes, trips, shapes, .34)

    visible = stations
    if location:
        d = haversine_distances_km(
            location[0], location[1], stations["stop_lat"], stations["stop_lon"]
        )
        visible = stations[d <= 3].copy()
    add_stations(fmap, visible, True)

    if location:
        folium.Marker(
            list(location), tooltip="Selected location", icon=folium.Icon(color="red")
        ).add_to(fmap)
        folium.Circle(
            list(location),
            radius=800,
            color=ACCENT,
            weight=2,
            dash_array="6 5",
            fill=True,
            fill_color="#60A5FA",
            fill_opacity=.06,
            tooltip="800 m catchment proxy",
        ).add_to(fmap)

    if station_code:
        hit = stations[stations["station_code"] == station_code]
        if not hit.empty:
            row = hit.iloc[0]
            folium.Circle(
                [float(row["stop_lat"]), float(row["stop_lon"])],
                radius=110,
                color="#0F172A",
                weight=3,
                fill=False,
                tooltip="Selected station",
            ).add_to(fmap)
    return fmap


def network_map(
    stations: pd.DataFrame,
    routes: pd.DataFrame,
    trips: pd.DataFrame,
    shapes: pd.DataFrame,
    catchments: bool,
) -> folium.Map:
    fmap = folium.Map(
        location=[3.13, 101.69],
        zoom_start=10,
        tiles="CartoDB positron",
        control_scale=True,
        prefer_canvas=True,
    )
    add_routes(fmap, routes, trips, shapes)
    if catchments:
        for _, row in stations.iterrows():
            folium.Circle(
                [float(row["stop_lat"]), float(row["stop_lon"])],
                radius=800,
                color="#93C5FD",
                weight=.7,
                fill=True,
                fill_color="#BFDBFE",
                fill_opacity=.035,
            ).add_to(fmap)
    add_stations(fmap, stations)
    return fmap


def main() -> None:
    ridership = load_parquet("daily_ridership_long.parquet")
    od = load_parquet("rapidrail_od_clean.parquet")
    station_summary = load_parquet("station_summary.parquet")
    pair_summary = load_parquet("station_pair_summary.parquet")

    if not ridership.empty:
        ridership = ridership.copy()
        ridership["date"] = pd.to_datetime(ridership["date"])
    if not od.empty:
        od = od.copy()
        od["date"] = pd.to_datetime(od["date"])

    error = None
    try:
        with st.spinner("Loading Klang Valley rail network…"):
            stops, routes, trips, shapes = gtfs()
        stations = build_station_metrics(stops, routes, station_summary)
    except Exception as exc:
        stops = routes = trips = shapes = stations = pd.DataFrame()
        error = str(exc)

    st.markdown(
        """
<section class="tp-hero">
<div class="eyebrow">Transit accessibility + demand intelligence</div>
<h1>How well does public transport serve you — and the city?</h1>
<p>TransitPulse turns Klang Valley rail geography and observed travel demand into two practical views: understand the rail access around a place you care about, or step back and see where network demand and accessibility do not align.</p>
</section>
<div class="tp-grid">
<div class="tp-purpose"><div class="k">For commuters</div><div class="t">Would this area work for me without a car?</div><div class="c">Pick a station or click anywhere on the map. See the nearest rail access, walking-distance proxy, nearby lines, direct network reach, station demand and common destinations.</div></div>
<div class="tp-purpose"><div class="k">For planners & analysts</div><div class="t">Where is demand stronger than network access?</div><div class="c">Compare observed demand with connectivity and nearby rail options, explore catchment coverage, and surface high-demand stations that merit closer review.</div></div>
</div>
""",
        unsafe_allow_html=True,
    )

    if error:
        st.error(
            "The official GTFS feed could not be loaded, so accessibility views are "
            f"temporarily unavailable. Demand evidence still works. Detail: {error}"
        )

    commuter, network, evidence, methodology = st.tabs(
        ["📍 Explore My Area", "🗺️ Network Explorer", "📊 Demand Evidence", "🧭 Methodology"]
    )

    with commuter:
        section(
            "Commuter explorer",
            "Start with a place, not a chart.",
            "Choose a station or click a location. TransitPulse estimates how easy it is to reach and use the rail network from there.",
        )
        if stations.empty:
            st.info("Rail network data is unavailable right now.")
        else:
            mode = st.radio(
                "How do you want to explore?",
                ["Choose a station", "Click a location on the map"],
                horizontal=True,
            )
            location = None
            selected_code = None

            if mode == "Choose a station":
                label = st.selectbox(
                    "Search for a Rapid Rail station",
                    stations.sort_values("station_label")["station_label"].tolist(),
                    index=None,
                    placeholder="Example: SP17: Bukit Jalil",
                )
                if label:
                    row = stations[stations["station_label"] == label].iloc[0]
                    location = (float(row["stop_lat"]), float(row["stop_lon"]))
                    selected_code = str(row["station_code"])
                st_folium(
                    commuter_map(stations, routes, trips, shapes, location, selected_code),
                    width=1250,
                    height=510,
                    key="station_map",
                )
            else:
                st.session_state.setdefault("tp_clicked", None)
                location = st.session_state["tp_clicked"]
                state = st_folium(
                    commuter_map(stations, routes, trips, shapes, location),
                    width=1250,
                    height=540,
                    key="click_map",
                )
                clicked = state.get("last_clicked") if state else None
                if clicked:
                    candidate = (float(clicked["lat"]), float(clicked["lng"]))
                    old = st.session_state.get("tp_clicked")
                    if old is None or abs(old[0]-candidate[0]) > 1e-6 or abs(old[1]-candidate[1]) > 1e-6:
                        st.session_state["tp_clicked"] = candidate
                        st.rerun()
                if location is None:
                    st.info("Click anywhere on the map to assess rail access around that location.")

            if location is not None:
                result = score_location(location[0], location[1], stations)
                nearest = result["nearest"]
                metrics(
                    [
                        ("Accessibility score", f"{result['accessibility_score']:.0f}/100", "Transparent composite score; see Methodology."),
                        ("Nearest station", str(nearest["station_name"]), f"{result['nearest_distance_km']*1000:,.0f} m straight-line distance."),
                        ("Rail lines nearby", str(result["line_count"]), "Within the 800 m proxy, or at the nearest station."),
                        ("Direct rail reach", f"{result['direct_reach']} stops", "Reach before considering line transfers."),
                    ]
                )

                score = result["accessibility_score"]
                verdict = (
                    "This location has strong rail access in the current model."
                    if score >= 75
                    else "This location has moderate rail access; proximity or network choice is weaker than the best-connected areas."
                    if score >= 50
                    else "This location has relatively weak rail access in the current model."
                )
                st.markdown(
                    f'<div class="tp-insight"><strong>What this means:</strong> {escape(verdict)}</div>',
                    unsafe_allow_html=True,
                )

                left, right = st.columns([1.05, 1])
                with left:
                    st.subheader("What is within reach?")
                    nearby = result["within_1500"].copy()
                    if nearby.empty:
                        st.write("No Rapid Rail station is within 1.5 km of this point.")
                    else:
                        nearby["Distance (m)"] = (nearby["distance_km"] * 1000).round().astype(int)
                        view = nearby[
                            ["station_label", "Distance (m)", "accessibility_score", "demand_score"]
                        ].rename(
                            columns={
                                "station_label": "Station",
                                "accessibility_score": "Station access",
                                "demand_score": "Demand percentile",
                            }
                        )
                        st.dataframe(view.head(12), hide_index=True, use_container_width=True)

                    if result["route_labels"]:
                        pills = "".join(
                            f'<span class="pill">{escape(x)}</span>'
                            for x in result["route_labels"]
                        )
                        st.markdown(f"<strong>Nearby lines</strong><br>{pills}", unsafe_allow_html=True)

                with right:
                    st.subheader(f"Where people travel from {nearest['station_name']}")
                    if od.empty:
                        st.write("OD demand data is unavailable.")
                    else:
                        code = str(nearest["station_code"]).upper()
                        outgoing = (
                            od[od["origin_code"].astype(str).str.upper() == code]
                            .groupby("destination_name", as_index=False)["ridership"]
                            .sum().sort_values("ridership", ascending=False).head(8)
                        )
                        if outgoing.empty:
                            outgoing = (
                                od[od["origin_name"].map(normalize_station_name) == normalize_station_name(nearest["station_name"])]
                                .groupby("destination_name", as_index=False)["ridership"]
                                .sum().sort_values("ridership", ascending=False).head(8)
                            )
                        if outgoing.empty:
                            st.write("No matching OD demand was found for this station.")
                        else:
                            fig = px.bar(
                                outgoing.sort_values("ridership"),
                                x="ridership",
                                y="destination_name",
                                orientation="h",
                                labels={"ridership": "Trips", "destination_name": ""},
                                color_discrete_sequence=[ACCENT],
                                title="Top observed destinations",
                            )
                            style_chart(fig, 390)
                            st.plotly_chart(fig, use_container_width=True)

                st.markdown(
                    '<div class="tp-note"><strong>Walking-distance note.</strong> '
                    "The 800 m circle is a straight-line catchment proxy, not a routed walking path. "
                    "Roads, crossings, entrances, elevation and barriers are not yet modelled.</div>",
                    unsafe_allow_html=True,
                )

    with network:
        section(
            "Network & planning explorer",
            "Where does observed demand outpace station-level access?",
            "Compare 2026 OD demand with station access based on nearby lines, direct rail reach and surrounding station density. This is a screening tool, not a claim of a transit desert.",
        )
        if stations.empty:
            st.info("Rail network data is unavailable right now.")
        else:
            latest = od["date"].max().date() if not od.empty else None
            review_count = int((stations["quadrant"] == "High demand / lower access").sum())
            metrics(
                [
                    ("Rapid Rail stops", f"{len(stations):,}", "GTFS stop records in the model."),
                    ("Rail routes", f"{routes['route_id'].nunique()}", "Official Rapid Rail KL GTFS feed."),
                    ("Priority-review stations", str(review_count), "High demand in the lower half of the access ranking."),
                    ("Demand data through", str(latest) if latest else "—", "Latest committed Rapid Rail OD date."),
                ]
            )

            left, right = st.columns([1.05, 1])
            with left:
                st.subheader("Demand vs accessibility")
                scatter = stations[stations["total_station_activity"] > 0].copy()
                fig = px.scatter(
                    scatter,
                    x="access_percentile",
                    y="demand_score",
                    size="total_station_activity",
                    size_max=26,
                    color="quadrant",
                    color_discrete_map=QUADRANT_COLORS,
                    hover_name="station_label",
                    hover_data={
                        "total_station_activity": ":,.0f",
                        "accessibility_score": True,
                        "line_count": True,
                        "direct_reach": True,
                        "gap_score": True,
                        "quadrant": False,
                    },
                    labels={
                        "access_percentile": "Accessibility percentile",
                        "demand_score": "Demand percentile",
                        "total_station_activity": "Observed station activity",
                        "accessibility_score": "Accessibility score",
                        "line_count": "Nearby lines",
                        "direct_reach": "Direct rail reach",
                        "gap_score": "Demand-access gap",
                    },
                )
                fig.add_vline(x=50, line_dash="dot", line_color="#94A3B8")
                fig.add_hline(y=50, line_dash="dot", line_color="#94A3B8")
                style_chart(fig, 500)
                fig.update_layout(legend=dict(orientation="h", y=-.18))
                st.plotly_chart(fig, use_container_width=True)

            with right:
                st.subheader("Stations to review first")
                priority = (
                    stations[stations["quadrant"] == "High demand / lower access"]
                    .sort_values(["gap_score", "demand_score"], ascending=False)
                    .head(12)
                )
                view = priority[
                    ["station_label", "demand_score", "access_percentile", "accessibility_score", "gap_score", "line_count", "direct_reach"]
                ].rename(
                    columns={
                        "station_label": "Station",
                        "demand_score": "Demand",
                        "access_percentile": "Access rank",
                        "accessibility_score": "Access score",
                        "gap_score": "Gap",
                        "line_count": "Lines",
                        "direct_reach": "Direct reach",
                    }
                )
                st.dataframe(view, hide_index=True, use_container_width=True, height=420)
                st.markdown(
                    '<div class="tp-note">A larger gap means the station\'s demand percentile '
                    "ranks higher than its accessibility percentile. This is a prompt for investigation, "
                    "not proof that a neighbourhood is underserved.</div>",
                    unsafe_allow_html=True,
                )

            st.subheader("Explore the network geographically")
            catchments = st.toggle("Show 800 m station catchment proxies", value=False)
            st_folium(
                network_map(stations, routes, trips, shapes, catchments),
                width=1250,
                height=610,
                key=f"network_{catchments}",
            )
            cols = st.columns(4)
            for col, (label, color) in zip(cols, QUADRANT_COLORS.items()):
                col.markdown(f"<span style='color:{color};font-size:1.1rem'>●</span> {escape(label)}", unsafe_allow_html=True)

    with evidence:
        section(
            "Demand evidence",
            "The charts are evidence — not the product.",
            "Inspect the historical ridership and origin-destination data that support the commuter and network views.",
        )
        if ridership.empty:
            st.info("Ridership data is unavailable.")
        else:
            min_date, max_date = ridership["date"].min().date(), ridership["date"].max().date()
            a, b = st.columns([1, 1.5])
            with a:
                date_range = st.date_input(
                    "Ridership date range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="evidence_dates",
                )
            with b:
                service_options = sorted(ridership["service"].dropna().unique())
                selected = st.multiselect(
                    "Services", service_options, default=service_options, key="evidence_services"
                )
            start, end = date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (min_date, max_date)
            filtered = ridership[
                (ridership["date"].dt.date >= start) & (ridership["date"].dt.date <= end)
            ]
            if selected:
                filtered = filtered[filtered["service"].isin(selected)]

            if filtered.empty:
                st.info("No ridership records match the filters.")
            else:
                totals = filtered.groupby("service", as_index=False)["ridership"].sum().sort_values("ridership", ascending=False)
                monthly = filtered.groupby(["month", "service"], as_index=False)["ridership"].sum().sort_values("month")
                monthly = monthly[monthly["service"].isin(totals.head(7)["service"])]
                left, right = st.columns([1.25, 1])
                with left:
                    fig = px.line(
                        monthly, x="month", y="ridership", color="service",
                        color_discrete_sequence=PALETTE,
                        labels={"month": "", "ridership": "Trips", "service": ""},
                        title="Monthly ridership — leading selected services",
                    )
                    style_chart(fig, 460)
                    st.plotly_chart(fig, use_container_width=True)
                with right:
                    fig = px.bar(
                        totals.head(10).sort_values("ridership"),
                        x="ridership", y="service", orientation="h",
                        color_discrete_sequence=[ACCENT],
                        labels={"ridership": "Trips", "service": ""},
                        title="Total trips by service",
                    )
                    style_chart(fig, 460)
                    st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("High-volume station-to-station movements")
        if pair_summary.empty:
            st.info("Station-pair summary is unavailable.")
        else:
            pairs = pair_summary.head(12).copy()
            pairs["pair"] = pairs["origin_name"] + " → " + pairs["destination_name"]
            fig = px.bar(
                pairs.sort_values("ridership"), x="ridership", y="pair",
                orientation="h", color_discrete_sequence=[CYAN],
                labels={"ridership": "Trips", "pair": ""},
            )
            style_chart(fig, 500)
            st.plotly_chart(fig, use_container_width=True)

    with methodology:
        section(
            "Methodology",
            "What TransitPulse measures — and what it does not.",
            "The scoring system is intentionally visible so the model can be challenged and improved rather than hidden behind one number.",
        )
        st.markdown(
            """
### Location Accessibility Score
- **45% proximity** — straight-line distance to the nearest Rapid Rail stop, tapering to zero at 2 km.
- **20% line choice** — rail lines available within the 800 m proxy, or at the nearest station if none fall inside it.
- **25% direct rail reach** — stops reachable on nearby lines before transfers.
- **10% station density** — stops inside the 800 m proxy.

### Station Accessibility
Station access is calculated **without ridership** using nearby line choice, direct reach and nearby-station density. This keeps network access independent from observed usage.

### Demand Score
Demand is the percentile rank of observed 2026 Rapid Rail station activity (inbound + outbound OD trips).

### Demand–Access Gap
`max(0, Demand percentile - Accessibility percentile)`

The gap is a **screening indicator**. It highlights stations where observed use ranks higher than relative network access; it is not a definitive transit-desert measure.

### What a stronger underserved-area model still needs
Population and employment density, routed pedestrian distance, feeder-bus access, service frequency, operating hours and socioeconomic/mobility-need indicators.
"""
        )
        st.markdown("### Data sources")
        st.markdown(
            f"- [Daily public transport ridership]({RIDERSHIP_SOURCE}) — data.gov.my\n"
            f"- [Rapid Rail daily OD ridership]({OD_SOURCE}) — data.gov.my\n"
            f"- [GTFS Static documentation]({GTFS_DOCS}) — official Malaysia Open API\n"
            f"- GTFS endpoint used by the app: `{GTFS_URL}`"
        )
        if not stations.empty:
            metrics(
                [
                    ("GTFS stops loaded", str(len(stations)), "Rapid Rail KL network."),
                    ("GTFS routes loaded", str(routes["route_id"].nunique()), "Official static feed."),
                    ("Stops matched to demand", str(int((stations["total_station_activity"] > 0).sum())), "Matched by station code or name."),
                    ("GTFS cache", "24 hours", "Avoids unnecessary repeated API requests."),
                ]
            )
        st.markdown(
            '<div class="tp-note"><strong>Interpretation rule:</strong> Ridership values represent trips, '
            "not unique passengers. OD journeys can span line transfers, so they should not be used to infer "
            "line-specific ridership.</div>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
