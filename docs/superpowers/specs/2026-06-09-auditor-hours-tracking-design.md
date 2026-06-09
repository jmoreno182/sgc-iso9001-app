# Auditor Hours Tracking Module - Design Specification

**Status:** Design Complete  
**Date:** 2026-06-09  
**Author:** Claude Code  
**Project:** ISO 9001:2015 Audit Management System (SGC)

---

## 1. Overview

This specification defines the complete design for a new **Auditor Hours Tracking Module** (HORAS) to be integrated into the existing Streamlit audit app. The module automates the tracking of auditor participation hours across multiple audits in 2026, replacing manual PDF-based tracking from 2025.

**Key Goals:**
- Normalize hour tracking data in Google Sheets (one row per auditor participation)
- Maintain historical hour accumulation from 2011-2025
- Auto-generate audit hour reports in ISO 9001:2015 format
- Provide Streamlit UI for easy data entry and report viewing
- Track cumulative hours, roles, and audit participation counts per auditor

---

## 2. Business Context

### 2.1 Current State (2025)
- Hours tracked manually in PDF form: "SGC-F-AS-024-2 Registro de horas de Auditoria"
- One PDF per audit period
- Manual calculations for cumulative hours
- No automated reporting or data aggregation

### 2.2 Target State (2026)
- Three audits scheduled in June 2026 (multiple processes across different dates)
- 15 auditors in the team (22 historical from PDF, 1 new: Sara Rabelo)
- Automated hour tracking with Google Sheets as single source of truth
- Real-time report generation matching PDF format
- Streamlit UI for data entry and queries

### 2.3 Audit Team Structure

**Roles:**
- **OB (Observador)**: Observer - Sara Rabelo (new), + others from historical data
- **AF (Auditor en Formación)**: Auditor in Training - Various team members
- **AD (Auditor Interno)**: Internal Auditor - Marlene Andrea, Yraima Rodríguez, Angelo Mazzarino
- **AL (Auditor Líder)**: Lead Auditor - Yolmarig Montilla (for 2026)

**Audit Schedule 2026:**
```
Period 1: 4-6 June 2026   (5 processes: EV, FP, TR, DR)
Period 2: 8-12 June 2026  (8 processes: AC, DD, AA, GI, GM, PB, PP, CO, AS)
Period 3: 15+ June 2026   (2 processes: GP, DI)
```

Responsible Auditors: Marlene Andrea, Angelo Mazzarino, Yraima Rodríguez

---

## 3. Google Sheets Architecture

### 3.1 Sheet 1: "Horas_Base_2011_2025" (Historical Base)

**Purpose:** Store cumulative hours from 2011-2025 (the baseline for 2026 calculations)

**Columns:**
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| Auditor | Text | Auditor full name | Marlene Andrea |
| OB_Prev | Number | Observador hours accumulated 2011-2025 | 12.2 |
| AF_Prev | Number | Auditor en Formación hours 2011-2025 | 42.1 |
| AD_Prev | Number | Auditor Interno hours 2011-2025 | 60.1 |
| AL_Prev | Number | Auditor Líder hours 2011-2025 | 32.6 |
| Notas | Text | Source/notes | Extracted from 2025 PDF |

**Data:**
- 22 auditors extracted from 2025 PDF (final column: "Total de Horas de Auditoría Acumuladas")
- Sara Rabelo added with 0.0 across all role columns (new auditor)
- Values are read-only (no modifications during 2026)

**Data Loading:**
Extract from PDF "SGC-F-AS-024-2 Registro de horas de Auditoria" (page 1):
- Column: "Horas Acumuladas Previas" → OB_Prev, AF_Prev, AD_Prev, AL_Prev
- One row per auditor

---

### 3.2 Sheet 2: "Participaciones_2026" (Transaction Log - Normalized)

**Purpose:** Normalized data entry point. One row = one auditor's participation in one audit period.

**Columns:**
| Column | Type | Validation | Description | Example |
|--------|------|-----------|-------------|---------|
| ID | Number | Auto-increment | Unique participation record | 1, 2, 3... |
| Fecha | Date | Required | Audit date | 4/6/2026 |
| Período | Text | Calculated | Period grouping (visual only) | Junio 1 (04-06) |
| Proceso | Text | Dropdown (15 options) | Process code audited | EV, FP, TR, etc. |
| Auditor | Text | Dropdown (23 names) | Auditor name | Marlene Andrea |
| Rol | Text | Dropdown (OB/AF/AD/AL) | Role during audit | AL |
| Horas | Number | > 0, decimal allowed | Hours worked | 10.0, 9.2, 8.5 |
| Observaciones | Text | Optional | Notes (audit type, etc.) | Auditoría Interna |

