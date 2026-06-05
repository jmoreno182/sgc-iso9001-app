import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# Configuración de la página del SGC
st.set_page_config(page_title="Dashboard Auditoría SGC", layout="wide")

# ==============================================================================
# NUEVA FUNCIÓN DE CONEXIÓN DIRECTA (REEMPLAZA A GSheetsConnection)
# ==============================================================================
# Coloca aquí el enlace "Compartir" de tu Google Sheet
URL_GOOGLE_SHEET = "TU_URL_DE_GOOGLE_SHEETS_AQUI"

def cargar_datos_sgc(url_compartir):
    """Convierte la URL de compartir en un enlace de descarga CSV directo para Pandas"""
    try:
        if "/edit" in url_compartir:
            base_url = url_compartir.split("/edit")[0]
            url_csv = f"{base_url}/export?format=csv"
            # Si tu enlace apunta a una pestaña específica (ej. Matriz de hallazgos), conserva el gid
            if "gid=" in url_compartir:
                gid = url_compartir.split("gid=")[1].split("&")[0]
                url_csv += f"&gid={gid}"
        else:
            url_csv = url_compartir
        
        # Retorna el DataFrame procesado por Pandas directamente de la nube
        return pd.read_csv(url_csv)
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

# Llamada para construir tu DataFrame principal
df = cargar_datos_sgc(URL_GOOGLE_SHEET)
# ==============================================================================

# ... A PARTIR DE AQUÍ CONSERVA TODO TU CÓDIGO ORIGINAL ...
# (Solo asegúrate de que tus funciones usen el 'df' generado arriba)

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
# FUNCIÓN ULTRA-ROBUSTA DE DETECCIÓN DE DATOS
# ==========================================
def normalizar_y_blindar_dataframe(df, tipo_tabla="Matriz"):
    if df.empty:
        return df
        
    # 1. Detectar si la cabecera real está desplazada por filas vacías arriba
    cabecera_encontrada = False
    for idx, row in df.iterrows():
        valores_fila = [str(v).strip().lower() for v in row.values if pd.notna(v)]
        # Buscamos palabras clave institucionales para identificar la fila de títulos
        if any('fecha' in v or 'proceso' in v or 'auditor' in v for v in valores_fila):
            nuevas_columnas = []
            for col_val in row.values:
                if pd.isna(col_val) or str(col_val).strip() == '':
                    nuevas_columnas.append('columna_vacia_desplazada')
                else:
                    nuevas_columnas.append(str(col_val).strip())
            df.columns = nuevas_columnas
            df = df.iloc[idx+1:].reset_index(drop=True)
            cabecera_encontrada = True
            break
            
    if not cabecera_encontrada:
        df.columns = [str(c).strip() for c in df.columns]
        
    # 2. Limpiar saltos de línea (\n) y múltiples espacios en los nombres de columnas
    df.columns = df.columns.str.replace('\n', ' ').str.replace(r'\s+', ' ', regex=True).str.strip()
    
    # 3. Diccionario de mapeo inteligente (Soporta nombres originales de tu Excel)
    mapeo_columnas = {
        'Fecha': 'fecha',
        'Proceso Auditado': 'proceso_auditado',
        'Auditor Responsable': 'auditor_responsable',
        'Requisito ISO 9001:2015': 'requisito_iso',
        'Requisito específico ISO 9001:2015': 'requisito_especifico',
        'Requisito Interno / Legal': 'requisito_interno_legal',
        'Tipo de Hallazgo': 'tipo_hallazgo',
        'Tipo de hallazgo': 'tipo_hallazgo',
        'Cumplimiento del requisito': 'cumplimiento',
        'Cumplimiento': 'cumplimiento',
        'Evidencia objetiva de NC': 'evidencia_objetiva',
        'Evidencia objetiva': 'evidencia_objetiva',
        'Observaciones / comentarios adicionales': 'observaciones',
        'Observaciones': 'observaciones',
        'Tipo de plan': 'tipo_plan',
        'Código': 'codigo',
        'Estatus del plan': 'estatus_plan',
        'Estatus de la eficacia': 'estatus_la_eficacia',
        'id': 'id'
    }
    
    df = df.rename(columns=mapeo_columnas)
    
    # 4. Forzar la existencia de columnas para evitar fallos de lectura (KeyError)
    columnas_requeridas = {
        "Matriz": ['id', 'fecha', 'proceso_auditado', 'auditor_responsable', 'requisito_iso', 
                   'requisito_especifico', 'requisito_interno_legal', 'tipo_hallazgo', 
                   'cumplimiento', 'evidencia_objetiva', 'observaciones'],
        "SAC_OM": ['id', 'fecha', 'proceso_auditado', 'auditor_responsable', 'requisito_iso', 
                   'tipo_plan', 'codigo', 'estatus_plan', 'estatus_la_eficacia', 'observaciones']
    }
    
    for col in columnas_requeridas[tipo_tabla]:
        if col not in df.columns:
            df[col] = ""
            
    # 5. Descartar filas basurilla o completamente vacías del final de la hoja
    df = df.dropna(subset=['proceso_auditado', 'requisito_iso'], how='all')
    df = df[df['proceso_auditado'].astype(str).str.strip() != '']
    
    # 6. Auto-generar identificadores únicos correlativos
    if 'id' not in df.columns or df['id'].astype(str).str.strip().eq('').all() or df['id'].isnull().all():
        df['id'] = range(1, len(df) + 1)
    else:
        df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(range(1, len(df) + 1)).astype(int)
        
    return df.reset_index(drop=True)

