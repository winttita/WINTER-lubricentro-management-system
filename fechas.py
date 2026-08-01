from datetime import datetime, timedelta

FORMATO_SALIDA = "%d/%m/%Y %H:%M"
FORMATO_UTC = "%Y-%m-%d %H:%M:%S"


def _offset_local():
    now = datetime.now().astimezone()
    return now.utcoffset() or timedelta(0)


def formatear_fecha_hora(valor):
    """Normaliza una fecha (datetime o string de la DB) a hora local y la formatea.

    - datetime: se formatea directo.
    - str con 'T': ISO local del adapter de database.py, se parsea directo.
    - str sin 'T' (YYYY-MM-DD HH:MM:SS): UTC de CURRENT_TIMESTAMP de SQLite,
      se convierte a hora local.
    Devuelve "" para None/vacio y el string crudo si no puede parsear.
    """
    if valor is None or valor == "":
        return ""
    if isinstance(valor, datetime):
        return valor.strftime(FORMATO_SALIDA)

    s = str(valor).strip()
    try:
        if "T" in s:
            dt = datetime.fromisoformat(s)
        else:
            dt = datetime.strptime(s, FORMATO_UTC)
            dt = dt + _offset_local()
    except ValueError:
        return s
    return dt.strftime(FORMATO_SALIDA)
