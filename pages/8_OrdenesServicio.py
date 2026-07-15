import streamlit as st
import database as db
from datetime import datetime

st.set_page_config(page_title="Orden de Servicio")

st.title("Orden de Servicio")

# Initialize session state for line items
if 'line_items' not in st.session_state:
    st.session_state.line_items = []  # each item: dict with tipo ('producto'/'servicio'), id, nombre, cantidad, precio_unitario

# Load clients and vehicles for selection
clientes = db.get_clientes()
vehiculos = db.get_vehiculos()
servicios = db.get_servicios()
productos = db.get_productos()

cliente_options = {c[1]: c[0] for c in clientes}  # name -> id
# For vehicle we need to filter by selected client later, but we can load all and filter in UI
vehiculo_options = {f"{v[2]} ({v[3]} {v[4]})": v[0] for v in vehiculos}  # display -> id

st.subheader("Datos de la Orden")
col1, col2 = st.columns(2)
with col1:
    cliente_sel = st.selectbox("Cliente", options=list(cliente_options.keys()) if cliente_options else [])
with col2:
    # Filter vehicles by selected client
    if cliente_sel:
        cliente_id = cliente_options[cliente_sel]
        vehiculos_cliente = [v for v in vehiculos if v[1] == cliente_id]
        vehiculo_options_filtered = {f"{v[2]} ({v[3]} {v[4]})": v[0] for v in vehiculos_cliente}
    else:
        vehiculo_options_filtered = {}
    vehiculo_sel = st.selectbox("Vehículo", options=list(vehiculo_options_filtered.keys()) if vehiculo_options_filtered else [])

fecha = st.date_input("Fecha", value=datetime.now())

st.subheader("Agregar Ítem")
tipo_item = st.radio("Tipo", ["Producto", "Servicio"], horizontal=True)
if tipo_item == "Producto":
    producto_opts = {p[3]: p[0] for p in productos}  # nombre -> id
    producto_sel = st.selectbox("Producto", options=list(producto_opts.keys()) if producto_opts else [])
    cantidad = st.number_input("Cantidad", min_value=0.0, step=0.01, format="%.2f")
    # precio unitario will be taken from product price (precio_venta) but we could allow override? We'll use product price.
    if st.button("Agregar Producto"):
        if producto_sel and cantidad > 0:
            pid = producto_opts[producto_sel]
            # get product name and price
            prod_info = next((p for p in productos if p[0] == pid), None)
            if prod_info:
                nombre = prod_info[3]
                precio = prod_info[10]  # precio_venta
                st.session_state.line_items.append({
                    'tipo': 'producto',
                    'id': pid,
                    'nombre': nombre,
                    'cantidad': cantidad,
                    'precio_unitario': precio
                })
                st.success(f"Producto {nombre} agregado")
            else:
                st.error("Producto no encontrado")
        else:
            st.error("Seleccione producto y cantidad > 0")
else:
    servicio_opts = {s[1]: s[0] for s in servicios}  # nombre -> id
    servicio_sel = st.selectbox("Servicio", options=list(servicio_opts.keys()) if servicio_opts else [])
    cantidad = st.number_input("Cantidad", min_value=0.0, step=0.01, format="%.2f")
    if st.button("Agregar Servicio"):
        if servicio_sel and cantidad > 0:
            sid = servicio_opts[servicio_sel]
            serv_info = next((s for s in servicios if s[0] == sid), None)
            if serv_info:
                nombre = serv_info[1]
                precio = serv_info[2]
                st.session_state.line_items.append({
                    'tipo': 'servicio',
                    'id': sid,
                    'nombre': nombre,
                    'cantidad': cantidad,
                    'precio_unitario': precio
                })
                st.success(f"Servicio {nombre} agregado")
            else:
                st.error("Servicio no encontrado")
        else:
            st.error("Seleccione servicio y cantidad > 0")

# Display current line items
st.subheader("Ítems de la Orden")
if st.session_state.line_items:
    total_servicios = 0.0
    total_productos = 0.0
    for idx, item in enumerate(st.session_state.line_items):
        col1, col2, col3, col4, col5 = st.columns([3,1,1,1,1])
        with col1:
            st.write(f"{item['tipo'].capitalize()}: {item['nombre']}")
        with col2:
            st.write(f"{item['cantidad']}")
        with col3:
            st.write(f"${item['precio_unitario']:.2f}")
        with col4:
            subtotal = item['cantidad'] * item['precio_unitario']
            st.write(f"${subtotal:.2f}")
            if item['tipo'] == 'servicio':
                total_servicios += subtotal
            else:
                total_productos += subtotal
        with col5:
            if st.button("Quitar", key=f"del_{idx}"):
                st.session_state.line_items.pop(idx)
                st.experimental_rerun()
    st.write(f"**Subtotal Productos:** ${total_productos:.2f}")
    st.write(f"**Subtotal Servicios:** ${total_servicios:.2f}")
    total = total_productos + total_servicios
    st.write(f"**Total:** ${total:.2f}")

    if st.button("Crear Orden de Servicio"):
        # Validate
        if not cliente_sel:
            st.error("Seleccione un cliente")
        elif not vehiculo_sel:
            st.error("Seleccione un vehículo")
        elif not st.session_state.line_items:
            st.error("Agregue al menos un ítem")
        else:
            cliente_id = cliente_options[cliente_sel]
            vehiculo_id = vehiculo_options_filtered[vehiculo_sel]
            # Create order
            orden_id = db.add_orden_servicio(cliente_id, vehiculo_id, datetime.combine(fecha, datetime.min.time()))
            if orden_id is None:
                st.error("Error al crear la orden")
            else:
                # Add each line item
                ok = True
                for item in st.session_state.line_items:
                    if not db.add_orden_detalle(orden_id,
                                                producto_id=item['id'] if item['tipo'] == 'producto' else None,
                                                servicio_id=item['id'] if item['tipo'] == 'servicio' else None,
                                                cantidad=item['cantidad'],
                                                precio_unitario=item['precio_unitario']):
                        ok = False
                        break
                if ok:
                    st.success(f"Orden de Servicio #{orden_id} creada exitosamente")
                    # Clear line items
                    st.session_state.line_items = []
                    # Optionally, we could show a summary or reset form
                else:
                    st.error("Error al agregar alguno de los ítems")
else:
    st.info("No hay ítems agregados aún.")

st.subheader("Ódenes recientes")
ordenes = db.get_ordenes(limit=5)
for o in ordenes:
    # o: (id, fecha, total_productos, total_servicios, total_final, cliente_nombre, vehiculo_patente)
    fecha_str = o[1].strftime("%d/%m/%y %H:%M") if o[1] else ""
    st.write(f"**#{o[0]}** - {fecha_str} - Cliente: {o[5]} - Vehículo: {o[6]} - Total: ${o[4]:.2f}")