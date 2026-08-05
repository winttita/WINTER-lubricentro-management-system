# Fix Logo PNG (centro_automotor.png) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the `centro_automotor.png` logo work reliably in dev mode and in the packaged Windows release (it currently breaks the login screen, main screen, and price-list PDF because the release ZIP omits the file and paths are CWD-relative).

**Architecture:** A shared `get_logo_path()` helper in `style.py` (already imported by both app.py and the price-list page) resolves the logo via CWD → module dir, returning `None` when missing. PDF generation moves to a new testable module `lista_precios_pdf.py` with a graceful no-logo fallback. The release workflow gains a `Copy-Item` for the PNG plus a ZIP verification gate.

**Tech Stack:** Python 3.13, Streamlit 1.59.2 (incl. `streamlit.testing.v1.AppTest`), fpdf2, pytest, GitHub Actions (PowerShell).

## Global Constraints

- Conventional Commits en español, sin emojis en mensajes de commit (CONVENTIONS.md §3, §6)
- Ejecutar `pytest` localmente antes de cada commit (CONVENTIONS.md)
- No agregar dependencias nuevas (requirements.txt: streamlit, pandas, pytest, pywin32, fpdf2)
- El archivo debe seguir llamándose `centro_automotor.png` y vivir en la raíz del repo (ya commiteado)
- En el ZIP de release el PNG va al nivel raíz (junto al exe), porque el launcher lanza streamlit con `cwd=ROOT` (`build/launcher.py:187`)
- Formato de fila de `db.get_precios_para_lista()`: tuplas `(proveedor_nombre, producto_nombre, codigo_barras, precio_venta, stock_actual, categoria_nombre)` — orden verificado en `database.py:1184-1190`

---

### Task 1: Helper `get_logo_path()` en `style.py`

**Files:**
- Modify: `style.py`
- Create: `tests/test_logo.py`

**Interfaces:**
- Produces: `style.LOGO_FILENAME: str = "centro_automotor.png"`; `style.get_logo_path() -> str | None` (ruta absoluta del primer candidato existente; CWD primero, luego el directorio del módulo — cubre dev desde la raíz y el layout empaquetado donde `style.py` queda junto al exe; `None` si no existe)

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/test_logo.py -v`
Expected: FAIL — `AttributeError: module 'style' has no attribute 'LOGO_FILENAME'`

- [ ] **Step 3: Write minimal implementation**

```python
# style.py
import os

import streamlit as st

LOGO_FILENAME = "centro_automotor.png"


def get_logo_path():
    """Devuelve la ruta absoluta del logo si existe, o None.

    Busca en el directorio de trabajo actual y en el directorio de este
    modulo (cubre el layout empaquetado donde el png queda junto al exe).
    """
    candidates = [
        os.path.join(os.getcwd(), LOGO_FILENAME),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), LOGO_FILENAME),
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    return None


