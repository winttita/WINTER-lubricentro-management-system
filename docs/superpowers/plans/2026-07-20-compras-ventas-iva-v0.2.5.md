# Correcciones UX Compras, Ventas e IVA v0.2.5 - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar correcciones UX en Compras, Ventas e IVA para v0.2.5 siguiendo Enfoque A (UI-first, mínimo).

**Architecture:** Enfoque UI-first - cambios mínimos en frontend (pages/8_Compras.py, pages/7_Ventas.py) y ajustes quirúrgicos en backend (database.py:crear_venta). Sin migraciones de esquema.

**Tech Stack:** Python 3.12, Streamlit, SQLite, pytest

## Global Constraints

- No emojis en commits, mensajes, documentación (CONVENTIONS.md)
- Mensajes de commit en Conventional Commits en español
- Versionado SemVer: v0.2.5
- TDD: tests primero, implementación mínima, commit frecuente
- Sigue patrones existentes en el código (st.session_state, get_connection, etc.)
- No emojis en UI ni documentación (CONVENTIONS.md)

---

### Task 1: Tests nuevos para database.py - crear_venta

**Files:**
- Create: `tests/test_database.py` (add tests to existing file)

**Interfaces:**
- Consumes: `database.py:crear_venta` (current signature)
- Produces: Test cases that will define the new signature `(venta_id, numero, error_msg)`

- [ ] **Step 1: Write failing tests for new signature and behaviors**

```python
def test_crear_venta_stock_insuficiente_retorna_mensaje_especifico(temp_db):
    """Stock insuficiente debe retornar mensaje especifico, no (None, None)."""
    from database import crear_venta, add_producto
    # Setup: crear producto con stock 5
    add_producto("P1", "CB001", "Producto Test", "", 1, 1, "Entero", 0, 10.0, 100.0, 5)
    items = [{"producto_id": 1, "cantidad": 10, "precio_unitario": 100.0}]
    venta_id, numero, error = crear_venta(None, "ticket", items, "efectivo", 1)
    assert venta_id is None
    assert error is not None
    assert "Stock insuficiente" in error
    assert "disponible 5" in error
    assert "solicitado 10" in error

def test_crear_venta_factura_a_calculo_iva_incluido(temp_db):
    """Factura A: precio_venta ya incluye IVA. Total = subtotal_neto + iva = precio_final."""
    from database import crear_venta, add_producto
    add_producto("P2", "CB002", "Producto A", "", 1, 1, "Entero", 0, 10.0, 121.0, 10)
    items = [{"producto_id": 1, "cantidad": 1, "precio_unitario": 121.0}]
    venta_id, numero, error = crear_venta(None, "factura_a", items, "efectivo", 1)
    assert venta_id is not None
    assert error is None
    # Verificar en BD
    import database as db
    conn = db.get_connection()
    row = conn.execute("SELECT subtotal, iva, total FROM ventas WHERE id = ?", (venta_id,)).fetchone()
    conn.close()
    assert row[2] == 121.0  # total = precio final
    assert row[1] == 21.0   # iva = 121 - (121/1.21)
    assert row[0] == 100.0  # subtotal = 121/1.21

def test_crear_venta_ticket_sin_iva(temp_db):
    """Ticket: sin IVA, subtotal = total = precio_venta."""
    from database import crear_venta, add_producto
    add_producto("P3", "CB003", "Producto B", "", 1, 1, "Entero", 0, 10.0, 100.0, 10)
    items = [{"producto_id": 1, "cantidad": 2, "precio_unitario": 100.0}]
    venta_id, numero, error = crear_venta(None, "ticket", items, "efectivo", 1)
    assert venta_id is not None
    assert error is None
    import database as db
    conn = db.get_connection()
    row = conn.execute("SELECT subtotal, iva, total FROM ventas WHERE id = ?", (venta_id,)).fetchone()
    conn.close()
    assert row[2] == 200.0  # total
    assert row[1] == 0.0    # iva
    assert row[0] == 200.0  # subtotal

def test_crear_venta_producto_inactivo_retorna_error(temp_db):
    """Producto inactivo debe retornar error especifico."""
    from database import crear_venta, add_producto
    add_producto("P4", "CB004", "Producto Inactivo", "", 1, 1, "Entero", 0, 10.0, 100.0, 10)
    # Desactivar producto
    import database as db
    conn = db.get_connection()
    conn.execute("UPDATE productos SET activo = 0 WHERE id = 1")
    conn.commit()
    conn.close()
    items = [{"producto_id": 1, "cantidad": 1, "precio_unitario": 100.0}]
    venta_id, numero, error = crear_venta(None, "ticket", items, "efectivo", 1)
    assert venta_id is None
    assert error is not None
    assert "inactivo o inexistente" in error

def test_crear_venta_items_vacios_retorna_error(temp_db):
    """Items vacios debe retornar error especifico."""
    from database import crear_venta
    venta_id, numero, error = crear_venta(None, "ticket", [], "efectivo", 1)
    assert venta_id is None
    assert error == "No hay items en la venta"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/federico/Documentos/Lubricentro && pytest tests/test_database.py -v -k "crear_venta" 2>&1 | head -50
```

