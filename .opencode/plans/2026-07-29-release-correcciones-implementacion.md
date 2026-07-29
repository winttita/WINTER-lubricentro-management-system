# Release v0.5.0 - Correcciones y mejoras - Plan de Implementacion

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corregir 7 bugs reportados e implementar aumento de precios por proveedor.

**Architecture:** Correcciones localizadas en UI (Streamlit) + DB (SQLite). Se mueven selectores fuera de formularios para autocompletado inmediato. Se elimina columna codigo_interno con migracion de indices.

**Tech Stack:** Python 3, Streamlit, SQLite, win32print (Windows), lp (Linux)

## Global Constraints

- No agregar funcionalidades no solicitadas (YAGNI)
- Mantener compatibilidad con tests existentes
- Seguir CONVENTIONS.md: emojis prohibidos, conventional commits en espanol
- Actualizar APP_VERSION en updater.py al final
- No modificar logica de negocio de crear_venta/crear_compra

---

### Task 1: B04 - Corregir precio_venta en Ventas

**Files:**
- Modify: `pages/7_Ventas.py:100`

**Interfaces:**
- Consumes: prod_lookup[id] devuelve tupla con p[10]=precio_costo, p[11]=precio_venta
- Produces: item['precio'] toma precio_venta correcto

- [ ] **Step 1: Corregir indice de precio**

Cambiar en `pages/7_Ventas.py:100`:
```python
# Antes:
item['precio'] = float(p[10])
# Despues:
item['precio'] = float(p[11])
```

- [ ] **Step 2: Commit**

```bash
git add pages/7_Ventas.py
git commit -m "fix: corrige indice de precio_venta en ventas (p[10] a p[11])"
```

---

### Task 2: B06 - Migrar BD: eliminar columna codigo_interno

**Files:**
- Modify: `database.py:130-152` (CREATE TABLE), `database.py:873-895` (add_producto), `database.py:1144-1180` (update_producto), `database.py:1115-1141` (get_precios_para_lista)

**Interfaces:**
- Consumes: DB schema con columna codigo_interno
- Produces: DB schema sin columna codigo_interno; add_producto sin parametro codigo_interno; update_producto sin parametro codigo_interno

- [ ] **Step 1: Agregar migracion a init_db**

En `database.py`, despues de la creacion de tablas en `init_db()`, agregar migracion para eliminar columna:

```python
# Migracion: eliminar codigo_interno de productos (v0.5.0)
try:
    cursor.execute("ALTER TABLE productos DROP COLUMN codigo_interno")
except sqlite3.OperationalError:
    pass  # Ya migrado
```

- [ ] **Step 2: Actualizar add_producto - quitar parametro codigo_interno**

```python
def add_producto(codigo_barras, nombre, descripcion, categoria_id, proveedor_id, tipo_unidad, stock_minimo, precio_costo, precio_venta, stock_inicial=0):
    if not nombre or not nombre.strip():
        return False
    ...
    cursor = conn.execute("""
        INSERT INTO productos (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, tipo_unidad, stock_minimo, precio_costo, precio_venta, stock_actual)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        codigo_barras.strip() if codigo_barras else None,
        nombre.strip(),
        descripcion, categoria_id, proveedor_id, tipo_unidad,
        stock_minimo, precio_costo, precio_venta, stock_inicial
    ))
```

- [ ] **Step 3: Actualizar update_producto - quitar parametro codigo_interno**

```python
def update_producto(id, codigo_barras, nombre, descripcion, categoria_id, proveedor_id, tipo_unidad, stock_minimo, precio_costo, precio_venta):
    ...
    cursor = conn.execute("""
        UPDATE productos
        SET codigo_barras = ?, nombre = ?, descripcion = ?,
            categoria_id = ?, proveedor_id = ?, tipo_unidad = ?,
            stock_minimo = ?, precio_costo = ?, precio_venta = ?
        WHERE id = ?
    """, (
        codigo_barras.strip() if codigo_barras else None,
        nombre.strip(),
        descripcion, categoria_id, proveedor_id, tipo_unidad,
        max(0.0, stock_minimo), max(0.0, precio_costo), max(0.0, precio_venta),
        id
    ))
```

- [ ] **Step 4: Actualizar get_precios_para_lista - quitar codigo_interno**