def inject_global_css():
    """Inyecta CSS para ocultar el mensaje 'Press Enter to submit form' de Streamlit."""
    st.markdown("""
    <style>
    /* Ocultar 'Press Enter to submit form' en formularios */
    div[data-testid="stForm"] small { display: none !important; }
    /* Streamlit 1.30+ usa .st-emotion-cache-* */
    .st-emotion-cache-1v0p1ee, .st-emotion-cache-ll22cq { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/test_logo.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add style.py tests/test_logo.py
git commit -m "feat(logo): helper get_logo_path para resolver la ruta del logo de forma robusta"
```

---

### Task 2: Módulo `lista_precios_pdf.py` con fallback de logo

**Files:**
- Create: `lista_precios_pdf.py`
- Create: `tests/test_lista_precios_pdf.py`

**Interfaces:**
- Consumes: filas de `db.get_precios_para_lista()` — tuplas `(proveedor, nombre, codigo, precio, stock, categoria)`
- Produces: `lista_precios_pdf.generar_pdf(productos: list, logo_path: str | None = None) -> bytes` — si `logo_path` es `None` o el archivo no existe, omite el logo en vez de fallar

- [ ] **Step 1: Write the failing test**

```python
# tests/test_lista_precios_pdf.py
import os

import pytest

from lista_precios_pdf import generar_pdf

PRODUCTOS = [
    ("Proveedor A", "Aceite 20W50", "123", 4500.00, 10, "Lubricantes"),
    ("Proveedor A", "Filtro de aceite", "456", 3500.00, 5, "Filtros"),
]
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_generar_pdf_con_logo():
    logo = os.path.join(REPO_ROOT, "centro_automotor.png")
    assert os.path.isfile(logo)
    out = generar_pdf(PRODUCTOS, logo_path=logo)
    assert out[:5] == b"%PDF-"
    assert len(out) > 1000


def test_generar_pdf_sin_logo_no_falla():
    out = generar_pdf(PRODUCTOS, logo_path=None)
    assert out[:5] == b"%PDF-"
    assert len(out) > 1000


def test_generar_pdf_con_logo_inexistente_no_falla(tmp_path):
    out = generar_pdf(PRODUCTOS, logo_path=str(tmp_path / "no-existe.png"))
    assert out[:5] == b"%PDF-"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/test_lista_precios_pdf.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'lista_precios_pdf'`

- [ ] **Step 3: Write minimal implementation** (lógica movida tal cual de `pages/10_ListaPrecios.py:34-97`; solo cambia la firma y el guard del logo)

```python
# lista_precios_pdf.py
import os
from datetime import datetime

from fpdf import FPDF


def generar_pdf(productos, logo_path=None):
    """Genera un PDF de la lista de precios agrupada por proveedor.

    Maneja acentos y eñes usando latin-1 explicito en cada string.
    Si logo_path es None o el archivo no existe, se omite el logo.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    # Encabezado
    pdf.add_page()
    if logo_path and os.path.isfile(logo_path):
        pdf.image(logo_path, x=(210 - 50) / 2, w=50)
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "LISTA DE PRECIOS", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Centro Automotor WINTER", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    fecha_str = datetime.now().strftime("%d/%m/%Y")
    pdf.cell(0, 6, f"Fecha de emision: {fecha_str}", ln=True, align="C")
    pdf.ln(3)

    grupos = {}
    for r in productos:
        prov = r[0] or "Sin proveedor"
        grupos.setdefault(prov, []).append(r)

    for proveedor, items in grupos.items():
        # Encabezado del proveedor
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(0, 7, proveedor, ln=True, fill=True)
        pdf.ln(1)

        # Cabecera de tabla
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(25, 6, "Codigo", border=1, fill=True)
        pdf.cell(85, 6, "Producto", border=1, fill=True)
        pdf.cell(40, 6, "Categoria", border=1, fill=True)
        pdf.cell(20, 6, "Precio", border=1, fill=True, align="R")
        pdf.ln()

        # Filas de productos
        pdf.set_font("Helvetica", "", 9)
        for p in items:
            codigo = (p[2] or "-")[:25]
            nombre = (p[1] or "-")[:50]
            categoria = (p[5] or "-")[:22]
            precio = f"${p[3] or 0:,.2f}"

            pdf.cell(25, 6, codigo, border=1)
            pdf.cell(85, 6, nombre, border=1)
            pdf.cell(40, 6, categoria, border=1)
            pdf.cell(20, 6, precio, border=1, align="R")
            pdf.ln()

        pdf.ln(2)

    # Footer
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, "Precios sujetos a cambio sin previo aviso.", ln=True, align="C")

    out = pdf.output()
    if isinstance(out, str):
        return out.encode('latin-1')
    return bytes(out)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/test_lista_precios_pdf.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add lista_precios_pdf.py tests/test_lista_precios_pdf.py
