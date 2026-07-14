---
name: document-code
description: Guía para documentar código de forma consistente y generar documentación automática. Incluye buenas prácticas para docstrings, comentarios, y generación de documentación con herramientas como Sphinx o pdoc.
---

# Documentar Código

Este skill proporciona un conjunto de pautas y pasos para documentar el código de forma clara, mantenerla actualizada y generar documentación automática cuando sea necesario.

## Buenas prácticas generales

1. **Docstrings estándar**: Usa el formato de docstring de tu lenguaje (por ejemplo, PEP 257 para Python, Javadoc para Java, JSDoc para JavaScript).
2. **Comentarios explicativos**: Añade comentarios para explicar el *porqué* de decisiones complejas, no el *qué* (que debería quedar claro por el nombre).
3. **Mantener actualizada la documentación**: Cada vez que modificas una función o clase, revisa su documentación.
4. **Ejemplos de uso**: Incluye ejemplos simples dentro de los docstrings cuando sea útil.
5. **Evitar redundancia**: No documentes lo obvio; enfócate en la intención, parámetros poco claros, valores de retorno y excepciones.

## Pasos para documentar un módulo (ejemplo en Python)

1. **Encabezado del módulo**
   ```python
   """
   Breve descripción del módulo.

   Puede incluir:
   - Propósito general
   - Dependencias externas
   - Notas de uso
   """
   ```

2. **Clases**
   ```python
   class MiClase:
       """
       Descripción de la clase y su responsabilidad.

       Attributes:
           atributo1 (tipo): descripción.
           atributo2 (tipo): descripción.
       """
   ```

3. **Métodos y funciones**
   ```python
   def mi_funcion(param1: tipo, param2: tipo = default) -> tipo:
       """
       Descripción de qué hace la función.

       Args:
           param1 (tipo): descripción.
           param2 (tipo, opcional): descripción. Por defecto: valor.

       Returns:
           tipo: descripción del valor de retorno.

       Raises:
           ValorError: cuándo y por qué se lanza esta excepción.
           OtroError: otra condición de error.

       Example:
           >>> mi_funcion(1, 2)
           3
       """
       # implementación
   ```

4. **Constantes y variables de módulo**
   Añade comentarios al estilo `#: Descripción` (si tu herramienta lo soporta) o una línea arriba.

## Generar documentación automática

### Con Sphinx (recomendado para Python)

1. Instala sphinx y un tema:
   ```bash
   pip install sphinx sphinx-rtd-theme
   ```
2. Inicializa:
   ```bash
   sphinx-quickstart
   ```
   Acepta los valores por defecto o ajusta según tu proyecto.
3. En `conf.py`, asegúrate de que la ruta al código esté en `sys.path` y habilita extensiones como `autodoc`, `napoleon` (para Google/NumPy style), `viewcode`.
4. Genera los archivos .rst con:
   ```bash
   sphinx-apidoc -o source/ ../ruta/al/paquete
   ```
5. Construye:
   ```bash
   make html
   ```
   La documentación aparecerá en `_build/html`.

### Con pdoc (más simple)

1. Instala:
   ```bash
   pip install pdoc3
   ```
2. Genera documentación en línea:
   ```bash
   pdoc --html --output-dir docs mi_paquete
   ```
3. O sirve en modo servidor:
   ```bash
   pdoc --http :8080 mi_paquete
   ```

## Checklist antes de hacer commit

- [ ] Todas las funciones y clases públicas tienen docstring.
- [ ] Los docstrings siguen el estilo acordado (Google, NumPy, Sphinx).
- [ ] Los argumentos, retornos y excepciones están documentados.
- [ ] Los ejemplos en los docstrings son válidos (puedes probarlos con `doctest`).
- [ ] No hay comentarios obsoletos o código comentado que deba eliminarse.
- [ ] Si usas generación automática, verifica que la documentación se genere sin errores y que el contenido sea correcto.

## Adaptación a otros lenguajes

El mismo principio aplica a otros lenguajes; solo cambia el formato de los docstrings/comentarios y la herramienta de generación (por ejemplo, Javadoc + javadoc, Doxygen para C/C++, JSDoc + documentation.js, etc.).

--- 
*Este skill está pensado como guía general; adapta los pasos a las convenciones y herramientas específicas de tu proyecto.*