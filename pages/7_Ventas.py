import streamlit as st
import database as db
import tickets as tk
from style import inject_global_css

st.set_page_config(page_title="Ventas", layout="wide")
inject_global_css()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Debe iniciar sesión para acceder a esta página.")
    st.stop()

st.title("Ventas - Punto de Venta")

if 'imprimir_ultima' not in st.session_state:
    st.session_state.imprimir_ultima = None

productos = db.get_productos()
clientes = db.get_clientes()

if not productos:
    st.warning("No hay productos cargados. Agregalos desde Productos primero.")
    st.stop()

# Filtrar productos activos con stock
productos_activos = [p for p in productos if p[12] and p[8] > 0]
if not productos_activos:
    st.warning("No hay productos activos con stock disponible.")
    st.stop()

# Mapeos para seleccionar productos
prod_opts = {f"[{p[1]}] {p[3]} - Stock: {p[8]} - ${p[10]:.2f}": p[0] for p in productos_activos}
prod_lookup = {p[0]: p for p in productos_activos}

# Estado del carrito
if 'venta_items' not in st.session_state:
    st.session_state.venta_items = [{'producto': None, 'cantidad': 1.0, 'precio': 0.0}]


def agregar_fila():
    st.session_state.venta_items.append({'producto': None, 'cantidad': 1.0, 'precio': 0.0})


def eliminar_fila(idx):
    if len(st.session_state.venta_items) > 1:
        st.session_state.venta_items.pop(idx)
        st.rerun()


def calcular_totales(items, tipo_comprobante):
    """Calcula subtotal, iva y total segun el tipo de comprobante.
    Reglas (alineadas con database.crear_venta):
      - factura_a: precios ya incluyen IVA. subtotal = total / 1.21, iva = total - subtotal.
      - ticket / factura_b / factura_c: sin IVA desglosado. subtotal = total, iva = 0.
    """
    total = sum(it['cantidad'] * it['precio'] for it in items if it['producto'])
    if tipo_comprobante == 'factura_a':
        subtotal = round(total / 1.21, 2)
        iva = round(total - subtotal, 2)
    else:
        subtotal = round(total, 2)
        iva = 0.0
    return subtotal, iva, total


# --- Cabecera de la venta ---
st.subheader("Nueva Venta")

# Cliente: Consumidor Final por defecto, resto en expander
cliente_id = None
cliente_sel = "Consumidor Final"
with st.expander("Seleccionar otro cliente", expanded=False):
    cliente_otro = st.selectbox("Cliente", [c[1] for c in clientes], key="venta_cli_sel")
    if cliente_otro:
        cliente_sel = cliente_otro
        cliente_id = next((c[0] for c in clientes if c[1] == cliente_otro), None)
st.caption(f"Cliente seleccionado: **{cliente_sel}**")

col_tc, col_mp = st.columns(2)
with col_tc:
    tipo_comp = st.selectbox("Comprobante", ["ticket", "factura_a", "factura_b", "factura_c"])
with col_mp:
    metodos = ["efectivo", "tarjeta", "transferencia", "cuenta_corriente"]
    metodo_pago = st.selectbox("Metodo de pago", metodos)

st.markdown("#### Productos")
with st.form("venta_form"):
    for idx, item in enumerate(st.session_state.venta_items):
        col_prod, col_cant, col_precio, col_sub, col_del = st.columns([3, 1, 1, 1, 0.5])
        with col_prod:
            prod_label = st.selectbox(
                f"Producto {idx+1}",
                list(prod_opts.keys()),
                index=list(prod_opts.keys()).index(item['producto']) if item['producto'] in prod_opts else 0,
                key=f"venta_prod_{idx}"
            )
            item['producto'] = prod_label
            # Auto-fill precio con precio de venta del producto
            if prod_label and item['precio'] == 0.0:
                pid = prod_opts[prod_label]
                p = prod_lookup[pid]
                item['precio'] = float(p[10])
        with col_cant:
            item['cantidad'] = st.number_input(
                "Cant.", min_value=0.0, step=1.0,
                value=item['cantidad'], key=f"venta_cant_{idx}"
            )
        with col_precio:
            # Precio NO editable (se asigna automáticamente desde el producto)
            st.write("Precio Unit.")
            st.write(f"**${item['precio']:.2f}**")
        with col_sub:
            subtotal_item = item['cantidad'] * item['precio']
            st.write("Subtotal")
            st.write(f"**${subtotal_item:.2f}**")
        with col_del:
            st.write("")
            if st.form_submit_button("🗑️", key=f"venta_del_{idx}", use_container_width=True):
                eliminar_fila(idx)

    col_add, col_spacer, col_submit = st.columns([1, 2, 2])
    with col_add:
        if st.form_submit_button("Agregar producto", use_container_width=True):
            agregar_fila()
            st.rerun()
    with col_submit:
        submitted = st.form_submit_button("Confirmar Venta", type="primary", use_container_width=True)

    if submitted:
        items = []
        for item in st.session_state.venta_items:
            if item['producto'] and item['cantidad'] > 0 and item['precio'] > 0:
                items.append({
                    'producto_id': prod_opts[item['producto']],
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio']
                })

        if not items:
            st.error("Agregá al menos un producto con cantidad mayor a 0.")
        else:
            # Validar stock antes de enviar
            stock_ok = True
            for it in items:
                p = prod_lookup[it['producto_id']]
                if it['cantidad'] > p[8]:
                    stock_ok = False
                    st.error(f"Stock insuficiente de \"{p[3]}\": solicitado {it['cantidad']}, disponible {p[8]}")
                    break

            if stock_ok:
                usuario_id = st.session_state.user_id
                venta_id, numero, error = db.crear_venta(cliente_id, tipo_comp, items, metodo_pago, usuario_id)
                if venta_id:
                    etiqueta = f"{tipo_comp.upper()} {numero:08d}" if numero else f"#{venta_id}"
                    st.success(f"Venta confirmada! {etiqueta}")
                    st.session_state.venta_items = [{'producto': None, 'cantidad': 1.0, 'precio': 0.0}]

                    # Impresión automática
                    ok_print = imprimir_venta(venta_id, tipo_comp, cliente_id)
                    if ok_print:
                        st.info("🖨️ Comprobante enviado a la impresora.")
                    else:
                        st.warning("No se pudo imprimir automáticamente. Botón de reintento abajo.")
                        st.session_state.imprimir_ultima = venta_id

                    st.rerun()
                else:
                    st.error(error or "Error al procesar la venta.")


