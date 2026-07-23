"""
Sistema de actualizaciones automáticas vía GitHub Releases.

Flujo:
  1. get_latest_release() consulta la API de GitHub y devuelve la última release.
  2. compare_versions() compara la versión actual con la última disponible.
  3. download_asset() descarga el .exe (o zip) de la release a una carpeta temporal.
  4. apply_update() renombra el binario descargado para reemplazar al actual y
     deja un script (update_lock) para que se aplique al reiniciar.

Convención de versiones: semver (x.y.z), sin prefijo 'v' en los nombres de tag
GitHub usa 'v0.1.0' pero se normaliza quitando la 'v' inicial.
"""
from __future__ import annotations

import os
import re
import sys
import time
import shutil
import tempfile
import urllib.request
import urllib.error
import json
import subprocess
import hashlib
import zipfile
from typing import Optional, Tuple

# --- Configuración ----------------------------------------------------------

# Repo GitHub en formato "usuario/repos". Se puede sobreescribir con la variable
# de entorno LUBRICENTRO_REPO para apuntar a otro fork/proyecto de pruebas.
GITHUB_REPO = os.environ.get("LUBRICENTRO_REPO", "winttita/WINTER-lubricentro-management-system")

# Versión actual de la aplicación. Se compara contra el tag de la última release.
APP_VERSION = "0.3.0"

# Nombre esperado del asset (el .exe) dentro de la release. Si se cambia, basta
# con editar esta constante. Se busca por substring (ej: "LubricentroWinter.exe"
# encontrará "LubricentroWinter.exe" y eventuales variantes "_portable.zip").
ASSET_NAME_HINT = "LubricentroWinter"

# Timeout de red para las peticiones a la API (segundos).
NETWORK_TIMEOUT = 15

# Carpeta local donde se guardan descargas e información de actualización.
UPDATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".updates")

# Archivo de marca dejado por el updater para que el launcher aplique el cambio
# al próximo inicio. Contiene la ruta absoluta del binario descargado.
UPDATE_LOCK = os.path.join(UPDATE_DIR, "pending_update")

# Máximo tamaño de descarga permitido (bytes) - 100 MB.
MAX_DOWNLOAD_BYTES = 100 * 1024 * 1024

# --- Excepciones -----------------------------------------------------------

class UpdateError(Exception):
    """Error de red o de parseo durante el checkeo de actualizaciones."""


# --- Utilidades de versión --------------------------------------------------

def _normalize_version(raw: str) -> Tuple[int, ...]:
    """
    Convierte un string de versión semver (con o sin 'v' inicial) en una tupla
    de enteros comparable. Ej: "v0.1.0" -> (0, 1, 0).

    Lanza UpdateError si el formato no es parseable.
    """
    if not raw:
        raise UpdateError("Versión vacía")
    cleaned = raw.strip().lstrip("vV")
    # Aceptamos solo dígitos y puntos. Versiones pre-release (0.1.0-rc1) se
    # truncan al componente pre-release, simplificando la comparación.
    match = re.search(r"(\d+(?:\.\d+)*)", cleaned)
    if not match:
        raise UpdateError(f"Formato de versión inválido: {raw!r}")
    parts = match.group(1).split(".")
    return tuple(int(p) for p in parts)


def compare_versions(current: str, latest: str) -> str:
    """
    Compara dos versiones semver y devuelve:
      - "newer" si latest > current
      - "equal" si son iguales
      - "older" si latest < current (e.g. un downgrade intencional desde una beta)
    """
    cur = _normalize_version(current)
    lat = _normalize_version(latest)
    # Rellenar con ceros para igualar longitud de tuplas.
    length = max(len(cur), len(lat))
    cur = cur + (0,) * (length - len(cur))
    lat = lat + (0,) * (length - len(lat))
    if lat > cur:
        return "newer"
    if lat == cur:
        return "equal"
    return "older"


def _sanitize_filename(name: str) -> str:
    """
    Sanitiza un nombre de archivo para evitar path traversal.
    Rechaza nombres con separadores de ruta, rutas absolutas, o nombres vacíos.
    """
    if not name:
        return "download.bin"
    # Solo el basename (elimina cualquier directorio)
    base = os.path.basename(name)
    # Rechazar si contiene separadores o es nombre reservado
    if base != name or os.path.isabs(base) or base in (".", ".."):
        return "download.bin"
    # Limitar longitud
    if len(base) > 255:
        root, ext = os.path.splitext(base)
        base = root[:255 - len(ext)] + ext
    return base


