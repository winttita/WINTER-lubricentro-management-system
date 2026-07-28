# Plan de Mejoras - Lubricentro v0.4.2

## Resumen
Plan detallado para implementar 5 mejoras solicitadas por el usuario:
1. Manejo de caja (simple)
2. IntegrityError faltantes
3. Carteles de éxito/error consistentes
4. Soft delete de clientes
5. Validación de fracciones en productos "Entero"

---

## 1. Manejo de caja (simple)

### Contexto
No existe ninguna funcionalidad de caja en el sistema actual.

### Propuesta
Crear módulo básico de caja con apertura, cierre y seguimiento de movimientos vinculados a ventas.

### Cambios en database.py
1. **Nueva tabla `caja`:**
```sql
CREATE TABLE IF NOT EXISTS caja (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    saldo_inicial REAL NOT NULL,
    saldo_actual REAL NOT NULL,
    fecha_apertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre TIMESTAMP,
    usuario_id INTEGER NOT NULL,
    abierta INTEGER DEFAULT 1,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

2. **Nueva tabla `movimientos_caja`:**
```sql
CREATE TABLE IF NOT EXISTS movimientos_caja (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caja_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('apertura', 'cierre', 'ajuste', 'ingreso_venta')),
    monto REAL NOT NULL,
    saldo_anterior REAL NOT NULL,
    saldo_nuevo REAL NOT NULL,
    observacion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (caja_id) REFERENCES caja(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

3. **Funciones API:**
```python
def abrir_caja(saldo_inicial, usuario_id):
    # Abre una nueva caja
    
def cerrar_caja(caja_id, saldo_final, usuario_id):
    # Cierra una caja abierta
    
def get_caja_abierta():
    # Obtiene la caja actualmente abierta
    
def registrar_movimiento_caja(caja_id, tipo, monto, saldo_anterior, saldo_nuevo, observacion, usuario_id):
    # Registra un movimiento en caja
```

### UI: pages/8_Caja.py
- Botón "Abrir caja" (requiere saldo inicial)
- Al cerrar: input para ingresar saldo final (arqueo real)
- Historial de movimientos de caja con filtros por fecha/tipo
- Mostrar estado actual: caja abierta/cerrada, saldo actual

### Integración
En `database.py:crear_venta()`: Si hay caja abierta, registrar automáticamente un movimiento de tipo 'ingreso_venta' con el total de la venta.

---

## 2. IntegrityError faltantes (rápido)

### Contexto
Algunas funciones de UI no manejan `sqlite3.IntegrityError` al eliminar/editar registros con claves foráneas.

### Archivos a revisar
1. `pages/0_Gestion.py`:
   - Editar/Eliminar cliente (líneas 55-68)
   - Editar/Eliminar proveedor 
   - Editar/Eliminar categoría

2. `pages/3_Productos.py`:
   - Editar/Eliminar producto

3. `pages/1_Stock.py`:
   - Ajustes de stock

### Implementación
En cada operación que modifica/elimina registros:
```python
try:
    # operación DB
    st.success("✅ [Operación] completada")
except sqlite3.IntegrityError as e:
    st.error("❌ Error: No se puede completar la operación debido a restricciones de integridad.")
except Exception as e:
    st.error(f"❌ Error inesperado: {str(e)}")
```

### Mensajes
Consistentes con mejora 3: usar emojis ✅ para éxito, ❌ para errores.

---

## 3. Carteles de éxito/error consistentes

### Contexto
Hay 77 ocurrencias de `st.success`/`st.error` en pages/, pero falta consistencia en formato y emojis.

### Estándar a aplicar
- **Éxito:** `st.success("✅ [Descripción de la acción] correctamente")`
- **Error:** `st.error("❌ Error al [descripción de la acción]")`
- **Advertencia:** `st.warning("⚠️ [Mensaje informativo]")` (solo para avisos no errores)

### Archivos a revisar
Todas las páginas en `pages/`:
- 0_Gestion.py
- 1_Stock.py  
- 2_Reportes.py
- 3_Productos.py
- 4_Ordenes.py
- 5_Clientes.py
- 6_Proveedores.py
- 7_Ventas.py

### Acciones
Revisar cada uso de `st.success`/`st.error`/`st.info` y aplicar el formato estándar.

---

## 4. Soft delete de clientes

### Contexto
El DELETE actual falla por claves foráneas cuando el cliente tiene ventas, vehículos, órdenes de servicio o cuenta corriente asociados.

### Propuesta
Implementar soft delete en lugar de hard delete.

### Cambios en database.py
1. **Migración:** Agregar columna `activo` a tabla clientes
```sql
ALTER TABLE clientes ADD COLUMN activo INTEGER DEFAULT 1;
```

2. **Modificar `get_clientes()`:**
```python
def get_clientes(incluir_inactivos=False):
    conn = get_connection()
    if incluir_inactivos:
        query = "SELECT * FROM clientes"
    else:
        query = "SELECT * FROM clientes WHERE activo = 1"
    clientes = conn.execute(query).fetchall()
    conn.close()
    return clientes
```

3. **Nueva función:**
```python
def desactivar_cliente(cliente_id):
    # Marca cliente como inactivo (activo=0)
    
def reactivar_cliente(cliente_id):
    # Reactiva cliente (activo=1)
```

### UI: pages/0_Gestion.py
- Cambiar botón "🗑️ Eliminar" por "🗑️ Desactivar"
- Al hacer click, mostrar confirmación con mensaje:
  - "¿Desactivar cliente [nombre]?"
  - Si tiene asociados: "Este cliente tiene [X] ventas, [Y] vehículos, [Z] órdenes. Al desactivarlo, estos registros seguirán existiendo pero no se podrán crear nuevos."
- Mantener botón de edición como está
- Agregar filtro "Mostrar inactivos" en la lista de clientes
- Para clientes inactivos: mostrar opción "Reactivar"

### Comportamiento
- Los clientes inactivos no aparecen en combobox de selección (ventas, órdenes, etc.)
- Los clientes inactivos siguen siendo mostrados en reportes históricos
- Se puede reactivar en cualquier momento

---

## 5. Validación de fracciones en productos "Entero"

### Contexto
Los productos tienen `tipo_unidad` con CHECK constraint `IN ('Entero', 'Fraccionable')`. Actualmente se permiten cantidades fraccionarias en ventas/órdenes incluso para productos "Entero".

### Propuesta
Bloquear guardar cantidad fraccionaria para productos "Entero" con mensaje específico.

### Archivos a modificar
1. `pages/7_Ventas.py` (líneas 101-105)
2. `pages/4_Ordenes.py` (líneas 154-155)

### Implementación
En ambos formularios, al intentar guardar/agregar ítem:
```python
# Obtener tipo_unidad del producto seleccionado
tipo_unidad = prod_lookup[pid][7]  # índice 7 = tipo_unidad

# Validar cantidad
if tipo_unidad == 'Entero' and not float(cantidad).is_integer():
    st.error("❌ No se puede vender este artículo fraccionado, seleccione una cantidad entera (ej: 1, 2, 3)")
    # No permitir guardar/agregar el ítem
else:
    # Proceder normalmente
```

### Experiencia de usuario
1. Usuario selecciona producto "ACEITE ENVASADO X4L" (tipo Entero)
2. En el number_input de cantidad, ingresa "1.5"
3. Al intentar guardar el ítem (o al cambiar de foco), mostrar error:
   ❌ No se puede vender este artículo fraccionado, seleccione una cantidad entera (ej: 1, 2, 3)
4. El ítem no se agrega/guarda hasta que ingrese cantidad entera

### Nota
Además del validation al guardar, se puede mejorar UX forzando `step=1` en el number_input cuando tipo_unidad == 'Entero', pero la validación crítica es al guardar.

---

## Próximos pasos

1. **Mañana:**
   - Implementar mejora 1 (caja): crear tabla, funciones API y página UI
   - Implementar mejora 2 (IntegrityError): revisar páginas y agregar try/except donde falte
   - Implementar mejora 3 (carteles): estandarizar mensajes en todas las páginas

2. **Pasado mañana:**
   - Implementar mejora 4 (clientes soft delete): migración DB, modificar get_clientes, actualizar UI
   - Implementar mejora 5 (fracciones): agregar validación en ventas y órdenes

3. **Testing:**
   - Verificar que las 85 pruebas existentes siguen pasando
   - Probar manualmente cada nueva funcionalidad
   - Verificar que no se introdujeron regresiones

4. **Documentación:**
   - Actualizar README si es necesario
   - Documentar nuevas tablas y funciones en comentarios del código

---
*Plan creado para implementación en versión 0.4.2*