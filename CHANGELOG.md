# Changelog - Lubricentro Winter

Todas las versiones notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [0.3.0] - 2026-07-23

### Agregado
- Sistema de autenticación con login (usuario `admin` / contraseña `winter1234`), sesiones y logout en sidebar
- Página **Gestión** (renombrada de Configuración): unifica Clientes, Vehículos, Categorías, Proveedores y Servicios
- Página **Stock**: Stock Actual (con búsqueda y alertas), Movimientos (filtros y resumen), Ajustes (con permisos admin/supervisor)
- Página **Cuenta Corriente**: lista deudores con antigüedad, detalle de movimientos, registro de pagos parciales/totales con selección de tickets a imputar
- Página **Órdenes de Servicio**: creación con cliente + vehículo filtrado, tabla dinámica de servicios y productos (descuenta stock), totales y confirmación
- Impresión automática de ticket/factura A/B/C al confirmar venta (usa `tickets.py` + `win32print`/`lp`)
- Botón 🗑️ (emoji) en lugar de "Quitar" en la tabla de ventas
- Precio no editable en ventas (se autocompleta del producto, solo modificable desde Productos o Compras)
- Aumento porcentual de precios por proveedor en Gestión (nuevo botón "Aplicar aumento" en cada proveedor)
- Ocultación del mensaje "Press Enter to submit form" en todos los formularios mediante CSS global (`style.py`)
- Validación de cliente duplicado en creación: muestra "Cliente Existente"
- Campo email opcional en creación de clientes (no lanza error si está vacío)

### Cambiado
- Renombrada sección "Configuración" → "Gestión" en sidebar y navegación
- Movida sección "Vehículos" desde página propia a dentro de Gestión
- Eliminadas páginas independientes: `4_Movimientos_Stock.py` y `5_Ajustes_Stock.py` (unificadas en `1_Stock.py`)
- `crear_venta` en `database.py` ahora inserta `tipo_movimiento='venta'` en `cuenta_corriente`
- `get_clientes_con_deuda` y `get_movimientos_cuenta_corriente` incluyen columnas de antigüedad, tipo y método de pago
- Reportes (tab "Cta. Corriente") actualizados para reflejar nuevas columnas
- Sidebar actualizado con nuevas secciones: Cuenta Corriente, Órdenes de Servicio, Gestión

### Corregido
- Error `ValueError: 5 columns passed, passed data had 7 columns` en Reportes → Cta. Corriente (DataFrame ahora tiene 7 y 12 columnas según corresponda)
- Precios en ventas ya no son editables (evita desviación del precio de lista)
- `get_ventas_pendientes_cc` calcula correctamente el pendiente por venta usando `ventas_imputadas`

### Seguridad
- Migración BD: tabla `cuenta_corriente` agrega columnas `tipo_movimiento`, `metodo_pago`, `observacion`, `usuario_id`, `ventas_imputadas`
- Login obligatorio en todas las páginas (guards en `app.py` y cada `pages/*.py`)
- Contraseña por defecto `winter1234` hasheada con SHA-256 (no texto plano)

### Infraestructura
- Build scripts (`build/build_windows.bat`, `.github/workflows/release.yml`) preparados para firma digital condicional con `signtool` (requiere certificado)
- Nuevo `style.py` para inyección CSS global
- Tests: 82 tests pasan (9 nuevos: autenticación, cuenta corriente pagos, aumento proveedor)


## [0.2.7] - 2026-07-21

### Agregado
- Icono personalizado para el ejecutable Windows (`build/icon.ico`): bidon minimalista de lubricante con gota dorada, multiresolucion (16x16, 32x32, 48x48, 64x64, 128x128, 256x256, 512x512) para mejorar la identificacion visual de la aplicacion en el escritorio y el explorador de archivos.

### Corregido
- Ninguno en esta release.

## [0.2.6] - 2026-07-21

### Corregido
- Aparicion de ventana de terminal con el comando `find "%PID%"` bloqueante durante la aplicacion de actualizaciones en `build/launcher.py:_write_update_batch`: el comando `find` de `cmd` esperaba entrada de STDIN de forma interactiva, deteniendo el proceso hasta que el usuario presionaba `Ctrl+C`. Se reemplazo por `findstr /C:"%PID%"` con redireccion `< nul` no interactiva.
- Falta del flag `CREATE_NO_WINDOW` en `build/launcher.py:check_and_launch_update` y `build/launcher.py:main` al lanzar `cmd /c update.bat`: el subproceso abria una consola visible. Ahora se combina con `DETACHED_PROCESS` y `CREATE_NEW_PROCESS_GROUP`.
- Llamada a PowerShell visible durante la descompresion del ZIP: se agrego `-WindowStyle Hidden` al comando `Expand-Archive` en `build/launcher.py:_write_update_batch`.
- Bloqueo `pause` en la rama de error del `update.bat`: impedia continuar el flujo automatico si la descompresion fallaba. Se elimino para mantener el flujo desatendido.

