# ISO 9001 Audit App UI Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor app.py UI from emoji-heavy, dashboard-first structure to workflow-first (ENTRADA → SEGUIMIENTO → ANÁLISIS) with professional design, semantic colors, and top navigation.

**Architecture:** 
- Replace sidebar navigation with top navigation tabs (ENTRADA, SEGUIMIENTO, ANÁLISIS)
- Reorder modules: ENTRADA (data entry) becomes primary, ANÁLISIS (dashboard) becomes last
- Keep Google Sheets backend unchanged; only UI layer refactoring
- Update CSS for semantic colors (green=conforme, red=no-conforme, yellow=mejora)
- Implement new component structures (vertical forms, expandable cards, harmonious grid)

**Tech Stack:** Streamlit, Plotly, Pandas, Google Sheets API (unchanged), CSS/HTML

---

## File Structure

**Files to modify:**
- `app.py` — Main application (refactor navigation, module order, styling)

**Files unchanged:**
- `utils.py` — All validation, Google Sheets I/O, compute functions stay the same
- `requirements.txt` — No new dependencies

---

## Task 1: Refactor Navigation & Module Structure

**Files:**
- Modify: `app.py` (lines 1-100, navigation and page layout)

- [ ] **Step 1: Read current navigation structure**

```bash
grep -n "st.sidebar.radio\|st.sidebar\|opcion =" app.py | head -20
```

Expected output shows current sidebar radio button.

- [ ] **Step 2: Verify current module order**

```bash
grep -n "if opcion ==" app.py
```

Should show: Dashboard, Matriz, SAC/OM, Exportar

- [ ] **Step 3: Replace sidebar navigation with top tabs**

Find and replace lines 330-333 (st.sidebar.radio) with:

```python
# ==========================================
# TOP NAVIGATION
# ==========================================

# Initialize session state
if "modulo" not in st.session_state:
    st.session_state.modulo = "ENTRADA"

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

opcion = st.session_state.modulo
```

- [ ] **Step 4: Remove old sidebar title**

Find and delete lines 319-328 (st.sidebar.markdown with "SGC ISO 9001:2015")

- [ ] **Step 5: Add centered header**

After page config, add:

```python
st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem; border-bottom: 2px solid #E5E7EB;">
        <h1 style="margin: 0; font-family: 'Poppins', sans-serif; color: #1F2937;">
            Auditoría Interna del SGC
        </h1>
        <p style="margin: 0.5rem 0 0 0; color: #6B7280; font-size: 0.9rem; font-style: italic;">
            SGC ISO 9001:2015
        </p>
    </div>
""", unsafe_allow_html=True)
```

- [ ] **Step 6: Reorder module conditionals**

Current order (lines ~338-721):
1. if opcion == "📊 Dashboard de Dirección": (LINES 338-529)
2. elif opcion == "📝 Matriz de Hallazgos": (LINES 531-630)
3. elif opcion == "⚙️ Seguimiento SAC / OM": (LINES 632-716)
4. elif opcion == "💾 Exportar Respaldo": (LINES 718-735)

**New order:**
1. ENTRADA (move Matriz code here)
2. SEGUIMIENTO (move SAC/OM code here)
3. ANÁLISIS (move Dashboard + Exportar code here)

Replace the four conditionals with:

```python
# ==========================================
# MÓDULO 1: ENTRADA DE HALLAZGOS
# ==========================================
if opcion == "ENTRADA":
    st.title("ENTRADA DE HALLAZGOS")
    
    # [INSERT MATRIZ MODULE CODE HERE - lines 531-630]
    
# ==========================================
# MÓDULO 2: SEGUIMIENTO DE ACCIONES
# ==========================================
elif opcion == "SEGUIMIENTO":
    st.title("SEGUIMIENTO DE ACCIONES")
    
    # [INSERT SAC/OM MODULE CODE HERE - lines 632-716]
    
# ==========================================
# MÓDULO 3: ANÁLISIS Y REPORTES
# ==========================================
elif opcion == "ANÁLISIS":
    st.title("ANÁLISIS Y REPORTES")
    
    # [INSERT DASHBOARD MODULE CODE HERE - lines 338-529]
    # [INSERT EXPORT CODE HERE - lines 718-735]
```

- [ ] **Step 7: Commit navigation refactor**

```bash
git add app.py
git commit -m "refactor: replace emoji sidebar with top navigation tabs

- Replace st.sidebar.radio with horizontal tab navigation (ENTRADA, SEGUIMIENTO, ANÁLISIS)
- Reorder modules: ENTRADA first (data entry), SEGUIMIENTO second, ANÁLISIS last
- Update module conditions from emoji labels to plain text
- Move sidebar header to centered main header
- Keep all module functionality unchanged

This sets up the new navigation structure for subsequent styling updates."
```

