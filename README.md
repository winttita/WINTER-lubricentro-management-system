# Sistema de Gestión para LUBRICENTRO WINTER

## Descripción
Proyecto de sistema de gestión de stock y punto de venta (POS) para el lubricentro familiar, desarrollado bajo requerimientos específicos para optimizar el control de inventario y servicios.

## Estado del Proyecto
Finalizada la Fase 1 (Infraestructura), Fase 2 (Gestión de Inventario: Productos, Categorías, Proveedores) y Fase 3 (Movimientos de Stock).

## Estructura Técnica
- **Framework:** Streamlit
- **Base de Datos:** SQLite
- **Módulos:**
  - `database.py`: Lógica de datos y persistencia.
  - `pages/1_Categorias.py`: Gestión de categorías.
  - `pages/2_Proveedores.py`: Gestión de proveedores.
  - `pages/3_Productos.py`: Gestión de productos.
  - `pages/4_Movimientos_Stock.py`: Registro de movimientos de stock (entradas/salidas).
  - `app.py`: Dashboard principal con métricas y navegación.

## Próximos Pasos
- Fase 4: Gestión de Clientes, Vehículos y Servicios.
- Fase 5: Reportes (ventas, inventario, ingresos vs egresos).