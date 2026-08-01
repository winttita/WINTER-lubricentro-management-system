import sqlite3
import streamlit as st
import database as db
import fechas
from style import inject_global_css, mostrar_flash, flash_exito, flash_error

st.set_page_config(page_title="Compras", layout="wide")
inject_global_css()
mostrar_flash()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Debe iniciar sesión para acceder a esta página.")
    st.stop()

st.title("Compras a Proveedores")

proveedores = db.get_proveedores()
productos = db.get_productos()

if not proveedores:
    st.warning("⚠️ No hay proveedores cargados. Agregalos desde Configuración primero.")

if not productos:
    st.warning("⚠️ No hay productos cargados. Agregalos desde Productos primero.")

if proveedores and productos:
    prov_dict = {p[1]: p[0] for p in proveedores}
    prod_opts = {p[0]: f"{p[2]} - Stock: {p[7]}" for p in productos if p[11]}
    prod_lookup = {p[0]: p for p in productos}
    prod_ids = list(prod_opts.keys())

    if 'compra_items' not in st.session_state:
        st.session_state.compra_items = [{'producto': None, 'cantidad': 1.0, 'precio': 0.0}]

    def agregar_fila():
        st.session_state.compra_items.append({'producto': None, 'cantidad': 1.0, 'precio': 0.0})

    def eliminar_fila(idx):
        if len(st.session_state.compra_items) > 1:
            st.session_state.compra_items.pop(idx)
            st.rerun()

    st.subheader("Nueva Compra")

    proveedor_sel = st.selectbox("Proveedor", list(prov_dict.keys()), key="compra_prov_sel")
    observaciones = st.text_area("Observaciones", placeholder="Opcional", key="compra_obs")

    st.markdown("#### Productos")

    col_scan, col_scan_info = st.columns([2, 2])
    with col_scan:
        if st.session_state.pop("compra_scan_clear", False):
            st.session_state["compra_codigo_scan"] = ""
        codigo_scan = st.text_input(
            "Codigo de barras (escanear)",
            placeholder="Escanee el codigo para rellenar el producto",
            key="compra_codigo_scan"
        )
    with col_scan_info:
        st.write("")
        if codigo_scan and st.button("Cargar en fila", key="compra_cargar_scan"):
            p = db.buscar_producto_por_codigo(codigo_scan)
            if p is None:
                st.error("No se encontro un producto con ese codigo de barras.")
            else:
                fila = next((i for i, it in enumerate(st.session_state.compra_items) if not it['producto']), None)
                if fila is None:
                    st.error("Todas las filas ya tienen producto. Quite una o agregue una fila.")
                else:
                    st.session_state.compra_items[fila]['producto'] = p[0]
                    st.session_state.compra_items[fila]['precio'] = float(p[9])
                    st.session_state.compra_scan_clear = True
                    st.rerun()

    for idx, item in enumerate(st.session_state.compra_items):
        col_prod, col_cant, col_precio, col_del = st.columns([3, 1, 1, 0.5])
        with col_prod:
            pid = st.selectbox(
                f"Producto {idx+1}",
                [""] + prod_ids,
                format_func=lambda pid_: prod_opts.get(pid_, "(seleccionar)") if pid_ else "",
                index=0 if item['producto'] is None else (
                    prod_ids.index(item['producto']) + 1
                    if item['producto'] in prod_ids else 0
                ),
                key=f"compra_prod_{idx}"
            )
            item['producto'] = pid

            if pid and pid in prod_ids:
                p = prod_lookup[pid]
                st.info(
                    f"Precio costo: ${p[9]:.2f} | "
                    f"Stock: {p[7]:.0f} | "
                    f"Prov: {p[13]} | "
                    f"Cód: {p[1]}"
                )
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
            if st.button("Quitar", key=f"compra_del_{idx}", use_container_width=True):
                if len(st.session_state.compra_items) > 1:
                    st.session_state.compra_items.pop(idx)
                    st.rerun()

    col_add, _ = st.columns([1, 3])
    with col_add:
        if st.button("Agregar producto", use_container_width=True):
            agregar_fila()
            st.rerun()

    with st.form("compra_form"):
        submitted = st.form_submit_button("Confirmar Compra", type="primary", use_container_width=True)

    if submitted:
        items = []
        for item in st.session_state.compra_items:
            if item['producto'] and item['cantidad'] > 0 and item['precio'] > 0:
                items.append({
                    'producto_id': item['producto'],
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio']
                })

        if not items:
            flash_error("Agregá al menos un producto con cantidad y precio mayor a 0.")
        else:
            try:
                compra_id = db.crear_compra(prov_dict[proveedor_sel], items, observaciones)
            except sqlite3.IntegrityError:
                compra_id = None
            if compra_id:
                flash_exito(f"Compra #{compra_id} registrada correctamente.")
                st.session_state.compra_items = [{'producto': None, 'cantidad': 1.0, 'precio': 0.0}]
                st.rerun()
            else:
                flash_error("Error al registrar la compra.")

st.divider()

st.subheader("Historial de Compras")
compras = db.get_compras()

if compras:
    for c in compras:
        estado_label = "Anulada" if c[6] == "anulada" else "Confirmada"
        with st.expander(f"#{c[0]} - {c[2]} - ${c[4]:.2f} - {fechas.formatear_fecha_hora(c[3])} - {estado_label}"):
            st.write(f"**Proveedor:** {c[2]}")
            st.write(f"**Fecha:** {fechas.formatear_fecha_hora(c[3])}")
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
                        st.success("✅ Compra anulada. Stock revertido correctamente.")
                        st.rerun()
                    else:
                        st.error("❌ Error al anular la compra.")
else:
    st.info("ℹ️ No hay compras registradas.")