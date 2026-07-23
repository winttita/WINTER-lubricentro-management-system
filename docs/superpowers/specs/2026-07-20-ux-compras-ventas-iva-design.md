# Diseño: Correcciones UX en Compras, Ventas e IVA para v0.2.5

Fecha: 2026-07-20
Versión destino: v0.2.5
Enfoque aprobado: A (minimo, UI-first)

## 1. Contexto y motivacion

El modulo de Compras limita artificiosamente la carga a 3 articulos y precarga todos los campos, lo que obliga al usuario a ver 3 grupos de inputs aunque solo quiera cargar 1. El modulo de Ventas presenta varios problemas de usabilidad: precarga automatica de todos los productos al ingresar, imposibilidad de especificar cantidades al agregar al carrito, informacion incompleta al buscar por codigo de barras (falta el nombre del producto) y un error generico "Error al procesar la venta, verificar stock" que aparece incluso cuando hay stock disponible. Adicionalmente, el IVA del 21% se muestra siempre y se suma al total sin importar el tipo de comprobante, cuando la convencion AFIP para Factura A indica que el precio final ya incluye IVA.

Estas correcciones buscan alinear el sistema con convenciones estandar de punto de venta (POS) y legislacion tributaria argentina, mejorando la intuicion del flujo de compra/venta.

## 2. Alcance

**Incluido:**
- `pages/8_Compras.py`: UI dinamica para items de compra.
- `pages/7_Ventas.py`: busqueda lazy, vista previa con input de cantidad,validacion UI de stock, desglose IVA condicional.
- `database.py`: cambio de firma de `crear_venta` para retornar mensaje de error especifico; correccion de la ecuacion de IVA; eliminacion del cierre prematuro de conexion en la validacion de stock.
- `tests/test_database.py`: tests nuevos para los casos corregidos.

**Excluido:**
- Migraciones de esquema de base de datos.
- Nuevas columnas `precio_venta_con_iva`.
- Refactor de reportes o tickets (mas alla de ajustar lectura de `subtotal`/`iva`/`total` ya existentes).
- Cambios en la pagina de Productos (precio sigue editable alli, segun aclaracion del usuario).

## 3. Decisiones confirmadas con el usuario

1. **Modelo de precio para Factura A:** `precio_venta` en tabla `productos` YA incluye IVA. No se suma 21% al final. Neto = `precio_venta / 1.21`.
2. **Flujo de carga de cantidades en venta:** vista previa + input de cantidad al hacer clic en un producto desde el buscador.
3. **Resolucion del bug "verificar stock":** validacion completa en UI + mensaje de error especifico desde el backend.
4. **Aclaracion adicional (seccion 2):** el precio NO se edita en el modulo de Ventas; solo en Productos y Compras.

## 4. Diseno por componente

### 4.1 Modulo de Compras - UI dinamica

**Archivo:** `pages/8_Compras.py` (no se toca `database.py:crear_compra`, que ya acepta lista completa).

**Estado del formulario:**
- `st.session_state.compra_items`: lista de dicts `{producto_id, cantidad, precio_unitario}`. Inicia con 1 entrada vacia.
- Boton "+ Agregar articulo" agrega un dict vacio; limite superior 100. Al llegar a 100, el boton se deshabilita con tooltip "Limite maximo alcanzado".

**Renderizado:**
- Itera sobre `st.session_state.compra_items` con `enumerate()`. Claves unicas: `prod_{i}`, `cant_{i}`, `precio_{i}`.
- El Articulo 1 (indice 0) se muestra siempre; no puede eliminarse.
- Los articulos 2..N tienen boton "Eliminar" (manipula `session_state` y `st.rerun()`).
- Encima del formulario: contador discreto `Articulos: K / 100`.

**Validacion al confirmar:**
- Filtra items con `cantidad > 0 AND precio_unitario > 0 AND producto_id != None`.
- Si la lista filtrada queda vacia: `st.error("Agrega al menos un articulo con cantidad y precio mayor a 0.")`.
- Si hay items con mismo `producto_id`, sugiere consolidar (no bloquea).
- Llama a `db.crear_compra(proveedor_id, items_filtrados, observaciones)`.
- En exito: muestra `Compra #{id} registrada correctamente.` y resetea `session_state.compra_items` a 1 entrada vacia.

**Historial de compras:** se mantiene intacto (lineas 60-93 del archivo actual).