```python
def get_precios_para_lista():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT prov.nombre as proveedor_nombre,
                   p.nombre as producto_nombre,
                   p.codigo_barras,
                   p.precio_venta,
                   p.stock_actual,
                   c.nombre as categoria_nombre
            FROM productos p
            LEFT JOIN proveedores prov ON p.proveedor_id = prov.id
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.activo = 1 AND p.stock_actual > 0
            ORDER BY prov.nombre, p.nombre
        """).fetchall()
        return rows
    finally:
        conn.close()
```

- [ ] **Step 5: Actualizar tests - quitar codigo_interno de llamadas a add_producto**

En `tests/test_database.py`, todas las ~60 llamadas a `database.add_producto("CODIGO", ...)` deben pasar sin el primer argumento.
```python
# Antes:
database.add_producto("C001", "7790001", "Aceite 5W30", "Sintetico", cat_id, prov_id, "Entero", 10, 1000, 1500)
# Despues:
database.add_producto("7790001", "Aceite 5W30", "Sintetico", cat_id, prov_id, "Entero", 10, 1000, 1500)
```

Tambien actualizar referencias SQL directas a codigo_interno (lineas 184, 219):
```python
# Antes:
conn.execute("UPDATE productos SET activo=0 WHERE codigo_interno='C100'")
conn.execute("UPDATE productos SET stock_actual = 20 WHERE codigo_interno = 'C001'")
# Despues:
conn.execute("UPDATE productos SET activo=0 WHERE id=1")
conn.execute("UPDATE productos SET stock_actual = 20 WHERE id=1")
```

Actualizar helper `_crear_producto_con_stock`:

```python
def _crear_producto_con_stock():
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "123", "Contado")
    cat_id = database.get_categorias()[0][0]
    prov_id = database.get_proveedores()[0][0]
    database.add_producto(
        "7790001", "Aceite 5W30", "Sintetico", cat_id, prov_id,
        "Entero", 10, 1000, 1500
    )
    conn = database.get_connection()
    conn.execute("UPDATE productos SET stock_actual = 20 WHERE id = 1")
    conn.commit()
    conn.close()
    return cat_id, prov_id
```

- [ ] **Step 6: Commit**

```bash
git add database.py tests/test_database.py
git commit -m "feat: elimina columna codigo_interno de productos (B06)"
```

---

### Task 3: B06 - Actualizar indices en UI y tests

**Files:**
- Modify: `pages/3_Productos.py`, `pages/7_Ventas.py`, `pages/1_Stock.py`, `pages/8_Compras.py`, `pages/10_ListaPrecios.py`, `pages/4_Ordenes.py`, `tests/test_database.py`

**Context:** Al eliminar `codigo_interno` (era p[1]), todos los indices se desplazan: codigo_barras pasa de p[2] a p[1], nombre de p[3] a p[2], etc.

**Tabla de migracion de indices:**

| Dato | Indice viejo | Indice nuevo |
|------|-------------|-------------|
| codigo_barras | p[2] | p[1] |
| nombre | p[3] | p[2] |
| descripcion | p[4] | p[3] |
| categoria_id | p[5] | p[4] |
| proveedor_id | p[6] | p[5] |
| tipo_unidad | p[7] | p[6] |
| stock_actual | p[8] | p[7] |
| stock_minimo | p[9] | p[8] |
| precio_costo | p[10] | p[9] |
| precio_venta | p[11] | p[10] |
| activo | p[12] | p[11] |
| categoria_nombre | p[13] | p[12] |
| proveedor_nombre | p[14] | p[13] |

- [ ] **Step 1: pages/3_Productos.py - eliminar referencias a codigo_interno**

Linea 83: eliminar `codigo_interno = st.text_input("Codigo Interno")`
Linea 108: cambiar `db.add_producto(codigo_interno, codigo_barras, ...)` a `db.add_producto(codigo_barras, ...)`
Linea 124: cambiar `f"[{p[1]}] {p[3]}"` a `f"{p[2]}"` (solo nombre)
Linea 128: eliminar `new_cod_int = st.text_input("Codigo Interno", value=p[1] or "", key=f"ci_{pid}")`

- [ ] **Step 2: pages/7_Ventas.py - actualizar indices**

Linea 32: cambiar `f"[{p[1]}] {p[3]}"` a `f"{p[2]}"` en prod_opts (solo nombre)
Verificar otros p[x] con la tabla de migracion

- [ ] **Step 3: pages/1_Stock.py - actualizar indices**