git commit -m "feat(logo): generar_pdf con fallback de logo en modulo lista_precios_pdf"
```

---

### Task 3: Integrar en `pages/10_ListaPrecios.py`

**Files:**
- Modify: `pages/10_ListaPrecios.py`

**Interfaces:**
- Consumes: `style.get_logo_path()`, `lista_precios_pdf.generar_pdf(productos, logo_path=None)` (de Task 1 y 2)

- [ ] **Step 1: Replace imports** (líneas 3-6 actuales)

```python
import streamlit as st
import database as db
import pandas as pd
from datetime import datetime
from lista_precios_pdf import generar_pdf
from style import inject_global_css, get_logo_path
```

- [ ] **Step 2: Delete the local `generar_pdf` function** (líneas 34-97, ahora vive en `lista_precios_pdf.py`) y actualizar la generación (línea 128)

```python
pdf_bytes = generar_pdf(productos, get_logo_path())
```

- [ ] **Step 3: Verify compile and suite**

Run: `venv/bin/python -m py_compile pages/10_ListaPrecios.py && venv/bin/python -m pytest tests/ -v`
Expected: todos los tests en verde (incluye test_database.py, test_logo.py, test_lista_precios_pdf.py)

- [ ] **Step 4: Smoke test manual** — levantar la app, loguearse, abrir "Lista de Precios" y descargar el PDF (con y sin `centro_automotor.png` a mano, verificar que la página no crashea)

- [ ] **Step 5: Commit**

```bash
git add pages/10_ListaPrecios.py
git commit -m "fix(logo): pagina de lista de precios usa get_logo_path con fallback sin logo"
```

---

### Task 4: `app.py` — logo robusto en login y pantalla principal

**Files:**
- Modify: `app.py`
- Create: `tests/test_app_logo.py`

**Interfaces:**
- Consumes: `style.get_logo_path()` (Task 1)
- Nota: `app.py` pasa a usar `import style` (módulo completo) para que los tests puedan parchear `style.get_logo_path()`

- [ ] **Step 1: Write the failing test** (usa `AppTest`, disponible en streamlit 1.59.2)

```python
# tests/test_app_logo.py
import os

import pytest
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


def test_login_sin_logo_no_falla(monkeypatch):
    at = _run_login(monkeypatch, lambda: None)
    assert not at.exception
```

- [ ] **Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/test_app_logo.py -v`
Expected: FAIL — la pantalla de login actual crashea al resolver `centro_automotor.png` desde el CWD del test (el helper aún no se usa) o `FileNotFoundError` en `st.image`

- [ ] **Step 3: Write minimal implementation**

```python
# app.py — reemplazar linea 6
import style

# reemplazar linea 14
style.inject_global_css()

# despues de init_session() (linea 48), agregar:
logo = style.get_logo_path()

# reemplazar linea 53 (pantalla de login)
    if logo:
        st.image(logo, width=250)

# reemplazar linea 84 (app principal)
if logo:
    st.image(logo, width=300)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/test_app_logo.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_app_logo.py
git commit -m "fix(logo): app usa get_logo_path y omite la imagen si no existe"
```

---

### Task 5: Incluir el PNG en el ZIP de release

**Files:**
- Modify: `.github/workflows/release.yml`

- [ ] **Step 1: Add Copy-Item** — después de la línea `Copy-Item build/icon.ico $STAGE/icon.ico -ErrorAction SilentlyContinue` (bloque "Copy additional assets")

```yaml
          Copy-Item centro_automotor.png $STAGE/centro_automotor.png -ErrorAction Stop
```

- [ ] **Step 2: Add CI gate** — en el paso `verify_zip`, inmediatamente después de la línea `Expand-Archive -Path $ZIP -DestinationPath $TMP -ErrorAction Stop`

```yaml
          if (-not (Test-Path "$TMP/centro_automotor.png")) {
            Write-Error "centro_automotor.png no esta en el ZIP"
            exit 1
          }
```

- [ ] **Step 3: Verify** — revisar indentación y sintaxis del YAML (las líneas nuevas deben estar a la misma indentación que los bloques que las rodean). No se puede ejecutar la action localmente; el gate se valida en el próximo release. Alternativa de validación rápida: `venv/bin/python -c "import yaml"` no está disponible (yaml no es dependencia), por lo que se valida visualmente contra el bloque `Copy additional assets`.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "fix(ci): incluye centro_automotor.png en el ZIP de release y lo verifica"
```

---

### Task 6: CHANGELOG y verificación final

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add Unreleased entry** — después del bloque introductorio (antes de `## [0.5.3]`), sin emojis, en español

```markdown
## [Unreleased]

### Corregido
- Logo `centro_automotor.png` ahora se incluye en el ZIP de release y su ruta se resuelve de forma robusta (dev y empaquetado); la lista de precios genera el PDF sin logo si el archivo no se encuentra
```

- [ ] **Step 2: Full suite**

Run: `venv/bin/python -m pytest tests/ -v`
Expected: todos los tests en verde

- [ ] **Step 3: Boot smoke test**

```bash
venv/bin/python -m streamlit run app.py --server.headless=true --browser.gatherUsageStats=false --server.port 8511 &
sleep 8 && curl -s -o /dev/null -w "%{http_code}" http://localhost:8511/_stcore/health
```

Expected: `200` y sin `Traceback` en la salida de streamlit; luego matar el proceso.

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: registra correcciones del logo en CHANGELOG"
```
