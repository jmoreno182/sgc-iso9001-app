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
    load_horas_data,
    append_participacion,
    update_participacion,
    PROCESOS_SGC,
    ROLES_AUDITOR,
    ROLES_DESCRIPCION,
)

ISO_TINTA = "#1E3A5F"
ISO_TINTA_FUERTE = "#10233A"
ISO_CONFORME = "#287A4D"
ISO_NO_CONFORME = "#B42318"
ISO_PENDIENTE = "#A16207"
ISO_TEXTO_TENUE = "#76808C"

# ==========================================
# PLOTLY TEMPLATE PERSONALIZADO
# ==========================================
def apply_iso_theme(fig):
    """Apply the institutional ISO 9001 theme to Plotly charts."""
    fig.update_layout(
        font=dict(family="Source Sans 3, sans-serif", size=12, color="#1C1E21"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(255,255,255,0)',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(28,30,33,0.08)',
            zeroline=False,
            showline=True,
            linewidth=1,
            linecolor='rgba(28,30,33,0.14)'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(28,30,33,0.08)',
            zeroline=False,
            showline=True,
            linewidth=1,
            linecolor='rgba(28,30,33,0.14)'
        ),
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified',
        transition=dict(duration=180),
    )
    return fig

# ==========================================
# CONFIGURACION DE PAGINA Y SISTEMA VISUAL
# ==========================================
st.set_page_config(
    page_title="Gestion SGC - Google Sheets Cloud",
    page_icon=None,
    layout="wide",
)

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --tinta: #1E3A5F;
            --tinta-fuerte: #10233A;
            --papel: #FAFAF8;
            --papel-elevado: #FFFFFF;
            --formulario: #F1F0EC;
            --linea-formulario: rgba(28, 30, 33, 0.14);
            --linea-suave: rgba(28, 30, 33, 0.08);
            --texto: #1C1E21;
            --texto-secundario: #4D5661;
            --texto-tenue: #76808C;
            --sello-conforme: #287A4D;
            --tinta-no-conforme: #B42318;
            --expediente-pendiente: #A16207;
            --control-bg: #F7F6F2;
            --control-border: rgba(30, 58, 95, 0.22);
        }

        * {
            font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        .main {
            background-color: var(--papel);
            padding: 0;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif;
            color: var(--tinta-fuerte);
            font-weight: 700;
            letter-spacing: 0;
        }

        h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        h2 { font-size: 1.45rem; margin-top: 1.25rem; margin-bottom: 0.75rem; }
        h3 { font-size: 1rem; margin-bottom: 0.5rem; color: var(--tinta); }

        .stButton>button {
            font-family: 'Source Sans 3', sans-serif;
            background: var(--tinta);
            color: #FFFFFF;
            border-radius: 6px;
            border: 1px solid rgba(16, 35, 58, 0.18);
            padding: 0.58rem 1rem;
            font-size: 0.95rem;
            font-weight: 600;
            transition: background-color 160ms ease-in-out, border-color 160ms ease-in-out;
            box-shadow: none;
        }

        .stButton>button:hover {
            background: var(--tinta-fuerte);
            border-color: rgba(16, 35, 58, 0.35);
            color: #FFFFFF;
        }

        .stButton>button:focus { box-shadow: 0 0 0 2px rgba(30, 58, 95, 0.18); }

        @media (max-width: 768px) {
            h1 { font-size: 1.75rem; }
            h2 { font-size: 1.25rem; }
            h3 { font-size: 1rem; }
            .metric-card { padding: 0.9rem; margin-bottom: 0.75rem; }
            .metric-card h2 { font-size: 1.8rem; }
        }

        @media (max-width: 480px) {
            h1 { font-size: 1.5rem; margin-bottom: 0.25rem; }
            h2 { font-size: 1.125rem; }
            .stButton>button { padding: 0.5rem 1rem; font-size: 0.875rem; }
            .metric-card { padding: 0.75rem; }
            .metric-card h3 { font-size: 0.75rem; }
            .metric-card h2 { font-size: 1.5rem; }
        }

        .metric-card {
            background: var(--papel-elevado);
            padding: 1.1rem 1.2rem;
            border-radius: 6px;
            border: 1px solid var(--linea-formulario);
            border-left: 3px solid var(--tinta);
            box-shadow: none;
            transition: border-color 160ms ease-in-out, background-color 160ms ease-in-out;
            min-height: 126px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        .metric-card:hover {
            background: #FDFDFC;
            border-color: rgba(30, 58, 95, 0.24);
        }

        .metric-card.primary {
            min-height: 168px;
            border-left-width: 5px;
            background: #FFFFFF;
        }

        .metric-card.compact { min-height: 112px; }

        .metric-card h3 {
            color: var(--texto-secundario);
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.4rem;
            margin-top: 0;
            position: relative;
            z-index: 1;
        }

        .metric-card h2 {
            color: var(--texto);
            font-family: 'IBM Plex Mono', monospace;
            font-size: 2rem;
            margin: 0.15rem 0;
            line-height: 1.12;
            font-weight: 700;
            position: relative;
            z-index: 1;
            font-variant-numeric: tabular-nums;
        }

        .metric-card.primary h2 { font-size: 2.7rem; }

        .metric-card p {
            color: var(--texto-tenue);
            font-size: 0.88rem;
            margin: 0;
            position: relative;
            z-index: 1;
        }

        hr { border-color: var(--linea-suave); margin: 1.5rem 0; }

        [data-testid="stExpander"] {
            border: 1px solid var(--linea-formulario);
            border-radius: 6px;
            transition: border-color 160ms ease-in-out;
        }

        [data-testid="stExpander"]:hover { border-color: var(--control-border); }

        .stDataFrame {
            border: 1px solid var(--linea-formulario);
            border-radius: 6px;
            overflow: hidden;
        }

        .stInfo, .stWarning, .stError { border-radius: 6px; padding: 0.9rem; }
        .stMarkdown { color: var(--texto); line-height: 1.55; }

        [data-testid="stSidebar"] {
            background: var(--papel);
            border-right: 1px solid var(--linea-suave);
        }

        [data-testid="stSidebar"] h1 {
            font-family: 'Source Sans 3', sans-serif;
            font-weight: 700;
            color: var(--tinta-fuerte);
        }

        [data-testid="stSidebar"] [role="radiogroup"] { gap: 0.5rem; }

        input, textarea, [data-baseweb="select"] > div {
            background-color: var(--control-bg);
            border-color: var(--control-border);
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CONEXIÓN DIRECTA A GOOGLE SHEETS
# ==========================================
# Nota: La URL del spreadsheet se configura en los Secrets de Streamlit

if "GOOGLE_SERVICE_ACCOUNT_INFO" not in st.secrets:
    st.warning("Aplicacion en modo configuracion")
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


try:
    df_matriz, df_sac = load_gsheets_data(max_retries=3)
    df_matriz = df_matriz.drop_duplicates(subset=['id'], keep='first')
    df_sac = df_sac.drop_duplicates(subset=['id'], keep='first')
except Exception as e:
    st.error(f"Error al cargar datos: {str(e)}")
    st.stop()

# ==========================================
# MENÚ LATERAL DE NAVEGACIÓN
# ==========================================
# Top navigation
st.markdown("""
    <div style="text-align: center; padding: 0.75rem 0 1rem; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(28,30,33,.12);">
        <h1 style="margin: 0; color: var(--tinta-fuerte); font-size: 1.9rem;">
            Auditoria Interna del SGC
        </h1>
        <p style="margin: 0.35rem 0 0 0; color: var(--texto-secundario); font-size: 0.9rem;">
            ISO 9001:2015 | Registro, seguimiento y evidencia
        </p>
    </div>
""", unsafe_allow_html=True)
# Initialize session state for module selection
if "modulo" not in st.session_state:
    st.session_state.modulo = "ENTRADA"

col1, col2, col3, col4 = st.columns(4, gap="small")
with col1:
    if st.button("ENTRADA", key="nav_entrada", use_container_width=True):
        st.session_state.modulo = "ENTRADA"
with col2:
    if st.button("SEGUIMIENTO", key="nav_seguimiento", use_container_width=True):
        st.session_state.modulo = "SEGUIMIENTO"
with col3:
    if st.button("HORAS", key="nav_horas", use_container_width=True):
        st.session_state.modulo = "HORAS"
with col4:
    if st.button("ANÁLISIS", key="nav_analisis", use_container_width=True):
        st.session_state.modulo = "ANÁLISIS"

opcion = st.session_state.modulo

# ==========================================
# MÓDULO 1: DASHBOARD DE DIRECCIÓN
# ==========================================
if opcion == "ANÁLISIS":
    st.title("ANÁLISIS Y REPORTES")

    # Filtros interactivos
    filter_cols = st.columns([1, 1, 1], gap="medium")

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
        st.info("Sin datos para mostrar. Agrega requisitos en 'Matriz de Hallazgos'.")
    else:
        # Metricas principales
        row1_col1, row1_col2 = st.columns(2, gap="medium")
        with row1_col1:
            trend_color = ISO_CONFORME if trend['trend'] == '↑' else ISO_NO_CONFORME if trend['trend'] == '↓' else ISO_TEXTO_TENUE
            st.markdown(f"<div class='metric-card primary'><h3>Conformidad Global</h3><h2>{stats['pct']:.1f}%</h2><p style='color: {trend_color}; font-size: 1.1rem;'>{trend['trend']} {abs(stats['pct'] - trend['previous']):.1f}p</p></div>", unsafe_allow_html=True)
        with row1_col2:
            st.markdown(f"<div class='metric-card compact'><h3>Requisitos Evaluados</h3><h2>{stats['total']}</h2><p>Avance del Plan</p></div>", unsafe_allow_html=True)

        st.divider()

        # Búsqueda rápida
        with st.expander("Búsqueda Rápida", expanded=False):
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

        fig_proc = px.bar(proc_stats, x='proceso_auditado', y='Conformidad', color_discrete_sequence=[ISO_TINTA], text_auto='.1f')
        fig_proc.add_hline(y=100, line_dash="dash", line_color=ISO_NO_CONFORME, annotation_text="Meta SGC")
        fig_proc.update_layout(yaxis_range=[0, 110])
        fig_proc = apply_iso_theme(fig_proc)
        st.plotly_chart(fig_proc, use_container_width=True)

        # --- FILA PARA GRÁFICOS 2 Y 3 ---
        col_izq, col_der = st.columns(2)
        with col_izq:
            st.subheader("2. Madurez del SGC por Requisito ISO 9001")
            req_stats = compute_requirement_stats(df_filtered)
            fig_req = px.bar(req_stats, x='requisito_iso', y='Conformidad', color_discrete_sequence=[ISO_TINTA], text_auto='.1f')
            fig_req.update_layout(yaxis_range=[0, 110])
            fig_req = apply_iso_theme(fig_req)
            st.plotly_chart(fig_req, use_container_width=True)

        with col_der:
            st.subheader("3. Distribución de Estatus de Acciones (SAC / OM)")
            if not df_sac.empty and 'tipo_plan' in df_sac.columns:
                fig_sac = px.histogram(
                    df_sac, x='tipo_plan', color='estatus_plan', barmode='group',
                    color_discrete_map={'Cerrado': ISO_CONFORME, 'Abierto': ISO_TINTA, 'Pendiente verificar': ISO_PENDIENTE}
                )
                fig_sac.update_layout(yaxis_title='Cantidad de Acciones')
                fig_sac.update_traces(textposition='outside', texttemplate='%{y:.0f}')
                fig_sac = apply_iso_theme(fig_sac)
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
                                color_discrete_sequence=[ISO_TINTA], text_auto='d')
            fig_auditor.update_layout(xaxis_title='Auditor', yaxis_title='Procesos Únicos Auditados')
            fig_auditor = apply_iso_theme(fig_auditor)
            st.plotly_chart(fig_auditor, use_container_width=True)

            # Grouped detail table by auditor
            st.write("**Detalle: Procesos por Auditor**")

            for auditor in sorted(auditor_detail['auditor_responsable'].unique()):
                auditor_rows = auditor_detail[auditor_detail['auditor_responsable'] == auditor][
                    ['proceso_auditado', 'fecha']
                ].reset_index(drop=True)

                with st.expander(f"{auditor} ({len(auditor_rows)} procesos)", expanded=True):
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
                                     color_discrete_sequence=[ISO_TINTA],
                                     labels={'Requisitos Evaluados': 'Productividad',
                                            'Conformidad': 'Conformidad (%)'})
                fig_comp.update_layout(height=400)
                fig_comp = apply_iso_theme(fig_comp)
                st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("Sin datos de auditores para graficar.")

# ==========================================
# MÓDULO 2: MATRIZ DE HALLAZGOS (CRUD)
# ==========================================
elif opcion == "ENTRADA":
    st.title("ENTRADA DE HALLAZGOS")
    st.write("Registro y seguimiento de hallazgos de auditoría interna ISO 9001:2015")
    st.divider()

    tab1, tab2 = st.tabs(["Historial del Día", "Registrar Hallazgo"])

    with tab1:
        st.subheader("Búsqueda y Filtros")
        search_term = st.text_input("Búsqueda", placeholder="ID, Auditor, Evidencia o ISO...", key="search_entrada")

        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            filter_proc = st.multiselect("Proceso", sorted(df_matriz['proceso_auditado'].dropna().unique()), key="proc_entrada")
        with col_f2:
            filter_auditor = st.multiselect("Auditor", sorted(df_matriz['auditor_responsable'].dropna().unique()), key="aud_entrada")
        with col_f3:
            filter_status = st.multiselect("Tipo", ["Conforme", "No Conforme", "Oportunidad de mejora"], key="status_entrada")
        with col_f4:
            sort_by = st.selectbox("Ordenar por", ["Fecha (desc)", "ISO", "Auditor"], key="sort_entrada")

        # Aplicar filtros
        df_filtered_matriz = df_matriz.copy()
        if filter_proc:
            df_filtered_matriz = df_filtered_matriz[df_filtered_matriz['proceso_auditado'].isin(filter_proc)]
        if filter_auditor:
            df_filtered_matriz = df_filtered_matriz[df_filtered_matriz['auditor_responsable'].isin(filter_auditor)]
        if filter_status:
            df_filtered_matriz = df_filtered_matriz[df_filtered_matriz['tipo_hallazgo'].isin(filter_status)]

        if search_term:
            search_term_lower = search_term.lower()
            df_filtered_matriz = df_filtered_matriz[
                df_filtered_matriz['id'].astype(str).str.contains(search_term_lower, case=False) |
                df_filtered_matriz['auditor_responsable'].str.contains(search_term_lower, case=False, na=False) |
                df_filtered_matriz['evidencia_objetiva'].str.contains(search_term_lower, case=False, na=False) |
                df_filtered_matriz['requisito_iso'].astype(str).str.contains(search_term_lower, case=False)
            ]

        # Ordenamiento
        if sort_by == "Fecha (desc)":
            df_filtered_matriz = df_filtered_matriz.sort_values('fecha', ascending=False)
        elif sort_by == "ISO":
            df_filtered_matriz = df_filtered_matriz.sort_values('requisito_iso')
        elif sort_by == "Auditor":
            df_filtered_matriz = df_filtered_matriz.sort_values('auditor_responsable')

        st.write(f"**{len(df_filtered_matriz)}** hallazgo(s) encontrado(s)")

        if df_filtered_matriz.empty:
            st.info("No hay hallazgos que coincidan con los criterios de búsqueda")
        else:
            for idx, row in df_filtered_matriz.iterrows():
                # Estado - prioridad correcta
                if not row['cumplimiento'] or str(row['cumplimiento']).strip() == '':
                    status_text = "Pendiente"
                elif row['cumplimiento'] == 'Conforme':
                    status_text = "Conforme"
                elif row['cumplimiento'] == 'No Conforme':
                    status_text = "No Conforme"
                else:
                    status_text = "Pendiente"

                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**ID #{row['id']}** | {row['proceso_auditado']} | ISO {row['requisito_iso']}")
                        st.write(f"Requisito específico: {row['requisito_especifico']}")
                    with col2:
                        st.write(f"**{status_text}**")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Auditor:** {row['auditor_responsable']}")
                        st.write(f"**Fecha:** {row['fecha']}")
                    with col2:
                        st.write(f"**Tipo:** {row['tipo_hallazgo']}")
                        st.write(f"**Cumplimiento:** {row['cumplimiento']}")

                    st.write(f"**Evidencia:** {str(row['evidencia_objetiva'] or '-')[:150]}{'...' if len(str(row['evidencia_objetiva'] or '')) > 150 else ''}")

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("Editar", key=f"btn_edit_{idx}", use_container_width=True):
                        st.session_state[f"modal_edit_{idx}"] = True
                with col_btn2:
                    if st.button("Detalles", key=f"btn_details_{idx}", use_container_width=True):
                        st.session_state[f"modal_details_{idx}"] = True

                if st.session_state.get(f"modal_edit_{idx}", False):
                    st.divider()
                    st.subheader(f"Editar Hallazgo #{row['id']}")
                    with st.form(f"form_edit_hallazgo_{idx}"):
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            tipo_h = st.selectbox("Tipo de Hallazgo", ["Conforme", "No Conforme", "Oportunidad de mejora"],
                                                 index=0 if row['tipo_hallazgo']=='Conforme' else 1 if row['tipo_hallazgo']=='No Conforme' else 2,
                                                 key=f"tipo_{idx}")
                        with col_e2:
                            # Determinar index correcto para cumplimiento (vacío = 0 para Conforme como default)
                            cump_index = 0
                            if row['cumplimiento'] == 'No Conforme':
                                cump_index = 1
                            cump = st.selectbox("Cumplimiento", ["Conforme", "No Conforme"],
                                               index=cump_index,
                                               key=f"cump_{idx}")

                        evid = st.text_area("Evidencia Objetiva", value=str(row['evidencia_objetiva'] or ''), height=100, key=f"evid_{idx}")

                        if cump == "No Conforme" and not evid.strip():
                            st.warning("La evidencia es requerida para hallazgos No Conforme")

                        obs = st.text_area("Observaciones", value=str(row['observaciones'] or ''), height=80, key=f"obs_{idx}")

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("Guardar Cambios", use_container_width=True):
                                st.session_state[f"edit_tipo_{idx}"] = tipo_h
                                st.session_state[f"edit_cump_{idx}"] = cump
                                st.session_state[f"edit_evid_{idx}"] = evid
                                st.session_state[f"edit_obs_{idx}"] = obs
                                st.session_state[f"confirm_edit_{idx}"] = True
                        with col_btn2:
                            if st.form_submit_button("Cancelar", use_container_width=True):
                                st.session_state[f"modal_edit_{idx}"] = False
                                st.rerun()

                    if st.session_state.get(f"confirm_edit_{idx}", False):
                        st.warning(f"Confirmar cambios en Hallazgo #{row['id']}")
                        col_c1, col_c2 = st.columns(2)
                        with col_c1:
                            if st.button("Confirmar cambios", key=f"confirm_yes_{idx}", use_container_width=True):
                                try:
                                    cump = st.session_state.get(f"edit_cump_{idx}")
                                    evid = st.session_state.get(f"edit_evid_{idx}", "")
                                    tipo_h = st.session_state.get(f"edit_tipo_{idx}")
                                    obs = st.session_state.get(f"edit_obs_{idx}", "")

                                    if cump == "No Conforme" and not (evid or "").strip():
                                        st.error("Evidencia requerida cuando cumplimiento es No Conforme")
                                    else:
                                        idx_row = df_matriz[df_matriz['id'] == row['id']].index[0]
                                        df_matriz.at[idx_row, 'tipo_hallazgo'] = tipo_h
                                        df_matriz.at[idx_row, 'cumplimiento'] = cump
                                        df_matriz.at[idx_row, 'evidencia_objetiva'] = evid
                                        df_matriz.at[idx_row, 'observaciones'] = obs

                                        try:
                                            with st.spinner("Guardando cambios en Google Sheets..."):
                                                update_gsheets("Matriz", df_matriz)
                                            st.success(f"Hallazgo #{row['id']} actualizado")
                                            st.session_state[f"modal_edit_{idx}"] = False
                                            st.session_state[f"confirm_edit_{idx}"] = False
                                            st.session_state.pop(f"edit_tipo_{idx}", None)
                                            st.session_state.pop(f"edit_cump_{idx}", None)
                                            st.session_state.pop(f"edit_evid_{idx}", None)
                                            st.session_state.pop(f"edit_obs_{idx}", None)
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error: {str(e)}")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        with col_c2:
                            if st.button("Cancelar", key=f"confirm_no_{idx}", use_container_width=True):
                                st.session_state[f"confirm_edit_{idx}"] = False
                                st.session_state.pop(f"edit_tipo_{idx}", None)
                                st.session_state.pop(f"edit_cump_{idx}", None)
                                st.session_state.pop(f"edit_evid_{idx}", None)
                                st.session_state.pop(f"edit_obs_{idx}", None)
                                st.rerun()

                if st.session_state.get(f"modal_details_{idx}", False):
                    st.divider()
                    st.subheader(f"Detalles - Hallazgo #{row['id']}")
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.write(f"**ID:** {row['id']}")
                        st.write(f"**Auditor:** {row['auditor_responsable']}")
                        st.write(f"**Fecha:** {row['fecha']}")
                    with col_d2:
                        st.write(f"**Proceso:** {row['proceso_auditado']}")
                        st.write(f"**Tipo:** {row['tipo_hallazgo']}")
                        st.write(f"**Cumplimiento:** {row['cumplimiento']}")

                    st.write(f"**ISO 9001:** Requisito {row['requisito_iso']}")
                    st.write(f"**Específico:** {row['requisito_especifico']}")
                    st.write(f"**Interno/Legal:** {row['requisito_interno_legal'] or '—'}")
                    st.write(f"**Evidencia:**\n{row['evidencia_objetiva'] or '—'}")
                    if row['observaciones']:
                        st.write(f"**Observaciones:**\n{row['observaciones']}")

                    if st.button("Cerrar", key=f"close_details_{idx}"):
                        st.session_state[f"modal_details_{idx}"] = False
                        st.rerun()

    with tab2:
        st.subheader("Registrar Nuevo Hallazgo")

        with st.form("form_nueva_fila"):
            st.write("**Información Básica**")
            col_nf1, col_nf2, col_nf3 = st.columns(3)
            with col_nf1:
                n_fecha = st.date_input("Fecha", datetime.now())
            with col_nf2:
                n_proc = st.text_input("Proceso (Siglas)").upper()
            with col_nf3:
                n_auditor = st.text_input("Auditor Responsable")

            st.write("**Requisitos**")
            col_nr1, col_nr2, col_nr3 = st.columns(3)
            with col_nr1:
                n_iso = st.number_input("ISO 9001 (4-10)", 4, 10, 4)
            with col_nr2:
                n_esp = st.text_input("Sub-requisito (ej. 7.1.4)")
            with col_nr3:
                n_legal = st.text_input("Requisito Interno/Legal")

            st.write("**Clasificación**")
            col_nt1, col_nt2 = st.columns(2)
            with col_nt1:
                n_tipo = st.selectbox("Tipo Hallazgo", ["Conforme", "No Conforme", "Oportunidad de mejora"])
            with col_nt2:
                n_cump = st.selectbox("Cumplimiento", ["Conforme", "No Conforme"])

            if n_cump == "No Conforme":
                st.warning("Evidencia requerida para hallazgos No Conforme")

            st.write("**Contenido**")
            n_evid = st.text_area("Evidencia Objetiva", height=120, placeholder="Describa la evidencia encontrada...")
            n_obs = st.text_area("Observaciones", height=80, placeholder="Notas adicionales (opcional)...")

            if st.form_submit_button("Registrar Hallazgo", use_container_width=True):
                try:
                    validate_required(n_proc, "Proceso")
                    validate_required(n_auditor, "Auditor")
                    validate_required(n_esp, "Sub-requisito")
                    if n_cump == "No Conforme":
                        validate_required(n_evid, "Evidencia (requerida si No Conforme)")
                    st.session_state["confirm_new_entrada"] = True
                except ValidationError as e:
                    st.error(f"{str(e)}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        if st.session_state.get("confirm_new_entrada", False):
            st.warning("Confirmar registro de nuevo hallazgo")
            st.write(f"**Proceso:** {n_proc} | **Auditor:** {n_auditor} | **Requisito:** {n_esp}")
            col_cf1, col_cf2 = st.columns(2)
            with col_cf1:
                if st.button("Confirmar registro", key="confirm_new_yes", use_container_width=True):
                    try:
                        nuevo_id = int(df_matriz['id'].max() + 1) if not df_matriz.empty else 1
                        nueva_fila = {
                            'id': nuevo_id, 'fecha': n_fecha.strftime('%Y-%m-%d'), 'proceso_auditado': n_proc.strip(),
                            'auditor_responsable': n_auditor.strip(), 'requisito_iso': n_iso, 'requisito_especifico': n_esp.strip(),
                            'requisito_interno_legal': n_legal.strip(), 'tipo_hallazgo': n_tipo, 'cumplimiento': n_cump,
                            'evidencia_objetiva': n_evid.strip(), 'observaciones': n_obs.strip()
                        }
                        df_matriz = pd.concat([df_matriz, pd.DataFrame([nueva_fila])], ignore_index=True)

                        try:
                            with st.spinner("Registrando hallazgo en Google Sheets..."):
                                update_gsheets("Matriz", df_matriz)
                            st.success("Hallazgo registrado exitosamente")
                            st.session_state["confirm_new_entrada"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar: {str(e)}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            with col_cf2:
                if st.button("Cancelar", key="confirm_new_no", use_container_width=True):
                    st.session_state["confirm_new_entrada"] = False
                    st.rerun()

# ==========================================
# MÓDULO 3: SEGUIMIENTO SAC / OM (CRUD)
# ==========================================
elif opcion == "SEGUIMIENTO":
    st.title("SEGUIMIENTO DE ACCIONES")
    st.write("Gestión de acciones correctivas y planes de mejora ISO 9001:2015")
    st.divider()

    tab_s1, tab_s2 = st.tabs(["Acciones Abiertas", "Registrar Nueva"])

    with tab_s1:
        if not df_sac.empty:
            # Búsqueda y filtros
            col_search, col_filter = st.columns([2, 1])
            with col_search:
                search_sac = st.text_input("Buscar por código, proceso o auditor:", placeholder="ej: SAC-001, IT, Carlos")
            with col_filter:
                filter_status = st.selectbox("Filtrar por estatus:", ["Todos", "Abierto", "Cerrado"], key="sac_status_filter")

            # Aplicar búsqueda y filtros
            df_sac_filtered = df_sac.copy()

            if search_sac:
                df_sac_filtered = df_sac_filtered[
                    (df_sac_filtered['codigo'].str.contains(search_sac, case=False, na=False)) |
                    (df_sac_filtered['proceso_auditado'].str.contains(search_sac, case=False, na=False)) |
                    (df_sac_filtered['auditor_responsable'].str.contains(search_sac, case=False, na=False))
                ]

            if filter_status != "Todos":
                df_sac_filtered = df_sac_filtered[df_sac_filtered['estatus_plan'] == filter_status]

            # Mostrar resultados
            if not df_sac_filtered.empty:
                st.write(f"**{len(df_sac_filtered)} plan(es) encontrado(s)**")
                st.dataframe(df_sac_filtered, use_container_width=True, hide_index=True)

                id_sac = st.selectbox("Seleccione ID del Plan para actualizar:", df_sac_filtered['id'].tolist())
            else:
                st.info("Sin planes que coincidan con los criterios de búsqueda")
                st.stop()

            idx_sac = df_sac[df_sac['id'] == id_sac].index[0]
            idx_sac = df_sac[df_sac['id'] == id_sac].index[0]
            fila_sac = df_sac.loc[idx_sac]

            with st.form("form_edit_sac"):
                st.write(f"**Código de Acción:** {fila_sac['codigo']} | **Proceso:** {fila_sac['proceso_auditado']}")
                e_plan = st.selectbox("Estatus del Plan:", ["Abierto", "Cerrado"], index=0 if fila_sac['estatus_plan']=='Abierto' else 1)
                e_efic = st.selectbox("Estatus de la Eficacia:", ["Pendiente verificar", "Eficaz", "No eficaz"],
                                      index=0 if fila_sac['estatus_la_eficacia']=='Pendiente verificar' else 1 if fila_sac['estatus_la_eficacia']=='Eficaz' else 2)
                e_obs = st.text_area("Comentarios de Verificación:", value=str(fila_sac['observaciones'] or ''))

                if st.form_submit_button("Actualizar Estatus en la Nube"):
                    if e_plan == "Cerrado" and e_efic == "Pendiente verificar":
                        st.error("No puede cerrar un plan con eficacia pendiente de verificar")
                    else:
                        st.session_state["confirm_sac_update"] = True

            if st.session_state.get("confirm_sac_update", False):
                st.warning(f"Confirmar actualización del plan {fila_sac['codigo']}")
                col_cs1, col_cs2 = st.columns(2)
                with col_cs1:
                    if st.button("Confirmar actualización", key="confirm_sac_yes", use_container_width=True):
                        try:
                            df_sac.at[idx_sac, 'estatus_plan'] = e_plan
                            df_sac.at[idx_sac, 'estatus_la_eficacia'] = e_efic
                            df_sac.at[idx_sac, 'observaciones'] = e_obs.strip()
                            try:
                                with st.spinner("Actualizando plan en Google Sheets..."):
                                    update_gsheets("SAC_OM", df_sac)
                                st.success("Plan actualizado exitosamente")
                                st.session_state["confirm_sac_update"] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al guardar: {str(e)}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                with col_cs2:
                    if st.button("Cancelar", key="confirm_sac_no", use_container_width=True):
                        st.session_state["confirm_sac_update"] = False
                        st.rerun()
        else:
            st.info("No hay planes de acción registrados en este momento.")

    with tab_s2:
        st.subheader("Registrar Nueva Acción")
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
                validation_errors = []

                # Validaciones de campos requeridos
                try:
                    validate_required(s_proc, "Proceso Responsable")
                    validate_required(s_auditor, "Auditor Emisor")
                    validate_required(s_req, "Requisito ISO")
                    validate_required(s_cod, "Código SAC/OM")
                    validate_required(s_obs, "Detalles del Plan")
                except ValidationError as e:
                    validation_errors.append(str(e))

                # Validación de código único
                if not validation_errors:
                    s_cod_upper = s_cod.strip().upper()
                    existing_codes = df_sac['codigo'].str.upper().tolist() if not df_sac.empty else []
                    if s_cod_upper in existing_codes:
                        validation_errors.append(f"Código '{s_cod}' ya existe en el sistema. Use un código único")

                # Validación de longitud mínima del código
                if not validation_errors and len(s_cod.strip()) < 3:
                    validation_errors.append("Código SAC/OM debe tener al menos 3 caracteres")

                # Mostrar errores o proceder
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                else:
                    st.session_state["confirm_sac_new"] = True

        if st.session_state.get("confirm_sac_new", False):
            st.warning(f"Confirmar registro de nueva acción: {s_cod}")
            col_cn1, col_cn2 = st.columns(2)
            with col_cn1:
                if st.button("Confirmar registro", key="confirm_sac_new_yes", use_container_width=True):
                    try:
                        nuevo_id_sac = int(df_sac['id'].max() + 1) if not df_sac.empty else 1
                        nueva_sac = {
                            'id': nuevo_id_sac, 'fecha': s_fecha.strftime('%Y-%m-%d'), 'proceso_auditado': s_proc.strip(),
                            'auditor_responsable': s_auditor.strip(), 'requisito_iso': s_req.strip(), 'tipo_plan': s_tipo,
                            'codigo': s_cod.strip(), 'estatus_plan': 'Abierto', 'estatus_la_eficacia': 'Pendiente verificar', 'observaciones': s_obs.strip()
                        }
                        df_sac = pd.concat([df_sac, pd.DataFrame([nueva_sac])], ignore_index=True)

                        try:
                            with st.spinner("Registrando plan en Google Sheets..."):
                                update_gsheets("SAC_OM", df_sac)
                            st.success("Plan registrado exitosamente")
                            st.session_state["confirm_sac_new"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar: {str(e)}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            with col_cn2:
                if st.button("Cancelar", key="confirm_sac_new_no", use_container_width=True):
                    st.session_state["confirm_sac_new"] = False
                    st.rerun()

# ==========================================
# MÓDULO 4: REGISTRO DE HORAS DE AUDITORÍA
# ==========================================
elif opcion == "HORAS":
    st.title("REGISTRO DE HORAS DE AUDITORÍA")
    st.write("Seguimiento de participación y horas de auditoría por auditor y rol")
    st.divider()

    try:
        df_part, df_reporte, lista_auditores = load_horas_data()
    except Exception as e:
        st.error(f"No se pudieron cargar las hojas del módulo HORAS: {str(e)}")
        st.info("Verifica que existan las hojas **Horas_Base_2011_2025**, **Participaciones_2026** y **Reporte_Horas_2026** en el Google Sheet. Ejecuta: `python setup_horas_sheets.py`")
        st.stop()

    tab_h1, tab_h2, tab_h3 = st.tabs(["Registrar Horas", "Editar Registro", "Ver Reporte"])

    # --- TAB 1: REGISTRAR PARTICIPACIÓN ---
    with tab_h1:
        st.subheader("Registrar Participación en Auditoría")

        with st.form("form_registrar_horas"):
            ch1, ch2 = st.columns(2)
            with ch1:
                h_fecha = st.date_input("Fecha de la auditoría:", datetime.now())
                h_proceso = st.selectbox("Proceso auditado:", PROCESOS_SGC)
                h_auditor = st.selectbox("Auditor:", lista_auditores)
            with ch2:
                h_rol = st.selectbox(
                    "Rol desempeñado:", ROLES_AUDITOR,
                    format_func=lambda r: f"{r} — {ROLES_DESCRIPCION[r]}"
                )
                h_horas = st.number_input("Horas:", min_value=0.1, max_value=24.0, value=8.0, step=0.5, format="%.1f")
            h_obs = st.text_area("Observaciones (opcional):", height=80)

            if st.form_submit_button("Registrar Horas"):
                validation_errors = []

                # Validaciones de campos requeridos
                try:
                    validate_required(h_auditor, "Auditor")
                    validate_required(h_proceso, "Proceso")
                except ValidationError as e:
                    validation_errors.append(str(e))

                # Validación de horas en rango válido
                if not validation_errors:
                    if h_horas < 0.1 or h_horas > 24.0:
                        validation_errors.append("Las horas deben estar entre 0.1 y 24.0 horas")

                # Validación de fecha (no puede ser en el futuro)
                if not validation_errors:
                    if h_fecha > datetime.now().date():
                        validation_errors.append("La fecha de auditoría no puede ser en el futuro")

                # Validación de fecha razonable (no más de 1 año atrás)
                if not validation_errors:
                    from datetime import timedelta
                    if h_fecha < datetime.now().date() - timedelta(days=365):
                        validation_errors.append("La fecha de auditoría no puede ser más de un año en el pasado")

                # Mostrar errores o proceder
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                else:
                    st.session_state["confirm_horas"] = True

        if st.session_state.get("confirm_horas", False):
            st.warning(f"Confirmar registro: {h_auditor} | {h_rol} | {h_horas:.1f}h | {h_proceso}")
            col_ch1, col_ch2 = st.columns(2)
            with col_ch1:
                if st.button("Confirmar registro", key="confirm_horas_yes", use_container_width=True):
                    try:
                        with st.spinner("Registrando participación en Google Sheets..."):
                            fila = append_participacion(h_fecha, h_proceso, h_auditor, h_rol, h_horas, h_obs)
                        st.success(f"Participación registrada: {h_auditor} | {h_rol} | {h_horas:.1f} h (fila {fila})")
                        st.session_state["confirm_horas"] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {str(e)}")
            with col_ch2:
                if st.button("Cancelar", key="confirm_horas_no", use_container_width=True):
                    st.session_state["confirm_horas"] = False
                    st.rerun()

        st.divider()
        st.subheader("Últimas Participaciones Registradas")
        if df_part.empty:
            st.info("Aún no hay participaciones registradas en 2026.")
        else:
            st.dataframe(df_part.drop(columns=["__sheet_row"], errors="ignore").tail(15).iloc[::-1], use_container_width=True, hide_index=True)

    # --- TAB 2: EDITAR PARTICIPACION ---
    with tab_h2:
        st.subheader("Editar Participacion Registrada")

        if df_part.empty:
            st.info("Aun no hay participaciones registradas en 2026.")
        else:
            df_edit = df_part.copy()
            df_edit["__sheet_row"] = pd.to_numeric(df_edit["__sheet_row"], errors="coerce").astype("Int64")
            df_edit = df_edit.dropna(subset=["__sheet_row"]).copy()
            df_edit["__label"] = df_edit.apply(
                lambda r: f"Fila {int(r['__sheet_row'])} | {r.get('Fecha', '')} | {r.get('Auditor', '')} | {r.get('Rol', '')} | {float(r.get('Horas', 0)):.1f} h | {r.get('Proceso', '')}",
                axis=1
            )

            selected_label = st.selectbox(
                "Registro a editar:",
                df_edit["__label"].iloc[::-1].tolist(),
                key="edit_horas_registro"
            )
            selected_row = df_edit[df_edit["__label"] == selected_label].iloc[0]

            with st.form("form_editar_horas"):
                eh1, eh2 = st.columns(2)
                with eh1:
                    e_fecha_actual = pd.to_datetime(selected_row.get("Fecha"), errors="coerce")
                    e_fecha_default = e_fecha_actual.date() if pd.notna(e_fecha_actual) else datetime.now().date()
                    e_fecha = st.date_input("Fecha de la auditoria:", e_fecha_default, key="edit_horas_fecha")
                    e_proceso = st.selectbox(
                        "Proceso auditado:",
                        PROCESOS_SGC,
                        index=PROCESOS_SGC.index(selected_row.get("Proceso")) if selected_row.get("Proceso") in PROCESOS_SGC else 0,
                        key="edit_horas_proceso"
                    )
                    e_auditor = st.selectbox(
                        "Auditor:",
                        lista_auditores,
                        index=lista_auditores.index(selected_row.get("Auditor")) if selected_row.get("Auditor") in lista_auditores else 0,
                        key="edit_horas_auditor"
                    )
                with eh2:
                    e_rol = st.selectbox(
                        "Rol desempenado:",
                        ROLES_AUDITOR,
                        index=ROLES_AUDITOR.index(selected_row.get("Rol")) if selected_row.get("Rol") in ROLES_AUDITOR else 0,
                        format_func=lambda r: f"{r} - {ROLES_DESCRIPCION[r]}",
                        key="edit_horas_rol"
                    )
                    e_horas = st.number_input(
                        "Horas:",
                        min_value=0.1,
                        max_value=24.0,
                        value=float(selected_row.get("Horas", 8.0) or 8.0),
                        step=0.5,
                        format="%.1f",
                        key="edit_horas_horas"
                    )
                e_obs = st.text_area(
                    "Observaciones (opcional):",
                    value=str(selected_row.get("Observaciones", "")),
                    height=80,
                    key="edit_horas_obs"
                )

                if st.form_submit_button("Guardar Cambios"):
                    validation_errors = []

                    try:
                        validate_required(e_auditor, "Auditor")
                        validate_required(e_proceso, "Proceso")
                    except ValidationError as e:
                        validation_errors.append(str(e))

                    if not validation_errors and (e_horas < 0.1 or e_horas > 24.0):
                        validation_errors.append("Las horas deben estar entre 0.1 y 24.0 horas")

                    if not validation_errors and e_fecha > datetime.now().date():
                        validation_errors.append("La fecha de auditoria no puede ser en el futuro")

                    if not validation_errors and e_fecha < datetime.now().date() - timedelta(days=365):
                        validation_errors.append("La fecha de auditoria no puede ser mas de un ano en el pasado")

                    if validation_errors:
                        for error in validation_errors:
                            st.error(error)
                    else:
                        st.session_state["confirm_horas_edit"] = {
                            "row_number": int(selected_row["__sheet_row"]),
                            "fecha": e_fecha,
                            "proceso": e_proceso,
                            "auditor": e_auditor,
                            "rol": e_rol,
                            "horas": e_horas,
                            "observaciones": e_obs,
                        }

            pending_edit = st.session_state.get("confirm_horas_edit")
            if pending_edit:
                st.warning(
                    f"Confirmar cambio fila {pending_edit['row_number']}: "
                    f"{pending_edit['auditor']} | {pending_edit['rol']} | {pending_edit['horas']:.1f} h | {pending_edit['proceso']}"
                )
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    if st.button("Confirmar cambios", key="confirm_horas_edit_yes", use_container_width=True):
                        try:
                            with st.spinner("Actualizando participacion en Google Sheets..."):
                                fila = update_participacion(
                                    pending_edit["row_number"],
                                    pending_edit["fecha"],
                                    pending_edit["proceso"],
                                    pending_edit["auditor"],
                                    pending_edit["rol"],
                                    pending_edit["horas"],
                                    pending_edit["observaciones"],
                                )
                            st.success(f"Participacion actualizada: fila {fila}")
                            st.session_state["confirm_horas_edit"] = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar: {str(e)}")
                with col_e2:
                    if st.button("Cancelar", key="confirm_horas_edit_no", use_container_width=True):
                        st.session_state["confirm_horas_edit"] = None
                        st.rerun()

            st.divider()
            st.subheader("Registros Disponibles")
            st.dataframe(df_edit.drop(columns=["__sheet_row", "__label"], errors="ignore").tail(30).iloc[::-1], use_container_width=True, hide_index=True)

    # --- TAB 3: REPORTE ACUMULADO ---
    with tab_h3:
        st.subheader("Reporte de Horas Acumuladas")

        if df_reporte.empty:
            st.info("El reporte está vacío. Verifica la hoja Reporte_Horas_2026.")
        else:
            df_rep = df_reporte.copy()
            cols_num = [c for c in df_rep.columns if c != "Auditor"]
            for c in cols_num:
                df_rep[c] = pd.to_numeric(df_rep[c].astype(str).str.replace(",", "."), errors="coerce").fillna(0)

            horas_2026 = df_rep[["OB_2026", "AF_2026", "AD_2026", "AL_2026"]].sum().sum()
            participaciones = len(df_part)
            activos = df_part["Auditor"].nunique() if not df_part.empty else 0

            k1, k2, k3 = st.columns(3, gap="medium")
            with k1:
                st.markdown(f"<div class='metric-card primary'><h3>Horas 2026</h3><h2>{horas_2026:.1f}</h2><p>Total registradas este año</p></div>", unsafe_allow_html=True)
            with k2:
                st.markdown(f"<div class='metric-card compact'><h3>Participaciones</h3><h2>{participaciones}</h2><p>Registros en 2026</p></div>", unsafe_allow_html=True)
            with k3:
                st.markdown(f"<div class='metric-card compact'><h3>Auditores Activos</h3><h2>{activos}</h2><p>Con horas en 2026</p></div>", unsafe_allow_html=True)

            st.divider()

            # Búsqueda por auditor
            search_auditor = st.text_input("Buscar auditor:", placeholder="Escribe nombre del auditor para filtrar")

            # Filtrar tabla
            df_rep_filtered = df_rep.copy()
            if search_auditor:
                df_rep_filtered = df_rep_filtered[
                    df_rep_filtered['Auditor'].str.contains(search_auditor, case=False, na=False)
                ]

            # Mostrar resultados
            if not df_rep_filtered.empty:
                st.write(f"**Tabla de Horas por Auditor** ({len(df_rep_filtered)} auditor(es))")
                st.dataframe(df_rep_filtered, use_container_width=True, hide_index=True)
            else:
                st.info("Sin auditores que coincidan con la búsqueda")

            # Gráfico: total acumulado por auditor y rol (usa datos filtrados)
            if not df_rep_filtered.empty:
                df_chart = df_rep_filtered[["Auditor", "OB_Total", "AF_Total", "AD_Total", "AL_Total"]].melt(
                    id_vars="Auditor", var_name="Rol", value_name="Horas"
                )
                df_chart["Rol"] = df_chart["Rol"].str.replace("_Total", "")
                fig_horas = px.bar(
                    df_chart, x="Auditor", y="Horas", color="Rol", barmode="stack",
                    color_discrete_map={"OB": ISO_TEXTO_TENUE, "AF": ISO_PENDIENTE, "AD": ISO_TINTA, "AL": ISO_CONFORME},
                    title="Horas Acumuladas Totales por Auditor y Rol",
                )
                fig_horas = apply_iso_theme(fig_horas)
                fig_horas.update_layout(xaxis_tickangle=-45, height=500)
                st.plotly_chart(fig_horas, use_container_width=True)

            # Exportar reporte a Excel (toda la base de datos, no solo filtrado)
            buffer_h = io.BytesIO()
            with pd.ExcelWriter(buffer_h, engine='openpyxl') as writer:
                df_rep.to_excel(writer, sheet_name='Reporte Horas', index=False)
                if not df_part.empty:
                    df_part.drop(columns=["__sheet_row"], errors="ignore").to_excel(writer, sheet_name='Participaciones 2026', index=False)
            st.download_button(
                label="Descargar Reporte de Horas (XLSX)",
                data=buffer_h.getvalue(),
                file_name=f"Reporte_Horas_Auditoria_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# ==========================================
# MÓDULO 5: EXPORTAR RESPALDO LOCAL
# ==========================================
elif opcion == "EXPORTAR":
    st.title("EXPORTACIÓN")
    st.write("Descargue respaldo completo de datos en formato Excel")
    st.divider()

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_matriz.to_excel(writer, sheet_name='Matriz de Hallazgos', index=False)
        df_sac.to_excel(writer, sheet_name='Seguimiento SAC OM', index=False)

    st.subheader("Respaldo de Base de Datos")
    st.write("Descargue todos los datos registrados en un archivo Excel")
    st.download_button(
        label="Descargar Base de Datos Completa (XLSX)",
        data=buffer.getvalue(),
        file_name=f"Respaldo_SGC_ISO9001_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
