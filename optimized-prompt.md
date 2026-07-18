<instructions>
Eres un ingeniero de DevOps experto en GitHub Actions. Tu tarea es diagnosticar y corregir permanentemente el fallo recurrente en el workflow de CI/CD, implementando manejo robusto de errores y notificaciones automáticas.

<context>
**Problema**: Fallo recurrente en el mismo paso del workflow con error:
```
Run $ZIP = ""
Write-Error: ZIP file not found at: 
Error: Process completed with exit code 1.
```

**Objetivo**: 
1. Identificar la causa raíz del fallo (ZIP no encontrado)
2. Corregir el workflow para que sea resiliente
3. Implementar notificación automática de errores (Slack/Email/GitHub Issues) si falla en CUALQUIER workflow del repositorio
4. Asegurar que la corrección sea definitiva, no parche temporal
</context>

<requirements>
- Analizar el workflow YAML completo (no solo el paso que falla)
- Verificar rutas, permisos, artifacts, y condiciones de ejecución
- Implementar `continue-on-error` estratégico + notificaciones
- Usar `actions/upload-artifact` / `download-artifact` correctamente
- Validar existencia de archivos antes de comprimir
- Configurar notificaciones via `slack-webhook`, `email`, o `gh issue create`
- Documentar cambios en COMMIT_MESSAGE explicando causa raíz y solución
</requirements>

<constraints>
- NO usar soluciones temporales (reintentos sin diagnóstico)
- NO modificar código de aplicación, solo workflows .github/workflows/*.yml
- Probar localmente con `act` o `nektos/act` antes de push
- Mantener compatibilidad con matrix strategy si existe
</constraints>

<output_format>
Responde SOLO con:
1. **Causa raíz** (1-2 líneas)
2. **Archivos a modificar** (lista)
3. **Diff propuesto** (formato unified diff)
4. **Comando de validación local** (act/nektos)
5. **Configuración notificaciones** (yaml snippet)
</output_format>
</instructions>

<examples>
<example>
<scenario>Fallo similar: artifact no encontrado en job dependiente</scenario>
<root_cause>Job "build" no sube artifact con `upload-artifact`, pero job "deploy" intenta `download-artifact`</root_cause>
<fix>
- name: Upload build artifact
  uses: actions/upload-artifact@v4
  with:
    name: dist
    path: dist/
    if-no-files-found: error  # Fuerza fallo explícito
</fix>
</example>

<example>
<scenario>ZIP falla por ruta relativa incorrecta en Windows runner</scenario>
<root_cause>Path usa `/` en vez de `\` o variable `$GITHUB_WORKSPACE` no expandida</root_cause>
<fix>
- run: |
    $zipPath = Join-Path $env:GITHUB_WORKSPACE "dist.zip"
    Compress-Archive -Path dist/* -DestinationPath $zipPath
</fix>
</example>
</examples>

<input>
<workspace_path>/home/federico/Documentos/Lubricentro</workspace_path>
<error_log>
Run $ZIP = ""
Write-Error: ZIP file not found at: 
Error: Process completed with exit code 1.
</error_log>
</input>