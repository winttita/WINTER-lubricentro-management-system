# Graph Report - Lubricentro  (2026-07-21)

## Corpus Check
- 27 files · ~26,362 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 274 nodes · 492 edges · 36 communities (17 shown, 19 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a6a32c48`
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
- get_compras
- 7_Ventas.py
- crear_ajuste_stock

## God Nodes (most connected - your core abstractions)
1. `get_connection()` - 52 edges
2. `get_productos()` - 25 edges
3. `add_producto()` - 23 edges
4. `_crear_producto_con_stock()` - 21 edges
5. `add_movimiento()` - 20 edges
6. `_crear_dependencias()` - 19 edges
7. `get_categorias()` - 13 edges
8. `add_categoria()` - 13 edges
9. `get_proveedores()` - 13 edges
10. `add_proveedor()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `_crear_producto_con_stock()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_add_producto_con_stock_inicial()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_add_producto_sin_stock_inicial()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_anular_compra()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_crear_ajuste_stock_con_movimiento()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py

## Import Cycles
- None detected.

## Communities (36 total, 19 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.11
Nodes (26): Exception, apply_update(), check_for_update(), clear_update_dir(), compare_versions(), download_asset(), find_asset(), get_latest_release() (+18 more)

### Community 1 - "test_database.py"
Cohesion: 0.15
Nodes (12): 10. Actualización de este documento, 11. Uso de este documento, 1. Propósito y alcance, 2. Tono y estilo, 3. Prohibición de emojis, 4. Versionado (SemVer), 5. Releases y CHANGELOG, 6. Conventional Commits (+4 more)

### Community 2 - "get_connection"
Cohesion: 0.17
Nodes (12): add_cliente(), add_servicio(), add_vehiculo(), anular_compra(), get_clientes(), get_connection(), get_orden_detalle(), get_ordenes() (+4 more)

### Community 3 - "database.py"
Cohesion: 0.29
Nodes (6): After Code Changes, AGENTS.md - Lubricentro Project, Auto-load Graphify Context on Session Start, Project Conventions, Project Structure, Quick Queries During Session

### Community 4 - "add_movimiento"
Cohesion: 0.06
Nodes (30): [0.1.0] - 2026-07-16, [0.2.0] - 2026-07-17, [0.2.1] - 2026-07-17, [0.2.2] - 2026-07-17, [0.2.3] - 2026-07-18, [0.2.4] - 2026-07-20, [0.2.5] - 2026-07-21, [0.2.6] - 2026-07-21 (+22 more)

### Community 5 - "get_movimientos"
Cohesion: 0.08
Nodes (38): add_movimiento(), add_orden_detalle(), get_movimientos(), Registra un movimiento de stock y actualiza el stock_actual del producto.     Re, _crear_producto_con_stock(), Helper para crear un producto con categoría, proveedor y stock inicial, Debe devolver una lista vacía cuando no hay movimientos, Debe devolver movimientos ordenados por fecha descendente y aplicar límite (+30 more)

### Community 6 - "_crear_producto_con_stock"
Cohesion: 0.25
Nodes (8): crear_compra(), get_compras(), get_detalle_compra(), Crea una compra a proveedor con múltiples items.     Actualiza stock de cada pro, Obtiene listado de compras con información del proveedor., Obtiene el detalle de una compra con información del producto., Debe crear una compra, actualizar stock y registrar movimientos., test_crear_y_get_compras()

### Community 7 - "tickets.py"
Cohesion: 0.17
Nodes (15): formatear_monto(), generar_factura_a_texto(), generar_factura_b_texto(), generar_factura_c_texto(), generar_ticket_texto(), guardar_comprobante_archivo(), imprimir_comprobante(), metodo_pago_nombre() (+7 more)

### Community 8 - "database.py"
Cohesion: 0.20
Nodes (3): add_orden_servicio(), cleanup_old_backups(), Elimina los backups más antiguos, conservando solo los últimos max_backups.

### Community 11 - "get_venta_completa"
Cohesion: 0.50
Nodes (4): get_venta_completa(), get_venta_detalle(), Obtiene el detalle de una venta., Obtiene venta completa con cabecera y items.

### Community 12 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 13 - "init_db"
Cohesion: 0.67
Nodes (3): init_db(), Apunta database.DB_NAME a un archivo temporal y lo inicializa limpio., temp_db()

### Community 14 - "crear_ajuste_stock"
Cohesion: 0.10
Nodes (50): add_categoria(), add_producto(), add_proveedor(), backup_db(), crear_venta(), get_categorias(), get_productos(), get_proveedores() (+42 more)

### Community 33 - "get_compras"
Cohesion: 0.50
Nodes (3): Notas de uso, Pendientes para v0.2.5, TODO.md - Lubricentro Project

## Knowledge Gaps
- **41 isolated node(s):** `Corregido`, `Cambiado`, `Agregado`, `Corregido`, `Cambiado` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_connection()` connect `get_connection` to `get_movimientos`, `_crear_producto_con_stock`, `database.py`, `crear_venta`, `get_venta_completa`, `init_db`, `crear_ajuste_stock`, `get_ajustes_stock`, `get_clientes_con_deuda`, `get_cuenta_corriente_cliente`, `get_movimientos_cuenta_corriente`, `get_reporte_ingresos_egresos`, `get_reporte_inventario`, `get_reporte_ventas`, `get_reporte_ventas_detallado`, `get_ventas`, `update_categoria`, `update_proveedor`, `update_producto`, `update_cliente`, `update_vehiculo`, `update_servicio`, `crear_ajuste_stock`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `add_movimiento()` connect `get_movimientos` to `database.py`, `get_connection`, `crear_ajuste_stock`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `get_productos()` connect `crear_ajuste_stock` to `database.py`, `get_connection`, `get_movimientos`, `_crear_producto_con_stock`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **What connects `Corregido`, `Cambiado`, `Agregado` to the rest of the system?**
  _41 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._
- **Should `add_movimiento` be split into smaller, more focused modules?**
  _Cohesion score 0.06451612903225806 - nodes in this community are weakly interconnected._
- **Should `get_movimientos` be split into smaller, more focused modules?**
  _Cohesion score 0.07539118065433854 - nodes in this community are weakly interconnected._