Linea 85: cambiar `f"[{p[1]}] {p[3]}"` a `f"{p[2]}"`
Linea 104: cambiar `f"[{p[1]}] {p[3]}"` a `f"{p[2]}"`
Linea 160: cambiar `f"[{p[1]}] {p[3]}"` a `f"{p[2]}"`

- [ ] **Step 4: pages/8_Compras.py - actualizar indices**

Linea 25: cambiar `f"[{p[1]}] {p[3]}"` a `f"{p[2]}"`

- [ ] **Step 5: pages/10_ListaPrecios.py - actualizar indices**

get_precios_para_lista ahora devuelve tupla sin codigo_interno.
Linea 75: p[2] (era codigo_barras, ahora es nombre) 
Linea 76: p[1] (era nombre) - ajustar indices

- [ ] **Step 6: pages/4_Ordenes.py - actualizar indices**

Linea 126: cambiar `f"[{p[1]}] {p[3]}"` a `f"{p[2]}"`

- [ ] **Step 7: tests/test_database.py - actualizar indices**

Linea 813-815: el comentario menciona "id, codigo_interno, codigo_barras, nombre..."
Actualizar comentario e indice: `prod[10]` (precio_costo) pasa a `prod[9]`

- [ ] **Step 8: Ejecutar tests para verificar**

```bash
pytest tests/test_database.py -v 2>&1 | head -80
```

- [ ] **Step 9: Commit**

```bash
git add pages/3_Productos.py pages/7_Ventas.py pages/1_Stock.py pages/8_Compras.py pages/10_ListaPrecios.py pages/4_Ordenes.py tests/test_database.py
git commit -m "fix: actualiza indices de columnas tras eliminar codigo_interno (B06)"
```

---

### Task 4: B05 - Cambiar selectbox a select_slider en Reportes

**Files:**
- Modify: `pages/9_Reportes.py:17`

- [ ] **Step 1: Cambiar selectbox a select_slider**

```python
# Antes:
periodo = st.sidebar.selectbox("Periodo", ["Hoy", "Ultimos 7 dias", "Ultimos 30 dias", "Este mes", "Todo"])
# Despues:
periodo = st.sidebar.select_slider("Periodo", options=["Hoy", "Ultimos 7 dias", "Ultimos 30 dias", "Este mes", "Todo"], value="Hoy")
```

- [ ] **Step 2: Commit**

```bash
git add pages/9_Reportes.py
git commit -m "fix: cambia selector de periodo a select_slider (B05)"
```

---

### Task 5: B07 - Carrito vacio en Compras

**Files:**
- Modify: `pages/8_Compras.py:28-29`

- [ ] **Step 1: Inicializar compra_items vacio**

```python
# Antes:
if 'compra_items' not in st.session_state:
    st.session_state.compra_items = [{'producto': None, 'cantidad': 1.0, 'precio': 0.0}]
# Despues:
if 'compra_items' not in st.session_state:
    st.session_state.compra_items = []
```

- [ ] **Step 2: Commit**

```bash
git add pages/8_Compras.py
git commit -m "fix: inicializa carrito de compras vacio (B07)"
```

---

### Task 6: B02+B03 - Ventas: carrito vacio, scanner, autofill precio

**Files:**
- Modify: `pages/7_Ventas.py:32-177`

**Context:** Este es el cambio mas grande. Se reestructura la seccion de productos de Ventas para:
1. Inicializar carrito vacio
2. Agregar campo de codigo de barras fuera del form
3. Mover selector de producto fuera del form (para autofill inmediato)
4. Mostrar precio/stock al seleccionar producto

- [ ] **Step 1: Inicializar carrito vacio**

Linea 36-37:
```python
# Antes:
if 'venta_items' not in st.session_state:
    st.session_state.venta_items = [{'producto': None, 'cantidad': 1.0, 'precio': 0.0}]
# Despues:
if 'venta_items' not in st.session_state:
    st.session_state.venta_items = []
```

- [ ] **Step 2: Agregar campo de codigo de barras fuera del form**

Despues de la linea 83 (metodo_pago), antes del form:

