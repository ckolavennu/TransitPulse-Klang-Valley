# TransitPulse Klang Valley — Project Plan

## 1. Product Definition

TransitPulse Klang Valley is an interactive public-transport accessibility and demand-intelligence project.

The product is now centred on two user needs:

### Direction 1 — Commuter Explorer

**Question:** How well does public transport serve a place I care about?

Users can choose a Rapid Rail station or click a location on the map to understand:

- nearest rail access
- station proximity
- nearby rail lines
- direct rail reach
- nearby stations
- station demand
- common destinations
- overall location accessibility

### Direction 2 — Network & Planning Explorer

**Question:** Where does observed transport demand appear stronger than station-level network access?

The network view combines:

- Rapid Rail geography
- station connectivity
- station density
- line availability
- OD demand
- demand/access comparison

The aim is to surface areas/stations that merit closer investigation, while clearly distinguishing exploratory indicators from definitive policy claims.

---

## 2. Core Problem

Public transport datasets can describe ridership and routes, but raw datasets do not directly answer practical questions such as:

- Is a location well served by rail?
- What rail options exist near it?
- How much of the network is directly reachable?
- Which stations experience high observed demand despite weaker network access?
- Where should an analyst investigate potential accessibility gaps further?

TransitPulse combines official open transport datasets into a single interactive analytical layer designed around those questions.

---

## 3. Current Data Layers

### Demand Layer

Built from:

- Daily Public Transport Ridership
- Rapid Rail Daily Origin-Destination Ridership

Provides:

- ridership trends
- service comparisons
- station activity
- OD flows
- demand percentiles

### Accessibility Layer

Built from the official Rapid Rail KL GTFS Static feed.

Provides:

- station coordinates
- route membership
- route shapes
- nearby station density
- line choice
- direct rail reach
- accessibility scoring

### Combined Layer

Combines independent demand and accessibility measures to create:

- demand vs accessibility quadrants
- a Demand–Access Gap
- station-level screening/prioritisation views

---

## 4. Current Product Experience

### Explore My Area

Users can:

- select a Rapid Rail station
- click a location on the map
- see the nearest station
- estimate rail proximity
- view an 800 m straight-line catchment proxy
- see nearby lines
- see direct rail reach
- see nearby stations
- inspect top observed destinations
- view a location Accessibility Score

### Network Explorer

Users can:

- see the Rapid Rail network on a map
- view route shapes
- inspect station demand and accessibility
- show 800 m station catchment proxies
- compare demand and accessibility in a quadrant chart
- identify high-demand / lower-access stations
- inspect a ranked review table

### Demand Evidence

Users can still inspect:

- historical service ridership trends
- service totals
- high-volume station-to-station movements

These charts support the product rather than define it.

### Methodology

The app explicitly documents:

- score components
- demand/access separation
- data sources
- limitations
- interpretation rules
- next analytical inputs

---

## 5. Scoring Framework

### Location Accessibility Score

Current weights:

- 45% proximity to nearest Rapid Rail stop
- 20% nearby line choice
- 25% direct rail reach
- 10% nearby station density

### Station Accessibility Score

Uses network characteristics only:

- accessible lines around the station
- direct reach on those lines
- nearby station density

Demand is intentionally excluded so that access and observed usage can be compared independently.

### Demand Score

Percentile rank of 2026 station activity from Rapid Rail OD data.

### Demand–Access Gap

```text
max(0, Demand percentile - Accessibility percentile)
```

This is a screening metric. It does not by itself establish that an area is underserved.

---

## 6. Milestones

## Milestone 1 — Project Foundation

**Status: Completed**

- repository and project structure
- environment and requirements
- README and project plan
- Streamlit foundation

## Milestone 2 — Demand Data Ingestion

**Status: Completed**

- daily public transport ridership
- Rapid Rail OD data
- reusable ingestion pipeline
- processed Parquet/CSV outputs

## Milestone 3 — Demand Cleaning & Modelling

**Status: Completed**

- station-code extraction
- station summaries
- station-pair summaries
- monthly/service summaries
- dashboard-ready outputs

## Milestone 4 — Demand Dashboard MVP

**Status: Completed / superseded**

The initial dashboard proved the data pipeline and analytics worked.

It included:

- ridership overview
- service comparison
- OD explorer
- station insights

The project has since moved beyond the chart-first MVP.

## Milestone 5 — Public Deployment

**Status: Completed**

- GitHub repository published
- processed dashboard datasets committed
- Streamlit Community Cloud deployment
- live dashboard link added to README

Live app:

https://transitpulse-klang.streamlit.app/

## Milestone 6 — Accessibility & Geospatial Intelligence

**Status: Implemented — Version 1**

- official GTFS Static integration
- station coordinates
- route shapes
- station-to-line relationships
- station-density calculations
- direct rail reach
- Accessibility Score
- commuter location explorer
- network map
- demand vs accessibility analysis
- Demand–Access Gap

## Milestone 7 — True Underserved-Area Model

**Status: Next**

The next model should move beyond station-centric access and incorporate:

- population density
- employment/activity density
- pedestrian walking networks
- feeder-bus coverage
- service frequency
- operating hours
- socioeconomic/mobility-need indicators

Deliverable:

> A defensible area-level transit-gap model rather than a station-only accessibility proxy.

## Milestone 8 — Product Expansion

**Status: Future**

Potential additions:

- compare two locations
- suburb / postcode search
- actual walking routes to stations
- journey-time accessibility
- real-time operational layer
- automated scheduled data refresh
- SvelteKit portfolio case-study frontend

---

## 7. Success Criteria

TransitPulse should be considered successful when it can answer these questions clearly:

### For a commuter

- How close is rail?
- Which stations and lines are nearby?
- How much of the network can I reach directly?
- Is the location comparatively well connected?
- Where do people commonly travel from the nearest station?

### For an analyst/planner

- Which stations have the strongest observed demand?
- Which stations have strong or weak network access?
- Where does demand rank above accessibility?
- Which locations merit deeper accessibility investigation?
- What additional evidence is required before making a policy claim?

---

## 8. Methodological Guardrails

TransitPulse should not claim more than the current data supports.

Do not describe a location as a confirmed “transit desert” based only on the current model.

Current limitations include:

- station-centric rather than population-centric scoring
- straight-line catchments rather than pedestrian network distances
- no feeder-bus accessibility in the score
- no service-frequency weighting
- no travel-time isochrones
- no socioeconomic need layer

These limitations should remain visible in the app and documentation.

---

## 9. Portfolio Value

The project now demonstrates more than dashboard development:

- open-government data ingestion
- large OD dataset processing
- GTFS integration
- geospatial analysis
- accessibility modelling
- metric design
- demand/access comparison
- interactive mapping
- product-oriented analytics
- transparent methodology
- public deployment

The key portfolio story is:

> TransitPulse combines official Malaysian transport demand and GTFS network data to help users understand rail accessibility around a location and to identify where observed station demand may be stronger than relative network access.