**Data Constraints:**
- `Fecha`: Only dates matching scheduled audits (4, 5, 8, 9, 10, 11, 12, 15 June 2026)
- `Proceso`: 15 valid codes (EV, FP, TR, DR, AC, DD, AA, GI, GM, PB, PP, CO, AS, GP, DI)
- `Auditor`: 23 auditors from team (Marlene, Yraima, Angelo, Yolmarig, Sara, + 18 others)
- `Rol`: Must match auditor's typical role (validation at entry time)
- `Horas`: Decimal, between 1.0 and 24.0

**Calculated Field:**
```
Período = IF(Fecha <= 6, "Junio 1 (04-06)", IF(Fecha <= 12, "Junio 2 (08-12)", "Junio 3 (15+)"))
```

**Example Data:**
```
ID | Fecha | Período | Proceso | Auditor | Rol | Horas | Observaciones
1  | 4/6/2026 | Junio 1 (04-06) | EV | Marlene Andrea | AL | 10.0 | Auditoría Interna
2  | 5/6/2026 | Junio 1 (04-06) | FP | Angelo Mazzarino | AD | 9.2 | -
3  | 5/6/2026 | Junio 1 (04-06) | TR | Yraima Rodríguez | AD | 8.5 | -
...
```

---

### 3.3 Sheet 3: "Reporte_Horas_2026" (Aggregated Report Output)

**Purpose:** Auto-generated report matching PDF format from 2025. Read-only output sheet (formulas only).

**Columns:**
| Column | Type | Formula | Description |
|--------|------|---------|-------------|
| Auditor | Text | - | Auditor name (list from team) |
| OB_2026 | Number | SUMIFS | Sum OB hours from Participaciones_2026 |
| AF_2026 | Number | SUMIFS | Sum AF hours from Participaciones_2026 |
| AD_2026 | Number | SUMIFS | Sum AD hours from Participaciones_2026 |
| AL_2026 | Number | SUMIFS | Sum AL hours from Participaciones_2026 |
| OB_Prev | Number | VLOOKUP | OB accumulation from Horas_Base_2011_2025 |
| AF_Prev | Number | VLOOKUP | AF accumulation from Horas_Base_2011_2025 |
| AD_Prev | Number | VLOOKUP | AD accumulation from Horas_Base_2011_2025 |
| AL_Prev | Number | VLOOKUP | AL accumulation from Horas_Base_2011_2025 |
| OB_Total | Number | =OB_2026+OB_Prev | Cumulative OB hours (2011-2026) |
| AF_Total | Number | =AF_2026+AF_Prev | Cumulative AF hours (2011-2026) |
| AD_Total | Number | =AD_2026+AD_Prev | Cumulative AD hours (2011-2026) |
| AL_Total | Number | =AL_2026+AL_Prev | Cumulative AL hours (2011-2026) |
| Total_Auditorías | Number | COUNTIF | Count of audit participations |

**Key Formulas:**

**OB_2026 (and similar for AF, AD, AL):**
```excel
=SUMIFS(
  Participaciones_2026!$G:$G,           # Sum hours column
  Participaciones_2026!$E:$E, A2,       # Where Auditor = this row
  Participaciones_2026!$F:$F, "OB"      # And Rol = OB
)
```

**OB_Prev (and similar for AF, AD, AL):**
```excel
=VLOOKUP(
  A2,                                    # Look up auditor name
  Horas_Base_2011_2025!$A:$B, 2,        # In historical base
  FALSE                                  # Exact match
)
```
(Column B for OB_Prev, adjust to C for AF_Prev, D for AD_Prev, E for AL_Prev)

**OB_Total (and similar for AF, AD, AL):**
```excel
=B2+F2   # 2026 hours + Previous hours
```

**Total_Auditorías:**
```excel
=COUNTIF(Participaciones_2026!$E:$E, A2)
```