# ==========================================
# CONEXIÓN DIRECTA A GOOGLE SHEETS
# ==========================================
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    df_matriz_raw = conn.read(worksheet="Matriz", ttl=0)
    df_sac_raw = conn.read(worksheet="SAC_OM", ttl=0)
    
    df_matriz = normalizar_y_blindar_dataframe(df_matriz_raw, "Matriz")
    df_sac = normalizar_y_blindar_dataframe(df_sac_raw, "SAC_OM")
    
except Exception as e:
    st.error(f"⚠️ Error de infraestructura: {e}")
    st.info("Asegúrese de que los nombres de las pestañas en Google Sheets sean exactamente 'Matriz' y 'SAC_OM'.")
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
if opcion == "📊 Dashboard de Direction":
    st.title("📊 Dashboard Ejecutivo de Calidad (Live)")
    st.markdown("Resultados calculados dinámicamente desde el Google Sheet institucional.")
    
    df_matriz['tipo_hallazgo_clean'] = df_matriz['tipo_hallazgo'].astype(str).str.strip()
    df_evaluados = df_matriz[(df_matriz['tipo_hallazgo_clean'] != '') & (df_matriz['tipo_hallazgo_clean'].str.lower() != 'nan')]
    
    if df_evaluados.empty:
        st.info("💡 La matriz en la nube no contiene filas evaluadas todavía. Diríjase a la sección 'Matriz de Hallazgos' para calificar requisitos.")
    else:
        df_evaluados['is_conforme'] = df_evaluados['cumplimiento'].astype(str).str.strip().str.lower() == 'conforme'
        
        total_evaluados = len(df_evaluados)
        total_conformes = df_evaluados['is_conforme'].sum()
        grado_global = (total_conformes / total_evaluados) * 100 if total_evaluados > 0 else 0
        
        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown(f"<div class='metric-card'><h3>Grado Conformidad Global</h3><h2>{grado_global:.2f}%</h2><p>Sobre requisitos evaluados</p></div>", unsafe_allow_html=True)
        with k2:
            st.markdown(f"<div class='metric-card'><h3>Requisitos Evaluados</h3><h2>{total_evaluados}</h2><p>Avance del Plan</p></div>", unsafe_allow_html=True)
        with k3:
            abiertos = len(df_sac[df_sac['estatus_plan'].astype(str).str.strip().str.lower() == 'abierto']) if not df_sac.empty else 0
            st.markdown(f"<div class='metric-card'><h3>Planes SAC/OM Abiertos</h3><h2>{abiertos}</h2><p>Pendientes por verificación</p></div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # --- GRÁFICO 1: CONFORMIDAD POR PROCESO ---
        st.subheader("1. Grado de Conformidad por Proceso Auditado")
        proc_stats = df_evaluados.groupby('proceso_auditado')['is_conforme'].mean().reset_index()
        proc_stats['Conformidad'] = proc_stats['is_conforme'] * 100
        
        fig_proc = px.bar(proc_stats, x='proceso_auditado', y='Conformidad', color_discrete_sequence=['#1E3A8A'], text_auto='.1f')
        fig_proc.add_hline(y=100, line_dash="dash", line_color="#EF4444", annotation_text="Meta SGC")
        fig_proc.update_layout(yaxis_range=[0, 110], plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_proc, use_container_width=True)
        
        # --- FILA PARA GRÁFICOS 2 Y 3 ---
        col_izq, col_der = st.columns(2)
        with col_izq:
            st.subheader("2. Madurez del SGC por Cláusula ISO 9001")
            req_stats = df_evaluados.groupby('requisito_iso')['is_conforme'].mean().reset_index()
            req_stats['Conformidad'] = req_stats['is_conforme'] * 100
            fig_req = px.bar(req_stats, x='requisito_iso', y='Conformidad', color_discrete_sequence=['#3B82F6'], text_auto='.1f')
            fig_req.update_layout(yaxis_range=[0, 110], plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_req, use_container_width=True)
            
        with col_der:
            st.subheader("3. Distribución de Estatus de Acciones (SAC / OM)")
            if not df_sac.empty:
                fig_sac = px.histogram(
                    df_sac, x='tipo_plan', color='estatus_plan', barmode='group',
                    color_discrete_map={'Cerrado': '#10B981', 'Abierto': '#1E3A8A', 'Pendiente verificar': '#F59E0B'}
                )
                fig_sac.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_sac, use_container_width=True)

