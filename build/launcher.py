"""
Launcher de Lubricentro Winter.

Este script se compila a un .exe pequeño con PyInstaller:
    pyinstaller --onefile --windowed --name LubricentroWinter launcher.py

El launcher.exe se distribuye junto a una carpeta `runtime/` que contiene
Python embebido + dependencias. El launcher:
  1. Detecta actualización pendiente (update_lock)
  2. Si hay update: escribe update.bat, lo lanza con PID actual y sale
  3. Si no hay update: verifica runtime, instala deps y arranca Streamlit

Debe mantenerse MÍNIMO para que el PyInstaller one-file sea pequeño y rápido
de descargar (las deps pesadas viven en runtime/, no dentro del .exe).
"""
from __future__ import annotations

import os
import sys
import shutil
import subprocess
import zipfile
import time
import tempfile

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

def _write_update_batch(zip_path: str, pid: int) -> str:
    """
    Escribe update.bat que:
      1. Espera a que termine el proceso PID (el launcher actual)
      2. Reemplaza LubricentroWinter.exe por el nuevo (si vino en el zip)
      3. Descomprime el zip en ROOT
      4. Lanza el nuevo .exe
    Devuelve la ruta al batch escrito.
    """
    bat_path = os.path.join(ROOT, "update.bat")
    # Launcher exe name (with .exe)
    launcher_name = os.path.basename(LAUNCHER_EXE)
    # Escape backslashes for the batch file content
    root_escaped = ROOT.replace("\\", "\\\\")
    zip_escaped = zip_path.replace("\\", "\\\\")
    bat_content = rf"""@echo off
REM ========================================================================
REM Auto-update batch para Lubricentro Winter
REM Se ejecuta después de que el launcher descargue una actualización.
REM ========================================================================

setlocal enabledelayedexpansion

set ROOT=%~dp0
set ZIP_PATH={zip_escaped}
set PID={pid}
set LAUNCHER={launcher_name}

REM Esperar a que termine el launcher anterior (PID %PID%).
REM findstr con /C y < nul: no interactivo, no espera stdin.
:WAIT_LOOP
tasklist /FI "PID eq %PID%" /NH 2>nul < nul | findstr /C:"%PID%" >nul 2>&1
if errorlevel 1 (
    goto DONE_WAIT
) else (
    timeout /t 1 /nobreak >nul
    goto WAIT_LOOP
)
:DONE_WAIT

echo [UPDATE] Aplicando actualizacion desde %ZIP_PATH%...

REM Backup del launcher actual por si acaso
if exist "%ROOT%\{launcher_name}.bak" del "%ROOT%\{launcher_name}.bak"
if exist "%ROOT%\{launcher_name}" rename "%ROOT%\{launcher_name}" "{launcher_name}.bak"

REM Descomprimir el zip (sobrescribe todo: app/, runtime/, etc.)
powershell -NoProfile -WindowStyle Hidden -Command "Expand-Archive -Force -Path '{zip_escaped}' -DestinationPath '{root_escaped}'"

REM Verificar que el nuevo launcher existe
if not exist "%ROOT%\{launcher_name}" (
    if exist "%ROOT%\{launcher_name}.bak" rename "%ROOT%\{launcher_name}.bak" "{launcher_name}"
    exit /b 1
)

echo [UPDATE] Limpieza...
if exist "%ZIP_PATH%" del "%ZIP_PATH%"
if exist "%ROOT%\{launcher_name}.bak" del "%ROOT%\{launcher_name}.bak"
if exist "%ROOT%\.updates\pending_update" del "%ROOT%\.updates\pending_update"

echo [UPDATE] Iniciando nueva version...
start "" "%ROOT%\{launcher_name}"

REM Autoborrado del .bat (no se puede del mientras corre)
(goto) 2>nul & del "%~f0"

exit /b 0
"""
    with open(bat_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(bat_content)
    return bat_path


def check_and_launch_update() -> bool:
    """
    Si existe UPDATE_LOCK:
      - Lee la ruta del zip descargado
      - Escribe update.bat
      - Lanza update.bat con PID actual (detached)
      - Sale (return True => el caller debe hacer sys.exit(0))
    Si no hay lock, return False.
    """
    if not os.path.exists(UPDATE_LOCK):
        return False

    try:
        with open(UPDATE_LOCK, "r", encoding="utf-8") as f:
            zip_path = f.read().strip()
    except OSError:
        return False

    if not zip_path or not os.path.exists(zip_path):
        log(f"Lock apunta a archivo inexistente: {zip_path}")
        try:
            os.remove(UPDATE_LOCK)
        except OSError:
            pass
        return False

    log(f"Actualización pendiente detectada: {zip_path}")

    # Escribir update.bat y lanzarlo
    pid = os.getpid()
    bat_path = _write_update_batch(zip_path, pid)
    log(f"Escrito {bat_path} para PID {pid}")

    # Lanzar detached y sin ventana visible
    CREATE_NO_WINDOW = 0x08000000
    try:
        subprocess.Popen(
            ["cmd", "/c", bat_path],
            cwd=ROOT,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW,
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
    if check_and_launch_update():
        return 0

    # 2. Flujo normal
    if not ensure_runtime():
        log("Runtime no encontrado; intentando con Python del sistema.")
    ensure_dependencies()
    rc = start_streamlit()

    # 3. Después de que Streamlit termine, verificar si hubo una actualización disparada en runtime
    if os.path.exists(UPDATE_LOCK):
        zip_path = ""
        try:
            with open(UPDATE_LOCK, "r", encoding="utf-8") as f:
                zip_path = f.read().strip()
        except OSError:
            zip_path = ""
        if zip_path and os.path.exists(zip_path):
            pid = os.getpid()
            bat_path = _write_update_batch(zip_path, pid)
            log("Actualización pendiente tras cierre de Streamlit. Lanzando update.bat...")
            try:
                CREATE_NO_WINDOW = 0x08000000
                subprocess.Popen(
                    ["cmd", "/c", bat_path],
                    cwd=ROOT,
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                log(f"Error lanzando update.bat: {e}")
        else:
            log("UPDATE_LOCK presente pero zip no encontrado; ignorando.")
    return rc


if __name__ == "__main__":
    sys.exit(main())