**Example Output:**
```
Auditor | OB_2026 | AF_2026 | AD_2026 | AL_2026 | OB_Prev | AF_Prev | AD_Prev | AL_Prev | OB_Total | AF_Total | AD_Total | AL_Total | Total_Auditorías
Marlene Andrea | - | - | 10.0 | 10.0 | 12.2 | 42.1 | 60.1 | 32.6 | 12.2 | 42.1 | 70.1 | 42.6 | 19
Yraima Rodríguez | - | - | 32.5 | 29.0 | 7.3 | 44.5 | 124.6 | 6.0 | 7.3 | 44.5 | 157.1 | 35.0 | 21
Angelo Mazzarino | - | - | 18.2 | - | 15.0 | 8.0 | 51.9 | 0.0 | 15.0 | 8.0 | 70.1 | 0.0 | 8
Sara Rabelo | 4.0 | - | - | - | 0.0 | 0.0 | 0.0 | 0.0 | 4.0 | 0.0 | 0.0 | 0.0 | 1
```

---

## 4. Data Flow & Lifecycle

### 4.1 Annual Cycle

**Year 2026:**
```
Horas_2026 + Horas_Acumuladas_Previas_2011_2025 = Total_Acumulado_2026
```

**Year 2027 (future):**
```
Horas_2027 + Horas_Acumuladas_Previas_2011_2026 = Total_Acumulado_2027
```

Where `Horas_Acumuladas_Previas_2011_2026` = `Total_Acumulado_2026` (rolled forward)

### 4.2 Data Entry Flow

1. **User selects period** (Junio 1, Junio 2, Junio 3)
2. **User adds multiple participations** (Auditor | Rol | Horas) in one form
3. **User clicks "Guardar Participaciones"**
4. **App validates** all entries (auditor exists, rol valid, horas > 0)
5. **App writes to Participaciones_2026** (Google Sheets)
6. **Formulas in Reporte_Horas_2026** auto-update
7. **Report is immediately available** for viewing

### 4.3 Synchronization

- **Read:** Participaciones_2026 (check for existing data)
- **Write:** Participaciones_2026 (new participation records)
- **Read:** Horas_Base_2011_2025 (for "Prev" columns)
- **Read (formulas only):** Reporte_Horas_2026 (no direct app writes)

All Google Sheets operations use `streamlit-gsheets-connection` with `ttl=0` (no caching).

---

## 5. Streamlit Integration

### 5.1 New Module: HORAS

Location in navigation: New button in top nav (alongside ENTRADA, SEGUIMIENTO, ANÁLISIS)

```
Navigation: [ENTRADA] [SEGUIMIENTO] [ANÁLISIS] [HORAS]
```

### 5.2 Module Structure

**Tab 1: "Registrar Horas"**

Purpose: Data entry interface for audit participations

Layout:
```
┌─────────────────────────────────────┐
│ Registrar Horas de Auditoría        │
├─────────────────────────────────────┤
│ Seleccionar Período: [Dropdown]     │
│  - Junio 1 (4-6)                    │
│  - Junio 2 (8-12)                   │
│  - Junio 3 (15+)                    │
├─────────────────────────────────────┤
│ Agregar Participaciones:            │
├─────────────────────────────────────┤
│ [Auditor] [Rol] [Horas] [Quitar]   │
│ [Auditor] [Rol] [Horas] [Quitar]   │
│ [Auditor] [Rol] [Horas] [Quitar]   │
│                                     │
│ [+ Agregar otra fila]               │
├─────────────────────────────────────┤
│ [Guardar Participaciones] [Limpiar] │
└─────────────────────────────────────┘
```

**Interaction:**
- Period selector (radio or selectbox)
- Dynamic form with multiple rows:
  - Auditor: Dropdown (23 names from team)
  - Rol: Dropdown (OB, AF, AD, AL)
  - Horas: Number input (decimal, > 0)
  - Remove button per row
- "Add another row" button (append empty row)
- Validation on submit:
  - All rows complete (no empty cells)
  - Horas > 0
  - No duplicate (auditor + período + rol)
- Success message with participation count
- Sync to Google Sheets (Participaciones_2026)

---

**Tab 2: "Ver Reporte"**

Purpose: View aggregated hour report (read-only)

