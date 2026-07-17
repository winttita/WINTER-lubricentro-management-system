# Changelog - Lubricentro Winter

Todas las versiones notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

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
