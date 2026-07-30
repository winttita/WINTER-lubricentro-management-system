# Sistema de Gestión para LUBRICENTRO WINTER

## Descripción
Proyecto de sistema de gestión de stock y punto de venta (POS) para el lubricentro familiar, desarrollado bajo requerimientos específicos para optimizar el control de inventario y servicios.

## Estado del Proyecto
Finalizada la Fase 1 (Infraestructura), Fase 2 (Gestión de Inventario: Productos, Categorías, Proveedores), Fase 3 (Movimientos de Stock), Fase 4 (Gestión de Clientes, Vehículos y Servicios) y Fase 5 (Reportes).

## Estructura Técnica
- **Framework:** Streamlit
- **Base de Datos:** SQLite
- **Módulos:**
  - `database.py`: Lógica de datos y persistencia.
    - `pages/1_Categorias.py`: Gestión de categorías.
    - `pages/2_Proveedores.py`: Gestión de proveedores.
    - `pages/3_Productos.py`: Gestión de productos.
    - `pages/4_Movimientos_Stock.py`: Registro de movimientos de stock (entradas/salidas).
    - `pages/5_Clientes.py`: Gestión de clientes.
    - `pages/6_Vehiculos.py`: Gestión de vehículos.
    - `pages/7_Servicios.py`: Gestión de servicios.
    - `pages/8_OrdenesServicio.py`: Gestión de órdenes de servicio (productos y servicios).
    - `pages/9_Reportes.py`: Reportes de ventas, inventario y balance ingresos vs egresos.
    - `app.py`: Dashboard principal con métricas y navegación.
  - `update_worker.py`: Watchdog de actualización en Python que maneja la extracción segura del ZIP y el relanzamiento del launcher (sin ventanas visibles).

## Release v0.5.0

- Aumento de precios por proveedor (general y parcial con filtro)
- Corrección de corte de ticket e impresión en ventas
- Carritos de venta y compra inician vacíos
- Escáner de código de barras en ventas
- Autocompletado de precio de venta al seleccionar producto
- Preview de producto en compras (precio, stock, proveedor, código)
- Selector de periodo reemplazado por deslizador
- Eliminación del campo código interno de productos
- Manejo de errores IntegrityError y DB locked
- Límite de descarga aumentado a 500 MB

## Próximos Pasos
- Mejoras futuras y feedback de usuarios.

## Actualizaciones Remotas
La aplicación consulta automáticamente GitHub Releases al iniciar y muestra un aviso en el sidebar si hay una versión más nueva. El usuario puede descargarla con un botón; al reiniciar la app, el `launcher.exe` aplica el cambio mediante un proceso silencioso.

- **Flujo de actualización:**
  1. Al hacer clic en "Descargar e instalar actualización", `app.py` descarga el ZIP y lanza el watchdog (`update_worker.py`) mediante `runtime\pythonw.exe` (sin ventana).
  2. El watchdog espera que la aplicación principal cierre, extrae el ZIP usando `zipfile` con validación anti path‑traversal, reemplaza los archivos y relanza el launcher.
  3. No se muestran ventanas de cmd/PowerShell; todo el proceso es automático e invisible para el usuario.
  4. En caso de error, se registra en `_logs/update_error.log`.

- **Base de datos:** Ahora reside siempre en el directorio de datos de usuario (`%APPDATA%\LubricentroWinter\` en Windows o `~/.local/share/LubricentroWinter/` en Linux), garantizando que las actualizaciones manuales (descarga y extracción del ZIP) no sobrescriban ni pierdan los datos.

- **Versionado de esquema:** Se añadió la tabla `_schema_version` para futuras migraciones de base de datos.

- Repo de releases: https://github.com/winttita/WINTER-lubricentro-management-system/releases
- Convención de versiones: semver `MAJOR.MINOR.PATCH` (tag `v0.1.0`, etc.).
- El archivo `updater.py` contiene toda la lógica de checkeo y descarga, incluyendo fallback por compatibilidad con builds antiguos.

## Build del .exe (Windows)
Para generar el .zip distribuible:

```bat
build\build_windows.bat
```

El script:
1. Compila `build/launcher.py` con PyInstaller -> `LubricentroWinter.exe`.
2. Descarga Python embebido 3.12 (amd64), instala pip y dependencias.
3. Copia `app.py`, `database.py`, `pages/`, `updater.py`, `update_worker.py` al paquete.
4. Genera `dist/LubricentroWinter_vX.Y.Z.zip`.

Subir ese .zip a una nueva GitHub Release (tag `vX.Y.Z`) para que la app lo detecte como actualización.

### Cambiar la versión actual
Editá `APP_VERSION` en `updater.py` antes de compilar/release.

## Impresora Térmica

Lubricentro Winter soporta impresión de tickets/facturas en impresoras térmicas
compatibles con ESC/POS (OCPP-80T, EPSON TM-T20, etc.).

### Instalación del driver (solo primera vez)

1. Conectá la impresora por USB a la PC
2. Abrí la carpeta `drivers/OCPP-80T/` de la instalación
3. Ejecutá `POS Printer Driver V8.11.230513.exe` como Administrador
4. Seguí los pasos del instalador

### Configuración en la app

1. Iniciá sesión en Lubricentro Winter
2. Andá a **Gestión** → sección **Impresora Térmica**
3. Seleccioná tu impresora del listado
4. Usá "Imprimir prueba" para verificar