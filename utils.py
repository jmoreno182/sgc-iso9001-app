"""Shared utilities: validation, Google Sheets operations, cached computations."""

from typing import Tuple, Any
import pandas as pd
import streamlit as st


class ValidationError(Exception):
    """Raised when user input validation fails."""
    pass


# Constantes del módulo HORAS
PROCESOS_SGC = ["EV", "FP", "TR", "DR", "AC", "DD", "AA", "GI", "GM", "PB", "PP", "CO", "AS", "GP", "DI"]
ROLES_AUDITOR = ["OB", "AF", "AD", "AL"]
ROLES_DESCRIPCION = {"OB": "Observador", "AF": "Auditor en Formación", "AD": "Auditor Interno", "AL": "Auditor Líder"}


def safe_int_convert(val: Any, field_name: str) -> int:
    """Convert value to int. Raise ValidationError if invalid."""
    try:
        return int(val)
    except (ValueError, TypeError):
        raise ValidationError(f"Campo '{field_name}' debe ser número. Recibido: {val}")


def validate_required(val: Any, field_name: str) -> Any:
    """Check val not empty. Raise ValidationError if missing."""
    if not val or (isinstance(val, str) and val.strip() == ''):
        raise ValidationError(f"Campo requerido: '{field_name}'")
    return val


def validate_date(val: Any, field_name: str) -> pd.Timestamp:
    """Parse date string. Raise ValidationError if invalid."""
    if isinstance(val, str):
        try:
            return pd.to_datetime(val)
        except:
            raise ValidationError(f"Fecha inválida en '{field_name}': {val}")
    return val


def load_gsheets_data(max_retries: int = 3) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load Matriz and SAC_OM sheets from Google Sheets using gspread."""
    import gspread
    from google.oauth2.service_account import Credentials
    import re

    for attempt in range(max_retries):
        try:
            sheet_url = st.secrets.get("connections", {}).get("gsheets", {}).get("spreadsheet", "")
            if not sheet_url:
                raise ValueError("No spreadsheet URL in secrets: connections.gsheets.spreadsheet")

            sheet_id = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
            if not sheet_id:
                raise ValueError(f"Invalid spreadsheet URL format: {sheet_url}")
            sheet_id = sheet_id.group(1)

            creds_dict = st.secrets.get("GOOGLE_SERVICE_ACCOUNT_INFO")
            if not creds_dict:
                raise ValueError("No GOOGLE_SERVICE_ACCOUNT_INFO in secrets")

            creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
            gc = gspread.authorize(creds)
            sh = gc.open_by_key(sheet_id)

            df_matriz = pd.DataFrame(sh.worksheet("Matriz").get_all_records())
            df_sac = pd.DataFrame(sh.worksheet("SAC_OM").get_all_records())

            # Normalize column names: lowercase, strip whitespace
            df_matriz.columns = df_matriz.columns.str.strip().str.lower()
            df_sac.columns = df_sac.columns.str.strip().str.lower()

            # Expected columns mapping (handle variations)
            matriz_cols_map = {
                'id': 'id', 'fecha': 'fecha', 'proceso auditado': 'proceso_auditado',
                'proceso_auditado': 'proceso_auditado', 'auditor responsable': 'auditor_responsable',
                'auditor_responsable': 'auditor_responsable', 'requisito iso 9001:2015': 'requisito_iso',
                'requisito iso': 'requisito_iso', 'requisito_iso': 'requisito_iso',
                'requisito específico iso 9001:2015': 'requisito_especifico', 'requisito específico': 'requisito_especifico',
                'requisito_especifico': 'requisito_especifico', 'requisito interno / legal': 'requisito_interno_legal',
                'requisito_interno_legal': 'requisito_interno_legal', 'tipo de hallazgo': 'tipo_hallazgo',
                'tipo_hallazgo': 'tipo_hallazgo', 'cumplimiento del requisito': 'cumplimiento',
                'cumplimiento': 'cumplimiento', 'evidencia objetiva de nc': 'evidencia_objetiva',
                'evidencia_objetiva': 'evidencia_objetiva', 'observaciones / comentarios adicionales': 'observaciones',
                'observaciones': 'observaciones'
            }

            sac_cols_map = {
                'id': 'id', 'fecha': 'fecha', 'proceso auditado': 'proceso_auditado',
                'proceso_auditado': 'proceso_auditado', 'auditor responsable': 'auditor_responsable',
                'auditor_responsable': 'auditor_responsable', 'requisito iso': 'requisito_iso',
                'requisito_iso': 'requisito_iso', 'tipo de plan': 'tipo_plan', 'tipo_plan': 'tipo_plan',
                'codigo': 'codigo', 'codigo': 'codigo', 'estatus plan': 'estatus_plan',
                'estatus_plan': 'estatus_plan', 'estatus eficacia': 'estatus_la_eficacia',
                'estatus_la_eficacia': 'estatus_la_eficacia', 'estatus_eficacia': 'estatus_la_eficacia',
                'observaciones': 'observaciones'
            }

            df_matriz = df_matriz.rename(columns=matriz_cols_map)
            df_sac = df_sac.rename(columns=sac_cols_map)

            if df_matriz.empty:
                st.warning("⚠️ Hoja 'Matriz' vacía. Inicia ingresando requisitos.")

            if not df_sac.empty and 'id' not in df_sac.columns:
                st.warning("⚠️ Hoja 'SAC_OM' falta columna 'id'.")

            try:
                df_matriz['id'] = pd.to_numeric(df_matriz['id'], errors='coerce').fillna(0).astype(int)
            except Exception as e:
                st.warning(f"⚠️ Columna 'id' en Matriz contiene datos inválidos: {e}")

            if not df_sac.empty:
                try:
                    df_sac['id'] = pd.to_numeric(df_sac['id'], errors='coerce').fillna(0).astype(int)
                except Exception as e:
                    st.warning(f"⚠️ Columna 'id' en SAC_OM contiene datos inválidos: {e}")

            return df_matriz, df_sac

        except Exception as e:
            error_msg = str(e)
            print(f"DEBUG: Attempt {attempt + 1}/{max_retries} error: {error_msg}")
            import traceback
            traceback.print_exc()

            if attempt < max_retries - 1:
                st.warning(f"⚠️ Intento {attempt + 1}/{max_retries} falló. Reintentando...")
                continue
            else:
                st.error(f"❌ Error Google Sheets (intento {max_retries}/{max_retries}):")
                st.error(error_msg)
                st.info("**Debug:** Revisa console para más detalles")
                raise


@st.cache_data
def compute_conformidad_stats(df: pd.DataFrame) -> dict:
    """Cache conformity metrics. Recomputed only if df changes."""
    df_eval = df[df['tipo_hallazgo'].notna() & (df['tipo_hallazgo'] != '')]
    total = len(df_eval)
    conforme = len(df_eval[df_eval['cumplimiento'] == 'Conforme'])
    return {'total': total, 'conforme': conforme, 'pct': (conforme / total * 100) if total > 0 else 0}


@st.cache_data
def compute_process_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Cache process-level conformity. Recomputed only if df changes."""
    df_eval = df[df['tipo_hallazgo'].notna() & (df['tipo_hallazgo'] != '')]
    return df_eval.groupby('proceso_auditado').apply(
        lambda x: (sum(x['cumplimiento'] == 'Conforme') / len(x)) * 100
    ).reset_index(name='Conformidad')


