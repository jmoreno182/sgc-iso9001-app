# Tareas Pendientes - HORAS Module Implementation

**Status:** Code complete — pending: run `setup_horas_sheets.py` + final verification  
**Date Created:** 2026-06-09  
**Last Updated:** 2026-06-10

> **2026-06-10 — Automatización:** Las tareas 1-3 (Google Sheets) fueron automatizadas
> en el script `setup_horas_sheets.py` (raíz del repo). Los datos de los 22 auditores ya
> fueron extraídos del PDF usando las columnas **"Total de Horas Acumuladas"** (incluye
> Dic 2025, decisión confirmada por José el 2026-06-10) + Sara Rabelo en cero.
> Ejecutar: `venv\Scripts\python setup_horas_sheets.py` (usa `--force` para recrear).
> Las tareas de código 4-8 ya están implementadas en `app.py` y `utils.py`.

---

## Google Sheets Setup Tasks (Manual)

These three tasks require manual setup in Google Sheets and should be completed before proceeding with code implementation (Tasks 4-10).

### ✅ Task 1: Create Google Sheets Sheet "Horas_Base_2011_2025"

**Status:** ⏳ PENDING  
**Estimated Time:** 20 minutes  
**Complexity:** Low - Manual data entry

**Description:** 
Set up the historical baseline sheet with 23 auditors and their cumulative hours from 2011-2025.

**Steps:**
1. Open your Google Sheets (same spreadsheet where Matriz and SAC_OM are located)
2. Right-click on a sheet tab → "Insert 1 sheet" → Name: `Horas_Base_2011_2025`
3. Create headers in Row 1:
   - A1: Auditor
   - B1: OB_Prev
   - C1: AF_Prev
   - D1: AD_Prev
   - E1: AL_Prev
   - F1: Notas
4. Extract data from PDF "SGC-F-AS-024-2 Registro de horas de Auditoria":
   - Copy "Horas Acumuladas Previas" columns for all 22 auditors (rows 2-23)
   - Add Sara Rabelo in row 24 with all values = 0.0 (new auditor 2026)
5. Formatting:
   - Column widths: A=30, B=12, C=12, D=12, E=12, F=25
   - Cells B2:E24: Format → Decimal (2 places)
   - Row 1: Format → Bold, background color light gray
6. Protection:
   - Right-click sheet tab → Protect sheet → Allow: "Select cells only" (lock against edits)

**Reference Data Source:** 
- PDF: SGC-F-AS-024-2 Registro de horas de Auditoria.pdf
- Section: "Horas Acumuladas Previas" (columns OB, AF, AD, AL)
- All 22 auditors from the 2025 report

**Verification:**
- Count rows: Should have 23 auditors (rows 2-24)
- Column A: Check auditor names are complete
- Columns B-E: Verify all values are > 0 where applicable

**Notes:** 
- This is the read-only historical baseline
- Values should match exactly with 2025 PDF
- Will be referenced by formulas in Task 3

---

### ✅ Task 2: Create Google Sheets Sheet "Participaciones_2026"

**Status:** ⏳ PENDING  
**Estimated Time:** 30 minutes  
**Complexity:** Medium - Dropdowns & formulas

**Description:**
Set up the transaction log sheet where each row = one auditor participation in an audit. This is the primary data entry point.

**Steps:**

1. Right-click sheet tab → "Insert 1 sheet" → Name: `Participaciones_2026`

2. Create headers in Row 1:
   - A1: ID
   - B1: Fecha
   - C1: Período
   - D1: Proceso
   - E1: Auditor
   - F1: Rol
   - G1: Horas
   - H1: Observaciones

3. Set up data validation dropdowns:

   **Column E (Auditor) - List from range:**
   - Select E2:E1000
   - Data → Validation → List from a range
   - Range: `Horas_Base_2011_2025!$A$2:$A$24`
   - Show dropdown arrow: Yes

   **Column F (Rol) - List of items:**
   - Select F2:F1000
   - Data → Validation → List of items
   - Items: `OB, AF, AD, AL`
   - Show dropdown arrow: Yes

   **Column D (Proceso) - List of items:**
   - Select D2:D1000
   - Data → Validation → List of items
   - Items: `EV, FP, TR, DR, AC, DD, AA, GI, GM, PB, PP, CO, AS, GP, DI`
   - Show dropdown arrow: Yes

