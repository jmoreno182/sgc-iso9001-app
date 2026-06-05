import io
import re
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Dashboard Auditoría SGC ISO 9001",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
    .main {
        background-color: #F8FAFC;
    }

    h1, h2, h3 {
        color: #1E3A8A;
        font-family: 'Segoe UI', sans-serif;
    }

    .metric-card {
        background-color: white;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        border-left: 5px solid #1E3A8A;
        min-height: 130px;
    }

    .metric-card h3 {
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }

    .metric-card h2 {
        font-size: 2rem;
        margin-bottom: 0.3rem;
    }

    .metric-card p {
        color: #475569;
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# URLs REALES DE GOOGLE SHEETS
# ============================================================

URL_MATRIZ = "https://docs.google.com/spreadsheets/d/1dBkUQESYGL676tFtXWXPu_iBnFy3-w96E9n9FQC-1kA/edit?gid=0#gid=0"

URL_SAC_OM = "https://docs.google.com/spreadsheets/d/1dBkUQESYGL676tFtXWXPu_iBnFy3-w96E9n9FQC-1kA/edit?gid=236973792#gid=236973792"


# ============================================================
# COLUMNAS ESPERADAS
# ============================================================

COLUMNAS_MATRIZ = [
    "id",
    "fecha",
    "proceso_auditado",
    "auditor_responsable",
    "requisito_iso",
    "requisito_especifico",
    "requisito_interno_legal",
    "tipo_hallazgo",
    "cumplimiento",
    "evidencia_objetiva",
    "observaciones",
]

COLUMNAS_SAC_OM = [
    "id",
    "fecha",
    "proceso_auditado",
    "auditor_responsable",
    "requisito_iso",
    "tipo_plan",
    "codigo",
    "estatus_plan",
    "estatus_eficacia",
    "observaciones",
]


MAPEO_COLUMNAS = {
    "id": "id",
    "ID": "id",
    "Id": "id",

    "Fecha": "fecha",

    "Proceso Auditado": "proceso_auditado",
    "Proceso auditado": "proceso_auditado",
    "Proceso": "proceso_auditado",

    "Auditor Responsable": "auditor_responsable",
    "Auditor responsable": "auditor_responsable",
    "Auditor": "auditor_responsable",

    "Requisito ISO 9001:2015": "requisito_iso",
    "Requisito ISO": "requisito_iso",
    "Cláusula ISO": "requisito_iso",
    "Clausula ISO": "requisito_iso",

    "Requisito específico ISO 9001:2015": "requisito_especifico",
    "Requisito Específico ISO 9001:2015": "requisito_especifico",
    "Requisito específico": "requisito_especifico",
    "Requisito Específico": "requisito_especifico",

    "Requisito Interno / Legal": "requisito_interno_legal",
    "Requisito interno / legal": "requisito_interno_legal",

    "Tipo de Hallazgo": "tipo_hallazgo",
    "Tipo de hallazgo": "tipo_hallazgo",
    "Hallazgo": "tipo_hallazgo",

    "Cumplimiento del requisito": "cumplimiento",
    "Cumplimiento": "cumplimiento",

    "Evidencia objetiva de NC": "evidencia_objetiva",
    "Evidencia objetiva": "evidencia_objetiva",
    "Evidencia Objetiva": "evidencia_objetiva",
    "Evidencia": "evidencia_objetiva",

    "Observaciones / comentarios adicionales": "observaciones",
    "Observaciones": "observaciones",
    "Comentarios": "observaciones",

    "Tipo de plan": "tipo_plan",
    "Tipo de Plan": "tipo_plan",
    "Plan": "tipo_plan",

    "Código": "codigo",
    "Codigo": "codigo",
    "Código del plan": "codigo",
    "Codigo del plan": "codigo",

    "Estatus del plan": "estatus_plan",
    "Estatus del Plan": "estatus_plan",
    "Estatus Plan": "estatus_plan",

    "Estatus de la eficacia": "estatus_eficacia",
    "Estatus de la Eficacia": "estatus_eficacia",
    "Eficacia": "estatus_eficacia",
}


# ============================================================
# FUNCIONES DE CARGA Y LIMPIEZA
# ============================================================

def convertir_url_google_sheets_a_csv(url: str) -> str:
    """
    Convierte una URL estándar de Google Sheets en una URL de exportación CSV.
    Preserva el gid de la pestaña cuando está presente.
    """
    if not isinstance(url, str) or "docs.google.com/spreadsheets" not in url:
        raise ValueError("La URL proporcionada no parece ser una URL válida de Google Sheets.")

    base_match = re.search(r"(https://docs\.google\.com/spreadsheets/d/[^/]+)", url)

    if not base_match:
        raise ValueError("No se pudo extraer el identificador del Google Sheet.")

    base_url = base_match.group(1)

    gid_match = re.search(r"gid=([0-9]+)", url)
    gid = gid_match.group(1) if gid_match else "0"

    return f"{base_url}/export?format=csv&gid={gid}"


def limpiar_nombre_columna(columna) -> str:
    """
    Limpia nombres de columnas para evitar errores en Pandas.
    """
    return (
        str(columna)
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )


def detectar_fila_cabecera(df_raw: pd.DataFrame) -> int:
    """
    Busca dinámicamente la fila real de encabezados.
    Se prioriza la presencia de 'Fecha', pero también se consideran otras palabras de control.
    """
    palabras_control = [
        "fecha",
        "proceso",
        "auditor",
        "requisito",
        "hallazgo",
        "cumplimiento",
        "estatus",
        "codigo",
        "código",
    ]

    max_filas = min(12, len(df_raw))

    for idx in range(max_filas):
        valores_fila = [
            str(valor).strip().lower()
            for valor in df_raw.iloc[idx].values
            if pd.notna(valor) and str(valor).strip() != ""
        ]

        if any("fecha" == valor or "fecha" in valor for valor in valores_fila):
            return idx

        coincidencias = 0

        for valor in valores_fila:
            if any(palabra in valor for palabra in palabras_control):
                coincidencias += 1

        if coincidencias >= 2:
            return idx

    return 0


def eliminar_columnas_invalidas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina columnas vacías, duplicadas, Unnamed, nan o columnas generadas por desplazamientos.
    """
    df = df.copy()

    columnas_limpias = []
    columnas_usadas = set()

    for idx, col in enumerate(df.columns):
        col_limpia = limpiar_nombre_columna(col)

        if (
            col_limpia == ""
            or col_limpia.lower() == "nan"
            or col_limpia.lower().startswith("unnamed")
        ):
            col_limpia = f"columna_vacia_{idx}"

        if col_limpia in columnas_usadas:
            col_limpia = f"{col_limpia}_{idx}"

        columnas_limpias.append(col_limpia)
        columnas_usadas.add(col_limpia)

    df.columns = columnas_limpias

    columnas_validas = [
        col for col in df.columns
        if not col.lower().startswith("columna_vacia")
        and col.strip() != ""
        and col.lower() != "nan"
        and not col.lower().startswith("unnamed")
    ]

    return df[columnas_validas]


def normalizar_dataframe(df_raw: pd.DataFrame, tipo_tabla: str) -> pd.DataFrame:
    """
    Normaliza estructura de datos procedente de Google Sheets.
    """
    if df_raw is None or df_raw.empty:
        columnas = COLUMNAS_MATRIZ if tipo_tabla == "matriz" else COLUMNAS_SAC_OM
        return pd.DataFrame(columns=columnas)

    df = df_raw.copy()

    fila_cabecera = detectar_fila_cabecera(df)

    df.columns = df.iloc[fila_cabecera].apply(limpiar_nombre_columna)
    df = df.iloc[fila_cabecera + 1:].reset_index(drop=True)

    df = eliminar_columnas_invalidas(df)

    df.columns = [limpiar_nombre_columna(col) for col in df.columns]

    df = df.rename(columns=MAPEO_COLUMNAS)

    df = df.dropna(how="all").reset_index(drop=True)

    for col in df.columns:
        df[col] = df[col].astype(str).replace("nan", "").str.strip()

    columnas_requeridas = COLUMNAS_MATRIZ if tipo_tabla == "matriz" else COLUMNAS_SAC_OM

    for columna in columnas_requeridas:
        if columna not in df.columns:
            df[columna] = ""

    df = df[columnas_requeridas]

    if "proceso_auditado" in df.columns:
        df = df[df["proceso_auditado"].astype(str).str.strip() != ""]

    df = asegurar_ids(df)

    return df.reset_index(drop=True)


def asegurar_ids(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garantiza que exista una columna id numérica y completa.
    """
    df = df.copy()

    if "id" not in df.columns:
        df["id"] = ""

    ids = pd.to_numeric(df["id"], errors="coerce")

    nuevos_ids = []
    usados = set()
    siguiente = 1

    for valor in ids:
        if pd.notna(valor):
            candidato = int(valor)

            if candidato not in usados:
                nuevos_ids.append(candidato)
                usados.add(candidato)
                siguiente = max(siguiente, candidato + 1)
                continue

        while siguiente in usados:
            siguiente += 1

        nuevos_ids.append(siguiente)
        usados.add(siguiente)
        siguiente += 1

    df["id"] = nuevos_ids

    return df


@st.cache_data(ttl=600, show_spinner="Cargando datos desde Google Sheets...")
def cargar_google_sheet_csv(url: str, tipo_tabla: str) -> pd.DataFrame:
    """
    Carga una pestaña de Google Sheets usando Pandas y CSV público.
    """
    try:
        url_csv = convertir_url_google_sheets_a_csv(url)

        df_raw = pd.read_csv(
            url_csv,
            header=None,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8",
        )

        return normalizar_dataframe(df_raw, tipo_tabla)

    except Exception as e:
        st.error(
            f"No se pudo cargar la fuente de datos '{tipo_tabla}'. "
            f"Verifique permisos del Google Sheet, conexión o estructura de encabezados."
        )

        with st.expander("Ver detalle técnico del error"):
            st.exception(e)

        columnas = COLUMNAS_MATRIZ if tipo_tabla == "matriz" else COLUMNAS_SAC_OM
        return pd.DataFrame(columns=columnas)


def crear_excel_respaldo(df_matriz: pd.DataFrame, df_sac_om: pd.DataFrame) -> bytes:
    """
    Genera un archivo Excel de respaldo en memoria.
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_matriz.to_excel(writer, index=False, sheet_name="Matriz")
        df_sac_om.to_excel(writer, index=False, sheet_name="SAC_OM")

    output.seek(0)
    return output.getvalue()


def limpiar_texto_serie(serie: pd.Series) -> pd.Series:
    return serie.astype(str).str.strip()


def filtrar_opciones_validas(df: pd.DataFrame, columna: str) -> list:
    if columna not in df.columns:
        return []

    valores = (
        df[columna]
        .dropna()
        .astype(str)
        .str.strip()
    )

    valores = valores[
        (valores != "")
        & (valores.str.lower() != "nan")
        & (valores.str.lower() != "none")
    ]

    return sorted(valores.unique().tolist())


def mostrar_tarjeta_metrica(titulo: str, valor: str, descripcion: str):
    st.markdown(
        f"""
        <div class='metric-card'>
            <h3>{titulo}</h3>
            <h2>{valor}</h2>
            <p>{descripcion}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CARGA DE DATOS
# ============================================================

df_matriz = cargar_google_sheet_csv(URL_MATRIZ, "matriz")
df_sac_om = cargar_google_sheet_csv(URL_SAC_OM, "sac_om")

# Compatibilidad si en alguna parte del código anterior se usaba df.
df = df_matriz.copy()


# ============================================================
# MENÚ LATERAL
# ============================================================

st.sidebar.title("SGC ISO 9001:2015")
st.sidebar.markdown("*Dashboard de Auditoría Interna*")
st.sidebar.write("---")

opcion = st.sidebar.radio(
    "Seleccione un módulo:",
    [
        "📊 Dashboard de Dirección",
        "📋 Matriz de Hallazgos",
        "🛠 Seguimiento SAC / OM",
        "💾 Exportar Respaldo",
        "ℹ️ Diagnóstico de Datos",
    ],
)

st.sidebar.write("---")

if st.sidebar.button("🔄 Actualizar datos"):
    st.cache_data.clear()
    st.rerun()


# ============================================================
# MÓDULO 1: DASHBOARD
# ============================================================

if opcion == "📊 Dashboard de Dirección":
    st.title("📊 Dashboard Ejecutivo de Calidad")
    st.markdown("Indicadores calculados desde las pestañas públicas de Google Sheets.")

    if df_matriz.empty:
        st.warning("No se encontraron datos válidos en la Matriz de Hallazgos.")
        st.stop()

    df_dashboard = df_matriz.copy()

    procesos = filtrar_opciones_validas(df_dashboard, "proceso_auditado")
    requisitos = filtrar_opciones_validas(df_dashboard, "requisito_iso")
    auditores = filtrar_opciones_validas(df_dashboard, "auditor_responsable")

    with st.sidebar:
        st.subheader("Filtros")

        proceso_sel = st.multiselect(
            "Proceso auditado:",
            procesos,
            default=procesos,
        )

        requisito_sel = st.multiselect(
            "Requisito ISO:",
            requisitos,
            default=requisitos,
        )

        auditor_sel = st.multiselect(
            "Auditor responsable:",
            auditores,
            default=auditores,
        )

    if proceso_sel:
        df_dashboard = df_dashboard[df_dashboard["proceso_auditado"].isin(proceso_sel)]

    if requisito_sel:
        df_dashboard = df_dashboard[df_dashboard["requisito_iso"].isin(requisito_sel)]

    if auditor_sel:
        df_dashboard = df_dashboard[df_dashboard["auditor_responsable"].isin(auditor_sel)]

    df_dashboard["tipo_hallazgo_clean"] = limpiar_texto_serie(df_dashboard["tipo_hallazgo"])
    df_dashboard["cumplimiento_clean"] = limpiar_texto_serie(df_dashboard["cumplimiento"]).str.lower()

    df_evaluados = df_dashboard[
        (df_dashboard["tipo_hallazgo_clean"] != "")
        & (df_dashboard["tipo_hallazgo_clean"].str.lower() != "nan")
    ].copy()

    if df_evaluados.empty:
        st.info("La matriz no contiene requisitos evaluados según los filtros seleccionados.")
        st.dataframe(df_dashboard, use_container_width=True, hide_index=True)
    else:
        df_evaluados["is_conforme"] = df_evaluados["cumplimiento_clean"] == "conforme"

        total_evaluados = len(df_evaluados)
        total_conformes = int(df_evaluados["is_conforme"].sum())
        total_no_conformes = total_evaluados - total_conformes
        grado_global = (total_conformes / total_evaluados) * 100 if total_evaluados > 0 else 0

        planes_abiertos = 0

        if not df_sac_om.empty and "estatus_plan" in df_sac_om.columns:
            planes_abiertos = len(
                df_sac_om[
                    df_sac_om["estatus_plan"].astype(str).str.strip().str.lower().isin(
                        ["abierto", "en ejecución", "pendiente verificar"]
                    )
                ]
            )

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            mostrar_tarjeta_metrica(
                "Grado de Conformidad Global",
                f"{grado_global:.2f}%",
                "Sobre requisitos evaluados",
            )

        with k2:
            mostrar_tarjeta_metrica(
                "Requisitos Evaluados",
                str(total_evaluados),
                "Registros con hallazgo definido",
            )

        with k3:
            mostrar_tarjeta_metrica(
                "No Conformidades",
                str(total_no_conformes),
                "Requisitos no conformes",
            )

        with k4:
            mostrar_tarjeta_metrica(
                "Planes SAC / OM Abiertos",
                str(planes_abiertos),
                "Acciones pendientes o en proceso",
            )

        st.write("---")

        st.subheader("1. Grado de Conformidad por Proceso Auditado")

        proc_stats = (
            df_evaluados.groupby("proceso_auditado", dropna=False)["is_conforme"]
            .mean()
            .reset_index()
        )

        proc_stats["Conformidad"] = proc_stats["is_conforme"] * 100

        fig_proc = px.bar(
            proc_stats,
            x="proceso_auditado",
            y="Conformidad",
            text_auto=".1f",
            color_discrete_sequence=["#1E3A8A"],
        )

        fig_proc.add_hline(
            y=100,
            line_dash="dash",
            line_color="#EF4444",
            annotation_text="Meta SGC",
        )

        fig_proc.update_layout(
            yaxis_range=[0, 110],
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Proceso auditado",
            yaxis_title="% Conformidad",
        )

        st.plotly_chart(fig_proc, use_container_width=True)

        col_izq, col_der = st.columns(2)

        with col_izq:
            st.subheader("2. Conformidad por Cláusula ISO 9001")

            req_stats = (
                df_evaluados.groupby("requisito_iso", dropna=False)["is_conforme"]
                .mean()
                .reset_index()
            )

            req_stats["Conformidad"] = req_stats["is_conforme"] * 100

            fig_req = px.bar(
                req_stats,
                x="requisito_iso",
                y="Conformidad",
                text_auto=".1f",
                color_discrete_sequence=["#3B82F6"],
            )

            fig_req.update_layout(
                yaxis_range=[0, 110],
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Cláusula ISO 9001",
                yaxis_title="% Conformidad",
            )

            st.plotly_chart(fig_req, use_container_width=True)

        with col_der:
            st.subheader("3. Distribución de Tipos de Hallazgo")

            hallazgos = df_evaluados[
                df_evaluados["tipo_hallazgo"].astype(str).str.strip() != ""
            ]

            if hallazgos.empty:
                st.info("No hay tipos de hallazgo disponibles para graficar.")
            else:
                fig_hallazgos = px.pie(
                    hallazgos,
                    names="tipo_hallazgo",
                    hole=0.35,
                )

                fig_hallazgos.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                )

                st.plotly_chart(fig_hallazgos, use_container_width=True)

        st.subheader("4. Distribución de Estatus de Acciones SAC / OM")

        if df_sac_om.empty:
            st.info("No se encontraron datos válidos en la pestaña SAC / OM.")
        else:
            fig_sac = px.histogram(
                df_sac_om,
                x="tipo_plan",
                color="estatus_plan",
                barmode="group",
                color_discrete_map={
                    "Cerrado": "#10B981",
                    "Abierto": "#1E3A8A",
                    "En ejecución": "#3B82F6",
                    "Pendiente verificar": "#F59E0B",
                },
            )

            fig_sac.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Tipo de plan",
                yaxis_title="Cantidad",
            )

            st.plotly_chart(fig_sac, use_container_width=True)