Layout:
```
┌─────────────────────────────────────────────────────────────┐
│ REGISTRO DE HORAS DE AUDITORÍAS DEL SGC - AÑO 2026          │
│ Fecha de actualización: [Today]                             │
├─────────────────────────────────────────────────────────────┤
│ Auditor | Horas 2026 (OB/AF/AD/AL) | Acum Prev | Total Acum │
├─────────────────────────────────────────────────────────────┤
│ Marlene Andrea | -/-/10.0/10.0 | 12.2/42.1/60.1/32.6 | ... │
│ Yraima Rodríguez | -/-/32.5/29.0 | 7.3/44.5/124.6/6.0 | ...│
│ Angelo Mazzarino | -/-/18.2/- | 15.0/8.0/51.9/0.0 | ... │
│ Sara Rabelo | 4.0/-/-/- | 0.0/0.0/0.0/0.0 | ... │
│ ...            │ ... | ... | ... │
├─────────────────────────────────────────────────────────────┤
│ [Descargar PDF] [Copiar tabla]                              │
└─────────────────────────────────────────────────────────────┘
```

**Interaction:**
- Read data from Reporte_Horas_2026 (via Google Sheets API)
- Display as formatted table (styled to match PDF)
- Download button (export as PDF or image)
- Copy-to-clipboard button (for sharing)
- Auto-refreshes (every page load)

---

### 5.3 Code Changes Required

**File: `app.py`**
- Add HORAS to navigation buttons (alongside ENTRADA, SEGUIMIENTO, ANÁLISIS)
- Add session state for HORAS module
- Add two new tabs: "Registrar Horas", "Ver Reporte"
- Implement Tab 1: Form with dynamic rows + submission logic
- Implement Tab 2: Read report from Google Sheets + display

**File: `utils.py`**
- Add new function: `load_auditor_hours_data()` - reads Participaciones_2026
- Add new function: `load_hours_report()` - reads Reporte_Horas_2026
- Add new function: `save_auditor_participation()` - writes to Participaciones_2026
- Add new function: `get_auditor_list()` - returns team members from Horas_Base_2011_2025

**File: `.streamlit/secrets.toml`** (no changes - uses existing gsheets connection)

---

## 6. Data Validation & Error Handling

### 6.1 Input Validation (Tab 1: Registrar Horas)

| Field | Rule | Error Message |
|-------|------|--------------|
| Período | Required, one of 3 | "Selecciona un período válido" |
| Auditor (per row) | Required, in team list | "Auditor no reconocido" |
| Rol (per row) | Required, in (OB, AF, AD, AL) | "Rol debe ser OB, AF, AD o AL" |
| Horas (per row) | > 0, ≤ 24, decimal allowed | "Horas debe ser entre 0.1 y 24.0" |
| Completitud | All rows filled | "Completa todas las filas" |
| Duplicados | No (Auditor + Período + Rol) | "Este auditor ya tiene registro en esta sección con este rol" |

### 6.2 Error Handling

**Network Errors:**
```python
try:
    save_auditor_participation(data)
except Exception as e:
    st.error(f"Error al sincronizar: {str(e)}")
```

**Data Format Errors:**
```python
try:
    horas = float(input_value)
    assert horas > 0
except:
    st.error("Horas debe ser un número > 0")
```

---

## 7. Audit Trail & Immutability

### 7.1 Historical Data Protection

- **Horas_Base_2011_2025:** Read-only (no edits in app)
  - Values are extracted from official PDF
  - Protected at Google Sheets level (locked cells)

- **Participaciones_2026:** Append-only (no deletes/edits in app)
  - Records are immutable once saved
  - If correction needed: add new row with corrected values, mark old row as "CANCELADO" in Observaciones

- **Reporte_Horas_2026:** Formula-driven (no manual edits)
  - Auto-updates when Participaciones_2026 changes

### 7.2 Change Log

Optional: Add timestamp column to Participaciones_2026
```
Timestamp | ID | Fecha | Período | Proceso | Auditor | Rol | Horas | Observaciones
2026-06-04 10:30 | 1 | 4/6/2026 | Junio 1 (04-06) | EV | Marlene Andrea | AL | 10.0 | -
```

---

## 8. Reporting & Export

### 8.1 PDF Export

The "Ver Reporte" tab includes a download button that:
1. Reads Reporte_Horas_2026 from Google Sheets
2. Formats as PDF matching official SGC form layout
3. Includes header: "REGISTRO DE HORAS DE AUDITORÍAS DEL SGC - AÑO 2026"
4. Includes footer: Signature lines for Auditor Líder, Coordinador SGC, etc.

