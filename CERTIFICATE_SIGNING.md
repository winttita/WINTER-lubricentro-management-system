# Guía de Firma Digital (Code Signing) para Lubricentro Winter

## Resumen

La firma digital elimina las alertas de **Windows SmartScreen** y **antivirus** al ejecutar el `.exe`. Requiere un certificado de firma de código (Code Signing Certificate) emitido por una CA de confianza (Sectigo, DigiCert, GlobalSign, etc.).

## Flujo General

1. Comprar certificado Code Signing (OV/EV) → archivo `.pfx` + password
2. Configurar secrets en GitHub (para CI/CD) o variables de entorno (build local)
3. El build automáticamente firma `launcher.exe` y el ZIP final
4. Sin certificado → el build funciona igual, solo avisa "Saltando firma digital"

---

## 1. Obtener el Certificado

### Opciones recomendadas (2024)

| Proveedor | Tipo | Precio aprox. (USD/año) | Validación |
|-----------|------|------------------------|------------|
| **Sectigo (Comodo)** | OV Code Signing | $70-100 | Organización |
| **DigiCert** | EV Code Signing | $400-600 | Extendida (SmartScreen inmediato) |
| **GlobalSign** | OV Code Signing | $200-300 | Organización |
| **SSL.com** | OV Code Signing | $65-90 | Organización |

> **EV (Extended Validation)**: Elimina SmartScreen desde el día 1, pero cuesta 4-6x más. OV tarda días/semanas en ganar reputación.

### Pasos
1. Generar CSR (Certificate Signing Request) - el proveedor te guía
2. Validación de identidad (documentos de la empresa, llamada telefónica)
3. Descargar certificado `.pfx` (incluye clave privada + certificado público)
4. Guardar **password del .pfx** de forma segura

---

## 2. Configurar Secrets en GitHub

En el repo: **Settings → Secrets and variables → Actions → New repository secret**

| Nombre | Valor | Descripción |
|--------|-------|-------------|
| `SIGN_CERT_BASE64` | Base64 del `.pfx` | `base64 -w 0 certificado.pfx` (Linux/Mac) o `[Convert]::ToBase64String([IO.File]::ReadAllBytes("cert.pfx"))` (PowerShell) |
| `SIGN_CERT_PASSWORD` | Password del .pfx | El password que definiste al exportar el .pfx |

> **NUNCA** subas el `.pfx` ni el password al repo. Solo a Secrets de GitHub.

---

## 3. Build Local con Firma (Windows)

### Prerrequisitos
- Windows SDK instalado (incluye `signtool.exe`)
- Certificado `.pfx` accesible

### Variables de entorno (PowerShell)
```powershell
$env:SIGN_CERT_PATH = "C:\ruta\certificado.pfx"
$env:SIGN_CERT_PASSWORD = "tu_password"
```

### Ejecutar build
```cmd
build\build_windows.bat 0.3.0
```

El script:
1. Compila `launcher.exe`
2. Si `SIGN_CERT_PATH` y `SIGN_CERT_PASSWORD` existen → firma con `signtool`
3. Arma el ZIP
4. Si las variables existen → firma también el ZIP

### Verificar firma
```cmd
signtool verify /pa /v dist\LubricentroWinter.exe
signtool verify /pa /v dist\LubricentroWinter_v0.3.0.zip
```

---

## 4. Build en GitHub Actions (CI/CD)

### Automático al pushear tag `v*`
```bash
git tag v0.3.0
git push origin v0.3.0
```

El workflow:
1. Compila `launcher.exe` con PyInstaller (`--uac-admin` para elevación)
2. **Si existen secrets** → firma `launcher.exe` y el ZIP final
3. Arma el release package
4. Publica en GitHub Releases

### Verificar en Actions
- En la run: busca step "Sign ZIP (conditional)" o "Sign launcher.exe"
- Si dice "Saltando firma digital" → secrets no configurados
- Si falla firma → revisar `signtool` output en logs

---

## 5. Configuración del Launcher (`--uac-admin`)

En `build/launcher.py` y en el workflow se usa `--uac-admin` en PyInstaller:

```bash
pyinstaller --onefile --windowed --uac-admin --icon=build/icon.ico build/launcher.py
```

Esto:
- Agrega manifiesto `requireAdministrator` al `.exe`
- Windows pide elevación (UAC) al hacer doble click
- Necesario para: escribir en `Program Files`, registro, actualizaciones

---

## 6. Troubleshooting Común

| Error | Causa | Solución |
|-------|-------|----------|
| `signtool: command not found` | Windows SDK no instalado / no en PATH | Instalar Windows SDK o agregar `C:\Program Files (x86)\Windows Kits\10\bin\10.0.xxx\x64` al PATH |
| `SignTool Error: The specified PFX password is incorrect` | Password erróneo | Verificar `SIGN_CERT_PASSWORD` en Secrets / variable de entorno |
| `SignTool Error: No certificates meet all the criteria` | Certificado no es Code Signing / expirado | Verificar que el .pfx sea "Code Signing" y válido |
| `The certificate chain was processed, but terminated in a root certificate which is not trusted` | CA no en Trusted Root | Usar CA pública (Sectigo, DigiCert, etc.) |
| SmartScreen sigue avisando | Certificado OV nuevo sin reputación | Esperar días/semanas, o usar EV. Asegurar timestamp server (`/tr http://timestamp.digicert.com`) |

---

## 6. Verificación Manual

```cmd
REM Verificar firma del EXE
signtool verify /pa /v "dist\LubricentroWinter.exe"

REM Verificar firma del ZIP
signtool verify /pa /v "dist\LubricentroWinter_v0.3.0.zip"

REM Ver detalles del certificado
signtool verify /pa /v "dist\LubricentroWinter.exe" 2>&1 | findstr "Signing Certificate"
```

Salida esperada:
```
Successfully verified: dist\LubricentroWinter.exe
...
Signing Certificate Chain:
    Issued to: Tu Empresa S.A.
    Issued by: Sectigo Code Signing CA
    Expires:   2025-07-15
```

---

## 7. Renovación Anual

Los certificados Code Signing duran **1-3 años**. Antes de expirar:

1. Renovar con el proveedor (generalmente mismo proceso)
2. Descargar nuevo `.pfx`
3. Actualizar secrets en GitHub:
   - `SIGN_CERT_BASE64` → nuevo base64
   - `SIGN_CERT_PASSWORD` → nuevo password (si cambió)
4. Probar build local y CI

---

## 8. Archivos Relacionados

| Archivo | Qué hace |
|---------|----------|
| `build/build_windows.bat` | Build local con firma condicional |
| `.github/workflows/release.yml` | CI/CD con firma condicional |
| `build/launcher.py` | PyInstaller spec implícito (`--uac-admin`) |
| `updater.py` | `APP_VERSION = "0.3.0"` (se actualiza en cada release) |

---

## 9. Checklist de Release

- [ ] Actualizar `APP_VERSION` en `updater.py`
- [ ] Actualizar `CHANGELOG.md` con cambios de la versión
- [ ] Commit y push
- [ ] Crear tag: `git tag v0.3.0 && git push origin v0.3.0`
- [ ] Verificar GitHub Actions: build + test + release
- [ ] Verificar firma: descargar ZIP del release y `signtool verify`
- [ ] Probar instalación limpia en Windows (VM o máquina limpia)
- [ ] Confirmar: no SmartScreen, no antivirus, UAC pide admin correctamente