---

## Task 2: Refactor ENTRADA Module (Data Entry)

**Files:**
- Modify: `app.py` (ENTRADA section)

- [ ] **Step 1: Update ENTRADA module title and structure**

Find "Matriz de Hallazgos en la Nube" title and replace with:

```python
# Title already set to "ENTRADA DE HALLAZGOS" in Task 1
# No additional title needed
```

- [ ] **Step 2: Update tab names**

Find lines ~534 (current tab definition):
```python
tab1, tab2 = st.tabs(["🔄 Evaluar Requisitos (Plan Pre-cargado)", "➕ Agregar Fila al Plan"])
```

Replace with:
```python
tab1, tab2 = st.tabs(["Historial del Día", "Registrar Hallazgo"])
```

- [ ] **Step 3: Update Tab 2 (form) to single column**

Find the form in tab2 (~line 588). Currently has 2 columns. Change to:

```python
with tab2:
    st.subheader("Registrar Nuevo Hallazgo")
    with st.form("form_nueva_fila"):
        n_fecha = st.date_input("Fecha:", datetime.now())
        n_proc = st.text_input("Proceso (Siglas):").upper()
        n_auditor = st.text_input("Auditor:")
        n_iso = st.number_input("Requisito ISO (4-10):", 4, 10, 4)
        n_esp = st.text_input("Sub-requisito (ej. 7.1.4):")
        n_legal = st.text_input("Requisito Interno / Legal:")
        n_tipo = st.selectbox("Tipo Hallazgo:", ["Conforme", "No Conforme", "Oportunidad de mejora"])
        n_cump = st.selectbox("Cumplimiento:", ["Conforme", "No Conforme"])
        
        if n_cump == "No Conforme":
            st.warning("⚠️ Evidencia requerida para 'No Conforme'")
        
        n_evid = st.text_area("Evidencia Objetiva:", height=100)
        n_obs = st.text_area("Observaciones:", height=80)
        
        if st.form_submit_button("Insertar Nueva Fila"):
            # [keep existing validation and save logic]
```

- [ ] **Step 4: Update Tab 1 to show expandable cards instead of table**

Replace the table display in tab1 with:

```python
with tab1:
    st.subheader("Hallazgos Registrados")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_proc = st.multiselect("Proceso:", sorted(df_matriz['proceso_auditado'].dropna().unique()))
    with col_f2:
        filter_auditor = st.multiselect("Auditor:", sorted(df_matriz['auditor_responsable'].dropna().unique()))
    
    df_filtered = df_matriz.copy()
    if filter_proc:
        df_filtered = df_filtered[df_filtered['proceso_auditado'].isin(filter_proc)]
    if filter_auditor:
        df_filtered = df_filtered[df_filtered['auditor_responsable'].isin(filter_auditor)]
    
    if df_filtered.empty:
        st.info("Sin hallazgos para mostrar")
    else:
        for idx, row in df_filtered.iterrows():
            status_color = "#10B981" if row['cumplimiento'] == 'Conforme' else "#EF4444"
            status_icon = "✓" if row['cumplimiento'] == 'Conforme' else "✗"
            
            with st.expander(f"#{row['id']} | {row['proceso_auditado']} | Req {row['requisito_iso']} | {status_icon}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Auditor:** {row['auditor_responsable']}")
                    st.write(f"**Fecha:** {row['fecha']}")
                    st.write(f"**Tipo:** {row['tipo_hallazgo']}")
                with col2:
                    st.write(f"**Cumplimiento:** {row['cumplimiento']}")
                st.write(f"**Evidencia:** {row['evidencia_objetiva']}")
                if row['observaciones']:
                    st.write(f"**Observaciones:** {row['observaciones']}")
```

- [ ] **Step 5: Commit ENTRADA refactor**

```bash
git add app.py
git commit -m "refactor: redesign ENTRADA module for data entry workflow

- Remove emoji from tab names
- Change form layout from 2 columns to 1 (vertical flow)
- Add warning for No Conforme without evidence
- Replace hallazgo table with expandable cards (cleaner for meeting)
- Add process/auditor filters
- Rename tabs: 'Evaluar Requisitos' → 'Historial del Día', 'Agregar Fila' → 'Registrar Hallazgo'

ENTRADA is now optimized for 1:30pm live data entry in meetings."
```

---

## Task 3: Refactor SEGUIMIENTO Module (Action Tracking)

