# Edge Cases Encontrados — v0.4.3

Reporte de comportamientos con datos inválidos/incompletos/borde por módulo.

| Módulo | Caso | Comportamiento | Severidad |
|---|---|---|---|
| **Clientes** | `add_cliente("", ...)` | `False` — rechaza nombre vacío | ✅ Correcto |
| | `add_cliente(None, ...)` | `False` — rechaza None | ✅ Correcto |
| | `add_cliente("Juan", None, None)` | `True` — tel/email opcionales | ✅ Correcto |
| **Vehículos** | `add_vehiculo(..., "", ...)` | `False` — rechaza patente vacía | ✅ Correcto |
| | Patente duplicada | `False` — UNIQUE en patente | ✅ Correcto |
| | `cliente_id=None` | `True` — NULL FK permitido | ⚠️ Cosmético (no hay ventas sin cliente) |
| **Proveedores** | `add_proveedor("", ...)` | `True` — nombre vacío permitido | ⚠️ Bajo (UI debería validar, pero DB lo permite) |
| | `add_proveedor(None, ...)` | `False` — NOT NULL constraint | ✅ Correcto |
| | condición_pago inválida | `IntegrityError` propagado | ✅ Correcto |
| **Servicios** | `add_servicio("", 100)` | `False` | ✅ Correcto |
| | `add_servicio("Test", -1)` | `False` — precio negativo | ✅ Correcto |
| | `add_servicio("Test", 0)` | `True` — precio 0 permitido | ⚠️ Bajo (servicio gratuito puede tener sentido) |
| | `add_servicio("Test", None)` | `False` — TypeError manejado | ✅ Corregido en v0.4.3 |
| **Categorías** | `add_categoria("")` | `True` — nombre vacío permitido | ⚠️ Cosmético |
| | `add_categoria(None)` | `False` — NOT NULL | ✅ Correcto |
| | Duplicado | `False` | ✅ Correcto |
| **Productos** | `add_producto("", "", "", ...)` | `True` — nombre vacío permitido | ⚠️ Bajo (falta validación en función) |
| | `add_producto("", "   ", "", ...)` | `True` — whitespace permitido | ⚠️ Bajo |
| | tipo_unidad inválido | `IntegrityError` propagado | ✅ Correcto |
| | Códigos duplicados | `IntegrityError` propagado | ✅ Correcto |
| **Stock** | `crear_ajuste_stock(id, 15, "", 1)` | `False` — motivo obligatorio | ✅ Correcto |
| | `crear_ajuste_stock(id, -5, "motivo", 1)` | `False` — stock negativo | ✅ Correcto |
| | Producto inexistente | `False` | ✅ Correcto |
| **Ventas** | Cantidad 0 | Rechazado con mensaje "Cantidad inválida (0)" | ✅ Correcto |
| | Cantidad negativa | Rechazado | ✅ Correcto |
| | Stock insuficiente | Mensaje específico con nombre producto | ✅ Correcto |
| | Items vacíos | Mensaje específico | ✅ Correcto |
| | tipo_comprobante inválido | Mensaje específico | ✅ Correcto |
| | Precio negativo | Rechazado | ✅ Correcto |
| | Producto inactivo | Rechazado con mensaje | ✅ Correcto |
| | cuenta_corriente sin cliente | Rechazado | ✅ Correcto |
| **Órdenes** | `add_orden_detalle(..., cantidad=0)` | `True` — cantidad 0 permitida | ⚠️ Bajo (producto gratis, sin stock) |
| | Producto inexistente | `False` | ✅ Correcto |
| | Servicio inexistente | `False` | ✅ Correcto |
| | Sin producto ni servicio | `False` | ✅ Correcto |
| **Compras** | `crear_compra(prov, [])` | `None` — items vacíos | ✅ Correcto |
| | `crear_compra(prov, None)` | `None` | ✅ Correcto |
| | `crear_compra(None, items)` | `None` — proveedor None | ✅ Correcto |
| **Caja** | `abrir_caja` con caja ya abierta | `None` | ✅ Correcto |
| | `cerrar_caja` ya cerrada | `False` | ✅ Correcto |
| | `cerrar_caja` inexistente | `False` | ✅ Correcto |
| | `registrar_movimiento_caja` tipo inválido | `False` | ✅ Correcto |
| **Aumentos** | Porcentaje 0 | True, no cambia precios | ✅ Correcto |
| | Porcentaje negativo | Rechazado | ✅ Correcto |
| | Proveedor/categoría inexistente | `False`/`0` | ✅ Correcto |
| **Lista Precios** | Productos sin stock | Excluidos de la lista | ✅ Correcto |
| | Productos inactivos | Excluidos | ✅ Correcto |
