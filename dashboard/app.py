"""Portfolio-ready Streamlit dashboard for TransitPulse Klang Valley."""

from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

ACCENT = "#2563EB"
ACCENT_2 = "#06B6D4"
INK = "#111827"
MUTED = "#64748B"
GRID = "#E2E8F0"
PALETTE = [
    "#2563EB",
    "#06B6D4",
    "#8B5CF6",
    "#F59E0B",
    "#10B981",
    "#EF4444",
    "#EC4899",
    "#14B8A6",
]

st.set_page_config(
    page_title="TransitPulse Klang Valley",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --tp-ink: #111827;
        --tp-muted: #64748B;
        --tp-border: #E2E8F0;
        --tp-card: #FFFFFF;
        --tp-bg: #F5F7FB;
    }

    .stApp { background: var(--tp-bg); }
    .block-container {
        max-width: 1440px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    header[data-testid="stHeader"] {
        background: rgba(245, 247, 251, 0.82);
        backdrop-filter: blur(12px);
    }
    section[data-testid="stSidebar"] {
        border-right: 1px solid var(--tp-border);
        background: #FFFFFF;
    }

    .tp-brand {
        display: flex;
        align-items: center;
        gap: .7rem;
        margin-bottom: 1.2rem;
    }
    .tp-logo {
        width: 38px;
        height: 38px;
        border-radius: 12px;
        display: grid;
        place-items: center;
        color: #FFFFFF;
        font-weight: 800;
        background: linear-gradient(135deg, #2563EB 0%, #06B6D4 100%);
        box-shadow: 0 8px 22px rgba(37, 99, 235, .22);
    }
    .tp-brand-name { font-weight: 800; color: var(--tp-ink); line-height: 1.05; }
    .tp-brand-sub { color: var(--tp-muted); font-size: .76rem; margin-top: .12rem; }

    .tp-hero {
        position: relative;
        overflow: hidden;
        border-radius: 24px;
        padding: 2.05rem 2.2rem;
        margin: .2rem 0 1.2rem 0;
        color: #FFFFFF;
        background:
            radial-gradient(circle at 88% 18%, rgba(6,182,212,.28), transparent 28%),
            radial-gradient(circle at 65% 100%, rgba(37,99,235,.35), transparent 35%),
            linear-gradient(120deg, #0F172A 0%, #172554 55%, #0F3A5B 100%);
        box-shadow: 0 18px 50px rgba(15, 23, 42, .12);
    }
    .tp-eyebrow {
        display: inline-flex;
        gap: .4rem;
        align-items: center;
        font-size: .78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .08em;
        color: #BAE6FD;
        margin-bottom: .75rem;
    }
    .tp-hero h1 {
        margin: 0;
        font-size: clamp(2rem, 4vw, 3.2rem);
        line-height: 1.03;
        letter-spacing: -.04em;
        color: #FFFFFF;
    }
    .tp-hero p {
        max-width: 760px;
        margin: .85rem 0 0 0;
        color: #D7E3F4;
        font-size: 1rem;
        line-height: 1.65;
    }
    .tp-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: .55rem;
        margin-top: 1.25rem;
    }
    .tp-chip {
        display: inline-flex;
        align-items: center;
        gap: .35rem;
        padding: .42rem .68rem;
        border: 1px solid rgba(255,255,255,.16);
        border-radius: 999px;
        background: rgba(255,255,255,.08);
        color: #E2E8F0;
        font-size: .78rem;
    }

    .tp-section-head {
        margin: 1.55rem 0 .8rem 0;
    }
    .tp-section-title {
        color: var(--tp-ink);
        font-size: 1.28rem;
        font-weight: 800;
        letter-spacing: -.02em;
    }
    .tp-section-copy {
        color: var(--tp-muted);
        font-size: .88rem;
        margin-top: .18rem;
    }

    .tp-card {
        min-height: 112px;
        padding: 1rem 1.05rem;
        border-radius: 18px;
        border: 1px solid var(--tp-border);
        background: #FFFFFF;
        box-shadow: 0 6px 24px rgba(15, 23, 42, .045);
    }
    .tp-card-label {
        color: var(--tp-muted);
        font-size: .76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .055em;
        margin-bottom: .48rem;
    }
    .tp-card-value {
        color: var(--tp-ink);
        font-size: 1.72rem;
        font-weight: 800;
        letter-spacing: -.035em;
        line-height: 1.05;
    }
    .tp-card-foot { color: var(--tp-muted); font-size: .75rem; margin-top: .48rem; }

    .tp-insight {
        height: 100%;
        padding: 1rem 1.05rem;
        border-radius: 16px;
        border: 1px solid #DBEAFE;
        background: linear-gradient(135deg, #EFF6FF 0%, #F0FDFA 100%);
    }
    .tp-insight-kicker {
        color: #1D4ED8;
        font-size: .72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .07em;
        margin-bottom: .38rem;
    }
    .tp-insight-text { color: #1E293B; font-size: .91rem; line-height: 1.5; }

    .tp-callout {
        padding: 1rem 1.1rem;
        border-radius: 16px;
        border: 1px solid var(--tp-border);
        background: #FFFFFF;
        color: #334155;
        font-size: .9rem;
        line-height: 1.55;
    }

    div[data-testid="stPlotlyChart"] {
        border: 1px solid var(--tp-border);
        border-radius: 18px;
        background: #FFFFFF;
        padding: .35rem .5rem .2rem .5rem;
        box-shadow: 0 6px 24px rgba(15, 23, 42, .04);
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--tp-border);
        border-radius: 16px;
        overflow: hidden;
    }
    div[data-testid="stDownloadButton"] button {
        border-radius: 12px;
        font-weight: 700;
    }
    div[role="radiogroup"] { gap: .2rem; }
    div[role="radiogroup"] label { border-radius: 999px; padding: .15rem .3rem; }

    .tp-footer {
        text-align: center;
        color: var(--tp-muted);
        font-size: .78rem;
        padding-top: 2.4rem;
    }

    @media (max-width: 800px) {
        .tp-hero { padding: 1.5rem 1.25rem; border-radius: 20px; }
        .tp-card { min-height: 98px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_compact(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "0"
    value = float(value)
    absolute = abs(value)
    if absolute >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if absolute >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if absolute >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def format_percent(value: float | None, decimals: int = 1) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.{decimals}f}%"


def metric_card(label: str, value: str, foot: str = "") -> None:
    st.markdown(
        f"""
        <div class="tp-card">
            <div class="tp-card-label">{escape(str(label))}</div>
            <div class="tp-card-value">{escape(str(value))}</div>
            <div class="tp-card-foot">{escape(str(foot))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(kicker: str, text: str) -> None:
    st.markdown(
        f"""
        <div class="tp-insight">
            <div class="tp-insight-kicker">{escape(str(kicker))}</div>
            <div class="tp-insight-text">{escape(str(text))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, copy: str = "") -> None:
    st.markdown(
        f"""
        <div class="tp-section-head">
            <div class="tp-section-title">{escape(title)}</div>
            <div class="tp-section-copy">{escape(copy)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig, height: int = 420, hovermode: str = "closest"):
    fig.update_layout(
        height=height,
        margin=dict(l=24, r=24, t=64, b=34),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif", color=INK, size=12),
        title=dict(font=dict(size=16, color=INK), x=0.02, xanchor="left"),
        legend_title_text="",
        hovermode=hovermode,
        colorway=PALETTE,
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=GRID,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
    )
    fig.update_yaxes(
        gridcolor=GRID,
        zeroline=False,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
    )
    return fig


@st.cache_data(show_spinner=False)
def load_parquet(filename: str) -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


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
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=file_name,
        mime="text/csv",
        use_container_width=True,
    )


def render_hero(min_date, max_date, service_count: int, data_through) -> None:
    st.markdown(
        f"""
        <div class="tp-hero">
            <div class="tp-eyebrow">🚆 Klang Valley mobility intelligence</div>
            <h1>TransitPulse Klang Valley</h1>
            <p>
                Turning public transport ridership and station-to-station demand into
                clear signals about how Klang Valley moves.
            </p>
            <div class="tp-chip-row">
                <span class="tp-chip">Historical ridership</span>
                <span class="tp-chip">Rapid Rail OD flows</span>
                <span class="tp-chip">{escape(str(service_count))} services available</span>
                <span class="tp-chip">{escape(str(min_date))} → {escape(str(max_date))}</span>
                <span class="tp-chip">Data through {escape(str(data_through))}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    ridership = load_parquet("daily_ridership_long.parquet")
    od = load_parquet("rapidrail_od_clean.parquet")
    station_summary = load_parquet("station_summary.parquet")
    pair_summary = load_parquet("station_pair_summary.parquet")

    if ridership.empty and od.empty:
        st.error(
            "Processed data files were not found. Run `python src/run_pipeline.py` "
            "and redeploy the generated files."
        )
        st.stop()

    if not ridership.empty:
        ridership = ridership.copy()
        ridership["date"] = pd.to_datetime(ridership["date"])
    if not od.empty:
        od = od.copy()
        od["date"] = pd.to_datetime(od["date"])

    with st.sidebar:
        st.markdown(
            """
            <div class="tp-brand">
                <div class="tp-logo">TP</div>
                <div>
                    <div class="tp-brand-name">TransitPulse</div>
                    <div class="tp-brand-sub">Klang Valley</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Explore the data")
        st.divider()

        if not ridership.empty:
            min_date = ridership["date"].min().date()
            max_date = ridership["date"].max().date()
            selected_dates = st.date_input(
                "Ridership period",
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
                "Transport services",
                options=services,
                default=services,
            )
            slider_max = max(3, min(12, len(services)))
            top_n_services = st.slider(
                "Services shown in overview",
                min_value=3,
                max_value=slider_max,
                value=min(7, slider_max),
            )
        else:
            min_date = max_date = None
            start_date = end_date = None
            services = []
            selected_services = []
            top_n_services = 7

        st.divider()
        st.caption("Ridership values represent recorded trips, not unique passengers.")
        st.markdown(
            "[GitHub repository](https://github.com/ckolavennu/TransitPulse-Klang-Valley)"
        )

    if not ridership.empty:
        ridership_filtered = filter_by_date(ridership, "date", start_date, end_date)
        if selected_services:
            ridership_filtered = ridership_filtered[
                ridership_filtered["service"].isin(selected_services)
            ]
        else:
            ridership_filtered = ridership_filtered.iloc[0:0]
    else:
        ridership_filtered = pd.DataFrame()

    service_count = ridership["service"].nunique() if not ridership.empty else 0
    date_candidates = []
    if not ridership.empty:
        date_candidates.append(ridership["date"].max().date())
    if not od.empty:
        date_candidates.append(od["date"].max().date())
    data_through = max(date_candidates) if date_candidates else "—"

    render_hero(min_date or "—", max_date or "—", service_count, data_through)

    navigation = st.radio(
        "Dashboard navigation",
        [
            "Overview",
            "Service Comparison",
            "OD Explorer",
            "Station Insights",
            "Data & Method",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    if navigation == "Overview":
        section_header(
            "Network overview",
            "A high-level view of demand across the selected period and services.",
        )

        if ridership_filtered.empty:
            st.info("Select at least one service to view ridership analytics.")
        else:
            daily_total = (
                ridership_filtered.groupby("date", as_index=False)["ridership"]
                .sum()
                .sort_values("date")
            )
            service_total = (
                ridership_filtered.groupby("service", as_index=False)["ridership"]
                .sum()
                .sort_values("ridership", ascending=False)
            )

            total_trips = float(ridership_filtered["ridership"].sum())
            average_daily = float(daily_total["ridership"].mean())
            top_service = str(service_total.iloc[0]["service"]) if not service_total.empty else "—"
            top_service_trips = float(service_total.iloc[0]["ridership"]) if not service_total.empty else 0.0
            top_share = (top_service_trips / total_trips * 100) if total_trips > 0 else 0.0

            peak_row = daily_total.loc[daily_total["ridership"].idxmax()]
            peak_date = pd.to_datetime(peak_row["date"]).date()
            peak_trips = float(peak_row["ridership"])

            weekend_daily = ridership_filtered.groupby(
                ["date", "is_weekend"], as_index=False
            )["ridership"].sum()
            weekday_avg = weekend_daily.loc[
                weekend_daily["is_weekend"] == False, "ridership"
            ].mean()
            weekend_avg = weekend_daily.loc[
                weekend_daily["is_weekend"] == True, "ridership"
            ].mean()
            weekend_delta = (
                ((weekend_avg - weekday_avg) / weekday_avg * 100)
                if pd.notna(weekday_avg) and weekday_avg
                else None
            )

            cols = st.columns(4)
            with cols[0]:
                metric_card("Total trips", format_compact(total_trips), f"{start_date} → {end_date}")
            with cols[1]:
                metric_card("Average daily", format_compact(average_daily), "Across selected services")
            with cols[2]:
                metric_card("Top service", top_service, f"{format_percent(top_share)} of selected trips")
            with cols[3]:
                metric_card("Peak day", format_compact(peak_trips), str(peak_date))

            section_header(
                "What stands out",
                "Automatically generated observations from the current filter selection.",
            )
            insight_cols = st.columns(3)
            with insight_cols[0]:
                insight_card(
                    "Demand leader",
                    f"{top_service} contributes {format_percent(top_share)} of trips within the current selection.",
                )
            with insight_cols[1]:
                insight_card(
                    "Peak demand",
                    f"The busiest recorded day in this view is {peak_date}, with {format_compact(peak_trips)} trips.",
                )
            with insight_cols[2]:
                if weekend_delta is None or pd.isna(weekend_delta):
                    weekend_text = "There is not enough data to compare weekday and weekend demand."
                elif weekend_delta < 0:
                    weekend_text = f"Weekend daily demand averages {abs(weekend_delta):.1f}% lower than weekday demand."
                else:
                    weekend_text = f"Weekend daily demand averages {weekend_delta:.1f}% higher than weekday demand."
                insight_card("Weekday pattern", weekend_text)

            section_header(
                "Ridership over time",
                "The highest-volume selected services are prioritised for readability.",
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
                title=f"Monthly ridership trend · top {len(top_services)} services",
                color_discrete_sequence=PALETTE,
            )
            fig_monthly.update_traces(line=dict(width=2.4))
            fig_monthly = style_chart(fig_monthly, height=470, hovermode="x unified")
            fig_monthly.update_yaxes(tickformat="~s", title_text="Trips")
            fig_monthly.update_xaxes(title_text="")
            st.plotly_chart(fig_monthly, use_container_width=True)

            left, right = st.columns([1.2, 1])
            with left:
                fig_service = px.bar(
                    service_total.head(10).sort_values("ridership"),
                    x="ridership",
                    y="service",
                    orientation="h",
                    title="Largest services by selected-period ridership",
                    color="ridership",
                    color_continuous_scale=["#BFDBFE", "#2563EB"],
                )
                fig_service.update_layout(coloraxis_showscale=False)
                fig_service.update_yaxes(title_text="")
                fig_service.update_xaxes(title_text="Trips", tickformat="~s")
                fig_service = style_chart(fig_service, height=430)
                st.plotly_chart(fig_service, use_container_width=True)

            with right:
                pie_data = service_total.head(7).copy()
                if len(service_total) > 7:
                    other_value = service_total.iloc[7:]["ridership"].sum()
                    pie_data = pd.concat(
                        [
                            pie_data,
                            pd.DataFrame([{"service": "Other selected", "ridership": other_value}]),
                        ],
                        ignore_index=True,
                    )
                fig_share = px.pie(
                    pie_data,
                    names="service",
                    values="ridership",
                    hole=0.64,
                    title="Share of selected ridership",
                    color_discrete_sequence=PALETTE,
                )
                fig_share.update_traces(
                    textposition="inside",
                    textinfo="percent",
                    hovertemplate="<b>%{label}</b><br>%{value:,.0f} trips<br>%{percent}<extra></extra>",
                )
                fig_share = style_chart(fig_share, height=430)
                st.plotly_chart(fig_share, use_container_width=True)

    elif navigation == "Service Comparison":
        section_header(
            "Service comparison",
            "Compare demand intensity, daily movement and weekday/weekend behaviour.",
        )

        if ridership_filtered.empty:
            st.info("Select at least one service in the sidebar.")
        else:
            service_total = (
                ridership_filtered.groupby("service", as_index=False)["ridership"]
                .sum()
                .sort_values("ridership", ascending=False)
            )
            default_focus = service_total.head(min(5, len(service_total)))["service"].tolist()
            focus_services = st.multiselect(
                "Services to compare closely",
                options=service_total["service"].tolist(),
                default=default_focus,
                key="service_focus",
            )

            if not focus_services:
                st.info("Choose at least one service to build the comparison.")
            else:
                comparison = ridership_filtered[
                    ridership_filtered["service"].isin(focus_services)
                ].copy()

                rolling = st.toggle("Smooth daily trend with a 7-day average", value=True)
                daily_service = (
                    comparison.groupby(["date", "service"], as_index=False)["ridership"]
                    .sum()
                    .sort_values(["service", "date"])
                )
                if rolling:
                    daily_service["ridership_display"] = daily_service.groupby("service")["ridership"].transform(
                        lambda s: s.rolling(7, min_periods=1).mean()
                    )
                    y_col = "ridership_display"
                    trend_title = "Daily demand · 7-day rolling average"
                else:
                    y_col = "ridership"
                    trend_title = "Daily demand"

                fig_daily = px.line(
                    daily_service,
                    x="date",
                    y=y_col,
                    color="service",
                    title=trend_title,
                    color_discrete_sequence=PALETTE,
                )
                fig_daily.update_traces(line=dict(width=2.3))
                fig_daily.update_xaxes(title_text="")
                fig_daily.update_yaxes(title_text="Trips", tickformat="~s")
                fig_daily = style_chart(fig_daily, height=455, hovermode="x unified")
                st.plotly_chart(fig_daily, use_container_width=True)

                left, right = st.columns(2)
                with left:
                    weekday_summary = comparison.groupby(
                        ["service", "is_weekend"], as_index=False
                    )["ridership"].mean()
                    weekday_summary["day_type"] = weekday_summary["is_weekend"].map(
                        {True: "Weekend", False: "Weekday"}
                    )
                    fig_weekday = px.bar(
                        weekday_summary,
                        x="service",
                        y="ridership",
                        color="day_type",
                        barmode="group",
                        title="Average day · weekday vs weekend",
                        color_discrete_map={"Weekday": ACCENT, "Weekend": ACCENT_2},
                    )
                    fig_weekday.update_xaxes(title_text="", tickangle=-20)
                    fig_weekday.update_yaxes(title_text="Average trips", tickformat="~s")
                    fig_weekday = style_chart(fig_weekday, height=420)
                    st.plotly_chart(fig_weekday, use_container_width=True)

                with right:
                    monthly_service = comparison.groupby(
                        ["month", "service"], as_index=False
                    )["ridership"].sum()
                    monthly_rank = monthly_service.groupby(
                        "service", as_index=False
                    )["ridership"].mean().sort_values("ridership", ascending=True)
                    fig_rank = px.bar(
                        monthly_rank,
                        x="ridership",
                        y="service",
                        orientation="h",
                        title="Average monthly ridership",
                        color="ridership",
                        color_continuous_scale=["#CFFAFE", "#0891B2"],
                    )
                    fig_rank.update_layout(coloraxis_showscale=False)
                    fig_rank.update_xaxes(title_text="Average monthly trips", tickformat="~s")
                    fig_rank.update_yaxes(title_text="")
                    fig_rank = style_chart(fig_rank, height=420)
                    st.plotly_chart(fig_rank, use_container_width=True)

                section_header(
                    "Service summary",
                    "Totals for the full sidebar selection, not only the focused comparison.",
                )
                summary_table = service_total.rename(
                    columns={"service": "Service", "ridership": "Trips"}
                ).copy()
                summary_table["Share"] = (
                    summary_table["Trips"] / summary_table["Trips"].sum() * 100
                ).round(2)
                st.dataframe(
                    summary_table,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Trips": st.column_config.NumberColumn(format="%,d"),
                        "Share": st.column_config.NumberColumn(format="%.2f%%"),
                    },
                )
                make_download_button(summary_table, "Download service summary", "service_summary.csv")

    elif navigation == "OD Explorer":
        section_header(
            "Origin–destination explorer",
            "See which Rapid Rail station pairs carry the strongest recorded flows.",
        )

        if od.empty:
            st.info("Origin–destination data is not available.")
        else:
            od_min = od["date"].min().date()
            od_max = od["date"].max().date()

            controls = st.columns([1.3, 1, 1])
            with controls[0]:
                od_dates = st.date_input(
                    "OD period",
                    value=(od_min, od_max),
                    min_value=od_min,
                    max_value=od_max,
                    key="od_dates",
                )
            with controls[1]:
                top_n = st.slider("Pairs shown", 10, 50, 20)
            with controls[2]:
                min_trips = st.number_input(
                    "Minimum aggregate trips",
                    min_value=0,
                    value=0,
                    step=1000,
                )

            if isinstance(od_dates, tuple) and len(od_dates) == 2:
                od_start, od_end = od_dates
            else:
                od_start, od_end = od_min, od_max

            od_filtered = filter_by_date(od, "date", od_start, od_end)
            pair_filtered = (
                od_filtered.groupby(
                    ["origin_code", "origin_name", "destination_code", "destination_name"],
                    dropna=False,
                    as_index=False,
                )["ridership"]
                .sum()
                .sort_values("ridership", ascending=False)
            )
            pair_filtered = pair_filtered[pair_filtered["ridership"] >= min_trips]

            if pair_filtered.empty:
                st.info("No station pairs match the current controls.")
            else:
                total_od = float(pair_filtered["ridership"].sum())
                top_pair = pair_filtered.iloc[0]
                unique_origins = int(pair_filtered["origin_name"].nunique())

                cards = st.columns(4)
                with cards[0]:
                    metric_card("OD trips", format_compact(total_od), f"{od_start} → {od_end}")
                with cards[1]:
                    metric_card("Station pairs", f"{len(pair_filtered):,}", "After minimum-trip filter")
                with cards[2]:
                    metric_card("Origins", f"{unique_origins:,}", "Unique origin stations")
                with cards[3]:
                    metric_card(
                        "Top flow",
                        format_compact(top_pair["ridership"]),
                        f"{top_pair['origin_name']} → {top_pair['destination_name']}",
                    )

                display_pairs = pair_filtered.head(top_n).copy()
                display_pairs["station_pair"] = (
                    display_pairs["origin_name"].astype(str)
                    + " → "
                    + display_pairs["destination_name"].astype(str)
                )

                fig_pairs = px.bar(
                    display_pairs.sort_values("ridership"),
                    x="ridership",
                    y="station_pair",
                    orientation="h",
                    title=f"Busiest station-to-station flows · top {len(display_pairs)}",
                    color="ridership",
                    color_continuous_scale=["#CFFAFE", "#2563EB"],
                )
                fig_pairs.update_layout(coloraxis_showscale=False)
                fig_pairs.update_xaxes(title_text="Trips", tickformat="~s")
                fig_pairs.update_yaxes(title_text="")
                fig_pairs = style_chart(fig_pairs, height=max(500, len(display_pairs) * 25))
                st.plotly_chart(fig_pairs, use_container_width=True)

                origin_summary = (
                    od_filtered.groupby("origin_name", as_index=False)["ridership"]
                    .sum()
                    .sort_values("ridership", ascending=False)
                    .head(12)
                )
                destination_summary = (
                    od_filtered.groupby("destination_name", as_index=False)["ridership"]
                    .sum()
                    .sort_values("ridership", ascending=False)
                    .head(12)
                )

                left, right = st.columns(2)
                with left:
                    fig_origins = px.bar(
                        origin_summary.sort_values("ridership"),
                        x="ridership",
                        y="origin_name",
                        orientation="h",
                        title="Top origin stations",
                        color="ridership",
                        color_continuous_scale=["#DBEAFE", "#2563EB"],
                    )
                    fig_origins.update_layout(coloraxis_showscale=False)
                    fig_origins.update_xaxes(title_text="Outbound trips", tickformat="~s")
                    fig_origins.update_yaxes(title_text="")
                    fig_origins = style_chart(fig_origins, height=430)
                    st.plotly_chart(fig_origins, use_container_width=True)

                with right:
                    fig_destinations = px.bar(
                        destination_summary.sort_values("ridership"),
                        x="ridership",
                        y="destination_name",
                        orientation="h",
                        title="Top destination stations",
                        color="ridership",
                        color_continuous_scale=["#CCFBF1", "#0F766E"],
                    )
                    fig_destinations.update_layout(coloraxis_showscale=False)
                    fig_destinations.update_xaxes(title_text="Inbound trips", tickformat="~s")
                    fig_destinations.update_yaxes(title_text="")
                    fig_destinations = style_chart(fig_destinations, height=430)
                    st.plotly_chart(fig_destinations, use_container_width=True)

                with st.expander("View station-pair table"):
                    table = display_pairs[
                        ["origin_name", "destination_name", "ridership"]
                    ].rename(
                        columns={
                            "origin_name": "Origin",
                            "destination_name": "Destination",
                            "ridership": "Trips",
                        }
                    )
                    st.dataframe(
                        table,
                        use_container_width=True,
                        hide_index=True,
                        column_config={"Trips": st.column_config.NumberColumn(format="%,d")},
                    )
                    make_download_button(table, "Download displayed pairs", "top_station_pairs.csv")

    elif navigation == "Station Insights":
        section_header(
            "Station profile",
            "Follow the inbound and outbound travel relationships of a selected Rapid Rail station.",
        )

        if station_summary.empty or od.empty:
            st.info("Station-level data is not available.")
        else:
            stations = sorted(station_summary["station_name"].dropna().unique())
            selected_station = st.selectbox("Choose a station", stations, key="station_select")

            station_row = station_summary[
                station_summary["station_name"] == selected_station
            ].head(1)

            if station_row.empty:
                st.info("No summary data was found for this station.")
            else:
                row = station_row.iloc[0]
                activity_sorted = station_summary.sort_values(
                    "total_station_activity", ascending=False
                ).reset_index(drop=True)
                rank_rows = activity_sorted.index[
                    activity_sorted["station_name"] == selected_station
                ].tolist()
                rank = rank_rows[0] + 1 if rank_rows else None

                outbound = float(row["outbound_trips"])
                inbound = float(row["inbound_trips"])
                total_activity = float(row["total_station_activity"])
                balance = ((outbound - inbound) / total_activity * 100) if total_activity else 0.0

                cards = st.columns(4)
                with cards[0]:
                    metric_card("Outbound", format_compact(outbound), "Trips starting here")
                with cards[1]:
                    metric_card("Inbound", format_compact(inbound), "Trips ending here")
                with cards[2]:
                    metric_card("Total activity", format_compact(total_activity), "Inbound + outbound")
                with cards[3]:
                    metric_card(
                        "Activity rank",
                        f"#{rank}" if rank is not None else "—",
                        f"Among {len(activity_sorted)} stations",
                    )

                if abs(balance) < 2:
                    balance_text = f"{selected_station} is closely balanced between inbound and outbound activity."
                elif balance > 0:
                    balance_text = (
                        f"{selected_station} records more outbound than inbound activity "
                        f"({abs(balance):.1f}% net outbound tilt)."
                    )
                else:
                    balance_text = (
                        f"{selected_station} records more inbound than outbound activity "
                        f"({abs(balance):.1f}% net inbound tilt)."
                    )

                section_header("Station signal")
                insight_card("Flow balance", balance_text)

                outgoing = (
                    od[od["origin_name"] == selected_station]
                    .groupby("destination_name", as_index=False)["ridership"]
                    .sum()
                    .sort_values("ridership", ascending=False)
                    .head(12)
                )
                incoming = (
                    od[od["destination_name"] == selected_station]
                    .groupby("origin_name", as_index=False)["ridership"]
                    .sum()
                    .sort_values("ridership", ascending=False)
                    .head(12)
                )

                left, right = st.columns(2)
                with left:
                    fig_out = px.bar(
                        outgoing.sort_values("ridership"),
                        x="ridership",
                        y="destination_name",
                        orientation="h",
                        title=f"Where riders go from {selected_station}",
                        color="ridership",
                        color_continuous_scale=["#DBEAFE", "#2563EB"],
                    )
                    fig_out.update_layout(coloraxis_showscale=False)
                    fig_out.update_xaxes(title_text="Outbound trips", tickformat="~s")
                    fig_out.update_yaxes(title_text="")
                    fig_out = style_chart(fig_out, height=455)
                    st.plotly_chart(fig_out, use_container_width=True)

                with right:
                    fig_in = px.bar(
                        incoming.sort_values("ridership"),
                        x="ridership",
                        y="origin_name",
                        orientation="h",
                        title="Where riders arrive from",
                        color="ridership",
                        color_continuous_scale=["#CCFBF1", "#0F766E"],
                    )
                    fig_in.update_layout(coloraxis_showscale=False)
                    fig_in.update_xaxes(title_text="Inbound trips", tickformat="~s")
                    fig_in.update_yaxes(title_text="")
                    fig_in = style_chart(fig_in, height=455)
                    st.plotly_chart(fig_in, use_container_width=True)

                with st.expander("View station flow tables"):
                    left, right = st.columns(2)
                    with left:
                        st.caption("Top destinations")
                        st.dataframe(
                            outgoing.rename(columns={"destination_name": "Destination", "ridership": "Trips"}),
                            use_container_width=True,
                            hide_index=True,
                        )
                    with right:
                        st.caption("Top origins")
                        st.dataframe(
                            incoming.rename(columns={"origin_name": "Origin", "ridership": "Trips"}),
                            use_container_width=True,
                            hide_index=True,
                        )

    else:
        section_header(
            "Data & methodology",
            "What the dashboard measures, where the data comes from, and how to interpret it.",
        )

        st.markdown(
            """
            <div class="tp-callout">
                <strong>What TransitPulse currently measures</strong><br><br>
                Historical public transport ridership, service-level demand, Rapid Rail
                origin–destination flows, and station-level inbound/outbound activity.
                The project is designed as a demand-intelligence dashboard; it does not
                currently claim to measure delays, cancellations or operational reliability.
            </div>
            """,
            unsafe_allow_html=True,
        )

        left, right = st.columns(2)
        with left:
            st.subheader("Data sources")
            st.markdown(
                """
                **Daily Public Transport Ridership**  
                Malaysia's official open-data portal, data.gov.my.

                **Rapid Rail Daily Origin–Destination Ridership**  
                Station-to-station ridership records for the Klang Valley Rapid Rail network.

                [Open ridership dataset](https://data.gov.my/data-catalogue/ridership_headline)  
                [Open Rapid Rail OD dataset](https://data.gov.my/data-catalogue/ridership_od_rapidrail_daily)
                """
            )

        with right:
            st.subheader("Interpretation")
            st.markdown(
                """
                - **Ridership means trips, not unique passengers.**
                - A single traveller can contribute multiple trips.
                - OD records describe station-to-station movements; transfers may form part of a longer journey.
                - Current outputs are descriptive analytics, not causal claims.
                """
            )

        section_header("Processed data health")
        file_status = pd.DataFrame(
            [
                {"Dataset": "Daily ridership (long)", "Available": not ridership.empty, "Rows": len(ridership)},
                {"Dataset": "Rapid Rail OD", "Available": not od.empty, "Rows": len(od)},
                {"Dataset": "Station summary", "Available": not station_summary.empty, "Rows": len(station_summary)},
                {"Dataset": "Station-pair summary", "Available": not pair_summary.empty, "Rows": len(pair_summary)},
            ]
        )
        st.dataframe(
            file_status,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Available": st.column_config.CheckboxColumn(),
                "Rows": st.column_config.NumberColumn(format="%,d"),
            },
        )

        st.markdown(
            """
            <div class="tp-callout">
                <strong>Next analytical layer</strong><br>
                Station mapping, catchment-area analysis and a transparent Transit
                Accessibility Score are planned as the next major expansion.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="tp-footer">
            TransitPulse Klang Valley · Built with Python, Plotly and Streamlit · Official Malaysian open transport data
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