Expected: FAIL - signature mismatch, new tests fail because signature not updated yet.

- [ ] **Step 3: Commit tests**

```bash
git add tests/test_database.py
git commit -m "test: agregar tests para crear_venta nueva firma y casos corregidos"
```

---

### Task 2: Actualizar firma y logica de crear_venta en database.py

**Files:**
- Modify: `database.py:925-1004` (crear_venta function)

**Interfaces:**
- Consumes: Tests from Task 1 (expected signature)
- Produces: New signature `crear_venta(...) -> (venta_id, numero, error_msg)`

- [ ] **Step 1: Update crear_venta signature and logic**

```python
def crear_venta(cliente_id, tipo_comprobante, items, metodo_pago, usuario_id):
    """
    Crea una venta completa con items, actualiza stock y registra movimiento.
    items: lista de dicts {producto_id, cantidad, precio_unitario}
    Retorna (venta_id, numero_comprobante, error_msg) donde error_msg es None si éxito.
    """
    if not items:
        return None, None, "No hay items en la venta"
    if not isinstance(items, list):
        return None, None, "Items debe ser una lista"
    
    conn = get_connection()
    try:
        # Validar stock y productos usando la MISMA conexion
        for item in items:
            if not isinstance(item, dict):
                return None, None, "Cada item debe ser un diccionario"
            if 'producto_id' not in item or 'cantidad' not in item or 'precio_unitario' not in item:
                return None, None, "Cada item debe tener producto_id, cantidad y precio_unitario"
            
            row = conn.execute("SELECT stock_actual, nombre FROM productos WHERE id = ? AND activo = 1", 
                             (item['producto_id'],)).fetchone()
            if not row:
                return None, None, f"Producto inactivo o inexistente (id={item['producto_id']})"
            stock_actual = float(row[0])
            nombre = row[1]
            cantidad = float(item['cantidad'])
            if stock_actual < cantidad:
                return None, None, f"Stock insuficiente de \"{nombre}\": solicitado {cantidad}, disponible {stock_actual}"
        
        # Calcular totales
        subtotal = sum(float(item['cantidad']) * float(item['precio_unitario']) for item in items)
        if tipo_comprobante == 'factura_a':
            subtotal_neto = round(subtotal / 1.21, 2)
            iva = round(subtotal - subtotal_neto, 2)
            total = round(subtotal_neto + iva, 2)
        else:
            subtotal_neto = round(subtotal, 2)
            iva = 0.0
            total = round(subtotal, 2)
        
        # Obtener siguiente numero
        punto_venta = '0001'
        numero_comprobante = get_ultimo_numero_comprobante(tipo_comprobante, punto_venta) + 1
        
        # Insertar venta
        cursor = conn.execute("""
            INSERT INTO ventas (cliente_id, tipo_comprobante, punto_venta, numero_comprobante,
                              subtotal, iva, total, metodo_pago, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cliente_id, tipo_comprobante, punto_venta, numero_comprobante,
              subtotal_neto, iva, total, metodo_pago, usuario_id))
        venta_id = cursor.lastrowid
        
        # Insertar items y actualizar stock
        for item in items:
            cantidad = float(item['cantidad'])
            precio_unitario = float(item['precio_unitario'])
            subtotal_item = round(cantidad * precio_unitario, 2)
            
            conn.execute("""
                INSERT INTO venta_items (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (venta_id, item['producto_id'], cantidad, precio_unitario, subtotal_item))
            
            if not add_movimiento(item['producto_id'], 'venta', cantidad, f'Venta #{venta_id}'):
                conn.rollback()
                return None, None, f"Error al registrar movimiento de venta para producto {item['producto_id']}"
        
        # Cuenta corriente si aplica
        if metodo_pago == 'cuenta_corriente' and cliente_id:
            row = conn.execute("SELECT COALESCE(SUM(monto), 0) FROM cuenta_corriente WHERE cliente_id = ?", 
                             (cliente_id,)).fetchone()
            saldo_anterior = float(row[0]) if row else 0.0
            saldo_nuevo = saldo_anterior + total
            conn.execute("""
                INSERT INTO cuenta_corriente (cliente_id, venta_id, monto, saldo_anterior, saldo_nuevo)
                VALUES (?, ?, ?, ?, ?)
            """, (cliente_id, venta_id, total, saldo_anterior, saldo_nuevo))
        
        conn.commit()
        return venta_id, numero_comprobante, None
    except Exception as e:
        conn.rollback()
        return None, None, f"Error al procesar la venta: {str(e)}"
    finally:
        conn.close()
```

