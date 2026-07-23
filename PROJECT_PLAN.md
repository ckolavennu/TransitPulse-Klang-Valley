# TransitPulse Klang Valley — Project Plan

## 1. Project Overview

TransitPulse Klang Valley is a public transport analytics dashboard focused on ridership trends and station-to-station travel demand in Klang Valley.

The project uses official open transport data from data.gov.my to analyse how public transport usage changes over time, which services are most used, and which Rapid Rail station pairs have the highest demand.

The long-term vision is to expand the project into a wider mobility intelligence dashboard that includes station accessibility, catchment areas, and potential underserved transit zones.

---

## 2. Problem Statement

Public transport data is available publicly, but it is not always easy for students, analysts, or general users to explore it interactively. Raw datasets can be large, especially origin-destination ridership data, and require cleaning, aggregation, and visualisation before meaningful insights can be extracted.

This project aims to solve that by creating a dashboard that helps users understand:

- overall public transport ridership trends
- service-level demand patterns
- busiest station pairs
- top origin and destination stations
- station-level travel flows

---

## 3. Project Scope

### Current Scope

The current MVP covers:

- daily public transport ridership
- service-level ridership comparison
- Rapid Rail origin-destination demand
- station-level demand summaries
- dashboard filters and visualisations

### Out of Scope for MVP

The following are not part of the current MVP:

- real-time delay detection
- route punctuality measurement
- train or bus cancellation analysis
- predictive modelling
- full GIS accessibility scoring
- mobile app development

These can be considered later once the base analytics layer is stable.

---

## 4. Main Datasets

### Daily Public Transport Ridership

Purpose:

- analyse ridership trends across services
- compare LRT, MRT, Monorail, bus, KTM, and other services
- identify long-term usage changes

Expected fields include:

- date
- service
- ridership

### Daily Origin-Destination Ridership: Rapid Rail Klang Valley

Purpose:

- analyse station-to-station demand
- identify busiest origin-destination pairs
- rank origin and destination stations
- understand key travel corridors

Expected fields include:

- date
- origin
- destination
- ridership

---

## 5. Milestones

## Milestone 1: Project Setup

Status: Completed

Tasks:

- Create project folder structure
- Add README.md
- Add PROJECT_PLAN.md
- Add requirements.txt
- Add .gitignore
- Set up Python virtual environment
- Install dependencies

Deliverable:

- Clean local project structure ready for development

---

## Milestone 2: Data Ingestion

Status: Completed / Working MVP

Tasks:

- Download daily public transport ridership data
- Download Rapid Rail OD ridership data
- Store raw files in data/raw
- Create reusable ingestion script
- Create main pipeline runner

Deliverable:

- Raw datasets available locally

---

## Milestone 3: Data Cleaning and Summary Tables

Status: Completed / Working MVP

Tasks:

- Clean date fields
- Standardise service names
- Validate ridership numeric fields
- Create monthly ridership summaries
- Create service comparison summaries
- Create station summary tables
- Create station-pair summary tables

Deliverable:

- Processed dashboard-ready files in data/processed

---

## Milestone 4: Dashboard MVP

Status: Completed

Tasks:

- Build Streamlit dashboard layout
- Add Overview page
- Add Service Comparison page
- Add OD Explorer page
- Add Station Insights page
- Add Data Notes page
- Add sidebar filters
- Add KPI cards
- Add Plotly visualisations

Deliverable:

- Working local Streamlit dashboard

---

## Milestone 5: Documentation and GitHub Preparation

Status: In Progress

Tasks:

- Improve README.md
- Add project purpose and methodology
- Add data source descriptions
- Add limitations section
- Add setup instructions
- Add screenshots
- Push project to GitHub

Deliverable:

- GitHub-ready project repository

---

## Milestone 6: Deployment

Status: Not Started

Tasks:

- Push final files to GitHub
- Deploy on Streamlit Community Cloud
- Test deployed dashboard
- Add live dashboard link to README
- Add dashboard link to portfolio website

Deliverable:

- Public dashboard link

---

## Milestone 7: Accessibility and Mapping Layer

Status: Future Enhancement

Tasks:

- Load GTFS Static station and stop data
- Extract station coordinates
- Create interactive station map
- Add station demand markers
- Add catchment radius layer
- Define Transit Accessibility Score
- Identify potential low-access areas

Deliverable:

- Map-based accessibility dashboard page

---

## 6. Suggested Dashboard Pages

### Page 1: Overview

Purpose:

- give a quick summary of ridership activity

Includes:

- total trips
- average daily trips
- services selected
- top service
- monthly ridership trend
- top services by ridership
- service share chart

### Page 2: Service Comparison

Purpose:

- compare transport services over time

Includes:

- service-level trends
- ranking by total trips
- share of ridership
- growth or decline analysis

### Page 3: OD Explorer

Purpose:

- explore Rapid Rail station-to-station travel demand

Includes:

- busiest station pairs
- origin-destination search
- top OD table
- filtered download option

### Page 4: Station Insights

Purpose:

- understand individual station demand

Includes:

- outbound trips
- inbound trips
- top destinations from selected station
- top origins to selected station

### Page 5: Data Notes

Purpose:

- explain methodology, data interpretation, and limitations

Includes:

- data source explanation
- ridership meaning
- current project limitations
- future enhancements

---

## 7. Success Criteria

The project will be considered successful when:

- the pipeline runs without errors
- processed data files are generated correctly
- the dashboard opens locally
- all dashboard pages work
- filters update charts correctly
- README clearly explains the project
- the project is pushed to GitHub
- the dashboard is deployed publicly
- the project is added to the portfolio website

---

## 8. Future Enhancements

Potential future improvements:

- GTFS Static station map
- station catchment analysis
- Transit Accessibility Score
- real-time vehicle position layer
- automated data refresh using GitHub Actions
- historical service recovery analysis after disruption periods
- dashboard design polish
- SvelteKit portfolio case study page

---

## 9. Portfolio Value

This project demonstrates:

- public open data usage
- data ingestion
- data cleaning
- large dataset handling
- origin-destination analysis
- time-series analysis
- dashboard development
- visual storytelling
- practical urban mobility analytics

It is designed to be stronger than a generic dataset visualisation project because it uses real Malaysian public transport data and answers a practical mobility-related problem.