**Tool:** `reportlab` (already in requirements.txt)

---

## 9. Testing Strategy

### 9.1 Data Integrity Tests

- ✓ Participaciones_2026 entries persist after app restart
- ✓ Reporte_Horas_2026 formulas calculate correctly
- ✓ Adding participation updates report immediately
- ✓ Cumulative totals match manual calculation (spot check)
- ✓ Sara Rabelo appears in report with correct role/hours

### 9.2 UI/UX Tests

- ✓ Tab 1 form accepts valid entries
- ✓ Tab 1 rejects invalid entries with clear messages
- ✓ Tab 2 displays report with correct formatting
- ✓ Tab 2 PDF export produces valid file
- ✓ Dynamic row addition/removal works smoothly

### 9.3 Edge Cases

- ✓ Empty form submission (should be rejected)
- ✓ Duplicate auditor+rol in same período (should be rejected)
- ✓ Very large decimal hours (e.g., 23.9) accepted
- ✓ Very small decimal hours (e.g., 0.1) accepted
- ✓ Auditor with no participations still appears in report (0 hours)

---

## 10. Data Migration (Initial Setup)

### Step 1: Create Google Sheets Structure
- Create 3 new sheets in existing Google Sheets file
- Set up column headers and formatting
- Add data validation/dropdowns

### Step 2: Load Historical Data
- Extract from 2025 PDF (Horas_Base_2011_2025)
- Load 22 auditors + their 4 role columns
- Add Sara Rabelo with 0.0 baseline

### Step 3: Configure Formulas
- Set up SUMIFS in Reporte_Horas_2026 for 2026 hours
- Set up VLOOKUP for previous hours
- Set up calculation columns (totals)
- Set up COUNTIF for audit participation count

### Step 4: Test Formulas
- Enter sample data in Participaciones_2026
- Verify Reporte_Horas_2026 calculates correctly
- Verify rollup for each auditor

---

## 11. Future Enhancements

### Phase 2 (Optional):
- Add audit type column (Interna/Externa) for reporting
- Add external auditor tracking (Fondonorma auditors)
- Dashboard: Hours trend by auditor over years
- Alerts: Auditors approaching retirement (hours threshold)
- Bulk import from CSV (for historical data corrections)

---

## 12. Acceptance Criteria

- ✓ Google Sheets structure created with 3 sheets
- ✓ Historical data (2011-2025) loaded for all 22 + Sara
- ✓ Formulas in Reporte_Horas_2026 working correctly
- ✓ Streamlit HORAS module integrated in top nav
- ✓ Tab 1 (Registrar Horas) allows entry of multiple participations
- ✓ Tab 2 (Ver Reporte) displays aggregated report
- ✓ PDF export button generates valid file
- ✓ Data validates on submission (auditor, rol, hours)
- ✓ Report matches 2025 PDF format
- ✓ Manual calculation spot-checks match formula output

---

## Appendix A: Team Auditor List

**Full Team (23 auditors):**
1. Marlene Andrea (AD)
2. Yraima Rodríguez (AD)
3. Yolmarig Montilla (AL for 2026)
4. Pablo Galvis
5. Angelo Mazzarino (AD)
6. Xiomara Navas
7. Wiston Martínez
8. Alexander Romero
9. Osmaida Garcés
10. Alonzo Albarracín
11. Jerly Vielma
12. Arnaldo Guerra
13. Julia Manzano
14. Rodney Mazza
15. Fernando Velásquez
16. Rafael Rojas
17. Nelson Castillo
18. Reina Tayupo
19. Orbethsy Guetierrez
20. Daniel García
21. Delvy Guetierrez
22. Angélica Maldonado
23. Sara Rabelo (OB - new 2026)

---

## Appendix B: Process Codes (2026 Audits)

```
EV - Evaluación
FP - Fabricación de Productos
TR - Transporte
DR - Distribución
AC - Almacenamiento y Control
DD - Definición de Datos
AA - Análisis de Auditoría
GI - Gestión de Inventario
GM - Gestión de Materiales
PB - Procesos de Base
PP - Procesos de Producción
CO - Comercial
AS - Administración del SGC
GP - Gestión de Personas
DI - Dirección
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-09  
**Next Review:** After initial 2026 audit (June 2026)
