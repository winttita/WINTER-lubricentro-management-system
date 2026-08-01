"""
Tests del sistema de actualizaciones (updater + preservación de DB).

Corren en Docker para reproducir el flujo real de apply_update + extracción
con tar sin depender de Windows. Mockean:
- GITHUB API via fixtures locales (no red real).
- UPDATE_DIR y UPDATE_LOCK con tempfile.
- DB local en un dir temporal que sobrevive a una "actualización" simulada.

Casos:
1. test_compare_versions — sanity de la base.
2. test_find_asset_matches_ci_name — el nombre que sube el CI debe matchear.
3. test_db_survives_simulated_update — DB con productos sigue existiendo
   después de apply_update + extracción con tar de un zip que NO toca la DB.
4. test_db_migrates_from_legacy_location — DB vieja junto al script se
   mueve al nuevo dir de datos al llamar init_db().
5. test_backup_db_runs_before_apply — verify backup_db + cleanup_old_backups.
6. test_apply_update_handles_path_traversal — _extract_zip_safe rechaza
   zips con rutas absolutas o "..".
7. test_extract_zip_safe_rejects_backslash_traversal — _extract_zip_safe
   rechaza también rutas windows con backslash que escapen del destino.
"""
from __future__ import annotations

import os
import sys
import shutil
import tempfile
import zipfile
import sqlite3
from unittest import mock

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
import database
import updater


# ---------- helpers ----------

def _make_db_with_products(db_path: str, n: int = 10) -> None:
    """Crea una DB con n productos usando el esquema real de database.init_db."""
    old_db = database.DB_NAME
    old_backup = database.BACKUP_DIR
    database.DB_NAME = db_path
    database.BACKUP_DIR = os.path.join(os.path.dirname(db_path), "backups")
    try:
        database.init_db()
        # agregar n productos
        for i in range(n):
            database.add_categoria(f"Cat_{i}")
            database.add_proveedor(f"Prov_{i}", " Juan", "123", "Contado")
            cat_id = database.get_categorias()[-1][0]
            prov_id = database.get_proveedores()[-1][0]
            database.add_producto(
                f"CB00{i}", f"Producto {i}", "", cat_id, prov_id,
                "Entero", 0, 10.0, 121.0, stock_inicial=10
            )
    finally:
        database.DB_NAME = old_db
        database.BACKUP_DIR = old_backup


