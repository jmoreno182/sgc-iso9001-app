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
# PLOTLY TEMPLATE PERSONALIZADO
# ==========================================
def apply_iso_theme(fig):
    """Aplica tema ISO 9001 personalizado a gráficos Plotly."""
    fig.update_layout(
        font=dict(family="Roboto, sans-serif", size=12, color="#374151"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(255,255,255,0)',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(229,231,235,0.5)',
            zeroline=False,
            showline=True,
            linewidth=1,
            linecolor='#E5E7EB'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(229,231,235,0.5)',
            zeroline=False,
            showline=True,
            linewidth=1,
            linecolor='#E5E7EB'
        ),
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified',
        transition=dict(duration=300),
    )
    return fig

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILO AZUL
# ==========================================
st.set_page_config(
    page_title="Gestión SGC - Google Sheets Cloud",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Roboto:wght@400;500&display=swap" rel="stylesheet">
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
            font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        .main {
            background-color: #FFFFFF;
            padding: 0;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #1F2937;
            font-weight: 700;
            letter-spacing: -0.5px;
        }

        h1 {
            font-size: clamp(1.5rem, 5vw, 2.5rem);
            margin-bottom: clamp(0.25rem, 2vw, 0.75rem);
        }
        h2 {
            font-size: clamp(1.125rem, 3.5vw, 1.875rem);
            margin-top: clamp(0.75rem, 2vw, 1.5rem);
            margin-bottom: clamp(0.5rem, 1.5vw, 1rem);
        }
        h3 {
            font-size: clamp(0.75rem, 2vw, 1.125rem);
            margin-bottom: clamp(0.25rem, 1vw, 0.75rem);
        }

        .stButton>button {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            color: white;
            border-radius: 8px;
            border: none;
            padding: clamp(0.5rem, 1.5vw, 0.75rem) clamp(1rem, 3vw, 1.5rem);
            font-size: clamp(0.8rem, 2vw, 1rem);
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2);
        }

        .stButton>button:hover {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(59, 130, 246, 0.35);
        }

        .stButton>button:active {
            transform: translateY(0);
        }

        /* Mobile responsiveness */
        @media (max-width: 768px) {
            h1 { font-size: 1.75rem; }
            h2 { font-size: 1.25rem; }
            h3 { font-size: 1rem; }
            .metric-card {
                padding: 1rem;
                margin-bottom: 0.75rem;
            }
            .metric-card h2 {
                font-size: 2rem;
            }
        }

        @media (max-width: 480px) {
            h1 { font-size: 1.5rem; margin-bottom: 0.25rem; }
            h2 { font-size: 1.125rem; }
            .stButton>button {
                padding: 0.5rem 1rem;
                font-size: 0.875rem;
            }
            .metric-card {
                padding: 0.75rem;
            }
            .metric-card h3 {
                font-size: 0.75rem;
            }
            .metric-card h2 {
                font-size: 1.5rem;
            }
        }

        .metric-card {
            background: linear-gradient(135deg, #FFFFFF 0%, #F3F4F6 100%);
            padding: clamp(0.75rem, 3vw, 1.5rem);
            border-radius: 12px;
            border: 1px solid #E5E7EB;
            border-left: 4px solid #3B82F6;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04);
            transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            min-height: clamp(100px, 15vh, 180px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(59, 130, 246, 0) 100%);
            pointer-events: none;
        }

        .metric-card:hover {
            box-shadow: 0 12px 28px rgba(59, 130, 246, 0.15), 0 4px 8px rgba(0, 0, 0, 0.08);
            transform: translateY(-4px);
            border-left-color: #2563EB;
        }

        .metric-card h3 {
            color: #6B7280;
            font-family: 'Poppins', sans-serif;
            font-size: clamp(0.65rem, 1.5vw, 0.875rem);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: clamp(0.25rem, 1vw, 0.5rem);
            margin-top: 0;
            position: relative;
            z-index: 1;
        }

        .metric-card h2 {
            color: #1F2937;
            font-family: 'Poppins', sans-serif;
            font-size: clamp(1.5rem, 4vw, 2.25rem);
            margin: clamp(0.15rem, 0.5vw, 0.35rem) 0;
            line-height: 1.2;
            font-weight: 700;
            position: relative;
            z-index: 1;
        }

        .metric-card p {
            color: #9CA3AF;
            font-size: clamp(0.7rem, 1.5vw, 0.9rem);
            margin: 0;
            position: relative;
            z-index: 1;
        }

        hr { border-color: #E5E7EB; margin: 2rem 0; }

        [data-testid="stExpander"] {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            transition: all 0.25s ease;
        }

        [data-testid="stExpander"]:hover {
            border-color: #3B82F6;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
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

        /* Sidebar enhancement */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #FFFFFF 0%, #F9FAFB 100%);
        }

        [data-testid="stSidebar"] h1 {
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            background: linear-gradient(135deg, #1F2937 0%, #3B82F6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        [data-testid="stSidebar"] [role="radiogroup"] {
            gap: 0.5rem;
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


try:
    df_matriz, df_sac = load_gsheets_data(max_retries=3)
except Exception as e:
    st.error(f"Error al cargar datos: {str(e)}")
    st.stop()

# ==========================================
# MENÚ LATERAL DE NAVEGACIÓN
# ==========================================
# Top navigation
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

# Initialize session state for module selection
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
        # Métricas (2+2 grid layout)
        row1_col1, row1_col2 = st.columns(2, gap="medium")
        with row1_col1:
            trend_color = '#10B981' if trend['trend'] == '↑' else '#EF4444' if trend['trend'] == '↓' else '#6B7280'
            st.markdown(f"<div class='metric-card'><h3>Conformidad Global</h3><h2>{stats['pct']:.1f}%</h2><p style='color: {trend_color}; font-size: 1.5rem;'>{trend['trend']} {abs(stats['pct'] - trend['previous']):.1f}p</p></div>", unsafe_allow_html=True)
        with row1_col2:
            st.markdown(f"<div class='metric-card'><h3>Requisitos Evaluados</h3><h2>{stats['total']}</h2><p>Avance del Plan</p></div>", unsafe_allow_html=True)

        st.divider()

        row2_col1, row2_col2 = st.columns(2, gap="medium")
        with row2_col1:
            abiertos = len(df_sac[df_sac['estatus_plan']=='Abierto']) if not df_sac.empty else 0
            sac_color = '#EF4444' if abiertos > 5 else '#F59E0B' if abiertos > 0 else '#10B981'
            st.markdown(f"<div class='metric-card'><h3>SAC/OM Abiertos</h3><h2 style='color: {sac_color};'>{abiertos}</h2><p>Pendientes por verificar</p></div>", unsafe_allow_html=True)
        with row2_col2:
            auditor_comp = compute_auditor_comparison(df_filtered)
            if not auditor_comp.empty:
                top_auditor = auditor_comp.loc[auditor_comp['Requisitos Evaluados'].idxmax()]
                st.markdown(f"<div class='metric-card'><h3>Auditor Top</h3><h2>{top_auditor['Auditor']}</h2><p>{int(top_auditor['Requisitos Evaluados'])} requisitos</p></div>", unsafe_allow_html=True)

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

        fig_proc = px.bar(proc_stats, x='proceso_auditado', y='Conformidad', color_discrete_sequence=['#3B82F6'], text_auto='.1f')
        fig_proc.add_hline(y=100, line_dash="dash", line_color="#EF4444", annotation_text="Meta SGC")
        fig_proc.update_layout(yaxis_range=[0, 110])
        fig_proc = apply_iso_theme(fig_proc)
        st.plotly_chart(fig_proc, use_container_width=True)
        
        # --- FILA PARA GRÁFICOS 2 Y 3 ---
        col_izq, col_der = st.columns(2)
        with col_izq:
            st.subheader("2. Madurez del SGC por Requisito ISO 9001")
            req_stats = compute_requirement_stats(df_filtered)
            fig_req = px.bar(req_stats, x='requisito_iso', y='Conformidad', color_discrete_sequence=['#2563EB'], text_auto='.1f')
            fig_req.update_layout(yaxis_range=[0, 110])
            fig_req = apply_iso_theme(fig_req)
            st.plotly_chart(fig_req, use_container_width=True)
            
        with col_der:
            st.subheader("3. Distribución de Estatus de Acciones (SAC / OM)")
            if not df_sac.empty and 'tipo_plan' in df_sac.columns:
                fig_sac = px.histogram(
                    df_sac, x='tipo_plan', color='estatus_plan', barmode='group',
                    color_discrete_map={'Cerrado': '#10B981', 'Abierto': '#3B82F6', 'Pendiente verificar': '#F59E0B'}
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
                                color_discrete_sequence=['#7C3AED'], text_auto='d')
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
                                     color_discrete_sequence=['#3B82F6'],
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
    
    tab1, tab2 = st.tabs(["Historial del Día", "Registrar Hallazgo"])
    
    with tab1:
        st.subheader("Hallazgos Registrados")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_proc = st.multiselect("Proceso:", sorted(df_matriz['proceso_auditado'].dropna().unique()))
        with col_f2:
            filter_auditor = st.multiselect("Auditor:", sorted(df_matriz['auditor_responsable'].dropna().unique()))

        df_filtered_matriz = df_matriz.copy()
        if filter_proc:
            df_filtered_matriz = df_filtered_matriz[df_filtered_matriz['proceso_auditado'].isin(filter_proc)]
        if filter_auditor:
            df_filtered_matriz = df_filtered_matriz[df_filtered_matriz['auditor_responsable'].isin(filter_auditor)]

        if df_filtered_matriz.empty:
            st.info("Sin hallazgos para mostrar")
        else:
            for idx, row in df_filtered_matriz.iterrows():
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

                    st.divider()

                    if st.button(f"Editar hallazgo #{row['id']}", key=f"edit_hallazgo_{row['id']}"):
                        st.session_state[f"editing_hallazgo_{row['id']}"] = True

                    if st.session_state.get(f"editing_hallazgo_{row['id']}", False):
                        st.subheader("Editar Hallazgo")
                        with st.form(f"form_edit_hallazgo_{row['id']}"):
                            tipo_h = st.selectbox("Tipo de Hallazgo:", ["Conforme", "No Conforme", "Oportunidad de mejora"],
                                                 index=0 if row['tipo_hallazgo']=='Conforme' else 1 if row['tipo_hallazgo']=='No Conforme' else 2,
                                                 key=f"tipo_{row['id']}")
                            cump = st.selectbox("Cumplimiento:", ["Conforme", "No Conforme"],
                                               index=0 if row['cumplimiento']=='Conforme' else 1,
                                               key=f"cump_{row['id']}")
                            evid = st.text_area("Evidencia Objetiva:", value=str(row['evidencia_objetiva'] or ''), height=100, key=f"evid_{row['id']}")
                            obs = st.text_area("Observaciones:", value=str(row['observaciones'] or ''), height=80, key=f"obs_{row['id']}")

                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.form_submit_button("Guardar Cambios"):
                                    try:
                                        if cump == "No Conforme" and not evid.strip():
                                            st.error("⚠️ Evidencia requerida cuando cumplimiento es 'No Conforme'")
                                        else:
                                            idx_row = df_matriz[df_matriz['id'] == row['id']].index[0]
                                            df_matriz.at[idx_row, 'tipo_hallazgo'] = tipo_h
                                            df_matriz.at[idx_row, 'cumplimiento'] = cump
                                            df_matriz.at[idx_row, 'evidencia_objetiva'] = evid
                                            df_matriz.at[idx_row, 'observaciones'] = obs

                                            try:
                                                update_gsheets("Matriz", df_matriz)
                                                st.success(f"✓ Hallazgo #{row['id']} actualizado")
                                                st.session_state[f"editing_hallazgo_{row['id']}"] = False
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Error al sincronizar: {str(e)}")
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                            with col_btn2:
                                if st.form_submit_button("Cancelar"):
                                    st.session_state[f"editing_hallazgo_{row['id']}"] = False
                                    st.rerun()

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
elif opcion == "SEGUIMIENTO":
    st.title("SEGUIMIENTO DE ACCIONES")
    st.subheader("Estado de Acciones Correctivas")

    tab_s1, tab_s2 = st.tabs(["Acciones Abiertas", "Registrar Nueva"])
    
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
elif opcion == "EXPORTAR":
    st.title("EXPORTACIÓN")
    
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