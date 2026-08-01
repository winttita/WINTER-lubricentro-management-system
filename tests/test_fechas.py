import os
import time
from datetime import datetime

import pytest

import fechas
import tickets


def _set_tz(tz):
    os.environ["TZ"] = tz
    time.tzset()


needs_tzset = pytest.mark.skipif(
    not hasattr(time, "tzset"), reason="time.tzset() solo disponible en Unix"
)


def test_none_vacio_devuelve_vacio():
    assert fechas.formatear_fecha_hora(None) == ""
    assert fechas.formatear_fecha_hora("") == ""


def test_datetime_local_se_formatea():
    dt = datetime(2026, 8, 1, 10, 30, 0)
    assert fechas.formatear_fecha_hora(dt) == "01/08/2026 10:30"


def test_string_iso_con_T_se_formatea_directo():
    assert fechas.formatear_fecha_hora("2026-08-01T10:30:45.123456") == "01/08/2026 10:30"


@needs_tzset
def test_string_utc_sin_T_se_convierte_a_local():
    tz_original = os.environ.get("TZ")
    _set_tz("America/Argentina/Buenos_Aires")
    try:
        assert fechas.formatear_fecha_hora("2026-08-01 14:30:45") == "01/08/2026 11:30"
    finally:
        if tz_original:
            _set_tz(tz_original)
        else:
            os.environ.pop("TZ", None)


@needs_tzset
def test_string_utc_con_microsegundos_se_convierte_a_local():
    tz_original = os.environ.get("TZ")
    _set_tz("America/Argentina/Buenos_Aires")
    try:
        assert fechas.formatear_fecha_hora("2026-08-01 14:30:45.123456") == "01/08/2026 11:30"
    finally:
        if tz_original:
            _set_tz(tz_original)
        else:
            os.environ.pop("TZ", None)


def test_string_invalido_devuelve_crudo():
    assert fechas.formatear_fecha_hora("no-es-fecha") == "no-es-fecha"


@needs_tzset
def test_ticket_venta_formatea_fecha_utc_a_local():
    tz_original = os.environ.get("TZ")
    _set_tz("America/Argentina/Buenos_Aires")
    try:
        venta = {
            "tipo_comprobante": "ticket",
            "punto_venta": "0001",
            "numero_comprobante": 42,
            "subtotal": 100.0,
            "iva": 0.0,
            "total": 100.0,
            "metodo_pago": "efectivo",
            "creado_en": "2026-08-01 14:30:45",
        }
        texto = tickets.generar_ticket_texto(venta, [], None)
        assert "Fecha: 01/08/2026 11:30" in texto
        assert "2026-08-01 14:30:45" not in texto
    finally:
        if tz_original:
            _set_tz(tz_original)
        else:
            os.environ.pop("TZ", None)
