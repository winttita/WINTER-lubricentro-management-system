# Diseno: Correcciones y mejoras para release v0.5.0

Fecha: 2026-07-29
Version destino: v0.5.0

## 1. Contexto y motivacion

Los usuarios detectaron varios errores en el sistema que afectan la operacion
diaria: la impresora termica no funciona en el flujo normal de venta, los
formularios muestran datos precargados en lugar de comenzar vacios, los precios
no se autocompletan al seleccionar productos (requieren un click extra en
"Agregar"), el selector de periodo en reportes no permite ver todas las
opciones, y el campo "codigo interno" de productos es irrelevante.
Adicionalmente, la funcionalidad de aumento de precios por proveedor acordada
previamente no fue implementada.

Estas correcciones buscan alinear el sistema con el flujo de trabajo real del
lubricentro: comenzar con campos vacios, mostrar informacion apenas se
selecciona un producto, y actualizar los resultados inmediatamente despues de
cada accion.

## 2. Alcance

**Incluido:**

- `pages/7_Ventas.py`: correcciones de precio (B04), autocompletado de precio
  al seleccionar producto (B03), carrito vacio al iniciar y busqueda por codigo
  de barras (B02), diagnostico de impresora (B01).
- `pages/1_Stock.py`: visualizacion inmediata de stock al seleccionar producto
  en ajustes, y nueva pestana "Aumento de Precios" (F01).
- `pages/8_Compras.py`: carrito vacio al iniciar (B07).
- `pages/3_Productos.py`: eliminacion del campo codigo_interno de formularios
  de alta y edicion (B06).
- `pages/9_Reportes.py`: selector de periodo a deslizador (B05).
- `tickets.py`: correccion de corte de ticket y diagnostico de impresora (B01).
- `database.py`: nueva funcion aumentar_precios_por_lista (F01) y eliminacion
  de columna codigo_interno (B06).
- `tests/test_database.py`: actualizacion de indices de columnas (B06) y tests
  de nueva funcion (F01).

**Excluido:**

- Refactor de la estructura general del proyecto.
- Cambios en la logica de negocio de crear_venta o crear_compra.
- Nuevos reportes o pantallas adicionales.
- Integracion con AFIP para facturacion electronica.

## 3. Decisiones confirmadas con el usuario

1. **Codigo interno (B06):** se elimina completamente de la UI y de la base
   de datos.
2. **Aumento de precios (F01):** porcentual, con modalidad general (todo el
   proveedor) y parcial (busqueda por texto + checkboxes por producto). Se
   agrega como pestana en `pages/1_Stock.py`.
3. **Selector de periodo (B05):** se reemplaza `st.selectbox` por
   `st.select_slider` para navegacion visual entre opciones.
4. **Campos vacios:** Todos los formularios y carritos deben iniciar sin
   valores precargados. Solo se muestra el campo vacio listo para completar.

## 4. Diseno por componente

### 4.1 Ventas - Correccion de precio (B04)

**Archivo:** `pages/7_Ventas.py:100`

**Problema:** La linea 100 asigna `item['precio'] = float(p[10])` donde p[10]
es precio_costo. Debe ser p[11] (precio_venta).

**Solucion:** Cambiar indice de p[10] a p[11].

### 4.2 Ventas - Autocompletado de precio (B03)

**Archivo:** `pages/7_Ventas.py:85-117`

**Problema:** El selector de producto y el autofill de precio estan dentro de
`st.form()`. Streamlit no rerunea la pagina cuando se cambia un widget dentro
de un formulario, por lo que el precio solo se actualiza al hacer submit.

**Solucion:** Mover el selector de producto y la visualizacion de precio FUERA
del formulario. Usar `on_change` callback en el `st.selectbox` para actualizar
el precio en `st.session_state` inmediatamente. Dentro del formulario quedan:
cantidad, subtotal del item y boton "Agregar producto".

### 4.3 Ventas - Carrito vacio y scanner (B02)

**Archivo:** `pages/7_Ventas.py:36-37`

**Problema:**
- `st.session_state.venta_items` se inicializa con 1 fila precargada
- El codigo de barras no tiene campo de entrada dedicado

**Solucion:**
- Inicializar `venta_items = []` (vacio)
- Agregar campo de texto "Codigo de barras" fuera del formulario
- Al escribir/escanear un codigo, buscar en productos por codigo_barras
- Si se encuentra, autoseleccionar el producto y mostrar precio/stock
- Si no se encuentra, mostrar mensaje "Producto no encontrado"

### 4.4 Ventas - Impresora (B01)

**Archivo:** `pages/7_Ventas.py:168-229`, `tickets.py:165-208`

