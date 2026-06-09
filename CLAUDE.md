# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Single-file Streamlit app (`app.py`) for ISO 9001:2015 audit management (SGC — Sistema de Gestión de Calidad). The app is written in Spanish and uses Google Sheets as its live backend database via `streamlit-gsheets-connection`.

## Commands

```bash
# Create virtual environment (first time)
python -m venv venv
source venv/Scripts/activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the app (runs on http://localhost:8501)
streamlit run app.py
```

## Configuration

Google Sheets credentials live in `.streamlit/secrets.toml` (copy from `.streamlit/secrets.example.toml`):

```toml
[connections.gsheets]
spreadsheet = "<Google Sheets URL>"

[GOOGLE_SERVICE_ACCOUNT_INFO]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
# ... (remaining OAuth fields)
```

The app loads data via the `load_gsheets_data()` helper in `utils.py`, which uses gspread + service account credentials. If credentials are missing or invalid, the app calls `st.stop()`.

## Google Sheets Schema

Two worksheets are read at startup with `ttl=0` (no caching, always fresh):

**`Matriz`** — Audit findings plan:
`id`, `fecha`, `proceso_auditado`, `auditor_responsable`, `requisito_iso`, `requisito_especifico`, `requisito_interno_legal`, `tipo_hallazgo`, `cumplimiento`, `evidencia_objetiva`, `observaciones`

**`SAC_OM`** — Corrective actions / improvement opportunities:
`id`, `fecha`, `proceso_auditado`, `auditor_responsable`, `requisito_iso`, `tipo_plan`, `codigo`, `estatus_plan`, `estatus_la_eficacia`, `observaciones`

## Utilities Module

**`utils.py`** contains:
- **Validation**: `validate_required()`, `validate_date()`, `safe_int_convert()` — raises `ValidationError` on invalid input
- **Google Sheets I/O**: `load_gsheets_data()` loads both worksheets with retry logic; `update_gsheets()` writes changes back
- **Compute helpers**: `compute_conformidad_stats()`, `compute_process_stats()`, `compute_auditor_stats()`, `compute_conformidad_trend()`, etc. — calculate KPIs and chart data

All computation functions are cached at the session/module level to avoid redundant recalculation.

## App Architecture

All logic lives in `app.py` as a single-module Streamlit script. Navigation is driven by `st.sidebar.radio` selecting among four modules:

- **Dashboard de Dirección** — KPI cards + Plotly charts (line, bar, pie, distribution) computed from `df_matriz` and `df_sac` via utility functions.
- **Matriz de Hallazgos** — Two tabs: (1) filter and update existing rows by process, (2) insert new rows. Calls `update_gsheets(worksheet="Matriz", data=df_matriz)` and `st.rerun()`.
- **Seguimiento SAC / OM** — Two tabs: (1) list and update plans with status/efficacy filtering, (2) register new plan. Calls `update_gsheets(worksheet="SAC_OM", data=df_sac)` and `st.rerun()`.
- **Exportar Respaldo** — Exports both dataframes to an in-memory Excel file (`openpyxl`) and optionally generates a PDF report (`reportlab`). Provides a download button.

**Data flow**: Load sheets (ttl=0, always fresh) → transform/validate user input → modify DataFrame in memory → `update_gsheets()` pushes the full DataFrame back → `st.rerun()` refreshes the UI with live data.