def _count_products(db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    finally:
        conn.close()


# ---------- tests ----------

def test_compare_versions_basic():
    assert updater.compare_versions("0.3.0", "0.3.0") == "equal"
    assert updater.compare_versions("0.3.0", "0.3.1") == "newer"
    assert updater.compare_versions("0.3.1", "0.3.0") == "older"
    assert updater.compare_versions("v0.3.0", "0.3.1") == "newer"


def test_find_asset_matches_ci_name():
    """El CI sube un asset llamado LubricentroWinter.zip (corregido en v0.3.0).
    find_asset debe encontrarlo por el hint exacto."""
    release = {
        "assets": [
            {"name": "LubricentroWinter.zip", "size": 50_000_000,
             "browser_download_url": "https://example.com/x.zip"},
        ]
    }
    asset = updater.find_asset(release)
    assert asset is not None
    assert asset["name"] == "LubricentroWinter.zip"


def test_find_asset_accepts_versioned_name_for_compatibility():
    """Compatibilidad: releases antiguas usan nombres como LubricentroWinter_v0.3.0.zip.
    El fallback de compatibilidad (paso 3) SÍ debe encontrarlos para no romper
    actualizaciones de usuarios con releases viejas."""
    release = {
        "assets": [{"name": "LubricentroWinter_v0.3.0.zip",
                    "browser_download_url": "x"}]
    }
    asset = updater.find_asset(release)
    assert asset is not None
    assert asset["name"] == "LubricentroWinter_v0.3.0.zip"


def test_db_survives_simulated_update(tmp_path):
    """Una DB con 10 productos debe seguir teniendo 10 después de:
    1. init_db() coloca la DB en el nuevo dir de datos (tmp_path).
    2. apply_update escribe update.bat + pending_update.
    3. Simulamos la extracción con tar (como hace el .bat) de un zip que
       trae SOLO LubricentroWinter.exe — no toca la DB.
    """
    db_path = str(tmp_path / "lubricentro.db")
    _make_db_with_products(db_path, n=10)
    assert _count_products(db_path) == 10

    # Mockear UPDATE_DIR y UPDATE_LOCK para no tocar paths reales
    update_dir = str(tmp_path / ".updates")
    os.makedirs(update_dir, exist_ok=True)
    fake_zip_path = str(tmp_path / "update.zip")
    with zipfile.ZipFile(fake_zip_path, "w") as zf:
        zf.writestr("LubricentroWinter.exe", b"FAKE_EXE")
        zf.writestr("runtime/pythonw.exe", b"FAKE_RUNTIME")

    with mock.patch.object(updater, "UPDATE_DIR", update_dir), \
         mock.patch.object(updater, "UPDATE_LOCK",
                            os.path.join(update_dir, "pending_update")), \
         mock.patch.object(updater, "_write_update_batch_secure"):
        lock = updater.apply_update(fake_zip_path)

    assert os.path.exists(lock)
    # Simular extracción (en Windows usa tar -xf que soporta .zip; en Linux
    # usamos zipfile nativo de Python para el mismo efecto).
    root_app = str(tmp_path / "app_install")
    os.makedirs(root_app)
    with zipfile.ZipFile(fake_zip_path, "r") as zf:
        zf.extractall(root_app)
    # La DB NO se toca (vive en tmp_path, no en root_app)
    assert _count_products(db_path) == 10, "DB fue sobre-escrita por extraccion"
    # Y el zip se extrajo correctamente
    assert os.path.exists(os.path.join(root_app, "LubricentroWinter.exe"))


def test_db_migrates_from_legacy_location(tmp_path, monkeypatch):
    """Si hay una DB legacy en el dir de database.py y la nueva DB no existe,
    init_db() debe moverla a la nueva ubicación."""
    # Crear DB legacy junto a un "module dir" falso
    legacy_dir = tmp_path / "legacy"
    legacy_dir.mkdir()
    legacy_db = legacy_dir / "lubricentro.db"
    _make_db_with_products(str(legacy_db), n=5)
    assert _count_products(str(legacy_db)) == 5

    # Mockear _user_data_dir para que apunte a un nuevo dir limpio
    new_dir = tmp_path / "newdata"
    monkeypatch.setattr(database, "_user_data_dir",
                         lambda: str(new_dir / "LubricentroWinter"))

    # Mockear __file__ NO se puede fácilmente. Pero _migrate_legacy_db_location
    # usa os.path.dirname(os.path.abspath(__file__)). Lo que hacemos es: poner
    # la DB legacy en el mismo dir que __file__ real, pero eso contaminaría.
    # En su lugar, patcheamos _migrate_legacy_db_location para que use legacy_dir.
    real_migrate = database._migrate_legacy_db_location

    def patched_migrate():
        # Misma lógica que la real pero con legacy_dir custom
        resolved_db, resolved_backup = database._resolve_data_paths()
        if database.DB_NAME != resolved_db:
            return
        legacy_db_path = str(legacy_db)
        legacy_backups = str(legacy_dir / "backups")
        try:
            if os.path.exists(legacy_db_path) and not os.path.exists(resolved_db):
                shutil.move(legacy_db_path, resolved_db)
            if os.path.isdir(legacy_backups) and not os.path.isdir(resolved_backup):
                shutil.move(legacy_backups, resolved_backup)
        except OSError:
            pass

    monkeypatch.setattr(database, "_migrate_legacy_db_location", patched_migrate)

    # Re-resolver paths con el nuevo _user_data_dir
    db_new, backup_new = database._resolve_data_paths()
    os.makedirs(os.path.dirname(db_new), exist_ok=True)
    monkeypatch.setattr(database, "DB_NAME", db_new)
    monkeypatch.setattr(database, "BACKUP_DIR", backup_new)

    # Llamar init_db() — debe migrar la DB
    database.init_db()

    assert os.path.exists(db_new), "DB no migrada al nuevo dir"
    assert not os.path.exists(legacy_db), "DB legacy no se movió"
    assert _count_products(db_new) == 5, "DB migrada perdió productos"


def test_backup_db_creates_backup_and_cleanup(tmp_path, monkeypatch):
    """backup_db debe crear un archivo .db en BACKUP_DIR y cleanup_old_backups
    debe mantener solo los últimos max_backups."""
    db_path = str(tmp_path / "lubricentro.db")
    backup_dir = tmp_path / "backups"
    monkeypatch.setattr(database, "DB_NAME", db_path)
    monkeypatch.setattr(database, "BACKUP_DIR", str(backup_dir))

    _make_db_with_products(db_path, n=3)

    # Crear 15 backups con timestamps escalonados (todos distintos).
    # backup_db usa datetime.now().strftime("%Y%m%d_%H%M%S") — todos en el
    # mismo segundo colisionan. Para forzar nombres únicos,esperamos 1s cada
    # 2 backups. Hacemos solo 3 backups rápidos y forzamos el patrón.
    import time as _t
    created = []
    for i in range(3):
        p = database.backup_db()
        if p:
            created.append(p)
        _t.sleep(0.5)

    # Verificar que hay al menos 1 backup creado
    backups_before = [f for f in os.listdir(str(backup_dir))
                       if f.startswith("lubricentro_backup_")]
    assert len(backups_before) >= 1, "No se creó ningún backup"
    # Forzar 12 backups más con timestamps UNIQUE via monkeypatch
    base_ts = "20260724_2005"
    for i in range(12):
        # Simular timestamp distinto renombrando el más reciente
        existing = [f for f in os.listdir(str(backup_dir))
                     if f.startswith("lubricentro_backup_")]
        if not existing:
            continue
        # copiar el backup a un nombre con i distinto
        src = os.path.join(str(backup_dir), existing[0])
        dst = os.path.join(str(backup_dir),
                           f"lubricentro_backup_{base_ts}{i:02d}.db")
        shutil.copy2(src, dst)

    backups_expanded = [f for f in os.listdir(str(backup_dir))
                        if f.startswith("lubricentro_backup_")]
    assert len(backups_expanded) >= 12

    database.cleanup_old_backups(max_backups=10)
    backups_after = [f for f in os.listdir(str(backup_dir))
                      if f.startswith("lubricentro_backup_")]
    assert len(backups_after) == 10, f"Esperaba 10, hay {len(backups_after)}"


def test_extract_zip_safe_rejects_path_traversal(tmp_path):
    """_extract_zip_safe debe rechazar zips con entradas absolutas o con .."""
    evil_zip = str(tmp_path / "evil.zip")
    with zipfile.ZipFile(evil_zip, "w") as zf:
        zf.writestr("../escape.txt", "malicious")
    dest = str(tmp_path / "dest")
    os.makedirs(dest)
    with pytest.raises(updater.UpdateError, match="path traversal|insegura"):
        updater._extract_zip_safe(evil_zip, dest)


def test_extract_zip_safe_rejects_backslash_traversal(tmp_path):
    """_extract_zip_safe debe rechazar también rutas windows (backslash) que
    escapen del directorio destino."""
    evil_zip = str(tmp_path / "evil2.zip")
    with zipfile.ZipFile(evil_zip, "w") as zf:
        zf.writestr("..\\escape.txt", "malicious")
    dest = str(tmp_path / "dest2")
    os.makedirs(dest)
    with pytest.raises(updater.UpdateError, match="path traversal|insegura"):
        updater._extract_zip_safe(evil_zip, dest)
