# tests/test_logo.py
import os

import style


def test_get_logo_path_encuentra_logo_en_cwd(monkeypatch, tmp_path):
    logo = tmp_path / style.LOGO_FILENAME
    logo.write_bytes(b"png")
    monkeypatch.chdir(tmp_path)
    assert style.get_logo_path() == str(logo)


def test_get_logo_path_devuelve_none_si_no_hay_logo(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(style, "__file__", str(tmp_path / "style.py"))
    assert style.get_logo_path() is None


def test_get_logo_path_busca_tambien_junto_al_modulo(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    path = style.get_logo_path()
    assert path is not None
    assert os.path.basename(path) == style.LOGO_FILENAME
