# Quick Start

Run these commands from the project folder.

## 1. Create virtual environment

```bash
python -m venv .venv
```

## 2. Activate virtual environment

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Mac/Linux:

```bash
source .venv/bin/activate
```

## 3. Install packages

```bash
pip install -r requirements.txt
```

## 4. Run full pipeline

```bash
python src/run_pipeline.py
```

## 5. Start dashboard

```bash
streamlit run dashboard/app.py
```
