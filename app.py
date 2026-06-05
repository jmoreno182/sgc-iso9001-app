import io
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_gsheets import GSheetsConnection


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Gestión SGC - Google Sheets Cloud",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
    .main {
        background-color: #F8FAFC;
    }

    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
    }

    .stButton>button:hover {
        background-color: #1D4ED8;
        color: white;
    }

    h1, h2, h3 {
        color: #1E3A8A;
        font-family: 'Segoe UI', sans-serif;
    }

    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 5px solid #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# CONSTANTES
# ============================================================

WORKSHEET_MATRIZ = "Matriz"
WORKSHEET_SAC_OM = "SAC_OM"

COLUMNAS_REQUERIDAS = {
    "Matriz": [
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
    ],
    "SAC_OM": [
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
    ],
}

MAPEO_COLUMNAS = {
    "Fecha": "fecha",
    "Proceso Auditado": "proceso_auditado",
    "Proceso auditado": "proceso_auditado",
    "Auditor Responsable": "auditor_responsable",
    "Auditor responsable": "auditor_responsable",
    "Requisito ISO 9001:2015": "requisito_iso",
    "Requisito específico ISO 9001:2015": "requisito_especifico",
    "Requisito Específico ISO 9001:2015": "requisito_especifico",
    "Requisito Interno / Legal": "requisito_interno_legal",
    "Tipo de Hallazgo": "tipo_hallazgo",
    "Tipo de hallazgo": "tipo_hallazgo",
    "Cumplimiento del requisito": "cumplimiento",
    "Cumplimiento": "cumplimiento",
    "Evidencia objetiva de NC": "evidencia_objetiva",
    "Evidencia objetiva": "evidencia_objetiva",
    "Observaciones / comentarios adicionales": "observaciones",
    "Observaciones": "observaciones",
    "Tipo de plan": "tipo_plan",
    "Tipo de Plan": "tipo_plan",
    "Código": "codigo",
    "Codigo": "codigo",
    "Estatus del plan": "estatus_plan",
    "Estatus del Plan": "estatus_plan",
    "Estatus de la eficacia": "estatus_eficacia",
    "Estatus de la Eficacia": "estatus_eficacia",
    "id": "id",
    "ID": "id",
}


# ============================================================
# FUNCIONES DE APOYO
# ============================================================

def limpiar_nombre_columna(columna: str) -> str:
    return (
        str(columna)
        .replace("\n", " ")
        .strip()
    )


def detectar_y_reasignar_cabecera(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta si la cabecera real está dentro de las primeras filas del DataFrame.
    Esto ayuda cuando Google Sheets tiene filas vacías o títulos institucionales antes de la tabla.
    """
    if df.empty:
        return df

    palabras_clave = ["fecha", "proceso", "auditor", "requisito", "hallazgo", "estatus"]

    for idx in range(min(8, len(df))):
        valores = [
            str(valor).strip().lower()
            for valor in df.iloc[idx].values
            if pd.notna(valor)
        ]

        coincidencias = sum(
            any(palabra in valor for palabra in palabras_clave)
            for valor in valores
        )

        if coincidencias >= 2:
            nuevas_columnas = [
                limpiar_nombre_columna(valor) if pd.notna(valor) and str(valor).strip() != ""
                else f"columna_vacia_{pos}"
                for pos, valor in enumerate(df.iloc[idx].values)
            ]

            df = df.iloc[idx + 1:].copy()
            df.columns = nuevas_columnas
            return df.reset_index(drop=True)

    return df


def normalizar_dataframe(df: pd.DataFrame, tipo_tabla: str) -> pd.DataFrame:
    """
    Normaliza columnas, elimina filas vacías y garantiza columnas mínimas.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=COLUMNAS_REQUERIDAS[tipo_tabla])

    df = df.copy()

    df = detectar_y_reasignar_cabecera(df)

    df.columns = [
        limpiar_nombre_columna(col)
        for col in df.columns
    ]

    df = df.loc[:, ~pd.Series(df.columns).astype(str).str.lower().str.match(r"^unnamed|^nan$").values]

    df = df.rename(columns=MAPEO_COLUMNAS)

    for columna in COLUMNAS_REQUERIDAS[tipo_tabla]:
        if columna not in df.columns:
            df[columna] = ""

    df = df[COLUMNAS_REQUERIDAS[tipo_tabla]]

    df = df.dropna(how="all").reset_index(drop=True)

    if "proceso_auditado" in df.columns:
        df = df[df["proceso_auditado"].astype(str).str.strip() != ""]

    df = asegurar_ids(df)

    return df.reset_index(drop=True)