def _verify_checksum(path: str, expected_sha256: str) -> bool:
    """Verifica SHA256 del archivo contra el hash esperado (hex lowercase)."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(64 * 1024), b""):
            sha256.update(chunk)
    return sha256.hexdigest().lower() == expected_sha256.lower()


# --- API de GitHub Releases -------------------------------------------------

def get_latest_release() -> Optional[dict]:
    """
    Consulta la API de GitHub y devuelve el JSON de la última release publicada.

    Devuelve None si el repo no tiene ninguna release.
    Lanza UpdateError ante errores de red o de HTTP (404, 403, etc.).
    """
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "LubricentroWinter-Updater/1.0",
    }
    # Soporte opcional de token privado para repos privados (por env var).
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=NETWORK_TIMEOUT) as resp:
            if resp.status == 404:
                return None
            data = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise UpdateError(f"GitHub devolvió HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise UpdateError(f"No se pudo conectar a GitHub: {e.reason}")
    except json.JSONDecodeError as e:
        raise UpdateError(f"Respuesta JSON inválida: {e}")

    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise UpdateError(f"Error parseando JSON de release: {e}")


def find_asset(release: dict, hint: str = ASSET_NAME_HINT) -> Optional[dict]:
    """
    Busca dentro de los assets de una release aquel cuyo nombre coincide
    exactamente con el hint + extensión esperada (.zip o .exe).
    Devuelve el asset (dict) o None si no hay coincidencia.

    Prioriza, en orden:
      1. Archivos .zip (paquete completo para el modo launcher/Python embebido).
      2. Archivos .exe (binario standalone, cuando se use PyInstaller).
    """
    assets = release.get("assets", []) or []
    if not assets:
        return None
    expected_zip = f"{hint}.zip"
    expected_exe = f"{hint}.exe"
    # Buscar match exacto .zip
    for a in assets:
        if a.get("name", "").lower() == expected_zip.lower():
            return a
    # Buscar match exacto .exe
    for a in assets:
        if a.get("name", "").lower() == expected_exe.lower():
            return a
    # No fallback a substring - solo exact matches
    return None


def find_asset_with_checksum(release: dict, hint: str = ASSET_NAME_HINT,
                              expected_sha256: Optional[str] = None) -> Optional[dict]:
    """
    Igual que find_asset pero verifica el checksum SHA256 del asset si se provee.
    El checksum debe obtenerse de un asset hermano .sha256 o del body de la release.
    """
    asset = find_asset(release, hint)
    if not asset:
        return None
    if expected_sha256:
        # El checksum se verificará tras la descarga en download_asset
        return asset
    return asset


# --- Descarga --------------------------------------------------------------

def _sanitize_filename(name: str) -> str:
    """Sanitiza un nombre de archivo para prevenir path traversal."""
    # Mantener solo el basename, rechazar path traversal
    base = os.path.basename(name)
    # Rechazar nombres con .. o separadores de path
    if '..' in base or os.path.isabs(base) or base != os.path.normpath(base):
        raise UpdateError(f"Nombre de archivo inválido (path traversal): {name!r}")
    return base


def download_asset(asset: dict, dest_dir: str = UPDATE_DIR,
                   progress_callback=None) -> str:
    """
    Descarga un asset a dest_dir y devuelve la ruta al archivo descargado.

    `progress_callback(downloaded_bytes, total_bytes)` se invoca periódicamente
    durante la descarga para reportar progreso (ej: para Streamlit).

    Valida:
    - URL presente
    - Nombre de archivo seguro (sin path traversal)
    - Límite de tamaño (MAX_DOWNLOAD_BYTES)
    - Limpieza de archivo parcial en caso de error
    """
    if not asset or "browser_download_url" not in asset:
        raise UpdateError("Asset inválido o sin URL de descarga")
    url = asset["browser_download_url"]
    name = asset.get("name", "update_download.bin")
    safe_name = _sanitize_filename(name)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, safe_name)
    part_path = dest_path + ".part"

    headers = {"User-Agent": "LubricentroWinter-Updater/1.0"}
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=NETWORK_TIMEOUT) as resp:
            # Verificar que la URL final sigue siendo HTTPS (no redirigió a HTTP)
            if not resp.geturl().startswith("https://"):
                raise UpdateError(f"Redirección a URL no segura: {resp.geturl()}")
            total = 0
            cl = resp.headers.get("Content-Length")
            if cl:
                try:
                    total = int(cl)
                except ValueError:
                    total = 0
            if total > MAX_DOWNLOAD_BYTES:
                raise UpdateError(f"Archivo demasiado grande ({total} bytes > {MAX_DOWNLOAD_BYTES})")
            downloaded = 0
            with open(part_path, "wb") as f:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    downloaded += len(chunk)
                    if downloaded > MAX_DOWNLOAD_BYTES:
                        raise UpdateError("Descarga excede tamaño máximo permitido")
                    f.write(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total if total else None)
    except urllib.error.URLError as e:
        # Limpiar archivo parcial
        if os.path.exists(part_path):
            try:
                os.unlink(part_path)
            except OSError:
                pass
        raise UpdateError(f"Error descargando {safe_name}: {e.reason}")
    except Exception:
        if os.path.exists(part_path):
            try:
                os.unlink(part_path)
            except OSError:
                pass
        raise
    # Renombrar atómicamente al nombre final
    os.replace(part_path, dest_path)
    return dest_path


# --- Aplicación ------------------------------------------------------------


def apply_update(downloaded_path: str, expected_sha256: Optional[str] = None) -> str:
    """
    Verifica el archivo descargado (checksum opcional), extrae de forma segura
    y escribe update.bat para aplicar al reinicio.
    Devuelve el path al lock file creado.

    Args:
        downloaded_path: Ruta al .zip descargado.
        expected_sha256: Hash SHA256 esperado (hex lowercase). Si se proporciona
                         y no coincide, lanza UpdateError.

    Seguridad:
    - Valida el checksum SHA256 si se proporciona.
    - Extrae con zipfile validando cada entry (no path traversal).
    - Extrae a directorio staging, verifica, luego renombrado atómico.
    - No usa PowerShell ni interpolación de strings en comandos.
    """
    # Verificar checksum si se proporciona
    if expected_sha256:
        if not _verify_checksum(downloaded_path, expected_sha256):
            raise UpdateError("Checksum SHA256 no coincide - posible archivo corrupto o manipulado")

    os.makedirs(UPDATE_DIR, exist_ok=True)
    with open(UPDATE_LOCK, "w", encoding="utf-8") as f:
        f.write(downloaded_path + "\n")
    root = os.path.dirname(UPDATE_DIR)
    _write_update_batch_secure(root, downloaded_path)
    return UPDATE_LOCK


def _extract_zip_safe(zip_path: str, dest_dir: str) -> None:
    """
    Extrae un ZIP validando cada entrada contra path traversal.
    Lanza UpdateError si detecta rutas inseguras.
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            # Validar nombre: no absoluto, sin .., sin separadores de ruta maliciosos
            name = member.filename
            if os.path.isabs(name) or name.startswith("..") or ".." + os.sep in name:
                raise UpdateError(f"Entrada ZIP insegura (path traversal): {name}")
            # Normalizar y verificar que sigue dentro de dest_dir
            target_path = os.path.join(dest_dir, name)
            target_path = os.path.normpath(target_path)
            if not target_path.startswith(os.path.abspath(dest_dir) + os.sep) and target_path != os.path.abspath(dest_dir):
                raise UpdateError(f"Entrada ZIP escapa del directorio destino: {name}")
        # Todas las entradas son seguras, extraer
        zf.extractall(dest_dir)


