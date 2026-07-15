# Sistema de Gestión para LUBRICENTRO WINTER

## Descripción
Proyecto de sistema de gestión de stock y punto de venta (POS) para el lubricentro familiar, desarrollado bajo requerimientos específicos para optimizar el control de inventario y servicios.

## Estado del Proyecto
Finalizada la Fase 1 (Infraestructura), Fase 2 (Gestión de Inventario: Productos, Categorías, Proveedores), Fase 3 (Movimientos de Stock) y Fase 4 (Gestión de Clientes, Vehículos y Servicios).

## Estructura Técnica
- **Framework:** Streamlit
- **Base de Datos:** SQLite
- **Módulos:**
- `database.py`: Lógica de datos y persistencia.
   - `pages/1_Categorias.py`: Gestión de categorías.
   - `pages/2_Proveedores.py`: Gestión de proveedores.
   - `pages/3_Productos.py`: Gestión de productos.
   - `pages/4_Movimientos_Stock.py`: Registro de movimientos de stock (entradas/salidas).
   - `pages/5_Clientes.py`: Gestión de clientes.
   - `pages/6_Vehiculos.py`: Gestión de vehículos.
   - `pages/7_Servicios.py`: Gestión de servicios.
   - `pages/8_OrdenesServicio.py`: Gestión de órdenes de servicio (productos y servicios).
   - `app.py`: Dashboard principal con métricas y navegación.

## Próximos Pasos
- Fase 5: Reportes (ventas, inventario, ingresos vs egresos).