# Sistema de Gestión para LUBRICENTRO WINTER

## Descripción
Proyecto de sistema de gestión de stock y punto de venta (POS) para el lubricentro familiar, desarrollado bajo requerimientos específicos para optimizar el control de inventario y servicios.

## Estado del Proyecto
Finalizada la Fase 1 (Infraestructura) y Fase 2 (Gestión de Inventario: Productos, Categorías, Proveedores). Se han corregido los problemas de integridad de la base de datos y se han pasado todas las pruebas unitarias.

## Estructura Técnica
- **Framework:** Streamlit
- **Base de Datos:** SQLite con claves foráneas habilitadas
- **Módulos:**
  - `database.py`: Lógica de datos y persistencia (con validaciones y manejo de errores)
  - `pages/1_Categorias.py`: Gestión de categorías
  - `pages/2_Proveedores.py`: Gestión de proveedores
  - `pages/3_Productos.py`: Gestión de productos

