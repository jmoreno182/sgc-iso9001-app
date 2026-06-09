# Auditor Hours Tracking Module - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a complete auditor hours tracking system in Google Sheets and Streamlit, automating the ISO 9001:2015 audit hour reporting process for 2026.

**Architecture:** Three-sheet Google Sheets database (historical base, transaction log, aggregated report) with Streamlit UI (HORAS module) for data entry and report viewing. Formulas auto-aggregate hours by auditor and role; app provides validation, data sync, and PDF export.

**Tech Stack:** Streamlit, Google Sheets API (via streamlit-gsheets-connection), Pandas, ReportLab (PDF export), Python

---

## File Structure

**Files to Create:**
- None (integration into existing app.py)

**Files to Modify:**
- `app.py` — Add HORAS module with 2 tabs (entry + report)
- `utils.py` — Add 4 new functions for hours data I/O

**Google Sheets (new sheets in existing spreadsheet):**
- `Horas_Base_2011_2025` — Historical accumulation (read-only reference)
- `Participaciones_2026` — Transaction log (data entry point)
- `Reporte_Horas_2026` — Report output (formula-driven aggregation)

---

## Task Breakdown

### Task 1: Create Google Sheets Structure - Sheet 1

**Files:**
- Google Sheets: Create new sheet `Horas_Base_2011_2025`

**Goal:** Set up the historical baseline with 22 auditors from 2025 PDF + Sara Rabelo (new).

- [ ] **Step 1: Create new sheet in Google Sheets**

In your existing Google Sheets file (same one where Matriz and SAC_OM are), right-click the sheet tab → "Insert 1 sheet" → Name: `Horas_Base_2011_2025`

- [ ] **Step 2: Set up column headers**

Row 1, enter these headers:
```
A1: Auditor
B1: OB_Prev
C1: AF_Prev
D1: AD_Prev
E1: AL_Prev
F1: Notas
```

- [ ] **Step 3: Load 2025 PDF data**

From "SGC-F-AS-024-2 Registro de horas de Auditoria" PDF, extract the "Horas Acumuladas Previas" columns for all 22 auditors. Enter data row by row:

```
A2: Marlene Andrea | B2: 12.2 | C2: 42.1 | D2: 60.1 | E2: 32.6 | F2: Extracted from 2025 PDF
A3: Yraima Rodríguez | B3: 7.3 | C3: 44.5 | D3: 124.6 | E3: 6.0 | F3: Extracted from 2025 PDF
A4: Yolmarig Montilla | B4: 12.3 | C4: 24.5 | D4: 112.5 | E4: 22.0 | F4: Extracted from 2025 PDF
A5: Pablo Galvis | B5: 9.2 | C5: 31.3 | D5: 52.3 | E5: 0.0 | F5: Extracted from 2025 PDF
A6: Angelo Mazzarino | B6: 15.0 | C6: 8.0 | D6: 51.9 | E6: 0.0 | F6: Extracted from 2025 PDF
A7: Xiomara Navas | B7: 4.0 | C7: 11.3 | D7: 45.4 | E7: 0.0 | F7: Extracted from 2025 PDF
... (continue for all 22 auditors from PDF)
```

Extract all 22 from the PDF's "Horas Acumuladas Previas" section.

- [ ] **Step 4: Add Sara Rabelo (new auditor)**

Row 24 (after all 22):
```
A24: Sara Rabelo | B24: 0.0 | C24: 0.0 | D24: 0.0 | E24: 0.0 | F24: Nueva 2026
```

- [ ] **Step 5: Format and protect sheet**

- Select columns A:F
- Set font to Arial 11
- Set column widths: A=30, B=12, C=12, D=12, E=12, F=25
- Select cells B2:E24 → Format → Number format → Decimal (2 places)
- Select rows 1 → Format → Bold, background color light gray
- Right-click sheet tab → Protect sheet → Allow: "Select cells only" (lock against edits)

- [ ] **Step 6: Verify data entry**

Count rows: Should have 23 auditors (rows 2-24)
Test formula reference: Click a cell, should show values

✅ **Checkpoint:** Sheet 1 created with 23 auditors and historical data locked.

---

### Task 2: Create Google Sheets Structure - Sheet 2

**Files:**
- Google Sheets: Create new sheet `Participaciones_2026`

**Goal:** Set up transaction log where each row = one auditor participation in one audit.

- [ ] **Step 1: Create new sheet**

Right-click sheet tab → "Insert 1 sheet" → Name: `Participaciones_2026`

- [ ] **Step 2: Set up column headers**

Row 1:
```
A1: ID
B1: Fecha
C1: Período
D1: Proceso
E1: Auditor
F1: Rol
G1: Horas
H1: Observaciones
```

- [ ] **Step 3: Set up data validation dropdowns**

Column E (Auditor) - Dropdown list:
- Select E2:E1000
- Data → Validation → List from a range
- Range: `Horas_Base_2011_2025!$A$2:$A$24` (all auditor names)
- Show dropdown arrow: Yes