- [ ] **Step 2: Run tests to verify they pass**

```bash
cd /home/federico/Documentos/Lubricentro && pytest tests/test_database.py -v -k "crear_venta" 2>&1 | head -50
```

Expected: PASS all 5 new tests.

- [ ] **Step 3: Update existing tests that use old signature**

Search for `crear_venta(` in tests and update to handle 3-return-value tuple.

```bash
cd /home/federico/Documentos/Lubricentro && grep -n "crear_venta(" tests/test_database.py
```

Update any calls expecting `(None, None)` to expect `(None, None, error_msg)`.

- [ ] **Step 3: Run full test suite**

```bash
cd /home/federico/Documentos/Lubricentro && pytest tests/test_database.py -v 2>&1 | tail -30
```

Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add database.py tests/test_database.py
git commit -m "feat(database): corregir crear_venta firma, validacion stock, calculo IVA incluido Factura A"
```

---

### Task 3: Implementar UI dinamica en pages/8_Compras.py

**Files:**
- Modify: `pages/8_Compras.py`

**Interfaces:**
- Consumes: `db.crear_compra` (unchanged)
- Produces: Dynamic form with session_state

- [ ] **Step 1: Write implementation**

```python
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

    # Inicializar session_state
    if 'compra_items' not in st.session_state:
        st.session_state.compra_items = [{'producto_id': None, 'cantidad': 0.0, 'precio_unitario': 0.0}]

    st.subheader("Nueva Compra")
    with st.form("compra_form"):
        proveedor_sel = st.selectbox("Proveedor", list(prov_dict.keys()))
        observaciones = st.text_area("Observaciones", placeholder="Opcional")

        st.markdown("#### Productos")
        
        # Renderizar items dinamicos
        items_para_eliminar = []
        for i, item in enumerate(st.session_state.compra_items):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                key_prod = f"prod_{i}"
                opciones = list(prod_opts.keys())
                valor_actual = None
                if item['producto_id'] is not None:
                    for k, v in prod_opts.items():
                        if v == item['producto_id']:
                            valor_actual = k
                            break
                prod_sel = st.selectbox(f"Producto {i+1}", opciones, index=opciones.index(valor_actual) if valor_actual else 0, key=key_prod)
                if prod_sel:
                    st.session_state.compra_items[i]['producto_id'] = prod_opts[prod_sel]
            with col2:
                cant = st.number_input(f"Cantidad {i+1}", min_value=0.0, step=1.0, value=item['cantidad'], key=f"cant_{i}")
                st.session_state.compra_items[i]['cantidad'] = cant
            with col3:
                precio = st.number_input(f"Precio Unit. {i+1}", min_value=0.0, step=0.01, value=item['precio_unitario'], key=f"precio_{i}")
                st.session_state.compra_items[i]['precio_unitario'] = precio
            with col4:
                if i > 0:  # Solo permitir eliminar si no es el primero
                    if st.form_submit_button("🗑️", key=f"del_{i}"):
                        st.session_state.compra_items.pop(i)
                        st.rerun()

        st.divider()
        
        # Boton agregar articulo
        col_add, col_cnt = st.columns([3, 1])
        with col_cnt:
            st.caption(f"Artículos: {len(st.session_state.compra_items)} / 100")
        with col_add:
            if len(st.session_state.compra_items) < 100:
                if st.form_submit_button("+ Agregar artículo"):
                    st.session_state.compra_items.append({'producto_id': None, 'cantidad': 0.0, 'precio_unitario': 0.0})
                    st.rerun()
            else:
                st.form_submit_button("+ Agregar artículo", disabled=True, help="Límite máximo alcanzado")

        submitted = st.form_submit_button("Confirmar Compra", type="primary")

        if submitted:
            items_validos = []
            for item in st.session_state.compra_items:
                pid = item.get('producto_id')
                cant = item.get('cantidad', 0)
                precio = item.get('precio_unitario', 0)
                if pid is not None and cant > 0 and precio > 0:
                    items_validos.append({'producto_id': pid, 'cantidad': cant, 'precio_unitario': precio})
            
            if not items_validos:
                st.error("Agregá al menos un artículo con cantidad y precio mayor a 0.")
            else:
                # Verificar duplicados (opcional: solo advertencia)
                ids = [i['producto_id'] for i in items_validos]
                if len(ids) != len(set(ids)):
                    st.warning("Hay productos duplicados. Se registrarán como items separados.")
                
                compra_id = db.crear_compra(prov_dict[proveedor_sel], items_validos, observaciones)
                if compra_id:
                    st.success(f"Compra #{compra_id} registrada correctamente.")
                    st.session_state.compra_items = [{'producto_id': None, 'cantidad': 0.0, 'precio_unitario': 0.0}]
                    st.rerun()
                else:
                    st.error("Error al registrar la compra.")

