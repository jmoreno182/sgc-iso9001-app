"""
Setup script: crea las 3 hojas del modulo HORAS en Google Sheets.
  1. Horas_Base_2011_2025  - base historica (solo lectura)
  2. Participaciones_2026  - registro de participaciones (entrada de datos)
  3. Reporte_Horas_2026    - reporte agregado con formulas (solo lectura)

Datos base extraidos del PDF "SGC-F-AS-024-2 Registro de horas de Auditoria"
usando las columnas "Total de Horas de Auditoria Acumuladas" (incluye Dic 2025).

Uso:  python setup_horas_sheets.py [--force]
      --force: elimina y recrea las hojas si ya existen
"""

import re
import sys

try:
    import tomllib  # Python 3.11+
    def load_toml(path):
        with open(path, "rb") as f:
            return tomllib.load(f)
except ImportError:
    import toml
    def load_toml(path):
        return toml.load(path)

import gspread
from google.oauth2.service_account import Credentials

SECRETS_PATH = ".streamlit/secrets.toml"
FORCE = "--force" in sys.argv

# (Auditor, OB_Prev, AF_Prev, AD_Prev, AL_Prev, Notas)
# Fuente: PDF SGC-F-AS-024-2, columnas "Total de Horas de Auditoria Acumuladas"
# (acumulado 2011 - Dic 2025)
AUDITORES = [
    ("Marlene Andrea",      12.2, 42.1, 70.1,  42.6, ""),
    ("Yraima Rodríguez",    7.3,  44.5, 124.6, 35.0, ""),
    ("Yolmarig Montilla",   12.3, 24.5, 112.5, 22.0, ""),
    ("Pablo Galvis",        9.2,  31.3, 52.3,  0.0,  ""),
    ("Angelo Mazzarino",    15.0, 8.0,  51.9,  0.0,  ""),
    ("Xiomara Navas",       4.0,  11.3, 45.4,  0.0,  ""),
    ("Wiston Martínez",     9.0,  12.2, 41.0,  0.0,  ""),
    ("Alexander Romero",    8.3,  8.2,  29.0,  0.0,  ""),
    ("Osmaida Garcés",      13.3, 30.4, 10.0,  0.0,  ""),
    ("Alonzo Albarracín",   10.2, 26.8, 0.0,   0.0,  ""),
    ("Jerly Vielma",        21.5, 23.4, 0.0,   0.0,  ""),
    ("Arnaldo Guerra",      9.0,  20.4, 0.0,   0.0,  ""),
    ("Julia Manzano",       14.5, 0.0,  0.0,   0.0,  ""),
    ("Rodney Mazza",        13.5, 0.0,  0.0,   0.0,  ""),
    ("Fernando Velásquez",  13.5, 0.0,  0.0,   0.0,  ""),
    ("Rafael Rojas",        13.0, 0.0,  0.0,   0.0,  ""),
    ("Nelson Castillo",     12.5, 0.0,  0.0,   0.0,  ""),
    ("Reina Tayupo",        11.0, 0.0,  0.0,   0.0,  ""),
    ("Orbethsy Guetierrez", 9.3,  0.0,  0.0,   0.0,  ""),
    ("Daniel García",       7.5,  0.0,  0.0,   0.0,  ""),
    ("Delvy Guetierrez",    5.7,  0.0,  0.0,   0.0,  ""),
    ("Angélica Maldonado",  5.5,  0.0,  0.0,   0.0,  ""),
    ("Sara Rabelo",         0.0,  0.0,  0.0,   0.0,  "Nueva auditora 2026"),
]

PROCESOS = ["EV", "FP", "TR", "DR", "AC", "DD", "AA", "GI", "GM", "PB", "PP", "CO", "AS", "GP", "DI"]
ROLES = ["OB", "AF", "AD", "AL"]
N_AUD = len(AUDITORES)          # 23
LAST_ROW = N_AUD + 1            # fila 24
GRAY = {"red": 0.85, "green": 0.85, "blue": 0.85}

# Separador de argumentos en fórmulas: depende del locale del spreadsheet.
# Locales en_* usan "," — el resto (es_ES, es_VE, etc.) usan ";".
SEP = ","


