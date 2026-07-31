import os

from lista_precios_pdf import generar_pdf

PRODUCTOS = [
    ("Proveedor A", "Aceite 20W50", "123", 4500.00, 10, "Lubricantes"),
    ("Proveedor A", "Filtro de aceite", "456", 3500.00, 5, "Filtros"),
]
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_generar_pdf_con_logo():
    logo = os.path.join(REPO_ROOT, "centro_automotor.png")
    assert os.path.isfile(logo)
    out = generar_pdf(PRODUCTOS, logo_path=logo)
    assert out[:5] == b"%PDF-"
    assert len(out) > 1000


def test_generar_pdf_sin_logo_no_falla():
    out = generar_pdf(PRODUCTOS, logo_path=None)
    assert out[:5] == b"%PDF-"
    assert len(out) > 1000


def test_generar_pdf_con_logo_inexistente_no_falla(tmp_path):
    out = generar_pdf(PRODUCTOS, logo_path=str(tmp_path / "no-existe.png"))
    assert out[:5] == b"%PDF-"