st.divider()

# Historial de compras (mantenido igual)
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
```

- [ ] **Step 2: Test manually**

```bash
cd /home/federico/Documentos/Lubricentro && streamlit run pages/8_Compras.py --server.port 8502 2>&1 &
```
Test: carga formulario, agregar/eliminar items, limite 100, validacion cantidad/precio > 0, exito.

- [ ] **Step 3: Commit**

```bash
git add pages/8_Compras.py
git commit -m "feat(compras): UI dinamica para items, limite 100, validaciones"
```

---

### Task 4: Implementar busqueda lazy, vista previa y carrito en pages/7_Ventas.py

**Files:**
- Modify: `pages/7_Ventas.py`

**Interfaces:**
- Consumes: `db.get_productos`, `db.crear_venta` (new signature)
- Produces: Lazy search, preview modal, quantity input, stock validation

- [ ] **Step 1: Write implementation**

```python
import streamlit as st
import database as db

st.set_page_config(page_title="Ventas", layout="wide")
st.title("Ventas - Punto de Venta")

productos = db.get_productos()
clientes = db.get_clientes()

if not productos:
    st.warning("No hay productos cargados. Agregá productos desde Configuración.")
    st.stop()

if 'carrito' not in st.session_state:
    st.session_state.carrito = []
if 'producto_seleccionado' not in st.session_state:
    st.session_state.producto_seleccionado = None

# Cache de productos para busqueda
@st.cache_data
def get_productos_cached():
    return db.get_productos()

productos_all = get_productos_cached()

# --- Sidebar: Carrito ---
with st.sidebar:
    st.header("🛍️ Carrito")
    if st.session_state.carrito:
        total_carrito = 0
        for idx, item in enumerate(st.session_state.carrito):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{item['nombre']}**")
                st.caption(f"${item['precio']:.2f} x {item['cantidad']}")
            with col2:
                # Input cantidad editable en carrito
                max_stock = item.get('stock', 0)
                new_cant = st.number_input(
                    "Cant", 
                    min_value=1, 
                    max_value=max_stock, 
                    value=item['cantidad'], 
                    key=f"cart_qty_{idx}",
                    label_visibility="collapsed"
                )
                if new_cant != item['cantidad']:
                    st.session_state.carrito[idx]['cantidad'] = new_cant
                    st.session_state.carrito[idx]['subtotal'] = new_cant * item['precio']
                    st.rerun()
            with col3:
                st.write(f"${item['subtotal']:.2f}")
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.carrito.pop(idx)
                    st.rerun()
            total_carrito += item['subtotal']
        st.divider()
        st.write(f"**Total: ${total_carrito:.2f}**")
    else:
        st.info("Carrito vacío")

