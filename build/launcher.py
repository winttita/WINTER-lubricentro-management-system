"""
Launcher de Lubricentro Winter.

Este script se compila a un .exe pequeño con PyInstaller:
    pyinstaller --onefile --name LubricentroWinter launcher.py

El launcher.exe se distribuye junto a una carpeta `runtime/` que contiene
Python embebido + dependencias. El launcher:
  1. Aplica actualizaciones pendientes (update_lock) reemplazando archivos.
  2. Verifica/instala dependencias en primera ejecución.
  3. Arranca Streamlit y abre el navegador.

Debe mantenerse MÍNIMO para que el PyInstaller one-file sea pequeño y rápido
de descargar (las deps pesadas viven en runtime/, no dentro del .exe).
"""
from __future__ import annotations

import os
import sys
import shutil
import hashlib
import subprocess
import tempfile
import zipfile
import time
import urllib.request
import urllib.error
import json

# --- Rutas base ------------------------------------------------------------

# Si está frozen (PyInstaller), el .exe está en el directorio raíz de la app.
ROOT = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))

RUNTIME_DIR = os.path.join(ROOT, "runtime")
PYTHON_EXE = os.path.join(RUNTIME_DIR, "pythonw.exe")
APP_DIR = os.path.join(ROOT, "app")
APP_ENTRY = os.path.join(APP_DIR, "app.py")
REQUIREMENTS = os.path.join(ROOT, "requirements.txt")

# Mismo layout de updater
UPDATE_DIR = os.path.join(ROOT, ".updates")
UPDATE_LOCK = os.path.join(UPDATE_DIR, "pending_update")
# Ruta donde se copia el launcher.exe en cada arranque para poder sobrescribirlo
LAUNCHER_EXE = sys.executable if getattr(sys, "frozen", False) else __file__


# --- Logging simple --------------------------------------------------------

def log(msg: str) -> None:
    """Escribe un log en updates/install.log del directorio raíz."""
    log_dir = os.path.join(ROOT, "_logs")
    try:
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "launcher.log"), "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except OSError:
        pass


# --- Aplicación de actualizaciones ----------------------------------------

def apply_pending_update() -> bool:
    """
    Si existe un update lock, renombra/mueve los archivos descargados al
    directorio raíz. En Windows no se puede sobrescribir un .exe en ejecución,
    pero el .exe en sí (launcher) no cambia; lo que cambia es el contenido
    de runtime/ y app/. El updater descarga un .zip y acá se descomprime.
    """
    if not os.path.exists(UPDATE_LOCK):
        return False
    try:
        with open(UPDATE_LOCK, "r", encoding="utf-8") as f:
            target = f.read().strip()
        if not target or not os.path.exists(target):
            log(f"Lock apunta a archivo inexistente: {target}")
            os.remove(UPDATE_LOCK)
            return False
        log(f"Aplicando actualización desde: {target}")
        # Si es zip, descomprimir en ROOT
        if target.lower().endswith(".zip"):
            with zipfile.ZipFile(target) as zf:
                zf.extractall(ROOT)
            log("Descompresión completa.")
        else:
            # Caso de binario standalone (PyInstaller one-file completo):
            # reemplazar el launcher.exe por el nuevo.
            # En Windows hacerlo in-place es problemático, así que renombramos
            # el viejo con .bak y copiamos el nuevo.
            backup = LAUNCHER_EXE + ".bak"
            try:
                if os.path.exists(backup):
                    os.remove(backup)
                os.rename(LAUNCHER_EXE, backup)
                shutil.copy2(target, LAUNCHER_EXE)
                log("Launcher reemplazado.")
            except OSError as e:
                log(f"No se pudo reemplazar el launcher: {e}")
        os.remove(UPDATE_LOCK)
        log("Actualización aplicada.")
        return True
    except Exception as e:
        log(f"Error aplicando actualización: {e}")
        return False


# --- Verificación del runtime ---------------------------------------------

def ensure_runtime() -> bool:
    """
    Verifica que runtime/pythonw.exe exista. Si no, instruimos al usuario a
    reinstalar o descargar el paquete completo. En una versión futura podría
    descargar automáticamente el runtime desde GitHub Releases.
    """
    if os.path.exists(PYTHON_EXE):
        return True
    log("Runtime de Python no encontrado en: " + PYTHON_EXE)
    return False


def ensure_dependencies() -> None:
    """
    Ejecuta `pip install -r requirements.txt` en el runtime embebido si la
    carpeta runtime/ está presente. Pip no viene en python-embed por defecto;
    el script de build se encarga de meter pip ahí.
    """
    if not os.path.exists(REQUIREMENTS):
        return
    try:
        subprocess.run(
            [sys.executable if not getattr(sys, "frozen", False) else PYTHON_EXE,
             "-m", "pip", "install", "--no-input", "-r", REQUIREMENTS],
            cwd=ROOT, check=False,
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
            timeout=300,
        )
    except Exception as e:
        log(f"pip install fallo: {e}")


# --- Arranque de Streamlit -------------------------------------------------

def python_executable() -> list[str]:
    """Devuelve argv para ejecutar python: prioriza el runtime embebido."""
    if os.path.exists(PYTHON_EXE):
        return [PYTHON_EXE]
    return [sys.executable]


def start_streamlit() -> int:
    """
    Lanza `pythonw.exe -X utf8 -m streamlit run app/app.py` y espera hasta
    que el servidor devuelva algo. Luego abre el navegador.
    """
    # Carpeta donde está el código fuente: en el .zip distribuido vive en app/
    # pero durante desarrollo vive junto al launcher; soportamos ambos.
    entry = APP_ENTRY
    if not os.path.exists(entry):
        # Modo desarrollo: app.py está en el mismo dir que este script
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
    # Streamlit tarda unos segundos en arrancar; mostramos un splash.
    time.sleep(1.5)
    # Abrir navegador (hacia el localhost:8501)
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
    apply_pending_update()
    if not ensure_runtime():
        # Intentar arrancar de todos modos con el Python del sistema.
        log("Runtime no encontrado; intentando con Python del sistema.")
    ensure_dependencies()
    return start_streamlit()


if __name__ == "__main__":
    sys.exit(main())
