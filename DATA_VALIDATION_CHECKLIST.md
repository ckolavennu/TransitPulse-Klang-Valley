# TransitPulse Klang Valley — Data Validation Checklist

Use this checklist before pushing the project to GitHub or deploying the dashboard.

---

## 1. Pipeline Validation

Run:

```bash
python src/run_pipeline.py
```

Confirm that the command finishes without errors.

---

## 2. Raw Data Check

Check that these folders contain files:

```text
data/raw/
data/processed/
```

Expected raw data includes:

- daily public transport ridership file
- Rapid Rail OD ridership file or files

---

## 3. Processed Data Check

Expected processed outputs may include:

- daily ridership cleaned file
- monthly ridership summary
- service comparison summary
- Rapid Rail OD cleaned file
- station summary file
- station pair summary file

---

## 4. Dashboard Validation

Run:

```bash
streamlit run dashboard/app.py
```

Confirm these pages open without errors:

- Overview
- Service Comparison
- OD Explorer
- Station Insights
- Data Notes

---

## 5. KPI Logic Check

In the dashboard, validate the following manually:

### Total Trips

Should equal:

```text
sum of ridership for selected date range and selected services
```

### Average Daily Trips

Should approximately equal:

```text
total trips / number of selected days
```

### Services Selected

Should equal:

```text
number of services selected in the sidebar
```

### Top Service

Should equal:

```text
service with the highest total ridership in the selected date range
```

---

## 6. OD Data Logic Check

For OD Explorer:

- origin should not be empty
- destination should not be empty
- ridership should be numeric
- busiest station pair should be based on total ridership
- selected date filters should update the table and charts

---

## 7. Station Insights Logic Check

For Station Insights:

- outbound trips should be based on selected station as origin
- inbound trips should be based on selected station as destination
- top destinations should use selected station as origin
- top origins should use selected station as destination

---

## 8. Documentation Check

Before GitHub push, confirm that README.md includes:

- project description
- project objectives
- data sources
- local setup steps
- dashboard features
- limitations
- future improvements

---

## 9. GitHub Readiness Check

Before pushing, confirm that `.gitignore` excludes:

- `.venv/`
- `__pycache__/`
- `.streamlit/secrets.toml`
- temporary files
- large unnecessary files

For large datasets, decide whether to:

1. exclude raw data from GitHub and download it through the pipeline, or
2. include only small processed sample files.

Recommended: do not push very large raw data files.

---

## 10. Deployment Check

Before Streamlit deployment:

- requirements.txt is complete
- dashboard/app.py is the main entry file
- pipeline either downloads required data or processed data is included
- app works from a fresh clone
- no local absolute paths are used
