import streamlit as st
import database as db

st.set_page_config(
    page_title="Lubricentro Winter",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Lubricentro Winter")
st.markdown("Sistema de gestión de stock y punto de venta")

db.init_db()

st.divider()

col1, col2, col3 = st.columns(3)

productos = db.get_productos()

with col1:
    st.metric("Productos Activos", len(productos))

with col2:
    valor_inventario = sum(p[10] * p[8] for p in productos)
    st.metric("Valor Inventario (Costo)", f"${valor_inventario:,.2f}")

with col3:
    stock_critico = sum(1 for p in productos if p[8] <= p[9])
    st.metric("Productos en Stock Crítico", stock_critico)

st.divider()

st.subheader("Navegación")
st.markdown("""
Usá el menú lateral izquierdo para acceder a las distintas secciones del sistema:

- **Categorías**: Gestión de categorías de productos
- **Proveedores**: Gestión de proveedores y condiciones de pago
- **Productos**: Alta y gestión de productos
""")