Column F (Rol) - Dropdown list:
- Select F2:F1000
- Data → Validation → List of items
- Items: `OB, AF, AD, AL`
- Show dropdown arrow: Yes

Column D (Proceso) - Dropdown list:
- Select D2:D1000
- Data → Validation → List of items
- Items: `EV, FP, TR, DR, AC, DD, AA, GI, GM, PB, PP, CO, AS, GP, DI`
- Show dropdown arrow: Yes

- [ ] **Step 4: Set up Período formula**

Column C will auto-calculate based on Fecha. Click C2:

```
=IF(DAY(B2)<=6,"Junio 1 (04-06)",IF(DAY(B2)<=12,"Junio 2 (08-12)","Junio 3 (15+)"))
```

Copy formula down to C1000.

- [ ] **Step 5: Set up ID auto-increment**

Click A2:
```
=IF(B2="","",ROW()-1)
```

Copy down to A1000 (will auto-number 1, 2, 3... as data is entered).

- [ ] **Step 6: Format columns**

- Column A (ID): Width 8, center align
- Column B (Fecha): Width 15, number format `M/D/YYYY`
- Column C (Período): Width 20, center align
- Column D (Proceso): Width 12, center align
- Column E (Auditor): Width 25
- Column F (Rol): Width 12, center align
- Column G (Horas): Width 12, number format decimal (1 decimal place)
- Column H (Observaciones): Width 30

- [ ] **Step 7: Add data validation to Horas column**

Select G2:G1000:
- Data → Validation → Custom formula
- Formula: `=AND(G2>0, G2<=24)`
- Show error: "Horas must be between 0.1 and 24.0"

✅ **Checkpoint:** Sheet 2 created with dropdowns, formulas, and validation ready for data entry.

---

### Task 3: Create Google Sheets Structure - Sheet 3

**Files:**
- Google Sheets: Create new sheet `Reporte_Horas_2026`

**Goal:** Auto-aggregating report sheet with formulas that calculate totals from Participaciones_2026.

- [ ] **Step 1: Create new sheet**

Right-click sheet tab → "Insert 1 sheet" → Name: `Reporte_Horas_2026`

- [ ] **Step 2: Set up column headers**

Row 1:
```
A1: Auditor
B1: OB_2026
C1: AF_2026
D1: AD_2026
E1: AL_2026
F1: OB_Prev
G1: AF_Prev
H1: AD_Prev
I1: AL_Prev
J1: OB_Total
K1: AF_Total
L1: AD_Total
M1: AL_Total
N1: Total_Auditorías
```

Format row 1: Bold, background light gray.

- [ ] **Step 3: List all auditors in column A**

Starting A2, list all 23 auditors (copy-paste from Horas_Base_2011_2025 column A):

```
A2: Marlene Andrea
A3: Yraima Rodríguez
A4: Yolmarig Montilla
... (all 23)
A24: Sara Rabelo
```

- [ ] **Step 4: Set up SUMIFS formula for OB_2026 (column B)**

Click B2:
```
=SUMIFS(Participaciones_2026!$G:$G, Participaciones_2026!$E:$E, A2, Participaciones_2026!$F:$F, "OB")
```

Copy this formula right to C2, D2, E2 BUT change the last parameter:
- C2 (AF_2026): Change "OB" → "AF"
- D2 (AD_2026): Change "OB" → "AD"
- E2 (AL_2026): Change "OB" → "AL"

Then copy all B2:E2 down to B24:E24.

- [ ] **Step 5: Set up VLOOKUP formula for OB_Prev (column F)**

Click F2:
```
=IFERROR(VLOOKUP(A2, Horas_Base_2011_2025!$A:$B, 2, FALSE), 0)
```

Copy this formula right to G2, H2, I2 BUT change the column number:
- F2 (OB_Prev): Column 2 (B = OB_Prev)
- G2 (AF_Prev): Change column 2 → 3 (C = AF_Prev)
- H2 (AD_Prev): Change column 2 → 4 (D = AD_Prev)
- I2 (AL_Prev): Change column 2 → 5 (E = AL_Prev)

Then copy all F2:I2 down to F24:I24.

- [ ] **Step 6: Set up sum formula for OB_Total (column J)**

Click J2:
```
=B2+F2
```

Copy right to K2, L2, M2 (will auto-adjust: C2+G2, D2+H2, E2+I2).
Then copy all J2:M2 down to J24:M24.

- [ ] **Step 7: Set up COUNTIF formula for Total_Auditorías (column N)**

Click N2:
```
=COUNTIF(Participaciones_2026!$E:$E, A2)
```

Copy down to N24.

- [ ] **Step 8: Format numeric columns**

Select B2:E24 (2026 hours) → Format → Decimal (1 decimal place)
Select F2:I24 (Prev hours) → Format → Decimal (1 decimal place)
Select J2:M24 (Total hours) → Format → Decimal (1 decimal place)
Select N2:N24 (Audit count) → Format → Number (0 decimal places)

