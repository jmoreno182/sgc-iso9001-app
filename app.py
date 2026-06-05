import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets_connection import GSheetsConnection
from datetime import datetime
import io

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
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Lectura de datos (con ttl=0 para forzar la actualización en tiempo real en cada CRUD)
    df_matriz = conn.read(worksheet="Matriz", ttl=0)
    df_sac = conn.read(worksheet="SAC_OM", ttl=0)
    
    # Convertir columnas a tipos manejables y limpiar nulos
    df_matriz['id'] = df_matriz['id'].astype(int)
    if not df_sac.empty and 'id' in df_sac.columns:
        df_sac['id'] = df_sac['id'].astype(int)
        
except Exception as e:
    st.error("Error de conexión con Google Sheets. Verifique la configuración de Secrets.")
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
    
    # Filtrar registros que ya han sido evaluados en la auditoría
    df_evaluados = df_matriz[df_matriz['tipo_hallazgo'].notna() & (df_matriz['tipo_hallazgo'] != '')]
    
    if df_evaluados.empty:
        st.info("💡 La matriz en la nube no tiene filas evaluadas aún. Proceda al módulo 'Matriz de Hallazgos' para calificar requisitos.")
    else:
        # KPIs de Control
        total_evaluados = len(df_evaluados)
        total_conformes = len(df_evaluados[df_evaluados['cumplimiento'] == 'Conforme'])
        grado_global = (total_conformes / total_evaluados) * 100 if total_evaluados > 0 else 0
        
        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown(f"<div class='metric-card'><h3>Grado Conformidad Global</h3><h2>{grado_global:.2f}%</h2><p>Sobre requisitos evaluados</p></div>", unsafe_allow_html=True)
        with k2:
            st.markdown(f"<div class='metric-card'><h3>Requisitos Evaluados</h3><h2>{total_evaluados}</h2><p>Avance del Plan</p></div>", unsafe_allow_html=True)
        with k3:
            abiertos = len(df_sac[df_sac['estatus_plan']=='Abierto']) if not df_sac.empty else 0
            st.markdown(f"<div class='metric-card'><h3>Planes SAC/OM Abiertos</h3><h2>{abiertos}</h2><p>Pendientes por revisión de eficacia</p></div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # --- GRÁFICO 1: CONFORMIDAD POR PROCESO ---
        st.subheader("1. Grado de Conformidad por Proceso Auditado")
        proc_stats = df_evaluados.groupby('proceso_auditado').apply(
            lambda x: (sum(x['cumplimiento'] == 'Conforme') / len(x)) * 100
        ).reset_index(name='Conformidad')
        
        fig_proc = px.bar(proc_stats, x='proceso_auditado', y='Conformidad', color_discrete_sequence=['#1E3A8A'], text_auto='.1f')
        fig_proc.add_hline(y=100, line_dash="dash", line_color="#EF4444", annotation_text="Meta SGC")
        fig_proc.update_layout(yaxis_range=[0, 110], plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_proc, use_container_width=True)
        
        # --- FILA PARA GRÁFICOS 2 Y 3 ---
        col_izq, col_der = st.columns(2)
        with col_izq:
            st.subheader("2. Madurez del SGC por Cláusula ISO 9001")
            req_stats = df_evaluados.groupby('requisito_iso').apply(
                lambda x: (sum(x['cumplimiento'] == 'Conforme') / len(x)) * 100
            ).reset_index(name='Conformidad')
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
                fig_sac.update_layout(plot_bgcolor='rgba(0,0,0,0)', ylabel={'title': 'Cantidad de Acciones'})
                st.plotly_chart(fig_sac, use_container_width=True)
            else:
                st.info("Sin registros en la tabla SAC_OM para graficar.")

# ==========================================
# MÓDULO 2: MATRIZ DE HALLAZGOS (CRUD)
# ==========================================
elif opcion == "📝 Matriz de Hallazgos":
    st.title("📝 Matriz de Hallazgos en la Nube")
    
    tab1, tab2 = st.tabs(["🔄 Evaluar Requisitos (Plan Pre-cargado)", "➕ Agregar Fila al Plan"])
    
    with tab1:
        procesos_disponibles = df_matriz['proceso_auditado'].dropna().unique().tolist()
        proc_sel = st.selectbox("Seleccione el proceso en evaluación:", procesos_disponibles)
        
        # Filtrar filas del proceso seleccionado
        df_proc = df_matriz[df_matriz['proceso_auditado'] == proc_sel]
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
                # Modificar el dataframe en memoria
                df_matriz.at[idx_row, 'tipo_hallazgo'] = tipo_h
                df_matriz.at[idx_row, 'cumplimiento'] = cump
                df_matriz.at[idx_row, 'evidencia_objetiva'] = evid
                df_matriz.at[idx_row, 'observaciones'] = obs
                
                # Empujar actualización completa
                conn.update(worksheet="Matriz", data=df_matriz)
                st.success("¡Datos sincronizados exitosamente en la nube!")
                st.rerun()

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
                nuevo_id = int(df_matriz['id'].max() + 1) if not df_matriz.empty else 1
                nueva_fila = {
                    'id': nuevo_id, 'fecha': n_fecha.strftime('%Y-%m-%d'), 'proceso_auditado': n_proc,
                    'auditor_responsable': n_auditor, 'requisito_iso': n_iso, 'requisito_especifico': n_esp,
                    'requisito_interno_legal': n_legal, 'tipo_hallazgo': n_tipo, 'cumplimiento': n_cump,
                    'evidencia_objetiva': n_evid, 'observaciones': n_obs
                }
                df_matriz = pd.concat([df_matriz, pd.DataFrame([nueva_fila])], ignore_index=True)
                conn.update(worksheet="Matriz", data=df_matriz)
                st.success("Fila añadida al Google Sheet.")
                st.rerun()

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
                    df_sac.at[idx_sac, 'estatus_plan'] = e_plan
                    df_sac.at[idx_sac, 'estatus_la_eficacia'] = e_efic
                    df_sac.at[idx_sac, 'observaciones'] = e_obs
                    conn.update(worksheet="SAC_OM", data=df_sac)
                    st.success("Plan de acción actualizado en Google Sheets.")
                    st.rerun()
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
                nuevo_id_sac = int(df_sac['id'].max() + 1) if not df_sac.empty else 1
                nueva_sac = {
                    'id': nuevo_id_sac, 'fecha': s_fecha.strftime('%Y-%m-%d'), 'proceso_auditado': s_proc,
                    'auditor_responsable': s_auditor, 'requisito_iso': s_req, 'tipo_plan': s_tipo,
                    'codigo': s_cod, 'estatus_plan': 'Abierto', 'estatus_la_eficacia': 'Pendiente verificar', 'observaciones': s_obs
                }
                df_sac = pd.concat([df_sac, pd.DataFrame([nueva_sac])], ignore_index=True)
                conn.update(worksheet="SAC_OM", data=df_sac)
                st.success("Plan aperturado en la nube de forma exitosa.")
                st.rerun()

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