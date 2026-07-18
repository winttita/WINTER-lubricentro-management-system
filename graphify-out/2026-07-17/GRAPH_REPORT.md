# Graph Report - Lubricentro  (2026-07-17)

## Corpus Check
- 19 files · ~8,755 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 130 nodes · 261 edges · 13 communities (8 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4883424f`
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
- add_categoria
- add_proveedor
- init_db
- graphify.js
- test_add_movimiento_devolucion
- test_add_movimiento_tipo_invalido

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
- `test_add_movimiento_compra_exitosa()` --calls--> `get_movimientos()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_add_movimiento_venta_exitosa()` --calls--> `get_movimientos()`  [EXTRACTED]
  tests/test_database.py → database.py

## Import Cycles
- None detected.

## Communities (13 total, 5 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.11
Nodes (24): Exception, apply_update(), check_for_update(), clear_update_dir(), compare_versions(), download_asset(), find_asset(), get_latest_release() (+16 more)

### Community 1 - "test_database.py"
Cohesion: 0.23
Nodes (19): add_producto(), add_proveedor(), backup_db(), get_proveedores(), _crear_dependencias(), test_add_producto_codigo_barras_duplicado(), test_add_producto_codigo_duplicado(), test_add_producto_fraccionable() (+11 more)

### Community 2 - "get_connection"
Cohesion: 0.09
Nodes (22): add_cliente(), add_orden_servicio(), add_servicio(), add_vehiculo(), cleanup_old_backups(), get_clientes(), get_connection(), get_orden_detalle() (+14 more)

### Community 3 - "database.py"
Cohesion: 0.33
Nodes (5): After Code Changes, AGENTS.md - Lubricentro Project, Auto-load Graphify Context on Session Start, Project Structure, Quick Queries During Session

### Community 4 - "add_movimiento"
Cohesion: 0.22
Nodes (10): add_movimiento(), add_orden_detalle(), Registra un movimiento de stock y actualiza el stock_actual del producto.     Re, Debe fallar cuando el producto_id no existe, Debe fallar cuando producto_id es None, Debe fallar cuando tipo es None, test_add_movimiento_cantidad_nula(), test_add_movimiento_producto_id_nulo() (+2 more)

### Community 5 - "get_movimientos"
Cohesion: 0.22
Nodes (9): get_movimientos(), Debe devolver una lista vacía cuando no hay movimientos, Debe devolver movimientos ordenados por fecha descendente y aplicar límite, Debe fallar cuando no hay suficiente stock para una salida, Debe aceptar una fecha personalizada, test_add_movimiento_fecha_personalizada(), test_add_movimiento_stock_insuficiente(), test_get_movimientos_con_datos() (+1 more)

### Community 6 - "_crear_producto_con_stock"
Cohesion: 0.29
Nodes (8): get_productos(), Debe manejar un ajuste positivo correctamente, Debe manejar el uso interno como salida de stock, Debe fallar cuando la cantidad no es válida, test_add_movimiento_ajuste_negativo(), test_add_movimiento_ajuste_positivo(), test_add_movimiento_cantidad_invalida(), test_add_movimiento_uso_interno()

### Community 17 - "test_add_movimiento_devolucion"
Cohesion: 0.39
Nodes (8): add_categoria(), get_categorias(), _crear_producto_con_stock(), Helper para crear un producto con categoría, proveedor y stock inicial, test_add_categoria_duplicado_devuelve_false(), test_add_categoria_null(), test_add_categoria_string_vacio(), test_add_y_get_categorias()

## Knowledge Gaps
- **4 isolated node(s):** `Auto-load Graphify Context on Session Start`, `After Code Changes`, `Quick Queries During Session`, `Project Structure`
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `add_movimiento()` connect `add_movimiento` to `get_connection`, `get_movimientos`, `_crear_producto_con_stock`, `add_categoria`, `add_proveedor`, `init_db`, `test_add_movimiento_tipo_invalido`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `get_connection()` connect `get_connection` to `test_database.py`, `add_movimiento`, `get_movimientos`, `_crear_producto_con_stock`, `test_add_movimiento_devolucion`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `get_productos()` connect `_crear_producto_con_stock` to `test_database.py`, `get_connection`, `add_movimiento`, `get_movimientos`, `add_categoria`, `add_proveedor`, `init_db`, `test_add_movimiento_tipo_invalido`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **What connects `Auto-load Graphify Context on Session Start`, `After Code Changes`, `Quick Queries During Session` to the rest of the system?**
  _4 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1076923076923077 - nodes in this community are weakly interconnected._
- **Should `get_connection` be split into smaller, more focused modules?**
  _Cohesion score 0.08870967741935484 - nodes in this community are weakly interconnected._