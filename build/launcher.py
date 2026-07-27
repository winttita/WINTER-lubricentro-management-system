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

def check_and_launch_update() -> bool:
    """
    Si existe UPDATE_LOCK y el .bat está presente (escrito por updater.apply_update):
      - Lanza update.bat (detached, sin ventana)
      - Sale (return True => el caller debe hacer sys.exit(0))

    Si solo existe UPDATE_LOCK pero no update.bat, limpia el lock (estado stale)
    y devuelve False para seguir con flujo normal.
    """
    if not os.path.exists(UPDATE_LOCK):
        return False

    # Limpiar locks stale (zip borrado o ausente)
    try:
        with open(UPDATE_LOCK, "r", encoding="utf-8") as f:
            zip_path = f.read().strip()
    except OSError:
        return False

    if not zip_path or not os.path.exists(zip_path):
        log(f"Lock stale: zip inexistente {zip_path}. Limpiando.")
        try:
            os.remove(UPDATE_LOCK)
        except OSError:
            pass
        return False

    # El .bat DEBE existir: lo escribió apply_update cuando el usuario confirmó.
    if not os.path.exists(UPDATE_BAT):
        log(f"Lock presente pero falta {UPDATE_BAT}. Abortando update, limpiando.")
        try:
            os.remove(UPDATE_LOCK)
        except OSError:
            pass
        return False

    log(f"Update pendiente: {zip_path}. Lanzando {UPDATE_BAT}...")
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