```python
st.markdown("#### Productos")

# Busqueda por codigo de barras
codigo_barras_input = st.text_input(
    "Codigo de barras",
    placeholder="Escanee o escriba el codigo de barras",
    key="barcode_input"
)
producto_encontrado = None
if codigo_barras_input:
    for p in productos_activos:
        if p[1] and str(p[1]).strip() == codigo_barras_input.strip():
            producto_encontrado = p
            break
    if producto_encontrado:
        st.success(f"Producto: {producto_encontrado[2]} - Stock: {producto_encontrado[7]} - Precio: ${producto_encontrado[10]:.2f}")
    else:
        st.warning("Producto no encontrado con ese codigo de barras.")
```

- [ ] **Step 3: Reestructurar form de venta - solo items del carrito**

El formulario solo contendra los items ya agregados al carrito y los botones de accion. El selector de producto para agregar nuevos items esta fuera del form:

```python
# Fuera del form: selector de producto + cantidad + boton agregar
col_prod, col_cant, col_add = st.columns([3, 1, 1])
with col_prod:
    prod_opts = {p[2]: p for p in productos_activos}
    prod_sel = st.selectbox(
        "Seleccionar producto",
        [""] + list(prod_opts.keys()),
        key="venta_prod_sel"
    )
with col_cant:
    cant_agregar = st.number_input("Cantidad", min_value=0.0, step=1.0, value=1.0, key="venta_cant_agregar")
with col_add:
    st.write("")
    if st.button("Agregar al carrito", use_container_width=True):
        if prod_sel and cant_agregar > 0:
            p = prod_opts[prod_sel]
            st.session_state.venta_items.append({
                'producto_id': p[0],
                'nombre': p[2],
                'cantidad': float(cant_agregar),
                'precio': float(p[10]),
                'stock': float(p[7])
            })
            st.rerun()

# Mostrar precio del producto seleccionado (autofill inmediato)
if prod_sel:
    p = prod_opts[prod_sel]
    st.info(f"Precio: ${float(p[10]):.2f} | Stock disponible: {float(p[7]):.0f}")
```

- [ ] **Step 4: Formulario con items del carrito + confirmar venta**

```python
st.markdown("#### Carrito")
with st.form("venta_form"):
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

        col_submit = st.columns([1])
        with col_submit[0]:
            submitted = st.form_submit_button("Confirmar Venta", type="primary", use_container_width=True)
```

- [ ] **Step 5: Ajustar logica de confirmacion**

```python
if submitted:
    items = []
    error_fraccion = False
    for item in st.session_state.venta_items:
        if item['cantidad'] > 0 and item['precio'] > 0:
            tipo_unidad = prod_lookup[item['producto_id']][6]  # tipo_unidad nuevo indice
            ...
```

- [ ] **Step 6: Commit**

```bash
git add pages/7_Ventas.py
git commit -m "fix: reestructura ventas - carrito vacio, scanner, autofill precio (B02 B03)"
```

---

### Task 7: Stock - Ajustes con stock inmediato

**Files:**
- Modify: `pages/1_Stock.py:150-190`

- [ ] **Step 1: Mover selector de producto fuera del formulario de ajustes**

En la pestana de Ajustes:

```python
with tab_adj:
    st.subheader("Ajustes de Stock")
    ...
    prod_opts_adj = {p[2]: p for p in productos}  # nombre -> producto tuple

    # Selector fuera del form
    prod_nombre_sel = st.selectbox("Producto", [""] + list(prod_opts_adj.keys()), key="adj_prod")
    prod_info = prod_opts_adj.get(prod_nombre_sel)
    if prod_info:
        stock_actual = float(prod_info[7])
        st.info(f"Stock actual: {stock_actual}")
    else:
        stock_actual = 0.0
```

- [ ] **Step 2: Formulario dentro con solo los campos de accion**

```python
    with st.form("ajuste_form"):
        stock_nuevo = st.number_input("Nuevo stock", min_value=0.0, value=stock_actual, step=1.0, key="adj_nuevo")
        motivo = st.text_area("Motivo *", placeholder="Ej: Rotura, merma...", height=100, key="adj_motivo")
        submitted = st.form_submit_button("Aplicar Ajuste", type="primary")
        if submitted:
            if not prod_nombre_sel:
                st.error("Seleccione un producto.")
            elif not motivo.strip():
                st.error("El motivo es obligatorio.")
            else:
                diff = stock_nuevo - stock_actual
                if diff == 0:
                    st.warning("El stock no cambio.")
                else:
                    ok = db.crear_ajuste_stock(prod_info[0], stock_nuevo, motivo.strip(), st.session_state.user_id)
                    if ok:
                        st.success(f"Ajuste aplicado: {stock_actual} -> {stock_nuevo} ({diff:+.2f})")
                        st.rerun()
                    else:
                        st.error("Error al aplicar ajuste.")
```

