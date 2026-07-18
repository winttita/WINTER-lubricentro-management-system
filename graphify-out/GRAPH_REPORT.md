# Graph Report - Lubricentro  (2026-07-18)

## Corpus Check
- 21 files · ~15,519 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 206 nodes · 363 edges · 33 communities (16 shown, 17 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ec83a4eb`
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
- test_add_movimiento_devolucion
- get_cuenta_corriente_cliente
- get_movimientos_cuenta_corriente
- get_reporte_ingresos_egresos
- get_reporte_inventario
- get_reporte_ventas
- get_reporte_ventas_detallado
- get_ventas
- update_categoria
- update_proveedor
- update_producto
- update_cliente
- update_vehiculo
- update_servicio

## God Nodes (most connected - your core abstractions)
1. `get_connection()` - 43 edges
2. `add_movimiento()` - 21 edges
3. `_crear_producto_con_stock()` - 21 edges
4. `get_productos()` - 20 edges
5. `_crear_dependencias()` - 13 edges
6. `add_producto()` - 11 edges
7. `Changelog - Lubricentro Winter` - 8 edges
8. `get_movimientos()` - 8 edges
9. `get_categorias()` - 8 edges
10. `add_categoria()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `_crear_producto_con_stock()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_get_productos_excluye_inactivos()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_init_db_crea_diez_tablas()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `_crear_dependencias()` --calls--> `get_categorias()`  [EXTRACTED]
  tests/test_database.py → database.py
- `_crear_producto_con_stock()` --calls--> `get_categorias()`  [EXTRACTED]
  tests/test_database.py → database.py

## Import Cycles
- None detected.

## Communities (33 total, 17 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.11
Nodes (26): Exception, apply_update(), check_for_update(), clear_update_dir(), compare_versions(), download_asset(), find_asset(), get_latest_release() (+18 more)

### Community 1 - "test_database.py"
Cohesion: 0.36
Nodes (10): add_producto(), _crear_dependencias(), test_add_producto_codigo_barras_duplicado(), test_add_producto_codigo_duplicado(), test_add_producto_fraccionable(), test_add_producto_nombre_null(), test_add_producto_stock_precio_cero(), test_add_producto_tipo_unidad_invalido() (+2 more)

### Community 2 - "get_connection"
Cohesion: 0.20
Nodes (10): add_cliente(), add_orden_detalle(), add_servicio(), get_clientes(), get_connection(), get_orden_detalle(), get_ordenes(), get_servicios() (+2 more)

### Community 3 - "database.py"
Cohesion: 0.33
Nodes (5): After Code Changes, AGENTS.md - Lubricentro Project, Auto-load Graphify Context on Session Start, Project Structure, Quick Queries During Session

### Community 4 - "add_movimiento"
Cohesion: 0.10
Nodes (19): [0.1.0] - 2026-07-16, [0.2.0] - 2026-07-17, [0.2.1] - 2026-07-17, [0.2.2] - 2026-07-17, [0.2.3] - 2026-07-18, Agregado, Agregado, Agregado (+11 more)

### Community 5 - "get_movimientos"
Cohesion: 0.11
Nodes (39): add_movimiento(), backup_db(), get_movimientos(), get_productos(), Registra un movimiento de stock y actualiza el stock_actual del producto.     Re, _crear_producto_con_stock(), Helper para crear un producto con categoría, proveedor y stock inicial, Debe devolver una lista vacía cuando no hay movimientos (+31 more)

### Community 6 - "_crear_producto_con_stock"
Cohesion: 0.53
Nodes (6): add_proveedor(), get_proveedores(), test_add_proveedor_condicion_pago_invalida(), test_add_proveedor_condicion_pago_valida(), test_add_proveedor_null_condicion(), test_add_y_get_proveedores()

### Community 7 - "tickets.py"
Cohesion: 0.17
Nodes (15): formatear_monto(), generar_factura_a_texto(), generar_factura_b_texto(), generar_factura_c_texto(), generar_ticket_texto(), guardar_comprobante_archivo(), imprimir_comprobante(), metodo_pago_nombre() (+7 more)

### Community 8 - "database.py"
Cohesion: 0.17
Nodes (4): add_orden_servicio(), add_vehiculo(), cleanup_old_backups(), Elimina los backups más antiguos, conservando solo los últimos max_backups.

### Community 9 - "crear_venta"
Cohesion: 0.50
Nodes (4): crear_venta(), get_ultimo_numero_comprobante(), Obtiene el último número de comprobante para un tipo y punto de venta., Crea una venta completa con items, actualiza stock y registra movimiento.     it

### Community 11 - "get_venta_completa"
Cohesion: 0.50
Nodes (4): get_venta_completa(), get_venta_detalle(), Obtiene venta completa con cabecera y items., Obtiene el detalle de una venta.

### Community 12 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 13 - "init_db"
Cohesion: 0.67
Nodes (3): init_db(), Apunta database.DB_NAME a un archivo temporal y lo inicializa limpio., temp_db()

### Community 17 - "test_add_movimiento_devolucion"
Cohesion: 0.53
Nodes (6): add_categoria(), get_categorias(), test_add_categoria_duplicado_devuelve_false(), test_add_categoria_null(), test_add_categoria_string_vacio(), test_add_y_get_categorias()

## Knowledge Gaps
- **19 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `Agregado`, `Corregido`, `Cambiado` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_connection()` connect `get_connection` to `test_database.py`, `get_movimientos`, `_crear_producto_con_stock`, `database.py`, `crear_venta`, `get_venta_completa`, `init_db`, `crear_ajuste_stock`, `get_ajustes_stock`, `get_clientes_con_deuda`, `test_add_movimiento_devolucion`, `get_cuenta_corriente_cliente`, `get_movimientos_cuenta_corriente`, `get_reporte_ingresos_egresos`, `get_reporte_inventario`, `get_reporte_ventas`, `get_reporte_ventas_detallado`, `get_ventas`, `update_categoria`, `update_proveedor`, `update_producto`, `update_cliente`, `update_vehiculo`, `update_servicio`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `add_movimiento()` connect `get_movimientos` to `database.py`, `crear_venta`, `get_connection`, `crear_ajuste_stock`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `get_productos()` connect `get_movimientos` to `database.py`, `test_database.py`, `get_connection`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **What connects `$schema`, `.opencode/plugins/graphify.js`, `Agregado` to the rest of the system?**
  _19 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._
- **Should `add_movimiento` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `get_movimientos` be split into smaller, more focused modules?**
  _Cohesion score 0.11025641025641025 - nodes in this community are weakly interconnected._