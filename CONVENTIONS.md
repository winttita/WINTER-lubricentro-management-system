# Convenciones del proyecto — Lubricentro Winter

Fuente única y obligatoria de convenciones para cualquiera (humano o agente) que publique contenido en nombre del proyecto: releases, commits, messages públicos, descripciones, documentación. Antes de publicar algo, consultar y respetar este archivo. Si surge una convención nueva, agregarla acá antes de aplicarla.

## 1. Propósito y alcance

Este documento rige toda comunicación pública del proyecto Lubricentro Winter: GitHub Releases, CHANGELOG, mensajes de commit, README, documentación generada y textos de la interfaz (Streamlit). Aplica a humanos y a agentes de IA.

No cubre convenciones de código Python por ahora; se agregarán más adelante si conviene.

## 2. Tono y estilo

- Formal, neutral, en tercera persona o imperativa neutra.
- Español neutro/rioplatense, sin modismos coloquiales.
- Frases cortas y descriptivas. Una idea por oración.
- Prohibido: marketing, exaggeraciones, signos de exclamación múltiples, jerga innecesaria.
- Ejemplos válidos:
  - "Se añade validación de stock en ventas."
  - "Se corrige error de conexión al cerrar reportes."
  - "Se reorganizan las páginas de Configuración."
- Ejemplos inválidos:
  - "¡Nueva release super increíble!"
  - "Ahora tenés POS con carrito loquito, disfrutalo."

## 3. Prohibición de emojis

- Prohibido el uso de emojis en:
  - GitHub Releases
  - CHANGELOG.md
  - Mensajes de commit
  - Comentarios de código
  - README y otra documentación
  - Textos visibles de la interfaz (Streamlit)
- Solo se permiten si el usuario lo solicita explícitamente.

## 4. Versionado (SemVer)

El proyecto sigue [Versionado Semántico](https://semver.org/lang/es/): `MAJOR.MINOR.PATCH`.

- **PATCH** (`0.2.2` → `0.2.3`): solo correcciones de bugs que no rompen compatibilidad.
- **MINOR** (`0.2.3` → `0.3.0`): nuevas funciones compatibles con versiones anteriores.
- **MAJOR** (`0.x` → `1.0.0`): cambios que rompen compatibilidad.
- Tags con formato `vX.Y.Z` (ej: `v0.2.3`).
- Antes de generar una release, actualizar `APP_VERSION` en `updater.py` con la misma versión del tag.

## 5. Releases y CHANGELOG

El CHANGELOG sigue el formato [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) en español:

- `Agregado` — nuevas funciones.
- `Cambiado` — cambios en funciones existentes.
- `Corregido` — correcciones de bugs.
- `Removido` — funciones eliminadas.

Reglas:

- Toda release debe tener su entrada en `CHANGELOG.md`. Prohibido publicar release sin changelog.
- Cuando una entrada afecte a una función o archivo concreto, citar con formato `archivo:función` (ej: `updater.py:_write_update_batch`).
- Citar número de issue/PR cuando exista (ej: `#42`).
- Longitud máxima por release: ~800 palabras.
- Prohibido emojis y signos de exclamación múltiples.
- El historial completo se mantiene en `CHANGELOG.md`; las GitHub Releases pueden replicar la sección correspondiente.

Ejemplo de entrada válida:

```
## [0.2.3] - 2026-07-18

### Agregado
- Sistema de usuarios con roles (admin, supervisor, operador) y autenticación básica #42
- Punto de Venta (POS) con carrito, búsqueda por código de barras y selección de cliente #45

### Corregido
- Reporte de ingresos/egresos: ahora cierra correctamente la conexión a la base de datos
- Updater: función `updater.py:_write_update_batch` faltante que causaba error al instalar actualizaciones
```

## 6. Conventional Commits

Los mensajes de commit siguen [Conventional Commits](https://www.conventionalcommits.org/) en español:

```
<tipo>(scope): descripción en presente y minúsculas

cuerpo opcional
```

Tipos habituales:

- `feat` — nueva función.
- `fix` — corrección de bug.
- `docs` — solo documentación.
- `chore` — tareas de mantenimiento.
- `refactor` — refactorización sin cambio de comportamiento.
- `test` — agregar o corregir tests.
- `ci` — cambios en CI/CD o workflows.
- `build` — cambios en el sistema de build.

Ejemplos válidos:

```
feat(ventas): añade validación de stock antes de crear una venta
fix(ci): corrige sintaxis PowerShell en release.yml
docs: aclara policy de versiones en README
```

Ejemplos inválidos:

```
Arreglé el bug del updater ;)
Actualicé cosas varias
```

## 7. CI/CD — Auto-corrección de builds fallidos

Si un push a `main` o un tag dispara un workflow de GitHub Actions y este falla, el agente **debe corregirlo automáticamente**. Procedimiento:

1. Leer el log del paso fallido:
   ```
   gh run view <run-id> --log-failed
   ```
2. Diagnosticar la causa raíz.
3. Aplicar la corrección mínima necesaria (sin re-arquitectura).
4. Ejecutar localmente `pytest` antes de un nuevo commit.
5. Commitear con mensaje `fix(ci): <descripción>` o `fix(build): <descripción>`, referenciando el workflow afectado en el cuerpo.
6. Volver a pushear.
7. Revisar el resultado de la nueva ejecución.

Límites y controles:

- Máximo 3 intentos de auto-corrección. Después, escalar al usuario.
- Confirmar con el usuario antes de commitear si la corrección afecta a más de 3 archivos.
- Si la falla es reproducible y no se arregla con cambio de código (ej: problema de credenciales, límite de rate), no investigar más y avisar al usuario.

Esta regla aplica también durante el flujo de release: no dejar una release rota.

## 8. Build Windows

Para generar el `.zip` distribuible:

```
build\build_windows.bat
```

Reglas:

- El `.zip` debe generarse desde un working tree limpio (sin archivos stale).
- Actualizar `APP_VERSION` en `updater.py` antes de compilar.
- Resultado: `dist/LubricentroWinter_vX.Y.Z.zip`.
- Adjuntar ese `.zip` a la GitHub Release del tag `vX.Y.Z` correspondiente.
- No subir el `.zip` a `main`; vive solo en la release.

## 9. Higiene del repo

No commitear:

- Backups y archivos temporales: `*.backup`, `*.backup2`, `*.with_my_updates`, `stash.patch`.
- Base de datos local: `lubricentro.db`.
- Salidas de build: `dist/`, `build_launcher/`, `.updates/`, `_logs/`.
- Caches de Python: `__pycache__/`, `.pytest_cache/`.
- Entorno virtual: `venv/`.

Estos patrones están reflejados en `.gitignore`.

Si se necesita un archivo temporal para trabajo intermedio, guardarlo fuera del repo (en `/tmp` o subDirectorio no trackeado) y borrarlo al terminar.

## 10. Actualización de este documento

Cuando surja una convención nueva:

1. Agregarla en la sección correspondiente de este archivo (o crear una sección nueva).
2. Reflejar el cambio en `CHANGELOG.md` bajo `### Cambiado` con una línea corta.
3. Si la convención afecta a `AGENTS.md` (ej: carga automática en cada sesión), actualizarlo también.

## 11. Uso de este documento

Este documento es obligatorio. Antes de publicar cualquier release, commit, mensaje público o descripción formal asociada al proyecto, se debe consultar y respetar este archivo. Si surge una convención nueva, agregarla acá antes de aplicarla.