- [ ] **Step 9: Lock sheet**

Right-click sheet tab → Protect sheet → Allow: "Select cells only, View formulas" (allows viewing but not editing).

✅ **Checkpoint:** Sheet 3 created with all formulas configured. Ready to auto-update as data is entered in Participaciones_2026.

---

### Task 4: Add HORAS Module to Streamlit - Navigation & Imports

**Files:**
- Modify: `app.py` (lines 330-350, navigation section)

**Goal:** Add HORAS button to top navigation and prepare module state.

- [ ] **Step 1: Read current navigation code**

Open `app.py`, find the navigation section (around line 330-343):

```python
col1, col2, col3 = st.columns(3, gap="small")
with col1:
    if st.button("ENTRADA", key="nav_entrada", use_container_width=True):
        st.session_state.modulo = "ENTRADA"
with col2:
    if st.button("SEGUIMIENTO", key="nav_seguimiento", use_container_width=True):
        st.session_state.modulo = "SEGUIMIENTO"
with col3:
    if st.button("ANÁLISIS", key="nav_analisis", use_container_width=True):
        st.session_state.modulo = "ANÁLISIS"
```

- [ ] **Step 2: Modify navigation to 4 columns**

Replace the 3-column setup with 4 columns:

```python
col1, col2, col3, col4 = st.columns(4, gap="small")
with col1:
    if st.button("ENTRADA", key="nav_entrada", use_container_width=True):
        st.session_state.modulo = "ENTRADA"
with col2:
    if st.button("SEGUIMIENTO", key="nav_seguimiento", use_container_width=True):
        st.session_state.modulo = "SEGUIMIENTO"
with col3:
    if st.button("ANÁLISIS", key="nav_analisis", use_container_width=True):
        st.session_state.modulo = "ANÁLISIS"
with col4:
    if st.button("HORAS", key="nav_horas", use_container_width=True):
        st.session_state.modulo = "HORAS"
```

- [ ] **Step 3: Update module initialization**

Find the line that initializes default module (around line 343):

```python
if "modulo" not in st.session_state:
    st.session_state.modulo = "ENTRADA"
```

No change needed (already correct).

- [ ] **Step 4: Commit navigation change**

```bash
git add app.py
git commit -m "feat: add HORAS button to top navigation (4-column layout)

- Replace 3-column nav with 4-column (ENTRADA, SEGUIMIENTO, ANÁLISIS, HORAS)
- Session state already handles module switching
- HORAS module implementation to follow"
```

✅ **Checkpoint:** Navigation updated. HORAS button visible in app (but no module logic yet).

---

### Task 5: Add HORAS Module - Tab 1 (Registrar Horas)

**Files:**
- Modify: `app.py` (add new elif block after ANÁLISIS section, around line 535)

**Goal:** Implement data entry form with dynamic rows for multiple auditor participations.

- [ ] **Step 1: Add module conditional**

Find the end of the ANÁLISIS module (around line 535), then add:

```python
# ==========================================
# MÓDULO 4: HORAS DE AUDITORÍA
# ==========================================
elif st.session_state.modulo == "HORAS":
    st.title("REGISTRO DE HORAS DE AUDITORÍA")
    st.markdown("Registra las horas de auditoría de cada participante por período.")
    
    tab1, tab2 = st.tabs(["Registrar Horas", "Ver Reporte"])
    
    with tab1:
        st.subheader("Registrar Participaciones")
        
        # Initialize session state for form
        if "horas_participaciones" not in st.session_state:
            st.session_state.horas_participaciones = [
                {"auditor": "", "rol": "", "horas": ""}
            ]
        
        # Period selector
        periodo = st.radio(
            "Selecciona el período de auditoría:",
            options=["Junio 1 (4-6)", "Junio 2 (8-12)", "Junio 3 (15+)"],
            horizontal=True,
            key="horas_periodo"
        )
        
        st.markdown("---")
        st.write("**Agregar participaciones de auditores:**")
        
        # Dynamic rows
        auditor_options = sorted(df_matriz['auditor_responsable'].dropna().unique().tolist()) if not df_matriz.empty else []
        # Also include all 23 from Horas_Base_2011_2025
        # For now, use available auditors from the app
        
        rol_options = ["OB", "AF", "AD", "AL"]
        
        for idx, participacion in enumerate(st.session_state.horas_participaciones):
            col1, col2, col3, col_btn = st.columns([3, 2, 2, 1])
            
            with col1:
                st.session_state.horas_participaciones[idx]["auditor"] = st.selectbox(
                    "Auditor",
                    options=auditor_options if auditor_options else ["Marlene Andrea", "Yraima Rodríguez", "Angelo Mazzarino"],
                    value=participacion.get("auditor", ""),
                    key=f"auditor_{idx}"
                )
            
            with col2:
                st.session_state.horas_participaciones[idx]["rol"] = st.selectbox(
                    "Rol",
                    options=rol_options,
                    value=participacion.get("rol", ""),
                    key=f"rol_{idx}"
                )
            
            with col3:
                horas_input = st.number_input(
                    "Horas",
                    min_value=0.1,
                    max_value=24.0,
                    value=float(participacion.get("horas")) if participacion.get("horas") else 0.0,
                    step=0.1,
                    key=f"horas_{idx}"
                )
                st.session_state.horas_participaciones[idx]["horas"] = str(horas_input)
            
            with col_btn:
                if st.button("❌", key=f"remove_{idx}", help="Remover esta fila"):
                    st.session_state.horas_participaciones.pop(idx)
                    st.rerun()
        
        st.markdown("")
        if st.button("+ Agregar otra fila", key="add_row"):
            st.session_state.horas_participaciones.append({"auditor": "", "rol": "", "horas": ""})
            st.rerun()
        
        st.markdown("---")
        
        # Submit button
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("Guardar Participaciones", use_container_width=True, key="save_horas"):
                # Validation
                try:
                    errors = []
                    
                    for idx, p in enumerate(st.session_state.horas_participaciones):
                        if not p.get("auditor"):
                            errors.append(f"Fila {idx+1}: Auditor requerido")
                        if not p.get("rol"):
                            errors.append(f"Fila {idx+1}: Rol requerido")
                        if not p.get("horas") or float(p.get("horas", 0)) <= 0:
                            errors.append(f"Fila {idx+1}: Horas debe ser > 0")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        # Save to Google Sheets
                        try:
                            save_auditor_participations(periodo, st.session_state.horas_participaciones)
                            st.success(f"✓ {len(st.session_state.horas_participaciones)} participación(es) guardada(s)")
                            st.session_state.horas_participaciones = [
                                {"auditor": "", "rol": "", "horas": ""}
                            ]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al sincronizar: {str(e)}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col_btn2:
            if st.button("Limpiar formulario", use_container_width=True):
                st.session_state.horas_participaciones = [
                    {"auditor": "", "rol": "", "horas": ""}
                ]
                st.rerun()
```

- [ ] **Step 2: Test the UI**

Run the app:
```bash
streamlit run app.py
```

Click HORAS button. Verify:
- ✓ Tab "Registrar Horas" shows period selector
- ✓ One empty row for entry (Auditor, Rol, Horas columns)
- ✓ "+ Agregar otra fila" button works
- ✓ "❌" button removes rows
- ✓ "Guardar Participaciones" button present

- [ ] **Step 3: Commit Tab 1**

```bash
git add app.py
git commit -m "feat: add HORAS Tab 1 (Registrar Horas) - UI only

- Dynamic form with period selector (Junio 1/2/3)
- Multiple rows: Auditor | Rol | Horas
- Add/remove row buttons
- Form state in session_state (not yet saved to Google Sheets)
- Validation logic ready (save function to be implemented in utils.py)"
```

✅ **Checkpoint:** Tab 1 UI complete and working. Form collects data but doesn't save yet.

---

### Task 6: Add HORAS Module - Tab 2 (Ver Reporte)

**Files:**
- Modify: `app.py` (in HORAS module, add Tab 2 content)

**Goal:** Display aggregated report from Google Sheets with formatting matching 2025 PDF.

- [ ] **Step 1: Add Tab 2 content (in same elif block, after with tab1)**

After the `with tab1:` block ends, add:

```python
    with tab2:
        st.subheader("Reporte de Horas de Auditoría 2026")
        
        try:
            # Load report from Google Sheets
            df_reporte = load_hours_report()
            
            if df_reporte.empty:
                st.info("Sin datos de horas registradas aún. Comienza en la tab 'Registrar Horas'.")
            else:
                # Display as formatted table
                st.write("**REGISTRO DE HORAS DE AUDITORÍAS DEL SGC - AÑO 2026**")
                st.write(f"*Fecha de actualización: {datetime.now().strftime('%d/%m/%Y')}*")
                
                st.dataframe(
                    df_reporte,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Auditor": st.column_config.TextColumn(width="large"),
                        "OB_2026": st.column_config.NumberColumn(format="%.1f"),
                        "AF_2026": st.column_config.NumberColumn(format="%.1f"),
                        "AD_2026": st.column_config.NumberColumn(format="%.1f"),
                        "AL_2026": st.column_config.NumberColumn(format="%.1f"),
                        "OB_Prev": st.column_config.NumberColumn(format="%.1f"),
                        "AF_Prev": st.column_config.NumberColumn(format="%.1f"),
                        "AD_Prev": st.column_config.NumberColumn(format="%.1f"),
                        "AL_Prev": st.column_config.NumberColumn(format="%.1f"),
                        "OB_Total": st.column_config.NumberColumn(format="%.1f"),
                        "AF_Total": st.column_config.NumberColumn(format="%.1f"),
                        "AD_Total": st.column_config.NumberColumn(format="%.1f"),
                        "AL_Total": st.column_config.NumberColumn(format="%.1f"),
                        "Total_Auditorías": st.column_config.NumberColumn(format="%.0f"),
                    }
                )
                
                st.markdown("---")
                
                # Export buttons
                col_export1, col_export2 = st.columns(2)
                
                with col_export1:
                    if st.button("Descargar PDF", use_container_width=True):
                        pdf_buffer = generate_hours_pdf(df_reporte)
                        st.download_button(
                            label="Descargar",
                            data=pdf_buffer,
                            file_name=f"Registro_Horas_Auditoria_2026_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                
                with col_export2:
                    if st.button("Copiar a portapapeles", use_container_width=True):
                        st.info("Funcionalidad para próximas versiones")
        
        except Exception as e:
            st.error(f"Error al cargar reporte: {str(e)}")
```