@st.cache_data
def compute_requirement_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Cache requirement-level conformity. Recomputed only if df changes."""
    df_eval = df[df['tipo_hallazgo'].notna() & (df['tipo_hallazgo'] != '')]
    return df_eval.groupby('requisito_iso').apply(
        lambda x: (sum(x['cumplimiento'] == 'Conforme') / len(x)) * 100
    ).reset_index(name='Conformidad')


@st.cache_data
def compute_auditor_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Get unique processes per auditor with dates."""
    df_clean = df[df['auditor_responsable'].notna() & (df['auditor_responsable'] != '') &
                   df['proceso_auditado'].notna() & (df['proceso_auditado'] != '')]
    # Select unique auditor-proceso combinations
    return df_clean[['auditor_responsable', 'proceso_auditado', 'fecha']].drop_duplicates(
        subset=['auditor_responsable', 'proceso_auditado']
    ).sort_values('auditor_responsable')


@st.cache_data
def compute_conformidad_trend(df: pd.DataFrame) -> dict:
    """Calculate conformity trend (current vs previous period)."""
    if df.empty:
        return {'current': 0, 'previous': 0, 'trend': '→'}

    try:
        df['fecha'] = pd.to_datetime(df['fecha'])
        df_eval = df[df['tipo_hallazgo'].notna() & (df['tipo_hallazgo'] != '')]

        if df_eval.empty:
            return {'current': 0, 'previous': 0, 'trend': '→'}

        # Split by median date
        median_date = df_eval['fecha'].median()
        current = df_eval[df_eval['fecha'] >= median_date]
        previous = df_eval[df_eval['fecha'] < median_date]

        current_pct = (len(current[current['cumplimiento'] == 'Conforme']) / len(current) * 100) if len(current) > 0 else 0
        previous_pct = (len(previous[previous['cumplimiento'] == 'Conforme']) / len(previous) * 100) if len(previous) > 0 else 0

        trend = '↑' if current_pct > previous_pct else '↓' if current_pct < previous_pct else '→'

        return {'current': round(current_pct, 1), 'previous': round(previous_pct, 1), 'trend': trend}
    except:
        return {'current': 0, 'previous': 0, 'trend': '→'}


