import streamlit as st
import database as db

st.set_page_config(page_title="Ventas", layout="wide")
st.title("Ventas - Punto de Venta")

productos = db.get_productos()
clientes = db.get_clientes()

if not productos:
    st.warning("No hay productos cargados. Agregalos desde Configuración.")
    st.stop()

if 'carrito' not in st.session_state:
    st.session_state.carrito = []

if 'vista_previa_idx' not in st.session_state:
    st.session_state.vista_previa_idx = None

if 'busqueda' not in st.session_state:
    st.session_state.busqueda = ""


def calcular_totales(carrito, tipo_comprobante):
    """Calcula subtotal, iva y total segun el tipo de comprobante.

    Reglas (alineadas con database.crear_venta):
      - factura_a: precios ya incluyen IVA. subtotal = total / 1.21, iva = total - subtotal.
      - ticket / factura_b / factura_c: sin IVA desglosado. subtotal = total, iva = 0.
    """
    total = sum(it['subtotal'] for it in carrito)
    if tipo_comprobante == 'factura_a':
        subtotal = round(total / 1.21, 2)
        iva = round(total - subtotal, 2)
    else:
        subtotal = round(total, 2)
        iva = 0.0
    return subtotal, iva, total


# --- Sidebar: Carrito ---
with st.sidebar:
    st.header("Carrito")
    if st.session_state.carrito:
        for idx, item in enumerate(st.session_state.carrito):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{item['nombre']}**")
                st.caption(f"${item['precio']:.2f} x {item['cantidad']}")
                stock = item.get('stock_disponible', None)
                if stock is not None and item['cantidad'] > stock:
                    st.error(f"Stock insuficiente (disp: {stock})")
            with col2:
                st.write(f"${item['subtotal']:.2f}")
            with col3:
                if st.button("X", key=f"del_{idx}"):
                    st.session_state.carrito.pop(idx)
                    st.rerun()
    else:
        st.info("Carrito vacio")


# --- Area principal ---
col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("Agregar productos")

    busqueda = st.text_input(
        "Buscar por codigo de barras o nombre",
        value=st.session_state.busqueda,
        placeholder="Escanear o escribir...",
        key="busqueda_input"
    )
    if busqueda != st.session_state.busqueda:
        st.session_state.busqueda = busqueda
        st.session_state.vista_previa_idx = None
        st.rerun()

    productos_filtrados = productos
    if busqueda:
        busqueda_lower = busqueda.lower()
        productos_filtrados = [p for p in productos if
                               busqueda_lower in (p[2] or '').lower() or
                               busqueda_lower in (p[3] or '').lower() or
                               busqueda_lower in (p[4] or '').lower()]

    limite_resultados = 24
    if productos_filtrados:
        cols = st.columns(3)
        for idx, p in enumerate(productos_filtrados[:limite_resultados]):
            with cols[idx % 3]:
                stock = p[8] if len(p) > 8 else 0
                if stock > 0:
                    if st.button(f"{p[4]}\n${p[10]:.2f} | Stock: {stock}", key=f"prod_{p[0]}", use_container_width=True):
                        existe = False
                        for item in st.session_state.carrito:
                            if item['producto_id'] == p[0]:
                                item['cantidad'] += 1
                                item['subtotal'] = item['cantidad'] * item['precio']
                                existe = True
                                break
                        if not existe:
                            st.session_state.carrito.append({
                                'producto_id': p[0],
                                'nombre': p[4],
                                'precio': float(p[10]),
                                'cantidad': 1,
                                'subtotal': float(p[10]),
                                'stock_disponible': float(stock)
                            })
                        st.rerun()
                else:
                    st.button(f"{p[4]} (SIN STOCK)", key=f"prod_{p[0]}", disabled=True, use_container_width=True)

        if len(productos_filtrados) > limite_resultados:
            st.caption(f"Mostrando {limite_resultados} de {len(productos_filtrados)} resultados. Afina la busqueda.")

        st.divider()
        st.subheader("Vista previa")
        if st.session_state.vista_previa_idx is not None:
            p = productos_filtrados[st.session_state.vista_previa_idx]
            st.write(f"**Nombre:** {p[4]}")
            st.write(f"**Codigo interno:** {p[2]}")
            st.write(f"**Codigo barras:** {p[3]}")
            st.write(f"**Precio:** ${p[10]:.2f}")
            st.write(f"**Stock actual:** {p[8]}")
            if st.button("Cerrar vista previa"):
                st.session_state.vista_previa_idx = None
                st.rerun()
        else:
            st.caption("Toca un producto para ver el detalle (futura mejora: selectable card).")

