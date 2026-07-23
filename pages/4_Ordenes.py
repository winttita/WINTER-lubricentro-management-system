import streamlit as st
import database as db
from style import inject_global_css

st.set_page_config(page_title="Órdenes de Servicio", layout="wide")
inject_global_css()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Debe iniciar sesión para acceder a esta página.")
    st.stop()

st.title("🔧 Órdenes de Servicio")

clientes = db.get_clientes()
vehiculos = db.get_vehiculos()
servicios = db.get_servicios()
productos = db.get_productos()

# --- Estado del carrito de orden ---
if 'orden_servicios' not in st.session_state:
    st.session_state.orden_servicios = []
if 'orden_productos' not in st.session_state:
    st.session_state.orden_productos = []
if 'orden_cliente' not in st.session_state:
    st.session_state.orden_cliente = None
if 'orden_vehiculo' not in st.session_state:
    st.session_state.orden_vehiculo = None


# =============================================================================
# Nueva orden
# =============================================================================
st.subheader("Nueva Orden de Servicio")

if not clientes:
    st.warning("No hay clientes cargados. Agregalos desde Gestión primero.")
    st.stop()
if not vehiculos:
    st.warning("No hay vehículos cargados. Agregalos desde Gestión primero.")
    st.stop()

# Cabecera: cliente + vehiculo
col_cli, col_veh = st.columns(2)
with col_cli:
    cliente_opts = {c[1]: c[0] for c in clientes}
    cliente_sel = st.selectbox("Cliente *", list(cliente_opts.keys()))
    st.session_state.orden_cliente = cliente_opts[cliente_sel]

with col_veh:
    # Filtrar vehículos del cliente seleccionado
    vehiculos_cliente = [v for v in vehiculos if v[1] == st.session_state.orden_cliente]
    if vehiculos_cliente:
        vehiculo_opts = {f"{v[2]} - {v[3]} {v[4]} ({v[5]})": v[0] for v in vehiculos_cliente}
        vehiculo_sel = st.selectbox("Vehículo *", list(vehiculo_opts.keys()))
        st.session_state.orden_vehiculo = vehiculo_opts[vehiculo_sel]
    else:
        st.warning("Este cliente no tiene vehículos cargados.")
        st.session_state.orden_vehiculo = None


# --- Servicios ---
st.markdown("#### Servicios")

if servicios:
    serv_opts = {f"{s[1]} - ${s[2]:.2f}": s[0] for s in servicios}
    serv_lookup = {s[0]: s for s in servicios}

    # Tabla dinámica de servicios
    def agregar_servicio():
        st.session_state.orden_servicios.append({'servicio': None, 'cantidad': 1})

    def eliminar_servicio(idx):
        if len(st.session_state.orden_servicios) > 0:
            st.session_state.orden_servicios.pop(idx)
            st.rerun()

    if not st.session_state.orden_servicios:
        st.session_state.orden_servicios = [{'servicio': None, 'cantidad': 1}]

    for idx, item in enumerate(st.session_state.orden_servicios):
        col_s, col_c, col_sub, col_del = st.columns([3, 1, 1, 0.5])
        with col_s:
            serv_label = st.selectbox(
                f"Servicio {idx+1}",
                list(serv_opts.keys()),
                index=list(serv_opts.keys()).index(item['servicio']) if item['servicio'] in serv_opts else 0,
                key=f"ord_serv_{idx}"
            )
            item['servicio'] = serv_label
            serv_id = serv_opts[serv_label]
            precio_serv = float(serv_lookup[serv_id][2])
        with col_c:
            item['cantidad'] = st.number_input("Cant.", min_value=1, step=1, value=int(item['cantidad']), key=f"ord_sc_{idx}")
        with col_sub:
            subtotal_s = item['cantidad'] * precio_serv
            st.write("Subtotal")
            st.write(f"**${subtotal_s:.2f}**")
        with col_del:
            st.write("")
            if st.button("Quitar", key=f"ord_sdel_{idx}"):
                eliminar_servicio(idx)

    col_add_s, _ = st.columns([1, 4])
    with col_add_s:
        if st.button("+ Agregar servicio", key="add_serv_btn"):
            agregar_servicio()
            st.rerun()

    total_servicios = sum(
        item['cantidad'] * float(serv_lookup[serv_opts[item['servicio']]][2])
        for item in st.session_state.orden_servicios
        if item['servicio']
    )
    st.write(f"**Total servicios:** ${total_servicios:.2f}")