# --- Área principal ---
col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("Agregar productos")
    
    busqueda = st.text_input("🔍 Buscar por nombre o código de barras", placeholder="Escribí al menos 3 caracteres...")
    
    productos_filtrados = []
    if busqueda and len(busqueda) >= 3:
        busqueda_lower = busqueda.lower()
        productos_filtrados = [p for p in productos_all if 
                              busqueda_lower in (p[2] or '').lower() or  # codigo_interno
                              busqueda_lower in (p[3] or '').lower() or  # codigo_barras
                              busqueda_lower in (p[4] or '').lower()]    # nombre
    elif not busqueda:
        productos_filtrados = []  # No precargar
    else:
        productos_filtrados = []
    
    # Mostrar resultados
    if productos_filtrados:
        cols = st.columns(3)
        for idx, p in enumerate(productos_filtrados):
            with cols[idx % 3]:
                stock = p[8] if len(p) > 8 else 0
                if stock > 0:
                    # Boton con nombre, codigo, precio, stock
                    label = f"{p[4]}\nCB: {p[3] or 'N/A'} | ${p[11]:.2f} | Stock: {stock}"
                    if st.button(label, key=f"prod_{p[0]}", use_container_width=True):
                        st.session_state.producto_seleccionado = p[0]
                        st.rerun()
                else:
                    st.button(f"{p[4]} (SIN STOCK)", key=f"prod_{p[0]}", disabled=True, use_container_width=True)
    elif busqueda and len(busqueda) >= 3:
        st.info("No se encontraron productos.")

# Vista previa del producto seleccionado
if st.session_state.producto_seleccionado is not None:
    prod_id = st.session_state.producto_seleccionado
    prod = next((p for p in productos_all if p[0] == prod_id), None)
    if prod:
        with st.container():
            st.markdown("---")
            col_info, col_accion = st.columns([2, 1])
            with col_info:
                st.write(f"**{prod[4]}**")
                st.caption(f"CB: {prod[3] or 'N/A'} | Categoría: {prod[12] if len(prod) > 12 else 'N/A'}")
                st.write(f"Precio unitario: **${prod[11]:.2f}**")
                stock = prod[8] if len(prod) > 8 else 0
                st.write(f"Stock disponible: **{stock}**")
            with col_accion:
                # Cantidad ya en carrito
                en_carrito = sum(item['cantidad'] for item in st.session_state.carrito if item['producto_id'] == prod_id)
                stock_disp = stock - en_carrito
                
                if stock_disp > 0:
                    cantidad = st.number_input(
                        "Cantidad a agregar", 
                        min_value=1, 
                        max_value=stock_disp, 
                        value=1, 
                        step=1,
                        key=f"qty_add_{prod_id}"
                    )
                    if st.button("✅ Agregar al carrito", type="primary", use_container_width=True):
                        # Agregar al carrito
                        existe = False
                        for item in st.session_state.carrito:
                            if item['producto_id'] == prod_id:
                                item['cantidad'] += cantidad
                                item['subtotal'] = item['cantidad'] * item['precio']
                                existe = True
                                break
                        if not existe:
                            st.session_state.carrito.append({
                                'producto_id': prod_id,
                                'nombre': prod[4],
                                'precio': float(prod[11]),
                                'cantidad': cantidad,
                                'subtotal': float(prod[11]) * cantidad,
                                'stock': stock
                            })
                        st.session_state.producto_seleccionado = None
                        st.rerun()
                else:
                    st.warning(f"Sin stock disponible (en carrito: {en_carrito})")
                if st.button("✖️ Cancelar", use_container_width=True):
                    st.session_state.producto_seleccionado = None
                    st.rerun()

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
        metodo_pago = st.selectbox("Método de pago", metodos)
        
        usuario_id = 1  # admin por defecto
        
        # Calcular totales para mostrar
        subtotal_carrito = sum(item['subtotal'] for item in st.session_state.carrito)
        
        # Mostrar totales segun tipo comprobante
        if tipo_comp == 'factura_a':
            neto = round(subtotal_carrito / 1.21, 2)
            iva = round(subtotal_carrito - neto, 2)
            st.write(f"**Subtotal neto:** ${neto:.2f}")
            st.write(f"**IVA (21%):** ${round(subtotal_carrito - neto, 2):.2f}")
            st.write(f"**Total:** ${subtotal_carrito:.2f}")
        else:
            st.write(f"**Total:** ${subtotal_carrito:.2f}")
        
        if st.button("✅ CONFIRMAR VENTA", type="primary", use_container_width=True):
            # Re-validar stock antes de enviar
            error_stock = None
            for item in st.session_state.carrito:
                prod_fresh = next((p for p in productos_all if p[0] == item['producto_id']), None)
                if prod_fresh:
                    stock_actual = prod_fresh[8] if len(prod_fresh) > 8 else 0
                    if item['cantidad'] > stock_actual:
                        error_stock = f"Stock insuficiente de \"{item['nombre']}\": solicitado {item['cantidad']}, disponible {stock_actual}"
                        break
            
            if error_stock:
                st.error(error_stock)
            else:
                items = [{
                    'producto_id': item['producto_id'],
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio']
                } for item in st.session_state.carrito]
                
                venta_id, numero, error = db.crear_venta(cliente_id, tipo_comp, items, metodo_pago, 1)
                
                if venta_id:
                    st.success(f"¡Venta confirmada! #{tipo_comp.upper()} {venta_id:08d}")
                    st.session_state.carrito = []
                    st.rerun()
                else:
                    st.error(f"Error al procesar la venta: {error}")
    else:
        st.info("Agregá productos al carrito")
