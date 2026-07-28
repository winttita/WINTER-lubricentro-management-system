# Graph Report - Lubricentro  (2026-07-28)

## Corpus Check
- 35 files · ~44,762 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 619 nodes · 1166 edges · 46 communities (38 shown, 8 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7b19df6e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- updater.py
- test_database.py
- get_connection
- database.py
- add_movimiento
- get_movimientos
- _crear_producto_con_stock
- tickets.py
- database.py
- crear_venta
- graphify.js
- get_venta_completa
- opencode.json
- init_db
- crear_ajuste_stock
- get_ajustes_stock
- get_clientes_con_deuda
- Diseño: Correcciones UX en Compras, Ventas e IVA para v0.2.5
- get_cuenta_corriente_cliente
- get_movimientos_cuenta_corriente
- get_reporte_ingresos_egresos
- get_reporte_inventario
- get_reporte_ventas
- get_reporte_ventas_detallado
- get_ventas
- update_categoria
- update_proveedor
- update_cliente
- update_vehiculo
- update_servicio
- get_compras
- Documentar Código
- 7_Ventas.py
- 8_Compras.py
- anular_compra
- Sistema de Gestión para LUBRICENTRO WINTER
- Agente de Testing
- backup_db
- crear_compra
- get_cuenta_corriente_cliente
- get_detalle_compra
- get_reporte_ventas
- test_get_movimientos_sin_movimientos

## God Nodes (most connected - your core abstractions)
1. `get_connection()` - 85 edges
2. `add_producto()` - 54 edges
3. `add_proveedor()` - 43 edges
4. `add_categoria()` - 40 edges
5. `get_productos()` - 33 edges
6. `_crear_producto_con_stock()` - 30 edges
7. `crear_venta()` - 29 edges
8. `_crear_dependencias()` - 25 edges
9. `add_movimiento()` - 23 edges
10. `add_cliente()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `_crear_producto_con_stock()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_add_producto_con_stock_inicial()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_add_producto_sin_stock_inicial()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_anular_compra()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_anular_compra_registra_devolucion_no_ajuste()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py

## Import Cycles
- None detected.

## Communities (46 total, 8 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.08
Nodes (37): Exception, apply_update(), check_for_update(), clear_update_dir(), compare_versions(), download_asset(), _extract_zip_safe(), find_asset() (+29 more)

### Community 1 - "test_database.py"
Cohesion: 0.15
Nodes (12): 10. Actualización de este documento, 11. Uso de este documento, 1. Propósito y alcance, 2. Tono y estilo, 3. Prohibición de emojis, 4. Versionado (SemVer), 5. Releases y CHANGELOG, 6. Conventional Commits (+4 more)

### Community 2 - "get_connection"
Cohesion: 0.07
Nodes (28): crear_ajuste_stock(), get_ajustes_stock(), get_compras(), get_connection(), get_orden_detalle(), get_ordenes(), get_ultimo_numero_comprobante(), Actualiza los datos de un producto existente. (+20 more)

### Community 3 - "database.py"
Cohesion: 0.29
Nodes (6): After Code Changes, AGENTS.md - Lubricentro Project, Auto-load Graphify Context on Session Start, Project Conventions, Project Structure, Quick Queries During Session

### Community 4 - "add_movimiento"
Cohesion: 0.04
Nodes (46): [0.1.0] - 2026-07-16, [0.2.0] - 2026-07-17, [0.2.1] - 2026-07-17, [0.2.2] - 2026-07-17, [0.2.3] - 2026-07-18, [0.2.4] - 2026-07-20, [0.2.5] - 2026-07-21, [0.2.6] - 2026-07-21 (+38 more)

### Community 5 - "get_movimientos"
Cohesion: 0.09
Nodes (30): add_movimiento(), Registra un movimiento de stock y actualiza el stock_actual del producto.     Re, _crear_producto_con_stock(), Helper para crear un producto con categoría, proveedor y stock inicial, Debe manejar un ajuste positivo correctamente, Debe manejar un ajuste negativo correctamente, Debe manejar una devolución como entrada de stock, Debe manejar el uso interno como salida de stock (+22 more)

### Community 7 - "tickets.py"
Cohesion: 0.12
Nodes (21): abrir_cajon(), formatear_monto(), generar_factura_a_texto(), generar_factura_b_texto(), generar_factura_c_texto(), generar_ticket_texto(), guardar_comprobante_archivo(), imprimir_comprobante() (+13 more)

### Community 8 - "database.py"
Cohesion: 0.09
Nodes (35): add_cliente(), add_orden_detalle(), add_orden_servicio(), add_vehiculo(), desactivar_cliente(), get_clientes(), get_vehiculos(), get_ventas_pendientes_cc() (+27 more)

### Community 9 - "crear_venta"
Cohesion: 0.16
Nodes (18): abrir_caja(), cerrar_caja(), get_caja_abierta(), Abre una nueva caja.          Args:         saldo_inicial (float): Saldo inicial, Cierra una caja abierta.          Args:         caja_id (int): ID de la caja a c, Obtiene la caja actualmente abierta.          Returns:         tuple: (id, saldo, Registra un movimiento en caja.          Args:         caja_id (int): ID de la c, registrar_movimiento_caja() (+10 more)

### Community 11 - "get_venta_completa"
Cohesion: 0.50
Nodes (4): get_venta_completa(), get_venta_detalle(), Obtiene el detalle de una venta., Obtiene venta completa con cabecera y items.

### Community 12 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 13 - "init_db"
Cohesion: 0.20
Nodes (9): init_db(), _migrate_legacy_db_location(), Devuelve el directorio de datos de usuario (absoluto) por SO.      Windows: %APP, Calcula DB_NAME y BACKUP_DIR absolutos. Crea el dir si no existe.     Devuelve (, Mueve lubricantro.db (y backups/) desde el directorio del script/app     (legacy, _resolve_data_paths(), _user_data_dir(), Apunta database.DB_NAME a un archivo temporal y lo inicializa limpio. (+1 more)

### Community 14 - "crear_ajuste_stock"
Cohesion: 0.07
Nodes (55): add_categoria(), add_proveedor(), aumentar_precios_por_categoria(), crear_compra(), get_categorias(), get_categorias_por_proveedor(), get_clientes_con_deuda(), get_precios_para_lista() (+47 more)

### Community 15 - "get_ajustes_stock"
Cohesion: 0.13
Nodes (14): Correcciones UX Compras, Ventas e IVA v0.2.5 - Implementation Plan, Global Constraints, Task 10: Actualizar APP_VERSION en updater.py y crear release v0.2.5, Task 11: Verificación final y commit final, Task 1: Tests nuevos para database.py - crear_venta, Task 2: Actualizar firma y logica de crear_venta en database.py, Task 3: Implementar UI dinamica en pages/8_Compras.py, Task 4: Implementar busqueda lazy, vista previa y carrito en pages/7_Ventas.py (+6 more)

### Community 16 - "get_clientes_con_deuda"
Cohesion: 0.35
Nodes (12): Path, _cleanup(), _extract_zip_safe(), _launch_launcher(), _log(), main(), Watchdog de actualizacion automatica para Lubricentro Winter.  Se lanza como pro, Extrae un ZIP validando cada entrada contra path traversal.      Devuelve True s (+4 more)

### Community 17 - "Diseño: Correcciones UX en Compras, Ventas e IVA para v0.2.5"
Cohesion: 0.13
Nodes (14): 1. Contexto y motivacion, 2. Alcance, 3. Decisiones confirmadas con el usuario, 4.1 Modulo de Compras - UI dinamica, 4.2 Modulo de Ventas - Busqueda, vista previa y cantidades, 4.3 Manejo de IVA - Factura A con precio IVA incluido, 4.4 Validacion de stock y mensajes de error especificos, 4. Diseno por componente (+6 more)

### Community 18 - "get_cuenta_corriente_cliente"
Cohesion: 0.09
Nodes (21): 1. Obtener el Certificado, 2. Configurar Secrets en GitHub, 3. Build Local con Firma (Windows), 4. Build en GitHub Actions (CI/CD), 5. Configuración del Launcher (`--uac-admin`), 6. Troubleshooting Común, 6. Verificación Manual, 7. Renovación Anual (+13 more)

### Community 19 - "get_movimientos_cuenta_corriente"
Cohesion: 0.17
Nodes (12): get_movimientos_cuenta_corriente(), Obtiene movimientos de cuenta corriente de un cliente (ventas y pagos)., Registra un pago (abono) de cuenta corriente.          Inserta un movimiento con, registrar_pago_cc(), registrar_pago_cc debe devolver False si el cliente no existe., El movimiento de pago debe tener tipo_movimiento='pago'., get_movimientos_cuenta_corriente debe incluir tipo_movimiento y metodo_pago., registrar_pago_cc no debe aceptar montos negativos. (+4 more)

### Community 20 - "get_reporte_ingresos_egresos"
Cohesion: 0.29
Nodes (4): calcular_totales(), imprimir_venta(), Genera e imprime el comprobante de una venta., Calcula subtotal, iva y total segun el tipo de comprobante.     Reglas (alineada

### Community 21 - "get_reporte_inventario"
Cohesion: 0.33
Nodes (4): cerrar_sesion(), init_session(), Inicializa flags de sesión si no existen., Limpia el estado de sesión.

### Community 22 - "get_reporte_ventas"
Cohesion: 0.10
Nodes (22): cambiar_password(), hash_password(), Genera un hash SHA-256 de la contraseña., Verifica credenciales de usuario.          Devuelve un dict con user_id, nombre,, Actualiza la contraseña de un usuario.          Devuelve True si se actualizó co, verificar_login(), hash_password debe devolver el mismo hash para la misma entrada., hash_password deve devolver hashes distintos para passwords distintas. (+14 more)

### Community 25 - "update_categoria"
Cohesion: 0.33
Nodes (6): aumentar_precios_proveedor(), Aumenta el precio_venta de todos los productos de un proveedor en un porcentaje, aumentar_precios_proveedor debe devolver False si el proveedor no existe., aumentar_precios_proveedor no debe aceptar porcentaje negativo., test_aumentar_precios_proveedor_porcentaje_negativo(), test_aumentar_precios_proveedor_proveedor_inexistente()

### Community 26 - "update_proveedor"
Cohesion: 0.40
Nodes (5): add_servicio(), get_servicios(), test_add_servicio_nombre_vacio(), test_add_servicio_precio_invalido(), test_add_servicio_precio_negativo()

### Community 28 - "update_cliente"
Cohesion: 0.67
Nodes (3): agrupar_por_proveedor(), generar_pdf(), Genera un PDF de la lista de precios agrupada por proveedor.      Maneja acentos

### Community 29 - "update_vehiculo"
Cohesion: 0.67
Nodes (3): backup_db(), test_backup_db_crea_archivo(), test_backup_db_no_existe()

### Community 30 - "update_servicio"
Cohesion: 0.14
Nodes (31): add_producto(), _crear_dependencias(), Verifica que get_reporte_inventario devuelva datos correctos con valorización., Solo productos activos con stock > 0 deben aparecer en la lista de precios., Stock insuficiente debe retornar mensaje especifico, no (None, None)., Factura A: precio_venta ya incluye IVA. Total = subtotal_neto + iva = precio_fin, Ticket: sin IVA, subtotal = total = precio_venta., Producto inactivo debe retornar error especifico. (+23 more)

### Community 33 - "get_compras"
Cohesion: 0.06
Nodes (32): 1. Manejo de caja (simple), 2. IntegrityError faltantes (rápido), 3. Carteles de éxito/error consistentes, 4. Soft delete de clientes, 5. Validación de fracciones en productos "Entero", Acciones, Archivos a modificar, Archivos a revisar (+24 more)

### Community 34 - "Documentar Código"
Cohesion: 0.22
Nodes (8): Adaptación a otros lenguajes, Buenas prácticas generales, Checklist antes de hacer commit, Con pdoc (más simple), Con Sphinx (recomendado para Python), Documentar Código, Generar documentación automática, Pasos para documentar un módulo (ejemplo en Python)

### Community 35 - "7_Ventas.py"
Cohesion: 0.33
Nodes (6): get_reporte_inventario(), Reporte de inventario actual: productos con stock y valorizacion., Cuando no hay productos activos, el reporte de inventario debe estar vacío., Productos desactivados (activo=0) no deben aparecer en el reporte., test_reporte_inventario_excluye_productos_inactivos(), test_reporte_inventario_vacio()

### Community 36 - "8_Compras.py"
Cohesion: 0.16
Nodes (6): cleanup_old_backups(), get_reporte_ingresos_egresos(), Reporte de ingresos vs egresos.     Ingresos = total FROM ventas (incluye IVA) +, Elimina los backups más antiguos, conservando solo los últimos max_backups., inject_global_css(), Inyecta CSS para ocultar el mensaje 'Press Enter to submit form' de Streamlit.

### Community 37 - "anular_compra"
Cohesion: 0.50
Nodes (4): anular_compra(), Anula una compra revirtiendo el stock de cada producto.     Retorna True si se a, anular_compra debe registrar el movimiento como 'devolucion', no 'ajuste'., test_anular_compra_registra_devolucion_no_ajuste()

### Community 38 - "Sistema de Gestión para LUBRICENTRO WINTER"
Cohesion: 0.17
Nodes (11): Actualizaciones Remotas, Build del .exe (Windows), Cambiar la versión actual, Configuración en la app, Descripción, Estado del Proyecto, Estructura Técnica, Impresora Térmica (+3 more)

### Community 39 - "Agente de Testing"
Cohesion: 0.40
Nodes (4): Agente de Testing, Flujo de trabajo típico, Idioma, Responsabilidades

### Community 42 - "get_cuenta_corriente_cliente"
Cohesion: 0.11
Nodes (20): crear_venta(), get_cuenta_corriente_cliente(), Crea una venta completa con items, actualiza stock y registra movimiento.     it, Obtiene el saldo actual de cuenta corriente de un cliente., Si no hay caja abierta, crear_venta no debe registrar movimiento de caja., Items vacios debe retornar error especifico., crear_venta debe rechazar cantidades negativas o cero., crear_venta debe rechazar precios negativos. (+12 more)

### Community 62 - "test_get_movimientos_sin_movimientos"
Cohesion: 0.16
Nodes (16): get_movimientos(), get_productos(), aumentar_precios_proveedor debe actualizar precio_venta de productos del proveed, Debe devolver una lista vacía cuando no hay movimientos, Debe devolver movimientos ordenados por fecha descendente y aplicar límite, Debe agregar una compra exitosamente y aumentar el stock, Debe agregar una venta exitosamente y disminuir el stock, Debe fallar cuando no hay suficiente stock para una salida (+8 more)

## Knowledge Gaps
- **137 isolated node(s):** `Descripción`, `Estado del Proyecto`, `Estructura Técnica`, `Próximos Pasos`, `Actualizaciones Remotas` (+132 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_connection()` connect `get_connection` to `get_movimientos`, `_crear_producto_con_stock`, `database.py`, `crear_venta`, `get_venta_completa`, `init_db`, `crear_ajuste_stock`, `get_movimientos_cuenta_corriente`, `get_reporte_ventas`, `get_reporte_ventas_detallado`, `get_ventas`, `update_categoria`, `update_proveedor`, `update_servicio`, `7_Ventas.py`, `8_Compras.py`, `anular_compra`, `backup_db`, `get_cuenta_corriente_cliente`, `get_detalle_compra`, `get_reporte_ventas`, `test_get_movimientos_sin_movimientos`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `add_producto()` connect `update_servicio` to `get_connection`, `7_Ventas.py`, `8_Compras.py`, `get_movimientos`, `database.py`, `get_cuenta_corriente_cliente`, `init_db`, `crear_ajuste_stock`, `get_movimientos_cuenta_corriente`, `test_get_movimientos_sin_movimientos`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `crear_venta()` connect `get_cuenta_corriente_cliente` to `get_connection`, `8_Compras.py`, `get_movimientos`, `database.py`, `crear_venta`, `crear_ajuste_stock`, `get_movimientos_cuenta_corriente`, `update_servicio`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **What connects `Descripción`, `Estado del Proyecto`, `Estructura Técnica` to the rest of the system?**
  _137 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07823613086770982 - nodes in this community are weakly interconnected._
- **Should `get_connection` be split into smaller, more focused modules?**
  _Cohesion score 0.07142857142857142 - nodes in this community are weakly interconnected._
- **Should `add_movimiento` be split into smaller, more focused modules?**
  _Cohesion score 0.0425531914893617 - nodes in this community are weakly interconnected._