def asegurar_ids(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garantiza IDs numéricos, únicos y completos.
    """
    df = df.copy()

    if "id" not in df.columns:
        df["id"] = ""

    df["id"] = pd.to_numeric(df["id"], errors="coerce")

    siguiente_id = 1
    ids_generados = []

    for valor in df["id"]:
        if pd.notna(valor) and int(valor) not in ids_generados:
            ids_generados.append(int(valor))
            siguiente_id = max(siguiente_id, int(valor) + 1)
        else:
            while siguiente_id in ids_generados:
                siguiente_id += 1
            ids_generados.append(siguiente_id)
            siguiente_id += 1

    df["id"] = ids_generados

    return df


@st.cache_data(ttl=60)
def cargar_datos(_conn):
    """
    Carga datos desde Google Sheets.
    El TTL de 60 segundos evita recargar la hoja en cada interacción menor.
    """
    matriz_raw = _conn.read(worksheet=WORKSHEET_MATRIZ)
    sac_raw = _conn.read(worksheet=WORKSHEET_SAC_OM)

    matriz = normalizar_dataframe(matriz_raw, "Matriz")
    sac_om = normalizar_dataframe(sac_raw, "SAC_OM")

    return matriz, sac_om


def actualizar_hoja(conn, worksheet: str, df: pd.DataFrame):
    """
    Actualiza Google Sheets y limpia caché para refrescar los datos.
    """
    conn.update(worksheet=worksheet, data=df)
    st.cache_data.clear()


def obtener_indice_seguro(lista, valor_actual, valor_default=0):
    """
    Devuelve el índice de un valor dentro de una lista.
    Si no existe, devuelve un índice por defecto.
    """
    try:
        return lista.index(str(valor_actual).strip())
    except ValueError:
        return valor_default


def crear_excel_respaldo(df_matriz: pd.DataFrame, df_sac_om: pd.DataFrame) -> bytes:
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_matriz.to_excel(writer, index=False, sheet_name="Matriz")
        df_sac_om.to_excel(writer, index=False, sheet_name="SAC_OM")

    output.seek(0)
    return output.getvalue()


# ============================================================
# CONEXIÓN
# ============================================================

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_matriz, df_sac = cargar_datos(conn)

except Exception as e:
    st.error(f"⚠️ Error de conexión o lectura de Google Sheets: {e}")
    st.info(
        "Verifique que la conexión `gsheets` esté configurada correctamente "
        "y que existan las pestañas `Matriz` y `SAC_OM`."
    )
    st.stop()


# ============================================================
# MENÚ LATERAL
# ============================================================

st.sidebar.image("https://img.icons8.com/fluency/96/google-sheets.png", width=70)
st.sidebar.title("SGC ISO 9001:2015")
st.sidebar.markdown("*Control sincronizado en la nube*")
st.sidebar.write("---")

opcion = st.sidebar.radio(
    "Seleccione un módulo:",
    [
        "📊 Dashboard de Dirección",
        "📝 Matriz de Hallazgos",
        "⚙️ Seguimiento SAC / OM",
        "💾 Exportar Respaldo",
    ],
)


# ============================================================
# MÓDULO 1: DASHBOARD
# ============================================================

if opcion == "📊 Dashboard de Dirección":
    st.title("📊 Dashboard Ejecutivo de Calidad")
    st.markdown("Indicadores calculados dinámicamente desde Google Sheets.")

    if df_matriz.empty:
        st.warning("La matriz de hallazgos no contiene datos disponibles.")
        st.stop()

    df_eval = df_matriz.copy()
    df_eval["tipo_hallazgo_clean"] = df_eval["tipo_hallazgo"].astype(str).str.strip()
    df_eval = df_eval[
        (df_eval["tipo_hallazgo_clean"] != "")
        & (df_eval["tipo_hallazgo_clean"].str.lower() != "nan")
    ].copy()

    if df_eval.empty:
        st.info(
            "La matriz no contiene requisitos evaluados todavía. "
            "Registre hallazgos en el módulo de Matriz de Hallazgos."
        )
    else:
        df_eval["is_conforme"] = (
            df_eval["cumplimiento"].astype(str).str.strip().str.lower() == "conforme"
        )

        total_evaluados = len(df_eval)
        total_conformes = int(df_eval["is_conforme"].sum())
        grado_global = (total_conformes / total_evaluados) * 100 if total_evaluados else 0

        planes_abiertos = 0
        if not df_sac.empty:
            planes_abiertos = len(
                df_sac[
                    df_sac["estatus_plan"].astype(str).str.strip().str.lower() == "abierto"
                ]
            )

        k1, k2, k3 = st.columns(3)

        with k1:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h3>Grado de Conformidad Global</h3>
                    <h2>{grado_global:.2f}%</h2>
                    <p>Sobre requisitos evaluados</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with k2:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h3>Requisitos Evaluados</h3>
                    <h2>{total_evaluados}</h2>
                    <p>Avance del plan de auditoría</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with k3:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h3>Planes SAC / OM Abiertos</h3>
                    <h2>{planes_abiertos}</h2>
                    <p>Pendientes por cierre o verificación</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("---")

        st.subheader("1. Grado de Conformidad por Proceso Auditado")

        proc_stats = (
            df_eval.groupby("proceso_auditado", dropna=False)["is_conforme"]
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
                df_eval.groupby("requisito_iso", dropna=False)["is_conforme"]
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
            st.subheader("3. Estatus de Acciones SAC / OM")

            if df_sac.empty:
                st.info("No hay acciones SAC / OM registradas.")
            else:
                fig_sac = px.histogram(
                    df_sac,
                    x="tipo_plan",
                    color="estatus_plan",
                    barmode="group",
                    color_discrete_map={
                        "Cerrado": "#10B981",
                        "Abierto": "#1E3A8A",
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

elif opcion == "📝 Matriz de Hallazgos":
    st.title("📝 Matriz de Hallazgos en la Nube")

    tab1, tab2 = st.tabs(
        ["🔄 Evaluar Requisitos", "➕ Agregar Requisito"]
    )

    with tab1:
        if df_matriz.empty:
            st.warning("No existen registros en la matriz.")
        else:
            procesos = sorted(
                df_matriz["proceso_auditado"]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
                .tolist()
            )

            if not procesos:
                st.warning("No hay procesos disponibles para evaluar.")
            else:
                proc_sel = st.selectbox(
                    "Seleccione el proceso en evaluación:",
                    procesos,
                )

                df_proc = df_matriz[
                    df_matriz["proceso_auditado"].astype(str).str.strip() == proc_sel
                ].copy()

                st.dataframe(
                    df_proc[
                        [
                            "id",
                            "requisito_iso",
                            "requisito_especifico",
                            "tipo_hallazgo",
                            "cumplimiento",
                            "observaciones",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

                id_sel = st.selectbox(
                    "ID del requisito a calificar:",
                    df_proc["id"].tolist(),
                )

                idx_row = df_matriz[df_matriz["id"] == id_sel].index[0]
                fila = df_matriz.loc[idx_row]

                opciones_hallazgo = [
                    "Conforme",
                    "No Conforme",
                    "Oportunidad de mejora",
                ]
                opciones_cumplimiento = [
                    "Conforme",
                    "No Conforme",
                ]

                with st.form(key=f"form_matriz_{id_sel}"):
                    c1, c2 = st.columns(2)

                    with c1:
                        st.info(
                            f"**Cláusula ISO:** {fila['requisito_iso']}  \n"
                            f"**Detalle:** {fila['requisito_especifico']}"
                        )

                        tipo_h = st.selectbox(
                            "Tipo de Hallazgo:",
                            opciones_hallazgo,
                            index=obtener_indice_seguro(
                                opciones_hallazgo,
                                fila["tipo_hallazgo"],
                                0,
                            ),
                        )

                    with c2:
                        cump = st.selectbox(
                            "Cumplimiento:",
                            opciones_cumplimiento,
                            index=obtener_indice_seguro(
                                opciones_cumplimiento,
                                fila["cumplimiento"],
                                0,
                            ),
                        )

                    evid = st.text_area(
                        "Evidencia objetiva hallada:",
                        value="" if pd.isna(fila["evidencia_objetiva"]) else str(fila["evidencia_objetiva"]),
                    )

                    obs = st.text_area(
                        "Observaciones técnicas:",
                        value="" if pd.isna(fila["observaciones"]) else str(fila["observaciones"]),
                    )

                    guardar = st.form_submit_button("Sincronizar con Google Sheets")

                    if guardar:
                        df_matriz.at[idx_row, "tipo_hallazgo"] = tipo_h
                        df_matriz.at[idx_row, "cumplimiento"] = cump
                        df_matriz.at[idx_row, "evidencia_objetiva"] = evid
                        df_matriz.at[idx_row, "observaciones"] = obs

                        actualizar_hoja(conn, WORKSHEET_MATRIZ, df_matriz)

                        st.success("Datos sincronizados exitosamente.")
                        st.rerun()

    with tab2:
        st.subheader("Incorporar un requisito adicional")

        with st.form("form_nueva_fila_matriz"):
            col1, col2 = st.columns(2)

            with col1:
                n_fecha = st.date_input("Fecha:", value=date.today())
                n_proc = st.text_input("Proceso auditado:")
                n_auditor = st.text_input("Auditor responsable:")
                n_iso = st.text_input("Cláusula ISO 9001:2015:")

            with col2:
                n_esp = st.text_input("Requisito específico:")
                n_legal = st.text_input("Requisito interno / legal:")
                n_tipo = st.selectbox(
                    "Tipo de hallazgo:",
                    ["Conforme", "No Conforme", "Oportunidad de mejora"],
                )
                n_cump = st.selectbox(
                    "Cumplimiento:",
                    ["Conforme", "No Conforme"],
                )

            n_evid = st.text_area("Evidencia objetiva:")
            n_obs = st.text_area("Observaciones:")

            insertar = st.form_submit_button("Insertar nueva fila")

            if insertar:
                nuevo_id = int(df_matriz["id"].max() + 1) if not df_matriz.empty else 1

                nueva_fila = {
                    "id": nuevo_id,
                    "fecha": n_fecha.strftime("%Y-%m-%d"),
                    "proceso_auditado": n_proc.strip().upper(),
                    "auditor_responsable": n_auditor.strip(),
                    "requisito_iso": n_iso.strip(),
                    "requisito_especifico": n_esp.strip(),
                    "requisito_interno_legal": n_legal.strip(),
                    "tipo_hallazgo": n_tipo,
                    "cumplimiento": n_cump,
                    "evidencia_objetiva": n_evid.strip(),
                    "observaciones": n_obs.strip(),
                }

                df_matriz = pd.concat(
                    [df_matriz, pd.DataFrame([nueva_fila])],
                    ignore_index=True,
                )

                actualizar_hoja(conn, WORKSHEET_MATRIZ, df_matriz)

                st.success("Fila añadida exitosamente.")
                st.rerun()


# ============================================================
# MÓDULO 3: SEGUIMIENTO SAC / OM
# ============================================================

elif opcion == "⚙️ Seguimiento SAC / OM":
    st.title("⚙️ Control de Acciones Correctivas y Oportunidades de Mejora")

    tab1, tab2 = st.tabs(
        ["🔎 Seguimiento de acciones", "➕ Registrar acción"]
    )

    with tab1:
        if df_sac.empty:
            st.warning("No existen acciones SAC / OM registradas.")
        else:
            st.dataframe(df_sac, use_container_width=True, hide_index=True)

            id_accion = st.selectbox(
                "Seleccione el ID de la acción:",
                df_sac["id"].tolist(),
            )

            idx = df_sac[df_sac["id"] == id_accion].index[0]
            fila = df_sac.loc[idx]

            opciones_estatus = [
                "Abierto",
                "En ejecución",
                "Pendiente verificar",
                "Cerrado",
            ]

            opciones_eficacia = [
                "No evaluada",
                "Eficaz",
                "No eficaz",
                "Pendiente verificar",
            ]

            with st.form(key=f"form_sac_{id_accion}"):
                c1, c2 = st.columns(2)

                with c1:
                    st.info(
                        f"**Código:** {fila['codigo']}  \n"
                        f"**Tipo de plan:** {fila['tipo_plan']}  \n"
                        f"**Proceso:** {fila['proceso_auditado']}"
                    )

                    estatus_plan = st.selectbox(
                        "Estatus del plan:",
                        opciones_estatus,
                        index=obtener_indice_seguro(
                            opciones_estatus,
                            fila["estatus_plan"],
                            0,
                        ),
                    )

                with c2:
                    estatus_eficacia = st.selectbox(
                        "Estatus de la eficacia:",
                        opciones_eficacia,
                        index=obtener_indice_seguro(
                            opciones_eficacia,
                            fila["estatus_eficacia"],
                            0,
                        ),
                    )

                observaciones = st.text_area(
                    "Observaciones de seguimiento:",
                    value="" if pd.isna(fila["observaciones"]) else str(fila["observaciones"]),
                )

                guardar_sac = st.form_submit_button("Actualizar seguimiento")

                if guardar_sac:
                    df_sac.at[idx, "estatus_plan"] = estatus_plan
                    df_sac.at[idx, "estatus_eficacia"] = estatus_eficacia
                    df_sac.at[idx, "observaciones"] = observaciones.strip()

                    actualizar_hoja(conn, WORKSHEET_SAC_OM, df_sac)

                    st.success("Seguimiento actualizado correctamente.")
                    st.rerun()

    with tab2:
        st.subheader("Registrar nueva acción SAC / OM")

        with st.form("form_nueva_accion"):
            c1, c2 = st.columns(2)

            with c1:
                a_fecha = st.date_input("Fecha:", value=date.today())
                a_proc = st.text_input("Proceso auditado:")
                a_auditor = st.text_input("Auditor responsable:")
                a_iso = st.text_input("Requisito ISO asociado:")

            with c2:
                a_tipo_plan = st.selectbox(
                    "Tipo de plan:",
                    ["SAC", "OM"],
                )
                a_codigo = st.text_input("Código del plan:")
                a_estatus = st.selectbox(
                    "Estatus del plan:",
                    ["Abierto", "En ejecución", "Pendiente verificar", "Cerrado"],
                )
                a_eficacia = st.selectbox(
                    "Estatus de la eficacia:",
                    ["No evaluada", "Eficaz", "No eficaz", "Pendiente verificar"],
                )

            a_obs = st.text_area("Observaciones:")

            registrar = st.form_submit_button("Registrar acción")

            if registrar:
                nuevo_id = int(df_sac["id"].max() + 1) if not df_sac.empty else 1

                nueva_accion = {
                    "id": nuevo_id,
                    "fecha": a_fecha.strftime("%Y-%m-%d"),
                    "proceso_auditado": a_proc.strip().upper(),
                    "auditor_responsable": a_auditor.strip(),
                    "requisito_iso": a_iso.strip(),
                    "tipo_plan": a_tipo_plan,
                    "codigo": a_codigo.strip().upper(),
                    "estatus_plan": a_estatus,
                    "estatus_eficacia": a_eficacia,
                    "observaciones": a_obs.strip(),
                }

                df_sac = pd.concat(
                    [df_sac, pd.DataFrame([nueva_accion])],
                    ignore_index=True,
                )

                actualizar_hoja(conn, WORKSHEET_SAC_OM, df_sac)

                st.success("Acción registrada correctamente.")
                st.rerun()


# ============================================================
# MÓDULO 4: EXPORTAR RESPALDO
# ============================================================

elif opcion == "💾 Exportar Respaldo":
    st.title("💾 Exportar Respaldo del SGC")

    st.markdown(
        "Desde este módulo puede descargar un respaldo consolidado "
        "de la Matriz de Hallazgos y del seguimiento SAC / OM."
    )

    archivo_excel = crear_excel_respaldo(df_matriz, df_sac)

    st.download_button(
        label="⬇️ Descargar respaldo en Excel",
        data=archivo_excel,
        file_name=f"respaldo_sgc_{date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.subheader("Vista previa - Matriz")
    st.dataframe(df_matriz, use_container_width=True, hide_index=True)

    st.subheader("Vista previa - SAC / OM")
    st.dataframe(df_sac, use_container_width=True, hide_index=True)
