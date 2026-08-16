"""TransitPulse Klang Valley — commuter and network accessibility explorer.

Reliability rule: the app boots from small committed CSV files only. Heavy parquet
files, mapping libraries and the external GTFS feed are loaded only after the user
opens the page that needs them. This keeps Streamlit's health check independent
from the live transport feed.
"""

from __future__ import annotations

from html import escape
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
sys.path.insert(0, str(PROJECT_ROOT / "src"))

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
.block-container{max-width:1420px;padding-top:1.25rem;padding-bottom:4rem}
header[data-testid="stHeader"]{background:rgba(246,248,252,.84);backdrop-filter:blur(12px)}
.tp-hero{padding:2.4rem 2.5rem;border-radius:26px;background:radial-gradient(circle at 88% 20%,rgba(34,211,238,.26),transparent 20rem),linear-gradient(135deg,#081426,#102A56 55%,#164E63);box-shadow:0 24px 70px rgba(15,23,42,.14);color:#fff;margin-bottom:1rem}
.tp-hero .eyebrow{display:inline-block;padding:.34rem .68rem;border:1px solid rgba(255,255,255,.22);border-radius:999px;background:rgba(255,255,255,.08);color:#BAE6FD;font-size:.76rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin-bottom:.9rem}
.tp-hero h1{max-width:950px;font-size:clamp(2.25rem,5vw,4.5rem);line-height:1;letter-spacing:-.055em;margin:0 0 1rem;color:#fff}
.tp-hero p{max-width:850px;font-size:1.06rem;line-height:1.65;color:#CBD5E1;margin:0}
.tp-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;margin:.9rem 0 1.4rem}
.tp-purpose,.tp-metric{background:#fff;border:1px solid var(--border);border-radius:19px;box-shadow:0 8px 26px rgba(15,23,42,.04)}
.tp-purpose{padding:1.2rem 1.3rem}.tp-purpose .k{color:#2563EB;font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em}.tp-purpose .t{font-size:1.15rem;font-weight:850;color:var(--ink);margin:.3rem 0}.tp-purpose .c{font-size:.92rem;color:var(--muted);line-height:1.55}
.tp-kicker{color:#2563EB;font-weight:800;text-transform:uppercase;font-size:.73rem;letter-spacing:.08em;margin-top:.7rem}.tp-title{font-size:1.75rem;font-weight:850;letter-spacing:-.025em;color:var(--ink);margin:.18rem 0}.tp-copy{color:var(--muted);line-height:1.55;margin-bottom:.9rem}
.tp-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.8rem;margin:.8rem 0 1.15rem}.tp-metric{padding:1rem 1.05rem;min-height:108px}.tp-metric .l{color:var(--muted);font-size:.73rem;font-weight:750;text-transform:uppercase;letter-spacing:.055em}.tp-metric .v{color:var(--ink);font-size:1.55rem;font-weight:850;line-height:1.08;margin-top:.42rem}.tp-metric .n{color:var(--muted);font-size:.75rem;line-height:1.35;margin-top:.4rem}
.tp-insight{border:1px solid #BFDBFE;background:linear-gradient(135deg,#EFF6FF,#ECFEFF);border-radius:16px;padding:.92rem 1rem;color:#1E3A5F;line-height:1.55;margin:.55rem 0 .9rem}
.tp-note{border:1px solid var(--border);background:rgba(255,255,255,.82);border-radius:15px;padding:.82rem .95rem;color:var(--muted);line-height:1.5;font-size:.88rem}
.pill{display:inline-block;padding:.2rem .5rem;margin:.12rem .18rem .12rem 0;border-radius:999px;background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;font-size:.75rem;font-weight:760}
div[data-testid="stDataFrame"]{border:1px solid var(--border);border-radius:14px;overflow:hidden}
@media(max-width:850px){.tp-hero{padding:1.55rem 1.2rem}.tp-grid,.tp-metrics{grid-template-columns:1fr}.block-container{padding-left:1rem;padding-right:1rem}}
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


def style_chart(fig, height: int = 430) -> None:
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=52, b=28),
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


@st.cache_data(show_spinner=False)
def load_csv(name: str) -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


@st.cache_data(ttl=86_400, show_spinner=False)
def load_station_metrics() -> tuple[pd.DataFrame, pd.DataFrame]:
    from analysis.accessibility import build_station_metrics
    from data_ingestion.gtfs_static import fetch_rapid_rail_core

    stops, routes = fetch_rapid_rail_core(timeout=20)
    station_summary = load_parquet("station_summary.parquet")
    return build_station_metrics(stops, routes, station_summary), routes


def network_or_error() -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        with st.spinner("Loading the Rapid Rail network…"):
            return load_station_metrics()
    except Exception as exc:
        st.error(
            "The live rail-network feed is temporarily unavailable. "
            "TransitPulse itself is still online; the demand pages continue to work."
        )
        with st.expander("Technical detail"):
            st.code(str(exc))
        return pd.DataFrame(), pd.DataFrame()


def station_map(
    stations: pd.DataFrame,
    location: tuple[float, float] | None = None,
    selected_code: str | None = None,
    catchments: bool = False,
):
    import folium
    from analysis.accessibility import haversine_distances_km

    center = list(location) if location else [3.13, 101.69]
    fmap = folium.Map(
        location=center,
        zoom_start=13 if location else 10,
        tiles="CartoDB positron",
        control_scale=True,
        prefer_canvas=True,
    )

    visible = stations
    if location:
        distances = haversine_distances_km(
            location[0], location[1], stations["stop_lat"], stations["stop_lon"]
        )
        visible = stations[distances <= 4].copy()

    if catchments:
        for _, row in visible.iterrows():
            folium.Circle(
                [float(row["stop_lat"]), float(row["stop_lon"])],
                radius=800,
                color="#93C5FD",
                weight=.7,
                fill=True,
                fill_color="#BFDBFE",
                fill_opacity=.035,
            ).add_to(fmap)

    for _, row in visible.iterrows():
        color = QUADRANT_COLORS.get(str(row["quadrant"]), "#64748B")
        lines = ", ".join(row["route_labels"]) if isinstance(row["route_labels"], list) else ""
        popup = (
            f"<b>{escape(str(row['station_label']))}</b><br>"
            f"Lines: {escape(lines or '—')}<br>"
            f"Accessibility: <b>{float(row['accessibility_score']):.0f}/100</b><br>"
            f"Demand percentile: <b>{float(row['demand_score']):.0f}</b>"
        )
        folium.CircleMarker(
            [float(row["stop_lat"]), float(row["stop_lon"])],
            radius=5,
            color="white",
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=.9,
            tooltip=str(row["station_label"]),
            popup=folium.Popup(popup, max_width=280),
        ).add_to(fmap)

    if location:
        folium.Marker(
            list(location),
            tooltip="Selected location",
            icon=folium.Icon(color="red"),
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
            tooltip="800 m access proxy",
        ).add_to(fmap)

    if selected_code:
        hit = stations[stations["station_code"] == selected_code]
        if not hit.empty:
            row = hit.iloc[0]
            folium.Circle(
                [float(row["stop_lat"]), float(row["stop_lon"])],
                radius=120,
                color="#0F172A",
                weight=3,
                fill=False,
            ).add_to(fmap)
    return fmap


def render_home() -> None:
    service_summary = load_csv("service_summary.csv")
    top_pairs = load_csv("top_station_pairs.csv")
    monthly = load_csv("monthly_ridership_summary.csv")

    service_count = len(service_summary) if not service_summary.empty else 0
    top_pair = "—"
    if not top_pairs.empty:
        row = top_pairs.iloc[0]
        top_pair = f"{row.get('origin_name', '—')} → {row.get('destination_name', '—')}"
    data_through = "—"
    if not monthly.empty and "month" in monthly.columns:
        data_through = str(monthly["month"].max())

    st.markdown(
        """
<section class="tp-hero">
<div class="eyebrow">Klang Valley transit accessibility + demand</div>
<h1>How well does public transport serve you — and the city?</h1>
<p>TransitPulse combines rail access and observed travel demand into two useful views: check whether a location is practical without a car, or explore where demand appears stronger than network access.</p>
</section>
<div class="tp-grid">
<div class="tp-purpose"><div class="k">For commuters</div><div class="t">Would this area work for me without a car?</div><div class="c">Explore nearby stations, access distance, rail-line choice, direct network reach and common travel destinations.</div></div>
<div class="tp-purpose"><div class="k">For planners & analysts</div><div class="t">Where is demand stronger than network access?</div><div class="c">Compare station demand with relative accessibility and surface places that merit closer investigation.</div></div>
</div>
""",
        unsafe_allow_html=True,
    )
    metrics(
        [
            ("Services tracked", f"{service_count:,}", "Historical transport services."),
            ("Demand evidence", "Rapid Rail OD", "Observed station-to-station trips."),
            ("Ridership data through", data_through, "Latest committed monthly record."),
            ("Strongest OD pair", top_pair, "Highest observed station-to-station flow."),
        ]
    )
    st.markdown(
        '<div class="tp-insight"><strong>Start with a question.</strong> '
        'Use <strong>Explore My Area</strong> if you care about a particular place. '
        'Use <strong>Network Explorer</strong> if you want to investigate system-level gaps.</div>',
        unsafe_allow_html=True,
    )


def render_commuter() -> None:
    section(
        "Commuter explorer",
        "Would this place work without a car?",
        "Choose a station or click a map location. TransitPulse estimates rail access using distance, nearby line choice, direct reach and nearby-station density.",
    )
    stations, _ = network_or_error()
    if stations.empty:
        return

    from analysis.accessibility import normalize_station_name, score_location
    from streamlit_folium import st_folium
    import plotly.express as px

    mode = st.radio(
        "Explore by",
        ["Choose a station", "Click a location"],
        horizontal=True,
        label_visibility="collapsed",
    )

    location = None
    selected_code = None

    if mode == "Choose a station":
        label = st.selectbox(
            "Station",
            stations.sort_values("station_label")["station_label"].tolist(),
            index=None,
            placeholder="Search for a Rapid Rail station…",
        )
        if not label:
            st.info("Choose a station to see its accessibility profile.")
            return
        row = stations[stations["station_label"] == label].iloc[0]
        location = (float(row["stop_lat"]), float(row["stop_lon"]))
        selected_code = str(row["station_code"])
        st_folium(
            station_map(stations, location, selected_code),
            use_container_width=True,
            height=480,
            key=f"station_{selected_code}",
        )
    else:
        st.session_state.setdefault("tp_click", None)
        location = st.session_state["tp_click"]
        state = st_folium(
            station_map(stations, location),
            use_container_width=True,
            height=500,
            key="click_location_map",
        )
        clicked = state.get("last_clicked") if state else None
        if clicked:
            candidate = (float(clicked["lat"]), float(clicked["lng"]))
            old = st.session_state.get("tp_click")
            if old is None or abs(old[0] - candidate[0]) > 1e-6 or abs(old[1] - candidate[1]) > 1e-6:
                st.session_state["tp_click"] = candidate
                st.rerun()
        if location is None:
            st.info("Click anywhere on the map to assess rail access around that point.")
            return

    result = score_location(location[0], location[1], stations)
    nearest = result["nearest"]
    metrics(
        [
            ("Accessibility score", f"{result['accessibility_score']:.0f}/100", "Composite access indicator."),
            ("Nearest station", str(nearest["station_name"]), f"{result['nearest_distance_km']*1000:,.0f} m straight-line."),
            ("Rail lines nearby", str(result["line_count"]), "Inside 800 m, or nearest station."),
            ("Direct rail reach", f"{result['direct_reach']} stops", "Before considering transfers."),
        ]
    )

    score = float(result["accessibility_score"])
    verdict = (
        "Strong rail access in the current model."
        if score >= 75
        else "Moderate rail access; one or more access factors are weaker than the best-connected locations."
        if score >= 50
        else "Relatively weak rail access in the current model."
    )
    st.markdown(
        f'<div class="tp-insight"><strong>What this means:</strong> {escape(verdict)}</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Nearby rail options")
        nearby = result["within_1500"].copy()
        if nearby.empty:
            st.write("No Rapid Rail station is within 1.5 km.")
        else:
            nearby["Distance (m)"] = (nearby["distance_km"] * 1000).round().astype(int)
            st.dataframe(
                nearby[["station_label", "Distance (m)", "accessibility_score", "demand_score"]]
                .rename(columns={
                    "station_label": "Station",
                    "accessibility_score": "Station access",
                    "demand_score": "Demand percentile",
                })
                .head(12),
                hide_index=True,
                use_container_width=True,
            )
        if result["route_labels"]:
            pills = "".join(f'<span class="pill">{escape(x)}</span>' for x in result["route_labels"])
            st.markdown(f"<strong>Nearby lines</strong><br>{pills}", unsafe_allow_html=True)

    with right:
        st.subheader(f"Where people travel from {nearest['station_name']}")
        od = load_parquet("rapidrail_od_clean.parquet")
        if od.empty:
            st.write("OD demand data is unavailable.")
        else:
            code = str(nearest["station_code"]).upper()
            outgoing = (
                od[od["origin_code"].astype(str).str.upper() == code]
                .groupby("destination_name", as_index=False)["ridership"]
                .sum()
                .sort_values("ridership", ascending=False)
                .head(8)
            )
            if outgoing.empty:
                outgoing = (
                    od[od["origin_name"].map(normalize_station_name) == normalize_station_name(nearest["station_name"])]
                    .groupby("destination_name", as_index=False)["ridership"]
                    .sum()
                    .sort_values("ridership", ascending=False)
                    .head(8)
                )
            if outgoing.empty:
                st.write("No matching OD demand was found for this station.")
            else:
                fig = px.bar(
                    outgoing.sort_values("ridership"),
                    x="ridership",
                    y="destination_name",
                    orientation="h",
                    color_discrete_sequence=[ACCENT],
                    labels={"ridership": "Trips", "destination_name": ""},
                    title="Top observed destinations",
                )
                style_chart(fig, 390)
                st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div class="tp-note"><strong>Distance note.</strong> The 800 m catchment is a straight-line proxy, '
        'not a routed walking path. Roads, crossings, entrances, elevation and barriers are not yet modelled.</div>',
        unsafe_allow_html=True,
    )


def render_network() -> None:
    section(
        "Network & planning explorer",
        "Where does observed demand outpace relative access?",
        "Compare station demand with line choice, direct rail reach and nearby-station density. This is a screening tool, not a definitive transit-desert classification.",
    )
    stations, routes = network_or_error()
    if stations.empty:
        return

    import plotly.express as px

    review_count = int((stations["quadrant"] == "High demand / lower access").sum())
    metrics(
        [
            ("Rapid Rail stops", f"{len(stations):,}", "Usable GTFS station records."),
            ("Rail routes", f"{routes['route_id'].nunique():,}", "Routes in the official feed."),
            ("Priority-review stations", f"{review_count:,}", "High demand / lower relative access."),
            ("Demand-matched stops", f"{int((stations['total_station_activity'] > 0).sum()):,}", "Stops matched to OD demand."),
        ]
    )

    left, right = st.columns([1.08, 1])
    with left:
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
                "accessibility_score": True,
                "line_count": True,
                "direct_reach": True,
                "gap_score": True,
                "total_station_activity": ":,.0f",
                "quadrant": False,
            },
            labels={
                "access_percentile": "Accessibility percentile",
                "demand_score": "Demand percentile",
                "total_station_activity": "Station activity",
            },
            title="Demand vs relative accessibility",
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
            .head(15)
        )
        st.dataframe(
            priority[
                ["station_label", "demand_score", "access_percentile", "accessibility_score", "gap_score", "line_count", "direct_reach"]
            ].rename(columns={
                "station_label": "Station",
                "demand_score": "Demand",
                "access_percentile": "Access rank",
                "accessibility_score": "Access score",
                "gap_score": "Gap",
                "line_count": "Lines",
                "direct_reach": "Direct reach",
            }),
            hide_index=True,
            use_container_width=True,
            height=440,
        )
        st.markdown(
            '<div class="tp-note">A larger gap means observed demand ranks higher than relative station access. '
            'It identifies places to investigate, not proof that an area is underserved.</div>',
            unsafe_allow_html=True,
        )

    st.subheader("Explore the network geographically")
    if st.toggle("Load interactive station map", value=False):
        from streamlit_folium import st_folium
        catchments = st.toggle("Show 800 m catchment proxies", value=False)
        st_folium(
            station_map(stations, catchments=catchments),
            use_container_width=True,
            height=570,
            key=f"network_map_{catchments}",
        )


def render_evidence() -> None:
    section(
        "Demand evidence",
        "The charts support the product — they are not the product.",
        "Inspect the historical ridership and station-to-station flows behind the commuter and network views.",
    )
    import plotly.express as px

    ridership = load_parquet("daily_ridership_long.parquet")
    pair_summary = load_parquet("station_pair_summary.parquet")
    if ridership.empty:
        st.info("Ridership data is unavailable.")
        return

    ridership = ridership.copy()
    ridership["date"] = pd.to_datetime(ridership["date"])
    min_date, max_date = ridership["date"].min().date(), ridership["date"].max().date()
    a, b = st.columns([1, 1.5])
    with a:
        date_range = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
    with b:
        options = sorted(ridership["service"].dropna().unique())
        selected = st.multiselect("Services", options, default=options)

    start, end = date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (min_date, max_date)
    filtered = ridership[
        (ridership["date"].dt.date >= start) & (ridership["date"].dt.date <= end)
    ]
    if selected:
        filtered = filtered[filtered["service"].isin(selected)]

    if not filtered.empty:
        totals = (
            filtered.groupby("service", as_index=False)["ridership"]
            .sum()
            .sort_values("ridership", ascending=False)
        )
        monthly = (
            filtered.groupby(["month", "service"], as_index=False)["ridership"]
            .sum()
            .sort_values("month")
        )
        monthly = monthly[monthly["service"].isin(totals.head(7)["service"])]
        left, right = st.columns([1.25, 1])
        with left:
            fig = px.line(
                monthly,
                x="month",
                y="ridership",
                color="service",
                color_discrete_sequence=PALETTE,
                labels={"month": "", "ridership": "Trips", "service": ""},
                title="Monthly ridership — leading selected services",
            )
            style_chart(fig, 450)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.bar(
                totals.head(10).sort_values("ridership"),
                x="ridership",
                y="service",
                orientation="h",
                color_discrete_sequence=[ACCENT],
                labels={"ridership": "Trips", "service": ""},
                title="Total trips by service",
            )
            style_chart(fig, 450)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("High-volume station-to-station movements")
    if pair_summary.empty:
        st.info("Station-pair summary is unavailable.")
    else:
        pairs = pair_summary.head(12).copy()
        pairs["pair"] = pairs["origin_name"] + " → " + pairs["destination_name"]
        fig = px.bar(
            pairs.sort_values("ridership"),
            x="ridership",
            y="pair",
            orientation="h",
            color_discrete_sequence=[CYAN],
            labels={"ridership": "Trips", "pair": ""},
        )
        style_chart(fig, 500)
        st.plotly_chart(fig, use_container_width=True)


def render_methodology() -> None:
    section(
        "Methodology",
        "What TransitPulse measures — and what it does not.",
        "The scoring system is visible so the assumptions can be challenged and improved.",
    )
    st.markdown(
        """
### Location Accessibility Score
- **45% proximity** — straight-line distance to the nearest Rapid Rail stop, tapering to zero at 2 km.
- **20% line choice** — lines available within the 800 m proxy, or at the nearest station.
- **25% direct rail reach** — stops reachable on nearby lines before transfers.
- **10% station density** — stops inside the 800 m proxy.

### Station Accessibility
Station accessibility excludes ridership. It uses line choice, direct reach and nearby-station density so access remains independent from observed use.

### Demand Score
Demand is the percentile rank of observed Rapid Rail station activity (inbound + outbound OD trips).

### Demand–Access Gap
`max(0, Demand percentile - Accessibility percentile)`

The gap is a **screening indicator**, not a definitive transit-desert measure.

### What a stronger underserved-area model still needs
Population and employment density, routed pedestrian distance, feeder-bus access, service frequency, operating hours, and socioeconomic or mobility-need indicators.

### Data interpretation
Ridership values represent **trips, not unique passengers**. A passenger can contribute multiple trips, and OD journeys can involve transfers.
"""
    )


def main() -> None:
    st.markdown("### 🚆 TransitPulse Klang Valley")
    page = st.radio(
        "Navigate",
        ["Home", "📍 Explore My Area", "🗺️ Network Explorer", "📊 Demand Evidence", "🧭 Methodology"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.divider()

    if page == "Home":
        render_home()
    elif page == "📍 Explore My Area":
        render_commuter()
    elif page == "🗺️ Network Explorer":
        render_network()
    elif page == "📊 Demand Evidence":
        render_evidence()
    else:
        render_methodology()


if __name__ == "__main__":
    main()
