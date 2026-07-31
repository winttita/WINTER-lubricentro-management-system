import os
from datetime import datetime

from fpdf import FPDF


def generar_pdf(productos: list, logo_path: str | None = None) -> bytes:
    """Genera un PDF de la lista de precios agrupada por proveedor.

    Maneja acentos y eñes usando latin-1 explicito en cada string.
    Si logo_path es None o el archivo no existe, se omite el logo.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    # Encabezado
    pdf.add_page()
    if logo_path and os.path.isfile(logo_path):
        pdf.image(logo_path, x=(210 - 50) / 2, w=50)
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "LISTA DE PRECIOS", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Centro Automotor WINTER", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    fecha_str = datetime.now().strftime("%d/%m/%Y")
    pdf.cell(0, 6, f"Fecha de emision: {fecha_str}", ln=True, align="C")
    pdf.ln(3)

    grupos = {}
    for r in productos:
        prov = r[0] or "Sin proveedor"
        grupos.setdefault(prov, []).append(r)

    for proveedor, items in grupos.items():
        # Encabezado del proveedor
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(0, 7, proveedor, ln=True, fill=True)
        pdf.ln(1)

        # Cabecera de tabla
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(25, 6, "Codigo", border=1, fill=True)
        pdf.cell(85, 6, "Producto", border=1, fill=True)
        pdf.cell(40, 6, "Categoria", border=1, fill=True)
        pdf.cell(20, 6, "Precio", border=1, fill=True, align="R")
        pdf.ln()

        # Filas de productos
        pdf.set_font("Helvetica", "", 9)
        for p in items:
            codigo = (p[2] or "-")[:25]
            nombre = (p[1] or "-")[:50]
            categoria = (p[5] or "-")[:22]
            precio = f"${p[3] or 0:,.2f}"

            pdf.cell(25, 6, codigo, border=1)
            pdf.cell(85, 6, nombre, border=1)
            pdf.cell(40, 6, categoria, border=1)
            pdf.cell(20, 6, precio, border=1, align="R")
            pdf.ln()

        pdf.ln(2)

    # Footer
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, "Precios sujetos a cambio sin previo aviso.", ln=True, align="C")

    out = pdf.output()
    if isinstance(out, str):
        return out.encode('latin-1')
    return bytes(out)