4. Set up auto-calculating columns:

   **Column C (Período) - Auto-calculate from date:**
   - Click C2
   - Enter formula: `=IF(DAY(B2)<=6,"Junio 1 (04-06)",IF(DAY(B2)<=12,"Junio 2 (08-12)","Junio 3 (15+)"))`
   - Copy formula down to C1000

   **Column A (ID) - Auto-increment:**
   - Click A2
   - Enter formula: `=IF(B2="","",ROW()-1)`
   - Copy down to A1000 (will auto-number 1, 2, 3... as data is entered)

5. Set up data validation for Horas:
   - Select G2:G1000
   - Data → Validation → Custom formula
   - Formula: `=AND(G2>0, G2<=24)`
   - Error message: "Horas must be between 0.1 and 24.0"

6. Format columns:
   - Column A (ID): Width 8, center align
   - Column B (Fecha): Width 15, number format `M/D/YYYY`
   - Column C (Período): Width 20, center align
   - Column D (Proceso): Width 12, center align
   - Column E (Auditor): Width 25
   - Column F (Rol): Width 12, center align
   - Column G (Horas): Width 12, number format decimal (1 decimal place)
   - Column H (Observaciones): Width 30

**Verification:**
- All dropdowns working
- Período formula calculates correctly (test with date 4/6/2026 → should show "Junio 1 (04-06)")
- ID formula works (test with any date → should show row number)
- No errors in validation formulas