# ==========================================
# MÓDULO 2: MATRIZ DE HALLAZGOS (CRUD)
# ==========================================
elif opcion == "📝 Matriz de Hallazgos":
    st.title("📝 Matriz de Hallazgos en la Nube")
    
    tab1, tab2 = st.tabs(["🔄 Evaluar Requisitos (Plan Pre-cargado)", "➕ Agregar Fila al Plan"])
    
    with tab1:
        procesos_disponibles = df_matriz['proceso_auditado'].dropna().unique().tolist()
        proc_sel = st.selectbox("Seleccione el proceso en evaluación:", procesos_disponibles)
        
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
                                     index=0 if str(fila_editar['tipo_hallazgo']).strip()=='Conforme' else 1 if str(fila_editar['tipo_hallazgo']).strip()=='No Conforme' else 2)
            with c2:
                cump = st.selectbox("Cumplimiento:", ["Conforme", "No Conforme"],
                                   index=0 if str(fila_editar['cumplimiento']).strip()=='Conforme' else 1)
            
            evid = st.text_area("Evidencia Objetiva hallada:", value=str(fila_editar['evidencia_objetiva'] if pd.notna(fila_editar['evidencia_objetiva']) else ''))
            obs = st.text_area("Observaciones técnicas:", value=str(fila_editar['observaciones'] if pd.notna(fila_editar['observaciones']) else ''))
            
            if st.form_submit_button("Sincronizar con Google Sheets"):
                df_matriz.at[idx_row, 'tipo_hallazgo'] = tipo_h
                df_matriz.at[idx_row, 'cumplimiento'] = cump
                df_matriz.at[idx_row, 'evidencia_objetiva'] = evid
                df_matriz.at[idx_row, 'observaciones'] = obs
                
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
                st.success("Fila añadida al Google Sheet de forma exitosa.")
                st.rerun()

# ==========================================
# MÓDULO 3: SEGUIMIENTO SAC / OM (CRUD)
# ==========================================
elif opcion == "⚙️ Seguimiento SAC / OM":
    st.title("⚙️ Control de Acciones Correctivas y OM")
    
    tab_s
