# Graph Report - Lubricentro  (2026-08-01)

## Corpus Check
- 51 files · ~103,012 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 848 nodes · 1520 edges · 71 communities (66 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `78836be7`
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
- formatear_fecha_hora
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
- get_logo_path
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
- check_for_update
- get_reporte_ventas
- get_ventas
- find_asset
- update_producto
- update_vehiculo
- test_add_movimiento_uso_interno
- test_add_movimiento_tipo_invalido
- test_add_movimiento_tipo_nulo
- backup_db
- test_registrar_pago_cc_con_ventas_imputa_pago
- imprimir_venta
- [0.5.3] - 2026-07-30
- get_ultimo_numero_comprobante
- update_producto
- registrar_movimiento_caja
- test_registrar_pago_cc_cliente_inexistente_devuelve_false
- test_get_movimientos_cuenta_corriente_incluye_tipo_y_metodo
- test_get_productos_por_proveedor_happy_path
- temp_db
- test_get_precios_para_lista_solo_activos_con_stock
- test_add_producto_con_stock_inicial
- [0.5.1] - 2026-07-30

## God Nodes (most connected - your core abstractions)
1. `get_connection()` - 90 edges
2. `add_producto()` - 64 edges
3. `add_proveedor()` - 47 edges
4. `add_categoria()` - 44 edges
5. `get_productos()` - 34 edges
6. `_crear_dependencias()` - 32 edges
7. `_crear_producto_con_stock()` - 30 edges
8. `crear_venta()` - 29 edges
9. `add_cliente()` - 23 edges
10. `add_movimiento()` - 22 edges

## Surprising Connections (you probably didn't know these)
- `test_compare_versions_basic()` --calls--> `compare_versions()`  [EXTRACTED]
  docker/test_updater.py → updater.py
- `test_find_asset_accepts_versioned_name_for_compatibility()` --calls--> `find_asset()`  [EXTRACTED]
  docker/test_updater.py → updater.py
- `test_find_asset_matches_ci_name()` --calls--> `find_asset()`  [EXTRACTED]
  docker/test_updater.py → updater.py
- `test_db_survives_simulated_update()` --calls--> `apply_update()`  [EXTRACTED]
  docker/test_updater.py → updater.py
- `test_get_logo_path_busca_tambien_junto_al_modulo()` --calls--> `get_logo_path()`  [EXTRACTED]
  tests/test_logo.py → style.py

## Import Cycles
- None detected.

## Communities (71 total, 5 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.15
Nodes (17): apply_update(), clear_update_dir(), download_asset(), find_asset(), _main(), Sistema de actualizaciones automáticas vía GitHub Releases.  Flujo:   1. get_lat, Verifica SHA256 del archivo contra el hash esperado (hex lowercase)., Verifica que un ZIP sea íntegro via CRC (testzip()) sin cargarlo en memoria. (+9 more)

### Community 1 - "test_database.py"
Cohesion: 0.15
Nodes (12): 10. Actualización de este documento, 11. Uso de este documento, 1. Propósito y alcance, 2. Tono y estilo, 3. Prohibición de emojis, 4. Versionado (SemVer), 5. Releases y CHANGELOG, 6. Conventional Commits (+4 more)

### Community 2 - "get_connection"
Cohesion: 0.18
Nodes (14): _count_products(), _make_db_with_products(), Tests del sistema de actualizaciones (updater + preservación de DB).  Corren en, Una DB con 10 productos debe seguir teniendo 10 después de:     1. init_db() col, Si hay una DB legacy en el dir de database.py y la nueva DB no existe,     init_, backup_db debe crear un archivo .db en BACKUP_DIR y cleanup_old_backups     debe, Crea una DB con n productos usando el esquema real de database.init_db., El CI sube un asset llamado LubricentroWinter.zip (corregido en v0.3.0).     fin (+6 more)

### Community 3 - "database.py"
Cohesion: 0.29
Nodes (6): After Code Changes, AGENTS.md - Lubricentro Project, Auto-load Graphify Context on Session Start, Project Conventions, Project Structure, Quick Queries During Session

### Community 4 - "add_movimiento"
Cohesion: 0.18
Nodes (10): [0.1.0] - 2026-07-16, [0.2.1] - 2026-07-17, [0.5.4] - 2026-07-31, Agregado, Agregado, Changelog - Lubricentro Winter, Convenciones de commits, Corregido (+2 more)

### Community 5 - "get_movimientos"
Cohesion: 0.05
Nodes (58): add_movimiento(), get_movimientos(), get_productos(), Registra un movimiento de stock y actualiza el stock_actual del producto.     Re, _crear_producto_con_stock(), aumentar_precios_proveedor debe actualizar precio_venta de productos del proveed, Helper para crear un producto con categoría, proveedor y stock inicial, Debe devolver una lista vacía cuando no hay movimientos (+50 more)

### Community 6 - "_crear_producto_con_stock"
Cohesion: 0.46
Nodes (7): _assert_pantalla_principal(), _run_login(), _run_principal(), test_login_con_logo(), test_login_sin_logo_no_falla(), test_principal_con_logo(), test_principal_sin_logo_no_falla()

### Community 7 - "tickets.py"
Cohesion: 0.14
Nodes (17): abrir_cajon(), formatear_monto(), generar_factura_a_texto(), generar_factura_b_texto(), generar_factura_c_texto(), generar_ticket_texto(), guardar_comprobante_archivo(), metodo_pago_nombre() (+9 more)

### Community 8 - "formatear_fecha_hora"
Cohesion: 0.24
Nodes (10): FPDF, generar_pdf(), Registra la fuente DejaVu Sans Unicode y devuelve el nombre de familia., Genera un PDF de la lista de precios agrupada por proveedor.      Usa fuente Uni, _register_unicode_font(), test_generar_pdf_con_campos_none_no_falla(), test_generar_pdf_con_logo(), test_generar_pdf_con_logo_inexistente_no_falla() (+2 more)

### Community 9 - "crear_venta"
Cohesion: 0.08
Nodes (44): add_categoria(), add_proveedor(), get_categorias(), get_proveedores(), aumentar_precios_proveedor no debe aceptar porcentaje negativo., aumentar_precios_por_lista debe actualizar el precio de los productos indicados., aumentar_precios_por_lista con porcentaje negativo debe devolver 0., get_productos_por_proveedor debe devolver solo los productos del proveedor indic (+36 more)

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
Cohesion: 0.07
Nodes (51): buscar_producto(), contar_movimientos(), crear_cliente_id(), crear_producto_id(), crear_proveedor_id(), nombre_unico(), Tests basados en propiedades (Hypothesis) para database.py.  Verifican invariant, Hipotesis: stock_actual == stock_inicial + suma(signo * cantidad)     para cualq (+43 more)

### Community 23 - "get_reporte_ventas_detallado"
Cohesion: 0.08
Nodes (26): cambiar_password(), hash_password(), Genera un hash scrypt con salt de la contraseña.          Formato: scrypt$N$r$p$, Verifica una contraseña contra un hash almacenado.          Soporta:     - scryp, Verifica credenciales de usuario.          Devuelve un dict con user_id, nombre,, Actualiza la contraseña de un usuario.          Devuelve True si se actualizó co, verificar_login(), _verify_password() (+18 more)

### Community 24 - "get_ventas"
Cohesion: 0.50
Nodes (4): [0.2.4] - 2026-07-20, Agregado, Cambiado, Corregido

### Community 25 - "update_categoria"
Cohesion: 0.40
Nodes (5): add_servicio(), get_servicios(), test_add_servicio_nombre_vacio(), test_add_servicio_precio_invalido(), test_add_servicio_precio_negativo()

### Community 26 - "update_proveedor"
Cohesion: 0.15
Nodes (12): Global Constraints, Release v0.5.0 - Correcciones y mejoras - Plan de Implementacion, Task 10: Verificacion final y release, Task 1: B04 - Corregir precio_venta en Ventas, Task 2: B06 - Migrar BD: eliminar columna codigo_interno, Task 3: B06 - Actualizar indices en UI y tests, Task 4: B05 - Cambiar selectbox a select_slider en Reportes, Task 5: B07 - Carrito vacio en Compras (+4 more)

### Community 27 - "update_producto"
Cohesion: 0.33
Nodes (6): aumentar_precios_por_lista(), Aumenta precio_venta de productos especificos.      Args:         producto_ids:, aumentar_precios_por_lista con lista vacia debe devolver 0., aumentar_precios_por_lista con IDs que no existen debe devolver 0., test_aumentar_precios_por_lista_ids_inexistentes(), test_aumentar_precios_por_lista_lista_vacia()

### Community 28 - "update_cliente"
Cohesion: 0.18
Nodes (10): Data flow after fix, File Structure, Global Constraints, Self-Review Checklist, Task 1: Refactor updater.py — verify ZIP integrity, standardize path, remove worker, Task 2: Fix update.bat — cleanup on error, .exe backup, extraction fallback, Task 3: Add retry protection to launcher.py, Task 4: Improve app.py feedback (+2 more)

### Community 29 - "update_vehiculo"
Cohesion: 0.22
Nodes (8): Change, Commit, git diff, Notas adicionales, Status: DONE, Summary, Task 1 Report — B04: Corregir precio_venta index en Ventas, Verificación de índices

### Community 30 - "update_servicio"
Cohesion: 0.10
Nodes (35): buscar_producto_por_codigo(), buscar_productos_por_nombre(), crear_compra(), get_categorias_por_proveedor(), proximo_codigo_fraccionado(), Resuelve un termino de busqueda: primero codigo de barras exacto, luego nombre e, Devuelve el siguiente codigo F-XXXX libre para productos sin codigo de barras fi, Devuelve las categorías que tienen productos activos para un proveedor dado. (+27 more)

### Community 33 - "get_compras"
Cohesion: 0.06
Nodes (32): 1. Manejo de caja (simple), 2. IntegrityError faltantes (rápido), 3. Carteles de éxito/error consistentes, 4. Soft delete de clientes, 5. Validación de fracciones en productos "Entero", Acciones, Archivos a modificar, Archivos a revisar (+24 more)

### Community 34 - "Documentar Código"
Cohesion: 0.22
Nodes (8): Adaptación a otros lenguajes, Buenas prácticas generales, Checklist antes de hacer commit, Con pdoc (más simple), Con Sphinx (recomendado para Python), Documentar Código, Generar documentación automática, Pasos para documentar un módulo (ejemplo en Python)

### Community 35 - "7_Ventas.py"
Cohesion: 0.33
Nodes (4): cerrar_sesion(), init_session(), Inicializa flags de sesión si no existen., Limpia el estado de sesión.

### Community 36 - "8_Compras.py"
Cohesion: 0.29
Nodes (8): flash_error(), flash_exito(), inject_global_css(), mostrar_flash(), Inyecta CSS para ocultar el mensaje 'Press Enter to submit form' de Streamlit., Guarda un mensaje de exito para mostrar en el proximo render., Guarda un mensaje de error y fuerza el rerun para mostrarlo., Muestra el mensaje flash pendiente (exito/error) y lo limpia.

### Community 37 - "get_logo_path"
Cohesion: 0.47
Nodes (5): get_logo_path(), Devuelve la ruta absoluta del logo si existe, o None.      Busca en el directori, test_get_logo_path_busca_tambien_junto_al_modulo(), test_get_logo_path_devuelve_none_si_no_hay_logo(), test_get_logo_path_encuentra_logo_en_cwd()

### Community 38 - "Sistema de Gestión para LUBRICENTRO WINTER"
Cohesion: 0.15
Nodes (12): Actualizaciones Remotas, Build del .exe (Windows), Cambiar la versión actual, Configuración en la app, Descripción, Estado del Proyecto, Estructura Técnica, Impresora Térmica (+4 more)

### Community 39 - "Agente de Testing"
Cohesion: 0.40
Nodes (4): Agente de Testing, Flujo de trabajo típico, Idioma, Responsabilidades

### Community 40 - "test_get_ventas_pendientes_cc_tras_pago_parcial"
Cohesion: 0.16
Nodes (18): abrir_caja(), cerrar_caja(), get_caja_abierta(), Abre una nueva caja.          Args:         saldo_inicial (float): Saldo inicial, Cierra una caja abierta.          Args:         caja_id (int): ID de la caja a c, Obtiene la caja actualmente abierta.          Args:         conn: conexión opcio, Registra un movimiento en caja y actualiza el saldo de la caja.          Args:, registrar_movimiento_caja() (+10 more)

### Community 42 - "get_cuenta_corriente_cliente"
Cohesion: 0.50
Nodes (4): [0.2.5] - 2026-07-21, Agregado, Cambiado, Corregido

### Community 43 - "get_detalle_compra"
Cohesion: 0.50
Nodes (4): [0.5.0] - 2026-07-30, Agregado, Corregido, Removido

### Community 44 - "get_reporte_ventas"
Cohesion: 0.14
Nodes (24): add_cliente(), add_orden_detalle(), add_orden_servicio(), add_vehiculo(), desactivar_cliente(), get_clientes(), Marca un cliente como inactivo (soft delete)., Reactivar un cliente inactivo. (+16 more)

### Community 45 - "get_ultimo_numero_comprobante"
Cohesion: 0.18
Nodes (12): test_compare_versions_basic(), Exception, check_for_update(), compare_versions(), get_latest_release(), _normalize_version(), Consulta la API de GitHub y devuelve el JSON de la última release publicada., Chequea si hay una actualización disponible.      Devuelve un dict con la info d (+4 more)

### Community 46 - "get_reporte_ingresos_egresos"
Cohesion: 0.33
Nodes (5): get_all_python_files(), Test that all Python files in the project compile without syntax errors., Test that a Python file compiles without syntax errors., Collect all .py files in the project (excluding __pycache__ and virtual envs)., test_python_file_compiles()

### Community 47 - "update_cliente"
Cohesion: 0.32
Nodes (3): _set_tz(), test_string_utc_sin_T_se_convierte_a_local(), test_ticket_venta_formatea_fecha_utc_a_local()

### Community 48 - "check_for_update"
Cohesion: 0.33
Nodes (5): Test that the legacy DB migration (removing codigo_interno) works correctly., Test that running init_db twice on the same DB doesn't cause errors., Test that init_db() correctly migrates a DB with the old schema     (codigo_inte, test_migration_idempotent(), test_migration_legacy_db_removes_codigo_interno()

### Community 49 - "get_reporte_ventas"
Cohesion: 0.67
Nodes (3): [0.2.0] - 2026-07-17, Agregado, Corregido

### Community 50 - "get_ventas"
Cohesion: 0.33
Nodes (6): _extract_zip_safe debe rechazar zips con entradas absolutas o con .., _extract_zip_safe debe rechazar también rutas windows (backslash) que     escape, test_extract_zip_safe_rejects_backslash_traversal(), test_extract_zip_safe_rejects_path_traversal(), _extract_zip_safe(), Extrae un ZIP validando cada entrada contra path traversal.     Lanza UpdateErro

### Community 52 - "update_producto"
Cohesion: 0.40
Nodes (4): calcular_totales(), imprimir_venta(), Calcula subtotal, iva y total segun el tipo de comprobante.     Reglas (alineada, Genera e imprime el comprobante de una venta.

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
Cohesion: 0.50
Nodes (4): [0.5.5] - 2026-07-31, Agregado, Corregido, Removido

### Community 57 - "backup_db"
Cohesion: 0.50
Nodes (4): imprimir_comprobante(), imprimir_prueba(), Imprime en impresora térmica usando comandos ESC/POS.     En Windows usa win32pr, Imprime un ticket de prueba.

### Community 58 - "test_registrar_pago_cc_con_ventas_imputa_pago"
Cohesion: 0.33
Nodes (6): get_reporte_inventario(), Reporte de inventario actual: productos con stock y valorizacion., Cuando no hay productos activos, el reporte de inventario debe estar vacío., Productos desactivados (activo=0) no deben aparecer en el reporte., test_reporte_inventario_excluye_productos_inactivos(), test_reporte_inventario_vacio()

### Community 59 - "imprimir_venta"
Cohesion: 0.67
Nodes (3): backup_db(), test_backup_db_crea_archivo(), test_backup_db_no_existe()

### Community 60 - "[0.5.3] - 2026-07-30"
Cohesion: 0.67
Nodes (3): [0.5.3] - 2026-07-30, Corregido, Modificado

### Community 61 - "get_ultimo_numero_comprobante"
Cohesion: 0.14
Nodes (14): anular_compra(), aumentar_precios_proveedor(), _num_finito(), Aumenta el precio_venta de todos los productos de un proveedor en un porcentaje, Actualiza los datos de un producto existente., Actualiza los datos de un servicio existente., Anula una compra revirtiendo el stock de cada producto.     Retorna True si se a, Registra un pago de cuenta corriente imputándolo a ventas específicas. (+6 more)

### Community 62 - "update_producto"
Cohesion: 0.50
Nodes (3): Global Constraints, Refactor UX de Compras (fila inicial + preview producto) Implementation Plan, Task 1: Refactor `pages/8_Compras.py` — estructura fuera del form + preview

### Community 64 - "registrar_movimiento_caja"
Cohesion: 0.67
Nodes (3): [0.5.1] - 2026-07-30, Corregido, Removido

### Community 69 - "test_registrar_pago_cc_cliente_inexistente_devuelve_false"
Cohesion: 0.14
Nodes (14): Registra un pago (abono) de cuenta corriente.          Inserta un movimiento con, registrar_pago_cc(), registrar_pago_cc no debe aceptar montos negativos., registrar_pago_cc debe devolver False si el cliente no existe., El movimiento de pago debe tener tipo_movimiento='pago'., get_movimientos_cuenta_corriente debe incluir tipo_movimiento y metodo_pago., registrar_pago_cc debe insertar un movimiento negativo y reducir el saldo., registrar_pago_cc con monto = deuda total debe dejar saldo en 0. (+6 more)

### Community 79 - "test_get_productos_por_proveedor_happy_path"
Cohesion: 0.50
Nodes (4): get_productos_por_proveedor(), Devuelve productos activos de un proveedor, opcionalmente filtrados.      Args:, get_productos_por_proveedor con proveedor inexistente debe devolver lista vacia., test_get_productos_por_proveedor_proveedor_inexistente()

### Community 84 - "temp_db"
Cohesion: 0.22
Nodes (9): init_db(), _migrate_legacy_db_location(), Devuelve el directorio de datos de usuario (absoluto) por SO.      Windows: %APP, Calcula DB_NAME y BACKUP_DIR absolutos. Crea el dir si no existe.     Devuelve (, Mueve lubricantro.db (y backups/) desde el directorio del script/app     (legacy, _resolve_data_paths(), _user_data_dir(), Apunta database.DB_NAME a un archivo temporal y lo inicializa limpio. (+1 more)

### Community 94 - "test_get_precios_para_lista_solo_activos_con_stock"
Cohesion: 0.07
Nodes (42): add_producto(), aumentar_precios_por_categoria(), crear_venta(), Aumenta el precio_venta de los productos de un proveedor filtrados por categoría, Crea una venta completa con items, actualiza stock y registra movimiento.     it, crear_venta a cuenta corriente debe registrar tipo_movimiento='venta'., get_clientes_con_deuda debe incluir antigüedad en días., get_ventas_pendientes_cc debe devolver ventas a crédito con saldo pendiente. (+34 more)

### Community 101 - "test_add_producto_con_stock_inicial"
Cohesion: 0.05
Nodes (49): cleanup_old_backups(), crear_ajuste_stock(), get_ajustes_stock(), get_clientes_con_deuda(), get_compras(), get_connection(), get_cuenta_corriente_cliente(), get_detalle_compra() (+41 more)

### Community 120 - "[0.5.1] - 2026-07-30"
Cohesion: 0.50
Nodes (4): [0.5.6] - 2026-08-01, Agregado, Corregido, Removido

## Knowledge Gaps
- **195 isolated node(s):** `Agregado`, `Corregido`, `Removido`, `Corregido`, `Removido` (+190 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_connection()` connect `test_add_producto_con_stock_inicial` to `get_movimientos`, `test_registrar_pago_cc_cliente_inexistente_devuelve_false`, `test_get_ventas_pendientes_cc_tras_pago_parcial`, `crear_venta`, `get_venta_completa`, `get_reporte_ventas`, `test_get_productos_por_proveedor_happy_path`, `get_reporte_ventas_detallado`, `temp_db`, `update_servicio`, `update_categoria`, `test_registrar_pago_cc_con_ventas_imputa_pago`, `update_producto`, `get_ultimo_numero_comprobante`, `test_get_precios_para_lista_solo_activos_con_stock`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `add_producto()` connect `test_get_precios_para_lista_solo_activos_con_stock` to `get_movimientos`, `test_add_producto_con_stock_inicial`, `test_registrar_pago_cc_cliente_inexistente_devuelve_false`, `crear_venta`, `get_reporte_ventas`, `test_registrar_pago_cc_con_ventas_imputa_pago`, `get_ultimo_numero_comprobante`, `update_servicio`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `add_proveedor()` connect `crear_venta` to `get_movimientos`, `test_registrar_pago_cc_cliente_inexistente_devuelve_false`, `test_add_producto_con_stock_inicial`, `update_servicio`, `test_registrar_pago_cc_con_ventas_imputa_pago`, `test_get_precios_para_lista_solo_activos_con_stock`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **What connects `Agregado`, `Corregido`, `Removido` to the rest of the system?**
  _195 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `get_movimientos` be split into smaller, more focused modules?**
  _Cohesion score 0.05263157894736842 - nodes in this community are weakly interconnected._
- **Should `tickets.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1437908496732026 - nodes in this community are weakly interconnected._
- **Should `crear_venta` be split into smaller, more focused modules?**
  _Cohesion score 0.07822410147991543 - nodes in this community are weakly interconnected._