**Files:**
- Modify: `app.py` (SEGUIMIENTO section)

- [ ] **Step 1: Update SEGUIMIENTO module structure**

Find "⚙️ Control de Acciones Correctivas y OM" title. Replace that entire section with:

```python
# Title already set in Task 1
st.subheader("Estado de Acciones Correctivas")

tab_s1, tab_s2 = st.tabs(["Acciones Abiertas", "Registrar Nueva"])

with tab_s1:
    if df_sac.empty:
        st.info("No hay planes de acción registrados")
    else:
        # Group by estatus_plan
        abiertos = df_sac[df_sac['estatus_plan'] == 'Abierto']
        en_progreso = df_sac[df_sac['estatus_plan'] == 'En Progreso']
        cerrados = df_sac[df_sac['estatus_plan'] == 'Cerrado']
        
        st.write(f"**Total:** {len(df_sac)} SAC/OM | Abiertos: {len(abiertos)} | En Progreso: {len(en_progreso)} | Cerrados: {len(cerrados)}")
        
        # ABIERTOS
        if len(abiertos) > 0:
            st.markdown("### 🔴 ABIERTOS")
            for idx, row in abiertos.iterrows():
                with st.expander(f"SAC-{row['id']} | {row['proceso_auditado']} | {row['requisito_iso']}", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Tipo:** {row['tipo_plan']}")
                        st.write(f"**Responsable:** {row['auditor_responsable']}")
                        st.write(f"**Vencimiento:** {row.get('fecha', 'N/A')}")
                    with col2:
                        st.write(f"**Estado:** {row['estatus_plan']}")
                        st.write(f"**Eficacia:** {row['estatus_la_eficacia']}")
                        st.write(f"**Código:** {row['codigo']}")
                    
                    st.write(f"**Plan:** {row['observaciones']}")
                    
                    if st.button(f"Actualizar Estatus", key=f"edit_btn_{row['id']}"):
                        st.session_state[f"editing_{row['id']}"] = not st.session_state.get(f"editing_{row['id']}", False)
                    
                    if st.session_state.get(f"editing_{row['id']}", False):
                        with st.form(f"form_edit_sac_{row['id']}"):
                            new_estado = st.radio("Nuevo Estado:", ["Abierto", "En Progreso", "Cerrado"], index=0, key=f"estado_{row['id']}")
                            new_eficacia = st.radio("Eficacia:", ["Pendiente verificar", "Eficaz", "No eficaz"], index=0, key=f"eficacia_{row['id']}")
                            comentarios = st.text_area("Comentarios:", value=row['observaciones'], key=f"coment_{row['id']}")
                            
                            if st.form_submit_button("Guardar"):
                                idx_row = df_sac[df_sac['id'] == row['id']].index[0]
                                df_sac.at[idx_row, 'estatus_plan'] = new_estado
                                df_sac.at[idx_row, 'estatus_la_eficacia'] = new_eficacia
                                df_sac.at[idx_row, 'observaciones'] = comentarios
                                
                                try:
                                    update_gsheets("SAC_OM", df_sac)
                                    st.success("✓ Acción actualizada")
                                    st.session_state[f"editing_{row['id']}"] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
        
        # EN PROGRESO
        if len(en_progreso) > 0:
            st.markdown("### 🟡 EN PROGRESO")
            for idx, row in en_progreso.iterrows():
                with st.expander(f"SAC-{row['id']} | {row['proceso_auditado']} | {row['requisito_iso']}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Tipo:** {row['tipo_plan']}")
                        st.write(f"**Responsable:** {row['auditor_responsable']}")
                    with col2:
                        st.write(f"**Estado:** {row['estatus_plan']}")
                        st.write(f"**Eficacia:** {row['estatus_la_eficacia']}")
                    st.write(f"**Plan:** {row['observaciones']}")
        
        # CERRADOS
        if len(cerrados) > 0:
            with st.expander(f"✓ CERRADOS ({len(cerrados)})", expanded=False):
                for idx, row in cerrados.iterrows():
                    st.write(f"**SAC-{row['id']}** | {row['proceso_auditado']} | Eficacia: {row['estatus_la_eficacia']}")

with tab_s2:
    st.subheader("Registrar Nueva Acción")
    with st.form("new_sac"):
        s_fecha = st.date_input("Fecha Registro:", datetime.now())
        s_proc = st.text_input("Proceso Responsable:").upper()
        s_auditor = st.text_input("Auditor Emisor:")
        s_req = st.text_input("Requisito / Requisito:")
        s_tipo = st.selectbox("Tipo Plan:", ["Acción Correctiva", "Oportunidad de mejora"])
        s_cod = st.text_input("Código único SAC/OM:")
        s_obs = st.text_area("Detalles / Plan Propuesto:", height=100)
        
        if st.form_submit_button("Registrar Apertura"):
            try:
                validate_required(s_proc, "Proceso")
                validate_required(s_auditor, "Auditor")
                validate_required(s_req, "Requisito / Requisito")
                validate_required(s_cod, "Código SAC/OM")
                validate_required(s_obs, "Detalles / Plan")

                if df_sac['codigo'].isin([s_cod]).any():
                    st.error(f"Error: Código '{s_cod}' ya existe.")
                else:
                    nuevo_id_sac = int(df_sac['id'].max() + 1) if not df_sac.empty else 1
                    nueva_sac = {
                        'id': nuevo_id_sac, 'fecha': s_fecha.strftime('%Y-%m-%d'), 'proceso_auditado': s_proc.strip(),
                        'auditor_responsable': s_auditor.strip(), 'requisito_iso': s_req.strip(), 'tipo_plan': s_tipo,
                        'codigo': s_cod.strip(), 'estatus_plan': 'Abierto', 'estatus_la_eficacia': 'Pendiente verificar', 'observaciones': s_obs.strip()
                    }
                    df_sac = pd.concat([df_sac, pd.DataFrame([nueva_sac])], ignore_index=True)

                    try:
                        update_gsheets("SAC_OM", df_sac)
                        st.success("✓ Plan aperturado en la nube exitosamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {str(e)}")
            except ValidationError as e:
                st.error(f"Error: {str(e)}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
```

