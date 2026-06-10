# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Single-file Streamlit app (`app.py`) for ISO 9001:2015 audit management (SGC — Sistema de Gestión de Calidad). The app is written in Spanish and uses Google Sheets as its live backend database via `streamlit-gsheets-connection`.

## Commands

```bash
# Create virtual environment (first time)
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate on macOS/Linux
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Run the app (runs on http://localhost:8501)
streamlit run app.py
```

### First-Time Setup

After installing dependencies, initialize the HORAS module Google Sheets:

```bash
# Create/update the three HORAS sheets in Google Sheets
python setup_horas_sheets.py

# Or recreate from scratch (destructive)
python setup_horas_sheets.py --force
```

This automates the creation of:
- `Horas_Base_2011_2025` — historical baseline with 23 auditors
- `Participaciones_2026` — transaction log for auditor participation
- `Reporte_Horas_2026` — aggregated report with auto-updating formulas

See `PENDING_TASKS.md` for manual verification steps or troubleshooting.

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

All computation functions are cached at the session/module level via `@st.cache_data` to avoid redundant recalculation. This means KPI cards and chart data refresh only when Google Sheets data changes (not on every page render).

## App Architecture

All logic lives in `app.py` as a single-module Streamlit script. Navigation is driven by `st.sidebar.radio` selecting among four modules:

### Modules Overview

- **Dashboard de Dirección** — KPI cards + Plotly charts (line, bar, pie, distribution) computed from `df_matriz` and `df_sac` via utility functions.
- **Matriz de Hallazgos** — Two tabs: (1) filter and update existing rows by process, (2) insert new rows. Calls `update_gsheets(worksheet="Matriz", data=df_matriz)` and `st.rerun()`.
- **Registro de Horas (HORAS)** — Two tabs: (1) register an auditor participation (writes via `append_participacion()`), (2) view the aggregated hours report with KPIs, stacked bar chart and Excel export. Data loads lazily only when this module is selected.
- **Seguimiento SAC / OM** — Two tabs: (1) list and update plans with status/efficacy filtering, (2) register new plan. Calls `update_gsheets(worksheet="SAC_OM", data=df_sac)` and `st.rerun()`.
- **Exportar Respaldo** — Exports both dataframes to an in-memory Excel file (`openpyxl`) and optionally generates a PDF report (`reportlab`). Provides a download button.

### Data Flow & Session Management

1. **Load phase**: Load sheets (ttl=0, always fresh) from Google Sheets via `load_gsheets_data()` and `load_horas_data()` (lazy)
2. **Transform phase**: Validate user input → modify DataFrame in memory
3. **Persist phase**: Call `update_gsheets()` to write back full DataFrame → `st.rerun()` refreshes UI
4. **Caching**: Computation functions use `@st.cache_data` to avoid recalculating KPIs and charts on every render
5. **Session state**: Streamlit session tracks filter selections, form inputs, and lazy-load state for the HORAS module

### Independent Data Workflows

The three main worksheets operate independently:

- **Matriz** — Audit findings: audit scope, requirements, compliance status, objective evidence
- **SAC_OM** — Corrective/preventive actions: ISO requirement, action code, status, efficacy tracking
- **HORAS** — Auditor hours: participation log, role, hours per audit type (OB/AF/AD/AL), annual report

## Troubleshooting

### Google Sheets Credentials Issues

**Symptom**: "No spreadsheet URL in secrets" or "No GOOGLE_SERVICE_ACCOUNT_INFO in secrets"

1. Verify `.streamlit/secrets.toml` exists (copied from `.streamlit/secrets.example.toml`)
2. Check that `connections.gsheets.spreadsheet` is set to the correct Google Sheets URL
3. Verify `GOOGLE_SERVICE_ACCOUNT_INFO` contains all OAuth fields (type, project_id, private_key, client_email, etc.)
4. Run `streamlit secrets show` to confirm secrets are loaded
5. Restart Streamlit: `streamlit run app.py`

### Google Sheets Write Failures

**Symptom**: Updates to Matriz or SAC_OM don't appear after clicking save

1. Verify the service account email (in `GOOGLE_SERVICE_ACCOUNT_INFO.client_email`) has editor permission on the Google Sheet
2. Check if the Google Sheets API quota has been exceeded (rate limit: 60 requests/minute per user)
3. Check the browser console for errors (F12 → Console tab)
4. Try `st.rerun()` manually to refresh data
5. Verify the worksheet name matches exactly: "Matriz", "SAC_OM", "Horas_Base_2011_2025", "Participaciones_2026", "Reporte_Horas_2026"

### HORAS Module Not Loading

**Symptom**: "Registro de Horas" tab shows error or blank screen

1. Verify Google Sheets sheets exist: run `python setup_horas_sheets.py` (or `--force` to recreate)
2. Check that all three HORAS sheets are present: `Horas_Base_2011_2025`, `Participaciones_2026`, `Reporte_Horas_2026`
3. Verify `PROCESOS_SGC` and `ROLES_AUDITOR` constants in `utils.py` match Google Sheets dropdown validations
4. Check for missing auditor names: verify all 23 auditors from Horas_Base_2011_2025 are present

### Streamlit Port Already in Use

**Symptom**: "Streamlit requires raw socket access, which is not available in this environment"

1. Check what process is using port 8501: `netstat -ano | findstr :8501` (Windows PowerShell)
2. Kill the process or run on a different port: `streamlit run app.py --server.port 8502`

### Chart/Dashboard Rendering Issues

**Symptom**: Plotly charts don't render or show as blank

1. Clear Streamlit cache: `streamlit cache clear`
2. Restart the app: stop with Ctrl+C and run `streamlit run app.py` again
3. Check browser console for JavaScript errors (F12 → Console)
4. Verify `compute_*` functions in `utils.py` return data with correct column names

## Development Utilities

The repo includes utility scripts for capturing app screenshots (not part of core app):
- `capture_screenshot.py` — Screenshot capture utility
- `capture_web_screenshot.py` — Web-based screenshot utility
- `take_screenshot.py` — Additional screenshot helper

These are development/documentation tools and not required for running the app.

## Additional Documentation

- **Setup & Verification**: See `PENDING_TASKS.md` for manual Google Sheets verification steps and troubleshooting
- **Implementation Details**: See `docs/` for specification, design, and implementation plans
- **Sheet Schema Details**: See "Google Sheets Schema" section above for column names and data types