# ============================================================
# MÓDULO 2: MATRIZ DE HALLAZGOS
# ============================================================

elif opcion == "📋 Matriz de Hallazgos":
    st.title("📋 Matriz de Hallazgos")

    if df_matriz.empty:
        st.warning("No se encontraron datos válidos en la Matriz de Hallazgos.")
    else:
        procesos = filtrar_opciones_validas(df_matriz, "proceso_auditado")
        tipos = filtrar_opciones_validas(df_matriz, "tipo_hallazgo")
        cumplimientos = filtrar_opciones_validas(df_matriz, "cumplimiento")

        c1, c2, c3 = st.columns(3)

        with c1:
            proceso = st.selectbox("Filtrar por proceso:", ["Todos"] + procesos)

        with c2:
            tipo = st.selectbox("Filtrar por tipo de hallazgo:", ["Todos"] + tipos)

        with c3:
            cumplimiento = st.selectbox("Filtrar por cumplimiento:", ["Todos"] + cumplimientos)

        df_vista = df_matriz.copy()

        if proceso != "Todos":
            df_vista = df_vista[df_vista["proceso_auditado"] == proceso]

        if tipo != "Todos":
            df_vista = df_vista[df_vista["tipo_hallazgo"] == tipo]

        if cumplimiento != "Todos":
            df_vista = df_vista[df_vista["cumplimiento"] == cumplimiento]

        st.dataframe(
            df_vista,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Modo lectura: los datos se consumen desde Google Sheets por CSV. "
            "Para editar registros, modifique directamente la hoja de cálculo."
        )


