# Graph Report - Lubricentro  (2026-07-30)

## Corpus Check
- 40 files · ~53,143 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 646 nodes · 797 edges · 120 communities (38 shown, 82 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d176fc0e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- updater.py
- test_database.py
- get_connection
- database.py
- add_movimiento
- get_movimientos
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
- test_get_ventas_pendientes_cc_tras_pago_parcial
- crear_compra
- get_cuenta_corriente_cliente
- get_detalle_compra
- get_reporte_ventas
- get_ultimo_numero_comprobante
- get_reporte_ingresos_egresos
- update_cliente
- get_movimientos_cuenta_corriente
- get_reporte_ventas
- get_ventas
- get_ventas_pendientes_cc
- update_producto
- update_vehiculo
- test_add_movimiento_uso_interno
- test_add_movimiento_tipo_invalido
- test_add_movimiento_tipo_nulo
- test_add_movimiento_fecha_personalizada
- get_cuenta_corriente_cliente
- update_servicio
- update_categoria
- get_ultimo_numero_comprobante
- update_producto
- update_vehiculo
- registrar_movimiento_caja
- reactivar_cliente
- update_proveedor
- test_registrar_pago_cc_registra_tipo_movimiento_pago
- test_crear_venta_cuenta_corriente_registra_tipo_venta
- test_get_clientes_con_deuda_incluye_antiguedad
- test_get_movimientos_cuenta_corriente_incluye_tipo_y_metodo
- test_aumentar_precios_proveedor
- test_aumentar_precios_proveedor_proveedor_inexistente
- test_aumentar_precios_proveedor_porcentaje_negativo
- temp_db
- test_aumentar_precios_por_lista_happy_path
- test_aumentar_precios_por_lista_lista_vacia
- test_aumentar_precios_por_lista_porcentaje_negativo
- test_aumentar_precios_por_lista_ids_inexistentes
- test_get_productos_por_proveedor_happy_path
- test_get_productos_por_proveedor_con_busqueda
- test_get_productos_por_proveedor_proveedor_inexistente
- test_get_productos_por_proveedor_sin_busqueda
- test_get_ventas_pendientes_cc
- test_registrar_pago_cc_con_ventas_imputa_pago
- test_registrar_pago_cc_con_ventas_monto_negativo_devuelve_false
- test_reporte_inventario_vacio
- test_reporte_inventario_con_datos
- test_reporte_inventario_excluye_productos_inactivos
- test_crear_venta_con_caja_abierta_registra_ingreso
- test_crear_venta_sin_caja_abierta_no_registra_ingreso
- test_get_precios_para_lista_solo_activos_con_stock
- test_get_precios_para_lista_ordenado_por_proveedor
- test_get_precios_para_lista_incluye_precio_venta
- test_aumentar_precios_por_categoria
- test_aumentar_precios_por_categoria_multiples_productos
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
- test_verificar_login_admin_correcto
- test_verificar_login_password_incorrecta
- test_verificar_login_usuario_inexistente
- test_verificar_login_usuario_inactivo
- test_cambiar_password_actualiza_hash
- test_cambiar_password_usuario_inexistente
- test_registrar_pago_cc_reduce_deuda
- test_registrar_pago_cc_pago_total_saldando
- test_registrar_pago_cc_monto_negativo_devuelve_false
- test_registrar_pago_cc_cliente_inexistente_devuelve_false

## God Nodes (most connected - your core abstractions)
1. `get_connection()` - 62 edges
2. `_crear_producto_con_stock()` - 24 edges
3. `_crear_dependencias()` - 20 edges
4. `Changelog - Lubricentro Winter` - 16 edges
5. `Guía de Firma Digital (Code Signing) para Lubricentro Winter` - 13 edges
6. `Global Constraints` - 13 edges
7. `Convenciones del proyecto — Lubricentro Winter` - 12 edges
8. `Diseño: Correcciones UX en Compras, Ventas e IVA para v0.2.5` - 10 edges
9. `UpdateError` - 9 edges
10. `main()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `abrir_caja()` --calls--> `get_connection()`  [EXTRACTED]
  database.py → database.py  _Bridges community 2 → community 29_
- `add_categoria()` --calls--> `get_connection()`  [EXTRACTED]
  database.py → database.py  _Bridges community 2 → community 22_
- `add_movimiento()` --calls--> `get_connection()`  [EXTRACTED]
  database.py → database.py  _Bridges community 2 → community 9_
- `add_orden_servicio()` --calls--> `get_connection()`  [EXTRACTED]
  database.py → database.py  _Bridges community 2 → community 8_
- `anular_compra()` --calls--> `get_connection()`  [EXTRACTED]
  database.py → database.py  _Bridges community 2 → community 44_

## Import Cycles
- None detected.

## Communities (120 total, 82 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.08
Nodes (37): Exception, apply_update(), check_for_update(), clear_update_dir(), compare_versions(), download_asset(), _extract_zip_safe(), find_asset() (+29 more)

### Community 1 - "test_database.py"
Cohesion: 0.15
Nodes (12): 10. Actualización de este documento, 11. Uso de este documento, 1. Propósito y alcance, 2. Tono y estilo, 3. Prohibición de emojis, 4. Versionado (SemVer), 5. Releases y CHANGELOG, 6. Conventional Commits (+4 more)

### Community 2 - "get_connection"
Cohesion: 0.10
Nodes (20): add_cliente(), add_servicio(), add_vehiculo(), crear_ajuste_stock(), get_ajustes_stock(), get_categorias(), get_connection(), get_movimientos() (+12 more)

### Community 3 - "database.py"
Cohesion: 0.29
Nodes (6): After Code Changes, AGENTS.md - Lubricentro Project, Auto-load Graphify Context on Session Start, Project Conventions, Project Structure, Quick Queries During Session

### Community 4 - "add_movimiento"
Cohesion: 0.33
Nodes (5): [0.1.0] - 2026-07-16, Agregado, Changelog - Lubricentro Winter, Convenciones de commits, Formato de versiones

### Community 5 - "get_movimientos"
Cohesion: 0.04
Nodes (46): _crear_producto_con_stock(), Helper para crear un producto con categoría, proveedor y stock inicial, Debe devolver movimientos ordenados por fecha descendente y aplicar límite, Debe agregar una compra exitosamente y aumentar el stock, Debe agregar una venta exitosamente y disminuir el stock, Debe manejar un ajuste positivo correctamente, Debe manejar un ajuste negativo correctamente, Debe manejar una devolución como entrada de stock (+38 more)

### Community 7 - "tickets.py"
Cohesion: 0.09
Nodes (25): calcular_totales(), imprimir_venta(), Genera e imprime el comprobante de una venta., Calcula subtotal, iva y total segun el tipo de comprobante.     Reglas (alineada, abrir_cajon(), formatear_monto(), generar_factura_a_texto(), generar_factura_b_texto() (+17 more)

### Community 8 - "database.py"
Cohesion: 0.11
Nodes (14): add_orden_servicio(), cleanup_old_backups(), get_categorias_por_proveedor(), get_clientes(), get_clientes_con_deuda(), get_precios_para_lista(), get_proveedores(), get_servicios() (+6 more)

### Community 9 - "crear_venta"
Cohesion: 0.29
Nodes (7): add_movimiento(), add_orden_detalle(), crear_venta(), get_caja_abierta(), Crea una venta completa con items, actualiza stock y registra movimiento.     it, Obtiene la caja actualmente abierta.          Args:         conn: conexión opcio, Registra un movimiento de stock y actualiza el stock_actual del producto.     Re

### Community 11 - "get_venta_completa"
Cohesion: 0.50
Nodes (4): get_venta_completa(), get_venta_detalle(), Obtiene el detalle de una venta., Obtiene venta completa con cabecera y items.

### Community 12 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 13 - "init_db"
Cohesion: 0.29
Nodes (7): [0.4.1] - 2026-07-27, Agregado, Agregado, Cambiado, Corregido, Corregido, Infraestructura

### Community 14 - "crear_ajuste_stock"
Cohesion: 0.33
Nodes (6): [0.3.0] - 2026-07-23, Agregado, Cambiado, Corregido, Infraestructura, Seguridad

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

### Community 20 - "get_reporte_ingresos_egresos"
Cohesion: 0.50
Nodes (4): [0.2.2] - 2026-07-17, Agregado, Cambiado, Corregido

### Community 21 - "get_reporte_inventario"
Cohesion: 0.50
Nodes (4): [0.2.3] - 2026-07-18, Agregado, Cambiado, Corregido

### Community 22 - "get_reporte_ventas"
Cohesion: 0.18
Nodes (10): add_categoria(), add_producto(), add_proveedor(), init_db(), _migrate_legacy_db_location(), Devuelve el directorio de datos de usuario (absoluto) por SO.      Windows: %APP, Calcula DB_NAME y BACKUP_DIR absolutos. Crea el dir si no existe.     Devuelve (, Mueve lubricantro.db (y backups/) desde el directorio del script/app     (legacy (+2 more)

### Community 23 - "get_reporte_ventas_detallado"
Cohesion: 0.33
Nodes (6): cambiar_password(), hash_password(), Genera un hash SHA-256 de la contraseña., Verifica credenciales de usuario.          Devuelve un dict con user_id, nombre,, Actualiza la contraseña de un usuario.          Devuelve True si se actualizó co, verificar_login()

### Community 24 - "get_ventas"
Cohesion: 0.50
Nodes (4): [0.2.4] - 2026-07-20, Agregado, Cambiado, Corregido

### Community 30 - "update_servicio"
Cohesion: 0.08
Nodes (26): _crear_dependencias(), Stock insuficiente debe retornar mensaje especifico, no (None, None)., Factura A: precio_venta ya incluye IVA. Total = subtotal_neto + iva = precio_fin, Ticket: sin IVA, subtotal = total = precio_venta., Producto inactivo debe retornar error especifico., Factura B: sin IVA desglosado., Factura C: sin IVA desglosado., test_add_orden_detalle_cantidad_cero() (+18 more)

### Community 33 - "get_compras"
Cohesion: 0.06
Nodes (32): 1. Manejo de caja (simple), 2. IntegrityError faltantes (rápido), 3. Carteles de éxito/error consistentes, 4. Soft delete de clientes, 5. Validación de fracciones en productos "Entero", Acciones, Archivos a modificar, Archivos a revisar (+24 more)

### Community 34 - "Documentar Código"
Cohesion: 0.22
Nodes (8): Adaptación a otros lenguajes, Buenas prácticas generales, Checklist antes de hacer commit, Con pdoc (más simple), Con Sphinx (recomendado para Python), Documentar Código, Generar documentación automática, Pasos para documentar un módulo (ejemplo en Python)

### Community 36 - "8_Compras.py"
Cohesion: 0.08
Nodes (9): cerrar_sesion(), init_session(), Inicializa flags de sesión si no existen., Limpia el estado de sesión., agrupar_por_proveedor(), generar_pdf(), Genera un PDF de la lista de precios agrupada por proveedor.      Maneja acentos, inject_global_css() (+1 more)

### Community 38 - "Sistema de Gestión para LUBRICENTRO WINTER"
Cohesion: 0.17
Nodes (11): Actualizaciones Remotas, Build del .exe (Windows), Cambiar la versión actual, Configuración en la app, Descripción, Estado del Proyecto, Estructura Técnica, Impresora Térmica (+3 more)

### Community 39 - "Agente de Testing"
Cohesion: 0.40
Nodes (4): Agente de Testing, Flujo de trabajo típico, Idioma, Responsabilidades

### Community 42 - "get_cuenta_corriente_cliente"
Cohesion: 0.50
Nodes (4): [0.2.5] - 2026-07-21, Agregado, Cambiado, Corregido

### Community 43 - "get_detalle_compra"
Cohesion: 0.50
Nodes (4): [0.5.0] - 2026-07-30, Agregado, Corregido, Removido

### Community 49 - "get_reporte_ventas"
Cohesion: 0.67
Nodes (3): [0.2.0] - 2026-07-17, Agregado, Corregido

### Community 52 - "update_producto"
Cohesion: 0.67
Nodes (3): [0.2.1] - 2026-07-17, Agregado, Corregido

### Community 53 - "update_vehiculo"
Cohesion: 0.67
Nodes (3): [0.2.6] - 2026-07-21, Cambiado, Corregido

### Community 54 - "test_add_movimiento_uso_interno"
Cohesion: 0.67
Nodes (3): [0.2.7] - 2026-07-21, Agregado, Corregido

### Community 55 - "test_add_movimiento_tipo_invalido"
Cohesion: 0.67
Nodes (3): [0.4.4] - 2026-07-28, Agregado, Corregido

## Knowledge Gaps
- **142 isolated node(s):** `Agregado`, `Corregido`, `Removido`, `Corregido`, `Agregado` (+137 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **82 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_connection()` connect `get_connection` to `database.py`, `crear_venta`, `get_venta_completa`, `get_movimientos_cuenta_corriente`, `get_reporte_ventas`, `get_reporte_ventas_detallado`, `update_categoria`, `update_proveedor`, `update_producto`, `update_cliente`, `update_vehiculo`, `7_Ventas.py`, `anular_compra`, `get_reporte_ventas`, `get_ultimo_numero_comprobante`, `get_reporte_ingresos_egresos`, `update_cliente`, `get_movimientos_cuenta_corriente`, `get_ventas`, `get_ventas_pendientes_cc`, `test_add_movimiento_tipo_nulo`, `test_add_movimiento_fecha_personalizada`, `get_cuenta_corriente_cliente`, `update_servicio`, `update_categoria`, `get_ultimo_numero_comprobante`, `update_producto`, `update_vehiculo`, `registrar_movimiento_caja`, `reactivar_cliente`, `update_proveedor`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `Changelog - Lubricentro Winter` connect `add_movimiento` to `get_cuenta_corriente_cliente`, `get_detalle_compra`, `init_db`, `crear_ajuste_stock`, `get_reporte_ventas`, `update_producto`, `get_reporte_inventario`, `get_reporte_ingresos_egresos`, `update_vehiculo`, `get_ventas`, `test_add_movimiento_uso_interno`, `test_add_movimiento_tipo_invalido`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **What connects `Agregado`, `Corregido`, `Removido` to the rest of the system?**
  _142 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07823613086770982 - nodes in this community are weakly interconnected._
- **Should `get_connection` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `get_movimientos` be split into smaller, more focused modules?**
  _Cohesion score 0.043478260869565216 - nodes in this community are weakly interconnected._
- **Should `_crear_producto_con_stock` be split into smaller, more focused modules?**
  _Cohesion score 0.043478260869565216 - nodes in this community are weakly interconnected._