### Cambiado
- Flujo de actualizacion totalmente automatico en `build/launcher.py`: descarga, descompresion, reemplazo del `.exe` y relanzamiento ahora ocurren sin intervencion del usuario, en segundo plano y sin ventanas de terminal visibles.

## [0.2.5] - 2026-07-21

### Agregado
- Validacion explicita de items y stock en `database.py:crear_venta`: retorna `(venta_id, numero, error_msg)` con mensaje especifico para cada caso (items vacios, producto inactivo, stock insuficiente, error de movimiento)
- Calculo de IVA incluido para `factura_a` en `database.py:crear_venta`: `subtotal = total / 1.21`, `iva = total - subtotal` (antes el IVA se sumaba al precio, duplicando el impuesto)
- Parametro `conn` opcional en `database.py:add_movimiento` para reutilizar la conexion del caller y evitar bloqueos SQLite cuando la operacion se realiza dentro de una transaccion abierta
- IU dinamica en la pagina de Compras (`pages/8_Compras.py`): se reemplaza el formulario estatico de 3 productos por una lista en `session_state` con agregar/quitar filas
- Busqueda lazy, vista previa y carrito mejorado en `pages/7_Ventas.py`: feedback de stock insuficiente en el carrito y totales coherentes con el tipo de comprobante (`calcular_totales`)
- Suite de tests ampliada para `crear_venta`: cubre stock insuficiente, factura A con IVA incluido, ticket/factura B/factura C sin IVA, producto inactivo e items vacios (`tests/test_database.py`)
- Dependabot para dependencias pip y GitHub Actions (`.github/dependabot.yml`)
- Plantillas de issues para reporte de bugs y solicitud de funciones (`.github/ISSUE_TEMPLATE/`)
- Workflow de CodeQL para analisis estatico de Python (`.github/workflows/codeql.yml`)

### Corregido
- Error `database is locked` en `database.py:crear_venta` y `database.py:crear_orden_servicio`: `add_movimiento` abria una segunda conexion mientras la primera mantenia una transaccion sin commitear; ahora usa la misma conexion del caller
- Calculo incorrecto de IVA en `database.py:crear_venta` para `factura_a`: el precio de venta ya incluye el IVA, por lo que la version anterior lo sumaba de mas sobre el total
- Llamada a `crear_venta` en `pages/7_Ventas.py` que desconocia la nueva firma de 3 valores y mostraba mensaje generico sin informacion del error

### Cambiado
- `database.py:crear_venta` ahora retorna tupla de 3 valores `(venta_id, numero_comprobante, error_msg)`, antes `(venta_id, numero_comprobante)`. Cambio que rompe compatibilidad: callers previos que esperan 2 valores deben actualizarse
- Eliminacion de emojis prohibidos en textos visibles de `pages/7_Ventas.py` y `pages/8_Compras.py` para cumplir CONVENTIONS.md

## [0.2.4] - 2026-07-20

### Agregado
- Stock inicial al crear producto: nuevo campo opcional en formulario de productos (`pages/3_Productos.py`)
- Módulo de compras a proveedores: tabla `compras` y `detalle_compras`, funciones `crear_compra`, `get_compras`, `get_detalle_compra`, `anular_compra` (`database.py`)
- Página de Compras (`pages/8_Compras.py`) con formulario de carga e historial con anulación
- Convenciones del proyecto (`CONVENTIONS.md`) con reglas de tono, emojis, versionado, commits y CI/CD
- Referencia a CONVENTIONS.md desde AGENTS.md para carga automática en cada sesión
- Seed de usuario admin por defecto en `init_db` para evitar violación de FK en ajustes de stock

### Corregido
- Error "cannot be modified after the widget with key codigo_barras_scanner is instantiated" en `pages/3_Productos.py`: se reemplazó asignación directa por patrón de bandera
- Error "Error al aplicar el ajuste" en `database.py:crear_ajuste_stock`: no se registraba el movimiento de stock y fallaba por FK violation (falta de usuario admin en la tabla usuarios)
- Eliminación de emojis prohibidos en las descripciones de GitHub Releases (workflow `.github/workflows/release.yml`) para cumplir con CONVENTIONS.md

### Cambiado
- `database.py:add_producto` ahora acepta `stock_inicial` opcional (default 0) y registra movimiento de compra inicial si > 0
- Actualización automática mejorada: al descargar una actualización, la app se cierra sola y se reabre automáticamente actualizada sin intervención manual
- Actualización de actualizaciones: se oculta la ventana de PowerShell durante la descompresión de archivos ZIP para mejorar la experiencia visual

