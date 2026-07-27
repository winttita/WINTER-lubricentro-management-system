"""Watchdog de actualizacion automatica para Lubricentro Winter.

Se lanza como proceso detached (sin ventana) via el runtime embebido
pythonw.exe. Lee la ruta del ZIP desde .updates/pending_update, espera
que la app principal cierre, extrae el ZIP al directorio raiz (ROOT)
usando zipfile (validando path traversal), y relanza el launcher.

No abre ninguna ventana de cmd ni powershell. Todo el trabajo es
silencioso y automatico. En caso de fallo, escribe a
_logs/update_error.log y sale sin tocar el runtime actual.

Llamada tipica (desde app.py via updater.apply_update):
    runtime\\pythonw.exe app\\update_worker.py

Args CLI (opcionales):
    --zip PATH    Ruta absoluta al ZIP (sobrescribe pending_update).
    --root PATH   Directorio raiz de la app (sobrescribe auto-detect).
"""
from __future__ import annotations

import os
import sys
import time
import zipfile
import subprocess
import shutil
from pathlib import Path


def _log(root: Path, msg: str) -> None:
    log_dir = root / "_logs"
    try:
        log_dir.mkdir(exist_ok=True)
        with open(log_dir / "update_error.log", "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except OSError:
        pass


def _resolve_root() -> Path:
    aqui = Path(__file__).resolve()
    # app/update_worker.py  -> ROOT = parent.parent
    # si esta en ROOT/update_worker.py -> ROOT = parent
    parent = aqui.parent
    if parent.name == "app":
        return parent.parent
    return parent


def _read_pending(root: Path) -> str | None:
    lock = root / ".updates" / "pending_update"
    if not lock.exists():
        return None
    try:
        with open(lock, "r", encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


def _extract_zip_safe(zip_path: str, dest_dir: Path) -> bool:
    """Extrae un ZIP validando cada entrada contra path traversal.

    Devuelve True si la extraccion fue exitosa, False en caso contrario.
    """
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            dest_abs = str(dest_dir.resolve())
            for member in zf.infolist():
                name = member.filename
                if os.path.isabs(name) or name.startswith("..") or (".." + os.sep) in name:
                    _log(dest_dir, f"Entrada ZIP insegura (path traversal): {name}")
                    return False
                target = os.path.normpath(os.path.join(dest_dir, name))
                if not target.startswith(dest_abs + os.sep) and target != dest_abs:
                    _log(dest_dir, f"Entrada ZIP escapa del destino: {name}")
                    return False
            zf.extractall(dest_dir)
        return True
    except (zipfile.BadZipFile, OSError) as e:
        _log(dest_dir, f"Error extrayendo ZIP: {e}")
        return False


def _wait_for_exit(timeout: int = 15) -> None:
    """Espera que el proceso padre (launcher + Streamlit) cierre.

    No es estrictamente necesario esperar, pero da margen para que
    Windows libere los locks de DLLs y archivos antes de extraer.
    """
    time.sleep(timeout)


def _launch_launcher(root: Path, launcher_name: str = "LubricentroWinter.exe") -> None:
    exe = root / launcher_name
    if not exe.exists():
        _log(root, f"Launcher no encontrado tras extraccion: {exe}")
        return
    try:
        subprocess.Popen(
            [str(exe)],
            cwd=str(root),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as e:
        _log(root, f"No se pudo relanzar el launcher: {e}")


def _cleanup(root: Path, zip_path: str | None) -> None:
    lock = root / ".updates" / "pending_update"
    try:
        if lock.exists():
            lock.unlink()
    except OSError:
        pass
    if zip_path:
        try:
            p = Path(zip_path)
            if p.exists():
                p.unlink()
        except OSError:
            pass


def main() -> int:
    root = _resolve_root()
    zip_path = None

    if len(sys.argv) >= 3 and sys.argv[1] == "--zip":
        zip_path = sys.argv[2]
    if len(sys.argv) >= 5 and sys.argv[3] == "--root":
        root = Path(sys.argv[4])

    if not zip_path:
        zip_path = _read_pending(root)
    if not zip_path or not os.path.exists(zip_path):
        _log(root, f"ZIP no encontrado (pending_update ausente o invalido). root={root}")
        return 1

    _wait_for_exit(3)

    _log(root, f"Iniciando extraccion de {zip_path} en {root}")
    ok = _extract_zip_safe(zip_path, root)
    if not ok:
        _log(root, "Extraccion fallo; manteniendo runtime actual.")
        _cleanup(root, None)
        return 1

    _cleanup(root, zip_path)
    _log(root, "Extraccion OK. Relanzando launcher.")
    _launch_launcher(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
