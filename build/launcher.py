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
import shutil
import socket
import subprocess
import sys
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

# Puerto de Streamlit (override con env LUBRICENTRO_PORT)
STREAMLIT_PORT = int(os.environ.get("LUBRICENTRO_PORT", "8501"))
BROWSER_WAIT_SECONDS = 30

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
    """Lee el contador de reintentos de update. Devuelve 0 si no existe o es inválido."""
    if not os.path.exists(UPDATE_RETRY):
        return 0
    try:
        with open(UPDATE_RETRY, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0


def _increment_retry() -> int:
    """Incrementa y persiste el contador de reintentos. Devuelve el nuevo valor."""
    count = _read_retry_count() + 1
    try:
        os.makedirs(UPDATE_DIR, exist_ok=True)
        with open(UPDATE_RETRY, "w", encoding="utf-8") as f:
            f.write(f"{count}\n")
    except OSError:
        pass
    return count


def _clean_stale_update() -> None:
    """Elimina todos los artefactos de update stale (lock, retry, bat)."""
    for path in [UPDATE_LOCK, UPDATE_RETRY, UPDATE_BAT]:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass


def _cleanup_orphan_update_artifacts() -> None:
    """Limpia update.bat y update_retry huerfanos (cuando no hay pending_update)."""
    if not os.path.exists(UPDATE_LOCK):
        for path in [UPDATE_BAT, UPDATE_RETRY]:
            if os.path.exists(path):
                log(f"Limpiando {os.path.basename(path)} huerfano (sin pending_update).")
                try:
                    os.remove(path)
                except OSError:
                    pass


def _recover_interrupted_update() -> bool:
    """
    Detecta y recupera una actualización interrumpida.
    
    Returns:
        True si se lanzó una recuperación (update.bat), False si no hay nada que hacer.
    """
    # Si hay lock pero no update.bat, verificar si hay zip para reintentar
    if os.path.exists(UPDATE_LOCK) and not os.path.exists(UPDATE_BAT):
        # Leer el path del zip desde pending_update
        zip_path = None
        try:
            with open(UPDATE_LOCK, "r", encoding="utf-8") as f:
                zip_path = f.read().strip()
        except OSError:
            pass
        
        if zip_path and os.path.exists(zip_path):
            log(f"Actualización interrumpida detectada. Reintentando con {zip_path}...")
            # Re-escribir update.bat usando el zip existente
            try:
                import updater
                updater._write_update_batch_secure(ROOT, zip_path)
            except Exception as e:
                log(f"Error reescribiendo update.bat: {e}")
                _clean_stale_update()
                return False
            # Ahora check_and_launch_update lo lanzará
            return True
        else:
            # No hay zip, verificar si hay backup para restaurar
            if os.path.exists(os.path.join(ROOT, "runtime.old")):
                log("Sin zip de update, restaurando runtime.old...")
                try:
                    if os.path.exists(os.path.join(ROOT, "runtime")):
                        shutil.rmtree(os.path.join(ROOT, "runtime"), ignore_errors=True)
                    shutil.move(os.path.join(ROOT, "runtime.old"), os.path.join(ROOT, "runtime"))
                except OSError as e:
                    log(f"Error restaurando runtime.old: {e}")
            if os.path.exists(os.path.join(ROOT, f"{os.path.basename(sys.executable)}.bak")):
                try:
                    bak = os.path.join(ROOT, f"{os.path.basename(sys.executable)}.bak")
                    shutil.copy2(bak, sys.executable)
                    os.remove(bak)
                except OSError as e:
                    log(f"Error restaurando launcher.bak: {e}")
            _clean_stale_update()
            return False
    
    # Si no hay lock pero hay residuos de update fallido (runtime.old, .bak)
    if not os.path.exists(UPDATE_LOCK):
        restored = False
        if os.path.exists(os.path.join(ROOT, "runtime.old")):
            log("Residuo runtime.old detectado sin lock de update. Restaurando...")
            try:
                if os.path.exists(os.path.join(ROOT, "runtime")):
                    shutil.rmtree(os.path.join(ROOT, "runtime"), ignore_errors=True)
                shutil.move(os.path.join(ROOT, "runtime.old"), os.path.join(ROOT, "runtime"))
                restored = True
            except OSError as e:
                log(f"Error restaurando runtime.old: {e}")
        if os.path.exists(os.path.join(ROOT, f"{os.path.basename(sys.executable)}.bak")):
            try:
                bak = os.path.join(ROOT, f"{os.path.basename(sys.executable)}.bak")
                shutil.copy2(bak, sys.executable)
                os.remove(bak)
                restored = True
            except OSError as e:
                log(f"Error restaurando launcher.bak: {e}")
        if restored:
            _clean_stale_update()
    
    return False


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


def _dependencies_missing() -> list[str]:
    """Devuelve las dependencias críticas ausentes (import fallido)."""
    missing = []
    for module in ["streamlit", "pandas"]:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    if sys.platform == "win32":
        try:
            __import__("win32print")
        except ImportError:
            missing.append("pywin32")
    return missing


def ensure_dependencies() -> None:
    """Instala dependencias SOLO si falta alguna; evita pip en cada arranque."""
    missing = _dependencies_missing()
    if not missing:
        return
    if not os.path.exists(REQUIREMENTS):
        log(f"Faltan dependencias ({', '.join(missing)}) pero no hay requirements.txt.")
        return
    log(f"Dependencias faltantes: {', '.join(missing)}. Instalando desde requirements.txt...")
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


def _wait_for_port(host: str, port: int, timeout: float = BROWSER_WAIT_SECONDS) -> bool:
    """Espera a que el puerto acepte conexiones (polling, sin sleep fijo)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


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
                                 "--server.headless=true", "--browser.gatherUsageStats=false",
                                 "--server.port", str(STREAMLIT_PORT)]
    log("Iniciando: " + " ".join(cmd))
    proc = subprocess.Popen(cmd, cwd=ROOT)
    try:
        import webbrowser
        if _wait_for_port("127.0.0.1", STREAMLIT_PORT):
            webbrowser.open(f"http://localhost:{STREAMLIT_PORT}")
        else:
            log(f"Streamlit no respondió en el puerto {STREAMLIT_PORT} tras {BROWSER_WAIT_SECONDS}s.")
    except Exception:
        pass
    proc.wait()
    return proc.returncode


# --- Main ------------------------------------------------------------------

def main() -> int:
    log("=== Lubricentro Winter launcher ===")

    _cleanup_orphan_update_artifacts()

    # 0. Recuperar actualización interrumpida si hay residuos
    if _recover_interrupted_update():
        # Si la recuperación lanzó update.bat, salir (el launcher se cede a update.bat)
        return 0

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