### 4.2 Modulo de Ventas - Busqueda, vista previa y cantidades

**Archivos:** `pages/7_Ventas.py` (UI), `database.py:crear_venta` (backend).

**Carga inicial:**
- Se elimina `productos = db.get_productos()` del tope del archivo (linea 8 actual).
- La lista de productos se carga solo cuando hay query de busqueda; minimo 3 caracteres para disparar la consulta.

**Buscador:**
- `st.text_input("Buscar por nombre o codigo de barras", placeholder="Escribi al menos 3 caracteres...")`.
- Filtro en memoria (Python list comprehension) sobre `db.get_productos()` cacheado en `st.session_state`.
- Cada resultado se muestra como boton con 3 lineas:
  ```
  {nombre}
  CB: {codigo_barras} | ${precio_venta:.2f} | Stock: {stock_actual}
  ```
- Productos con `stock_actual == 0` se desactivan con etiqueta `(SIN STOCK)`.

**Vista previa al hacer clic:**
- `st.session_state.producto_seleccionado = producto_id`.
- Tarjeta con:
  - Nombre, codigo de barras, categoria (info de solo lectura).
  - Precio unitario (solo lectura, **no editable**).
  - Stock disponible.
  - `st.number_input("Cantidad a agregar", min_value=1, max_value=stock_disponible, step=1)`.
  - Boton "Agregar al carrito": valida `cantidad <= stock_actual - cantidad_ya_en_carrito(producto_id)`.
  - Boton "Cancelar": limpia `producto_seleccionado`.

**Carrito (sidebar):**
- Estructura similar a la actual: nombre, precio (solo lectura), cantidad, subtotal.
- **Cantidad editable** directamente en el sidebar via `st.number_input`. Al cambiar, se re-valida contra stock actual.
- Boton "Eliminar" para quitar items.

**Confirmacion de venta:**
- Antes de llamar a `db.crear_venta()`, re-loopea el carrito y valida `cantidad <= stock_actual` por item.
- Si algun item falla, muestra `st.error` con el primer item fallido y NO llama al backend.

### 4.3 Manejo de IVA - Factura A con precio IVA incluido

**Archivos:** `pages/7_Ventas.py` (sidebar), `database.py:crear_venta` (calculo).

**Modelo de precio:**
- `precio_venta` en tabla `productos` = precio final con IVA incluido (Factura A) y precio final para otros comprobantes (B/C/ticket no desglosan IVA).

**Frontend (sidebar de Ventas):**
- Se eliminan las lineas 38-40 actuales que siempre muestran IVA y total c/IVA.
- Reemplazo condicional segun `tipo_comp`:
  - `factura_a`: muestra `Subtotal neto`, `IVA (21%)`, `Total` donde `neto = total / 1.21` y `iva = total - neto`.
  - `ticket`, `factura_b`, `factura_c`: muestra solo `Total: $X` (sin desglose).

**Backend (`database.py:crear_venta`, lineas 948-950):**
- Cambio de la ecuacion:
  ```python
  total = sum(float(item['cantidad']) * float(item['precio_unitario']) for item in items)
  if tipo_comprobante == 'factura_a':
      subtotal = round(total / 1.21, 2)
      iva = round(total - subtotal, 2)
  else:
      subtotal = total
      iva = 0.0
  ```
- Se persisten `subtotal`, `iva`, `total` en la tabla `ventas` (campos ya existen).

**Compatibilidad:**
- Tickets, reportes y `get_venta_detalle` leen `subtotal`/`iva`/`total` de la DB; con el nuevo calculo:
  - Factura A: `subtotal < total`, `iva > 0`.
  - Otros: `subtotal == total`, `iva == 0`.
- No requiere migracion.

### 4.4 Validacion de stock y mensajes de error especificos

**Archivos:** `database.py:crear_venta` (firma y logica), `pages/7_Ventas.py` (consumo del nuevo mensaje), `tests/test_database.py`.

**Cambio de firma de `crear_venta`:**
- Actual: `crear_venta(...) -> (venta_id, numero_comprobante) | (None, None)`.
- Nueva: `crear_venta(...) -> (venta_id, numero, error_msg)` donde `error_msg` es `None` en exito o string especifico en fallo.

