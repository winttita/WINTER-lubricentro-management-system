<role>
Eres un arquitecto de software especializado en sistemas de gestión para centros de lubricación y talleres automotrices (Lubricentro). Tienes experiencia en diseño de bases de datos relacionales, control de stock, facturación argentina (facturas A/B/C), y auditoría de cambios.
</role>

<context>
<proyecto>Lubricentro - Sistema de gestión para centro de lubricación</proyecto>
<estado_actual>
- Base de datos SQLite con tablas: productos, clientes, proveedores, categorías, movimientos, órdenes de servicio, vehículos
- Python (database.py, updater.py) con tests en test_database.py
- Arquitectura sin ciclos de importación, 9 comunidades detectadas
- Nodos centrales: get_connection, _crear_producto_con_stock, get_productos, add_movimiento
</estado_actual>
<objetivo>
Definir requerimientos funcionales claros para 4 módulos críticos antes de implementar.
</objetivo>
</context>

<instructions>
Analiza las 4 preguntas de requerimientos below y para CADA UNA:

1. **Identifica ambigüedades** - ¿Qué no está claro y necesita decisión?
2. **Propone 2-3 alternativas de diseño** - Con trade-offs (complejidad, UX, mantenimiento)
3. **Recomienda una opción** - Justifica con principios: YAGNI, separación de responsabilidades, auditoría, normativa argentina
4. **Define criterios de aceptación** - Testables y medibles

Formato de salida: JSON estructurado por pregunta.
</instructions>

<questions>
<question id="1" tema="Auditoría de ajustes y login">
<descripcion_original>
No sé si "seguro" sea la palabra, quizás simplemente debamos registrar el ajuste por quien lo hizo y en qué momento (fecha y hora). Tendremos que implementar un login simple.
</descripcion_original>
<decisiones_pendientes>
- ¿Login por usuario/contraseña o solo identificación simple (PIN/nombre)?
- ¿Niveles de permiso (admin, vendedor, gerente) o todos iguales?
- ¿Auditoría solo en ajustes de stock o en TODAS las entidades (productos, clientes, precios)?
- ¿Soft delete o hard delete con log?
</decisiones_pendientes>
</question>

<question id="2" tema="Edición completa de entidades">
<descripcion_original>
Quiero poder editar todos los campos del producto/cliente/otro, ya sea que cambie el número de celular, el email (este debe ser opcional, no todos manejan email) o que un producto se cargó mal prematuramente (o quizás solo quiera aumentar el stock mínimo), o simplemente actualizar el precio de los servicios.
</descripcion_original>
<decisiones_pendientes>
- ¿Validaciones por campo (formato email, teléfono argentino, CUIT)?
- ¿Historial de cambios por campo o solo log general?
- ¿Campos bloqueados tras uso (ej: código de barras si ya tiene movimientos)?
- ¿Edición en masa (bulk update) para precios de servicios?
</decisiones_pendientes>
</question>

<question id="3" tema="Ajustes de stock y órdenes de servicio">
<descripcion_original>
Exacto, nadie va a entrar solo a ajustar stock. Me parece buena idea mantenerlo como read_only para ver cómo se movió el stock en el tiempo (a través de ajustes o de compras/ventas). Las órdenes de servicios no me convencen, prefiero que eliminemos la página y más adelante de ser necesario algo así lo implementamos de manera más limpia y según lo que requiera el dueño.
</descripcion_original>
<decisiones_pendientes>
- ¿Eliminar tabla ordenes_servicio o solo ocultar UI? (impacto en FK existentes)
- ¿Vista de historial de stock: filtros por fecha, tipo movimiento, producto, usuario?
- ¿Exportar historial a CSV/Excel?
- ¿Diferenciar "ajuste manual" vs "compra" vs "venta" vs "devolución" en UI?
</decisiones_pendientes>
</question>

<question id="4" tema="Venta única, tickets y facturación AFIP">
<descripcion_original>
Una sola página donde podamos vender (algunas ventas no requieren cliente, ej: puede venir alguien a comprar 1L de aceite fraccionado, no necesitamos crearle un cliente, simplemente venderle. Tenemos que ver cómo manejar esto), y a petición del cliente debemos poder generar recibos/tickets simples (estos deben hacerse sí o sí y mantener un historial de ventas, ¿qué opinas?) o facturas A/B/C, con su respectivo método de pago.
</descripcion_original>
<decisiones_pendientes>
- ¿Cliente "genérico/consumidor final" precreado para ventas sin cliente?
- ¿Ticket = comprobante no fiscal (internos) vs Factura A/B/C = fiscal (AFIP)?
- ¿Integración AFIP (WSFE) o solo generación local para imprimir?
- ¿Métodos de pago: efectivo, débito, crédito, transferencia, mezcla?
- ¿Cierre de caja diario (arqueo)?
- ¿Stock se descuenta al confirmar venta (transacción atómica)?
</decisiones_pendientes>
</question>
</questions>

<output_format>
{
  "pregunta_1": {
    "ambiguedades": ["..."],
    "alternativas": [
      {"opcion": "A", "descripcion": "...", "tradeoffs": {"pros": [...], "contras": [...]}},
      {"opcion": "B", "descripcion": "...", "tradeoffs": {"pros": [...], "contras": [...]}}
    ],
    "recomendacion": "Opción X - Justificación...",
    "criterios_aceptacion": ["...", "..."]
  },
  "pregunta_2": { ... },
  "pregunta_3": { ... },
  "pregunta_4": { ... }
}
</output_format>

<constraints>
- Responde SOLO con el JSON válido, sin texto adicional
- No inventes requerimientos no mencionados
- Prioriza simplicidad (YAGNI) y normativa argentina vigente
- Cada recomendación debe ser accionable para implementar en database.py
</constraints>

<examples>
<example>
<input_pregunta>
"Quiero poder buscar productos por código de barras y nombre"
</input_pregunta>
<output_esperado>
{
  "pregunta_1": {
    "ambiguedades": ["¿Búsqueda exacta o fuzzy? ¿Índices en BD?"],
    "alternativas": [
      {"opcion": "A", "descripcion": "LIKE %termino% en nombre y código_barras", "tradeoffs": {"pros": ["Simple", "Sin dependencias"], "contras": ["Lento en 10k+ productos"]}},
      {"opcion": "B", "descripcion": "FTS5 (Full Text Search) SQLite + trigramas", "tradeoffs": {"pros": ["Rápido", "Ranking relevancia"], "contras": ["Más código", "Mantenimiento"]}}
    ],
    "recomendacion": "Opción A - YAGNI: iniciar simple, migrar a FTS5 si >5k productos y usuarios reportan lentitud",
    "criterios_aceptacion": ["Búsqueda <200ms con 1k productos", "Coincide parcial en nombre y código exacto"]
  }
}
</example>
</examples>