@st.cache_data
def compute_auditor_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Compare productivity and conformity by auditor."""
    df_clean = df[df['auditor_responsable'].notna() & (df['auditor_responsable'] != '') &
                   df['tipo_hallazgo'].notna() & (df['tipo_hallazgo'] != '')]

    if df_clean.empty:
        return pd.DataFrame()

    return df_clean.groupby('auditor_responsable').agg({
        'id': 'count',
        'cumplimiento': lambda x: (x == 'Conforme').sum()
    }).rename(columns={'id': 'Requisitos Evaluados', 'cumplimiento': 'Conformes'}).reset_index().rename(
        columns={'auditor_responsable': 'Auditor'}
    ).assign(Conformidad=lambda x: (x['Conformes'] / x['Requisitos Evaluados'] * 100).round(1))


def _connect_gsheets():
    """Open the spreadsheet using service account credentials from secrets."""
    import gspread
    from google.oauth2.service_account import Credentials
    import re

    sheet_url = st.secrets.get("connections", {}).get("gsheets", {}).get("spreadsheet", "")
    if not sheet_url:
        raise ValueError("No spreadsheet URL in secrets: connections.gsheets.spreadsheet")

    sheet_id = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url).group(1)

    creds_dict = st.secrets.get("GOOGLE_SERVICE_ACCOUNT_INFO")
    if not creds_dict:
        raise ValueError("No GOOGLE_SERVICE_ACCOUNT_INFO in secrets")

    creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds).open_by_key(sheet_id)


def load_horas_data() -> Tuple[pd.DataFrame, pd.DataFrame, list]:
    """Load HORAS module data: participaciones, reporte and auditor list.

    Returns:
        df_participaciones: registros 2026 (filas con fecha no vacía)
        df_reporte: reporte agregado con totales por auditor
        auditores: lista de nombres de la hoja base histórica
    """
    sh = _connect_gsheets()

    # Participaciones: filas 2-1000 tienen fórmulas en A y C, filtrar por Fecha (col B)
    raw = sh.worksheet("Participaciones_2026").get_all_values()
    header = raw[0] if raw else []
    rows = [r for r in raw[1:] if len(r) > 1 and str(r[1]).strip() != ""]
    df_part = pd.DataFrame(rows, columns=header) if rows else pd.DataFrame(columns=header)
    if not df_part.empty:
        df_part["Horas"] = pd.to_numeric(df_part["Horas"].astype(str).str.replace(",", "."), errors="coerce").fillna(0.0)

    df_rep = pd.DataFrame(sh.worksheet("Reporte_Horas_2026").get_all_records())

    auditores = [a for a in sh.worksheet("Horas_Base_2011_2025").col_values(1)[1:] if str(a).strip()]

    return df_part, df_rep, auditores


def append_participacion(fecha, proceso: str, auditor: str, rol: str, horas: float, observaciones: str = "") -> int:
    """Append one participation row to Participaciones_2026.

    Writes only columns B (Fecha), D-H; columns A (ID) and C (Período)
    are auto-calculated by sheet formulas. Returns the row number written.
    """
    if not (0 < float(horas) <= 24):
        raise ValidationError("Horas debe estar entre 0.1 y 24.0")

    sh = _connect_gsheets()
    ws = sh.worksheet("Participaciones_2026")

    # Primera fila libre = última fila con Fecha (col B) + 1
    next_row = len(ws.col_values(2)) + 1

    fecha_str = fecha.strftime("%Y-%m-%d") if hasattr(fecha, "strftime") else str(fecha)
    ws.batch_update([
        {"range": f"B{next_row}", "values": [[fecha_str]]},
        {"range": f"D{next_row}:H{next_row}",
         "values": [[proceso, auditor, rol, float(horas), observaciones.strip()]]},
    ], value_input_option="USER_ENTERED")
    return next_row


def update_gsheets(worksheet_name: str, data: pd.DataFrame) -> None:
    """Update worksheet in Google Sheets with new data."""
    import gspread
    from google.oauth2.service_account import Credentials
    import re

    sheet_url = st.secrets.get("connections", {}).get("gsheets", {}).get("spreadsheet", "")
    if not sheet_url:
        raise ValueError("No spreadsheet URL in secrets")

    sheet_id = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url).group(1)

    creds_dict = st.secrets.get("GOOGLE_SERVICE_ACCOUNT_INFO")
    if not creds_dict:
        raise ValueError("No GOOGLE_SERVICE_ACCOUNT_INFO in secrets")

    creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(sheet_id)
    ws = sh.worksheet(worksheet_name)

    data_clean = data.reset_index(drop=True)
    ws.clear()
    ws.append_rows([data_clean.columns.tolist()] + data_clean.values.tolist(), value_input_option="USER_ENTERED")
