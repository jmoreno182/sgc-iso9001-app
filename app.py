import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

from utils import (
    ValidationError,
    validate_required,
    validate_date,
    load_gsheets_data,
    update_gsheets,
    compute_conformidad_stats,
    compute_process_stats,
    compute_requirement_stats,
    compute_auditor_stats,
    compute_conformidad_trend,
    compute_auditor_comparison,
)

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILO AZUL
# ==========================================
st.set_page_config(
    page_title="Gestión SGC - Google Sheets Cloud",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
    <style>
        :root {
            --primary: #1F2937;
            --accent: #3B82F6;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
            --light-bg: #F9FAFB;
            --border: #E5E7EB;
        }

        * {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', sans-serif;
        }

        .main {
            background-color: #FFFFFF;
            padding: 0;
        }

        h1, h2, h3 {
            color: #1F2937;
            font-weight: 700;
            letter-spacing: -0.5px;
        }

        h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        h2 { font-size: 1.875rem; margin-top: 1.5rem; margin-bottom: 1rem; }
        h3 { font-size: 1.25rem; margin-bottom: 0.75rem; }

        .stButton>button {
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2);
        }

        .stButton>button:hover {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
            transform: translateY(-2px);
            box-shadow: 0 8px 12px rgba(59, 130, 246, 0.3);
        }

        .stButton>button:active {
            transform: translateY(0);
        }

        .metric-card {
            background: linear-gradient(135deg, #FFFFFF 0%, #F3F4F6 100%);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid #E5E7EB;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }

        .metric-card:hover {
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            transform: translateY(-4px);
        }

        .metric-card h3 {
            color: #6B7280;
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.75rem;
        }

        .metric-card h2 {
            color: #1F2937;
            font-size: 2.5rem;
            margin: 0 0 0.5rem 0;
        }

        .metric-card p {
            color: #9CA3AF;
            font-size: 0.875rem;
            margin: 0;
        }

        hr { border-color: #E5E7EB; margin: 2rem 0; }

        [data-testid="stExpander"] {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
        }

        .stDataFrame {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            overflow: hidden;
        }

        .stInfo, .stWarning, .stError {
            border-radius: 8px;
            padding: 1rem;
        }

        .stMarkdown {
            color: #374151;
            line-height: 1.6;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CONEXIÓN DIRECTA A GOOGLE SHEETS
# ==========================================
# Nota: La URL del spreadsheet se configura en los Secrets de Streamlit

if "GOOGLE_SERVICE_ACCOUNT_INFO" not in st.secrets:
    st.warning("⚠️ **Aplicación en modo configuración**")
    st.info("""
    ### Pasos para activar la aplicación:

    1. **Ir a Streamlit Cloud Dashboard**
       - https://share.streamlit.io/
       - Selecciona tu app "sgc-iso9001-app"

    2. **Configurar Secrets**
       - Click en "..." → "Edit secrets"
       - Agrega GOOGLE_SERVICE_ACCOUNT_INFO con tus credenciales

    3. **Habilitar Google Sheets API**
       - https://console.cloud.google.com/apis/api/sheets.googleapis.com/overview

    4. **Recargar página** (Ctrl+F5)
    """)
    st.stop()

st.write("📡 Inicializando conexión...")
try:
    df_matriz, df_sac = load_gsheets_data(max_retries=3)
    st.write("✓ Conexión exitosa")
except Exception as e:
    st.error(f"❌ Error al cargar datos de Google Sheets:")
    st.error(str(e))
    st.info("**Soluciones:**\n1. Verifica conexión a internet\n2. Revisa `.streamlit/secrets.toml` tiene URL válida\n3. Verifica permisos en Google Sheets")
    st.stop()

# ==========================================
# MENÚ LATERAL DE NAVEGACIÓN
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/google-sheets.png", width=70)
st.sidebar.title("SGC ISO 9001:2015")
st.sidebar.markdown("*Control Sincronizado en la Nube*")
st.sidebar.write("---")

opcion = st.sidebar.radio(
    "Seleccione un Módulo:",
    ["📊 Dashboard de Dirección", "📝 Matriz de Hallazgos", "⚙️ Seguimiento SAC / OM", "💾 Exportar Respaldo"]
)

# ==========================================
# MÓDULO 1: DASHBOARD DE DIRECCIÓN
# ==========================================
if opcion == "📊 Dashboard de Dirección":
    st.title("📊 Dashboard")
    st.markdown("Resultados calculados dinámicamente desde el Google Sheet institucional.")

    # Filtros interactivos
    st.write("**🔍 Filtros**")
    filter_cols = st.columns([2, 2, 2])

    with filter_cols[0]:
        auditor_filter = st.multiselect(
            "Auditor",
            options=sorted(df_matriz['auditor_responsable'].dropna().unique()),
            default=None,
            help="Deja vacío para ver todos"
        )

    with filter_cols[1]:
        proceso_filter = st.multiselect(
            "Proceso",
            options=sorted(df_matriz['proceso_auditado'].dropna().unique()),
            default=None,
            help="Deja vacío para ver todos"
        )

    with filter_cols[2]:
        # Parse fechas safely
        try:
            df_fechas = pd.to_datetime(df_matriz['fecha'], errors='coerce').dropna()
            fecha_min = df_fechas.min().date() if not df_fechas.empty else datetime.now().date()
            fecha_max = df_fechas.max().date() if not df_fechas.empty else datetime.now().date()
        except:
            fecha_min = datetime.now().date()
            fecha_max = datetime.now().date()

        fecha_range = st.date_input(
            "Rango de Fecha",
            value=(fecha_min, fecha_max),
            help="Selecciona rango de auditoría"
        )

    # Aplicar filtros
    df_filtered = df_matriz.copy()
    if auditor_filter:
        df_filtered = df_filtered[df_filtered['auditor_responsable'].isin(auditor_filter)]
    if proceso_filter:
        df_filtered = df_filtered[df_filtered['proceso_auditado'].isin(proceso_filter)]

    try:
        df_filtered['fecha'] = pd.to_datetime(df_filtered['fecha'])
        if isinstance(fecha_range, tuple) and len(fecha_range) == 2:
            df_filtered = df_filtered[(df_filtered['fecha'] >= pd.Timestamp(fecha_range[0])) &
                                     (df_filtered['fecha'] <= pd.Timestamp(fecha_range[1]))]
    except:
        pass

    st.write("---")

    # Usar df_filtered en lugar de df_matriz para cálculos
    stats = compute_conformidad_stats(df_filtered)
    trend = compute_conformidad_trend(df_filtered)

    if stats['total'] == 0:
        st.info("💡 La matriz en la nube no tiene filas evaluadas aún. Proceda al módulo 'Matriz de Hallazgos' para calificar requisitos.")
    else:
        # KPIs mejorados con trending
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            trend_color = '#10B981' if trend['trend'] == '↑' else '#EF4444' if trend['trend'] == '↓' else '#6B7280'
            st.markdown(f"<div class='metric-card'><h3>Conformidad Global</h3><h2>{stats['pct']:.1f}%</h2><p style='color: {trend_color}; font-size: 1.5rem;'>{trend['trend']} {abs(stats['pct'] - trend['previous']):.1f}p</p></div>", unsafe_allow_html=True)
        with k2:
            st.markdown(f"<div class='metric-card'><h3>Requisitos Evaluados</h3><h2>{stats['total']}</h2><p>Avance del Plan</p></div>", unsafe_allow_html=True)
        with k3:
            abiertos = len(df_sac[df_sac['estatus_plan']=='Abierto']) if not df_sac.empty else 0
            sac_color = '#EF4444' if abiertos > 5 else '#F59E0B' if abiertos > 0 else '#10B981'
            st.markdown(f"<div class='metric-card'><h3>SAC/OM Abiertos</h3><h2 style='color: {sac_color};'>{abiertos}</h2><p>Pendientes por verificar</p></div>", unsafe_allow_html=True)
        with k4:
            # Auditor con más carga
            auditor_comp = compute_auditor_comparison(df_filtered)
            if not auditor_comp.empty:
                top_auditor = auditor_comp.loc[auditor_comp['Requisitos Evaluados'].idxmax()]
                st.markdown(f"<div class='metric-card'><h3>Auditor Top</h3><h2>{top_auditor['Auditor']}</h2><p>{int(top_auditor['Requisitos Evaluados'])} requisitos</p></div>", unsafe_allow_html=True)

        st.write("---")

        # Búsqueda rápida
        with st.expander("🔍 Búsqueda Rápida", expanded=False):
            search_term = st.text_input("Buscar por auditor, proceso, requisito:", placeholder="ej: Carlos, IT, 7.1")
            if search_term:
                df_search = df_filtered[
                    (df_filtered['auditor_responsable'].str.contains(search_term, case=False, na=False)) |
                    (df_filtered['proceso_auditado'].str.contains(search_term, case=False, na=False)) |
                    (df_filtered['requisito_iso'].astype(str).str.contains(search_term, case=False, na=False))
                ]
                if not df_search.empty:
                    st.write(f"**{len(df_search)} resultados encontrados**")
                    st.dataframe(df_search[['auditor_responsable', 'proceso_auditado', 'requisito_iso', 'cumplimiento']], use_container_width=True, hide_index=True)
                else:
                    st.info("Sin resultados")

        st.write("---")

        st.subheader("1. Grado de Conformidad por Proceso Auditado")
        proc_stats = compute_process_stats(df_filtered)
        
        fig_proc = px.bar(proc_stats, x='proceso_auditado', y='Conformidad', color_discrete_sequence=['#1E3A8A'], text_auto='.1f')
        fig_proc.add_hline(y=100, line_dash="dash", line_color="#EF4444", annotation_text="Meta SGC")
        fig_proc.update_layout(yaxis_range=[0, 110], plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_proc, use_container_width=True)
        
        # --- FILA PARA GRÁFICOS 2 Y 3 ---
        col_izq, col_der = st.columns(2)
        with col_izq:
            st.subheader("2. Madurez del SGC por Requisito ISO 9001")
            req_stats = compute_requirement_stats(df_filtered)
            fig_req = px.bar(req_stats, x='requisito_iso', y='Conformidad', color_discrete_sequence=['#3B82F6'], text_auto='.1f')
            fig_req.update_layout(yaxis_range=[0, 110], plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_req, use_container_width=True)
            
        with col_der:
            st.subheader("3. Distribución de Estatus de Acciones (SAC / OM)")
            if not df_sac.empty and 'tipo_plan' in df_sac.columns:
                fig_sac = px.histogram(
                    df_sac, x='tipo_plan', color='estatus_plan', barmode='group',
                    color_discrete_map={'Cerrado': '#10B981', 'Abierto': '#1E3A8A', 'Pendiente verificar': '#F59E0B'}
                )
                fig_sac.update_layout(plot_bgcolor='rgba(0,0,0,0)', yaxis_title='Cantidad de Acciones')
                st.plotly_chart(fig_sac, use_container_width=True)
            else:
                st.info("Sin registros en la tabla SAC_OM para graficar.")

        st.write("---")

        st.subheader("4. Detalle de Procesos Auditados por Auditor")
        auditor_detail = compute_auditor_stats(df_filtered)
        if not auditor_detail.empty:
            # Count unique processes per auditor
            auditor_count = auditor_detail.groupby('auditor_responsable').size().reset_index(name='Total Procesos Únicos')

            # Bar chart of unique process count
            fig_auditor = px.bar(auditor_count, x='auditor_responsable', y='Total Procesos Únicos',
                                color_discrete_sequence=['#8B5CF6'], text_auto='d')
            fig_auditor.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_title='Auditor',
                                     yaxis_title='Procesos Únicos Auditados')
            st.plotly_chart(fig_auditor, use_container_width=True)

            # Grouped detail table by auditor
            st.write("**Detalle: Procesos por Auditor**")

            for auditor in sorted(auditor_detail['auditor_responsable'].unique()):
                auditor_rows = auditor_detail[auditor_detail['auditor_responsable'] == auditor][
                    ['proceso_auditado', 'fecha']
                ].reset_index(drop=True)

                with st.expander(f"📋 {auditor} ({len(auditor_rows)} procesos)", expanded=True):
                    st.dataframe(
                        auditor_rows.rename(columns={
                            'proceso_auditado': 'Proceso',
                            'fecha': 'Fecha'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )

            # Comparativas auditor vs auditor
            st.write("---")
            st.subheader("5. Comparativa: Productividad y Conformidad por Auditor")
            auditor_comp = compute_auditor_comparison(df_filtered)
            if not auditor_comp.empty:
                # Tabla comparativa
                st.write("**Tabla Comparativa de Auditores**")
                auditor_comp_display = auditor_comp.sort_values('Requisitos Evaluados', ascending=False)
                st.dataframe(auditor_comp_display, use_container_width=True, hide_index=True)

                # Gráfico comparativo
                fig_comp = px.scatter(auditor_comp, x='Requisitos Evaluados', y='Conformidad',
                                     size='Requisitos Evaluados', text='Auditor',
                                     color_discrete_sequence=['#3B82F6'],
                                     labels={'Requisitos Evaluados': 'Productividad',
                                            'Conformidad': 'Conformidad (%)'})
                fig_comp.update_layout(plot_bgcolor='rgba(0,0,0,0)', height=400)
                st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("Sin datos de auditores para graficar.")

# ==========================================
# MÓDULO 2: MATRIZ DE HALLAZGOS (CRUD)
# ==========================================
elif opcion == "📝 Matriz de Hallazgos":
    st.title("📝 Matriz de Hallazgos en la Nube")
    
    tab1, tab2 = st.tabs(["🔄 Evaluar Requisitos (Plan Pre-cargado)", "➕ Agregar Fila al Plan"])
    
    with tab1:
        procesos_disponibles = df_matriz['proceso_auditado'].dropna().unique().tolist()

        if not procesos_disponibles:
            st.warning("⚠️ Sin procesos cargados. Añade filas en la pestaña 'Agregar Fila'.")
        else:
            proc_sel = st.selectbox("Seleccione el proceso en evaluación:", procesos_disponibles)

            df_proc = df_matriz[df_matriz['proceso_auditado'] == proc_sel]
            if df_proc.empty:
                st.error("❌ No hay requisitos para este proceso.")
            else:
                st.dataframe(df_proc[['id', 'requisito_iso', 'requisito_especifico', 'tipo_hallazgo', 'cumplimiento', 'observaciones']], use_container_width=True, hide_index=True)

                id_sel = st.selectbox("ID del requisito a calificar:", df_proc['id'].tolist())
                idx_row = df_matriz[df_matriz['id'] == id_sel].index[0]
                fila_editar = df_matriz.loc[idx_row]

                with st.form(key=f"form_matriz_{id_sel}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.info(f"**Requisito ISO:** {fila_editar['requisito_iso']} | **Detalle:** {fila_editar['requisito_especifico']}")
                        tipo_h = st.selectbox("Tipo de Hallazgo:", ["Conforme", "No Conforme", "Oportunidad de mejora"],
                                             index=0 if fila_editar['tipo_hallazgo']=='Conforme' else 1 if fila_editar['tipo_hallazgo']=='No Conforme' else 2)
                    with c2:
                        cump = st.selectbox("Cumplimiento:", ["Conforme", "No Conforme"],
                                           index=0 if fila_editar['cumplimiento']=='Conforme' else 1)

                    evid = st.text_area("Evidencia Objetiva hallada:", value=str(fila_editar['evidencia_objetiva'] or ''))
                    obs = st.text_area("Observaciones técnicas:", value=str(fila_editar['observaciones'] or ''))

                    if st.form_submit_button("Sincronizar con Google Sheets"):
                        try:
                            if cump == "No Conforme" and not evid.strip():
                                st.error("❌ Evidencia requerida cuando cumplimiento es 'No Conforme'")
                            else:
                                df_matriz.at[idx_row, 'tipo_hallazgo'] = tipo_h
                                df_matriz.at[idx_row, 'cumplimiento'] = cump
                                df_matriz.at[idx_row, 'evidencia_objetiva'] = evid
                                df_matriz.at[idx_row, 'observaciones'] = obs

                                try:
                                    update_gsheets("Matriz", df_matriz)
                                    st.success("✓ Datos sincronizados en la nube!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error al sincronizar: {str(e)}")
                        except Exception as e:
                            st.error(f"❌ Error validación: {str(e)}")

    with tab2:
        st.subheader("Incorporar un Requisito Adicional sobre la marcha")
        with st.form("form_nueva_fila"):
            col1, col2 = st.columns(2)
            with col1:
                n_fecha = st.date_input("Fecha:", datetime.now())
                n_proc = st.text_input("Proceso (Siglas):").upper()
                n_auditor = st.text_input("Auditor:")
                n_iso = st.number_input("Requisito ISO (4-10):", 4, 10, 4)
            with col2:
                n_esp = st.text_input("Sub-requisito (ej. 7.1.4):")
                n_legal = st.text_input("Requisito Interno / Legal:")
                n_tipo = st.selectbox("Tipo Hallazgo:", ["Conforme", "No Conforme", "Oportunidad de mejora"])
                n_cump = st.selectbox("Cumplimiento:", ["Conforme", "No Conforme"])
                
            n_evid = st.text_area("Evidencia:")
            n_obs = st.text_area("Observaciones:")
            
            if st.form_submit_button("Insertar Nueva Fila"):
                try:
                    validate_required(n_proc, "Proceso")
                    validate_required(n_auditor, "Auditor")
                    validate_required(n_esp, "Sub-requisito")
                    if n_cump == "No Conforme":
                        validate_required(n_evid, "Evidencia (requerida si No Conforme)")

                    nuevo_id = int(df_matriz['id'].max() + 1) if not df_matriz.empty else 1
                    nueva_fila = {
                        'id': nuevo_id, 'fecha': n_fecha.strftime('%Y-%m-%d'), 'proceso_auditado': n_proc.strip(),
                        'auditor_responsable': n_auditor.strip(), 'requisito_iso': n_iso, 'requisito_especifico': n_esp.strip(),
                        'requisito_interno_legal': n_legal.strip(), 'tipo_hallazgo': n_tipo, 'cumplimiento': n_cump,
                        'evidencia_objetiva': n_evid.strip(), 'observaciones': n_obs.strip()
                    }
                    df_matriz = pd.concat([df_matriz, pd.DataFrame([nueva_fila])], ignore_index=True)

                    try:
                        update_gsheets("Matriz", df_matriz)
                        st.success("✓ Fila añadida al Google Sheet.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al guardar: {str(e)}")
                except ValidationError as e:
                    st.error(f"❌ {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ==========================================
# MÓDULO 3: SEGUIMIENTO SAC / OM (CRUD)
# ==========================================
elif opcion == "⚙️ Seguimiento SAC / OM":
    st.title("⚙️ Control de Acciones Correctivas y OM")
    
    tab_s1, tab_s2 = st.tabs(["📋 Listado y Cierre Eficacia", "➕ Registrar Apertura"])
    
    with tab_s1:
        if not df_sac.empty:
            st.dataframe(df_sac, use_container_width=True, hide_index=True)
            
            id_sac = st.selectbox("Seleccione ID del Plan para actualizar:", df_sac['id'].tolist())
            idx_sac = df_sac[df_sac['id'] == id_sac].index[0]
            fila_sac = df_sac.loc[idx_sac]
            
            with st.form("form_edit_sac"):
                st.write(f"**Código de Acción:** {fila_sac['codigo']} | **Proceso:** {fila_sac['proceso_auditado']}")
                e_plan = st.selectbox("Estatus del Plan:", ["Abierto", "Cerrado"], index=0 if fila_sac['estatus_plan']=='Abierto' else 1)
                e_efic = st.selectbox("Estatus de la Eficacia:", ["Pendiente verificar", "Eficaz", "No eficaz"], 
                                      index=0 if fila_sac['estatus_la_eficacia']=='Pendiente verificar' else 1 if fila_sac['estatus_la_eficacia']=='Eficaz' else 2)
                e_obs = st.text_area("Comentarios de Verificación:", value=str(fila_sac['observaciones'] or ''))
                
                if st.form_submit_button("Actualizar Estatus en la Nube"):
                    try:
                        if e_plan == "Cerrado" and e_efic == "Pendiente verificar":
                            st.error("❌ No puede cerrar plan con eficacia 'Pendiente verificar'")
                        else:
                            df_sac.at[idx_sac, 'estatus_plan'] = e_plan
                            df_sac.at[idx_sac, 'estatus_la_eficacia'] = e_efic
                            df_sac.at[idx_sac, 'observaciones'] = e_obs.strip()
                            try:
                                update_gsheets("SAC_OM", df_sac)
                                st.success("✓ Plan actualizado en Google Sheets.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al guardar: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.info("No hay planes de acción registrados en este momento.")
            
    with tab_s2:
        st.subheader("Dar de alta un nuevo Plan de Acción")
        with st.form("new_sac"):
            cx1, cx2 = st.columns(2)
            with cx1:
                s_fecha = st.date_input("Fecha Registro:", datetime.now())
                s_proc = st.text_input("Proceso Responsable:").upper()
                s_auditor = st.text_input("Auditor Emisor:")
            with cx2:
                s_req = st.text_input("Requisito / Requisito:")
                s_tipo = st.selectbox("Tipo Plan:", ["Acción Correctiva", "Oportunidad de mejora"])
                s_cod = st.text_input("Código único SAC/OM:")
            s_obs = st.text_area("Detalles / Plan Propuesto:")
            
            if st.form_submit_button("Registrar Apertura"):
                try:
                    validate_required(s_proc, "Proceso")
                    validate_required(s_auditor, "Auditor")
                    validate_required(s_req, "Requisito / Requisito")
                    validate_required(s_cod, "Código SAC/OM")
                    validate_required(s_obs, "Detalles / Plan")

                    if df_sac['codigo'].isin([s_cod]).any():
                        st.error(f"❌ Código '{s_cod}' ya existe. Use código único.")
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
                            st.error(f"❌ Error al guardar: {str(e)}")
                except ValidationError as e:
                    st.error(f"❌ {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ==========================================
# MÓDULO 4: EXPORTAR RESPALDO LOCAL
# ==========================================
elif opcion == "💾 Exportar Respaldo":
    st.title("💾 Descarga de Seguridad")
    st.markdown("Aunque tus datos están en Google Sheets, siempre es buena práctica descargar un respaldo local en Excel.")
    
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