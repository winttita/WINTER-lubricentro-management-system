import sqlite3
import os
from datetime import datetime
import shutil

DB_NAME = "lubricentro.db"
BACKUP_DIR = "backups"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Categorías
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    """)
    
    # 2. Proveedores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto TEXT,
            telefono TEXT,
            condiciones_pago TEXT CHECK(condiciones_pago IN (
                'Contado', 
                'Cuenta Corriente (7 días)', 
                'Cuenta Corriente (15 días)', 
                'Cuenta Corriente (30 días)', 
                'Otro'
            ))
        )
    """)
    
    # 3. Productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_interno TEXT UNIQUE,
            codigo_barras TEXT UNIQUE,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            categoria_id INTEGER,
            proveedor_id INTEGER,
            tipo_unidad TEXT CHECK(tipo_unidad IN ('Entero', 'Fraccionable')),
            stock_actual REAL DEFAULT 0,
            stock_minimo REAL DEFAULT 0,
            precio_costo REAL DEFAULT 0,
            precio_venta REAL DEFAULT 0,
            activo INTEGER DEFAULT 1,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id),
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
        )
    """)
    
    # 4. Catalogo Proveedor
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS catalogo_proveedor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER,
            proveedor_id INTEGER,
            precio_costo_proveedor REAL,
            FOREIGN KEY (producto_id) REFERENCES productos(id),
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
        )
    """)
    
    # 5. Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT
        )
    """)
    
    # 6. Vehículos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            patente TEXT NOT NULL UNIQUE,
            marca TEXT,
            modelo TEXT,
            anio INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)
    
    # 7. Servicios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL
        )
    """)
    
    # 8. Movimientos Stock
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER,
            tipo TEXT CHECK(tipo IN ('compra', 'venta', 'ajuste', 'devolucion', 'uso_interno')),
            cantidad REAL NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            motivo TEXT,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)
    
    # 9. Ordenes de Servicio
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordenes_servicio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cliente_id INTEGER,
            vehiculo_id INTEGER,
            total_productos REAL,
            total_servicios REAL,
            total_final REAL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id)
        )
    """)
    
    # 10. Orden Detalle
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orden_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER,
            producto_id INTEGER,
            servicio_id INTEGER,
            cantidad REAL,
            precio_unitario REAL,
            FOREIGN KEY (orden_id) REFERENCES ordenes_servicio(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id),
            FOREIGN KEY (servicio_id) REFERENCES servicios(id)
        )
    """)
    
    conn.commit()
    conn.close()

def backup_db():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    if os.path.exists(DB_NAME):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"lubricentro_backup_{timestamp}.db")
        shutil.copy2(DB_NAME, backup_path)
        return backup_path
    return None

if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada correctamente.")
