# TransitPulse Klang Valley

**TransitPulse Klang Valley** is an interactive rail-accessibility and transport-demand project for the Klang Valley.

**Live app:** https://transitpulse-klang.streamlit.app/

The project is built around two practical questions:

1. **For commuters:** *How well does public transport serve a place I care about?*
2. **For planners and analysts:** *Where does observed rail demand appear stronger than station-level network access?*

Rather than treating charts as the product, TransitPulse uses ridership, origin-destination demand and official GTFS network data as evidence behind an interactive accessibility experience.

---

## What the app does

### 📍 Explore My Area

Choose a Rapid Rail station or click a location on the map to see:

- nearest Rapid Rail station
- straight-line distance to rail
- an 800 m station-access catchment proxy
- nearby rail lines
- direct rail reach before transfers
- nearby stations within 1.5 km
- a location-level **Accessibility Score**
- observed top destinations from the nearest station

The goal is not to replace Google Maps or a journey planner. TransitPulse answers a different question:

> **How good is the rail access around this place?**

### 🗺️ Network Explorer

Explore the Klang Valley rail network as a planning/analysis layer:

- official Rapid Rail station geography and route shapes
- station-level accessibility
- observed 2026 OD demand
- demand vs accessibility quadrant analysis
- station catchment proxies
- a **Demand–Access Gap** for screening stations that merit closer review

The gap is deliberately presented as a screening indicator, **not** as proof that an area is a transit desert.

### 📊 Demand Evidence

Historical charts remain available as evidence for the model:

- public transport ridership trends
- service comparison
- high-volume Rapid Rail station pairs

---

## Current scoring model

### Location Accessibility Score

The current location score combines:

- **45% proximity** — distance to the nearest Rapid Rail stop
- **20% line choice** — number of nearby rail lines
- **25% direct rail reach** — stops reachable on nearby lines before transfers
- **10% station density** — number of stops inside the 800 m proxy

The score is designed to be interpretable and will evolve as better accessibility inputs are added.

### Station Accessibility

Station-level accessibility is calculated **without ridership** using:

- nearby line choice
- direct rail reach
- nearby station density

This lets the project compare access and demand independently.

### Demand Score

Demand is the percentile rank of observed station activity from the Rapid Rail origin-destination dataset.

### Demand–Access Gap

The current gap is:

```text
Demand percentile - Accessibility percentile
```

floored at zero.

A larger value means observed station demand ranks higher than the station's relative accessibility ranking.

---

## Data sources

TransitPulse currently uses official Malaysian open transport data.

### Daily Public Transport Ridership

Source:  
https://data.gov.my/data-catalogue/ridership_headline

Used for:

- historical public transport demand
- service-level ridership trends
- evidence/context

### Rapid Rail Daily Origin-Destination Ridership

Source:  
https://data.gov.my/data-catalogue/ridership_od_rapidrail_daily

Used for:

- station activity
- origin-destination demand
- top station movements
- demand scoring

### Rapid Rail KL GTFS Static

Documentation:  
https://developer.data.gov.my/realtime-api/gtfs-static

Endpoint used by the app:

```text
https://api.data.gov.my/gtfs-static/prasarana?category=rapid-rail-kl
```

Used for:

- station coordinates
- rail routes
- route shapes
- station-to-line relationships
- accessibility/connectivity modelling

The Streamlit app caches the GTFS feed for 24 hours to avoid unnecessary repeated requests.

---

## Important interpretation notes

- Ridership represents **trips, not unique passengers**.
- OD journeys can include transfers between Rapid Rail lines.
- The 800 m radius is a **straight-line catchment proxy**, not a routed walking path.
- The current accessibility model does not yet include feeder buses, pedestrian barriers, population, employment density or service frequency.
- The Demand–Access Gap is a screening metric and should not be interpreted as a definitive policy recommendation.

---

## Next analytical layers

The strongest next improvements are:

- population and population-density data
- employment/activity density
- actual pedestrian-network walking distances
- feeder-bus accessibility
- rail service frequency and operating hours
- socioeconomic/mobility-need indicators
- area-to-area comparison
- automated data refresh

These additions would allow TransitPulse to move from a station-centric network model toward a stronger **underserved-area / transit-gap model**.

---

## Tech stack

- **Python**
- **Pandas / NumPy**
- **Parquet / PyArrow**
- **Streamlit**
- **Plotly**
- **Folium + streamlit-folium**
- **data.gov.my open datasets**
- **GTFS Static**
- **GitHub**
- **Streamlit Community Cloud**

---

## Run locally

Clone the project:

```bash
git clone https://github.com/ckolavennu/TransitPulse-Klang-Valley.git
cd TransitPulse-Klang-Valley
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the local data pipeline if you want to refresh the committed demand outputs:

```bash
python src/run_pipeline.py
```

Start the dashboard:

```bash
streamlit run dashboard/app.py
```

The accessibility views fetch the Rapid Rail KL GTFS Static feed from the official data.gov.my API at runtime.

---

## Project structure

```text
TransitPulse-Klang-Valley/
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── notebooks/
│
├── src/
│   ├── data_ingestion/
│   ├── data_cleaning/
│   ├── analysis/
│   └── run_pipeline.py
│
├── outputs/
├── README.md
├── PROJECT_PLAN.md
└── requirements.txt
```

---

## Portfolio purpose

TransitPulse is designed as a practical urban-mobility analytics project rather than a generic dashboard. It demonstrates:

- public API/data ingestion
- large origin-destination dataset processing
- data cleaning and modelling
- geospatial analysis
- GTFS parsing
- accessibility metric design
- demand/access comparison
- interactive mapping
- analytical communication
- deployed data-product development