**Problemas:**
1. **No imprime en venta:** `imprimir_venta()` traga toda excepcion con
   `except Exception: return False`.
2. **Ticket cortado:** Solo 2 saltos de linea (`b'\n\n'`) antes del comando
   de corte `GS V\x00`.

**Solucion:**
- Agregar logging/diagnostico a `imprimir_venta()` para identificar el error
- Aumentar los saltos de linea en `imprimir_comprobante()` de 2 a ~8

### 4.5 Stock - Ajustes con stock inmediato

**Archivo:** `pages/1_Stock.py:150-190`

**Problema:** El selector de producto esta dentro de `st.form()`, el stock
actual no se muestra al seleccionar producto. El stock post-ajuste tampoco se
refleja visualmente.

**Solucion:**
- Mover el selector de producto fuera del formulario
- Mostrar stock actual inmediatamente debajo del selector
- Despues de aplicar el ajuste, mostrar el nuevo stock

### 4.6 Compras - Carrito vacio (B07)

**Archivo:** `pages/8_Compras.py:28-29`

**Problema:** `compra_items` se inicializa con 1 fila precargada.

**Solucion:** Inicializar `compra_items = []` (vacio).

### 4.7 Productos - Eliminar codigo interno (B06)

**Archivos:** `pages/3_Productos.py`, `database.py`

**Problema:** El campo codigo_interno es irrelevante para el usuario.

**Solucion:**
- Eliminar del formulario de creacion y edicion en `3_Productos.py`
- Eliminar columna de la BD con ALTER TABLE
- Actualizar `add_producto()` y `update_producto()` en `database.py`
- Actualizar `get_precios_para_lista()` en `database.py`
- Actualizar indices de columnas en todos los archivos que usan `p.*`
- Actualizar etiquetas de productos en selectboxes (eliminar `[p[1]]`)
- Actualizar tests que referencian indices de productos

**Impacto de cambio de indices (get_productos):**

| Columna | Indice actual | Nuevo indice |
|---------|--------------|--------------|
| id | p[0] | p[0] |
| codigo_interno | p[1] | eliminado |
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

### 4.8 Reportes - Selector de periodo (B05)

**Archivo:** `pages/9_Reportes.py:17`

**Problema:** `st.sidebar.selectbox` no permite ver todas las opciones.

**Solucion:** Cambiar a `st.sidebar.select_slider`.

### 4.9 Tickets - Ticket cortado (B01)

**Archivo:** `tickets.py:176`

**Problema:** Solo 2 lineas en blanco antes del comando de corte.

**Solucion:** Cambiar `b'\n\n'` a `b'\n' * 8`.

### 4.10 Nueva funcionalidad - Aumento de precios (F01)

**Archivo:** `pages/1_Stock.py` (nueva pestana), `database.py` (nueva funcion)

**Requisitos:**
- GENERAL: seleccionar proveedor, ingresar porcentaje, aplicar a todos
- PARCIAL: seleccionar proveedor, escribir busqueda, mostrar productos
  filtrados con checkboxes, seleccionar, ingresar % y aplicar

**Nueva funcion en database.py:**

```python
def aumentar_precios_por_lista(producto_ids, porcentaje):
    """Aumenta precio_venta de una lista de productos.
    Args:
        producto_ids: lista de IDs
        porcentaje: ej: 10.0 = +10%
    Returns:
        int: cantidad actualizados
    """
```

**UX:**
- Radio button: General / Parcial
- General: select proveedor + % + boton
- Parcial: select proveedor + busqueda + tabla checkboxes + % + boton
- Mensaje de exito con cantidad de productos actualizados

## 5. Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `pages/7_Ventas.py` | B02, B03, B04 |
| `pages/1_Stock.py` | Ajustes + pestana F01 |
| `pages/8_Compras.py` | B07 |
| `pages/3_Productos.py` | B06 |
| `pages/9_Reportes.py` | B05 |
| `tickets.py` | B01 |
| `database.py` | B06 + F01 |
| `tests/test_database.py` | B06 |
| `pages/10_ListaPrecios.py` | B06 (indices) |
| `pages/4_Ordenes.py` | B06 (indices) |
| `pages/0_Gestion.py` | B06 (indices, verificar) |

## 6. Orden de implementacion sugerido

1. B04 (1 linea, riesgo bajo)
2. B06 (codigo_interno) - impacto global, temprano
3. B05 (select_slider) - cambio aislado
4. B07 (carrito compras vacio) - cambio aislado
5. B02 + B03 (ventas: carrito, scanner, autofill)
6. Stock: ajustes con stock inmediato
7. B01 + ticket cortado (impresora)
8. F01 (aumento precios)
9. Tests y verificacion final