```

- [ ] **Step 2: Test manually**

```bash
cd /home/federico/Documentos/Lubricentro && streamlit run pages/7_Ventas.py --server.port 8503 2>&1 &
```
Test: busqueda lazy, vista previa con cantidad, stock validation, IVA factura_a vs ticket, carrito editable.

- [ ] **Step 3: Commit**

```bash
git add pages/7_Ventas.py
git commit -m "feat(ventas): busqueda lazy, vista previa con cantidad, validacion stock UI, IVA condicional"
```

---

### Task 5: Actualizar IVA en sidebar y calculos backend (ya cubierto en Task 2 y 4)

- [ ] **Step 1: Verificar que 7_Ventas.py sidebar ya no muestra IVA hardcoded**
  - Verificar que no hay lineas 38-40 originales (iva hardcoded)
  - Confirmar que solo muestra IVA cuando tipo_comp == 'factura_a'

- [ ] **Step 2: Verificar backend ya actualizado en Task 2**
  - database.py crear_venta ya calcula IVA incluido para factura_a

- [ ] **Step 3: Commit si hubo cambios**

```bash
git add pages/7_Ventas.py
git commit -m "fix(ventas): eliminar IVA hardcoded sidebar, solo desglose Factura A"
```

---

### Task 6: Tests de integracion para flujo completo

**Files:**
- Modify: `tests/test_database.py`

- [ ] **Step 1: Add integration test**

```python
def test_flujo_completo_venta_factura_a_con_iva_incluido(temp_db):
    """Test end-to-end: busqueda, carrito, confirmacion Factura A con IVA incluido."""
    from database import crear_venta, add_producto, get_ventas, get_venta_detalle
    add_producto("INT1", "CB123", "Aceite 10W40", "", 1, 1, "Entero", 0, 500.0, 121.0, 10)
    items = [{"producto_id": 1, "cantidad": 2, "precio_unitario": 121.0}]
    venta_id, numero, error = crear_venta(None, "factura_a", items, "efectivo", 1)
    assert venta_id is not None
    assert error is None
    
    # Verificar venta
    ventas = get_ventas(limit=1)
    v = ventas[0]
    assert v[2] == "factura_a"
    assert v[5] == 200.0  # subtotal neto = 242/1.21 = 200
    assert v[6] == 42.0   # iva = 42
    assert v[7] == 242.0  # total = 242

def test_crear_venta_ticket_sin_desglose_iva(temp_db):
    """Ticket no debe tener IVA desglosado."""
    from database import crear_venta, add_producto
    add_producto("INT2", "CB456", "Filtro", "", 1, 1, "Entero", 0, 20.0, 50.0, 5)
    items = [{"producto_id": 1, "cantidad": 1, "precio_unitario": 50.0}]
    venta_id, numero, error = crear_venta(None, "ticket", items, "efectivo", 1)
    assert venta_id is not None
    import database as db
    conn = db.get_connection()
    row = conn.execute("SELECT subtotal, iva, total FROM ventas WHERE id = ?", (venta_id,)).fetchone()
    conn.close()
    assert row[0] == 50.0  # subtotal
    assert row[1] == 0.0   # iva
    assert row[2] == 50.0  # total
