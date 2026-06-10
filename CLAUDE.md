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

## User Experience & Interface Design

### Visual Design & Aesthetics

The app implements a professional, institutional design system:

- **Color Palette**: Blue tonalities only (light blue `#E8F1F9` to dark blue `#1A3A52`), grays for text and borders
- **Typography**: Roboto font throughout for consistency
- **Layout**: Symmetric, ordered, grid-based structure with proper spacing
- **Styling**: Native Streamlit components (no complex HTML/CSS) for reliability and maintainability
- **Decoration**: Zero emojis or playful elements — purely functional and clean

All modules follow this design consistently, including Dashboard, ENTRADA, SEGUIMIENTO, HORAS, and EXPORTAR.

### Interaction Features

#### Save Confirmations

All data modification operations require user confirmation before persisting to Google Sheets:

- **ENTRADA**: Confirm when editing or registering hallazgos
- **SEGUIMIENTO**: Confirm when updating plan status or registering new actions
- **HORAS**: Confirm when registering auditor participation

Implementation: Session state tracks confirmation dialogs. User sees operation details before committing.

#### Loading Indicators

Google Sheets synchronization operations show visual feedback via `st.spinner()`:

- "Guardando cambios en Google Sheets..." — during edit operations
- "Registrando hallazgo en Google Sheets..." — during new record creation
- "Actualizando plan en Google Sheets..." — during status updates
- "Registrando participación en Google Sheets..." — during participation logging

This improves perceived responsiveness and prevents user anxiety during network operations.

#### Robust Input Validation

Each module validates user input before confirmation:

**ENTRADA**:
- Required field checks (proceso, auditor, requisito específico)
- Conditional validation: if `cumplimiento == "No Conforme"`, require evidencia_objetiva

**SEGUIMIENTO**:
- Required field checks (all fields mandatory)
- Código uniqueness check (case-insensitive)
- Código minimum length validation (≥3 characters)
- Multiple errors collected and displayed together

**HORAS**:
- Required field checks (auditor, process)
- Hours range validation (0.1 ≤ horas ≤ 24.0)
- Date validation: no future dates
- Reasonable date range: no more than 1 year in past
- Multiple validation errors shown together

Validation errors prevent form submission; users must correct all issues before confirmation.

#### Search & Filtering

All data-viewing modules support text search and filtering:

**ENTRADA (Historial)**: 
- Search by auditor, process, or requirement (case-insensitive)
- Results counter showing matches
- Collapsible search section

**SEGUIMIENTO (Acciones Abiertas)**:
- Search by código, process, or auditor (case-insensitive)
- Status filter dropdown: Todos, Abierto, Cerrado
- Results counter
- Graceful empty state messaging

**HORAS (Reporte)**:
- Search by auditor name (case-insensitive)
- Dynamic table filtering
- Chart adapts to filtered data
- Full dataset available for export (unfiltered)

Search is case-insensitive and updates results in real-time as users type.

### Status Display Logic

Empty compliance fields (`cumplimiento == null or empty`) now correctly display as "Pendiente" instead of "No Conforme". This reflects the actual state of unclassified findings and prevents false negatives in reporting.

Implementation: Priority-based status determination checks empty/null first, then matches specific values.

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

## Recent Improvements (June 2026)

### UI/UX Enhancements

**Institutional Design System**:
- Implemented professional blue-gray color palette across all modules
- Removed all decorative elements (emojis) for cleaner, institutional appearance
- Consistent typography (Roboto) and symmetric layouts
- Improved form grouping and visual hierarchy

**Data Integrity & User Safety**:
- Added confirmation dialogs before all save operations (prevents accidental data loss)
- Implemented loading spinners during Google Sheets synchronization
- Fixed status display bug where empty `cumplimiento` fields showed as "No Conforme" (now shows "Pendiente")

**User Feedback & Discoverability**:
- Added comprehensive input validation with specific error messages
- Implemented search functionality in SEGUIMIENTO and HORAS modules (matching ENTRADA)
- Added results counters and empty state messaging for better feedback
- Improved form error handling to show multiple validation issues at once

**Code Quality**:
- Simplified overly complex HTML/CSS styling to use native Streamlit components for better reliability
- Standardized error message formatting across all modules (removed emoji prefixes)
- Consistent validation patterns across ENTRADA, SEGUIMIENTO, HORAS modules

### Technical Details

All changes maintain backward compatibility with existing Google Sheets data and workflows. No schema changes required. Session state management improved for modal dialogs and search filtering.

## Additional Documentation

- **Setup & Verification**: See `PENDING_TASKS.md` for manual Google Sheets verification steps and troubleshooting
- **Implementation Details**: See `docs/` for specification, design, and implementation plans
- **Sheet Schema Details**: See "Google Sheets Schema" section above for column names and data types
