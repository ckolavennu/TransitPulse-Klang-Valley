# TransitPulse Klang Valley

TransitPulse Klang Valley is a data analytics dashboard that explores public transport ridership and origin-destination demand across the Klang Valley. The project uses official Malaysian open transport data to identify usage patterns, busy services, high-demand station pairs, and station-level travel flows.

The aim is to turn public transport data into a clear, interactive dashboard that can support mobility analysis, portfolio storytelling, and future accessibility research.

---

## Project Objectives

This project focuses on three main questions:

1. How has public transport ridership changed over time?
2. Which services carry the highest number of trips?
3. Which Rapid Rail station pairs and stations generate the strongest travel demand?

Future versions may expand into station mapping, catchment areas, and a Transit Accessibility Score.

---

## Current Dashboard Features

The current Streamlit dashboard includes:

- Ridership overview KPIs
- Date range filtering
- Service filtering
- Monthly ridership trend analysis
- Top services by total ridership
- Ridership share by service
- Service comparison view
- Rapid Rail origin-destination explorer
- Top origin and destination stations
- Station-level insights
- Data notes and limitations
- Downloadable filtered data tables

---

## Data Sources

This project currently uses official public transport datasets from Malaysia's open data portal, data.gov.my.

### 1. Daily Public Transport Ridership

This dataset provides daily ridership figures for multiple public transport services in Malaysia, including services such as LRT, MRT, Monorail, Rapid Bus, KTM, ETS, and others.

Source page:  
https://data.gov.my/data-catalogue/ridership_headline

Direct CSV source:  
https://storage.data.gov.my/transportation/ridership_headline.csv

### 2. Daily Origin-Destination Ridership: Rapid Rail Klang Valley

This dataset provides daily station-to-station ridership for the Rapid Rail network in Klang Valley. It includes the date, origin station, destination station, and ridership value.

Source page:  
https://data.gov.my/data-catalogue/ridership_od_rapidrail_daily

Example yearly Parquet source:  
https://storage.data.gov.my/transportation/rail/rapidrail_2026_daily.parquet

---

## Important Data Interpretation Notes

- Ridership values represent the number of trips, not unique passengers.
- One person may make multiple trips in a day, so this dashboard should describe values as “trips” rather than “people.”
- Origin-destination data represents station-to-station movements, but a full passenger journey may involve line transfers.
- The dashboard is currently focused on historical demand analysis, not real-time delay detection.
- Real-time vehicle tracking may be added later, but delay analysis would require additional scheduled data collection and comparison against GTFS schedules.

---

## Project Structure

```text
transitpulse_klang_valley/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── dashboard/
│   └── app.py
│
├── notebooks/
│   └── 01_data_exploration.ipynb
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
├── requirements.txt
└── .gitignore
```

---

## How to Run Locally

Clone the repository and move into the project folder:

```bash
cd transitpulse_klang_valley
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the data pipeline:

```bash
python src/run_pipeline.py
```

Launch the dashboard:

```bash
streamlit run dashboard/app.py
```

---

## Current Status

The current version is a working MVP. It successfully loads official ridership data, creates processed analytical outputs, and displays them in a Streamlit dashboard.

Completed:

- Project structure created
- Data ingestion pipeline created
- Data cleaning scripts created
- Processed summary tables generated
- Streamlit dashboard MVP created
- Dashboard V2 layout added
- Overview, service comparison, OD explorer, station insights, and data notes pages working

---

## Planned Improvements

Next improvements include:

1. Add screenshots to README
2. Improve visual design and dashboard layout
3. Add more explanatory insight cards
4. Add station map using GTFS Static stop data
5. Build station catchment area analysis
6. Create a Transit Accessibility Score
7. Deploy dashboard on Streamlit Community Cloud
8. Add a portfolio case study page

---

## Limitations

This project does not currently measure delays, cancellations, or service reliability. The current dashboard focuses on historical ridership and station-to-station demand. Real-time vehicle positions and delay analysis may be explored in a later version if sufficient data collection is implemented.

---

## Portfolio Summary

TransitPulse Klang Valley demonstrates data ingestion, data cleaning, exploratory analysis, dashboard development, and public-sector open data usage. It is designed as a practical data analytics portfolio project focused on transport demand and accessibility in Klang Valley.
