import streamlit as st
import database as db
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from style import inject_global_css

st.set_page_config(page_title="Lista de Precios", layout="wide")
inject_global_css()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Debe iniciar sesión para acceder a esta página.")
    st.stop()

st.title("📋 Lista de Precios")
st.caption("Productos activos con stock. Precios de venta. Actualizada automáticamente.")

productos = db.get_precios_para_lista()

if not productos:
    st.info("ℹ️ No hay productos con stock disponible para listar.")
    st.stop()


# --- Helper: agrupar por proveedor ---
def agrupar_por_proveedor(rows):
    grupos = {}
    for r in rows:
        prov = r[0] or "Sin proveedor"
        grupos.setdefault(prov, []).append(r)
    return grupos


def generar_pdf(productos):
    """Genera un PDF de la lista de precios agrupada por proveedor.

    Maneja acentos y eñes usando latin-1 explicito en cada string.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    # Encabezado
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "LISTA DE PRECIOS", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Lubricentro Winter", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    fecha_str = datetime.now().strftime("%d/%m/%Y")
    pdf.cell(0, 6, f"Fecha de emision: {fecha_str}", ln=True, align="C")
    pdf.ln(3)

    grupos = agrupar_por_proveedor(productos)

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
            precio = f"${p[3]:,.2f}"

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
    return bytes(out)


# --- Vista previa en pantalla ---
grupos = agrupar_por_proveedor(productos)

col_info1, col_info2 = st.columns(2)
with col_info1:
    st.metric("Productos en lista", len(productos))
with col_info2:
    st.metric("Proveedores", len(grupos))

st.divider()

for proveedor, items in grupos.items():
    with st.expander(f"{proveedor} ({len(items)} productos)", expanded=False):
        data = []
        for p in items:
            data.append({
                "Codigo": p[2] or "-",
                "Producto": p[1],
                "Categoria": p[5] or "-",
                "Precio Venta": p[3],
                "Stock": p[4],
            })
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()

# --- Generacion y descarga del PDF ---
pdf_bytes = generar_pdf(productos)
fecha_archivo = datetime.now().strftime("%Y%m%d")

st.download_button(
    label="📄 Descargar PDF",
    data=pdf_bytes,
    file_name=f"lista_precios_{fecha_archivo}.pdf",
    mime="application/pdf",
    use_container_width=True,
)
st.success(f"✅ PDF generado: {len(productos)} productos de {len(grupos)} proveedores.")