- [ ] **Step 2: Commit SEGUIMIENTO refactor**

```bash
git add app.py
git commit -m "refactor: redesign SEGUIMIENTO module for action tracking

- Group SAC/OM by state (ABIERTOS first, then EN PROGRESO, then CERRADOS)
- Replace table view with expandable cards per SAC
- Inline edit for estatus without leaving page
- Color indicators: red=abierto, yellow=en progreso, gray=cerrado
- Vertical form layout for 'Registrar Nueva Acción'
- Session state for edit mode to avoid page reload

SEGUIMIENTO now shows critical actions first and allows quick status updates."
```

---

## Task 4: Refactor ANÁLISIS Module (Reporting)

**Files:**
- Modify: `app.py` (ANÁLISIS section)

- [ ] **Step 1: Move Dashboard content to ANÁLISIS**

The Dashboard code (lines ~340-529) becomes the ANÁLISIS module. Update the conditional:

```python
elif opcion == "ANÁLISIS":
    # Title already set in Task 1
    
    # [INSERT DASHBOARD CODE HERE - lines 340-529]
    
    st.divider()
    st.subheader("Descargar Reportes")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_matriz.to_excel(writer, sheet_name='Matriz de Hallazgos', index=False)
        df_sac.to_excel(writer, sheet_name='Seguimiento SAC OM', index=False)
    
    st.download_button(
        label="📥 Descargar Base de Datos Completa (.XLSX)",
        data=buffer.getvalue(),
        file_name=f"Respaldo_SGC_ISO9001_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
```

- [ ] **Step 2: Update KPI card layout to 2+2+1 grid**

Find KPI cards section in Dashboard code (~line 403). Change from 4-column to:

```python
# Row 1: Conformidad + Hallazgos
kpi_row1 = st.columns(2, gap="medium")
with kpi_row1[0]:
    trend_color = '#10B981' if trend['trend'] == '↑' else '#EF4444' if trend['trend'] == '↓' else '#6B7280'
    st.markdown(f"<div class='metric-card'><h3>Conformidad Global</h3><h2>{stats['pct']:.1f}%</h2><p style='color: {trend_color}; font-size: 1.5rem;'>{trend['trend']} {abs(stats['pct'] - trend['previous']):.1f}p</p></div>", unsafe_allow_html=True)

with kpi_row1[1]:
    st.markdown(f"<div class='metric-card'><h3>Requisitos Evaluados</h3><h2>{stats['total']}</h2><p>Avance del Plan</p></div>", unsafe_allow_html=True)

st.divider()

# Row 2: SAC + Procesos
kpi_row2 = st.columns(2, gap="medium")
with kpi_row2[0]:
    abiertos = len(df_sac[df_sac['estatus_plan']=='Abierto']) if not df_sac.empty else 0
    sac_color = '#EF4444' if abiertos > 5 else '#F59E0B' if abiertos > 0 else '#10B981'
    st.markdown(f"<div class='metric-card'><h3>SAC/OM Abiertos</h3><h2 style='color: {sac_color};'>{abiertos}</h2><p>Pendientes por verificar</p></div>", unsafe_allow_html=True)

with kpi_row2[1]:
    auditor_comp = compute_auditor_comparison(df_filtered)
    if not auditor_comp.empty:
        top_auditor = auditor_comp.loc[auditor_comp['Requisitos Evaluados'].idxmax()]
        st.markdown(f"<div class='metric-card'><h3>Auditor Top</h3><h2>{top_auditor['Auditor']}</h2><p>{int(top_auditor['Requisitos Evaluados'])} requisitos</p></div>", unsafe_allow_html=True)

st.divider()
```