def connect():
    global SEP
    secrets = load_toml(SECRETS_PATH)
    url = secrets["connections"]["gsheets"]["spreadsheet"]
    sheet_id = re.search(r"/d/([a-zA-Z0-9-_]+)", url).group(1)
    creds = Credentials.from_service_account_info(
        secrets["GOOGLE_SERVICE_ACCOUNT_INFO"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(sheet_id)
    print(f"Conectado a: {sh.title}")
    meta = sh.fetch_sheet_metadata()
    locale = meta["properties"].get("locale", "en_US")
    SEP = "," if locale.lower().startswith("en") else ";"
    print(f"Locale del spreadsheet: {locale} (separador de fórmulas: '{SEP}')")
    return sh, secrets["GOOGLE_SERVICE_ACCOUNT_INFO"]["client_email"]


def get_or_create(sh, name, rows, cols):
    existing = [w.title for w in sh.worksheets()]
    if name in existing:
        if not FORCE:
            print(f"AVISO: la hoja '{name}' ya existe. Usa --force para recrearla.")
            return None
        sh.del_worksheet(sh.worksheet(name))
        print(f"Hoja '{name}' eliminada (--force).")
    ws = sh.add_worksheet(title=name, rows=rows, cols=cols)
    print(f"Hoja '{name}' creada.")
    return ws


def header_format_request(sheet_id, n_cols):
    return {
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1,
                      "startColumnIndex": 0, "endColumnIndex": n_cols},
            "cell": {"userEnteredFormat": {
                "textFormat": {"bold": True},
                "backgroundColor": GRAY,
                "horizontalAlignment": "CENTER"}},
            "fields": "userEnteredFormat(textFormat,backgroundColor,horizontalAlignment)",
        }
    }


def number_format_request(sheet_id, r1, r2, c1, c2, pattern, ntype="NUMBER"):
    return {
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": r1, "endRowIndex": r2,
                      "startColumnIndex": c1, "endColumnIndex": c2},
            "cell": {"userEnteredFormat": {"numberFormat": {"type": ntype, "pattern": pattern}}},
            "fields": "userEnteredFormat.numberFormat",
        }
    }


def col_width_request(sheet_id, col_index, pixels):
    return {
        "updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "COLUMNS",
                      "startIndex": col_index, "endIndex": col_index + 1},
            "properties": {"pixelSize": pixels},
            "fields": "pixelSize",
        }
    }


def center_request(sheet_id, r1, r2, c1, c2):
    return {
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": r1, "endRowIndex": r2,
                      "startColumnIndex": c1, "endColumnIndex": c2},
            "cell": {"userEnteredFormat": {"horizontalAlignment": "CENTER"}},
            "fields": "userEnteredFormat.horizontalAlignment",
        }
    }


def protect_request(sheet_id, description, editor_email):
    return {
        "addProtectedRange": {
            "protectedRange": {
                "range": {"sheetId": sheet_id},
                "description": description,
                "warningOnly": False,
                "editors": {"users": [editor_email]},
            }
        }
    }


def setup_horas_base(sh, editor_email):
    ws = get_or_create(sh, "Horas_Base_2011_2025", rows=30, cols=6)
    if ws is None:
        return
    values = [["Auditor", "OB_Prev", "AF_Prev", "AD_Prev", "AL_Prev", "Notas"]]
    values += [list(a) for a in AUDITORES]
    ws.update(values, "A1", value_input_option="USER_ENTERED")

    widths = [240, 95, 95, 95, 95, 200]
    reqs = [header_format_request(ws.id, 6),
            number_format_request(ws.id, 1, LAST_ROW, 1, 5, "0.00")]
    reqs += [col_width_request(ws.id, i, w) for i, w in enumerate(widths)]
    reqs.append(protect_request(ws.id, "Base historica - solo lectura", editor_email))
    sh.batch_update({"requests": reqs})
    print(f"Horas_Base_2011_2025 lista: {N_AUD} auditores (filas 2-{LAST_ROW}).")


def setup_participaciones(sh, editor_email):
    ws = get_or_create(sh, "Participaciones_2026", rows=1000, cols=8)
    if ws is None:
        return
    ws.update([["ID", "Fecha", "Período", "Proceso", "Auditor", "Rol", "Horas", "Observaciones"]],
              "A1", value_input_option="USER_ENTERED")

    # Formulas auto-calculadas: ID (col A) y Período (col C), filas 2-1000
    f_id, f_per = [], []
    for r in range(2, 1001):
        f_id.append([f'=IF($B{r}=""{SEP}""{SEP}ROW()-1)'])
        f_per.append([f'=IF($B{r}=""{SEP}""{SEP}IF(DAY($B{r})<=6{SEP}"Junio 1 (04-06)"{SEP}'
                      f'IF(DAY($B{r})<=12{SEP}"Junio 2 (08-12)"{SEP}"Junio 3 (15+)")))'])
    ws.update(f_id, "A2:A1000", value_input_option="USER_ENTERED")
    ws.update(f_per, "C2:C1000", value_input_option="USER_ENTERED")

    def validation(c1, c2, condition, strict=True, show_ui=True, msg=None):
        rule = {"condition": condition, "strict": strict, "showCustomUi": show_ui}
        if msg:
            rule["inputMessage"] = msg
        return {"setDataValidation": {
            "range": {"sheetId": ws.id, "startRowIndex": 1, "endRowIndex": 1000,
                      "startColumnIndex": c1, "endColumnIndex": c2},
            "rule": rule}}

    reqs = [
        # D: Proceso (lista)
        validation(3, 4, {"type": "ONE_OF_LIST",
                          "values": [{"userEnteredValue": p} for p in PROCESOS]}),
        # E: Auditor (rango de Horas_Base)
        validation(4, 5, {"type": "ONE_OF_RANGE",
                          "values": [{"userEnteredValue": f"=Horas_Base_2011_2025!$A$2:$A${LAST_ROW}"}]}),
        # F: Rol (lista)
        validation(5, 6, {"type": "ONE_OF_LIST",
                          "values": [{"userEnteredValue": r} for r in ROLES]}),
        # G: Horas (0 < x <= 24)
        validation(6, 7, {"type": "CUSTOM_FORMULA",
                          "values": [{"userEnteredValue": f"=AND(G2>0{SEP}G2<=24)"}]},
                   show_ui=False, msg="Horas debe estar entre 0.1 y 24.0"),
        header_format_request(ws.id, 8),
        number_format_request(ws.id, 1, 1000, 1, 2, "M/d/yyyy", ntype="DATE"),
        number_format_request(ws.id, 1, 1000, 6, 7, "0.0"),
        center_request(ws.id, 1, 1000, 0, 1),   # ID
        center_request(ws.id, 1, 1000, 2, 4),   # Período, Proceso
        center_request(ws.id, 1, 1000, 5, 6),   # Rol
    ]
    widths = [60, 110, 150, 90, 200, 90, 90, 240]
    reqs += [col_width_request(ws.id, i, w) for i, w in enumerate(widths)]
    sh.batch_update({"requests": reqs})
    print("Participaciones_2026 lista: dropdowns, validaciones y fórmulas configuradas.")


