# Update System Reliable Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the auto-update system bulletproof so the lubricentro staff never needs to manually download/extract from GitHub.

**Architecture:** Eliminate the dead code path (`update_worker.py` + `pythonw.exe`) and strengthen the single reliable path (`update.bat`). Add ZIP integrity verification before committing to an update. Add retry protection in the launcher to prevent infinite loops if update.bat fails repeatedly. Fix all error cleanup paths.

**Tech Stack:** Python (updater, launcher), Windows Batch (update.bat), zipfile/stdlib only (no new dependencies).

---

## Global Constraints

- Do not modify `database.py`, `pages/`, or any UI pages
- Do not add new Python dependencies (stdlib only)
- Windows batch file must use only commands available in Windows 10 1803+ / Win 11 (tar, taskkill, timeout, cmd builtins)
- All paths use `os.path.join`, never hardcoded `/` or `\\`
- All file operations that can fail must handle `OSError` gracefully
- The `.updates/` directory is the single source of truth for update state

---

## File Structure

| File | Responsibility |
|---|---|
| `updater.py` | GitHub API check, download, ZIP verification, lock writing, batch generation |
| `build/launcher.py` | Startup check for pending update, retry protection, normal boot |
| `app.py` | Download progress UI, initiate update, confirmation message |
| `update_worker.py` | **Deprecated** — keep file but remove all call sites; no changes to file itself |

### Data flow after fix

```
app.py → download_asset(zip → .updates/update.zip)
       → verify_zip_integrity(.updates/update.zip)      ← NEW
       → apply_update() → writes .updates/pending_update
                        → writes .updates/update_retry   ← NEW
                        → writes update.bat
       → os._exit(0)

next launch → launcher.py → check_and_launch_update()
                          → reads .updates/update_retry  ← NEW
                          → if retries >= 3: clean stale lock, boot normally
                          → spawn update.bat, exit

update.bat → cleans pending_update at START (defensive)  ← NEW
           → kills processes
           → backs up LubricentroWinter.exe               ← NEW
           → tar -xf (primary) or Expand-Archive (fallback)
           → on error: clean pending_update + retry file  ← FIX
           → on success: clean, relaunch
```

---

### Task 1: Refactor updater.py — verify ZIP integrity, standardize path, remove worker

**Files:**
- Modify: `updater.py` (multiple sections)

**Interfaces:**
- Consumes: `APP_VERSION`, `GITHUB_REPO`, `ASSET_NAME_HINT` (existing)
- Produces: `_verify_zip_integrity(zip_path: str) -> bool`, modified `apply_update(downloaded_path, expected_sha256)`

- [ ] **Step 1: Add `_verify_zip_integrity` function after line 131 (after `_verify_checksum`)**

Add this function that validates a ZIP can be opened and read without errors:

```python
def _verify_zip_integrity(zip_path: str) -> bool:
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            bad = zf.testzip()
            if bad is not None:
                return False
            for member in zf.infolist():
                zf.read(member.filename)
        return True
    except (zipfile.BadZipFile, OSError, RuntimeError):
        return False
```

- [ ] **Step 2: Modify `download_asset` to always save as `.updates/update.zip`**

Change line ~258: replace `dest_path = os.path.join(dest_dir, safe_name)` with:
```python
    dest_path = os.path.join(dest_dir, "update.zip")
```

- [ ] **Step 3: Modify `apply_update` to verify ZIP integrity and remove worker call**

Replace `apply_update` function (lines 312-340) with:

```python
def apply_update(downloaded_path: str, expected_sha256: Optional[str] = None) -> str:
    if expected_sha256:
        if not _verify_checksum(downloaded_path, expected_sha256):
            raise UpdateError("Checksum SHA256 no coincide - posible archivo corrupto o manipulado")

    if not _verify_zip_integrity(downloaded_path):
        raise UpdateError("El archivo ZIP descargado está corrupto o es inválido")

    os.makedirs(UPDATE_DIR, exist_ok=True)

    zip_abs = os.path.abspath(downloaded_path)
    with open(UPDATE_LOCK, "w", encoding="utf-8") as f:
        f.write(zip_abs + "\n")

    retry_path = os.path.join(UPDATE_DIR, "update_retry")
    with open(retry_path, "w", encoding="utf-8") as f:
        f.write("0\n")

    root = os.path.dirname(UPDATE_DIR)
    _write_update_batch_secure(root, zip_abs)
    return UPDATE_LOCK
```

- [ ] **Step 4: Replace `_spawn_update_worker` with a no-op stub**

```python
def _spawn_update_worker(root: str, zip_path: str) -> None:
    pass
```

- [ ] **Step 5: Run tests to verify no regressions**

```bash
python -c "from updater import apply_update, _verify_zip_integrity, download_asset, get_latest_release, compare_versions; print('Imports OK')"
```

Expected: `Imports OK`

- [ ] **Step 6: Commit**

```bash
git add updater.py
git commit -m "fix(updater): verify ZIP integrity, standardize download path, remove dead worker code"
```

---

### Task 2: Fix update.bat — cleanup on error, .exe backup, extraction fallback

