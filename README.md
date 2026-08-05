# Sistema de Gestión para LUBRICENTRO WINTER (Centro Automotor WINTER)

## Descripción
Proyecto de sistema de gestión de stock y punto de venta (POS) para el lubricentro familiar, desarrollado bajo requerimientos específicos para optimizar el control de inventario y servicios.

## Estado del Proyecto
Finalizada la Fase 1 (Infraestructura), Fase 2 (Gestión de Inventario: Productos, Categorías, Proveedores), Fase 3 (Movimientos de Stock), Fase 4 (Gestión de Clientes, Vehículos y Servicios) y Fase 5 (Reportes). La versión actual es **v0.5.6**.

## Estructura Técnica
- **Framework:** Streamlit
- **Base de Datos:** SQLite
- **Módulos:**
  - `database.py`: Lógica de datos y persistencia.
  - `app.py`: Dashboard principal con métricas y navegación.
  - `pages/0_Gestion.py`: Gestión general (usuarios, impresora térmica).
  - `pages/1_Stock.py`: Control de stock y ajustes.
  - `pages/2_Cuenta_Corriente.py`: Cuenta corriente de clientes.
  - `pages/3_Productos.py`: Gestión de productos (incluye generación de códigos F).
  - `pages/4_Ordenes.py`: Órdenes de servicio.
  - `pages/7_Ventas.py`: Punto de venta con carrito, escáner de código de barras e impresión de tickets.
  - `pages/8_Caja.py`: Apertura y cierre de caja, movimientos de caja.
  - `pages/8_Compras.py`: Gestión de compras a proveedores con carrito y escaneo.
  - `pages/9_Reportes.py`: Reportes de ventas, inventario y balance ingresos vs egresos.
  - `pages/10_ListaPrecios.py`: Generación de lista de precios en PDF.
  - `tickets.py`: Generación e impresión de tickets en impresoras térmicas ESC/POS.
  - `fechas.py`: Normalización y formato de fechas y horas.
  - `style.py`: Estilos, logo y mensajes persistentes (flash/toast).
  - `lista_precios_pdf.py`: Generación de PDF de lista de precios.
  - `updater.py`: Checkeo y descarga de actualizaciones desde GitHub Releases.
  - `update.bat`: Script de aplicación de la actualización generado dinámicamente.
  - `build/launcher.py`: Launcher de Windows que arranca la app y aplica actualizaciones con recuperación ante fallos.
  - `tests/`: Suite de tests (unitarios, compilación, migración legacy, basados en propiedades).

## Release v0.5.6

- Ventas: campo unificado de búsqueda que resuelve código de barras escaneado o nombre y agrega el producto al carrito
- Compras: campo de escaneo de código de barras que rellena el producto y autocompleta el precio costo
- Productos: botón "Generar código F" (F0001, F0002...) para productos sin código de barras físico
- Ventas: checkbox "Imprimir ticket" por venta (marcado por defecto)
- Tickets: fechas normalizadas a hora local con formato DD/MM/AAAA HH:MM
- Carteles: mensajes de éxito/error persistentes tras el submit en todos los formularios
- Migración de DB legacy preservando datos, autenticación con scrypt, backup consistente con API de SQLite
- Actualización del nombre del local a "Centro Automotor WINTER" con logo propio

## Próximos Pasos
- Mejoras futuras y feedback de usuarios.

## Actualizaciones Remotas
La aplicación consulta automáticamente GitHub Releases al iniciar (con caché de 1 hora) y muestra un aviso en el sidebar si hay una versión más nueva. El usuario puede descargarla con un botón; al reiniciar, el launcher aplica el cambio mediante un proceso silencioso.

- **Flujo de actualización:**
  1. Al hacer clic en "Descargar e instalar actualización", `updater.py` descarga el ZIP (con verificación de integridad y checksum) y genera `update.bat`.
  2. El launcher, al reiniciar, ejecuta el proceso de extracción segura (con validación anti path-traversal), respalda el ejecutable anterior y reemplaza los archivos.
  3. Si la actualización queda a medio aplicar, el launcher restaura el backup en el próximo arranque (máximo 3 reintentos).
  4. No se muestran ventanas de cmd/PowerShell; todo el proceso es automático e invisible para el usuario.
  5. En caso de error, se registra en `_logs/update_error.log`.

- **Base de datos:** Reside siempre en el directorio de datos de usuario (`%APPDATA%\LubricentroWinter\` en Windows o `~/.local/share/LubricentroWinter/` en Linux), garantizando que las actualizaciones no sobrescriban ni pierdan los datos.

- **Versionado de esquema:** Tabla `_schema_version` para futuras migraciones de base de datos.

- Repo de releases: https://github.com/winttita/WINTER-lubricentro-management-system/releases
- Convención de versiones: semver `MAJOR.MINOR.PATCH` (tag `v0.1.0`, etc.).

## Build del .exe (Windows)
Para generar el .zip distribuible:

```bat
build\build_windows.bat
```

El script:
1. Compila `build/launcher.py` con PyInstaller -> `LubricentroWinter.exe`.
2. Descarga Python embebido 3.12 (amd64), instala pip y dependencias.
3. Copia `app.py`, `database.py`, `pages/`, `updater.py`, `fonts/` y el logo al paquete.
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

## Tests

```bash
pytest
```

La suite cubre la lógica de base de datos, compilación de todos los módulos,
migración de bases legacy y propiedades invariantes (stock, cuentas, códigos).