else:
    st.info("No hay servicios cargados. Agregalos desde Gestión.")
    total_servicios = 0.0


# --- Productos ---
st.markdown("#### Productos")

if productos:
    prod_activos = [p for p in productos if p[12] and p[8] > 0]
    if prod_activos:
        prod_opts = {f"[{p[1]}] {p[3]} - Stock: {p[8]} - ${p[10]:.2f}": p[0] for p in prod_activos}
        prod_lookup = {p[0]: p for p in prod_activos}

        def agregar_producto():
            st.session_state.orden_productos.append({'producto': None, 'cantidad': 1.0})

        def eliminar_producto(idx):
            if len(st.session_state.orden_productos) > 0:
                st.session_state.orden_productos.pop(idx)
                st.rerun()

        if not st.session_state.orden_productos:
            st.session_state.orden_productos = [{'producto': None, 'cantidad': 1.0}]

        for idx, item in enumerate(st.session_state.orden_productos):
            col_p, col_c, col_pre, col_sub, col_del = st.columns([3, 1, 1, 1, 0.5])
            with col_p:
                prod_label = st.selectbox(
                    f"Producto {idx+1}",
                    list(prod_opts.keys()),
                    index=list(prod_opts.keys()).index(item['producto']) if item['producto'] in prod_opts else 0,
                    key=f"ord_prod_{idx}"
                )
                item['producto'] = prod_label
                pid = prod_opts[prod_label] if prod_label else None
                # Auto-fill precio
                if pid and not item.get('precio'):
                    item['precio'] = float(prod_lookup[pid][10])
            with col_c:
                item['cantidad'] = st.number_input("Cant.", min_value=0.0, step=1.0, value=item['cantidad'], key=f"ord_pc_{idx}")
            with col_pre:
                item['precio'] = st.number_input("Precio", min_value=0.0, step=0.01, value=item.get('precio', 0.0), key=f"ord_pp_{idx}")
            with col_sub:
                subtotal_p = item['cantidad'] * item.get('precio', 0.0)
                st.write("Subtotal")
                st.write(f"**${subtotal_p:.2f}**")
            with col_del:
                st.write("")
                if st.button("Quitar", key=f"ord_pdel_{idx}"):
                    eliminar_producto(idx)

        col_add_p, _ = st.columns([1, 4])
        with col_add_p:
            if st.button("+ Agregar producto", key="add_prod_btn"):
                agregar_producto()
                st.rerun()

        total_productos = sum(
            item['cantidad'] * item.get('precio', 0.0)
            for item in st.session_state.orden_productos
            if item['producto']
        )
        st.write(f"**Total productos:** ${total_productos:.2f}")
    else:
        st.info("No hay productos activos con stock.")
        total_productos = 0.0
else:
    st.info("No hay productos cargados.")
    total_productos = 0.0


# --- Totales + confirmar ---
st.divider()
total_final = total_servicios + total_productos
col_t1, col_t2, col_t3 = st.columns(3)
col_t1.metric("Total servicios", f"${total_servicios:.2f}")
col_t2.metric("Total productos", f"${total_productos:.2f}")
col_t3.metric("TOTAL", f"${total_final:.2f}")

