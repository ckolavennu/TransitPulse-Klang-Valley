# Data Folder

This folder stores raw, processed, and external data files.

## Folders

- `raw/`: Original downloaded files from official data sources.
- `processed/`: Cleaned datasets used by analysis scripts and the dashboard.
- `external/`: Supporting files such as station locations, boundaries, or GTFS extracts.

Large datasets should not normally be committed to GitHub. The ingestion scripts should be used to download or regenerate them.
