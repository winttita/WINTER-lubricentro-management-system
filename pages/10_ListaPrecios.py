import streamlit as st
import database as db
import pandas as pd
from datetime import datetime
from lista_precios_pdf import generar_pdf
from style import inject_global_css, get_logo_path

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
pdf_bytes = generar_pdf(productos, get_logo_path())
fecha_archivo = datetime.now().strftime("%Y%m%d")

st.download_button(
    label="📄 Descargar PDF",
    data=pdf_bytes,
    file_name=f"lista_precios_{fecha_archivo}.pdf",
    mime="application/pdf",
    use_container_width=True,
)
st.success(f"✅ PDF generado: {len(productos)} productos de {len(grupos)} proveedores.")