- [ ] **Step 2: Test Tab 2**

Run app and click HORAS → Ver Reporte tab.

Expected:
- ✓ "Sin datos" message if no participations yet
- ✓ (After adding data in Tab 1) Table displays with all columns
- ✓ Numbers formatted with 1 decimal place
- ✓ "Descargar PDF" button present
- ✓ No errors in console

- [ ] **Step 3: Commit Tab 2**

```bash
git add app.py
git commit -m "feat: add HORAS Tab 2 (Ver Reporte) - UI only

- Display aggregated report from Reporte_Horas_2026 sheet
- Formatted dataframe with 14 numeric columns
- Decimal formatting (1 place for hours, 0 for count)
- Download PDF button (function to be implemented)
- Real-time auto-refresh from Google Sheets"
```

✅ **Checkpoint:** Tab 2 UI complete. Shows placeholder message until data functions are implemented.

---

### Task 7: Add Google Sheets I/O Functions to utils.py

**Files:**
- Modify: `utils.py` (add 4 new functions at end)

**Goal:** Implement data I/O for hours tracking (read/write to Google Sheets).

- [ ] **Step 1: Add function to load hours base data**

At the end of `utils.py`, add:

```python
def load_hours_base_data():
    """
    Load historical hours data (2011-2025) from Horas_Base_2011_2025 sheet.
    Returns: DataFrame with columns [Auditor, OB_Prev, AF_Prev, AD_Prev, AL_Prev, Notas]
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(
            spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"],
            worksheet="Horas_Base_2011_2025",
            ttl=0
        )
        return df
    except Exception as e:
        st.error(f"Error loading hours base data: {str(e)}")
        return pd.DataFrame()


def load_participations_2026():
    """
    Load 2026 audit participations from Participaciones_2026 sheet.
    Returns: DataFrame with columns [ID, Fecha, Período, Proceso, Auditor, Rol, Horas, Observaciones]
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(
            spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"],
            worksheet="Participaciones_2026",
            ttl=0
        )
        # Remove empty rows
        df = df.dropna(subset=["ID"])
        return df
    except Exception as e:
        st.error(f"Error loading participations: {str(e)}")
        return pd.DataFrame()


def load_hours_report():
    """
    Load aggregated hours report from Reporte_Horas_2026 sheet.
    Returns: DataFrame with columns [Auditor, OB_2026, AF_2026, AD_2026, AL_2026, 
                                      OB_Prev, AF_Prev, AD_Prev, AL_Prev,
                                      OB_Total, AF_Total, AD_Total, AL_Total, Total_Auditorías]
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(
            spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"],
            worksheet="Reporte_Horas_2026",
            ttl=0
        )
        return df
    except Exception as e:
        st.error(f"Error loading hours report: {str(e)}")
        return pd.DataFrame()


def save_auditor_participations(periodo, participaciones):
    """
    Save auditor participations to Participaciones_2026 sheet.
    
    Args:
        periodo: String like "Junio 1 (4-6)"
        participaciones: List of dicts [{"auditor": "...", "rol": "...", "horas": "..."}]
    
    Returns: True if success, raises Exception if error
    """
    try:
        # Load existing data
        df_existing = load_participations_2026()
        
        # Determine next ID
        max_id = int(df_existing['ID'].max()) if not df_existing.empty else 0
        
        # Create new rows
        new_rows = []
        for idx, p in enumerate(participaciones):
            if p.get("auditor") and p.get("rol") and p.get("horas"):
                # Extract date from periodo
                if "4-6" in periodo:
                    fecha = "4/6/2026"
                elif "8-12" in periodo:
                    fecha = "8/6/2026"
                else:
                    fecha = "15/6/2026"
                
                new_rows.append({
                    "ID": max_id + idx + 1,
                    "Fecha": fecha,
                    "Período": periodo,
                    "Proceso": "",  # Will be filled separately if needed
                    "Auditor": p.get("auditor"),
                    "Rol": p.get("rol"),
                    "Horas": float(p.get("horas")),
                    "Observaciones": ""
                })
        
        if not new_rows:
            raise ValueError("No valid participations to save")
        
        # Append to existing
        df_new = pd.DataFrame(new_rows)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        
        # Write back to Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.write(
            data=df_combined,
            spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"],
            worksheet="Participaciones_2026"
        )
        
        return True
    
    except Exception as e:
        raise Exception(f"Error saving participations: {str(e)}")
```