- [ ] **Step 3: Commit**

```bash
git add pages/1_Stock.py
git commit -m "fix: muestra stock actual al seleccionar producto en ajustes"
```

---

### Task 8: B01 - Correccion impresora y ticket cortado

**Files:**
- Modify: `tickets.py:176` (corte), `pages/7_Ventas.py:180-229` (diagnostico)

- [ ] **Step 1: Aumentar saltos de linea antes del corte en tickets.py**

```python
# Antes (linea 176):
payload += b'\n\n'
# Despues:
payload += b'\n' * 8
```

- [ ] **Step 2: Agregar logging a imprimir_venta en 7_Ventas.py (B01 diagnostico)**

```python
def imprimir_venta(venta_id, tipo_comp, cliente_id):
    import logging
    logging.basicConfig(level=logging.DEBUG, filename='impresora.log')
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
        ...
        result = tk.imprimir_comprobante(texto)
        logging.info(f"imprimir_comprobante resulto: {result}")
        return result
    except Exception as e:
        logging.exception(f"Error en imprimir_venta para venta_id={venta_id}: {e}")
        return False
```

- [ ] **Step 3: Commit**

```bash
git add tickets.py pages/7_Ventas.py
git commit -m "fix: corrige corte de ticket y agrega diagnostico a impresora (B01)"
```

---

### Task 9: F01 - Aumento de precios por proveedor

**Files:**
- Modify: `database.py` (nueva funcion), `pages/1_Stock.py` (nueva pestana)

- [ ] **Step 1: Agregar funcion aumentar_precios_por_lista en database.py**

En `database.py`, despues de `aumentar_precios_por_categoria`:

```python
def aumentar_precios_por_lista(producto_ids, porcentaje):
    """Aumenta precio_venta de productos especificos.

    Args:
        producto_ids: lista de IDs de productos
        porcentaje: porcentaje de aumento (ej: 10.0 = +10%)

    Returns:
        int: cantidad de productos actualizados, o 0 si error
    """
    if not producto_ids:
        return 0
    try:
        porcentaje = float(porcentaje)
    except (ValueError, TypeError):
        return 0
    if porcentaje < 0:
        return 0

    conn = get_connection()
    try:
        placeholders = ','.join('?' * len(producto_ids))
        factor = 1 + (porcentaje / 100.0)
        cursor = conn.execute(
            f"UPDATE productos SET precio_venta = ROUND(precio_venta * ?, 2) "
            f"WHERE id IN ({placeholders}) AND activo = 1",
            (factor, *producto_ids)
        )
        conn.commit()
        return cursor.rowcount
    except Exception:
        conn.rollback()
        return 0
    finally:
        conn.close()
```

- [ ] **Step 2: Agregar funcion get_productos_por_proveedor con busqueda**

En `database.py`:

```python
def get_productos_por_proveedor(proveedor_id, busqueda=None):
    """Devuelve productos activos de un proveedor, opcionalmente filtrados.

    Args:
        proveedor_id: ID del proveedor
        busqueda: texto para filtrar por nombre (opcional)

    Returns:
        lista de tuplas (id, nombre, precio_venta, stock_actual)
    """
    conn = get_connection()
    try:
        query = """
            SELECT id, nombre, precio_venta, stock_actual
            FROM productos
            WHERE proveedor_id = ? AND activo = 1
        """
        params = [proveedor_id]
        if busqueda:
            query += " AND (nombre LIKE ? OR codigo_barras LIKE ?)"
            params.extend([f"%{busqueda}%", f"%{busqueda}%"])
        query += " ORDER BY nombre"
        rows = conn.execute(query, params).fetchall()
        return rows
    finally:
        conn.close()
```

- [ ] **Step 3: Agregar pestana "Aumento de Precios" en 1_Stock.py**

Agregar una cuarta pestana:

```python
tab_stock, tab_mov, tab_adj, tab_precios = st.tabs(["Stock Actual", "Movimientos", "Ajustes", "Aumento de Precios"])
```

- [ ] **Step 4: Implementar UI de la pestana**

