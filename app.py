import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

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
        .main { background-color: #F8FAFC; }
        .stButton>button {
            background-color: #1E3A8A;
            color: white;
            border-radius: 6px;
            border: none;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover { background-color: #1D4ED8; color: white; }
        h1, h2, h3 { color: #1E3A8A; font-family: 'Segoe UI', sans-serif; }
        .metric-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 5px solid #1E3A8A;
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
    st.title("📊 Dashboard Ejecutivo de Calidad (Live)")
    st.markdown("Resultados calculados dinámicamente desde el Google Sheet institucional.")

    stats = compute_conformidad_stats(df_matriz)

    if stats['total'] == 0:
        st.info("💡 La matriz en la nube no tiene filas evaluadas aún. Proceda al módulo 'Matriz de Hallazgos' para calificar requisitos.")
    else:
        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown(f"<div class='metric-card'><h3>Grado Conformidad Global</h3><h2>{stats['pct']:.2f}%</h2><p>Sobre requisitos evaluados</p></div>", unsafe_allow_html=True)
        with k2:
            st.markdown(f"<div class='metric-card'><h3>Requisitos Evaluados</h3><h2>{stats['total']}</h2><p>Avance del Plan</p></div>", unsafe_allow_html=True)
        with k3:
            abiertos = len(df_sac[df_sac['estatus_plan']=='Abierto']) if not df_sac.empty else 0
            st.markdown(f"<div class='metric-card'><h3>Planes SAC/OM Abiertos</h3><h2>{abiertos}</h2><p>Pendientes por revisión de eficacia</p></div>", unsafe_allow_html=True)

        st.write("---")

        st.subheader("1. Grado de Conformidad por Proceso Auditado")
        proc_stats = compute_process_stats(df_matriz)
        
        fig_proc = px.bar(proc_stats, x='proceso_auditado', y='Conformidad', color_discrete_sequence=['#1E3A8A'], text_auto='.1f')
        fig_proc.add_hline(y=100, line_dash="dash", line_color="#EF4444", annotation_text="Meta SGC")
        fig_proc.update_layout(yaxis_range=[0, 110], plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_proc, use_container_width=True)
        
        # --- FILA PARA GRÁFICOS 2 Y 3 ---
        col_izq, col_der = st.columns(2)
        with col_izq:
            st.subheader("2. Madurez del SGC por Cláusula ISO 9001")
            req_stats = compute_requirement_stats(df_matriz)
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
        auditor_detail = compute_auditor_stats(df_matriz)
        if not auditor_detail.empty:
            # Count unique processes per auditor
            auditor_count = auditor_detail.groupby('auditor_responsable').size().reset_index(name='Total Procesos Únicos')

            # Bar chart of unique process count
            fig_auditor = px.bar(auditor_count, x='auditor_responsable', y='Total Procesos Únicos',
                                color_discrete_sequence=['#8B5CF6'], text_auto='d')
            fig_auditor.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_title='Auditor',
                                     yaxis_title='Procesos Únicos Auditados')
            st.plotly_chart(fig_auditor, use_container_width=True)

            # Interactive detail table
            st.write("**Detalle: Auditor-Proceso-Fecha**")
            st.dataframe(auditor_detail.rename(columns={
                'auditor_responsable': 'Auditor',
                'proceso_auditado': 'Proceso',
                'fecha': 'Fecha'
            }), use_container_width=True, hide_index=True)
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
                        st.info(f"**Cláusula ISO:** {fila_editar['requisito_iso']} | **Detalle:** {fila_editar['requisito_especifico']}")
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
                n_iso = st.number_input("Cláusula ISO (4-10):", 4, 10, 4)
            with col2:
                n_esp = st.text_input("Sub-cláusula (ej. 7.1.4):")
                n_legal = st.text_input("Requisito Interno / Legal:")
                n_tipo = st.selectbox("Tipo Hallazgo:", ["Conforme", "No Conforme", "Oportunidad de mejora"])
                n_cump = st.selectbox("Cumplimiento:", ["Conforme", "No Conforme"])
                
            n_evid = st.text_area("Evidencia:")
            n_obs = st.text_area("Observaciones:")
            
            if st.form_submit_button("Insertar Nueva Fila"):
                try:
                    validate_required(n_proc, "Proceso")
                    validate_required(n_auditor, "Auditor")
                    validate_required(n_esp, "Sub-cláusula")
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
                s_req = st.text_input("Requisito / Cláusula:")
                s_tipo = st.selectbox("Tipo Plan:", ["Acción Correctiva", "Oportunidad de mejora"])
                s_cod = st.text_input("Código único SAC/OM:")
            s_obs = st.text_area("Detalles / Plan Propuesto:")
            
            if st.form_submit_button("Registrar Apertura"):
                try:
                    validate_required(s_proc, "Proceso")
                    validate_required(s_auditor, "Auditor")
                    validate_required(s_req, "Requisito / Cláusula")
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