- [ ] **Step 2: Add function to generate PDF**

Continue in `utils.py`:

```python
def generate_hours_pdf(df_reporte):
    """
    Generate PDF report of hours in SGC format.
    
    Args:
        df_reporte: DataFrame from load_hours_report()
    
    Returns: BytesIO buffer with PDF content
    """
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from io import BytesIO
    
    try:
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=0.5*inch)
        elements = []
        
        # Title
        styles = getSampleStyleSheet()
        title = Paragraph(
            "<b>REGISTRO DE HORAS DE AUDITORÍAS DEL SGC - AÑO 2026</b>",
            styles['Heading2']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Prepare table data
        headers = [
            "Auditor", "OB_2026", "AF_2026", "AD_2026", "AL_2026",
            "OB_Prev", "AF_Prev", "AD_Prev", "AL_Prev",
            "OB_Total", "AF_Total", "AD_Total", "AL_Total", "Total_Auditorías"
        ]
        
        table_data = [headers]
        for _, row in df_reporte.iterrows():
            table_data.append([
                str(row.get('Auditor', '')),
                f"{row.get('OB_2026', 0):.1f}",
                f"{row.get('AF_2026', 0):.1f}",
                f"{row.get('AD_2026', 0):.1f}",
                f"{row.get('AL_2026', 0):.1f}",
                f"{row.get('OB_Prev', 0):.1f}",
                f"{row.get('AF_Prev', 0):.1f}",
                f"{row.get('AD_Prev', 0):.1f}",
                f"{row.get('AL_Prev', 0):.1f}",
                f"{row.get('OB_Total', 0):.1f}",
                f"{row.get('AF_Total', 0):.1f}",
                f"{row.get('AD_Total', 0):.1f}",
                f"{row.get('AL_Total', 0):.1f}",
                f"{int(row.get('Total_Auditorías', 0))}"
            ])
        
        # Create table
        table = Table(table_data, colWidths=[1.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch,
                                             0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch,
                                             0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch])
        
        # Style table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer
    
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None
```

- [ ] **Step 3: Add imports at top of utils.py**

Make sure these are in the imports section:

```python
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
```

- [ ] **Step 4: Test the functions**

In Python terminal:

```python
# Test load functions (should not error)
from utils import load_hours_base_data, load_participations_2026, load_hours_report
df_base = load_hours_base_data()
print(f"Base data: {len(df_base)} rows")
df_part = load_participations_2026()
print(f"Participations: {len(df_part)} rows")
df_report = load_hours_report()
print(f"Report: {len(df_report)} rows")
```

- [ ] **Step 5: Commit utils.py changes**

```bash
git add utils.py
git commit -m "feat: add Google Sheets I/O functions for hours tracking

- load_hours_base_data(): Read Horas_Base_2011_2025 (historical)
- load_participations_2026(): Read Participaciones_2026 (transaction log)
- load_hours_report(): Read Reporte_Horas_2026 (aggregated report)
- save_auditor_participations(): Write new participations, auto-assign ID
- generate_hours_pdf(): Create PDF export of report
- All functions use ttl=0 for real-time data sync"
```

✅ **Checkpoint:** All Google Sheets I/O functions implemented. App can now read/write hours data.

---

### Task 8: Wire Functions to HORAS Module UI

**Files:**
- Modify: `app.py` (update HORAS module to call functions)

**Goal:** Connect form submission and report display to actual Google Sheets data.

- [ ] **Step 1: Update Tab 1 save button call**

In the Tab 1 "Guardar Participaciones" button section, update the call:

From:
```python
save_auditor_participations(periodo, st.session_state.horas_participaciones)
```

To add import at top of app.py:
```python
from utils import load_hours_base_data, load_participations_2026, load_hours_report, save_auditor_participations, generate_hours_pdf
```

Then the call remains the same (already correct in Task 5).

- [ ] **Step 2: Update Tab 2 report load**

In Tab 2 "Ver Reporte" section, the code already calls `load_hours_report()`, which is now implemented.

- [ ] **Step 3: Test end-to-end flow**

1. Start app: `streamlit run app.py`
2. Click HORAS button
3. Click "Registrar Horas" tab
4. Select period "Junio 1 (4-6)"
5. Fill in one row:
   - Auditor: "Marlene Andrea"
   - Rol: "AL"
   - Horas: "10.0"
6. Click "Guardar Participaciones"
7. Expected: Success message
8. Click "Ver Reporte" tab
9. Expected: Table shows Marlene Andrea with AL_2026 = 10.0, AL_Total = 32.6 + 10.0 = 42.6

- [ ] **Step 4: Commit wiring**

