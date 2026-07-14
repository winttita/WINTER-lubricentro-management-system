import sqlite3
import os
from datetime import datetime
import shutil

DB_NAME = "lubricentro.db"
BACKUP_DIR = "backups"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

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

# --- Funciones de Categorías ---
def get_categorias():
    conn = get_connection()
    categorias = conn.execute("SELECT * FROM categorias").fetchall()
    conn.close()
    return categorias

def add_categoria(nombre):
    conn = get_connection()
    try:
        param = None if nombre is None else nombre.strip()
        conn.execute("INSERT INTO categorias (nombre) VALUES (?)", (param,))
        conn.commit()
    except sqlite3.IntegrityError as e:
        msg = str(e)
        if "UNIQUE constraint failed" in msg:
            parts = msg.split(":")
            if len(parts) >= 2:
                rest = parts[1].strip()
                if "." in rest:
                    table = rest.split(".")[0]
                    if table == "categorias":
                        return False
        elif "NOT NULL constraint failed" in msg:
            parts = msg.split(":")
            if len(parts) >= 2:
                rest = parts[1].strip()
                if "." in rest:
                    table = rest.split(".")[0]
                    column = rest.split(".")[1] if "." in rest else ""
                    if table == "categorias" and column == "nombre":
                        return False
        raise
    finally:
        conn.close()
    return True

# --- Funciones de Proveedores ---
def get_proveedores():
    conn = get_connection()
    proveedores = conn.execute("SELECT * FROM proveedores").fetchall()
    conn.close()
    return proveedores

def add_proveedor(nombre, contacto, telefono, condiciones_pago):
    conn = get_connection()
    try:
        param = None if nombre is None else nombre.strip()
        conn.execute("INSERT INTO proveedores (nombre, contacto, telefono, condiciones_pago) VALUES (?, ?, ?, ?)",
                     (param, contacto, telefono, condiciones_pago))
        conn.commit()
    except sqlite3.IntegrityError as e:
        msg = str(e)
        if "UNIQUE constraint failed" in msg:
            parts = msg.split(":")
            if len(parts) >= 2:
                rest = parts[1].strip()
                if "." in rest:
                    table = rest.split(".")[0]
                    if table == "proveedores":
                        return False
        elif "NOT NULL constraint failed" in msg:
            parts = msg.split(":")
            if len(parts) >= 2:
                rest = parts[1].strip()
                if "." in rest:
                    table = rest.split(".")[0]
                    column = rest.split(".")[1] if "." in rest else ""
                    if table == "proveedores" and column == "nombre":
                        return False
        raise
    finally:
        conn.close()
    return True

# --- Funciones de Productos ---
def get_productos():
    conn = get_connection()
    productos = conn.execute("""
        SELECT p.*, c.nombre as categoria_nombre, prov.nombre as proveedor_nombre 
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN proveedores prov ON p.proveedor_id = prov.id
        WHERE p.activo = 1
    """).fetchall()
    conn.close()
    return productos

def add_producto(codigo_interno, codigo_barras, nombre, descripcion, categoria_id, proveedor_id, tipo_unidad, stock_minimo, precio_costo, precio_venta):
    # Ensure numeric fields are non-negative (optional)
    if stock_minimo < 0 or precio_costo < 0 or precio_venta < 0:
        return False
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO productos (codigo_interno, codigo_barras, nombre, descripcion, categoria_id, proveedor_id, tipo_unidad, stock_minimo, precio_costo, precio_venta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (codigo_interno, codigo_barras, nombre.strip() if nombre is not None else None, descripcion, categoria_id, proveedor_id, tipo_unidad, stock_minimo, precio_costo, precio_venta))
        conn.commit()
    except sqlite3.IntegrityError:
        # For producto, we re-raise all integrity errors to let tests expecting exceptions pass
        raise
    finally:
        conn.close()
    return True