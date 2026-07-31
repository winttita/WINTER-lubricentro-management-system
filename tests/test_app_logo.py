import os

from streamlit.testing.v1 import AppTest

import database
import style
import updater

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")


def _run_login(monkeypatch, logo_factory):
    monkeypatch.setattr(database, "init_db", lambda: None)
    monkeypatch.setattr(database, "backup_db", lambda: None)
    monkeypatch.setattr(database, "cleanup_old_backups", lambda: None)
    monkeypatch.setattr(style, "get_logo_path", logo_factory)
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    return at


def _run_principal(monkeypatch, logo_factory):
    monkeypatch.setattr(database, "init_db", lambda: None)
    monkeypatch.setattr(database, "backup_db", lambda: None)
    monkeypatch.setattr(database, "cleanup_old_backups", lambda: None)
    monkeypatch.setattr(database, "get_productos", lambda: [])
    monkeypatch.setattr(database, "get_movimientos", lambda limit=5: [])
    monkeypatch.setattr(updater, "check_for_update", lambda: None)
    monkeypatch.setattr(style, "get_logo_path", logo_factory)
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.session_state["logged_in"] = True
    at.session_state["user_id"] = 1
    at.session_state["user_nombre"] = "Admin"
    at.session_state["user_rol"] = "admin"
    at.run()
    return at


def _assert_pantalla_principal(at):
    assert not at.exception
    assert at.title[0].value == "Centro Automotor WINTER"
    assert any("Bienvenido, **Admin**" in m.value for m in at.markdown)


def test_login_con_logo(monkeypatch):
    at = _run_login(monkeypatch, lambda: "centro_automotor.png")
    assert not at.exception
    assert len(at.image) == 1


def test_login_sin_logo_no_falla(monkeypatch):
    at = _run_login(monkeypatch, lambda: None)
    assert not at.exception
    assert len(at.image) == 0


def test_principal_con_logo(monkeypatch):
    at = _run_principal(monkeypatch, lambda: "centro_automotor.png")
    _assert_pantalla_principal(at)
    assert len(at.image) == 1


def test_principal_sin_logo_no_falla(monkeypatch):
    at = _run_principal(monkeypatch, lambda: None)
    _assert_pantalla_principal(at)
    assert len(at.image) == 0