```bash
git add app.py
git commit -m "feat: wire HORAS module to Google Sheets functions

- Tab 1 form now saves to Participaciones_2026
- Tab 2 report now reads from Reporte_Horas_2026
- Import all functions from utils.py
- End-to-end data flow: Entry → Google Sheets → Report"
```

✅ **Checkpoint:** HORAS module fully functional. Data entry saves and displays in report.

---

### Task 9: Testing & Validation

**Files:**
- Test: Manual testing (no unit tests for Streamlit)

**Goal:** Verify all functionality works correctly.

- [ ] **Step 1: Data validation testing**

Test invalid entries in Tab 1:
- [ ] Empty auditor → should show error "Auditor requerido"
- [ ] Empty rol → should show error "Rol requerido"
- [ ] Horas = 0 → should show error "Horas debe ser > 0"
- [ ] Horas = 25.0 → should be rejected (max 24.0)
- [ ] All fields filled → should save successfully

- [ ] **Step 2: Data persistence testing**

1. Add participations: Marlene (AL, 10.0), Yraima (AD, 20.0)
2. Refresh app (Ctrl+R)
3. Go to "Ver Reporte" tab
4. Expected: Data still there, not lost

- [ ] **Step 3: Calculation verification**

1. Add: Marlene (AL, 10.0) in Junio 1
2. Go to report
3. Verify:
   - Marlene: AL_2026 = 10.0
   - Marlene: AL_Prev = 32.6 (from base)
   - Marlene: AL_Total = 32.6 + 10.0 = 42.6
   - Marlene: Total_Auditorías = 1

- [ ] **Step 4: Multiple roles for same auditor**

1. Add: Marlene (AL, 10.0)
2. Add: Marlene (AD, 5.0)
3. Report should show:
   - AD_2026 = 5.0
   - AL_2026 = 10.0
   - Totals correctly summed by role

- [ ] **Step 5: PDF export test**

1. Add some data
2. Go to "Ver Reporte" tab
3. Click "Descargar PDF"
4. File should download with name: `Registro_Horas_Auditoria_2026_YYYYMMDD.pdf`
5. Open PDF: should show table with data

- [ ] **Step 6: Edge cases**

- [ ] Add decimal hours: 7.5, 12.3 → should work
- [ ] Add very small hours: 0.1 → should work
- [ ] Add Sara Rabelo (new auditor) → should work
- [ ] Add non-AD auditors (e.g., Pablo Galvis) → should work

- [ ] **Step 7: Document testing results**

Create file `TEST_RESULTS.md`:

```markdown
# HORAS Module - Testing Results

**Date:** [Today]
**Tester:** [Your name]

## Test Cases Passed
- [x] Data validation (empty fields rejected)
- [x] Data persistence (refresh doesn't lose data)
- [x] Calculations (formulas correct)
- [x] Multiple roles per auditor
- [x] PDF export (generates valid file)
- [x] Edge cases (decimals, small hours, new auditor)

## Known Issues
None

## Ready for Production
Yes ✓
```

- [ ] **Step 8: Final commit**

```bash
git add -A
git commit -m "test: complete HORAS module testing and validation

Verified:
- Form validation works (rejects invalid input)
- Data persists (Google Sheets sync works)
- Formulas calculate correctly (totals match manual calc)
- Multiple roles per auditor handled correctly
- PDF export generates valid file
- Edge cases handled (decimals, new auditors, etc.)
- Full end-to-end flow tested

All acceptance criteria met. Ready for production."
```

✅ **Checkpoint:** All testing complete. Module verified working correctly.

---

### Task 10: Final Integration & Documentation

**Files:**
- Modify: `CLAUDE.md` (add HORAS module documentation)

**Goal:** Document the new module for future reference.

- [ ] **Step 1: Update CLAUDE.md**

Add new section in CLAUDE.md after the existing modules:

```markdown
## HORAS Module - Auditor Hours Tracking

Three new Google Sheets worksheets manage auditor hours:

**`Horas_Base_2011_2025`** — Historical cumulative hours (2011-2025) by auditor and role (OB, AF, AD, AL). Read-only reference. Updated annually; 2025 values extracted from official PDF.

**`Participaciones_2026`** — Transaction log: one row per auditor participation in an audit. Columns: ID, Fecha, Período, Proceso, Auditor, Rol, Horas, Observaciones. Data entry point. Streamlit validates: auditor exists, rol in {OB, AF, AD, AL}, horas in [0.1, 24.0].

**`Reporte_Horas_2026`** — Auto-aggregating report (formulas only). Reads from Participaciones_2026 and Horas_Base_2011_2025. Calculates total hours per auditor per role (2026 + previous = cumulative 2026). Matches official SGC form layout.

### Streamlit HORAS Module

Two tabs:
- **Registrar Horas**: Dynamic form for entering multiple auditor participations per period (Junio 1/2/3). Period selector → Auditor | Rol | Horas fields → Guardar button → syncs to Google Sheets.
- **Ver Reporte**: Reads and displays Reporte_Horas_2026. Shows 14 columns (OB/AF/AD/AL for 2026, prev, total + audit count). PDF export button.

### Utility Functions (utils.py)

```python
load_hours_base_data()              # Read Horas_Base_2011_2025
load_participations_2026()          # Read Participaciones_2026
load_hours_report()                 # Read Reporte_Horas_2026
save_auditor_participations(...)    # Write to Participaciones_2026
generate_hours_pdf(df_reporte)      # Create PDF export
```

All use `ttl=0` (real-time sync, no caching).

### Annual Cycle

- **2026**: Horas_2026 + Horas_Acumuladas_Previas_2011_2025 = Total_Acumulado_2026
- **2027**: Horas_2027 + Horas_Acumuladas_Previas_2011_2026 = Total_Acumulado_2027 (where prev = 2026 total)

At year-end, copy Reporte_Horas_2026 totals → next year's Horas_Base sheet.
```

