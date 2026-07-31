import os

from streamlit.testing.v1 import AppTest

import database
import style

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")


def _run_login(monkeypatch, logo_factory):
    monkeypatch.setattr(database, "init_db", lambda: None)
    monkeypatch.setattr(database, "backup_db", lambda: None)
    monkeypatch.setattr(database, "cleanup_old_backups", lambda: None)
    monkeypatch.setattr(style, "get_logo_path", logo_factory)
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    return at


def test_login_con_logo(monkeypatch):
    at = _run_login(monkeypatch, lambda: "centro_automotor.png")
    assert not at.exception
    assert len(at.image) == 1


def test_login_sin_logo_no_falla(monkeypatch):
    at = _run_login(monkeypatch, lambda: None)
    assert not at.exception
    assert len(at.image) == 0
