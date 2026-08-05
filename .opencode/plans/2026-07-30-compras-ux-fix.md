# Refactor UX de Compras (fila inicial + preview producto) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mejorar UX de `pages/8_Compras.py`: mostrar 1 fila vacía al cargar la página y mostrar preview del producto al seleccionarlo.

**Architecture:** Refactor de una sola página Streamlit siguiendo el patrón de `pages/7_Ventas.py`: mover selects/inputs fuera del form, agregar `st.info()` con preview inmediato.

**Tech Stack:** Python + Streamlit

## Global Constraints

- No cambiar lógica de negocio en `database.py`
- 139 tests existentes deben seguir pasando
- Seguir patrón de Ventas (`pages/7_Ventas.py`) para consistencia

---

### Task 1: Refactor `pages/8_Compras.py` — estructura fuera del form + preview

**Files:**
- Modify: `pages/8_Compras.py`

**Interfaces:**
- Consumes: funciones existentes de `database.py` (sin cambios)
- Produces: página refactorizada con preview de producto

- [ ] **Step 1: Leer el archivo actual para entender estructura**

Paso informativo — ya está leído.

- [ ] **Step 2: Cambiar inicialización de compra_items a 1 fila vacía**

Cambiar línea 30 de:
```python
st.session_state.compra_items = []
```
a:
```python
st.session_state.compra_items = [{'producto': None, 'cantidad': 1.0, 'precio': 0.0}]
```

- [ ] **Step 3: Mover proveedor y observaciones fuera del form**

Antes del `with st.form()`:
```python
proveedor_sel = st.selectbox("Proveedor", list(prov_dict.keys()), key="compra_prov_sel")
observaciones = st.text_area("Observaciones", placeholder="Opcional", key="compra_obs")
```

Quitar las mismas líneas de adentro del form.

- [ ] **Step 4: Renderizar filas de producto fuera del form**

Mover el bloque `for idx, item in enumerate(...)` fuera del `with st.form()`.
Los selects/inputs pasan a usar `st.selectbox`/`st.number_input` comunes (no form).
Botón "Quitar" cambia de `st.form_submit_button` a `st.button`.

```python
st.markdown("#### Productos")

for idx, item in enumerate(st.session_state.compra_items):
    col_prod, col_cant, col_precio, col_del = st.columns([3, 1, 1, 0.5])
    with col_prod:
        prod_label = st.selectbox(
            f"Producto {idx+1}",
            [""] + list(prod_opts.keys()),
            index=0 if item['producto'] is None else (list(prod_opts.keys()).index(item['producto']) + 1 if item['producto'] in prod_opts else 0),
            key=f"compra_prod_{idx}"
        )
        item['producto'] = prod_label
        
        # Preview inmediato del producto seleccionado
        if prod_label and prod_label in prod_opts:
            p = prod_lookup[prod_opts[prod_label]]
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
```

- [ ] **Step 5: Botón "Agregar producto" fuera del form**

```python
col_add, _ = st.columns([1, 3])
with col_add:
    if st.button("Agregar producto", use_container_width=True):
        agregar_fila()
        st.rerun()
```

- [ ] **Step 6: Form reducido solo para Confirmar Compra**

```python
with st.form("compra_form"):
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
        st.error("❌ Agregá al menos un producto con cantidad y precio mayor a 0.")
    else:
        try:
            compra_id = db.crear_compra(prov_dict[proveedor_sel], items, observaciones)
        except sqlite3.IntegrityError:
            compra_id = None
        if compra_id:
            st.success(f"✅ Compra #{compra_id} registrada correctamente.")
            st.session_state.compra_items = [{'producto': None, 'cantidad': 1.0, 'precio': 0.0}]
            st.rerun()
        else:
            st.error("❌ Error al registrar la compra.")
```

- [ ] **Step 7: Verificar que el archivo compile sin errores**

```bash
python3 -c "import py_compile; py_compile.compile('pages/8_Compras.py', doraise=True)"
```

- [ ] **Step 8: Ejecutar tests**

```bash
python -m pytest tests/ -q
```
Expected: 139 passed

- [ ] **Step 9: Commit**

```bash
git add pages/8_Compras.py
git commit -m "fix: mejora UX de compras - fila inicial y preview de producto"
```

---

Post-commit, regenerar grafo:
```bash
graphify update .
```
