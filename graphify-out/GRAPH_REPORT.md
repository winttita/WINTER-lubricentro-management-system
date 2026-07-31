# Graph Report - Lubricentro  (2026-07-30)

## Corpus Check
- 42 files · ~92,397 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 725 nodes · 1325 edges · 85 communities (71 shown, 14 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bd91ab27`
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
- test_aumentar_precios_por_lista_lista_vacia
- test_aumentar_precios_por_lista_ids_inexistentes
- test_get_productos_por_proveedor_proveedor_inexistente
- test_reporte_inventario_vacio
- test_crear_venta_con_caja_abierta_registra_ingreso
- test_get_precios_para_lista_solo_activos_con_stock
- test_add_producto_con_stock_inicial
- test_add_producto_sin_stock_inicial
- test_crear_venta_items_vacios_retorna_error
- test_init_db_admin_no_password_vacio
- test_get_connection_tiene_busy_timeout
- test_init_db_crea_usuario_admin_por_defecto
- test_registrar_pago_cc_cliente_inexistente_devuelve_false
- [0.5.1] - 2026-07-30

## God Nodes (most connected - your core abstractions)
1. `get_connection()` - 87 edges
2. `add_producto()` - 59 edges
3. `add_proveedor()` - 49 edges
4. `add_categoria()` - 46 edges
5. `get_productos()` - 34 edges
6. `_crear_producto_con_stock()` - 30 edges
7. `crear_venta()` - 29 edges
8. `_crear_dependencias()` - 24 edges
9. `add_movimiento()` - 23 edges
10. `add_cliente()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `test_init_db_crea_tablas()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_db_migrates_from_legacy_location()` --calls--> `_resolve_data_paths()`  [EXTRACTED]
  docker/test_updater.py → database.py
- `_crear_producto_con_stock()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_add_producto_con_stock_inicial()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py
- `test_add_producto_sin_stock_inicial()` --calls--> `get_connection()`  [EXTRACTED]
  tests/test_database.py → database.py

## Import Cycles
- None detected.

## Communities (85 total, 14 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.19
Nodes (11): apply_update(), clear_update_dir(), Sistema de actualizaciones automáticas vía GitHub Releases.  Flujo:   1. get_lat, Verifica SHA256 del archivo contra el hash esperado (hex lowercase)., Verifica que un ZIP sea íntegro via CRC (testzip()) sin cargarlo en memoria., Elimina la marca de actualización pendiente. Útil si el checkeo falla., Elimina archivos temporales de descargas anteriores para ahorrar disco., rollback_pending_update() (+3 more)

### Community 1 - "test_database.py"
Cohesion: 0.15
Nodes (12): 10. Actualización de este documento, 11. Uso de este documento, 1. Propósito y alcance, 2. Tono y estilo, 3. Prohibición de emojis, 4. Versionado (SemVer), 5. Releases y CHANGELOG, 6. Conventional Commits (+4 more)

### Community 2 - "get_connection"
Cohesion: 0.08
Nodes (22): crear_ajuste_stock(), get_ajustes_stock(), get_orden_detalle(), get_ordenes(), get_reporte_ventas(), get_reporte_ventas_detallado(), get_ultimo_numero_comprobante(), get_ventas() (+14 more)

### Community 3 - "database.py"
Cohesion: 0.29
Nodes (6): After Code Changes, AGENTS.md - Lubricentro Project, Auto-load Graphify Context on Session Start, Project Conventions, Project Structure, Quick Queries During Session

### Community 4 - "add_movimiento"
Cohesion: 0.33
Nodes (5): [0.1.0] - 2026-07-16, Agregado, Changelog - Lubricentro Winter, Convenciones de commits, Formato de versiones

### Community 5 - "get_movimientos"
Cohesion: 0.08
Nodes (37): add_movimiento(), get_movimientos(), Registra un movimiento de stock y actualiza el stock_actual del producto.     Re, _crear_producto_con_stock(), Helper para crear un producto con categoría, proveedor y stock inicial, Debe devolver una lista vacía cuando no hay movimientos, Debe devolver movimientos ordenados por fecha descendente y aplicar límite, Debe agregar una compra exitosamente y aumentar el stock (+29 more)

### Community 6 - "_crear_producto_con_stock"
Cohesion: 0.12
Nodes (22): add_orden_detalle(), add_orden_servicio(), add_vehiculo(), desactivar_cliente(), get_clientes(), get_vehiculos(), Marca un cliente como inactivo (soft delete)., Reactivar un cliente inactivo. (+14 more)

### Community 7 - "tickets.py"
Cohesion: 0.14
Nodes (17): formatear_monto(), generar_factura_a_texto(), generar_factura_b_texto(), generar_factura_c_texto(), generar_ticket_texto(), guardar_comprobante_archivo(), imprimir_comprobante(), metodo_pago_nombre() (+9 more)

### Community 8 - "database.py"
Cohesion: 0.15
Nodes (17): cleanup_old_backups(), init_db(), Elimina los backups más antiguos, conservando solo los últimos max_backups., _count_products(), _make_db_with_products(), Tests del sistema de actualizaciones (updater + preservación de DB).  Corren en, Una DB con 10 productos debe seguir teniendo 10 después de:     1. init_db() col, Si hay una DB legacy en el dir de database.py y la nueva DB no existe,     init_ (+9 more)

### Community 9 - "crear_venta"
Cohesion: 0.16
Nodes (18): abrir_caja(), cerrar_caja(), get_caja_abierta(), Abre una nueva caja.          Args:         saldo_inicial (float): Saldo inicial, Cierra una caja abierta.          Args:         caja_id (int): ID de la caja a c, Obtiene la caja actualmente abierta.          Args:         conn: conexión opcio, Registra un movimiento en caja y actualiza el saldo de la caja.          Args:, registrar_movimiento_caja() (+10 more)

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

### Community 19 - "get_movimientos_cuenta_corriente"
Cohesion: 0.11
Nodes (17): 1. Contexto y motivacion, 2. Alcance, 3. Decisiones confirmadas con el usuario, 4.10 Nueva funcionalidad - Aumento de precios (F01), 4.1 Ventas - Correccion de precio (B04), 4.2 Ventas - Autocompletado de precio (B03), 4.3 Ventas - Carrito vacio y scanner (B02), 4.4 Ventas - Impresora (B01) (+9 more)

### Community 20 - "get_reporte_ingresos_egresos"
Cohesion: 0.50
Nodes (4): [0.2.2] - 2026-07-17, Agregado, Cambiado, Corregido

### Community 21 - "get_reporte_inventario"
Cohesion: 0.50
Nodes (4): [0.2.3] - 2026-07-18, Agregado, Cambiado, Corregido

### Community 22 - "get_reporte_ventas"
Cohesion: 0.33
Nodes (6): _migrate_legacy_db_location(), Devuelve el directorio de datos de usuario (absoluto) por SO.      Windows: %APP, Calcula DB_NAME y BACKUP_DIR absolutos. Crea el dir si no existe.     Devuelve (, Mueve lubricantro.db (y backups/) desde el directorio del script/app     (legacy, _resolve_data_paths(), _user_data_dir()

### Community 23 - "get_reporte_ventas_detallado"
Cohesion: 0.10
Nodes (22): cambiar_password(), hash_password(), Genera un hash SHA-256 de la contraseña., Verifica credenciales de usuario.          Devuelve un dict con user_id, nombre,, Actualiza la contraseña de un usuario.          Devuelve True si se actualizó co, verificar_login(), hash_password debe devolver el mismo hash para la misma entrada., hash_password deve devolver hashes distintos para passwords distintas. (+14 more)

### Community 24 - "get_ventas"
Cohesion: 0.50
Nodes (4): [0.2.4] - 2026-07-20, Agregado, Cambiado, Corregido

### Community 25 - "update_categoria"
Cohesion: 0.33
Nodes (6): aumentar_precios_proveedor(), Aumenta el precio_venta de todos los productos de un proveedor en un porcentaje, aumentar_precios_proveedor debe devolver False si el proveedor no existe., aumentar_precios_proveedor no debe aceptar porcentaje negativo., test_aumentar_precios_proveedor_porcentaje_negativo(), test_aumentar_precios_proveedor_proveedor_inexistente()

### Community 26 - "update_proveedor"
Cohesion: 0.15
Nodes (12): Global Constraints, Release v0.5.0 - Correcciones y mejoras - Plan de Implementacion, Task 10: Verificacion final y release, Task 1: B04 - Corregir precio_venta en Ventas, Task 2: B06 - Migrar BD: eliminar columna codigo_interno, Task 3: B06 - Actualizar indices en UI y tests, Task 4: B05 - Cambiar selectbox a select_slider en Reportes, Task 5: B07 - Carrito vacio en Compras (+4 more)

### Community 27 - "update_producto"
Cohesion: 0.17
Nodes (13): anular_compra(), crear_compra(), Crea una compra a proveedor con múltiples items.     Actualiza stock de cada pro, Anula una compra revirtiendo el stock de cada producto.     Retorna True si se a, crear_compra debe actualizar productos.precio_costo con el precio de compra., crear_compra debe registrar IVA de la compra., anular_compra debe rechazar si el stock resultante sería negativo., anular_compra debe registrar el movimiento como 'devolucion', no 'ajuste'. (+5 more)

### Community 28 - "update_cliente"
Cohesion: 0.18
Nodes (10): Data flow after fix, File Structure, Global Constraints, Self-Review Checklist, Task 1: Refactor updater.py — verify ZIP integrity, standardize path, remove worker, Task 2: Fix update.bat — cleanup on error, .exe backup, extraction fallback, Task 3: Add retry protection to launcher.py, Task 4: Improve app.py feedback (+2 more)

### Community 29 - "update_vehiculo"
Cohesion: 0.22
Nodes (8): Change, Commit, git diff, Notas adicionales, Status: DONE, Summary, Task 1 Report — B04: Corregir precio_venta index en Ventas, Verificación de índices

### Community 30 - "update_servicio"
Cohesion: 0.19
Nodes (21): get_productos(), _crear_dependencias(), Stock insuficiente debe retornar mensaje especifico, no (None, None)., Ticket: sin IVA, subtotal = total = precio_venta., Factura C: sin IVA desglosado., test_add_producto_codigo_barras_duplicado(), test_add_producto_fraccionable(), test_add_producto_nombre_null() (+13 more)

### Community 33 - "get_compras"
Cohesion: 0.06
Nodes (32): 1. Manejo de caja (simple), 2. IntegrityError faltantes (rápido), 3. Carteles de éxito/error consistentes, 4. Soft delete de clientes, 5. Validación de fracciones en productos "Entero", Acciones, Archivos a modificar, Archivos a revisar (+24 more)

### Community 34 - "Documentar Código"
Cohesion: 0.22
Nodes (8): Adaptación a otros lenguajes, Buenas prácticas generales, Checklist antes de hacer commit, Con pdoc (más simple), Con Sphinx (recomendado para Python), Documentar Código, Generar documentación automática, Pasos para documentar un módulo (ejemplo en Python)

### Community 35 - "7_Ventas.py"
Cohesion: 0.33
Nodes (6): get_reporte_inventario(), Reporte de inventario actual: productos con stock y valorizacion., Verifica que get_reporte_inventario devuelva datos correctos con valorización., Productos desactivados (activo=0) no deben aparecer en el reporte., test_reporte_inventario_con_datos(), test_reporte_inventario_excluye_productos_inactivos()

### Community 37 - "anular_compra"
Cohesion: 0.25
Nodes (8): El CI sube un asset llamado LubricentroWinter.zip (corregido en v0.3.0).     fin, Sanity: si el CI usara LubricentroWinter_v0.3.0.zip (viejo nombre),     find_ass, test_find_asset_matches_ci_name(), test_find_asset_rejects_versioned_name(), find_asset(), find_asset_with_checksum(), Busca dentro de los assets de una release aquel cuyo nombre coincide     exactam, Igual que find_asset pero verifica el checksum SHA256 del asset si se provee.

### Community 38 - "Sistema de Gestión para LUBRICENTRO WINTER"
Cohesion: 0.15
Nodes (12): Actualizaciones Remotas, Build del .exe (Windows), Cambiar la versión actual, Configuración en la app, Descripción, Estado del Proyecto, Estructura Técnica, Impresora Térmica (+4 more)

### Community 39 - "Agente de Testing"
Cohesion: 0.40
Nodes (4): Agente de Testing, Flujo de trabajo típico, Idioma, Responsabilidades

### Community 40 - "test_get_ventas_pendientes_cc_tras_pago_parcial"
Cohesion: 0.17
Nodes (12): get_ventas_pendientes_cc(), Obtiene las ventas a cuenta corriente con el saldo pendiente de cada una., Registra un pago de cuenta corriente imputándolo a ventas específicas., registrar_pago_cc_con_ventas(), get_ventas_pendientes_cc debe devolver ventas a crédito con saldo pendiente., get_ventas_pendientes_cc debe reflejar pagos parciales aplicados a una venta., registrar_pago_cc_con_ventas debe imputar el pago a las ventas indicadas., registrar_pago_cc_con_ventas no debe aceptar monto negativo. (+4 more)

### Community 42 - "get_cuenta_corriente_cliente"
Cohesion: 0.50
Nodes (4): [0.2.5] - 2026-07-21, Agregado, Cambiado, Corregido

### Community 43 - "get_detalle_compra"
Cohesion: 0.50
Nodes (4): [0.5.0] - 2026-07-30, Agregado, Corregido, Removido

### Community 44 - "get_reporte_ventas"
Cohesion: 0.25
Nodes (8): Exception, download_asset(), Sanitiza un nombre de archivo para evitar path traversal.     Rechaza nombres co, Sanitiza un nombre de archivo para prevenir path traversal., Descarga un asset a dest_dir y devuelve la ruta al archivo descargado.      `pro, Error de red o de parseo durante el checkeo de actualizaciones., _sanitize_filename(), UpdateError

### Community 45 - "get_ultimo_numero_comprobante"
Cohesion: 0.22
Nodes (13): add_producto(), aumentar_precios_por_categoria(), Aumenta el precio_venta de los productos de un proveedor filtrados por categoría, aumentar_precios_proveedor debe actualizar precio_venta de productos del proveed, Solo los productos del proveedor Y categoria especificados deben actualizarse., Si el proveedor tiene varios productos en la categoria, todos se actualizan., test_aumentar_precios_por_categoria(), test_aumentar_precios_por_categoria_categoria_sin_productos() (+5 more)

### Community 46 - "get_reporte_ingresos_egresos"
Cohesion: 0.50
Nodes (4): get_reporte_ingresos_egresos(), Reporte de ingresos vs egresos.     Ingresos = total FROM ventas (incluye IVA) +, El reporte de egresos no debe contar 'Stock inicial' como egreso real., test_get_reporte_ingresos_egresos_no_cuenta_stock_inicial()

### Community 47 - "update_cliente"
Cohesion: 0.33
Nodes (4): cerrar_sesion(), init_session(), Inicializa flags de sesión si no existen., Limpia el estado de sesión.

### Community 48 - "get_movimientos_cuenta_corriente"
Cohesion: 0.33
Nodes (6): check_for_update(), get_latest_release(), _main(), Consulta la API de GitHub y devuelve el JSON de la última release publicada., Chequea si hay una actualización disponible.      Devuelve un dict con la info d, Permite ejecutar `python updater.py` desde la terminal para checkear.

### Community 49 - "get_reporte_ventas"
Cohesion: 0.67
Nodes (3): [0.2.0] - 2026-07-17, Agregado, Corregido

### Community 50 - "get_ventas"
Cohesion: 0.40
Nodes (5): add_servicio(), get_servicios(), test_add_servicio_nombre_vacio(), test_add_servicio_precio_invalido(), test_add_servicio_precio_negativo()

### Community 51 - "get_ventas_pendientes_cc"
Cohesion: 0.40
Nodes (5): get_categorias_por_proveedor(), Devuelve las categorías que tienen productos activos para un proveedor dado., test_get_categorias_por_proveedor(), test_get_categorias_por_proveedor_proveedor_inexistente(), test_get_categorias_por_proveedor_sin_productos()

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

### Community 56 - "test_add_movimiento_tipo_nulo"
Cohesion: 0.33
Nodes (6): aumentar_precios_por_lista(), Aumenta precio_venta de productos especificos.      Args:         producto_ids:, aumentar_precios_por_lista debe actualizar el precio de los productos indicados., aumentar_precios_por_lista con porcentaje negativo debe devolver 0., test_aumentar_precios_por_lista_happy_path(), test_aumentar_precios_por_lista_porcentaje_negativo()

### Community 57 - "test_add_movimiento_fecha_personalizada"
Cohesion: 0.40
Nodes (5): test_compare_versions_basic(), compare_versions(), _normalize_version(), Convierte un string de versión semver (con o sin 'v' inicial) en una tupla     d, Compara dos versiones semver y devuelve:       - "newer" si latest > current

### Community 58 - "get_cuenta_corriente_cliente"
Cohesion: 0.25
Nodes (8): get_productos_por_proveedor(), Devuelve productos activos de un proveedor, opcionalmente filtrados.      Args:, get_productos_por_proveedor debe devolver solo los productos del proveedor indic, get_productos_por_proveedor con busqueda debe filtrar por nombre., get_productos_por_proveedor sin busqueda debe devolver todos los productos del p, test_get_productos_por_proveedor_con_busqueda(), test_get_productos_por_proveedor_happy_path(), test_get_productos_por_proveedor_sin_busqueda()

### Community 60 - "update_categoria"
Cohesion: 0.40
Nodes (4): calcular_totales(), imprimir_venta(), Genera e imprime el comprobante de una venta., Calcula subtotal, iva y total segun el tipo de comprobante.     Reglas (alineada

### Community 61 - "get_ultimo_numero_comprobante"
Cohesion: 0.50
Nodes (4): _extract_zip_safe debe rechazar zips con entradas absolutas o con .., test_extract_zip_safe_rejects_path_traversal(), _extract_zip_safe(), Extrae un ZIP validando cada entrada contra path traversal.     Lanza UpdateErro

### Community 62 - "update_producto"
Cohesion: 0.50
Nodes (3): Global Constraints, Refactor UX de Compras (fila inicial + preview producto) Implementation Plan, Task 1: Refactor `pages/8_Compras.py` — estructura fuera del form + preview

### Community 63 - "update_vehiculo"
Cohesion: 0.67
Nodes (3): agrupar_por_proveedor(), generar_pdf(), Genera un PDF de la lista de precios agrupada por proveedor.      Maneja acentos

### Community 64 - "registrar_movimiento_caja"
Cohesion: 0.67
Nodes (3): [0.5.3] - 2026-07-30, Corregido, Modificado

### Community 65 - "reactivar_cliente"
Cohesion: 0.67
Nodes (3): backup_db(), test_backup_db_crea_archivo(), test_backup_db_no_existe()

### Community 67 - "test_registrar_pago_cc_registra_tipo_movimiento_pago"
Cohesion: 0.13
Nodes (19): add_cliente(), get_cuenta_corriente_cliente(), get_movimientos_cuenta_corriente(), Obtiene el saldo actual de cuenta corriente de un cliente., Obtiene movimientos de cuenta corriente de un cliente (ventas y pagos)., Registra un pago (abono) de cuenta corriente.          Inserta un movimiento con, registrar_pago_cc(), El movimiento de pago debe tener tipo_movimiento='pago'. (+11 more)

### Community 69 - "test_get_clientes_con_deuda_incluye_antiguedad"
Cohesion: 0.50
Nodes (4): get_clientes_con_deuda(), Obtiene clientes que tienen deuda en cuenta corriente.          Devuelve tuplas:, get_clientes_con_deuda debe incluir antigüedad en días., test_get_clientes_con_deuda_incluye_antiguedad()

### Community 89 - "test_crear_venta_con_caja_abierta_registra_ingreso"
Cohesion: 0.20
Nodes (11): get_compras(), get_connection(), get_detalle_compra(), Obtiene listado de compras con información del proveedor., Obtiene el detalle de una compra con información del producto., Verifica que crear_venta registre automáticamente un movimiento ingreso_venta en, Si no hay caja abierta, crear_venta no debe registrar movimiento de caja., Debe crear una compra, actualizar stock y registrar movimientos. (+3 more)

### Community 91 - "test_get_precios_para_lista_solo_activos_con_stock"
Cohesion: 0.25
Nodes (8): get_precios_para_lista(), Devuelve productos activos con stock > 0 para armar la lista de precios.      Re, Solo productos activos con stock > 0 deben aparecer en la lista de precios., La lista debe estar ordenada por proveedor y luego por nombre de producto., La lista debe incluir el precio de venta correcto., test_get_precios_para_lista_incluye_precio_venta(), test_get_precios_para_lista_ordenado_por_proveedor(), test_get_precios_para_lista_solo_activos_con_stock()

### Community 99 - "test_add_producto_con_stock_inicial"
Cohesion: 0.29
Nodes (11): add_proveedor(), get_proveedores(), Debe crear producto con stock inicial y registrar movimiento., Debe anular compra y revertir stock., test_add_producto_con_stock_inicial(), test_add_proveedor_condicion_pago_invalida(), test_add_proveedor_condicion_pago_valida(), test_add_proveedor_nombre_vacio() (+3 more)

### Community 100 - "test_add_producto_sin_stock_inicial"
Cohesion: 0.31
Nodes (10): add_categoria(), get_categorias(), Debe crear producto con stock 0 por defecto y sin movimiento., Debe crear ajuste y registrar movimiento en la misma transacción., test_add_categoria_duplicado_devuelve_false(), test_add_categoria_null(), test_add_categoria_string_vacio(), test_add_producto_sin_stock_inicial() (+2 more)

### Community 104 - "test_crear_venta_items_vacios_retorna_error"
Cohesion: 0.11
Nodes (18): crear_venta(), Crea una venta completa con items, actualiza stock y registra movimiento.     it, Factura A: precio_venta ya incluye IVA. Total = subtotal_neto + iva = precio_fin, Producto inactivo debe retornar error especifico., Items vacios debe retornar error especifico., Factura B: sin IVA desglosado., crear_venta debe rechazar cantidades negativas o cero., crear_venta debe rechazar precios negativos. (+10 more)

### Community 120 - "[0.5.1] - 2026-07-30"
Cohesion: 0.67
Nodes (3): [0.5.1] - 2026-07-30, Corregido, Removido

## Knowledge Gaps
- **188 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `run_tests.sh script`, `Responsabilidades`, `Flujo de trabajo típico` (+183 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_connection()` connect `test_crear_venta_con_caja_abierta_registra_ingreso` to `get_connection`, `get_movimientos`, `_crear_producto_con_stock`, `database.py`, `crear_venta`, `get_venta_completa`, `get_reporte_ventas_detallado`, `update_categoria`, `update_producto`, `update_servicio`, `7_Ventas.py`, `test_get_ventas_pendientes_cc_tras_pago_parcial`, `get_ultimo_numero_comprobante`, `get_reporte_ingresos_egresos`, `get_ventas`, `get_ventas_pendientes_cc`, `test_add_movimiento_tipo_nulo`, `get_cuenta_corriente_cliente`, `update_proveedor`, `test_registrar_pago_cc_registra_tipo_movimiento_pago`, `test_crear_venta_cuenta_corriente_registra_tipo_venta`, `test_get_clientes_con_deuda_incluye_antiguedad`, `test_get_precios_para_lista_solo_activos_con_stock`, `test_add_producto_con_stock_inicial`, `test_add_producto_sin_stock_inicial`, `test_crear_venta_items_vacios_retorna_error`, `test_init_db_admin_no_password_vacio`, `test_get_connection_tiene_busy_timeout`, `test_init_db_crea_usuario_admin_por_defecto`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `add_producto()` connect `get_ultimo_numero_comprobante` to `get_connection`, `test_add_producto_con_stock_inicial`, `test_add_producto_sin_stock_inicial`, `get_movimientos`, `_crear_producto_con_stock`, `test_registrar_pago_cc_registra_tipo_movimiento_pago`, `database.py`, `test_crear_venta_items_vacios_retorna_error`, `test_get_clientes_con_deuda_incluye_antiguedad`, `test_get_ventas_pendientes_cc_tras_pago_parcial`, `7_Ventas.py`, `get_ventas_pendientes_cc`, `test_add_movimiento_tipo_nulo`, `test_crear_venta_con_caja_abierta_registra_ingreso`, `get_cuenta_corriente_cliente`, `test_get_precios_para_lista_solo_activos_con_stock`, `update_servicio`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `add_proveedor()` connect `test_add_producto_con_stock_inicial` to `get_connection`, `test_registrar_pago_cc_registra_tipo_movimiento_pago`, `test_add_producto_sin_stock_inicial`, `get_movimientos`, `test_get_clientes_con_deuda_incluye_antiguedad`, `7_Ventas.py`, `database.py`, `test_get_ventas_pendientes_cc_tras_pago_parcial`, `test_get_precios_para_lista_solo_activos_con_stock`, `get_ultimo_numero_comprobante`, `get_ventas_pendientes_cc`, `update_categoria`, `test_add_movimiento_tipo_nulo`, `test_crear_venta_con_caja_abierta_registra_ingreso`, `get_cuenta_corriente_cliente`, `update_producto`, `update_servicio`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **What connects `$schema`, `.opencode/plugins/graphify.js`, `run_tests.sh script` to the rest of the system?**
  _188 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `get_connection` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._
- **Should `get_movimientos` be split into smaller, more focused modules?**
  _Cohesion score 0.07807807807807808 - nodes in this community are weakly interconnected._
- **Should `_crear_producto_con_stock` be split into smaller, more focused modules?**
  _Cohesion score 0.12121212121212122 - nodes in this community are weakly interconnected._