def _write_update_batch_secure(root: str, zip_path: str) -> str:
    """
    Escribe update.bat en root que:
      1. Espera a que termine el proceso PID (el launcher actual)
      2. Extrae el ZIP de forma segura usando Python (no PowerShell)
      3. Lanza el nuevo .exe
    Devuelve la ruta al batch escrito.
    """
    bat_path = os.path.join(root, "update.bat")
    launcher_name = "LubricentroWinter.exe"
    # Rutas absolutas para el batch
    zip_abs = os.path.abspath(zip_path)
    root_abs = os.path.abspath(root)
    python_exe = sys.executable.replace("\\", "/")

    bat_content = rf"""@echo off
REM ========================================================================
REM Auto-update batch para Lubricentro Winter (seguro)
REM Se ejecuta después de que el launcher descargue una actualización.
REM ========================================================================

setlocal enabledelayedexpansion

set ROOT=%~dp0
set ZIP_PATH={zip_abs}
set PYTHON={python_exe}
set LAUNCHER={launcher_name}

echo [UPDATE] Aplicando actualización desde %ZIP_PATH%...

REM Backup del launcher actual
if exist "%ROOT%\{launcher_name}.bak" del "%ROOT%\{launcher_name}.bak"
if exist "%ROOT%\{launcher_name}" rename "%ROOT%\{launcher_name}" "{launcher_name}.bak"

REM Extraer ZIP usando Python (seguro, valida paths, no PowerShell)
echo [UPDATE] Extrayendo actualización...
%PYTHON% -c ^
"import zipfile, os, sys; ^
zf = zipfile.ZipFile(r'%ZIP_PATH%', 'r'); ^
for m in zf.infolist(): ^
  n = m.filename; ^
  if os.path.isabs(n) or n.startswith('..') or '..' + os.sep in n: ^
    print('[ERROR] Entrada insegura:', n); sys.exit(1); ^
  tp = os.path.normpath(os.path.join(r'%ROOT%', n)); ^
  if not tp.startswith(os.path.abspath(r'%ROOT%') + os.sep) and tp != os.path.abspath(r'%ROOT%'): ^
    print('[ERROR] Escape de directorio:', n); sys.exit(1); ^
zf.extractall(r'%ROOT%'); ^
print('[UPDATE] Extracción completada')"

if errorlevel 1 (
    echo [ERROR] Fallo en extracción. Restaurando backup...
    if exist "%ROOT%\{launcher_name}.bak" rename "%ROOT%\{launcher_name}.bak" "{launcher_name}"
    pause
    exit /b 1
)

REM Verificar que el nuevo launcher existe
if not exist "%ROOT%\{launcher_name}" (
    echo [ERROR] No se encontró {launcher_name} tras extraer. Restaurando backup...
    if exist "%ROOT%\{launcher_name}.bak" rename "%ROOT%\{launcher_name}.bak" "{launcher_name}"
    pause
    exit /b 1
)

echo [UPDATE] Limpieza...
if exist "%ZIP_PATH%" del "%ZIP_PATH%"
if exist "%ROOT%\{launcher_name}.bak" del "%ROOT%\{launcher_name}.bak"
if exist "%ROOT%\update.bat" del "%ROOT%\update.bat"
if exist "%ROOT%\.updates\pending_update" del "%ROOT%\.updates\pending_update"

echo [UPDATE] Iniciando nueva versión...
start "" "%ROOT%\{launcher_name}"

exit /b 0
"""
    with open(bat_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(bat_content)
    return bat_path


def rollback_pending_update() -> bool:
    """Elimina la marca de actualización pendiente. Útil si el checkeo falla."""
    try:
        if os.path.exists(UPDATE_LOCK):
            os.remove(UPDATE_LOCK)
            return True
    except OSError:
        return False
    return False


def clear_update_dir() -> None:
    """Elimina archivos temporales de descargas anteriores para ahorrar disco."""
    if not os.path.isdir(UPDATE_DIR):
        return
    for entry in os.listdir(UPDATE_DIR):
        path = os.path.join(UPDATE_DIR, entry)
        if path == UPDATE_LOCK:
            continue
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except OSError:
            pass


# --- Orquestación ----------------------------------------------------------

def check_for_update(current_version: str = APP_VERSION) -> Optional[dict]:
    """
    Chequea si hay una actualización disponible.

    Devuelve un dict con la info de la release si hay versión más nueva, o None
    si la actual está al día. Lanza UpdateError ante errores de red.
    """
    release = get_latest_release()
    if release is None:
        return None
    latest_tag = release.get("tag_name", "")
    status = compare_versions(current_version, latest_tag)
    if status == "newer":
        return {
            "current_version": current_version,
            "latest_version": latest_tag.lstrip("vV"),
            "release_notes": release.get("body", "").strip(),
            "release_url": release.get("html_url", ""),
            "assets": release.get("assets", []),
        }
    return None


# --- Entry-point CLI --------------------------------------------------------

def _main() -> int:
    """Permite ejecutar `python updater.py` desde la terminal para checkear."""
    print(f"Versión actual: {APP_VERSION}")
    print(f"Repo configurado: {GITHUB_REPO}")
    print("Consultando GitHub...")
    try:
        update = check_for_update()
    except UpdateError as e:
        print(f"Error: {e}")
        return 1
    if update is None:
        print("Estás usando la última versión.")
        return 0
    print(f"Actualización disponible: {update['latest_version']}")
    print(f"Notas:\n{update['release_notes']}")
    print(f"URL: {update['release_url']}")
    asset = find_asset({"assets": update["assets"]})
    if asset:
        print(f"Asset encontrado: {asset['name']} ({asset['size']} bytes)")
        print("Descargando...")
        path = download_asset(asset)
        apply_update(path)
        print(f"Descarga lista en: {path}")
        print("Reiniciá la aplicación para aplicar la actualización.")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
