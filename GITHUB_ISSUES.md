# Suggested GitHub Milestones and Issues

Use this file to create GitHub milestones and issues manually.

## Milestone 1: Project Setup

- [ ] Create repository structure
- [ ] Add README.md
- [ ] Add PROJECT_PLAN.md
- [ ] Add requirements.txt
- [ ] Add .gitignore
- [ ] Set up Python virtual environment
- [ ] Document initial data sources

## Milestone 2: Data Ingestion

- [ ] Download Daily Public Transport Ridership dataset
- [ ] Download Rapid Rail OD 2026 dataset
- [ ] Save raw files in `data/raw`
- [ ] Add reusable data source configuration
- [ ] Validate that files can be loaded with Python
- [ ] Document source links and update dates

## Milestone 3: Data Cleaning

- [ ] Clean daily ridership data
- [ ] Convert date columns to datetime
- [ ] Standardise service column names
- [ ] Clean Rapid Rail OD data
- [ ] Extract station codes and station names
- [ ] Validate ridership values
- [ ] Save processed files in `data/processed`

## Milestone 4: Exploratory Data Analysis

- [ ] Analyse total ridership trends
- [ ] Compare ridership by service
- [ ] Identify busiest station pairs
- [ ] Identify top origin stations
- [ ] Identify top destination stations
- [ ] Create monthly summary tables
- [ ] Write key findings

## Milestone 5: Dashboard MVP

- [ ] Create Streamlit dashboard layout
- [ ] Build Overview page
- [ ] Add KPI cards
- [ ] Add ridership trend charts
- [ ] Add service comparison charts
- [ ] Build OD Explorer page
- [ ] Add station-level filters
- [ ] Add station pair ranking table

## Milestone 6: Accessibility Map

- [ ] Load GTFS Static station data
- [ ] Extract station coordinates
- [ ] Build station map
- [ ] Add station demand markers
- [ ] Add catchment radius layer
- [ ] Define Transit Accessibility Score
- [ ] Add map page to dashboard

## Milestone 7: Deployment and Portfolio

- [ ] Deploy dashboard to Streamlit Community Cloud
- [ ] Add screenshots to README
- [ ] Write project methodology
- [ ] Add limitations section
- [ ] Add future improvements section
- [ ] Create portfolio case study page
- [ ] Link GitHub repository and live dashboard
