# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Single-file Streamlit app (`app.py`) for ISO 9001:2015 audit management (SGC — Sistema de Gestión de Calidad). The app is written in Spanish and uses Google Sheets as its live backend database via `streamlit-gsheets-connection`.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Configuration

Google Sheets credentials live in `.streamlit/secrets.toml`:

```toml
[connections.gsheets]
spreadsheet = "<Google Sheets URL>"
```

The connection is established at startup with `st.connection("gsheets", type=GSheetsConnection)`. If this fails, the app calls `st.stop()`.

## Google Sheets Schema

Two worksheets are read at startup with `ttl=0` (no caching, always fresh):

**`Matriz`** — Audit findings plan:
`id`, `fecha`, `proceso_auditado`, `auditor_responsable`, `requisito_iso`, `requisito_especifico`, `requisito_interno_legal`, `tipo_hallazgo`, `cumplimiento`, `evidencia_objetiva`, `observaciones`

**`SAC_OM`** — Corrective actions / improvement opportunities:
`id`, `fecha`, `proceso_auditado`, `auditor_responsable`, `requisito_iso`, `tipo_plan`, `codigo`, `estatus_plan`, `estatus_la_eficacia`, `observaciones`

## App Architecture

All logic lives in `app.py` as a single-module Streamlit script. Navigation is driven by `st.sidebar.radio` selecting among four modules:

- **Dashboard de Dirección** — KPI cards + Plotly charts computed from `df_matriz` and `df_sac`.
- **Matriz de Hallazgos** — Two tabs: (1) evaluate/update existing rows by process, (2) insert new rows. Both write back via `conn.update(worksheet="Matriz", data=df_matriz)`.
- **Seguimiento SAC / OM** — Two tabs: (1) list all plans and update estatus/eficacia, (2) register a new plan. Writes back via `conn.update(worksheet="SAC_OM", data=df_sac)`.
- **Exportar Respaldo** — Writes both dataframes to an in-memory Excel file (`io.BytesIO` + `openpyxl`) and exposes a download button.

CRUD pattern: modify the in-memory DataFrame, call `conn.update(...)` with the full DataFrame, then `st.rerun()` to refresh from the live sheet.