## [0.2.3] - 2026-07-18

### Agregado
- **Nuevas tablas de base de datos**: usuarios, ajustes_stock, ventas, venta_items, cuenta_corriente
- **Sistema de usuarios**: Roles (admin, supervisor, operador) con autenticación básica
- **Ajustes de stock con auditoría**: Registro de cambios de stock con motivo, usuario y diferencia
- **Punto de Venta (POS)**: Carrito de compras, búsqueda por código de barras/nombre, selección de cliente
- **Gestión de ventas**: Comprobantes (Factura A/B, Nota de Crédito, Ticket), métodos de pago, IVA automático
- **Cuenta Corriente**: Registro de deudas de clientes, historial de movimientos, reporte de deudores
- **Edición de entidades**: Funciones `update_categoria`, `update_proveedor`, `update_producto`, `update_cliente`, `update_vehiculo`, `update_servicio`
- **Nuevas páginas Streamlit**: Configuración unificada (Categorías + Proveedores), Ajustes de Stock, Ventas/POS, Reportes extendidos

### Corregido
- Reporte de ingresos/egresos: ahora cierra correctamente la conexión a base de datos
- Validaciones de stock en creación de ventas (evita venta sin stock)
- Manejo de errores en constraints únicos (código de barras, nombres duplicados)
- **Updater**: Función `_write_update_batch` faltante que causaba error "name 'write_update_bat' is not defined" al descargar e instalar actualizaciones

### Cambiado
- Reorganización de páginas: Categorías y Proveedores unificadas en Configuración (0_Configuracion.py)
- Páginas removidas: 1_Categorias.py, 2_Proveedores.py, 5_Clientes.py, 7_Servicios.py, 8_OrdenesServicio.py
- Páginas renombradas: 5_Ajustes_Stock.py, 7_Ventas.py

## [0.2.2] - 2026-07-17

### Agregado
- **Visualización de versión en sidebar**: La versión actual ahora se muestra en la barra lateral de la aplicación
- **Verificación automática de actualizaciones**: La aplicación comprueba actualizaciones disponibles al iniciar
- **Interfaz mejorada de actualización**: UX optimizada para el proceso de descarga e instalación de actualizaciones
- **Workflow de CI/CD automatizado**: GitHub Actions para compilación y liberación de releases de Windows
- **AGENTS.md**: Documentación de arquitectura para asistentes de código (integración con graphify)

### Corregido
- Sintaxis de scripts PowerShell en workflow de GitHub Actions
- Manejo de errores robusto con try/catch y validación de códigos de salida
- Ruta absoluta para `get-pip.py` en instalación de Python embebido
- Logging y diagnóstico mejorado en proceso de build

### Cambiado
- Refactorización de scripts de build para mayor confiabilidad
- Validación de pasos críticos con verificación de códigos de salida

## [0.2.1] - 2026-07-17

### Agregado
- **Auto-actualización completa**: Mecanismo de swap .exe tras cerrar la aplicación (`update.bat`)
- **Reinicio automático**: La aplicación se reinicia sola tras aplicar la actualización

### Corregido
- **KeyError en productos**: Manejo correcto cuando no hay categorías o proveedores cargados
- Prevención de errores al acceder a claves inexistentes en diccionarios de productos

## [0.2.0] - 2026-07-17

### Agregado
- **Sistema de backups automático**: Backup al iniciar la aplicación
- **Botón de backup manual**: Opción para crear backups bajo demanda
- **Limpieza de backups antiguos**: Retención configurable (por defecto 10 backups)
- **Sistema de actualizaciones remotas**: Descarga e instalación desde GitHub Releases
- **Launcher .exe para Windows**: Ejecutable nativo compilado con PyInstaller

### Corregido
- Registro de adapter datetime→ISO 8601 para SQLite (compatibilidad Python 3.12+)

## [0.1.0] - 2026-07-16

### Agregado
- **Fase 5 completa**: Reportes de ventas, inventario y balance
- **Fase 4 completa**: Clientes, vehículos, servicios y órdenes de servicio
- Pruebas unitarias con pytest
- Base del sistema de gestión de lubricentro

---

## Formato de versiones

- **MAJOR** (X.0.0): Cambios incompatibles en API/UX
- **MINOR** (0.X.0): Nuevas funcionalidades compatibles
- **PATCH** (0.0.X): Correcciones de bugs compatibles

## Convenciones de commits

Este proyecto sigue [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bug
- `docs:` - Cambios en documentación
- `style:` - Formato, punto y coma, etc. (sin cambio de lógica)
- `refactor:` - Refactorización de código
- `perf:` - Mejora de rendimiento
- `test:` - Añadir o modificar tests
- `chore:` - Tareas de mantenimiento, dependencias, build
- `ci:` - Cambios en configuración de CI/CD
