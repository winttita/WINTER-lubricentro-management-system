import streamlit as st
import database as db
from datetime import datetime

st.set_page_config(page_title="Movimientos de Stock")

st.title("Movimientos de Stock")

# Formulario para registrar un movimiento
st.subheader("Registrar Movimiento")

# Obtener productos para el selectbox
productos = db.get_productos()
producto_options = {f"[{p[1]}] {p[3]}": p[0] for p in productos}  # codigo_interno, nombre -> id

if not producto_options:
    st.warning("No hay productos registrados. Por favor, agregue productos primero.")
else:
    with st.form("movimiento_form"):
        producto_seleccionado = st.selectbox("Producto", options=list(producto_options.keys()))
        tipo = st.selectbox("Tipo", options=['compra', 'venta', 'ajuste', 'devolucion', 'uso_interno'])
        cantidad = st.number_input("Cantidad", min_value=0.0, step=0.01, format="%.2f")
        motivo = st.text_area("Motivo (opcional)")
        
        submitted = st.form_submit_button("Registrar Movimiento")
        if submitted:
            producto_id = producto_options[producto_seleccionado]
            if cantidad <= 0:
                st.error("La cantidad debe ser mayor que cero")
            else:
                success = db.add_movimiento(producto_id, tipo, cantidad, motivo)
                if success:
                    st.success("Movimiento registrado exitosamente")
                    # Limpiar el formulario (Streamlit no tiene un clear_form directo, pero podemos rerun)
                else:
                    st.error("Error al registrar movimiento. Verifique que haya suficiente stock.")

st.divider()

# Mostrar movimientos recientes
st.subheader("Movimientos Recientes")
movimientos = db.get_movimientos(limit=10)

if movimientos:
    # Preparar datos para la tabla
    data = []
    for m in movimientos:
        # m: (id, producto_id, tipo, cantidad, fecha, motivo, producto_nombre)
        fecha_str = m[4].strftime("%d/%m/%Y %H:%M") if m[4] else ""
        data.append({
            "Fecha": fecha_str,
            "Producto": m[6],
            "Tipo": m[2].capitalize(),
            "Cantidad": m[3],
            "Motivo": m[5] or "-"
        })
    st.dataframe(data, use_container_width=True, hide_index=True)
else:
    st.info("No hay movimientos registrados aún.")