if st.button("✅ Confirmar Orden", type="primary", use_container_width=True):
    if st.session_state.orden_cliente is None or st.session_state.orden_vehiculo is None:
        st.error("Seleccioná cliente y vehículo.")
    elif total_final == 0:
        st.error("La orden no puede estar vacía.")
    else:
        # Validar stock de productos
        stock_ok = True
        for item in st.session_state.orden_productos:
            if item['producto'] and item['cantidad'] > 0:
                pid = prod_opts[item['producto']]
                p = prod_lookup[pid]
                if item['cantidad'] > p[8]:
                    stock_ok = False
                    st.error(f"Stock insuficiente de \"{p[3]}\": solicitado {item['cantidad']}, disponible {p[8]}")
                    break

        if stock_ok:
            orden_id = db.add_orden_servicio(st.session_state.orden_cliente, st.session_state.orden_vehiculo)
            if orden_id is None:
                st.error("Error al crear la orden.")
            else:
                ok_all = True
                # Agregar servicios
                for item in st.session_state.orden_servicios:
                    if item['servicio'] and item['cantidad'] > 0:
                        sid = serv_opts[item['servicio']]
                        if not db.add_orden_detalle(orden_id, servicio_id=sid, cantidad=item['cantidad']):
                            ok_all = False
                            st.error(f"Error al agregar servicio #{sid}")
                            break
                # Agregar productos
                if ok_all:
                    for item in st.session_state.orden_productos:
                        if item['producto'] and item['cantidad'] > 0 and item.get('precio', 0) > 0:
                            pid = prod_opts[item['producto']]
                            if not db.add_orden_detalle(orden_id, producto_id=pid, cantidad=item['cantidad'], precio_unitario=item['precio']):
                                ok_all = False
                                st.error(f"Error al agregar producto #{pid}")
                                break

                if ok_all:
                    st.success(f"Orden #{orden_id} creada correctamente. Total: ${total_final:.2f}")
                    st.session_state.orden_servicios = [{'servicio': None, 'cantidad': 1}]
                    st.session_state.orden_productos = [{'producto': None, 'cantidad': 1.0}]
                    st.rerun()
                else:
                    st.error(f"La orden #{orden_id} quedó incompleta. Revisá los detalles.")

st.divider()

# =============================================================================
# Historial de órdenes
# =============================================================================
st.subheader("Historial de Órdenes")

ordenes = db.get_ordenes(limit=50)
if ordenes:
    data = []
    for o in ordenes:
        # o: (id, fecha, total_productos, total_servicios, total_final, cliente_nombre, vehiculo_patente)
        fecha_raw = o[1]
        if fecha_raw:
            try:
                fecha_str = fecha_raw.strftime("%d/%m/%Y %H:%M") if hasattr(fecha_raw, 'strftime') else str(fecha_raw)
            except Exception:
                fecha_str = str(fecha_raw)
        else:
            fecha_str = "-"
        data.append({
            "ID": o[0],
            "Fecha": fecha_str,
            "Cliente": o[5] or "-",
            "Vehículo": o[6] or "-",
            "Total productos": f"${o[2]:.2f}",
            "Total servicios": f"${o[3]:.2f}",
            "TOTAL": f"${o[4]:.2f}",
        })
    st.dataframe(data, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### Ver detalle de orden")
    orden_sel = st.selectbox("Seleccionar orden", [f"#{o[0]} - {o[5] or '-'} - {o[6] or '-'} - {o[1]}" for o in ordenes])
    if orden_sel:
        orden_id_sel = int(orden_sel.split(" - ")[0].replace("#", ""))
        detalle = db.get_orden_detalle(orden_id_sel)
        if detalle:
            for d in detalle:
                # d: (id, producto_id, servicio_id, cantidad, precio_unitario, producto_nombre, servicio_nombre)
                if d[5]:
                    st.write(f"• {d[5]} x{d[3]} @ ${d[4]:.2f} = ${d[3]*d[4]:.2f}")
                elif d[6]:
                    st.write(f"• {d[6]} x{d[3]} @ ${d[4]:.2f} = ${d[3]*d[4]:.2f}")
        else:
            st.info("Sin detalles.")
else:
    st.info("No hay órdenes de servicio registradas.")
