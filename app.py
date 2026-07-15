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
    valor_inventario = sum(p[10] * p[8] for p in productos)  # precio_venta * stock_actual
    st.metric("Valor Inventario (Precio Venta)", f"${valor_inventario:,.2f}")

with col3:
    stock_critico = sum(1 for p in productos if p[8] <= p[9])  # stock_actual <= stock_minimo
    st.metric("Productos en Stock Crítico", stock_critico)

st.divider()

st.subheader("Últimos Movimientos")
movimientos_recientes = db.get_movimientos(limit=5)
if movimientos_recientes:
    # Mostrar en una tabla pequeña
    data = []
    for m in movimientos_recientes:
        # m: (id, producto_id, tipo, cantidad, fecha, motivo, producto_nombre)
        fecha_str = m[4].strftime("%d/%m/%y %H:%M") if m[4] else ""
        data.append({
            "Fecha": fecha_str,
            "Producto": m[6],
            "Tipo": m[2].capitalize(),
            "Cantidad": m[3],
            "Motivo": (m[5] or "-")[:20] + "..." if m[5] and len(m[5]) > 20 else (m[5] or "-")
        })
    st.dataframe(data, use_container_width=True, hide_index=True)
else:
    st.info("No hay movimientos recientes.")

st.divider()

st.subheader("Navegación")
st.markdown("""
Usá el menú lateral izquierdo para acceder a las distintas secciones del sistema:

- **Categorías**: Gestión de categorías de productos
- **Proveedores**: Gestión de proveedores y condiciones de pago
- **Productos**: Alta y gestión de productos
- **Movimientos**: Registro de entradas y salidas de stock
- **Clientes**: Gestión de clientes
- **Vehículos**: Gestión de vehículos
- **Servicios**: Gestión de servicios
- **Órdenes de Servicio**: Creación de órdenes de trabajo (servicios y consumo de productos)
- **Reportes**: Reportes de ventas, inventario y balance ingresos vs egresos
""")