# ============================================================
# MÓDULO 3: SEGUIMIENTO SAC / OM
# ============================================================

elif opcion == "🛠 Seguimiento SAC / OM":
    st.title("🛠 Seguimiento de Acciones SAC / OM")

    if df_sac_om.empty:
        st.warning("No se encontraron datos válidos en la pestaña SAC / OM.")
    else:
        tipos_plan = filtrar_opciones_validas(df_sac_om, "tipo_plan")
        estatus_plan = filtrar_opciones_validas(df_sac_om, "estatus_plan")
        estatus_eficacia = filtrar_opciones_validas(df_sac_om, "estatus_eficacia")

        c1, c2, c3 = st.columns(3)

        with c1:
            tipo_plan_sel = st.selectbox("Filtrar por tipo de plan:", ["Todos"] + tipos_plan)

        with c2:
            estatus_plan_sel = st.selectbox("Filtrar por estatus del plan:", ["Todos"] + estatus_plan)

        with c3:
            estatus_eficacia_sel = st.selectbox("Filtrar por eficacia:", ["Todos"] + estatus_eficacia)

        df_vista = df_sac_om.copy()

        if tipo_plan_sel != "Todos":
            df_vista = df_vista[df_vista["tipo_plan"] == tipo_plan_sel]

        if estatus_plan_sel != "Todos":
            df_vista = df_vista[df_vista["estatus_plan"] == estatus_plan_sel]

        if estatus_eficacia_sel != "Todos":
            df_vista = df_vista[df_vista["estatus_eficacia"] == estatus_eficacia_sel]

        st.dataframe(
            df_vista,
            use_container_width=True,
            hide_index=True,
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            mostrar_tarjeta_metrica(
                "Total de acciones",
                str(len(df_vista)),
                "Según filtros aplicados",
            )

        with col2:
            abiertas = len(
                df_vista[
                    df_vista["estatus_plan"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .isin(["abierto", "en ejecución", "pendiente verificar"])
                ]
            )

            mostrar_tarjeta_metrica(
                "Acciones abiertas",
                str(abiertas),
                "Pendientes o en seguimiento",
            )

        with col3:
            cerradas = len(
                df_vista[
                    df_vista["estatus_plan"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    == "cerrado"
                ]
            )

            mostrar_tarjeta_metrica(
                "Acciones cerradas",
                str(cerradas),
                "Cerradas según estatus",
            )


# ============================================================
# MÓDULO 4: EXPORTAR RESPALDO
# ============================================================

elif opcion == "💾 Exportar Respaldo":
    st.title("💾 Exportar Respaldo")

    st.markdown(
        "Descarga un respaldo consolidado en Excel con la Matriz de Hallazgos "
        "y el Seguimiento SAC / OM."
    )

    archivo_excel = crear_excel_respaldo(df_matriz, df_sac_om)

    st.download_button(
        label="⬇️ Descargar respaldo Excel",
        data=archivo_excel,
        file_name=f"respaldo_sgc_{date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    tab1, tab2 = st.tabs(["Matriz de Hallazgos", "SAC / OM"])

    with tab1:
        st.dataframe(df_matriz, use_container_width=True, hide_index=True)

    with tab2:
        st.dataframe(df_sac_om, use_container_width=True, hide_index=True)


# ============================================================
# MÓDULO 5: DIAGNÓSTICO
# ============================================================

elif opcion == "ℹ️ Diagnóstico de Datos":
    st.title("ℹ️ Diagnóstico de Datos")

    st.subheader("Matriz de Hallazgos")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Filas", len(df_matriz))

    with c2:
        st.metric("Columnas", len(df_matriz.columns))

    with c3:
        st.metric("Procesos", df_matriz["proceso_auditado"].nunique() if not df_matriz.empty else 0)

    st.write("Columnas detectadas:")
    st.code(", ".join(df_matriz.columns.tolist()))

    st.dataframe(df_matriz.head(20), use_container_width=True, hide_index=True)

    st.write("---")

    st.subheader("Seguimiento SAC / OM")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Filas", len(df_sac_om))

    with c2:
        st.metric("Columnas", len(df_sac_om.columns))

    with c3:
        st.metric("Tipos de plan", df_sac_om["tipo_plan"].nunique() if not df_sac_om.empty else 0)

    st.write("Columnas detectadas:")
    st.code(", ".join(df_sac_om.columns.tolist()))

    st.dataframe(df_sac_om.head(20), use_container_width=True, hide_index=True)