**Notes:**
- This is the data entry point for Streamlit app
- Data will be read by formulas in Task 3
- Empty rows will be auto-generated with formulas (don't delete them)

---

### ✅ Task 3: Create Google Sheets Sheet "Reporte_Horas_2026"

**Status:** ⏳ PENDING  
**Estimated Time:** 40 minutes  
**Complexity:** High - Complex formulas

**Description:**
Set up the aggregated report sheet with formulas that auto-calculate totals from Participaciones_2026. This is read-only and updates automatically.

**Steps:**

1. Right-click sheet tab → "Insert 1 sheet" → Name: `Reporte_Horas_2026`

2. Create headers in Row 1:
   - A1: Auditor
   - B1: OB_2026
   - C1: AF_2026
   - D1: AD_2026
   - E1: AL_2026
   - F1: OB_Prev
   - G1: AF_Prev
   - H1: AD_Prev
   - I1: AL_Prev
   - J1: OB_Total
   - K1: AF_Total
   - L1: AD_Total
   - M1: AL_Total
   - N1: Total_Auditorías

3. Format row 1: Bold, background color light gray

4. List all 23 auditors in column A:
   - Starting at A2, copy-paste all 23 auditors from Horas_Base_2011_2025 column A
   - Rows 2-24 should be: Marlene Andrea, Yraima Rodríguez, ..., Sara Rabelo

5. Set up SUMIFS formulas for 2026 hours (columns B-E):
   - Click B2
   - Enter formula: `=SUMIFS(Participaciones_2026!$G:$G, Participaciones_2026!$E:$E, A2, Participaciones_2026!$F:$F, "OB")`
   - This sums hours from Participaciones_2026 where Auditor = A2 and Rol = "OB"
   - Copy this formula right to C2, D2, E2 BUT change the last parameter:
     - C2 (AF_2026): Change "OB" → "AF"
     - D2 (AD_2026): Change "OB" → "AD"
     - E2 (AL_2026): Change "OB" → "AL"
   - Then copy all B2:E2 down to B24:E24

6. Set up VLOOKUP formulas for previous hours (columns F-I):
   - Click F2
   - Enter formula: `=IFERROR(VLOOKUP(A2, Horas_Base_2011_2025!$A:$B, 2, FALSE), 0)`
   - This looks up auditor in historical base and returns OB_Prev value
   - Copy this formula right to G2, H2, I2 BUT change the column number:
     - F2 (OB_Prev): Column 2 (column B of Horas_Base_2011_2025 = OB_Prev)
     - G2 (AF_Prev): Change column 2 → 3 (column C = AF_Prev)
     - H2 (AD_Prev): Change column 2 → 4 (column D = AD_Prev)
     - I2 (AL_Prev): Change column 2 → 5 (column E = AL_Prev)
   - Then copy all F2:I2 down to F24:I24

7. Set up sum formulas for totals (columns J-M):
   - Click J2
   - Enter formula: `=B2+F2`
   - This adds 2026 hours + previous hours = cumulative total
   - Copy right to K2, L2, M2 (will auto-adjust: C2+G2, D2+H2, E2+I2)
   - Then copy all J2:M2 down to J24:M24

8. Set up COUNTIF formula for audit count (column N):
   - Click N2
   - Enter formula: `=COUNTIF(Participaciones_2026!$E:$E, A2)`
   - This counts how many times auditor appears in Participaciones_2026
   - Copy down to N24

9. Format numeric columns:
   - B2:E24 (2026 hours): Format → Decimal (1 decimal place)
   - F2:I24 (Prev hours): Format → Decimal (1 decimal place)
   - J2:M24 (Total hours): Format → Decimal (1 decimal place)
   - N2:N24 (Audit count): Format → Number (0 decimal places)

10. Protect sheet:
    - Right-click sheet tab → Protect sheet
    - Allow: "Select cells only, View formulas" (allows viewing but not editing)

**Verification:**
- All 23 auditors appear in rows 2-24
- All formulas calculate without errors (check for #REF!, #VALUE!, etc.)
- Test with sample data:
  - Add 1 row to Participaciones_2026: Marlene Andrea, AL, 10.0
  - Reporte_Horas_2026 should update: Marlene AL_2026 = 10.0, AL_Total = 32.6 + 10.0 = 42.6
- Empty cells should show 0 (not errors)

**Notes:**
- This is read-only (protected from editing)
- Formulas auto-update when data is added to Participaciones_2026
- Values match 2025 PDF format and structure
- Will be displayed in Streamlit Tab 2

---

## Code Implementation Tasks (Automated - Ready for Subagents)

Tasks 4-10 are code-based and will be handled by subagents after these 3 Google Sheets tasks are complete.

- [x] Task 4: Add HORAS Module to Streamlit - Navigation & Imports ✅ 2026-06-10
- [x] Task 5: Add HORAS Module - Tab 1 (Registrar Horas) ✅ 2026-06-10
- [x] Task 6: Add HORAS Module - Tab 2 (Ver Reporte) ✅ 2026-06-10
- [x] Task 7: Add Google Sheets I/O Functions to utils.py (`load_horas_data`, `append_participacion`) ✅ 2026-06-10
- [x] Task 8: Wire Functions to HORAS Module UI ✅ 2026-06-10
- [ ] Task 9: Testing & Validation (pendiente: requiere hojas creadas — ejecutar setup_horas_sheets.py)
- [x] Task 10: Final Integration & Documentation (CLAUDE.md actualizado) ✅ 2026-06-10

---

## Completion Checklist

### Google Sheets Tasks
- [ ] Task 1: Horas_Base_2011_2025 sheet created with 23 auditors
- [ ] Task 2: Participaciones_2026 sheet created with dropdowns & formulas
- [ ] Task 3: Reporte_Horas_2026 sheet created with aggregation formulas

**All done?** Run: `git status` and post message below to continue with code tasks.

### Code Tasks (After Google Sheets)
- [ ] Task 4-10: Automated via subagents

---

## How to Use This Document

1. **Open this file** when you're ready to set up Google Sheets
2. **Complete each task in order** (Task 1 → Task 2 → Task 3)
3. **Verify each checkpoint** before moving to next
4. **Post message** when all 3 are done to start code implementation

**Estimated Total Time:** 90 minutes for all 3 sheets

---

## Reference Files

- PDF Source: `SGC-F-AS-024-2 Registro de horas de Auditoria.pdf` (in this repo)
- Implementation Plan: `docs/superpowers/plans/2026-06-09-auditor-hours-tracking-implementation.md`
- Design Spec: `docs/superpowers/specs/2026-06-09-auditor-hours-tracking-design.md`

---

**Created:** 2026-06-09  
**Last Updated:** 2026-06-09
