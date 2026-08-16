"""TransitPulse Klang Valley — commuter and planning explorer."""
from __future__ import annotations
from html import escape
from pathlib import Path
import sys

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
sys.path.insert(0, str(ROOT / "src"))

from analysis.accessibility import build_station_metrics, route_shape_data, score_location  # noqa: E402
from data_ingestion.gtfs_static import fetch_rapid_rail_gtfs  # noqa: E402

ACCENT = "#2563EB"
CYAN = "#06B6D4"
INK = "#0F172A"
COLORS = {
    "High demand / lower access": "#F97316",
    "High demand / strong access": "#2563EB",
    "Lower demand / strong access": "#10B981",
    "Lower demand / lower access": "#94A3B8",
}

st.set_page_config(page_title="TransitPulse Klang Valley", page_icon="🚆", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
.stApp{background:#F6F8FC}.block-container{max-width:1420px;padding-top:1.2rem;padding-bottom:3rem}
.hero{padding:2.2rem 2.3rem;border-radius:24px;color:white;background:linear-gradient(135deg,#081426,#123263 58%,#155E75);box-shadow:0 20px 55px rgba(15,23,42,.14);margin-bottom:1rem}
.hero .eyebrow{font-size:.75rem;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:#BAE6FD}.hero h1{font-size:clamp(2.2rem,5vw,4.3rem);line-height:1;letter-spacing:-.05em;margin:.65rem 0;color:white}.hero p{max-width:850px;color:#D7E3F4;line-height:1.65}
.cards,.metrics{display:grid;gap:.8rem}.cards{grid-template-columns:repeat(2,1fr);margin:1rem 0}.metrics{grid-template-columns:repeat(4,1fr);margin:.8rem 0 1rem}.card,.metric{background:white;border:1px solid #E2E8F0;border-radius:18px;padding:1rem 1.1rem;box-shadow:0 6px 22px rgba(15,23,42,.04)}
.card .k,.metric .l,.kicker{color:#2563EB;font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em}.card .t{font-size:1.15rem;font-weight:800;color:#0F172A;margin:.3rem 0}.card .c,.metric .n,.copy{color:#64748B;line-height:1.5}.metric .v{font-size:1.6rem;font-weight:850;color:#0F172A;margin-top:.35rem}.metric .l{color:#64748B}.metric .n{font-size:.75rem;margin-top:.35rem}
.title{font-size:1.65rem;font-weight:850;color:#0F172A;margin:.2rem 0}.note{border:1px solid #E2E8F0;background:white;border-radius:14px;padding:.8rem .95rem;color:#64748B;line-height:1.5}.insight{border:1px solid #BFDBFE;background:linear-gradient(135deg,#EFF6FF,#ECFEFF);border-radius:14px;padding:.85rem 1rem;color:#1E3A5F;margin:.7rem 0}
div[data-testid="stPlotlyChart"],div[data-testid="stDataFrame"]{background:white;border:1px solid #E2E8F0;border-radius:16px;padding:.2rem}
@media(max-width:800px){.cards,.metrics{grid-template-columns:1fr}.hero{padding:1.5rem 1.2rem}}
</style>
""", unsafe_allow_html=True)


def section(kicker, title, copy):
    st.markdown(f'<div class="kicker">{escape(kicker)}</div><div class="title">{escape(title)}</div><div class="copy">{escape(copy)}</div>', unsafe_allow_html=True)


def metric_cards(items):
    html = ''.join(f'<div class="metric"><div class="l">{escape(a)}</div><div class="v">{escape(b)}</div><div class="n">{escape(c)}</div></div>' for a,b,c in items)
    st.markdown(f'<div class="metrics">{html}</div>', unsafe_allow_html=True)


def compact(v):
    v=float(v or 0)
    return f"{v/1e9:.2f}B" if abs(v)>=1e9 else f"{v/1e6:.2f}M" if abs(v)>=1e6 else f"{v/1e3:.1f}K" if abs(v)>=1e3 else f"{v:,.0f}"


def chart_style(fig,h=430):
    fig.update_layout(height=h,margin=dict(l=18,r=18,t=52,b=28),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color=INK),legend_title_text="")
    fig.update_xaxes(gridcolor="#EAEFF5",zeroline=False); fig.update_yaxes(gridcolor="#EAEFF5",zeroline=False)


@st.cache_data(show_spinner=False)
def parquet(name):
    p=DATA/name
    return pd.read_parquet(p) if p.exists() else pd.DataFrame()


@st.cache_data(ttl=86400,show_spinner=False)
def network_data():
    return fetch_rapid_rail_gtfs(timeout=12)


def load_network(station_summary):
    try:
        with st.spinner("Loading Rapid Rail network…"):
            stops,routes,trips,shapes=network_data()
            stations=build_station_metrics(stops,routes,station_summary)
        return stations,routes,trips,shapes,None
    except Exception as e:
        return pd.DataFrame(),pd.DataFrame(),pd.DataFrame(),pd.DataFrame(),str(e)


def rail_map(stations,routes,trips,shapes,selected=None,catchments=False):
    center=[3.13,101.69]
    zoom=10
    if selected is not None:
        center=[float(selected.stop_lat),float(selected.stop_lon)]; zoom=13
    m=folium.Map(location=center,zoom_start=zoom,tiles="CartoDB positron",prefer_canvas=True,control_scale=True)
    for label,color,coords in route_shape_data(routes,trips,shapes):
        folium.PolyLine(coords,color=color,weight=3,opacity=.5,tooltip=label).add_to(m)
    for _,r in stations.iterrows():
        if catchments:
            folium.Circle([float(r.stop_lat),float(r.stop_lon)],radius=800,color="#93C5FD",weight=.6,fill=True,fill_opacity=.025).add_to(m)
        col=COLORS.get(str(r.quadrant),"#64748B")
        popup=f"<b>{escape(str(r.station_label))}</b><br>Accessibility: {float(r.accessibility_score):.0f}/100<br>Demand percentile: {float(r.demand_score):.0f}"
        folium.CircleMarker([float(r.stop_lat),float(r.stop_lon)],radius=5,color="white",weight=1,fill=True,fill_color=col,fill_opacity=.9,tooltip=str(r.station_label),popup=popup).add_to(m)
    if selected is not None:
        folium.Circle([float(selected.stop_lat),float(selected.stop_lon)],radius=800,color=ACCENT,weight=2,dash_array="6 5",fill=True,fill_opacity=.05,tooltip="800 m catchment proxy").add_to(m)
    return m


def home(ridership,od,stations):
    st.markdown("""
    <section class="hero"><div class="eyebrow">Transit accessibility + demand intelligence</div><h1>How well does public transport serve you — and the city?</h1><p>TransitPulse helps commuters understand the rail access around a place, while giving planners and analysts a way to investigate where observed travel demand appears stronger than network access.</p></section>
    <div class="cards"><div class="card"><div class="k">For commuters</div><div class="t">Would this area work for me without a car?</div><div class="c">Choose a rail station and see nearby access, network reach, demand and common destinations.</div></div><div class="card"><div class="k">For planners & analysts</div><div class="t">Where is demand stronger than network access?</div><div class="c">Compare demand with connectivity and surface stations that deserve closer investigation.</div></div></div>
    """,unsafe_allow_html=True)
    metric_cards([
        ("Services tracked",str(ridership.service.nunique() if not ridership.empty else 0),"Historical headline ridership."),
        ("OD stations",str(len(stations)),"Rapid Rail demand profiles."),
        ("Ridership through",str(ridership.date.max().date() if not ridership.empty else "—"),"Latest committed record."),
        ("OD demand through",str(od.date.max().date() if not od.empty else "—"),"Latest committed OD record."),
    ])
    st.markdown('<div class="note"><b>Why this page exists:</b> the charts are supporting evidence. The main product is the commuter explorer and the demand-vs-access planning view.</div>',unsafe_allow_html=True)


def commuter(station_summary,od):
    section("Commuter explorer","Start with a station, not a chart.","Choose a Rapid Rail station to understand its access, network reach and observed travel demand.")
    stations,routes,trips,shapes,error=load_network(station_summary)
    if error:
        st.error(f"Rail-network data is temporarily unavailable. Demand pages still work. Detail: {error}"); return
    label=st.selectbox("Choose a Rapid Rail station",stations.sort_values("station_label").station_label.tolist(),index=None,placeholder="Example: SP17: Bukit Jalil")
    if not label:
        st.info("Choose a station to load its access profile and map."); return
    row=stations[stations.station_label==label].iloc[0]
    result=score_location(float(row.stop_lat),float(row.stop_lon),stations)
    metric_cards([
        ("Accessibility",f"{result['accessibility_score']:.0f}/100","Composite rail-access score."),
        ("Nearby lines",str(result['line_count']),"Within the local access proxy."),
        ("Direct rail reach",f"{result['direct_reach']} stops","Before line transfers."),
        ("Observed demand",f"{float(row.demand_score):.0f}th pct",f"{compact(row.total_station_activity)} station trips."),
    ])
    st_folium(rail_map(stations,routes,trips,shapes,row),use_container_width=True,height=500,key="commuter_map")
    left,right=st.columns([1,1])
    with left:
        st.subheader("Nearby stations")
        near=result['within_1500'].copy(); near['Distance (m)']=(near.distance_km*1000).round().astype(int)
        st.dataframe(near[["station_label","Distance (m)","accessibility_score","demand_score"]].head(12).rename(columns={"station_label":"Station","accessibility_score":"Access","demand_score":"Demand"}),hide_index=True,use_container_width=True)
    with right:
        st.subheader("Top observed destinations")
        code=str(row.station_code).upper()
        out=od[od.origin_code.astype(str).str.upper()==code].groupby("destination_name",as_index=False).ridership.sum().sort_values("ridership",ascending=False).head(8) if not od.empty else pd.DataFrame()
        if out.empty: st.write("No matching OD demand found.")
        else:
            fig=px.bar(out.sort_values("ridership"),x="ridership",y="destination_name",orientation="h",labels={"ridership":"Trips","destination_name":""},color_discrete_sequence=[ACCENT]); chart_style(fig,380); st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="note"><b>Walking-distance note:</b> the 800 m catchment is a straight-line proxy. It does not yet model roads, crossings, station entrances, elevation or barriers.</div>',unsafe_allow_html=True)


def planning(station_summary,od):
    section("Network explorer","Where does observed demand outpace station access?","Compare Rapid Rail demand with station connectivity. Treat this as a screening tool, not proof of a transit desert.")
    stations,routes,trips,shapes,error=load_network(station_summary)
    if error:
        st.error(f"Rail-network data is temporarily unavailable. Demand pages still work. Detail: {error}"); return
    review=int((stations.quadrant=="High demand / lower access").sum())
    metric_cards([("Rail stops",str(len(stations)),"GTFS stations in model."),("Rail routes",str(routes.route_id.nunique()),"Official Rapid Rail feed."),("Priority review",str(review),"High demand / lower access."),("OD through",str(od.date.max().date() if not od.empty else "—"),"Demand evidence date.")])
    left,right=st.columns([1.1,1])
    with left:
        sc=stations[stations.total_station_activity>0].copy()
        fig=px.scatter(sc,x="access_percentile",y="demand_score",size="total_station_activity",size_max=25,color="quadrant",color_discrete_map=COLORS,hover_name="station_label",labels={"access_percentile":"Accessibility percentile","demand_score":"Demand percentile","quadrant":""}); fig.add_vline(x=50,line_dash="dot",line_color="#94A3B8"); fig.add_hline(y=50,line_dash="dot",line_color="#94A3B8"); chart_style(fig,480); st.plotly_chart(fig,use_container_width=True)
    with right:
        st.subheader("Stations to review first")
        p=stations[stations.quadrant=="High demand / lower access"].sort_values(["gap_score","demand_score"],ascending=False).head(12)
        st.dataframe(p[["station_label","demand_score","access_percentile","accessibility_score","gap_score"]].rename(columns={"station_label":"Station","demand_score":"Demand","access_percentile":"Access rank","accessibility_score":"Access score","gap_score":"Gap"}),hide_index=True,use_container_width=True,height=410)
    show=st.toggle("Load interactive network map",False)
    if show:
        catch=st.toggle("Show 800 m catchment proxies",False)
        st_folium(rail_map(stations,routes,trips,shapes,None,catch),use_container_width=True,height=590,key=f"network_{catch}")


def evidence(ridership,pairs):
    section("Demand evidence","The charts support the product.","Review the ridership and OD patterns behind the commuter and planning experiences.")
    if not ridership.empty:
        totals=ridership.groupby("service",as_index=False).ridership.sum().sort_values("ridership",ascending=False)
        monthly=ridership.groupby(["month","service"],as_index=False).ridership.sum(); monthly=monthly[monthly.service.isin(totals.head(7).service)]
        l,r=st.columns([1.25,1])
        with l:
            fig=px.line(monthly,x="month",y="ridership",color="service",labels={"month":"","ridership":"Trips","service":""},title="Monthly ridership — leading services"); chart_style(fig,450); st.plotly_chart(fig,use_container_width=True)
        with r:
            fig=px.bar(totals.head(10).sort_values("ridership"),x="ridership",y="service",orientation="h",labels={"ridership":"Trips","service":""},color_discrete_sequence=[ACCENT],title="Total trips by service"); chart_style(fig,450); st.plotly_chart(fig,use_container_width=True)
    if not pairs.empty:
        st.subheader("High-volume station pairs")
        x=pairs.head(12).copy(); x['pair']=x.origin_name+' → '+x.destination_name
        fig=px.bar(x.sort_values('ridership'),x='ridership',y='pair',orientation='h',color_discrete_sequence=[CYAN],labels={'ridership':'Trips','pair':''}); chart_style(fig,480); st.plotly_chart(fig,use_container_width=True)


def methodology():
    section("Methodology","Transparent scoring, explicit limitations.","TransitPulse separates accessibility from demand, then compares the two.")
    st.markdown("""
### Location accessibility
- **45% proximity** to the nearest Rapid Rail stop.
- **20% line choice** available locally.
- **25% direct rail reach** before transfers.
- **10% station density** within the 800 m proxy.

### Demand
Demand is based on the percentile rank of observed Rapid Rail station activity from origin-destination trips.

### Demand–Access Gap
`max(0, Demand percentile - Accessibility percentile)`

This is a **screening indicator**, not a definitive transit-desert score. A stronger model should add population and employment density, routed walking distance, feeder buses, frequency, operating hours and socioeconomic need.

Ridership values represent **trips, not unique passengers**.
""")


def main():
    # Startup uses only committed local data. GTFS/maps are lazy-loaded by page.
    ridership=parquet("daily_ridership_long.parquet"); od=parquet("rapidrail_od_clean.parquet"); station_summary=parquet("station_summary.parquet"); pairs=parquet("station_pair_summary.parquet")
    if not ridership.empty: ridership=ridership.copy(); ridership['date']=pd.to_datetime(ridership.date)
    if not od.empty: od=od.copy(); od['date']=pd.to_datetime(od.date)
    st.markdown("### 🚆 TransitPulse Klang Valley")
    page=st.radio("Navigate",["Home","📍 Explore My Area","🗺️ Network Explorer","📊 Demand Evidence","🧭 Methodology"],horizontal=True,label_visibility="collapsed")
    st.divider()
    if page=="Home": home(ridership,od,station_summary)
    elif page=="📍 Explore My Area": commuter(station_summary,od)
    elif page=="🗺️ Network Explorer": planning(station_summary,od)
    elif page=="📊 Demand Evidence": evidence(ridership,pairs)
    else: methodology()

if __name__=="__main__": main()
