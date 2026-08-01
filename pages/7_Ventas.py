import logging
import sqlite3
import streamlit as st
import database as db
import tickets as tk
from style import inject_global_css, mostrar_flash, flash_exito, flash_error

logging.basicConfig(level=logging.DEBUG, filename='impresora.log')

st.set_page_config(page_title="Ventas", layout="wide")
inject_global_css()
mostrar_flash()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Debe iniciar sesión para acceder a esta página.")
    st.stop()

st.title("Ventas - Punto de Venta")

if 'imprimir_ultima' not in st.session_state:
    st.session_state.imprimir_ultima = None

productos = db.get_productos()
clientes = db.get_clientes()

if not productos:
    st.warning("⚠️ No hay productos cargados. Agregalos desde Productos primero.")
    st.stop()

# Filtrar productos activos con stock
productos_activos = [p for p in productos if p[11] and p[7] > 0]
if not productos_activos:
    st.warning("⚠️ No hay productos activos con stock disponible.")
    st.stop()

# Lookup de productos por ID - incluye todos los productos para validación de carrito
prod_lookup = {p[0]: p for p in productos}
prod_lookup_activos = {p[0]: p for p in productos_activos}

# Estado del carrito
if 'venta_items' not in st.session_state:
    st.session_state.venta_items = []


def imprimir_venta(venta_id, tipo_comp, cliente_id):
    """Genera e imprime el comprobante de una venta."""
    try:
        vc = db.get_venta_completa(venta_id)
        if not vc:
            logging.error(f"get_venta_completa devolvio None para venta_id={venta_id}")
            return False
        v = vc['venta']
        if not v:
            logging.error(f"vc['venta'] es None para venta_id={venta_id}")
            return False
        items_db = vc.get('items', [])

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
        result = tk.imprimir_comprobante(texto)
        logging.info(f"imprimir_comprobante resulto: {result}")
        return result
    except Exception as e:
        logging.exception(f"Error en imprimir_venta para venta_id={venta_id}: {e}")
        return False


def calcular_totales(items, tipo_comprobante):
    """Calcula subtotal, iva y total segun el tipo de comprobante.
    Reglas (alineadas con database.crear_venta):
      - factura_a: precios ya incluyen IVA. subtotal = total / 1.21, iva = total - subtotal.
      - ticket / factura_b / factura_c: sin IVA desglosado. subtotal = total, iva = 0.
    """
    total = sum(it['cantidad'] * it['precio'] for it in items if it.get('producto_id'))
    if tipo_comprobante == 'factura_a':
        subtotal = round(total / 1.21, 2)
        iva = round(total - subtotal, 2)
    else:
        subtotal = round(total, 2)
        iva = 0.0
    return subtotal, iva, total


# --- Cabecera de la venta ---
st.subheader("Nueva Venta")

# Cliente: Consumidor Final es la primera opción visible
cliente_opciones = ["Consumidor Final"] + [c[1] for c in clientes]
cliente_sel = st.selectbox("Cliente", cliente_opciones, key="venta_cli_sel")
cliente_id = None
if cliente_sel != "Consumidor Final":
    cliente_id = next((c[0] for c in clientes if c[1] == cliente_sel), None)
st.caption(f"Cliente seleccionado: **{cliente_sel}**")

col_tc, col_mp = st.columns(2)
with col_tc:
    tipo_comp = st.selectbox("Comprobante", ["ticket", "factura_a", "factura_b", "factura_c"])
with col_mp:
    metodos = ["efectivo", "tarjeta", "transferencia", "cuenta_corriente"]
    metodo_pago = st.selectbox("Metodo de pago", metodos)

st.markdown("#### Productos")

# Busqueda unificada: escanear codigo de barras o escribir nombre
col_busq, col_agregar = st.columns([3, 1])
with col_busq:
    termino = st.text_input(
        "Buscar producto (escanee codigo de barras o escriba nombre)",
        placeholder="Escanee el codigo o escriba el nombre",
        key="venta_busqueda"
    )
with col_agregar:
    st.write("")
    agregar_click = st.button("Agregar al carrito", use_container_width=True, key="venta_agregar_btn")

if termino:
    producto_encontrado = db.resolver_producto(termino)
    if producto_encontrado:
        p = producto_encontrado
        st.info(f"**{p[2]}** | Stock: {p[7]:.0f} | Precio: ${float(p[10]):.2f} | Cod: {p[1]}")
        if agregar_click:
            if p[7] <= 0:
                st.error("Producto sin stock disponible.")
            else:
                st.session_state.venta_items.append({
                    'producto_id': p[0],
                    'nombre': p[2],
                    'cantidad': 1.0,
                    'precio': float(p[10]),
                    'stock': float(p[7])
                })
                st.rerun()
    else:
        coincidencias = db.buscar_productos_por_nombre(termino)
        if coincidencias:
            st.warning(f"Hay {len(coincidencias)} productos con ese nombre. Escriba el nombre completo.")
        else:
            st.warning("Producto no encontrado con ese codigo o nombre.")