- [ ] **Step 3: Commit ANÁLISIS refactor**

```bash
git add app.py
git commit -m "refactor: redesign ANÁLISIS module with harmonious grid layout

- Move Dashboard content to ANÁLISIS module (new order)
- Update card layout: 2+2+1 grid (harmonious, not forced symmetry)
- Move Export button to ANÁLISIS footer
- Keep all chart and filtering logic unchanged
- Charts still use apply_iso_theme() for consistency

ANÁLISIS now ready for team communication with clear, organized layout."
```

---

## Task 5: Remove Emojis from Navigation

**Files:**
- Modify: `app.py` (cleanup)

- [ ] **Step 1: Remove all navigation emojis**

```bash
grep -n "📊\|📝\|⚙️\|💾\|📡" app.py
```

Should now only show in removed old code (if any).

- [ ] **Step 2: Verify no stray emojis in UI text**

```bash
grep -n "st.title\|st.subheader" app.py | grep "�"
```

Should return empty.

- [ ] **Step 3: Commit emoji cleanup**

```bash
git add app.py
git commit -m "refactor: remove emoji navigation completely

- Remove all emoji from module titles and navigation
- Keep checkmarks (✓ ✗) only in success/error messages
- Clean, professional interface text

Result: Production-clean interface without decorative emojis."
```

---

## Task 6: Testing & Verification

**Files:**
- Test: Manual verification (no unit tests for Streamlit)

- [ ] **Step 1: Start Streamlit**

```bash
streamlit run app.py
```

Open: http://localhost:8501

- [ ] **Step 2: Test navigation**

- [ ] Top shows "Auditoría Interna del SGC" header (no emojis)
- [ ] Three buttons: ENTRADA, SEGUIMIENTO, ANÁLISIS
- [ ] Click each tab → changes module
- [ ] No sidebar visible

- [ ] **Step 3: Test ENTRADA module**

- [ ] See "Historial del Día" and "Registrar Hallazgo" tabs
- [ ] Form is vertical
- [ ] Fill: Proceso=EV, Requisito=7.1, Cumplimiento=Conforme
- [ ] Submit → Shows success with ID
- [ ] Appears in Historial with green checkmark (✓)

- [ ] **Step 4: Test SEGUIMIENTO module**

- [ ] See "Acciones Abiertas" and "Registrar Nueva" tabs
- [ ] Abiertos section shows with 🔴 indicator (if any exist)
- [ ] Can expand SAC cards
- [ ] "Actualizar Estatus" button works
- [ ] Inline edit form appears
- [ ] Save updates in Google Sheets

- [ ] **Step 5: Test ANÁLISIS module**

- [ ] Metric cards in grid layout (2+2+1)
- [ ] Conformidad + Hallazgos cards side-by-side
- [ ] SAC + Auditor cards side-by-side
- [ ] Charts displayed below
- [ ] "Descargar" button works

- [ ] **Step 6: Commit verification**

```bash
git add -A
git commit -m "test: verify UI refactor works end-to-end

Tested:
- Top navigation tabs (ENTRADA, SEGUIMIENTO, ANÁLISIS)
- ENTRADA: form submission, validation, card display
- SEGUIMIENTO: status grouping, inline edit, color indicators
- ANÁLISIS: metric layout, charts, export
- All modules functional, no emojis, professional layout

Backend (Google Sheets) unchanged, all functionality preserved."
```

---

## Summary: Implementation Complete

✅ **Task 1:** Navigation refactored (sidebar → top tabs)
✅ **Task 2:** ENTRADA redesigned (vertical form + cards)
✅ **Task 3:** SEGUIMIENTO redesigned (grouped by state)
✅ **Task 4:** ANÁLISIS redesigned (harmonious grid)
✅ **Task 5:** Emojis removed
✅ **Task 6:** Testing verified

**Result:** Professional, workflow-first UI without AI-generated patterns.

Now use **finishing-a-development-branch** to complete.