def setup_reporte(sh, editor_email):
    ws = get_or_create(sh, "Reporte_Horas_2026", rows=30, cols=14)
    if ws is None:
        return
    header = ["Auditor", "OB_2026", "AF_2026", "AD_2026", "AL_2026",
              "OB_Prev", "AF_Prev", "AD_Prev", "AL_Prev",
              "OB_Total", "AF_Total", "AD_Total", "AL_Total", "Total_Auditorías"]
    values = [header]
    for i, aud in enumerate(AUDITORES):
        r = i + 2
        row = [aud[0]]
        # B-E: horas 2026 por rol (SUMIFS)
        for rol in ROLES:
            row.append(f'=SUMIFS(Participaciones_2026!$G:$G{SEP}'
                       f'Participaciones_2026!$E:$E{SEP}$A{r}{SEP}'
                       f'Participaciones_2026!$F:$F{SEP}"{rol}")')
        # F-I: horas previas (VLOOKUP a la base)
        for col_idx in (2, 3, 4, 5):
            row.append(f'=IFERROR(VLOOKUP($A{r}{SEP}Horas_Base_2011_2025!$A:$E{SEP}{col_idx}{SEP}FALSE){SEP}0)')
        # J-M: totales
        for c2026, cprev in zip("BCDE", "FGHI"):
            row.append(f"={c2026}{r}+{cprev}{r}")
        # N: numero de auditorias 2026
        row.append(f'=COUNTIF(Participaciones_2026!$E:$E{SEP}$A{r})')
        values.append(row)
    ws.update(values, "A1", value_input_option="USER_ENTERED")

    reqs = [header_format_request(ws.id, 14),
            number_format_request(ws.id, 1, LAST_ROW, 1, 13, "0.0"),
            number_format_request(ws.id, 1, LAST_ROW, 13, 14, "0"),
            protect_request(ws.id, "Reporte automatico - solo lectura", editor_email)]
    widths = [240] + [85] * 12 + [130]
    reqs += [col_width_request(ws.id, i, w) for i, w in enumerate(widths)]
    sh.batch_update({"requests": reqs})
    print(f"Reporte_Horas_2026 lista: fórmulas para {N_AUD} auditores.")


def verify(sh):
    print("\n--- Verificación ---")
    base = sh.worksheet("Horas_Base_2011_2025").get_all_values()
    print(f"Horas_Base: {len(base) - 1} auditores (esperado {N_AUD})")
    rep = sh.worksheet("Reporte_Horas_2026").get_all_values()
    errores = [c for row in rep for c in row if c.startswith("#")]
    print(f"Reporte: {len(rep) - 1} filas, errores de fórmula: {len(errores)}")
    if errores:
        print("  Ejemplos:", errores[:5])
    # Marlene: OB_Total debe ser = OB_2026 (0) + OB_Prev (12.2)
    marlene = rep[1]
    print(f"Marlene Andrea -> Prev: {marlene[5:9]} | Total: {marlene[9:13]} | N: {marlene[13]}")


if __name__ == "__main__":
    sh, sa_email = connect()
    setup_horas_base(sh, sa_email)
    setup_participaciones(sh, sa_email)
    setup_reporte(sh, sa_email)
    verify(sh)
    print("\nListo. Las 3 hojas fueron creadas y verificadas.")