def imprimir_venta(venta_id, tipo_comp, cliente_id):
    """Genera e imprime el comprobante de una venta."""
    try:
        vc = db.get_venta_completa(venta_id)
        if not vc:
            return False
        v = vc['venta']
        items_db = vc['items']

        venta_dict = {
            'tipo_comprobante': v[2],
            'punto_venta': v[3],
            'numero_comprobante': v[4],
            'subtotal': v[5],
            'iva': v[6],
            'total': v[7],
            'metodo_pago': v[8],
            'creado_en': str(v[10]) if v[10] else "",
        }
        items_dict = [{
            'producto_nombre': it[5],
            'cantidad': it[2],
            'precio_unitario': it[3],
            'subtotal': it[4],
        } for it in items_db]

        cliente_dict = None
        if cliente_id:
            clientes = db.get_clientes()
            cli = next((c for c in clientes if c[0] == cliente_id), None)
            if cli:
                cliente_dict = {'nombre': cli[1], 'telefono': cli[2], 'email': cli[3]}

        if tipo_comp == 'ticket':
            texto = tk.generar_ticket_texto(venta_dict, items_dict, cliente_dict)
        elif tipo_comp == 'factura_a':
            texto = tk.generar_factura_a_texto(venta_dict, items_dict, cliente_dict or {'nombre': 'Consumidor Final'})
        elif tipo_comp == 'factura_b':
            texto = tk.generar_factura_b_texto(venta_dict, items_dict, cliente_dict or {'nombre': 'Consumidor Final'})
        elif tipo_comp == 'factura_c':
            texto = tk.generar_factura_c_texto(venta_dict, items_dict, cliente_dict or {'nombre': 'Consumidor Final'})
        else:
            texto = tk.generar_ticket_texto(venta_dict, items_dict, cliente_dict)

        # Guardar como respaldo
        tk.guardar_comprobante_archivo(texto, venta_dict, tipo_comp)
        # Enviar a impresora
        return tk.imprimir_comprobante(texto)
    except Exception:
        return False

# Totales calculados (visual)
subtotal, iva, total = calcular_totales(st.session_state.venta_items, tipo_comp)
st.divider()
col_t1, col_t2, col_t3 = st.columns([1, 1, 1])
col_t1.metric("Subtotal", f"${subtotal:.2f}")
col_t2.metric("IVA", f"${iva:.2f}")
col_t3.metric("Total", f"${total:.2f}")

# Reintentar impresión si quedó pendiente
if st.session_state.imprimir_ultima:
    st.warning(f"⚠️ Impresión pendiente de venta #{st.session_state.imprimir_ultima}")
    if st.button("🖨️ Reintentar impresión"):
        ok = imprimir_venta(st.session_state.imprimir_ultima, tipo_comp, cliente_id)
        if ok:
            st.success("Comprobante impreso correctamente.")
            st.session_state.imprimir_ultima = None
            st.rerun()
        else:
            st.error("La impresión falló nuevamente.")

st.divider()

# --- Historial de Ventas ---
st.subheader("Historial de Ventas")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    fecha_desde = st.date_input("Desde", value=None, key="hist_fd")
with col_f2:
    fecha_hasta = st.date_input("Hasta", value=None, key="hist_fh")
with col_f3:
    filtro_cliente = st.selectbox("Cliente", ["Todos"] + [c[1] for c in clientes], key="hist_cli")

if st.button("Buscar", key="hist_btn"):
    fd = fecha_desde.strftime("%Y-%m-%d") if fecha_desde else None
    fh = fecha_hasta.strftime("%Y-%m-%d") if fecha_hasta else None
    cli_id = None
    if filtro_cliente != "Todos":
        cli_id = next((c[0] for c in clientes if c[1] == filtro_cliente), None)

    ventas = db.get_ventas(limit=100, fecha_desde=fd, fecha_hasta=fh, cliente_id=cli_id)

    if ventas:
        for v in ventas:
            estado_label = "Anulada" if len(v) > 13 and v[13] == 'anulada' else "Confirmada"
            with st.expander(f"#{v[0]} - {v[11] or 'Consumidor Final'} - {v[3]}-{v[4]:08d} - ${v[7]:.2f} - {estado_label}"):
                st.write(f"**Fecha:** {v[10]}")
                st.write(f"**Tipo:** {v[2].upper()} {v[3]}-{v[4]:08d}")
                st.write(f"**Método pago:** {v[8]}")
                st.write(f"**Usuario:** {v[12]}")

                items = db.get_venta_detalle(v[0])
                for it in items:
                    st.write(f"  - {it[5]} x{it[2]} @ ${it[3]:.2f} = ${it[4]:.2f}")

                st.write(f"**Subtotal:** ${v[5]:.2f}")
                st.write(f"**IVA:** ${v[6]:.2f}")
                st.write(f"**Total:** ${v[7]:.2f}")
    else:
        st.info("No se encontraron ventas.")