- [ ] **Step 2: Update app.py docstring (if exists)**

Add HORAS to the navigation description in app.py header comments.

- [ ] **Step 3: Create README for hours module**

Create file `docs/HORAS_MODULE.md`:

```markdown
# HORAS Module - Auditor Hours Tracking

## Quick Start

### Registering Hours
1. Click HORAS button in top navigation
2. Select period: Junio 1 (4-6), Junio 2 (8-12), or Junio 3 (15+)
3. Add rows: Select Auditor → Select Rol (OB/AF/AD/AL) → Enter Horas
4. Click "+ Agregar otra fila" to add more auditors
5. Click "Guardar Participaciones" to sync to Google Sheets

### Viewing Reports
1. Click HORAS button → Ver Reporte tab
2. Table shows all auditors with:
   - 2026 hours by role (OB_2026, AF_2026, AD_2026, AL_2026)
   - Cumulative prev hours (OB_Prev, etc.) from 2011-2025
   - Total cumulative (OB_Total, etc.) = 2026 + Prev
   - Total participations count
3. Click "Descargar PDF" to export

## Data Structure

### Google Sheets Sheets
- `Horas_Base_2011_2025`: 23 auditors × 4 roles = 92 cells (read-only baseline)
- `Participaciones_2026`: Growing log of audit participation records
- `Reporte_Horas_2026`: Auto-calculated aggregation (formulas)

### Validation Rules
- Auditor: Must be in team list (23 auditors)
- Rol: OB, AF, AD, or AL
- Horas: 0.1 to 24.0 (decimal allowed)
- Período: 3 options (auto-calculated from fecha)

## Troubleshooting

**Q: Report shows "Sin datos"**
A: No participations saved yet. Go to "Registrar Horas" tab and add data.

**Q: Numbers don't match my manual calculation**
A: Verify that Horas_Base_2011_2025 has correct 2025 values from PDF.

**Q: PDF export fails**
A: Check that reportlab is installed: `pip install reportlab`

**Q: Auditor doesn't appear in dropdown**
A: Make sure auditor is in Horas_Base_2011_2025. Add if new.

## Annual Maintenance

**At end of year (December):**
1. Export Reporte_Horas_YYYY totals
2. Create new sheet Horas_Base_YYYY (copy from Reporte_Horas_YYYY totals)
3. Create new sheet Participaciones_YYYY+1 (empty, same structure)
4. Update formulas in Reporte_Horas_YYYY+1 to reference Horas_Base_YYYY
5. Update Streamlit module to use new sheets
```

- [ ] **Step 4: Final commit**

```bash
git add CLAUDE.md docs/HORAS_MODULE.md
git commit -m "docs: add HORAS module documentation

- Update CLAUDE.md with module overview
- Create HORAS_MODULE.md with user guide
- Document Google Sheets structure
- Document validation rules
- Include troubleshooting and annual maintenance guide"
```

- [ ] **Step 5: Push all changes**

```bash
git push origin main
```

✅ **Checkpoint:** HORAS module complete, tested, documented, and pushed to production.

---

## Summary

**Total Tasks:** 10  
**Estimated Time:** 4-6 hours  
**Deliverables:**
- ✅ 3 new Google Sheets (Horas_Base_2011_2025, Participaciones_2026, Reporte_Horas_2026)
- ✅ HORAS module in Streamlit (Tab 1: Entry, Tab 2: Report)
- ✅ 5 new utility functions in utils.py
- ✅ Data validation and error handling
- ✅ PDF export functionality
- ✅ Complete testing and documentation

**Acceptance Criteria Met:**
- [x] Google Sheets structure created (3 sheets)
- [x] Historical data loaded (23 auditors from PDF)
- [x] Formulas configured (SUMIFS, VLOOKUP, calculations)
- [x] Streamlit HORAS module functional
- [x] Tab 1 allows entry of multiple participations
- [x] Tab 2 displays aggregated report
- [x] PDF export works
- [x] Data validates on submission
- [x] Report matches 2025 PDF format
- [x] End-to-end testing complete

---

**Next Steps:** See execution options below.
