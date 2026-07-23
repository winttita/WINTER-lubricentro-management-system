# Graph Report - Lubricentro  (2026-07-22)

## Corpus Check
- 27 files · ~26,358 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 331 nodes · 550 edges · 43 communities (22 shown, 21 thin omitted)
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
- update_producto
- update_cliente
- update_vehiculo
- update_servicio
- get_compras
- Documentar Código
- 7_Ventas.py
- crear_ajuste_stock
- Sistema de Gestión para LUBRICENTRO WINTER
- Agente de Testing
- backup_db
- anular_compra
- get_detalle_compra

## God Nodes (most connected - your core abstractions)
1. `get_connection()` - 53 edges
2. `get_productos()` - 25 edges
3. `add_producto()` - 24 edges
4. `add_movimiento()` - 21 edges
5. `_crear_producto_con_stock()` - 21 edges
6. `_crear_dependencias()` - 19 edges
7. `add_categoria()` - 14 edges
8. `add_proveedor()` - 14 edges
9. `get_categorias()` - 13 edges
10. `get_proveedores()` - 13 edges

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

## Communities (43 total, 21 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.11
Nodes (26): Exception, apply_update(), check_for_update(), clear_update_dir(), compare_versions(), download_asset(), find_asset(), get_latest_release() (+18 more)

### Community 1 - "test_database.py"
Cohesion: 0.15
Nodes (12): 10. Actualización de este documento, 11. Uso de este documento, 1. Propósito y alcance, 2. Tono y estilo, 3. Prohibición de emojis, 4. Versionado (SemVer), 5. Releases y CHANGELOG, 6. Conventional Commits (+4 more)

### Community 2 - "get_connection"
Cohesion: 0.17
Nodes (12): add_cliente(), add_orden_detalle(), add_vehiculo(), get_ajustes_stock(), get_clientes(), get_connection(), get_orden_detalle(), get_ordenes() (+4 more)

### Community 3 - "database.py"
Cohesion: 0.29
Nodes (6): After Code Changes, AGENTS.md - Lubricentro Project, Auto-load Graphify Context on Session Start, Project Conventions, Project Structure, Quick Queries During Session

### Community 4 - "add_movimiento"
Cohesion: 0.06
Nodes (33): [0.1.0] - 2026-07-16, [0.2.0] - 2026-07-17, [0.2.1] - 2026-07-17, [0.2.2] - 2026-07-17, [0.2.3] - 2026-07-18, [0.2.4] - 2026-07-20, [0.2.5] - 2026-07-21, [0.2.6] - 2026-07-21 (+25 more)

### Community 5 - "get_movimientos"
Cohesion: 0.07
Nodes (64): add_movimiento(), add_producto(), crear_venta(), get_movimientos(), get_productos(), Registra un movimiento de stock y actualiza el stock_actual del producto.     Re, Crea una venta completa con items, actualiza stock y registra movimiento.     it, _crear_dependencias() (+56 more)

### Community 7 - "tickets.py"
Cohesion: 0.17
Nodes (15): formatear_monto(), generar_factura_a_texto(), generar_factura_b_texto(), generar_factura_c_texto(), generar_ticket_texto(), guardar_comprobante_archivo(), imprimir_comprobante(), metodo_pago_nombre() (+7 more)

### Community 8 - "database.py"
Cohesion: 0.18
Nodes (4): add_orden_servicio(), add_servicio(), cleanup_old_backups(), Elimina los backups más antiguos, conservando solo los últimos max_backups.

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
Cohesion: 0.15
Nodes (24): add_categoria(), add_proveedor(), crear_compra(), get_categorias(), get_proveedores(), Crea una compra a proveedor con múltiples items.     Actualiza stock de cada pro, Debe crear producto con stock inicial y registrar movimiento., Debe crear producto con stock 0 por defecto y sin movimiento. (+16 more)

### Community 15 - "get_ajustes_stock"
Cohesion: 0.13
Nodes (14): Correcciones UX Compras, Ventas e IVA v0.2.5 - Implementation Plan, Global Constraints, Task 10: Actualizar APP_VERSION en updater.py y crear release v0.2.5, Task 11: Verificación final y commit final, Task 1: Tests nuevos para database.py - crear_venta, Task 2: Actualizar firma y logica de crear_venta en database.py, Task 3: Implementar UI dinamica en pages/8_Compras.py, Task 4: Implementar busqueda lazy, vista previa y carrito en pages/7_Ventas.py (+6 more)

### Community 17 - "Diseño: Correcciones UX en Compras, Ventas e IVA para v0.2.5"
Cohesion: 0.13
Nodes (14): 1. Contexto y motivacion, 2. Alcance, 3. Decisiones confirmadas con el usuario, 4.1 Modulo de Compras - UI dinamica, 4.2 Modulo de Ventas - Busqueda, vista previa y cantidades, 4.3 Manejo de IVA - Factura A con precio IVA incluido, 4.4 Validacion de stock y mensajes de error especificos, 4. Diseno por componente (+6 more)

### Community 33 - "get_compras"
Cohesion: 0.50
Nodes (3): Notas de uso, Pendientes para v0.2.7, TODO.md - Lubricentro Project

### Community 34 - "Documentar Código"
Cohesion: 0.22
Nodes (8): Adaptación a otros lenguajes, Buenas prácticas generales, Checklist antes de hacer commit, Con pdoc (más simple), Con Sphinx (recomendado para Python), Documentar Código, Generar documentación automática, Pasos para documentar un módulo (ejemplo en Python)

### Community 38 - "Sistema de Gestión para LUBRICENTRO WINTER"
Cohesion: 0.22
Nodes (8): Actualizaciones Remotas, Build del .exe (Windows), Cambiar la versión actual, Descripción, Estado del Proyecto, Estructura Técnica, Próximos Pasos, Sistema de Gestión para LUBRICENTRO WINTER

### Community 39 - "Agente de Testing"
Cohesion: 0.40
Nodes (4): Agente de Testing, Flujo de trabajo típico, Idioma, Responsabilidades

### Community 40 - "backup_db"
Cohesion: 0.67
Nodes (3): backup_db(), test_backup_db_crea_archivo(), test_backup_db_no_existe()

## Knowledge Gaps
- **82 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `Responsabilidades`, `Flujo de trabajo típico`, `Idioma` (+77 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_connection()` connect `get_connection` to `get_movimientos`, `_crear_producto_con_stock`, `database.py`, `crear_venta`, `get_venta_completa`, `init_db`, `crear_ajuste_stock`, `get_clientes_con_deuda`, `get_cuenta_corriente_cliente`, `get_movimientos_cuenta_corriente`, `get_reporte_ingresos_egresos`, `get_reporte_inventario`, `get_reporte_ventas`, `get_reporte_ventas_detallado`, `get_ventas`, `update_categoria`, `update_proveedor`, `update_producto`, `update_cliente`, `update_vehiculo`, `update_servicio`, `crear_ajuste_stock`, `anular_compra`, `get_detalle_compra`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `add_movimiento()` connect `get_movimientos` to `database.py`, `get_connection`, `crear_ajuste_stock`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `get_productos()` connect `get_movimientos` to `database.py`, `get_connection`, `crear_ajuste_stock`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **What connects `$schema`, `.opencode/plugins/graphify.js`, `Responsabilidades` to the rest of the system?**
  _82 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._
- **Should `add_movimiento` be split into smaller, more focused modules?**
  _Cohesion score 0.058823529411764705 - nodes in this community are weakly interconnected._
- **Should `get_movimientos` be split into smaller, more focused modules?**
  _Cohesion score 0.07211538461538461 - nodes in this community are weakly interconnected._