**Validacion de stock (backend):**
- Se mueve el bloque de validacion (lineas 934-943 actuales) **dentro** del mismo `try` que las inserciones, usando la misma conexion. Elimina el `conn.close()` prematuro de la linea 945 (causa raiz probable del bug reportado).
- Mensajes de error especificos:
  - Stock insuficiente: `f"Stock insuficiente de \"{nombre_producto}\": solicitado {cant}, disponible {stock}"`.
  - Producto inexistente o inactivo: `f"Producto inactivo o inexistente (id={item['producto_id']})"`.
  - Items vacios: `"No hay items en la venta"`.

**Validacion de stock (frontend):**
- Al agregar al carrito: `cantidad <= stock_actual - cantidad_ya_en_carrito(producto_id)`.
- Al confirmar: re-valida todos los items; si alguno falla, muestra error con detalle y no llama al backend.

**Tests nuevos en `tests/test_database.py`:**
- `test_crear_venta_stock_insuficiente_retorna_mensaje_especifico`
- `test_crear_venta_factura_a_calculo_iva_incluido`
- `test_crear_venta_ticket_sin_iva`
- `test_crear_venta_producto_inactivo_retorna_error`

**Tests existentes que verifican `(None, None)` de `crear_venta`:** se actualizan a `(None, None, msg)`.

## 5. Arquitectura y flujo de datos

```
[Usuario: busca producto]
        |
        v
[7_Ventas.py: filtra productos por query]
        |
        v
[Usuario: clic en resultado]
        |
        v
[Vista previa: cantidad + agregar]
        |
        v
[session_state.carrito]
        |
        v
[Usuario: confirmar venta]
        |
        v
[7_Ventas.py: re-valida stock por item en UI]
        |  (si falla -> st.error con detalle, no llama backend)
        v
[db.crear_venta(cliente_id, tipo_comp, items, metodo, usuario_id)]
        |
        v
[backend: valida stock + calcula subtotal/iva/total + inserta]
        |
        v
[(venta_id, numero, None) | (None, None, error_msg)]
```

Compras sigue un flujo similar pero sin validacion de stock (las compras SUMAN stock).

## 6. Manejo de errores

| Caso | Frontend | Backend |
|------|----------|---------|
| Carrito vacio | `st.error("Agrega productos al carrito")` | no se llama |
| Stock insuficiente en agregar | `st.warning("Solo hay N unidades disponibles")` | no se llama |
| Stock insuficiente en confirmar | `st.error` con item+detalle, no llama backend | no se llama |
| Stock cambiado entre UI y backend | - | Retorna `(None, None, "Stock insuficiente de X: solicitado N, disponible M")` |
| Producto inactivo | no aparece en busqueda | (None, None, "Producto inactivo o inexistente") |
| Items vacios en crear_venta | no aplica | (None, None, "No hay items en la venta") |
| Compra sin items validos | `st.error("Agrega al menos un articulo...")` | no se llama |
| Limite 100 articulos alcanzado | boton "+" deshabilitado | no aplica |

## 7. Testing

- Tests unitarios en `tests/test_database.py` con `temp_db` (fixture ya existente).
- Cobertura:
  - `crear_venta` exito con ticket (iva=0, subtotal=total).
  - `crear_venta` exito con factura_a (iva=total - total/1.21, subtotal=total/1.21).
  - `crear_venta` stock insuficiente retorna mensaje especifico.
  - `crear_venta` producto inactivo retorna error.
  - Compra con 1 item exito.
  - Compra con 100 items exito (limite).
  - Compra con 101 items: UI lo impide; no se prueba backend.
- Tests de UI no se automatizan (Streamlit testing es costoso); se verifica manualmente.

## 8. Convenciones y compatibilidad

- Sigue CONVENTIONS.md: sin emojis en codigo/commits, mensajes de commit en Conventional Commits en espanol.
- `APP_VERSION` en `updater.py` se actualizara a `0.2.5` antes de taggear.
- CHANGELOG.md recibira entrada `[0.2.5]` bajo `Agregado`, `Corregido`, `Cambiado` segun corresponda.
- No rompe builds existentes: el cambio de firma de `crear_venta` afecta solo a `7_Ventas.py` y tests; se actualizan ambos en el mismo PR.

## 9. Out of scope (YAGNI)

- Login/permisos en ventas (queda `usuario_id = 1` hardcodeado).
- Multi-almacen/sucursal.
- Descuentos/promociones.
- Edicion de precio en linea del carrito de ventas.
- Migracon de esquema.
- Refactor de reportes mas alla de leer campos ya existentes.
