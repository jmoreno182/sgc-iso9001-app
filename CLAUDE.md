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

Three additional worksheets support the HORAS module (created by `setup_horas_sheets.py`):

**`Horas_Base_2011_2025`** — Read-only historical baseline (23 auditors):
`Auditor`, `OB_Prev`, `AF_Prev`, `AD_Prev`, `AL_Prev`, `Notas`. Values come from the "Total de Horas Acumuladas" columns of the PDF `SGC-F-AS-024-2` (cumulative through Dec 2025).

**`Participaciones_2026`** — Transaction log, one row per auditor participation:
`ID`, `Fecha`, `Período`, `Proceso`, `Auditor`, `Rol`, `Horas`, `Observaciones`. Columns `ID` and `Período` are sheet formulas (rows 2-1000); the app writes only `Fecha` (col B) and `Proceso`→`Observaciones` (cols D-H) via `append_participacion()`. Dropdown validations: Proceso (15 siglas), Auditor (range from Horas_Base), Rol (OB/AF/AD/AL), Horas (0 < x ≤ 24).

**`Reporte_Horas_2026`** — Read-only aggregated report:
`Auditor`, `OB_2026`..`AL_2026` (SUMIFS over Participaciones), `OB_Prev`..`AL_Prev` (VLOOKUP to base), `OB_Total`..`AL_Total` (sum), `Total_Auditorías` (COUNTIF). Auto-updates when participations are added.

## Utilities Module

**`utils.py`** contains:
- **Validation**: `validate_required()`, `validate_date()`, `safe_int_convert()` — raises `ValidationError` on invalid input
- **Google Sheets I/O**: `load_gsheets_data()` loads both worksheets with retry logic; `update_gsheets()` writes changes back; `load_horas_data()` loads the three HORAS sheets; `append_participacion()` appends a single participation row (cols B, D-H only)
- **Constants**: `PROCESOS_SGC`, `ROLES_AUDITOR`, `ROLES_DESCRIPCION` for the HORAS module
- **Compute helpers**: `compute_conformidad_stats()`, `compute_process_stats()`, `compute_auditor_stats()`, `compute_conformidad_trend()`, etc. — calculate KPIs and chart data

All computation functions are cached at the session/module level to avoid redundant recalculation.

## App Architecture

All logic lives in `app.py` as a single-module Streamlit script. Navigation is driven by `st.sidebar.radio` selecting among four modules:

- **Dashboard de Dirección** — KPI cards + Plotly charts (line, bar, pie, distribution) computed from `df_matriz` and `df_sac` via utility functions.
- **Matriz de Hallazgos** — Two tabs: (1) filter and update existing rows by process, (2) insert new rows. Calls `update_gsheets(worksheet="Matriz", data=df_matriz)` and `st.rerun()`.
- **Registro de Horas (HORAS)** — Two tabs: (1) register an auditor participation (writes via `append_participacion()`), (2) view the aggregated hours report with KPIs, stacked bar chart and Excel export. Data loads lazily only when this module is selected.
- **Seguimiento SAC / OM** — Two tabs: (1) list and update plans with status/efficacy filtering, (2) register new plan. Calls `update_gsheets(worksheet="SAC_OM", data=df_sac)` and `st.rerun()`.
- **Exportar Respaldo** — Exports both dataframes to an in-memory Excel file (`openpyxl`) and optionally generates a PDF report (`reportlab`). Provides a download button.

**Data flow**: Load sheets (ttl=0, always fresh) → transform/validate user input → modify DataFrame in memory → `update_gsheets()` pushes the full DataFrame back → `st.rerun()` refreshes the UI with live data.
