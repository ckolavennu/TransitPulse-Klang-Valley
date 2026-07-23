"""Run the basic TransitPulse data pipeline from download to summaries."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    "src/data_ingestion/download_data.py",
    "src/data_cleaning/clean_ridership.py",
    "src/data_cleaning/clean_od.py",
    "src/analysis/basic_insights.py",
]


def run_step(script_path: str) -> None:
    print(f"\n=== Running {script_path} ===")
    subprocess.run([sys.executable, script_path], cwd=PROJECT_ROOT, check=True)


def main() -> None:
    for step in STEPS:
        run_step(step)

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()