```python
with tab_precios:
    st.subheader("Aumento de Precios")
    proveedores = db.get_proveedores()
    prov_dict = {p[1]: p[0] for p in proveedores}
    if not proveedores:
        st.warning("No hay proveedores cargados.")
    else:
        modo = st.radio("Modalidad", ["General", "Parcial"], horizontal=True)
        prov_sel = st.selectbox("Proveedor", list(prov_dict.keys()), key="aum_prov")

        if modo == "General":
            porcentaje = st.number_input("Porcentaje de aumento (%)", min_value=0.0, step=0.5, format="%.1f", key="aum_pct_gen")
            if st.button("Aplicar a todos los productos", type="primary"):
                if porcentaje <= 0:
                    st.error("Ingrese un porcentaje mayor a 0.")
                else:
                    ok = db.aumentar_precios_proveedor(prov_dict[prov_sel], porcentaje)
                    if ok:
                        st.success(f"Aumento del {porcentaje}% aplicado a todos los productos de {prov_sel}.")
                        st.rerun()
                    else:
                        st.error("Error al aplicar aumento.")

        else:  # Parcial
            busqueda = st.text_input("Buscar productos", placeholder="Ej: elaion, aceite, filtro...", key="aum_busqueda")
            productos_prov = db.get_productos_por_proveedor(
                prov_dict[prov_sel],
                busqueda if busqueda else None
            )
            if not productos_prov:
                st.info("No hay productos para este proveedor con ese filtro.")
            else:
                st.write(f"Productos encontrados: {len(productos_prov)}")
                seleccionados = []
                for pid, pnombre, pprecio, pstock in productos_prov:
                    if st.checkbox(f"{pnombre} - ${pprecio:.2f} - Stock: {pstock:.0f}", key=f"aum_chk_{pid}"):
                        seleccionados.append(pid)

                porcentaje = st.number_input("Porcentaje de aumento (%)", min_value=0.0, step=0.5, format="%.1f", key="aum_pct_par")
                if st.button("Aplicar a seleccionados", type="primary"):
                    if not seleccionados:
                        st.error("Seleccione al menos un producto.")
                    elif porcentaje <= 0:
                        st.error("Ingrese un porcentaje mayor a 0.")
                    else:
                        cant = db.aumentar_precios_por_lista(seleccionados, porcentaje)
                        if cant > 0:
                            st.success(f"Aumento del {porcentaje}% aplicado a {cant} producto(s).")
                            st.rerun()
                        else:
                            st.error("Error al aplicar aumento.")
```

- [ ] **Step 5: Commit**

```bash
git add database.py pages/1_Stock.py
git commit -m "feat: agrega aumento de precios por proveedor (F01)"
```

---

### Task 10: Verificacion final y release

**Files:**
- Modify: `updater.py` (APP_VERSION), `CHANGELOG.md`

- [ ] **Step 1: Ejecutar tests**

```bash
pytest tests/test_database.py -v 2>&1
```

- [ ] **Step 2: Verificar que no haya regresiones**

```bash
python -c "from database import get_connection; conn = get_connection(); print(conn.execute('SELECT sql FROM sqlite_master WHERE name=\"productos\"').fetchone()[0])"
```

- [ ] **Step 3: Actualizar APP_VERSION en updater.py a 0.5.0**

- [ ] **Step 4: Actualizar CHANGELOG.md**

```
## [0.5.0] - 2026-07-29

### Agregado
- Aumento de precios por proveedor: modalidad general y parcial con busqueda y seleccion por checkboxes (F01)

### Corregido
- Ventas: precio unitario tomaba precio de costo en vez de precio de venta (B04)
- Ventas: precio ahora se muestra al seleccionar producto sin necesidad de presionar "Agregar" (B03)
- Ventas: carrito inicia vacio y se agrega campo de codigo de barras (B02)
- Ventas: se agrega diagnostico a impresora para identificar fallas (B01)
- Stock: ajustes muestran stock actual al seleccionar producto y stock resultante post-ajuste
- Compras: carrito inicia vacio (B07)
- Productos: se elimina campo codigo_interno de UI y BD (B06)
- Reportes: selector de periodo cambiado a deslizador visual (B05)
- Tickets: se corrigen saltos de linea antes del corte (B01)

### Removido
- Columna codigo_interno de la tabla productos
```

- [ ] **Step 5: Commit final**

```bash
git add updater.py CHANGELOG.md
git commit -m "chore: bump version to 0.5.0"
git tag v0.5.0
```
