# Graph Report - Lubricentro  (2026-07-23)

## Corpus Check
- 29 files · ~34,697 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 467 nodes · 840 edges · 40 communities (27 shown, 13 thin omitted)
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
- 8_Compras.py
- Sistema de Gestión para LUBRICENTRO WINTER
- Agente de Testing
- backup_db

## God Nodes (most connected - your core abstractions)
1. `get_connection()` - 69 edges
2. `add_producto()` - 34 edges
3. `_crear_producto_con_stock()` - 30 edges
4. `get_productos()` - 28 edges
5. `add_proveedor()` - 26 edges
6. `add_categoria()` - 25 edges
7. `crear_venta()` - 25 edges
8. `add_movimiento()` - 23 edges
9. `_crear_dependencias()` - 19 edges
10. `add_cliente()` - 14 edges

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

## Communities (40 total, 13 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.08
Nodes (35): Exception, apply_update(), check_for_update(), clear_update_dir(), compare_versions(), download_asset(), _extract_zip_safe(), find_asset() (+27 more)

### Community 1 - "test_database.py"
Cohesion: 0.15
Nodes (12): 10. Actualización de este documento, 11. Uso de este documento, 1. Propósito y alcance, 2. Tono y estilo, 3. Prohibición de emojis, 4. Versionado (SemVer), 5. Releases y CHANGELOG, 6. Conventional Commits (+4 more)

### Community 2 - "get_connection"
Cohesion: 0.11
Nodes (19): crear_ajuste_stock(), get_clientes(), get_connection(), get_ordenes(), get_reporte_inventario(), get_reporte_ventas(), get_servicios(), Actualiza los datos de un servicio existente. (+11 more)

### Community 3 - "database.py"
Cohesion: 0.29
Nodes (6): After Code Changes, AGENTS.md - Lubricentro Project, Auto-load Graphify Context on Session Start, Project Conventions, Project Structure, Quick Queries During Session

### Community 4 - "add_movimiento"
Cohesion: 0.05
Nodes (39): [0.1.0] - 2026-07-16, [0.2.0] - 2026-07-17, [0.2.1] - 2026-07-17, [0.2.2] - 2026-07-17, [0.2.3] - 2026-07-18, [0.2.4] - 2026-07-20, [0.2.5] - 2026-07-21, [0.2.6] - 2026-07-21 (+31 more)

### Community 5 - "get_movimientos"
Cohesion: 0.05
Nodes (82): add_movimiento(), add_producto(), crear_venta(), get_movimientos(), get_productos(), Crea una venta completa con items, actualiza stock y registra movimiento.     it, Registra un movimiento de stock y actualiza el stock_actual del producto.     Re, _crear_dependencias() (+74 more)

### Community 7 - "tickets.py"
Cohesion: 0.17
Nodes (15): formatear_monto(), generar_factura_a_texto(), generar_factura_b_texto(), generar_factura_c_texto(), generar_ticket_texto(), guardar_comprobante_archivo(), imprimir_comprobante(), metodo_pago_nombre() (+7 more)

### Community 8 - "database.py"
Cohesion: 0.12
Nodes (16): add_orden_detalle(), add_orden_servicio(), add_servicio(), add_vehiculo(), cleanup_old_backups(), get_cuenta_corriente_cliente(), get_detalle_compra(), get_orden_detalle() (+8 more)

### Community 11 - "get_venta_completa"
Cohesion: 0.50
Nodes (4): get_venta_completa(), get_venta_detalle(), Obtiene el detalle de una venta., Obtiene venta completa con cabecera y items.

### Community 12 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 13 - "init_db"
Cohesion: 0.20
Nodes (9): hash_password(), init_db(), Genera un hash SHA-256 de la contraseña., Apunta database.DB_NAME a un archivo temporal y lo inicializa limpio., hash_password debe devolver el mismo hash para la misma entrada., hash_password deve devolver hashes distintos para passwords distintas., temp_db(), test_hash_password_diferente_para_distintas_entradas() (+1 more)

### Community 14 - "crear_ajuste_stock"
Cohesion: 0.10
Nodes (36): add_categoria(), add_proveedor(), anular_compra(), crear_compra(), get_categorias(), get_proveedores(), Crea una compra a proveedor con múltiples items.     Actualiza stock de cada pro, Anula una compra revirtiendo el stock de cada producto.     Retorna True si se a (+28 more)

### Community 15 - "get_ajustes_stock"
Cohesion: 0.13
Nodes (14): Correcciones UX Compras, Ventas e IVA v0.2.5 - Implementation Plan, Global Constraints, Task 10: Actualizar APP_VERSION en updater.py y crear release v0.2.5, Task 11: Verificación final y commit final, Task 1: Tests nuevos para database.py - crear_venta, Task 2: Actualizar firma y logica de crear_venta en database.py, Task 3: Implementar UI dinamica en pages/8_Compras.py, Task 4: Implementar busqueda lazy, vista previa y carrito en pages/7_Ventas.py (+6 more)