**Files:**
- Modify: `updater.py` (function `_write_update_batch_secure`)

**Interfaces:**
- Consumes: `_write_update_batch_secure(root, zip_path)` (existing signature)
- Produces: Robust update.bat with all error paths covered

- [ ] **Step 1: Rewrite `_write_update_batch_secure` with hardened batch content**

Replace the body of `_write_update_batch_secure` (from line 415 onward):

New batch:
1. Clean pending_update + retry file at START (defensive, removes stale state)
2. Backup LubricentroWinter.exe → LubricentroWinter.exe.bak
3. Try `tar -xf` first; if it fails, fall back to PowerShell `Expand-Archive`
4. On ANY error: clean pending_update + update_retry + update.zip, restore .exe.bak
5. On success: clean everything, relaunch

```python
def _write_update_batch_secure(root: str, zip_path: str) -> str:
    bat_path = os.path.join(root, "update.bat")
    launcher_name = "LubricentroWinter.exe"
    zip_abs = os.path.abspath(zip_path)
    root_abs = os.path.abspath(root)

    bat_content = rf"""@echo off
setlocal enabledelayedexpansion

set ROOT=%~dp0
set ZIP_PATH={zip_abs}
set LAUNCHER={launcher_name}

if exist "%ROOT%\.updates\pending_update" del "%ROOT%\.updates\pending_update" 2>nul
if exist "%ROOT%\.updates\update_retry" del "%ROOT%\.updates\update_retry" 2>nul

echo [UPDATE] Cerrando LubricentroWinter...
taskkill /F /IM "%LAUNCHER%" >nul 2>&1
taskkill /F /IM "pythonw.exe" >nul 2>&1
taskkill /F /IM "streamlit.exe" >nul 2>&1

timeout /t 3 /nobreak >nul

echo [UPDATE] Respaldando binario actual...
if exist "%ROOT%\%LAUNCHER%" (
    copy /Y "%ROOT%\%LAUNCHER%" "%ROOT%\%LAUNCHER%.bak" >nul 2>&1
)

echo [UPDATE] Respaldando runtime actual...
if exist "%ROOT%\runtime.old" rmdir /S /Q "%ROOT%\runtime.old" 2>nul
if exist "%ROOT%\runtime" rename "%ROOT%\runtime" "runtime.old"

echo [UPDATE] Extrayendo actualizacion...
tar -xf "%ZIP_PATH%" -C "%ROOT%"
if errorlevel 1 (
    echo [UPDATE] tar fallo, intentando con PowerShell Expand-Archive...
    powershell -Command "Expand-Archive -Path '%ZIP_PATH%' -DestinationPath '%ROOT%' -Force" >nul 2>&1
)
if errorlevel 1 goto FAIL

if not exist "%ROOT%\%LAUNCHER%" (
    echo [ERROR] %LAUNCHER% no encontrado en el zip.
    if exist "%ROOT%\%LAUNCHER%.bak" (
        copy /Y "%ROOT%\%LAUNCHER%.bak" "%ROOT%\%LAUNCHER%" >nul 2>&1
    )
    goto FAIL
)

echo [UPDATE] Limpieza...
if exist "%ROOT%\runtime.old" rmdir /S /Q "%ROOT%\runtime.old" 2>nul
if exist "%ROOT%\%LAUNCHER%.bak" del "%ROOT%\%LAUNCHER%.bak" 2>nul
if exist "%ZIP_PATH%" del "%ZIP_PATH%" 2>nul
if exist "%ROOT%\.updates\pending_update" del "%ROOT%\.updates\pending_update" 2>nul
if exist "%ROOT%\.updates\update_retry" del "%ROOT%\.updates\update_retry" 2>nul

echo [UPDATE] Iniciando nueva version...
start "" "%ROOT%\%LAUNCHER%"
(goto) 2>nul & del "%~f0"
exit /b 0

:FAIL
echo [ERROR] Fallo la actualizacion. Restaurando respaldo...
if exist "%ROOT%\runtime.old" (
    if exist "%ROOT%\runtime" rmdir /S /Q "%ROOT%\runtime" 2>nul
    rename "%ROOT%\runtime.old" "runtime"
)
if exist "%ROOT%\%LAUNCHER%.bak" (
    copy /Y "%ROOT%\%LAUNCHER%.bak" "%ROOT%\%LAUNCHER%" >nul 2>&1
    del "%ROOT%\%LAUNCHER%.bak" 2>nul
)
if not exist "%ROOT%\_logs" mkdir "%ROOT%\_logs" 2>nul
echo [%date% %time%] ERROR: update fallo - %ZIP_PATH% >> "%ROOT%\_logs\update_error.log"
exit /b 1
"""
    with open(bat_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(bat_content)
    return bat_path
```

- [ ] **Step 2: Verify no syntax errors**

```bash
python -c "import updater; print('Syntax OK')"
```

Expected: `Syntax OK`

- [ ] **Step 3: Run full test suite**

```bash
python -m pytest tests/ -v 2>&1 | head -40
```

Expected: All existing tests pass.

