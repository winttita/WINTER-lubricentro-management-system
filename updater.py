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
from typing import Optional, Tuple

# --- Configuración ----------------------------------------------------------

# Repo GitHub en formato "usuario/repos". Se puede sobreescribir con la variable
# de entorno LUBRICENTRO_REPO para apuntar a otro fork/proyecto de pruebas.
GITHUB_REPO = os.environ.get("LUBRICENTRO_REPO", "winttita/WINTER-lubricentro-management-system")

# Versión actual de la aplicación. Se compara contra el tag de la última release.
APP_VERSION = "0.2.0"

# Nombre esperado del asset (el .exe) dentro de la release. Si se cambia, basta
# con editar esta constante. Se busca por substring (ej: "LubricentroWinter.exe"
# encontrará "LubricentroWinter.exe" y eventual variantes "_portable.zip").
ASSET_NAME_HINT = "LubricentroWinter"

# Timeout de red para las peticiones a la API (segundos).
NETWORK_TIMEOUT = 15

# Carpeta local donde se guardan descargas e información de actualización.
UPDATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".updates")

# Archivo de marca dejado por el updater para que el launcher aplique el cambio
# al próximo inicio. Contiene la ruta absoluta del binario descargado.
UPDATE_LOCK = os.path.join(UPDATE_DIR, "pending_update")

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
    Busca dentro de los assets de una release aquel cuyo nombre contiene
    `hint`. Devuelve el asset (dict) o None si no hay coincidencia.

    Prioriza, en orden:
      1. Archivos .zip (paquete completo para el modo launcher/Python embebido).
      2. Archivos .exe (binario standalone, cuando se use PyInstaller).
    """
    assets = release.get("assets", []) or []
    if not assets:
        return None
    # Priorizar .zip
    for a in assets:
        name = a.get("name", "")
        if hint.lower() in name.lower() and name.lower().endswith(".zip"):
            return a
    for a in assets:
        name = a.get("name", "")
        if hint.lower() in name.lower() and name.lower().endswith(".exe"):
            return a
    # Fallback: cualquier asset con el hint
    for a in assets:
        if hint.lower() in a.get("name", "").lower():
            return a
    return None


# --- Descarga --------------------------------------------------------------

def download_asset(asset: dict, dest_dir: str = UPDATE_DIR,
                   progress_callback=None) -> str:
    """
    Descarga un asset a dest_dir y devuelve la ruta al archivo descargado.

    `progress_callback(downloaded_bytes, total_bytes)` se invoca periódicamente
    durante la descarga para reportar progreso (ej: para Streamlit).
    """
    if not asset or "browser_download_url" not in asset:
        raise UpdateError("Asset inválido o sin URL de descarga")
    url = asset["browser_download_url"]
    name = asset.get("name", "update_download.bin")
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, name)

    headers = {"User-Agent": "LubricentroWinter-Updater/1.0"}
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=NETWORK_TIMEOUT) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            with open(dest_path, "wb") as f:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total)
    except urllib.error.URLError as e:
        raise UpdateError(f"Error descargando {name}: {e.reason}")
    return dest_path


# --- Aplicación ------------------------------------------------------------


def apply_update(downloaded_path: str) -> str:
    """
    Marca `downloaded_path` como actualización pendiente y escribe update.bat.
    Devuelve el path al lock file creado.

    El launcher leerá UPDATE_LOCK en el próximo arranque, lanzará update.bat
    con su PID y saldrá. update.bat esperará a que el proceso muera,
    descomprimirá el zip (incluyendo el nuevo .exe) y relanzará la app.
    """
    os.makedirs(UPDATE_DIR, exist_ok=True)
    with open(UPDATE_LOCK, "w", encoding="utf-8") as f:
        f.write(downloaded_path + "\n")
    # Escribir también el script de post-update
    root = os.path.dirname(UPDATE_DIR)
    _write_update_bat(root, downloaded_path)
    return UPDATE_LOCK


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