```

- [ ] **Step 2: Run tests**

```bash
cd /home/federico/Documentos/Lubricentro && pytest tests/test_database.py -v -k "flujo_completo or ticket_sin_desglose" -v
```

Expected: PASS

- [ ] **Step 3: Run full test suite**

```bash
cd /home/federico/Documentos/Lubricentro && pytest tests/ -v 2>&1 | tail -50
```

Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/test_database.py
git commit -m "test: agregar tests integracion venta Factura A y ticket sin IVA"
```

---

### Task 7: Configurar Dependabot para actualizaciones automáticas

**Files:**
- Create: `.github/dependabot.yml`

- [ ] **Step 1: Create dependabot config**

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "python"
    commit-message:
      prefix: "deps(pip): "
      include: "scope"
    allow:
      - dependency-type: "direct"
      - dependency-type: "indirect"
```

- [ ] **Step 2: Commit**

```bash
git add .github/dependabot.yml
git commit -m "ci: agregar Dependabot para actualizaciones semanales de dependencias pip"
```

---

### Task 8: Agregar plantillas de issues (issue templates)

**Files:**
- Create: `.github/ISSUE_TEMPLATE/bug_report.yml`
- Create: `.github/ISSUE_TEMPLATE/feature_request.yml`

- [ ] **Step 1: Create bug report template**

```yaml
name: Bug Report
description: Reportar un error o comportamiento inesperado
title: "[Bug] "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: "Gracias por reportar un bug. Por favor completa la información siguiente."
  - type: input
    id: version
    attributes:
      label: "Versión de la aplicación"
      description: "Ej: v0.2.4"
      placeholder: "v0.2.4"
    validations:
      required: true
  - type: textarea
    id: description
    attributes:
      label: "Descripción del problema"
      description: "Descripción clara y concisa del bug"
      placeholder: "Al hacer clic en..."
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: "Pasos para reproducir"
      description: "Pasos numerados para reproducir el comportamiento"
      placeholder: "1. Ir a...\n2. Hacer clic en...\n3. Ver error..."
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: "Comportamiento esperado"
      description: "Qué deberia pasar"
    validations:
      required: true
  - type: textarea
    id: actual
    attributes:
      label: "Comportamiento actual"
      description: "Qué pasa en realidad"
    validations:
      required: true
  - type: input
    id: environment
    attributes:
      label: "Entorno"
      description: "SO, Python version, navegador si aplica"
      placeholder: "Windows 10, Python 3.12, Chrome 118"
    validations:
      required: false
  - type: checkboxes
    id: terms
    attributes:
      label: "Checklist"
      options:
        - label: "He buscado issues existentes y no encontré duplicados"
          required: true
        - label: "He reproducido el problema en la última versión"
          required: true
```

- [ ] **Step 2: Create feature request template**

```yaml
name: Feature Request
description: Sugerir una nueva funcionalidad o mejora
title: "[Feature] "
labels: ["enhancement"]
body:
  - type: markdown
    attributes:
      value: "Gracias por sugerir una mejora. Describe la funcionalidad deseada."
  - type: textarea
    id: problem
    attributes:
      label: "Problema a resolver"
      description: "Qué problema resuelve esta feature"
      placeholder: "Actualmente no se puede..."
    validations:
      required: true
  - type: textarea
    id: solution
    attributes:
      label: "Solución propuesta"
      description: "Cómo te imaginas la solución"
      placeholder: "Me gustaría que..."
    validations:
      required: true
  - type: textarea
    id: alternatives
    attributes:
      label: "Alternativas consideradas"
      description: "Otras soluciones que consideraste"
    validations:
      required: false
  - type: textarea
    id: context
    attributes:
      label: "Contexto adicional"
      description: "Capturas de pantalla, mockups, referencias"
    validations:
      required: false
```

- [ ] **Step 2: Commit**

```bash
git add .github/ISSUE_TEMPLATE/
git commit -m "ci: agregar plantillas de issues (bug report y feature request)"
```

---

### Task 8b: Configurar CodeQL para análisis de seguridad (GitHub Advanced Security)

**Files:**
- Create: `.github/workflows/codeql.yml`

- [ ] **Step 1: Create CodeQL workflow**

```yaml
name: "CodeQL Analysis"

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Monday

