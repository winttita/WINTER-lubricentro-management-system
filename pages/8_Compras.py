import streamlit as st
import database as db
from style import inject_global_css

st.set_page_config(page_title="Compras", layout="wide")
inject_global_css()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Debe iniciar sesión para acceder a esta página.")
    st.stop()

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

    if 'compra_items' not in st.session_state:
        st.session_state.compra_items = [{'producto': None, 'cantidad': 1.0, 'precio': 0.0}]

    def agregar_fila():
        st.session_state.compra_items.append({'producto': None, 'cantidad': 1.0, 'precio': 0.0})

    def eliminar_fila(idx):
        if len(st.session_state.compra_items) > 1:
            st.session_state.compra_items.pop(idx)
            st.rerun()

    st.subheader("Nueva Compra")
    with st.form("compra_form"):
        proveedor_sel = st.selectbox("Proveedor", list(prov_dict.keys()))
        observaciones = st.text_area("Observaciones", placeholder="Opcional")

        st.markdown("#### Productos")

        for idx, item in enumerate(st.session_state.compra_items):
            col_prod, col_cant, col_precio, col_del = st.columns([3, 1, 1, 0.5])
            with col_prod:
                prod_label = st.selectbox(
                    f"Producto {idx+1}",
                    list(prod_opts.keys()),
                    index=list(prod_opts.keys()).index(item['producto']) if item['producto'] in prod_opts else 0,
                    key=f"compra_prod_{idx}"
                )
                item['producto'] = prod_label
            with col_cant:
                item['cantidad'] = st.number_input(
                    "Cant.", min_value=0.0, step=1.0,
                    value=item['cantidad'], key=f"compra_cant_{idx}"
                )
            with col_precio:
                item['precio'] = st.number_input(
                    "Precio Unit.", min_value=0.0, step=0.01,
                    value=item['precio'], key=f"compra_precio_{idx}"
                )
            with col_del:
                st.write("")
                if st.form_submit_button("Quitar", key=f"compra_del_{idx}", use_container_width=True):
                    eliminar_fila(idx)

        col_add, col_submit = st.columns([1, 3])
        with col_add:
            if st.form_submit_button("Agregar producto", use_container_width=True):
                agregar_fila()
                st.rerun()
        with col_submit:
            submitted = st.form_submit_button("Confirmar Compra", type="primary", use_container_width=True)

        if submitted:
            items = []
            for item in st.session_state.compra_items:
                if item['producto'] and item['cantidad'] > 0 and item['precio'] > 0:
                    items.append({
                        'producto_id': prod_opts[item['producto']],
                        'cantidad': item['cantidad'],
                        'precio_unitario': item['precio']
                    })

            if not items:
                st.error("Agregá al menos un producto con cantidad y precio mayor a 0.")
            else:
                compra_id = db.crear_compra(prov_dict[proveedor_sel], items, observaciones)
                if compra_id:
                    st.success(f"Compra #{compra_id} registrada correctamente.")
                    st.session_state.compra_items = [{'producto': None, 'cantidad': 1.0, 'precio': 0.0}]
                    st.rerun()
                else:
                    st.error("Error al registrar la compra.")

st.divider()

st.subheader("Historial de Compras")
compras = db.get_compras()

if compras:
    for c in compras:
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