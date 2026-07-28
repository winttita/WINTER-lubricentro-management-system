# Graph Report - Lubricentro  (2026-07-27)

## Corpus Check
- 32 files · ~38,272 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 502 nodes · 644 edges · 81 communities (25 shown, 56 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fa417194`
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
- anular_compra
- Sistema de Gestión para LUBRICENTRO WINTER
- Agente de Testing
- backup_db
- crear_compra
- get_cuenta_corriente_cliente
- get_detalle_compra
- get_reporte_ventas
- update_servicio
- registrar_pago_cc_con_ventas
- test_registrar_pago_cc_cliente_inexistente_devuelve_false
- test_registrar_pago_cc_registra_tipo_movimiento_pago
- test_crear_venta_cuenta_corriente_registra_tipo_venta
- test_get_clientes_con_deuda_incluye_antiguedad
- test_get_movimientos_cuenta_corriente_incluye_tipo_y_metodo
- test_aumentar_precios_proveedor_proveedor_inexistente
- temp_db
- test_aumentar_precios_proveedor_porcentaje_negativo
- test_get_ventas_pendientes_cc_tras_pago_parcial
- test_registrar_pago_cc_con_ventas_imputa_pago
- test_registrar_pago_cc_con_ventas_monto_negativo_devuelve_false
- test_reporte_inventario_con_datos
- test_reporte_inventario_excluye_productos_inactivos
- test_get_movimientos_sin_movimientos
- test_add_movimiento_producto_inexistente
- test_add_movimiento_producto_id_nulo
- test_add_producto_con_stock_inicial
- test_add_producto_sin_stock_inicial
- test_crear_ajuste_stock_con_movimiento
- test_crear_y_get_compras
- test_anular_compra
- test_crear_venta_items_vacios_retorna_error
- test_init_db_admin_no_password_vacio
- test_get_connection_tiene_busy_timeout
- test_hash_password_es_deterministico
- test_hash_password_diferente_para_distintas_entradas
- test_init_db_crea_usuario_admin_por_defecto
- test_verificar_login_password_incorrecta
- test_verificar_login_usuario_inexistente
- test_verificar_login_usuario_inactivo
- test_cambiar_password_usuario_inexistente
- test_registrar_pago_cc_reduce_deuda
- test_registrar_pago_cc_pago_total_saldando
- test_registrar_pago_cc_monto_negativo_devuelve_false

## God Nodes (most connected - your core abstractions)
1. `get_connection()` - 51 edges
2. `_crear_producto_con_stock()` - 24 edges
3. `_crear_dependencias()` - 15 edges
4. `Changelog - Lubricentro Winter` - 14 edges
5. `Guía de Firma Digital (Code Signing) para Lubricentro Winter` - 13 edges
6. `Global Constraints` - 13 edges
7. `Convenciones del proyecto — Lubricentro Winter` - 12 edges
8. `inject_global_css()` - 10 edges
9. `Diseño: Correcciones UX en Compras, Ventas e IVA para v0.2.5` - 10 edges
10. `main()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `add_servicio()` --calls--> `get_connection()`  [EXTRACTED]
  database.py → database.py  _Bridges community 8 → community 2_
- `anular_compra()` --calls--> `get_connection()`  [EXTRACTED]
  database.py → database.py  _Bridges community 8 → community 37_
- `aumentar_precios_proveedor()` --calls--> `get_connection()`  [EXTRACTED]
  database.py → database.py  _Bridges community 8 → community 25_
- `cambiar_password()` --calls--> `get_connection()`  [EXTRACTED]
  database.py → database.py  _Bridges community 8 → community 13_
- `crear_compra()` --calls--> `get_connection()`  [EXTRACTED]
  database.py → database.py  _Bridges community 8 → community 41_

## Import Cycles
- None detected.

## Communities (81 total, 56 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.07
Nodes (41): cerrar_sesion(), init_session(), Inicializa flags de sesión si no existen., Limpia el estado de sesión., Exception, apply_update(), check_for_update(), clear_update_dir() (+33 more)

### Community 1 - "test_database.py"
Cohesion: 0.15
Nodes (12): 10. Actualización de este documento, 11. Uso de este documento, 1. Propósito y alcance, 2. Tono y estilo, 3. Prohibición de emojis, 4. Versionado (SemVer), 5. Releases y CHANGELOG, 6. Conventional Commits (+4 more)

### Community 2 - "get_connection"
Cohesion: 0.12
Nodes (15): add_servicio(), add_vehiculo(), cleanup_old_backups(), crear_ajuste_stock(), get_clientes_con_deuda(), get_ordenes(), get_proveedores(), get_vehiculos() (+7 more)

### Community 3 - "database.py"
Cohesion: 0.29
Nodes (6): After Code Changes, AGENTS.md - Lubricentro Project, Auto-load Graphify Context on Session Start, Project Conventions, Project Structure, Quick Queries During Session

### Community 4 - "add_movimiento"
Cohesion: 0.04
Nodes (46): [0.1.0] - 2026-07-16, [0.2.0] - 2026-07-17, [0.2.1] - 2026-07-17, [0.2.2] - 2026-07-17, [0.2.3] - 2026-07-18, [0.2.4] - 2026-07-20, [0.2.5] - 2026-07-21, [0.2.6] - 2026-07-21 (+38 more)

### Community 5 - "get_movimientos"
Cohesion: 0.04
Nodes (46): _crear_producto_con_stock(), Helper para crear un producto con categoría, proveedor y stock inicial, Debe devolver movimientos ordenados por fecha descendente y aplicar límite, Debe agregar una compra exitosamente y aumentar el stock, Debe agregar una venta exitosamente y disminuir el stock, Debe manejar un ajuste positivo correctamente, Debe manejar un ajuste negativo correctamente, Debe manejar una devolución como entrada de stock (+38 more)

### Community 6 - "_crear_producto_con_stock"
Cohesion: 0.33
Nodes (4): get_compras(), Actualiza los datos de un cliente existente., Obtiene listado de compras con información del proveedor., update_cliente()

### Community 7 - "tickets.py"
Cohesion: 0.17
Nodes (15): formatear_monto(), generar_factura_a_texto(), generar_factura_b_texto(), generar_factura_c_texto(), generar_ticket_texto(), guardar_comprobante_archivo(), imprimir_comprobante(), metodo_pago_nombre() (+7 more)

### Community 8 - "database.py"
Cohesion: 0.15
Nodes (17): add_categoria(), add_cliente(), add_movimiento(), add_orden_detalle(), add_orden_servicio(), add_producto(), add_proveedor(), crear_venta() (+9 more)

### Community 11 - "get_venta_completa"
Cohesion: 0.50
Nodes (4): get_venta_completa(), get_venta_detalle(), Obtiene el detalle de una venta., Obtiene venta completa con cabecera y items.

### Community 12 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 13 - "init_db"
Cohesion: 0.15
Nodes (13): cambiar_password(), hash_password(), init_db(), _migrate_legacy_db_location(), Devuelve el directorio de datos de usuario (absoluto) por SO.      Windows: %APP, Calcula DB_NAME y BACKUP_DIR absolutos. Crea el dir si no existe.     Devuelve (, Genera un hash SHA-256 de la contraseña., Verifica credenciales de usuario.          Devuelve un dict con user_id, nombre, (+5 more)

### Community 14 - "crear_ajuste_stock"
Cohesion: 0.11
Nodes (6): aumentar_precios_proveedor debe actualizar precio_venta de productos del proveed, get_ventas_pendientes_cc debe devolver ventas a crédito con saldo pendiente., Cuando no hay productos activos, el reporte de inventario debe estar vacío., test_aumentar_precios_proveedor(), test_get_ventas_pendientes_cc(), test_reporte_inventario_vacio()

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

### Community 30 - "update_servicio"
Cohesion: 0.10
Nodes (21): _crear_dependencias(), Stock insuficiente debe retornar mensaje especifico, no (None, None)., Factura A: precio_venta ya incluye IVA. Total = subtotal_neto + iva = precio_fin, Ticket: sin IVA, subtotal = total = precio_venta., Producto inactivo debe retornar error especifico., Factura B: sin IVA desglosado., Factura C: sin IVA desglosado., test_add_producto_codigo_barras_duplicado() (+13 more)

### Community 33 - "get_compras"
Cohesion: 0.50
Nodes (3): Notas de uso, Pendientes para v0.2.7, TODO.md - Lubricentro Project

### Community 34 - "Documentar Código"
Cohesion: 0.22
Nodes (8): Adaptación a otros lenguajes, Buenas prácticas generales, Checklist antes de hacer commit, Con pdoc (más simple), Con Sphinx (recomendado para Python), Documentar Código, Generar documentación automática, Pasos para documentar un módulo (ejemplo en Python)

### Community 36 - "8_Compras.py"
Cohesion: 0.12
Nodes (6): calcular_totales(), imprimir_venta(), Genera e imprime el comprobante de una venta., Calcula subtotal, iva y total segun el tipo de comprobante.     Reglas (alineada, inject_global_css(), Inyecta CSS para ocultar el mensaje 'Press Enter to submit form' de Streamlit.

### Community 38 - "Sistema de Gestión para LUBRICENTRO WINTER"
Cohesion: 0.22
Nodes (8): Actualizaciones Remotas, Build del .exe (Windows), Cambiar la versión actual, Descripción, Estado del Proyecto, Estructura Técnica, Próximos Pasos, Sistema de Gestión para LUBRICENTRO WINTER

### Community 39 - "Agente de Testing"
Cohesion: 0.40
Nodes (4): Agente de Testing, Flujo de trabajo típico, Idioma, Responsabilidades

## Knowledge Gaps
- **110 isolated node(s):** `Corregido`, `Agregado`, `Corregido`, `Agregado`, `Cambiado` (+105 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **56 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_connection()` connect `database.py` to `get_connection`, `_crear_producto_con_stock`, `crear_venta`, `get_venta_completa`, `init_db`, `get_movimientos_cuenta_corriente`, `get_reporte_ingresos_egresos`, `get_reporte_inventario`, `get_reporte_ventas_detallado`, `get_ventas`, `update_categoria`, `update_proveedor`, `update_producto`, `update_vehiculo`, `7_Ventas.py`, `anular_compra`, `backup_db`, `crear_compra`, `get_cuenta_corriente_cliente`, `get_detalle_compra`, `get_reporte_ventas`, `update_servicio`, `registrar_pago_cc_con_ventas`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **What connects `Corregido`, `Agregado`, `Corregido` to the rest of the system?**
  _110 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06871035940803383 - nodes in this community are weakly interconnected._
- **Should `get_connection` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `add_movimiento` be split into smaller, more focused modules?**
  _Cohesion score 0.0425531914893617 - nodes in this community are weakly interconnected._
- **Should `get_movimientos` be split into smaller, more focused modules?**
  _Cohesion score 0.043478260869565216 - nodes in this community are weakly interconnected._
- **Should `crear_ajuste_stock` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._