# Graph Report - Lubricentro  (2026-07-17)

## Corpus Check
- 20 files · ~10,684 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 146 nodes · 276 edges · 9 communities (8 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4eca91e9`
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
- graphify.js
- test_add_movimiento_devolucion

## God Nodes (most connected - your core abstractions)
1. `get_connection()` - 26 edges
2. `_crear_producto_con_stock()` - 21 edges
3. `get_productos()` - 20 edges
4. `add_movimiento()` - 19 edges
5. `_crear_dependencias()` - 13 edges
6. `add_producto()` - 11 edges
7. `get_movimientos()` - 8 edges
8. `get_categorias()` - 8 edges
9. `add_categoria()` - 8 edges
10. `get_proveedores()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `_crear_producto_con_stock()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_get_productos_excluye_inactivos()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_init_db_crea_diez_tablas()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_add_movimiento_cantidad_nula()` --calls--> `add_movimiento()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_add_movimiento_tipo_nulo()` --calls--> `add_movimiento()`  [EXTRACTED]
  tests/test_database.py → database.py

## Import Cycles
- None detected.

## Communities (9 total, 1 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.11
Nodes (24): Exception, apply_update(), check_for_update(), clear_update_dir(), compare_versions(), download_asset(), find_asset(), get_latest_release() (+16 more)

### Community 1 - "test_database.py"
Cohesion: 0.26
Nodes (17): add_producto(), backup_db(), get_productos(), _crear_dependencias(), Debe fallar cuando tipo es None, test_add_movimiento_cantidad_nula(), test_add_movimiento_tipo_nulo(), test_add_producto_codigo_barras_duplicado() (+9 more)

### Community 2 - "get_connection"
Cohesion: 0.09
Nodes (22): add_cliente(), add_orden_servicio(), add_servicio(), add_vehiculo(), cleanup_old_backups(), get_clientes(), get_connection(), get_orden_detalle() (+14 more)

### Community 3 - "database.py"
Cohesion: 0.33
Nodes (5): After Code Changes, AGENTS.md - Lubricentro Project, Auto-load Graphify Context on Session Start, Project Structure, Quick Queries During Session

### Community 4 - "add_movimiento"
Cohesion: 0.12
Nodes (15): [0.1.0] - 2026-07-16, [0.2.0] - 2026-07-17, [0.2.1] - 2026-07-17, [0.2.2] - 2026-07-17, Agregado, Agregado, Agregado, Agregado (+7 more)

### Community 5 - "get_movimientos"
Cohesion: 0.09
Nodes (33): add_movimiento(), add_orden_detalle(), get_movimientos(), Registra un movimiento de stock y actualiza el stock_actual del producto.     Re, _crear_producto_con_stock(), Helper para crear un producto con categoría, proveedor y stock inicial, Debe devolver una lista vacía cuando no hay movimientos, Debe devolver movimientos ordenados por fecha descendente y aplicar límite (+25 more)

### Community 6 - "_crear_producto_con_stock"
Cohesion: 0.53
Nodes (6): add_proveedor(), get_proveedores(), test_add_proveedor_condicion_pago_invalida(), test_add_proveedor_condicion_pago_valida(), test_add_proveedor_null_condicion(), test_add_y_get_proveedores()

### Community 17 - "test_add_movimiento_devolucion"
Cohesion: 0.53
Nodes (6): add_categoria(), get_categorias(), test_add_categoria_duplicado_devuelve_false(), test_add_categoria_null(), test_add_categoria_string_vacio(), test_add_y_get_categorias()

## Knowledge Gaps
- **14 isolated node(s):** `Agregado`, `Corregido`, `Cambiado`, `Agregado`, `Corregido` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `add_movimiento()` connect `get_movimientos` to `test_database.py`, `get_connection`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `get_connection()` connect `get_connection` to `test_add_movimiento_devolucion`, `get_movimientos`, `test_database.py`, `_crear_producto_con_stock`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `get_productos()` connect `test_database.py` to `get_connection`, `get_movimientos`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **What connects `Agregado`, `Corregido`, `Cambiado` to the rest of the system?**
  _14 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1076923076923077 - nodes in this community are weakly interconnected._
- **Should `get_connection` be split into smaller, more focused modules?**
  _Cohesion score 0.08870967741935484 - nodes in this community are weakly interconnected._
- **Should `add_movimiento` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._