st.markdown("#### Carrito")
with st.form("venta_form"):
    submitted = False
    if not st.session_state.venta_items:
        st.info("Agregue productos al carrito usando el selector de arriba.")
    else:
        for idx, item in enumerate(st.session_state.venta_items[:]):
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 0.5])
            with c1:
                st.write(item['nombre'])
            with c2:
                item['cantidad'] = st.number_input("Cant.", min_value=0.0, step=1.0, value=item['cantidad'], key=f"vc_{idx}")
            with c3:
                st.write(f"${item['precio']:.2f}")
            with c4:
                st.write(f"${item['cantidad'] * item['precio']:.2f}")
            with c5:
                if st.form_submit_button("X", key=f"vdel_{idx}", use_container_width=True):
                    st.session_state.venta_items.pop(idx)
                    st.rerun()

        imprimir_ticket = st.checkbox("Imprimir ticket", value=True, key="venta_imprimir")

        col_submit = st.columns([1])
        with col_submit[0]:
            submitted = st.form_submit_button("Confirmar Venta", type="primary", use_container_width=True)

    if submitted:
        items = []
        error_fraccion = False
        for item in st.session_state.venta_items:
            if item['cantidad'] > 0 and item['precio'] > 0:
                # Usar prod_lookup (todos los productos) para validación de tipo_unidad
                p_lookup = prod_lookup.get(item['producto_id'])
                if not p_lookup:
                    flash_error(f"Producto ID {item['producto_id']} no encontrado en la base de datos.")
                    error_fraccion = True
                    break
                tipo_unidad = p_lookup[6] if len(p_lookup) > 6 else 'Entero'
                if tipo_unidad == 'Entero' and not float(item['cantidad']).is_integer():
                    flash_error(f"No se puede vender \"{item['nombre']}\" fraccionado, seleccione una cantidad entera (ej: 1, 2, 3)")
                    error_fraccion = True
                    break
                items.append({
                    'producto_id': item['producto_id'],
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio']
                })

        if error_fraccion:
            pass
        elif not items:
            flash_error("Agregá al menos un producto con cantidad mayor a 0.")
        else:
            stock_ok = True
            for it in items:
                # Usar prod_lookup_activos para validación de stock (solo activos con stock)
                p = prod_lookup_activos.get(it['producto_id'])
                if not p:
                    stock_ok = False
                    flash_error(f"Producto no disponible o sin stock: ID {it['producto_id']}")
                    break
                if it['cantidad'] > p[7]:
                    stock_ok = False
                    flash_error(f"Stock insuficiente de \"{p[2]}\": solicitado {it['cantidad']}, disponible {p[7]}")
                    break

            if stock_ok:
                usuario_id = st.session_state.user_id
                try:
                    venta_id, numero, error = db.crear_venta(cliente_id, tipo_comp, items, metodo_pago, usuario_id)
                except sqlite3.IntegrityError:
                    venta_id, numero, error = None, None, "Error de integridad en la venta"
                if venta_id:
                    etiqueta = f"{tipo_comp.upper()} {numero:08d}" if numero else f"#{venta_id}"
                    flash_exito(f"Venta confirmada {etiqueta}")
                    st.session_state.venta_items = []

                    if imprimir_ticket:
                        ok_print = imprimir_venta(venta_id, tipo_comp, cliente_id)
                        if ok_print:
                            st.info("Comprobante enviado a la impresora.")
                        else:
                            st.warning("No se pudo imprimir automaticamente. Boton de reintento abajo.")
                            st.session_state.imprimir_ultima = venta_id

                    st.rerun()
                else:
                    flash_error(f"{error or 'Error al procesar la venta.'}")


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
            st.success("✅ Comprobante impreso correctamente.")
            st.session_state.imprimir_ultima = None
            st.rerun()
        else:
            st.error("❌ La impresión falló nuevamente.")

st.divider()

# --- Historial de Ventas ---
st.subheader("Historial de Ventas")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    fecha_desde = st.date_input("Desde", value=None, key="hist_fd")
with col_f2:
    fecha_hasta = st.date_input("Hasta", value=None, key="hist_fh")
with col_f3:
    filtro_opciones = ["Todos", "Consumidor Final"] + [c[1] for c in clientes]
    filtro_cliente = st.selectbox("Cliente", filtro_opciones, key="hist_cli")

if st.button("Buscar", key="hist_btn"):
    fd = fecha_desde.strftime("%Y-%m-%d") if fecha_desde else None
    fh = fecha_hasta.strftime("%Y-%m-%d") if fecha_hasta else None
    cli_id = None
    only_cf = False
    if filtro_cliente == "Consumidor Final":
        only_cf = True
    elif filtro_cliente != "Todos":
        cli_id = next((c[0] for c in clientes if c[1] == filtro_cliente), None)

    ventas = db.get_ventas(limit=100, fecha_desde=fd, fecha_hasta=fh,
                           cliente_id=cli_id, only_consumidor_final=only_cf)

    if ventas:
        for v in ventas:
            with st.expander(f"#{v[0]} - {v[11] or 'Consumidor Final'} - {v[3]}-{v[4]:08d} - ${v[7]:.2f} - Confirmada"):
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
        st.info("ℹ️ No se encontraron ventas.")
