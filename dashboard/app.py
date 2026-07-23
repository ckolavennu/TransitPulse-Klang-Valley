"""Improved Streamlit dashboard for TransitPulse Klang Valley.

Replace: dashboard/app.py
Run:     streamlit run dashboard/app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

st.set_page_config(
    page_title="TransitPulse Klang Valley",
    page_icon="🚆",
    layout="wide",
)


# -----------------------------------------------------------------------------
# Styling and helpers
# -----------------------------------------------------------------------------

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.4rem;
            font-weight: 800;
            margin-bottom: 0.15rem;
        }
        .subtitle {
            color: #6b7280;
            font-size: 0.95rem;
            margin-bottom: 1.3rem;
        }
        .section-note {
            color: #6b7280;
            font-size: 0.9rem;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.7rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_compact(value: float | int | None) -> str:
    """Format large numbers in a dashboard-friendly way."""
    if value is None or pd.isna(value):
        return "0"

    value = float(value)
    abs_value = abs(value)

    if abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs_value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def add_chart_layout(fig, height: int = 430):
    """Apply consistent chart layout."""
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=55, b=25),
        legend_title_text="",
        hovermode="x unified",
    )
    fig.update_yaxes(tickformat="~s")
    return fig


@st.cache_data(show_spinner=False)
def load_parquet(filename: str) -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


@st.cache_data(show_spinner=False)
def load_csv(filename: str) -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def show_missing_data_message() -> None:
    st.warning(
        "Processed data files were not found. Run the pipeline first: "
        "`python src/run_pipeline.py`"
    )


def filter_by_date(df: pd.DataFrame, date_col: str, start_date, end_date) -> pd.DataFrame:
    if df.empty or date_col not in df.columns:
        return df

    work = df.copy()
    work[date_col] = pd.to_datetime(work[date_col])
    return work[
        (work[date_col].dt.date >= start_date)
        & (work[date_col].dt.date <= end_date)
    ]


def make_download_button(df: pd.DataFrame, label: str, file_name: str) -> None:
    if df.empty:
        return
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv,
        file_name=file_name,
        mime="text/csv",
        use_container_width=True,
    )


# -----------------------------------------------------------------------------
# Main app
# -----------------------------------------------------------------------------


def main() -> None:
    st.markdown('<div class="main-title">TransitPulse Klang Valley</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Public transport ridership and origin-destination demand analytics for Klang Valley.</div>',
        unsafe_allow_html=True,
    )

    ridership = load_parquet("daily_ridership_long.parquet")
    od = load_parquet("rapidrail_od_clean.parquet")
    station_summary = load_parquet("station_summary.parquet")
    pair_summary = load_parquet("station_pair_summary.parquet")

    if ridership.empty and od.empty:
        show_missing_data_message()
        st.stop()

    if not ridership.empty:
        ridership = ridership.copy()
        ridership["date"] = pd.to_datetime(ridership["date"])

    if not od.empty:
        od = od.copy()
        od["date"] = pd.to_datetime(od["date"])

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")

        if not ridership.empty:
            min_date = ridership["date"].min().date()
            max_date = ridership["date"].max().date()
            selected_dates = st.date_input(
                "Ridership date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )
            if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                start_date, end_date = selected_dates
            else:
                start_date, end_date = min_date, max_date

            services = sorted(ridership["service"].dropna().unique())
            selected_services = st.multiselect(
                "Services",
                options=services,
                default=services,
            )

            top_n_services = st.slider("Services to show in overview trend", 3, 14, 8)
        else:
            start_date = end_date = None
            selected_services = []
            top_n_services = 8

        st.divider()
        st.caption("Ridership values represent trips, not unique passengers.")

    if not ridership.empty:
        ridership_filtered = filter_by_date(ridership, "date", start_date, end_date)
        if selected_services:
            ridership_filtered = ridership_filtered[
                ridership_filtered["service"].isin(selected_services)
            ]
    else:
        ridership_filtered = pd.DataFrame()

    tab_overview, tab_services, tab_od, tab_station, tab_notes = st.tabs(
        [
            "Overview",
            "Service Comparison",
            "OD Explorer",
            "Station Insights",
            "Data Notes",
        ]
    )

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------
    with tab_overview:
        st.header("Ridership Overview")

        if ridership_filtered.empty:
            st.info("Daily ridership data is not available for the selected filters.")
        else:
            daily_total = (
                ridership_filtered.groupby("date", as_index=False)["ridership"].sum()
                .sort_values("date")
            )
            service_total = (
                ridership_filtered.groupby("service", as_index=False)["ridership"]
                .sum()
                .sort_values("ridership", ascending=False)
            )

            total_trips = ridership_filtered["ridership"].sum()
            average_daily = daily_total["ridership"].mean()
            active_services = ridership_filtered["service"].nunique()
            peak_service = service_total.iloc[0]["service"] if not service_total.empty else "-"

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Trips", format_compact(total_trips))
            col2.metric("Average Daily Trips", format_compact(average_daily))
            col3.metric("Services Selected", f"{active_services}")
            col4.metric("Top Service", str(peak_service))

            st.markdown(
                '<div class="section-note">The full history is useful, but the long time range can hide recent patterns. Use the sidebar date filter to zoom into recent years.</div>',
                unsafe_allow_html=True,
            )

            monthly = (
                ridership_filtered.groupby(["month", "service"], as_index=False)["ridership"]
                .sum()
                .sort_values("month")
            )

            top_services = service_total.head(top_n_services)["service"].tolist()
            monthly_top = monthly[monthly["service"].isin(top_services)]

            fig_monthly = px.line(
                monthly_top,
                x="month",
                y="ridership",
                color="service",
                markers=True,
                title=f"Monthly Ridership Trend — Top {len(top_services)} Selected Services",
            )
            fig_monthly = add_chart_layout(fig_monthly, height=480)
            st.plotly_chart(fig_monthly, use_container_width=True)

            col_left, col_right = st.columns([1.25, 1])
            with col_left:
                fig_service = px.bar(
                    service_total.head(12).sort_values("ridership"),
                    x="ridership",
                    y="service",
                    orientation="h",
                    text="ridership",
                    title="Top Services by Total Ridership",
                )
                fig_service.update_traces(texttemplate="%{text:.2s}", textposition="outside")
                fig_service = add_chart_layout(fig_service, height=450)
                st.plotly_chart(fig_service, use_container_width=True)

            with col_right:
                fig_share = px.pie(
                    service_total.head(8),
                    names="service",
                    values="ridership",
                    hole=0.45,
                    title="Ridership Share — Top Services",
                )
                fig_share.update_layout(height=450, margin=dict(l=20, r=20, t=55, b=25))
                st.plotly_chart(fig_share, use_container_width=True)

    # ------------------------------------------------------------------
    # Service comparison
    # ------------------------------------------------------------------
    with tab_services:
        st.header("Service Comparison")

        if ridership_filtered.empty:
            st.info("Service data is not available for the selected filters.")
        else:
            st.subheader("Daily Trend")
            smoothing = st.checkbox("Show 7-day rolling average", value=True)

            daily_service = (
                ridership_filtered.groupby(["date", "service"], as_index=False)["ridership"]
                .sum()
                .sort_values(["service", "date"])
            )

            if smoothing:
                daily_service["ridership_display"] = daily_service.groupby("service")[
                    "ridership"
                ].transform(lambda s: s.rolling(7, min_periods=1).mean())
                y_col = "ridership_display"
                title = "Daily Ridership Trend — 7-Day Rolling Average"
            else:
                y_col = "ridership"
                title = "Daily Ridership Trend"

            fig_daily = px.line(
                daily_service,
                x="date",
                y=y_col,
                color="service",
                title=title,
            )
            fig_daily = add_chart_layout(fig_daily, height=460)
            st.plotly_chart(fig_daily, use_container_width=True)

            col_left, col_right = st.columns(2)

            with col_left:
                weekday_summary = (
                    ridership_filtered.groupby(["service", "is_weekend"], as_index=False)[
                        "ridership"
                    ]
                    .mean()
                    .sort_values("ridership", ascending=False)
                )
                weekday_summary["day_type"] = weekday_summary["is_weekend"].map(
                    {True: "Weekend", False: "Weekday"}
                )
                fig_weekday = px.bar(
                    weekday_summary,
                    x="service",
                    y="ridership",
                    color="day_type",
                    barmode="group",
                    title="Average Daily Ridership: Weekday vs Weekend",
                )
                fig_weekday = add_chart_layout(fig_weekday, height=430)
                st.plotly_chart(fig_weekday, use_container_width=True)

            with col_right:
                monthly_service = (
                    ridership_filtered.groupby(["month", "service"], as_index=False)[
                        "ridership"
                    ].sum()
                )
                monthly_rank = (
                    monthly_service.groupby("service", as_index=False)["ridership"]
                    .mean()
                    .sort_values("ridership", ascending=False)
                )
                fig_rank = px.bar(
                    monthly_rank.sort_values("ridership"),
                    x="ridership",
                    y="service",
                    orientation="h",
                    text="ridership",
                    title="Average Monthly Ridership by Service",
                )
                fig_rank.update_traces(texttemplate="%{text:.2s}", textposition="outside")
                fig_rank = add_chart_layout(fig_rank, height=430)
                st.plotly_chart(fig_rank, use_container_width=True)

            st.subheader("Service Summary Table")
            summary_table = service_total.copy()
            summary_table["ridership_formatted"] = summary_table["ridership"].apply(format_compact)
            st.dataframe(summary_table, use_container_width=True, hide_index=True)
            make_download_button(summary_table, "Download service summary", "service_summary.csv")

    # ------------------------------------------------------------------
    # OD Explorer
    # ------------------------------------------------------------------
    with tab_od:
        st.header("Origin-Destination Explorer")

        if od.empty:
            st.info("OD data is not available yet.")
        else:
            od_min = od["date"].min().date()
            od_max = od["date"].max().date()

            col_filter1, col_filter2, col_filter3 = st.columns([1.2, 1, 1])
            with col_filter1:
                od_dates = st.date_input(
                    "OD date range",
                    value=(od_min, od_max),
                    min_value=od_min,
                    max_value=od_max,
                    key="od_dates",
                )
            with col_filter2:
                top_n = st.slider("Station pairs to show", 10, 100, 25)
            with col_filter3:
                min_trips = st.number_input("Minimum trips", min_value=0, value=0, step=100)

            if isinstance(od_dates, tuple) and len(od_dates) == 2:
                od_start, od_end = od_dates
            else:
                od_start, od_end = od_min, od_max

            od_filtered = filter_by_date(od, "date", od_start, od_end)
            od_filtered = od_filtered[od_filtered["ridership"] >= min_trips]

            pair_filtered = (
                od_filtered.groupby(
                    ["origin_code", "origin_name", "destination_code", "destination_name"],
                    dropna=False,
                    as_index=False,
                )["ridership"]
                .sum()
                .sort_values("ridership", ascending=False)
            )

            col1, col2, col3 = st.columns(3)
            col1.metric("OD Trips", format_compact(pair_filtered["ridership"].sum()))
            col2.metric("Station Pairs", f"{len(pair_filtered):,}")
            col3.metric("Date Range", f"{od_start} → {od_end}")

            display_pairs = pair_filtered.head(top_n).copy()
            display_pairs["station_pair"] = (
                display_pairs["origin_name"] + " → " + display_pairs["destination_name"]
            )

            fig_pairs = px.bar(
                display_pairs.sort_values("ridership"),
                x="ridership",
                y="station_pair",
                orientation="h",
                text="ridership",
                title="Busiest Rapid Rail Station Pairs",
            )
            fig_pairs.update_traces(texttemplate="%{text:.2s}", textposition="outside")
            fig_pairs = add_chart_layout(fig_pairs, height=max(480, top_n * 20))
            st.plotly_chart(fig_pairs, use_container_width=True)

            st.subheader("Station Pair Data")
            st.dataframe(display_pairs, use_container_width=True, hide_index=True)
            make_download_button(display_pairs, "Download station pairs", "top_station_pairs.csv")

    # ------------------------------------------------------------------
    # Station insights
    # ------------------------------------------------------------------
    with tab_station:
        st.header("Station Insights")

        if station_summary.empty or od.empty:
            st.info("Station data is not available yet.")
        else:
            stations = sorted(station_summary["station_name"].dropna().unique())
            selected_station = st.selectbox("Select station", stations)

            station_row = station_summary[
                station_summary["station_name"] == selected_station
            ].head(1)

            if not station_row.empty:
                row = station_row.iloc[0]
                col1, col2, col3 = st.columns(3)
                col1.metric("Outbound Trips", format_compact(row["outbound_trips"]))
                col2.metric("Inbound Trips", format_compact(row["inbound_trips"]))
                col3.metric("Total Activity", format_compact(row["total_station_activity"]))

            outgoing = (
                od[od["origin_name"] == selected_station]
                .groupby("destination_name", as_index=False)["ridership"]
                .sum()
                .sort_values("ridership", ascending=False)
                .head(15)
            )
            incoming = (
                od[od["destination_name"] == selected_station]
                .groupby("origin_name", as_index=False)["ridership"]
                .sum()
                .sort_values("ridership", ascending=False)
                .head(15)
            )

            col_left, col_right = st.columns(2)
            with col_left:
                fig_out = px.bar(
                    outgoing.sort_values("ridership"),
                    x="ridership",
                    y="destination_name",
                    orientation="h",
                    text="ridership",
                    title=f"Top Destinations From {selected_station}",
                )
                fig_out.update_traces(texttemplate="%{text:.2s}", textposition="outside")
                fig_out = add_chart_layout(fig_out, height=520)
                st.plotly_chart(fig_out, use_container_width=True)

            with col_right:
                fig_in = px.bar(
                    incoming.sort_values("ridership"),
                    x="ridership",
                    y="origin_name",
                    orientation="h",
                    text="ridership",
                    title=f"Top Origins To {selected_station}",
                )
                fig_in.update_traces(texttemplate="%{text:.2s}", textposition="outside")
                fig_in = add_chart_layout(fig_in, height=520)
                st.plotly_chart(fig_in, use_container_width=True)

            st.subheader("Station Tables")
            col_left, col_right = st.columns(2)
            with col_left:
                st.caption("Top destinations")
                st.dataframe(outgoing, use_container_width=True, hide_index=True)
            with col_right:
                st.caption("Top origins")
                st.dataframe(incoming, use_container_width=True, hide_index=True)

    # ------------------------------------------------------------------
    # Data notes
    # ------------------------------------------------------------------
    with tab_notes:
        st.header("Data Notes")
        st.markdown(
            """
            This dashboard currently focuses on the MVP scope:

            - historical public transport ridership trends
            - service-level comparison
            - Rapid Rail origin-destination demand
            - station-level inbound and outbound activity

            Important interpretation note: **ridership means number of trips, not unique passengers**. A passenger who changes lines or makes multiple journeys can contribute more than one trip.
            """
        )

        file_status = pd.DataFrame(
            [
                {
                    "processed_file": "daily_ridership_long.parquet",
                    "available": not ridership.empty,
                    "rows": len(ridership),
                },
                {
                    "processed_file": "rapidrail_od_clean.parquet",
                    "available": not od.empty,
                    "rows": len(od),
                },
                {
                    "processed_file": "station_summary.parquet",
                    "available": not station_summary.empty,
                    "rows": len(station_summary),
                },
                {
                    "processed_file": "station_pair_summary.parquet",
                    "available": not pair_summary.empty,
                    "rows": len(pair_summary),
                },
            ]
        )
        st.dataframe(file_status, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
