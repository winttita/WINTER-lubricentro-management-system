@echo off
REM ============================================================================
REM Build script para Lubricentro Winter (Windows).
REM
REM Genera dist/LubricentroWinter_vX.Y.Z.zip listo para subir a GitHub Releases.
REM Contenido del zip:
REM   LubricentroWinter.exe         (launcher compilado con PyInstaller, ventana oculta)
REM   runtime/                       (Python embebido + deps)
REM   app/                           (codigo fuente de la app)
REM   requirements.txt
REM   updater.py
REM
REM Requisitos previos en la maquina que corre este script:
REM   - Python 3.12+ instalado (con pip) SOLO para compilar el launcher.exe
REM   - PyInstaller:  pip install pyinstaller
REM   - 7zip NO hace falta, usamos Compress-Archive de PowerShell
REM
REM Firma digital (opcional):
REM   - Certificado de firma de código (Code Signing) .pfx con password
REM   - Variables de entorno: SIGN_CERT_PATH, SIGN_CERT_PASSWORD
REM   - signtool.exe en PATH (incluido en Windows SDK / Visual Studio)
REM
REM Uso:
REM   build\build_windows.bat [version]
REM   (si no se pasa version, se lee de updater.py:APP_VERSION o se usa la fecha)
REM ============================================================================

setlocal enabledelayedexpansion
set HERE=%~dp0
set ROOT=%HERE%..

REM --- Detectar version ----------------------------------------------------
set VERSION=%1
if "%VERSION%"=="" (
    REM Intentar leer APP_VERSION de updater.py
    for /f "tokens=2 delims==" %%a in ('findstr /c:"APP_VERSION =" "%ROOT%\updater.py"') do (
        set RAW=%%a
        set RAW=!RAW:"=!
        set RAW=!RAW: =!
        set VERSION=!RAW!
    )
)
if "%VERSION%"=="" set VERSION=dev
echo Version detectada: %VERSION%

REM --- Configurar paths ----------------------------------------------------
set DIST=%ROOT%\dist
set STAGE=%DIST%\LubricentroWinter_v%VERSION%
set ZIP=%DIST%\LubricentroWinter_v%VERSION%.zip

REM Limpiar stage previo
if exist "%STAGE%" rmdir /s /q "%STAGE%"
if exist "%ZIP%" del "%ZIP%"
mkdir "%STAGE%"

REM --- 1. Compilar launcher.exe con PyInstaller (ventana oculta) -----------
echo [1/8] Compilando launcher.exe con PyInstaller...
cd /d %ROOT%
python -m pip install --quiet pyinstaller
python -m PyInstaller --onefile --windowed --uac-admin --noconfirm --name LubricentroWinter ^
    --distpath "%STAGE%" --workpath "%DIST%\build_launcher" ^
    --specpath "%DIST%\build_launcher" ^
    build\launcher.py
if errorlevel 1 (
    echo ERROR compilando launcher.
    exit /b 1
)

REM --- 2. Firma digital del launcher.exe (opcional) ------------------------
if defined SIGN_CERT_PATH if defined SIGN_CERT_PASSWORD (
    echo [2/8] Firmando launcher.exe digitalmente...
    signtool sign /f "%SIGN_CERT_PATH%" /p "%SIGN_CERT_PASSWORD%" ^
        /fd sha256 /tr http://timestamp.digicert.com /td sha256 ^
        "%STAGE%\LubricentroWinter.exe"
    if errorlevel 1 (
        echo ADVERTENCIA: Fallo la firma digital. Continuando sin firmar...
    )
) else (
    echo [2/8] Sin certificado de firma configurado (SIGN_CERT_PATH/SIGN_CERT_PASSWORD). Saltando firma digital.
)

REM --- 3. Descargar y preparar Python embebido ----------------------------
echo [3/8] Preparando Python embebido...
set PYVER=3.12.7
set PYARCH=amd64
set PYURL=https://www.python.org/ftp/python/%PYVER%/python-%PYVER%-embed-%PYARCH%.zip
set PYZIP=%DIST%\python-embed.zip
set PYDIR=%STAGE%\runtime

if not exist "%PYZIP%" (
    echo Descargando %PYURL% ...
    powershell -NoProfile -Command "Invoke-WebRequest -Uri '%PYURL%' -OutFile '%PYZIP%'"
    if errorlevel 1 (
        echo ERROR descargando Python embebido.
        exit /b 1
    )
)
mkdir "%PYDIR%"
powershell -NoProfile -Command "Expand-Archive -Path '%PYZIP%' -DestinationPath '%PYDIR%' -Force"

REM Habilitar pip en python embebido (renombrar python312._pth y baja get-pip)
pushd "%PYDIR%"
for %%f in (python*._pth) do (
    ren "%%f" "%%f.disabled"
)
if not exist get-pip.py (
    powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'"
)
python.exe get-pip.py --no-warn-script-location
popd

REM --- 4. Instalar dependencias de la app en el runtime embebido -----------
echo [4/8] Instalando dependencias en el runtime embebido...
"%PYDIR%\python.exe" -m pip install --no-warn-script-location -r "%ROOT%\requirements.txt"

REM --- 5. Copiar codigo fuente ---------------------------------------------
echo [5/8] Copiando codigo fuente...
mkdir "%STAGE%\app" 2>nul
copy /Y "%ROOT%\app.py"       "%STAGE%\app\app.py"       >nul
copy /Y "%ROOT%\database.py" "%STAGE%\app\database.py"  >nul
xcopy /E /I /Q "%ROOT%\pages" "%STAGE%\app\pages\"      >nul
copy /Y "%ROOT%\updater.py"      "%STAGE%\updater.py"      >nul
copy /Y "%ROOT%\requirements.txt" "%STAGE%\requirements.txt" >nul

REM --- 6. Copiar archivos de estilo/tickets -------------------------------
echo [6/8] Copiando assets adicionales...
copy /Y "%ROOT%\style.py"       "%STAGE%\style.py"       >nul
copy /Y "%ROOT%\tickets.py"     "%STAGE%\tickets.py"     >nul
copy /Y "%ROOT%\build\icon.ico"  "%STAGE%\icon.ico"       >nul 2>nul

REM --- 7. Empaquetar ZIP ---------------------------------------------------
echo [7/8] Empaquetando %ZIP% ...
powershell -NoProfile -Command "Compress-Archive -Path '%STAGE%\*' -DestinationPath '%ZIP%' -Force"

REM --- 8. Firma digital del ZIP (opcional) ---------------------------------
if defined SIGN_CERT_PATH if defined SIGN_CERT_PASSWORD (
    echo [8/8] Firmando ZIP digitalmente...
    signtool sign /f "%SIGN_CERT_PATH%" /p "%SIGN_CERT_PASSWORD%" ^
        /fd sha256 /tr http://timestamp.digicert.com /td sha256 ^
        "%ZIP%"
    if errorlevel 1 (
        echo ADVERTENCIA: Fallo la firma del ZIP. Continuando...
    )
) else (
    echo [8/8] Sin certificado de firma configurado. Saltando firma del ZIP.
)

echo.
echo BUILD OK
echo   Stage: %STAGE%
echo   Zip:   %ZIP%
echo.
echo Proximo paso: subir %ZIP% a GitHub Releases con tag v%VERSION%.
endlocal