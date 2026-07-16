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

## Próximos Pasos
- Mejoras futuras y feedback de usuarios.

## Actualizaciones Remotas
La aplicación consulta automáticamente GitHub Releases al iniciar y muestra un
aviso en el sidebar si hay una versión más nueva. El usuario puede descargarla
con un botón; al reiniciar la app, el `launcher.exe` aplica el cambio.

- Repo de releases: https://github.com/winttita/WINTER-lubricentro-management-system/releases
- Convención de versiones: semver `MAJOR.MINOR.PATCH` (tag `v0.1.0`, etc.).
- El archivo `updater.py` contiene toda la lógica de checkeo y descarga.

## Build del .exe (Windows)
Para generar el .zip distribuible:

```bat
build\build_windows.bat
```

El script:
1. Compila `build/launcher.py` con PyInstaller -> `LubricentroWinter.exe`.
2. Descarga Python embebido 3.12 (amd64), instala pip y dependencias.
3. Copia `app.py`, `database.py`, `pages/`, `updater.py` al paquete.
4. Genera `dist/LubricentroWinter_vX.Y.Z.zip`.

Subir ese .zip a una nueva GitHub Release (tag `vX.Y.Z`) para que la app lo
detecte como actualización.

### Cambiar la versión actual
Editá `APP_VERSION` en `updater.py` antes de compilar/release.