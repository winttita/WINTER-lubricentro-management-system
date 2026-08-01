# Graph Report - Lubricentro  (2026-07-31)

## Corpus Check
- 48 files · ~97,573 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 813 nodes · 1013 edges · 123 communities (50 shown, 73 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0eddbfe9`
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
- get_reporte_ingresos_egresos
- update_servicio
- update_categoria
- get_ultimo_numero_comprobante
- update_producto
- update_categoria
- registrar_movimiento_caja
- update_proveedor
- update_vehiculo
- test_registrar_pago_cc_registra_tipo_movimiento_pago
- test_registrar_pago_cc_monto_negativo_devuelve_false
- test_registrar_pago_cc_cliente_inexistente_devuelve_false
- test_get_movimientos_cuenta_corriente_incluye_tipo_y_metodo
- test_registrar_pago_cc_registra_tipo_movimiento_pago
- test_crear_venta_cuenta_corriente_registra_tipo_venta
- test_get_clientes_con_deuda_incluye_antiguedad
- test_get_movimientos_cuenta_corriente_incluye_tipo_y_metodo
- test_aumentar_precios_proveedor_porcentaje_negativo
- test_aumentar_precios_por_lista_happy_path
- test_aumentar_precios_por_lista_porcentaje_negativo
- test_aumentar_precios_por_lista_ids_inexistentes
- test_get_productos_por_proveedor_happy_path
- test_get_productos_por_proveedor_con_busqueda
- [0.2.1] - 2026-07-17
- test_get_productos_por_proveedor_proveedor_inexistente
- test_get_productos_por_proveedor_sin_busqueda
- temp_db
- test_get_ventas_pendientes_cc
- test_get_ventas_pendientes_cc_tras_pago_parcial
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
- test_add_movimiento_producto_inexistente
- test_add_movimiento_producto_id_nulo
- test_add_producto_con_stock_inicial
- test_add_producto_sin_stock_inicial
- test_crear_ajuste_stock_con_movimiento
- test_crear_venta_items_vacios_retorna_error
- test_crear_y_get_compras
- test_anular_compra
- test_crear_venta_items_vacios_retorna_error
- test_init_db_admin_no_password_vacio
- test_get_connection_tiene_busy_timeout
- test_hash_password_con_salt_aleatorio
- test_verify_password_soporta_hash_legacy_sha256
- test_hash_password_diferente_para_distintas_entradas
- test_init_db_crea_usuario_admin_por_defecto
- test_verificar_login_admin_correcto
- test_verificar_login_password_incorrecta
- test_verificar_login_usuario_inexistente
- test_verificar_login_usuario_inactivo
- test_cambiar_password_actualiza_hash
- test_cambiar_password_usuario_inexistente
- [0.5.1] - 2026-07-30
- test_registrar_pago_cc_reduce_deuda
- test_registrar_pago_cc_pago_total_saldando

## God Nodes (most connected - your core abstractions)
1. `get_connection()` - 61 edges
2. `_crear_producto_con_stock()` - 24 edges
3. `Changelog - Lubricentro Winter` - 20 edges
4. `_crear_dependencias()` - 20 edges
5. `crear_producto_id()` - 18 edges
6. `_num_finito()` - 15 edges
7. `Guía de Firma Digital (Code Signing) para Lubricentro Winter` - 13 edges
8. `Global Constraints` - 13 edges
9. `Convenciones del proyecto — Lubricentro Winter` - 12 edges
10. `stock_de()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `test_generar_pdf_con_campos_none_no_falla()` --calls--> `generar_pdf()`  [EXTRACTED]
  tests/test_lista_precios_pdf.py → lista_precios_pdf.py
- `test_generar_pdf_con_logo()` --calls--> `generar_pdf()`  [EXTRACTED]
  tests/test_lista_precios_pdf.py → lista_precios_pdf.py
- `test_generar_pdf_con_logo_inexistente_no_falla()` --calls--> `generar_pdf()`  [EXTRACTED]
  tests/test_lista_precios_pdf.py → lista_precios_pdf.py
- `test_generar_pdf_sin_logo_no_falla()` --calls--> `generar_pdf()`  [EXTRACTED]
  tests/test_lista_precios_pdf.py → lista_precios_pdf.py
- `test_generar_pdf_sin_productos()` --calls--> `generar_pdf()`  [EXTRACTED]
  tests/test_lista_precios_pdf.py → lista_precios_pdf.py

## Import Cycles
- None detected.

## Communities (123 total, 73 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.09
Nodes (32): Exception, apply_update(), check_for_update(), clear_update_dir(), compare_versions(), download_asset(), _extract_zip_safe(), find_asset() (+24 more)

### Community 1 - "test_database.py"
Cohesion: 0.15
Nodes (12): 10. Actualización de este documento, 11. Uso de este documento, 1. Propósito y alcance, 2. Tono y estilo, 3. Prohibición de emojis, 4. Versionado (SemVer), 5. Releases y CHANGELOG, 6. Conventional Commits (+4 more)

### Community 3 - "database.py"
Cohesion: 0.29
Nodes (6): After Code Changes, AGENTS.md - Lubricentro Project, Auto-load Graphify Context on Session Start, Project Conventions, Project Structure, Quick Queries During Session

### Community 4 - "add_movimiento"
Cohesion: 0.18
Nodes (10): [0.1.0] - 2026-07-16, [0.5.3] - 2026-07-30, [0.5.4] - 2026-07-31, Agregado, Changelog - Lubricentro Winter, Convenciones de commits, Corregido, Corregido (+2 more)

### Community 5 - "get_movimientos"
Cohesion: 0.04
Nodes (46): _crear_producto_con_stock(), Helper para crear un producto con categoría, proveedor y stock inicial, Debe devolver movimientos ordenados por fecha descendente y aplicar límite, Debe agregar una compra exitosamente y aumentar el stock, Debe agregar una venta exitosamente y disminuir el stock, Debe manejar un ajuste positivo correctamente, Debe manejar un ajuste negativo correctamente, Debe manejar una devolución como entrada de stock (+38 more)

### Community 7 - "tickets.py"
Cohesion: 0.09
Nodes (25): calcular_totales(), imprimir_venta(), Calcula subtotal, iva y total segun el tipo de comprobante.     Reglas (alineada, Genera e imprime el comprobante de una venta., abrir_cajon(), formatear_monto(), generar_factura_a_texto(), generar_factura_b_texto() (+17 more)

### Community 8 - "database.py"
Cohesion: 0.13
Nodes (18): _count_products(), _make_db_with_products(), Tests del sistema de actualizaciones (updater + preservación de DB).  Corren en, Una DB con 10 productos debe seguir teniendo 10 después de:     1. init_db() col, Si hay una DB legacy en el dir de database.py y la nueva DB no existe,     init_, backup_db debe crear un archivo .db en BACKUP_DIR y cleanup_old_backups     debe, _extract_zip_safe debe rechazar zips con entradas absolutas o con .., El _sanitize_filename activo (línea 216, el segundo) debe rechazar     nombres c (+10 more)

### Community 9 - "crear_venta"
Cohesion: 0.09
Nodes (23): add_categoria(), add_cliente(), add_orden_servicio(), add_proveedor(), cerrar_caja(), get_ajustes_stock(), get_categorias_por_proveedor(), get_clientes() (+15 more)

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
Cohesion: 0.13
Nodes (15): cambiar_password(), hash_password(), init_db(), _migrate_legacy_db_location(), Devuelve el directorio de datos de usuario (absoluto) por SO.      Windows: %APP, Calcula DB_NAME y BACKUP_DIR absolutos. Crea el dir si no existe.     Devuelve (, Genera un hash scrypt con salt de la contraseña.          Formato: scrypt$N$r$p$, Verifica una contraseña contra un hash almacenado.          Soporta:     - scryp (+7 more)

### Community 24 - "get_ventas"
Cohesion: 0.50
Nodes (4): [0.2.4] - 2026-07-20, Agregado, Cambiado, Corregido

### Community 25 - "update_categoria"
Cohesion: 0.08
Nodes (24): abrir_caja(), add_producto(), add_servicio(), anular_compra(), aumentar_precios_por_categoria(), aumentar_precios_por_lista(), aumentar_precios_proveedor(), crear_compra() (+16 more)

### Community 26 - "update_proveedor"
Cohesion: 0.15
Nodes (12): Global Constraints, Release v0.5.0 - Correcciones y mejoras - Plan de Implementacion, Task 10: Verificacion final y release, Task 1: B04 - Corregir precio_venta en Ventas, Task 2: B06 - Migrar BD: eliminar columna codigo_interno, Task 3: B06 - Actualizar indices en UI y tests, Task 4: B05 - Cambiar selectbox a select_slider en Reportes, Task 5: B07 - Carrito vacio en Compras (+4 more)

### Community 28 - "update_cliente"
Cohesion: 0.18
Nodes (10): Data flow after fix, File Structure, Global Constraints, Self-Review Checklist, Task 1: Refactor updater.py — verify ZIP integrity, standardize path, remove worker, Task 2: Fix update.bat — cleanup on error, .exe backup, extraction fallback, Task 3: Add retry protection to launcher.py, Task 4: Improve app.py feedback (+2 more)

### Community 29 - "update_vehiculo"
Cohesion: 0.22
Nodes (8): Change, Commit, git diff, Notas adicionales, Status: DONE, Summary, Task 1 Report — B04: Corregir precio_venta index en Ventas, Verificación de índices

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
Nodes (11): cerrar_sesion(), init_session(), Inicializa flags de sesión si no existen., Limpia el estado de sesión., get_logo_path(), inject_global_css(), Inyecta CSS para ocultar el mensaje 'Press Enter to submit form' de Streamlit., Devuelve la ruta absoluta del logo si existe, o None.      Busca en el directori (+3 more)

### Community 37 - "anular_compra"
Cohesion: 0.46
Nodes (7): _assert_pantalla_principal(), _run_login(), _run_principal(), test_login_con_logo(), test_login_sin_logo_no_falla(), test_principal_con_logo(), test_principal_sin_logo_no_falla()

### Community 38 - "Sistema de Gestión para LUBRICENTRO WINTER"
Cohesion: 0.15
Nodes (12): Actualizaciones Remotas, Build del .exe (Windows), Cambiar la versión actual, Configuración en la app, Descripción, Estado del Proyecto, Estructura Técnica, Impresora Térmica (+4 more)

### Community 39 - "Agente de Testing"
Cohesion: 0.40
Nodes (4): Agente de Testing, Flujo de trabajo típico, Idioma, Responsabilidades

### Community 40 - "test_get_ventas_pendientes_cc_tras_pago_parcial"
Cohesion: 0.29
Nodes (7): add_movimiento(), add_orden_detalle(), crear_venta(), get_caja_abierta(), Crea una venta completa con items, actualiza stock y registra movimiento.     it, Obtiene la caja actualmente abierta.          Args:         conn: conexión opcio, Registra un movimiento de stock y actualiza el stock_actual del producto.     Re

### Community 42 - "get_cuenta_corriente_cliente"
Cohesion: 0.50
Nodes (4): [0.2.5] - 2026-07-21, Agregado, Cambiado, Corregido

### Community 43 - "get_detalle_compra"
Cohesion: 0.50
Nodes (4): [0.5.0] - 2026-07-30, Agregado, Corregido, Removido

### Community 46 - "get_reporte_ingresos_egresos"
Cohesion: 0.33
Nodes (5): get_all_python_files(), Test that all Python files in the project compile without syntax errors., Test that a Python file compiles without syntax errors., Collect all .py files in the project (excluding __pycache__ and virtual envs)., test_python_file_compiles()

### Community 48 - "check_for_update"
Cohesion: 0.33
Nodes (5): Test that the legacy DB migration (removing codigo_interno) works correctly., Test that running init_db twice on the same DB doesn't cause errors., Test that init_db() correctly migrates a DB with the old schema     (codigo_inte, test_migration_idempotent(), test_migration_legacy_db_removes_codigo_interno()

### Community 49 - "get_reporte_ventas"
Cohesion: 0.67
Nodes (3): [0.2.0] - 2026-07-17, Agregado, Corregido

### Community 53 - "update_vehiculo"
Cohesion: 0.67
Nodes (3): [0.2.6] - 2026-07-21, Cambiado, Corregido

### Community 54 - "test_add_movimiento_uso_interno"
Cohesion: 0.67
Nodes (3): [0.2.7] - 2026-07-21, Agregado, Corregido

### Community 55 - "test_add_movimiento_tipo_invalido"
Cohesion: 0.67
Nodes (3): [0.4.4] - 2026-07-28, Agregado, Corregido

### Community 60 - "update_categoria"
Cohesion: 0.24
Nodes (10): FPDF, generar_pdf(), Registra la fuente DejaVu Sans Unicode y devuelve el nombre de familia., Genera un PDF de la lista de precios agrupada por proveedor.      Usa fuente Uni, _register_unicode_font(), test_generar_pdf_con_campos_none_no_falla(), test_generar_pdf_con_logo(), test_generar_pdf_con_logo_inexistente_no_falla() (+2 more)

### Community 62 - "update_producto"
Cohesion: 0.50
Nodes (3): Global Constraints, Refactor UX de Compras (fila inicial + preview producto) Implementation Plan, Task 1: Refactor `pages/8_Compras.py` — estructura fuera del form + preview

### Community 64 - "registrar_movimiento_caja"
Cohesion: 0.67
Nodes (3): [0.5.1] - 2026-07-30, Corregido, Removido

### Community 81 - "[0.2.1] - 2026-07-17"
Cohesion: 0.67
Nodes (3): [0.2.1] - 2026-07-17, Agregado, Corregido

### Community 104 - "test_crear_venta_items_vacios_retorna_error"
Cohesion: 0.10
Nodes (16): add_vehiculo(), cleanup_old_backups(), get_categorias(), get_clientes_con_deuda(), get_compras(), get_orden_detalle(), get_proveedores(), get_reporte_inventario() (+8 more)

### Community 120 - "[0.5.1] - 2026-07-30"
Cohesion: 0.50
Nodes (4): [0.5.5] - 2026-07-31, Agregado, Corregido, Removido

## Knowledge Gaps
- **192 isolated node(s):** `Corregido`, `Removido`, `Agregado`, `Corregido`, `Corregido` (+187 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **73 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_connection()` connect `crear_venta` to `_crear_producto_con_stock`, `get_venta_completa`, `get_reporte_ventas_detallado`, `update_categoria`, `test_get_ventas_pendientes_cc_tras_pago_parcial`, `get_ultimo_numero_comprobante`, `update_cliente`, `find_asset`, `update_producto`, `test_add_movimiento_tipo_nulo`, `backup_db`, `get_reporte_ingresos_egresos`, `update_servicio`, `get_ultimo_numero_comprobante`, `update_categoria`, `update_proveedor`, `update_vehiculo`, `test_registrar_pago_cc_registra_tipo_movimiento_pago`, `test_crear_venta_items_vacios_retorna_error`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Why does `Changelog - Lubricentro Winter` connect `add_movimiento` to `registrar_movimiento_caja`, `get_cuenta_corriente_cliente`, `get_detalle_compra`, `init_db`, `crear_ajuste_stock`, `[0.2.1] - 2026-07-17`, `get_reporte_ventas`, `get_reporte_ingresos_egresos`, `get_reporte_inventario`, `update_vehiculo`, `test_add_movimiento_uso_interno`, `get_ventas`, `test_add_movimiento_tipo_invalido`, `[0.5.1] - 2026-07-30`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **What connects `Corregido`, `Removido`, `Agregado` to the rest of the system?**
  _192 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08901515151515152 - nodes in this community are weakly interconnected._
- **Should `get_movimientos` be split into smaller, more focused modules?**
  _Cohesion score 0.043478260869565216 - nodes in this community are weakly interconnected._
- **Should `tickets.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09116809116809117 - nodes in this community are weakly interconnected._
- **Should `database.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12631578947368421 - nodes in this community are weakly interconnected._