- [ ] **Step 4: Commit**

```bash
git add updater.py
git commit -m "fix(updater): harden update.bat with .exe backup, PowerShell fallback, and error cleanup"
```

---

### Task 3: Add retry protection to launcher.py

**Files:**
- Modify: `build/launcher.py`

**Interfaces:**
- Consumes: `UPDATE_DIR`, `UPDATE_LOCK`, `UPDATE_BAT` (existing constants)
- Produces: Retry-limited `check_and_launch_update()`, new `UPDATE_RETRY` constant

- [ ] **Step 1: Add `UPDATE_RETRY` and `MAX_UPDATE_RETRIES` constants after line 39**

```python
UPDATE_RETRY = os.path.join(UPDATE_DIR, "update_retry")
MAX_UPDATE_RETRIES = 3
```

- [ ] **Step 2: Add `_read_retry_count`, `_increment_retry`, and `_clean_stale_update` helper functions before `check_and_launch_update`**

```python
def _read_retry_count() -> int:
    if not os.path.exists(UPDATE_RETRY):
        return 0
    try:
        with open(UPDATE_RETRY, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0


def _increment_retry() -> int:
    count = _read_retry_count() + 1
    try:
        os.makedirs(UPDATE_DIR, exist_ok=True)
        with open(UPDATE_RETRY, "w", encoding="utf-8") as f:
            f.write(f"{count}\n")
    except OSError:
        pass
    return count


def _clean_stale_update() -> None:
    for path in [UPDATE_LOCK, UPDATE_RETRY, UPDATE_BAT]:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass
```

- [ ] **Step 3: Modify `check_and_launch_update` to check retry count**

Replace the existing function (lines 57-111) with:

```python
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
```

- [ ] **Step 4: Verify no syntax errors**

```bash
python -c "import sys; sys.path.insert(0, 'build'); import launcher; print('Syntax OK')"
```

Expected: `Syntax OK`

- [ ] **Step 5: Commit**

```bash
git add build/launcher.py
git commit -m "fix(launcher): add retry protection to prevent infinite update loops"
```

---

### Task 4: Improve app.py feedback

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `apply_update` (raises `UpdateError` on corrupt ZIP now)
- Produces: Better error messages for the user

- [ ] **Step 1: Wrap `apply_update` call with error handling for the new integrity check**

Replace lines 148-154:

```python
                try:
                    db.backup_db()
                except Exception:
                    pass
                try:
                    apply_update(path)
                except Exception as e:
                    st.error(f"❌ Error al preparar la actualización: {e}")
                    st.stop()
                st.success("✅ Actualización lista. La app se cerrará y reiniciará.")
                time.sleep(2)
                os._exit(0)
```

- [ ] **Step 2: Verify no syntax errors**

```bash
python -c "import ast; ast.parse(open('app.py').read()); print('Syntax OK')"
```

Expected: `Syntax OK`

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "fix(app): add error handling for ZIP verification failure"
```

---

### Task 5: Add defensive cleanup of stale update.bat on normal startup

**Files:**
- Modify: `build/launcher.py`

**Interfaces:**
- Consumes: `main()` (existing)
- Produces: Cleanup of orphaned `update.bat` at every normal boot

- [ ] **Step 1: Add `_cleanup_orphan_update_artifacts` function before `check_and_launch_update`**

```python
def _cleanup_orphan_update_artifacts() -> None:
    if not os.path.exists(UPDATE_LOCK):
        if os.path.exists(UPDATE_BAT):
            log("Limpiando update.bat huerfano (sin pending_update).")
            try:
                os.remove(UPDATE_BAT)
            except OSError:
                pass
```

- [ ] **Step 2: Call it at the start of `main()`, after the log line and before the update check**

```python
def main() -> int:
    log("=== Lubricentro Winter launcher ===")

    _cleanup_orphan_update_artifacts()

    if check_and_launch_update():
        return 0
    # ... rest unchanged ...
```

- [ ] **Step 3: Verify**

```bash
python -c "import sys; sys.path.insert(0, 'build'); import launcher; print('Syntax OK')"
```

Expected: `Syntax OK`

- [ ] **Step 4: Commit**

```bash
git add build/launcher.py
git commit -m "fix(launcher): clean orphaned update.bat on normal startup"
```

---

## Self-Review Checklist

1. **Spec coverage:** Every requirement accounted for:
   - ZIP verification before commit → Task 1 Steps 1, 3
   - Fixed ZIP path (no temp path confusion) → Task 1 Step 2
   - Remove dead update_worker code path → Task 1 Step 4
   - .exe backup before update → Task 2 Step 1
   - PowerShell fallback if tar fails → Task 2 Step 1
   - Error cleanup in .bat (clean lock on failure) → Task 2 Step 1
   - Retry protection (max 3 attempts) → Task 3 Step 3
   - Better user feedback (try/except + delay) → Task 4 Step 1
   - Stale artifact cleanup → Task 5 Step 1

2. **Placeholder scan:** No "TBD", "TODO", "implement later" patterns. All code concrete.

3. **Type consistency:** All function names and signatures match across tasks.
