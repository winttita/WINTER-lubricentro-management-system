"""
Launcher de Lubricentro Winter.

Este script se compila a un .exe pequeño con PyInstaller:
    pyinstaller --onefile --windowed --uac-admin --name LubricentroWinter launcher.py

El launcher.exe se distribuye junto a una carpeta `runtime/` que contiene
Python embebido + dependencias. El launcher:
  1. Detecta actualización pendiente (UPDATE_LOCK): si existe update.bat
     escrito por updater.apply_update (corriendo dentro de la app), lo lanza
     y sale.
  2. Si no hay update: verifica runtime, instala deps y arranca Streamlit.

El launcher YA NO escribe update.bat; esa responsabilidad es 100% de
updater.apply_update (invocado desde app.py al confirmar el botón de update).
Esto elimina la duplicación de DOS .bat que se pisaban entre sí.
"""
from __future__ import annotations

import os
import sys
import subprocess
import time

# --- Rutas base ------------------------------------------------------------

# Si está frozen (PyInstaller), el .exe está en el directorio raíz de la app.
ROOT = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))

RUNTIME_DIR = os.path.join(ROOT, "runtime")
PYTHON_EXE = os.path.join(RUNTIME_DIR, "pythonw.exe")
APP_DIR = os.path.join(ROOT, "app")
APP_ENTRY = os.path.join(APP_DIR, "app.py")
REQUIREMENTS = os.path.join(ROOT, "requirements.txt")

# Layout de updater
UPDATE_DIR = os.path.join(ROOT, ".updates")
UPDATE_LOCK = os.path.join(UPDATE_DIR, "pending_update")
UPDATE_BAT = os.path.join(ROOT, "update.bat")
UPDATE_RETRY = os.path.join(UPDATE_DIR, "update_retry")
MAX_UPDATE_RETRIES = 3
LAUNCHER_EXE = sys.executable if getattr(sys, "frozen", False) else __file__

# --- Logging simple --------------------------------------------------------

def log(msg: str) -> None:
    """Escribe un log en _logs/launcher.log del directorio raíz."""
    log_dir = os.path.join(ROOT, "_logs")
    try:
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "launcher.log"), "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except OSError:
        pass


# --- Auto-actualización ----------------------------------------------------

def _read_retry_count() -> int:
    if not os.path.exists(UPDATE_RETRY):
        return 0
    try:
        with open(UPDATE_RETRY, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0


def _increment_retry() -> int:
    count = _read_retry_count() + 1
    try:
        os.makedirs(UPDATE_DIR, exist_ok=True)
        with open(UPDATE_RETRY, "w", encoding="utf-8") as f:
            f.write(f"{count}\n")
    except OSError:
        pass
    return count


def _clean_stale_update() -> None:
    for path in [UPDATE_LOCK, UPDATE_RETRY, UPDATE_BAT]:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass


def _cleanup_orphan_update_artifacts() -> None:
    if not os.path.exists(UPDATE_LOCK):
        if os.path.exists(UPDATE_BAT):
            log("Limpiando update.bat huerfano (sin pending_update).")
            try:
                os.remove(UPDATE_BAT)
            except OSError:
                pass


def check_and_launch_update() -> bool:
    if not os.path.exists(UPDATE_LOCK):
        _clean_stale_update()
        return False

    if not os.path.exists(UPDATE_BAT):
        log(f"Lock presente pero falta {UPDATE_BAT}. Limpiando update stale.")
        _clean_stale_update()
        return False

    retry_count = _read_retry_count()
    if retry_count >= MAX_UPDATE_RETRIES:
        log(f"Update reintentado {retry_count} veces. Limpiando y arrancando normalmente.")
        _clean_stale_update()
        return False

    retry_count = _increment_retry()
    log(f"Update pendiente, intento {retry_count}/{MAX_UPDATE_RETRIES}. Lanzando {UPDATE_BAT}...")

    CREATE_NO_WINDOW = 0x08000000
    try:
        subprocess.Popen(
            ["cmd", "/c", UPDATE_BAT],
            cwd=ROOT,
            creationflags=subprocess.DETACHED_PROCESS
                         | subprocess.CREATE_NEW_PROCESS_GROUP
                         | CREATE_NO_WINDOW,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        log(f"Error lanzando update.bat: {e}")
        return False

    log("Launcher cediendo control a update.bat...")
    return True


# --- Verificación del runtime ---------------------------------------------

def ensure_runtime() -> bool:
    if os.path.exists(PYTHON_EXE):
        return True
    log("Runtime de Python no encontrado en: " + PYTHON_EXE)
    return False


def ensure_dependencies() -> None:
    if not os.path.exists(REQUIREMENTS):
        return
    try:
        subprocess.run(
            [PYTHON_EXE if os.path.exists(PYTHON_EXE) else sys.executable,
             "-m", "pip", "install", "--no-input", "-r", REQUIREMENTS],
            cwd=ROOT, check=False,
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
            timeout=300,
        )
    except Exception as e:
        log(f"pip install fallo: {e}")


# --- Arranque de Streamlit -------------------------------------------------

def python_executable() -> list[str]:
    if os.path.exists(PYTHON_EXE):
        return [PYTHON_EXE]
    return [sys.executable]


def start_streamlit() -> int:
    entry = APP_ENTRY
    if not os.path.exists(entry):
        alt = os.path.join(ROOT, "app.py")
        if os.path.exists(alt):
            entry = alt
        else:
            log("No se encontró app.py ni en app/ ni en la raíz.")
            return 1
    cmd = python_executable() + ["-X", "utf8", "-m", "streamlit", "run", entry,
                                 "--server.headless=true", "--browser.gatherUsageStats=false"]
    log("Iniciando: " + " ".join(cmd))
    proc = subprocess.Popen(cmd, cwd=ROOT)
    time.sleep(1.5)
    try:
        import webbrowser
        webbrowser.open("http://localhost:8501")
    except Exception:
        pass
    proc.wait()
    return proc.returncode


# --- Main ------------------------------------------------------------------

def main() -> int:
    log("=== Lubricentro Winter launcher ===")

    _cleanup_orphan_update_artifacts()

    # 1. ¿Hay actualización pendiente al arrancar? Si sí, lanzar update.bat y salir.
    #    El .bat lo escribió updater.apply_update (corriendo dentro de app.py),
    #    no es responsabilidad del launcher generarlo.
    if check_and_launch_update():
        return 0

    # 2. Flujo normal
    if not ensure_runtime():
        log("Runtime no encontrado; intentando con Python del sistema.")
    ensure_dependencies()
    rc = start_streamlit()

    # 3. Tras cerrar Streamlit, NO volvemos a tocar update.bat: si se disparó
    #    una actualización mientras la app corría, update.bat ya fue lanzado
    #    por app.py (que también hace os._exit). El launcher solo reguarda el
    #    rc y sale.
    return rc


if __name__ == "__main__":
    sys.exit(main())