### Community 17 - "Diseño: Correcciones UX en Compras, Ventas e IVA para v0.2.5"
Cohesion: 0.13
Nodes (14): 1. Contexto y motivacion, 2. Alcance, 3. Decisiones confirmadas con el usuario, 4.1 Modulo de Compras - UI dinamica, 4.2 Modulo de Ventas - Busqueda, vista previa y cantidades, 4.3 Manejo de IVA - Factura A con precio IVA incluido, 4.4 Validacion de stock y mensajes de error especificos, 4. Diseno por componente (+6 more)

### Community 18 - "get_cuenta_corriente_cliente"
Cohesion: 0.09
Nodes (21): 1. Obtener el Certificado, 2. Configurar Secrets en GitHub, 3. Build Local con Firma (Windows), 4. Build en GitHub Actions (CI/CD), 5. Configuración del Launcher (`--uac-admin`), 6. Troubleshooting Común, 6. Verificación Manual, 7. Renovación Anual (+13 more)

### Community 21 - "get_reporte_inventario"
Cohesion: 0.12
Nodes (21): add_cliente(), Registra un pago (abono) de cuenta corriente.          Inserta un movimiento con, Registra un pago de cuenta corriente imputándolo a ventas específicas., registrar_pago_cc(), registrar_pago_cc_con_ventas(), registrar_pago_cc debe devolver False si el cliente no existe., El movimiento de pago debe tener tipo_movimiento='pago'., get_movimientos_cuenta_corriente debe incluir tipo_movimiento y metodo_pago. (+13 more)

### Community 22 - "get_reporte_ventas"
Cohesion: 0.20
Nodes (10): Verifica credenciales de usuario.          Devuelve un dict con user_id, nombre,, verificar_login(), verificar_login debe devolver info del usuario admin cuando las credenciales son, verificar_login deve devolver None cuando la contraseña es incorrecta., verificar_login deve devolver None cuando el usuario no existe., verificar_login deve devolver None cuando el usuario está inactivo., test_verificar_login_admin_correcto(), test_verificar_login_password_incorrecta() (+2 more)

### Community 25 - "update_categoria"
Cohesion: 0.33
Nodes (6): aumentar_precios_proveedor(), Aumenta el precio_venta de todos los productos de un proveedor en un porcentaje, aumentar_precios_proveedor debe devolver False si el proveedor no existe., aumentar_precios_proveedor no debe aceptar porcentaje negativo., test_aumentar_precios_proveedor_porcentaje_negativo(), test_aumentar_precios_proveedor_proveedor_inexistente()

### Community 28 - "update_cliente"
Cohesion: 0.33
Nodes (6): cambiar_password(), Actualiza la contraseña de un usuario.          Devuelve True si se actualizó co, cambiar_password debe actualizar el password_hash en la BD., cambiar_password debe devolver False si el usuario no existe., test_cambiar_password_actualiza_hash(), test_cambiar_password_usuario_inexistente()

### Community 33 - "get_compras"
Cohesion: 0.50
Nodes (3): Notas de uso, Pendientes para v0.2.7, TODO.md - Lubricentro Project

### Community 34 - "Documentar Código"
Cohesion: 0.22
Nodes (8): Adaptación a otros lenguajes, Buenas prácticas generales, Checklist antes de hacer commit, Con pdoc (más simple), Con Sphinx (recomendado para Python), Documentar Código, Generar documentación automática, Pasos para documentar un módulo (ejemplo en Python)

### Community 36 - "8_Compras.py"
Cohesion: 0.10
Nodes (10): cerrar_sesion(), init_session(), Inicializa flags de sesión si no existen., Limpia el estado de sesión., calcular_totales(), imprimir_venta(), Genera e imprime el comprobante de una venta., Calcula subtotal, iva y total segun el tipo de comprobante.     Reglas (alineada (+2 more)

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
- **104 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `Responsabilidades`, `Flujo de trabajo típico`, `Idioma` (+99 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_connection()` connect `get_connection` to `get_movimientos`, `_crear_producto_con_stock`, `database.py`, `crear_venta`, `get_venta_completa`, `init_db`, `crear_ajuste_stock`, `get_clientes_con_deuda`, `get_movimientos_cuenta_corriente`, `get_reporte_ingresos_egresos`, `get_reporte_inventario`, `get_reporte_ventas`, `get_reporte_ventas_detallado`, `get_ventas`, `update_categoria`, `update_proveedor`, `update_producto`, `update_cliente`, `update_vehiculo`, `update_servicio`, `7_Ventas.py`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `crear_venta()` connect `get_movimientos` to `database.py`, `get_connection`, `get_reporte_inventario`, `crear_ajuste_stock`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `add_movimiento()` connect `get_movimientos` to `database.py`, `get_connection`, `init_db`, `crear_ajuste_stock`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **What connects `$schema`, `.opencode/plugins/graphify.js`, `Responsabilidades` to the rest of the system?**
  _104 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08253968253968254 - nodes in this community are weakly interconnected._
- **Should `get_connection` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `add_movimiento` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._