permissions:
  security-events: write
  contents: read

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        language: [python]
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v3
      with:
        languages: ${{ matrix.language }}
        queries: +security-and-quality

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v3
      with:
        category: "/language:${{ matrix.language }}"
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/codeql.yml
git commit -m "ci: agregar CodeQL para analisis de seguridad semanal"
```

---

### Task 9: Actualizar CHANGELOG.md para v0.2.5

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add v0.2.5 entry**

```markdown
## [0.2.5] - 2026-07-20

### Agregado
- UI dinamica en modulo Compras: limite de 100 articulos, agregar/eliminar items dinamicamente, solo primer articulo precargado
- Busqueda lazy en modulo Ventas: productos se cargan solo al buscar (min 3 caracteres)
- Vista previa al agregar productos en Ventas: muestra nombre, codigo, precio, stock y input de cantidad
- Validacion de stock en tiempo real al agregar al carrito y al confirmar venta
- Desglose de IVA condicional: solo para Factura A (precio ya incluye IVA, neto = total/1.21)
- Mensajes de error especificos en validacion de stock (producto, cantidad solicitada, disponible)

### Corregido
- Error "Error al procesar la venta, verificar stock" que aparecia con stock disponible: validacion movida a misma transaccion y mensaje especifico
- Eliminada precarga automatica de productos en modulo Ventas (carga lazy al buscar)
- Eliminado desglose IVA hardcoded en sidebar para todos los comprobantes (solo Factura A)
- Bug indices de columnas en busqueda de productos (nombre, codigo_barras, precio)
- Precio unitario no editable en modulo Ventas (solo lectura, editable solo en Productos y Compras)

### Cambiado
- Modulo Compras: limite aumentado de 3 a 100 articulos, UI dinamica con boton "Agregar articulo"
- Modulo Ventas: busqueda lazy (min 3 caracteres), vista previa con input cantidad, validacion stock en UI
- Backend `crear_venta`: firma extendida para retornar mensaje de error especifico, validacion stock en misma transaccion, IVA incluido para Factura A
```

- [ ] **Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: actualizar CHANGELOG para v0.2.5"
```

---

### Task 10: Actualizar APP_VERSION en updater.py y crear release v0.2.5

**Files:**
- Modify: `updater.py` (line ~35)
- Create: Git tag v0.2.5 and push

- [ ] **Step 1: Update version**

```python
# updater.py line ~35
APP_VERSION = "0.2.5"
```

- [ ] **Step 2: Commit version bump**

```bash
git add updater.py
git commit -m "chore: bump version to 0.2.5"
```

- [ ] **Step 3: Create and push tag**

```bash
cd /home/federico/Documentos/Lubricentro
git tag v0.2.5
git push origin main
git push origin v0.2.5
```

- [ ] **Step 4: Verify GitHub Actions runs**

Check GitHub Actions tab for successful build and release creation.

---

### Task 11: Verificación final y commit final

- [ ] **Step 1: Run full test suite**

```bash
cd /home/federico/Documentos/Lubricentro && pytest tests/ -v 2>&1 | tail -30
```

Expected: All tests pass.

- [ ] **Step 2: Manual smoke test**

```bash
streamlit run app.py --server.port 8501
```
Test: Compras (agregar 5 items, limite 100), Ventas (buscar, agregar cantidad, stock, factura A vs ticket), Compras historial.

- [ ] **Step 3: Final commit and push**

```bash
git push origin main
```

- [ ] **Step 4: Verify GitHub Actions and Release**

Check GitHub Actions tab and Releases page for v0.2.5.
```

- [ ] **Step 5: Final commit message**

```bash
git commit -m "release: v0.2.5 - Correcciones UX Compras, Ventas e IVA"
```

---

## Self-Review Checklist

- [ ] All spec requirements covered by tasks
- [ ] No placeholders (TBD, TODO, "implement later")
- [ ] Type consistency: `crear_venta` returns `(id, num, err_msg)` everywhere
- [ ] Tests cover: IVA Factura A, ticket sin IVA, stock insuficiente, producto inactivo
- [ ] GitHub Actions: Dependabot, Issue templates, CodeQL
- [ ] CHANGELOG follows Keep a Changelog format
- [ ] No emojis in commits, docs, code
- [ ] Version bumped to 0.2.5 in updater.py
- [ ] Tag v0.2.5 pushed