import streamlit as st
import database as db

st.set_page_config(page_title="Compras", layout="wide")
st.title("Compras a Proveedores")

proveedores = db.get_proveedores()
productos = db.get_productos()

if not proveedores:
    st.warning("No hay proveedores cargados. Agregalos desde Configuración primero.")

if not productos:
    st.warning("No hay productos cargados. Agregalos desde Productos primero.")

if proveedores and productos:
    prov_dict = {p[1]: p[0] for p in proveedores}
    prod_opts = {f"[{p[1]}] {p[3]} - Stock: {p[8]}": p[0] for p in productos if p[12]}
    prod_lookup = {p[0]: p for p in productos}

    st.subheader("Nueva Compra")
    with st.form("compra_form"):
        proveedor_sel = st.selectbox("Proveedor", list(prov_dict.keys()))
        observaciones = st.text_area("Observaciones", placeholder="Opcional")

        st.markdown("#### Productos")
        prod_sel_1 = st.selectbox("Producto 1", list(prod_opts.keys()), key="prod_1")
        cant_1 = st.number_input("Cantidad 1", min_value=0.0, step=1.0, key="cant_1")
        precio_1 = st.number_input("Precio Unit. 1", min_value=0.0, step=0.01, key="precio_1")

        prod_sel_2 = st.selectbox("Producto 2 (opcional)", ["---"] + list(prod_opts.keys()), key="prod_2")
        cant_2 = st.number_input("Cantidad 2", min_value=0.0, step=1.0, key="cant_2")
        precio_2 = st.number_input("Precio Unit. 2", min_value=0.0, step=0.01, key="precio_2")

        prod_sel_3 = st.selectbox("Producto 3 (opcional)", ["---"] + list(prod_opts.keys()), key="prod_3")
        cant_3 = st.number_input("Cantidad 3", min_value=0.0, step=1.0, key="cant_3")
        precio_3 = st.number_input("Precio Unit. 3", min_value=0.0, step=0.01, key="precio_3")

        submitted = st.form_submit_button("Confirmar Compra", type="primary")

        if submitted:
            items = []
            if prod_sel_1 and cant_1 > 0 and precio_1 > 0:
                items.append({'producto_id': prod_opts[prod_sel_1], 'cantidad': cant_1, 'precio_unitario': precio_1})
            if prod_sel_2 != "---" and cant_2 > 0 and precio_2 > 0:
                items.append({'producto_id': prod_opts[prod_sel_2], 'cantidad': cant_2, 'precio_unitario': precio_2})
            if prod_sel_3 != "---" and cant_3 > 0 and precio_3 > 0:
                items.append({'producto_id': prod_opts[prod_sel_3], 'cantidad': cant_3, 'precio_unitario': precio_3})

            if not items:
                st.error("Agregá al menos un producto con cantidad y precio mayor a 0.")
            else:
                compra_id = db.crear_compra(prov_dict[proveedor_sel], items, observaciones)
                if compra_id:
                    st.success(f"Compra #{compra_id} registrada correctamente.")
                    st.rerun()
                else:
                    st.error("Error al registrar la compra.")

st.divider()

st.subheader("Historial de Compras")
compras = db.get_compras()

if compras:
    for c in compras:
        # c: id, proveedor_id, proveedor, fecha, total, observaciones, estado
        estado_label = "Anulada" if c[6] == "anulada" else "Confirmada"
        with st.expander(f"#{c[0]} - {c[2]} - ${c[4]:.2f} - {c[3]} - {estado_label}"):
            st.write(f"**Proveedor:** {c[2]}")
            st.write(f"**Fecha:** {c[3]}")
            st.write(f"**Total:** ${c[4]:.2f}")
            st.write(f"**Estado:** {estado_label}")
            if c[5]:
                st.write(f"**Observaciones:** {c[5]}")

            detalle = db.get_detalle_compra(c[0])
            if detalle:
                st.markdown("#### Detalle")
                for d in detalle:
                    # d: id, producto_id, producto, codigo_barras, cantidad, precio_unitario, subtotal
                    st.write(f"- {d[2]} x{d[4]:.0f} @ ${d[5]:.2f} = ${d[6]:.2f}")

            if c[6] != "anulada":
                if st.button("Anular compra", key=f"anular_{c[0]}"):
                    ok = db.anular_compra(c[0])
                    if ok:
                        st.success("Compra anulada. Stock revertido.")
                        st.rerun()
                    else:
                        st.error("Error al anular la compra.")
else:
    st.info("No hay compras registradas.")