with col_der:
    st.subheader("Finalizar venta")

    if st.session_state.carrito:
        cliente_opciones = ["Consumidor Final"] + [c[1] for c in clientes]
        cliente_sel = st.selectbox("Cliente", cliente_opciones)
        cliente_id = None
        if cliente_sel != "Consumidor Final":
            cliente_id = next((c[0] for c in clientes if c[1] == cliente_sel), None)

        tipo_comp = st.selectbox("Comprobante", ["ticket", "factura_a", "factura_b", "factura_c"])

        metodos = ["efectivo", "tarjeta_debito", "tarjeta_credito", "transferencia", "cuenta_corriente"]
        metodo_pago = st.selectbox("Metodo de pago", metodos)

        usuario_id = 1

        subtotal, iva, total = calcular_totales(st.session_state.carrito, tipo_comp)
        st.write(f"**Subtotal:** ${subtotal:.2f}")
        if iva > 0:
            st.write(f"**IVA (incluido):** ${iva:.2f}")
        st.write(f"**Total:** ${total:.2f}")

        if st.button("CONFIRMAR VENTA", type="primary", use_container_width=True):
            items = [{
                'producto_id': item['producto_id'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio']
            } for item in st.session_state.carrito]

            venta_id, numero, error = db.crear_venta(cliente_id, tipo_comp, items, metodo_pago, usuario_id)

            if venta_id:
                etiqueta = f"{tipo_comp.upper()} {numero:08d}" if numero else f"#{venta_id}"
                st.success(f"Venta confirmada! {etiqueta}")
                st.session_state.carrito = []
                st.rerun()
            else:
                msg = error or "Error al procesar la venta."
                st.error(msg)
    else:
        st.info("Agrega productos al carrito")

st.divider()

st.subheader("Historial de Ventas")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    fecha_desde = st.date_input("Desde", value=None)
with col_f2:
    fecha_hasta = st.date_input("Hasta", value=None)
with col_f3:
    filtro_cliente = st.selectbox("Cliente", ["Todos"] + [c[1] for c in clientes])

if st.button("Buscar"):
    fd = fecha_desde.strftime("%Y-%m-%d") if fecha_desde else None
    fh = fecha_hasta.strftime("%Y-%m-%d") if fecha_hasta else None
    cli_id = None
    if filtro_cliente != "Todos":
        cli_id = next((c[0] for c in clientes if c[1] == filtro_cliente), None)

    ventas = db.get_ventas(limit=100, fecha_desde=fd, fecha_hasta=fh, cliente_id=cli_id)

    if ventas:
        for v in ventas:
            with st.expander(f"#{v[0]} - {v[11] or 'Consumidor Final'} - {v[3]}-{v[4]:08d} - ${v[7]:.2f} - {v[9]}"):
                st.write(f"**Fecha:** {v[10]}")
                st.write(f"**Tipo:** {v[2].upper()} {v[3]}-{v[4]:08d}")
                st.write(f"**Metodo pago:** {v[8]}")
                st.write(f"**Usuario:** {v[12]}")

                items = db.get_venta_detalle(v[0])
                for it in items:
                    st.write(f"  - {it[5]} x{it[2]} @ ${it[3]:.2f} = ${it[4]:.2f}")

                st.write(f"**Subtotal:** ${v[5]:.2f}")
                st.write(f"**IVA:** ${v[6]:.2f}")
                st.write(f"**Total:** ${v[7]:.2f}")
    else:
        st.info("No se encontraron ventas")
