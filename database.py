import sqlite3
import os
from datetime import datetime
import shutil

# Adapter for datetime -> ISO 8601 string to avoid deprecation warning in Python 3.12+
sqlite3.register_adapter(datetime, lambda val: val.isoformat())

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
    
    # 11. Usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'operador',
            activo INTEGER DEFAULT 1,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 12. Ajustes Stock
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ajustes_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            stock_anterior REAL NOT NULL,
            stock_nuevo REAL NOT NULL,
            diferencia REAL NOT NULL,
            motivo TEXT NOT NULL,
            usuario_id INTEGER NOT NULL,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producto_id) REFERENCES productos(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)
    
    # 13. Ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NULL,
            tipo_comprobante TEXT NOT NULL,
            punto_venta TEXT NOT NULL DEFAULT '0001',
            numero_comprobante INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            iva REAL NOT NULL DEFAULT 0,
            total REAL NOT NULL,
            metodo_pago TEXT NOT NULL,
            usuario_id INTEGER NOT NULL,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            UNIQUE(punto_venta, tipo_comprobante, numero_comprobante)
        )
    """)
    
    # 14. Venta Items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS venta_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad REAL NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)
    
    # 15. Cuenta Corriente
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cuenta_corriente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            venta_id INTEGER NOT NULL,
            monto REAL NOT NULL,
            saldo_anterior REAL NOT NULL,
            saldo_nuevo REAL NOT NULL,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (venta_id) REFERENCES ventas(id)
        )
    """)

    # 16. Compras a proveedores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proveedor_id INTEGER NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL DEFAULT 0,
            observaciones TEXT,
            estado TEXT NOT NULL DEFAULT 'confirmada',
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
        )
    """)

    # 17. Detalle de Compras
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            compra_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad REAL NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (compra_id) REFERENCES compras(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    conn.commit()

    # Seed: usuario admin por defecto (si no existe ninguno)
    exists = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    if exists == 0:
        conn.execute("""
            INSERT INTO usuarios (username, password_hash, nombre, rol)
            VALUES (?, ?, ?, ?)
        """, ("admin", "", "Administrador", "admin"))
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

def cleanup_old_backups(max_backups=10):
    """Elimina los backups más antiguos, conservando solo los últimos max_backups."""
    if not os.path.exists(BACKUP_DIR):
        return
    backups = []
    for f in os.listdir(BACKUP_DIR):
        path = os.path.join(BACKUP_DIR, f)
        if f.startswith("lubricentro_backup_") and f.endswith(".db"):
            backups.append((os.path.getmtime(path), path))
    backups.sort(reverse=True)  # más recientes primero
    for _, path in backups[max_backups:]:
        try:
            os.remove(path)
        except OSError:
            pass

# --- Funciones de Movimientos de Stock ---
def get_movimientos(limit=10):
    conn = get_connection()
    movimientos = conn.execute("""
        SELECT m.id, m.producto_id, m.tipo, m.cantidad, m.fecha, m.motivo, p.nombre as producto_nombre
        FROM movimientos_stock m
        JOIN productos p ON m.producto_id = p.id
        ORDER BY m.fecha DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return movimientos

def add_movimiento(producto_id, tipo, cantidad, motivo, fecha=None, conn=None):
    """
    Registra un movimiento de stock y actualiza el stock_actual del producto.
    Returns True si se realizó exitosamente, False si hay stock insuficiente u otro error.

    Si se pasa ``conn`` (una conexion sqlite3 abierta), se usa esa conexion
    en lugar de abrir una nueva. Esto es necesario cuando el caller ya tiene
    una transaccion abierta (por ejemplo crear_venta / crear_compra), porque
    SQLite bloquea una segunda conexion intentando escribir mientras la
    primera tiene una transaccion sin commitear ("database is locked").
    El caller es responsable del commit/rollback/close de su propia conexion.
    """
    # Validaciones básicas
    if producto_id is None or tipo is None or cantidad is None:
        return False
    if tipo not in ('compra', 'venta', 'ajuste', 'devolucion', 'uso_interno'):
        return False
    try:
        cantidad = float(cantidad)
    except (ValueError, TypeError):
        return False

    own_conn = conn is None
    if own_conn:
        conn = get_connection()
    try:
        # Obtener stock actual del producto
        cursor = conn.execute("SELECT stock_actual FROM productos WHERE id = ?", (producto_id,))
        row = cursor.fetchone()
        if row is None:
            return False  # producto no existe
        stock_actual = float(row[0])

        # Calcular el delta según el tipo
        if tipo in ('compra', 'devolucion'):
            delta = cantidad
        elif tipo in ('venta', 'uso_interno'):
            delta = -cantidad
        else:  # ajuste
            delta = cantidad  # cantidad puede ser positivo o negativo

        nuevo_stock = stock_actual + delta
        if nuevo_stock < 0:
            # No hay suficiente stock
            return False

        # Insertar movimiento
        if fecha is None:
            fecha = datetime.now()
        cursor = conn.execute("""
            INSERT INTO movimientos_stock (producto_id, tipo, cantidad, fecha, motivo)
            VALUES (?, ?, ?, ?, ?)
        """, (producto_id, tipo, cantidad, fecha, motivo))
        movimiento_id = cursor.lastrowid

        # Actualizar stock del producto
        conn.execute("UPDATE productos SET stock_actual = ? WHERE id = ?", (nuevo_stock, producto_id))

        if own_conn:
            conn.commit()
        return True
    except Exception as e:
        # En caso de cualquier error, hacemos rollback (solo de nuestra propia conexion)
        conn.rollback()
        return False
    finally:
        if own_conn:
            conn.close()

# --- Funciones de Clientes ---
def get_clientes():
    conn = get_connection()
    clientes = conn.execute("SELECT * FROM clientes ORDER BY nombre").fetchall()
    conn.close()
    return clientes

def add_cliente(nombre, telefono, email):
    if not nombre or not nombre.strip():
        return False
    conn = get_connection()
    try:
        conn.execute("INSERT INTO clientes (nombre, telefono, email) VALUES (?, ?, ?)",
                     (nombre.strip(), telefono, email))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

# --- Funciones de Vehículos ---
def get_vehiculos():
    conn = get_connection()
    vehiculos = conn.execute("""SELECT v.id, v.cliente_id, v.patente, v.marca, v.modelo, v.anio, c.nombre as cliente_nombre
                               FROM vehiculos v
                               LEFT JOIN clientes c ON v.cliente_id = c.id
                               ORDER BY v.patente""").fetchall()
    conn.close()
    return vehiculos

def add_vehiculo(cliente_id, patente, marca, modelo, anio):
    if not patente or not patente.strip():
        return False
    conn = get_connection()
    try:
        conn.execute("INSERT INTO vehiculos (cliente_id, patente, marca, modelo, anio) VALUES (?, ?, ?, ?, ?)",
                     (cliente_id, patente.strip(), marca, modelo, anio))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

# --- Funciones de Servicios ---
def get_servicios():
    conn = get_connection()
    servicios = conn.execute("SELECT * FROM servicios ORDER BY nombre").fetchall()
    conn.close()
    return servicios

def add_servicio(nombre, precio):
    if not nombre or not nombre.strip():
        return False
    try:
        precio = float(precio)
        if precio < 0:
            return False
    except ValueError:
        return False
    conn = get_connection()
    try:
        conn.execute("INSERT INTO servicios (nombre, precio) VALUES (?, ?)",
                     (nombre.strip(), precio))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

# --- Funciones de Ordenes de Servicio ---
def get_ordenes(limit=10):
    conn = get_connection()
    ordenes = conn.execute("""SELECT o.id, o.fecha, o.total_productos, o.total_servicios, o.total_final,
                                   c.nombre as cliente_nombre, v.patente as vehiculo_patente
                            FROM ordenes_servicio o
                            LEFT JOIN clientes c ON o.cliente_id = c.id
                            LEFT JOIN vehiculos v ON o.vehiculo_id = v.id
                            ORDER BY o.fecha DESC
                            LIMIT ?""", (limit,)).fetchall()
    conn.close()
    return ordenes

def add_orden_servicio(cliente_id, vehiculo_id, fecha=None):
    if fecha is None:
        fecha = datetime.now()
    conn = get_connection()
    try:
        cursor = conn.execute("INSERT INTO ordenes_servicio (fecha, cliente_id, vehiculo_id, total_productos, total_servicios, total_final) VALUES (?, ?, ?, 0, 0, 0)",
                              (fecha, cliente_id, vehiculo_id))
        conn.commit()
        orden_id = cursor.lastrowid
        return orden_id
    except Exception:
        return None
    finally:
        conn.close()

def add_orden_detalle(orden_id, producto_id=None, servicio_id=None, cantidad=1, precio_unitario=None):
    conn = get_connection()
    try:
        if producto_id is not None:
            # get product price
            prod = conn.execute("SELECT precio_venta FROM productos WHERE id = ?", (producto_id,)).fetchone()
            if prod is None:
                return False
            if precio_unitario is None:
                precio_unitario = prod[0]
            # Insert detalle
            conn.execute("INSERT INTO orden_detalle (orden_id, producto_id, servicio_id, cantidad, precio_unitario) VALUES (?, ?, ?, ?, ?)",
                         (orden_id, producto_id, None, cantidad, precio_unitario))
            # Update order totals: add to total_productos
            conn.execute("UPDATE ordenes_servicio SET total_productos = total_productos + ? WHERE id = ?", (cantidad * precio_unitario, orden_id))
            # Also create movement of tipo 'uso_interno' for stock deduction
            if not add_movimiento(producto_id, 'uso_interno', cantidad, f'Uso en orden de servicio #{orden_id}', conn=conn):
                conn.rollback()
                return False
        elif servicio_id is not None:
            serv = conn.execute("SELECT precio FROM servicios WHERE id = ?", (servicio_id,)).fetchone()
            if serv is None:
                return False
            if precio_unitario is None:
                precio_unitario = serv[0]
            conn.execute("INSERT INTO orden_detalle (orden_id, producto_id, servicio_id, cantidad, precio_unitario) VALUES (?, ?, ?, ?, ?)",
                         (orden_id, None, servicio_id, cantidad, precio_unitario))
            # Update total_servicios
            conn.execute("UPDATE ordenes_servicio SET total_servicios = total_servicios + ? WHERE id = ?", (cantidad * precio_unitario, orden_id))
        else:
            return False
        # Update total_final
        conn.execute("""UPDATE ordenes_servicio SET total_final = 
                        (SELECT COALESCE(SUM(cantidad * precio_unitario), 0) 
                         FROM orden_detalle 
                         WHERE orden_id = ?) WHERE id = ?""", (orden_id, orden_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        conn.close()

def get_orden_detalle(orden_id):
    conn = get_connection()
    detalle = conn.execute("""SELECT d.id, d.producto_id, d.servicio_id, d.cantidad, d.precio_unitario,
                                   p.nombre as producto_nombre, s.nombre as servicio_nombre
                            FROM orden_detalle d
                            LEFT JOIN productos p ON d.producto_id = p.id
                            LEFT JOIN servicios s ON d.servicio_id = s.id
                            WHERE d.orden_id = ?""", (orden_id,)).fetchall()
    conn.close()
    return detalle

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

def add_producto(codigo_interno, codigo_barras, nombre, descripcion, categoria_id, proveedor_id, tipo_unidad, stock_minimo, precio_costo, precio_venta, stock_inicial=0):
    # Ensure numeric fields are non-negative (optional)
    if stock_minimo < 0 or precio_costo < 0 or precio_venta < 0:
        return False
    try:
        stock_inicial = float(stock_inicial)
    except (ValueError, TypeError):
        stock_inicial = 0.0
    if stock_inicial < 0:
        return False
    conn = get_connection()
    try:
        cursor = conn.execute("""
            INSERT INTO productos (codigo_interno, codigo_barras, nombre, descripcion, categoria_id, proveedor_id, tipo_unidad, stock_minimo, precio_costo, precio_venta, stock_actual)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (codigo_interno, codigo_barras, nombre.strip() if nombre is not None else None, descripcion, categoria_id, proveedor_id, tipo_unidad, stock_minimo, precio_costo, precio_venta, stock_inicial))
        producto_id = cursor.lastrowid

        # Registrar movimiento de compra inicial si hay stock inicial > 0
        if stock_inicial > 0:
            conn.execute("""
                INSERT INTO movimientos_stock (producto_id, tipo, cantidad, fecha, motivo)
                VALUES (?, 'compra', ?, ?, ?)
            """, (producto_id, stock_inicial, datetime.now(), "Stock inicial al crear producto"))

        conn.commit()
    except sqlite3.IntegrityError:
        # For producto, we re-raise all integrity errors to let tests expecting exceptions pass
        raise
    finally:
        conn.close()
    return True

# --- Funciones de Reportes ---
def get_reporte_ventas(fecha_desde=None, fecha_hasta=None):
    """Reporte de ventas: ordenes de servicio y movimientos de venta en un rango de fechas.
    Devuelve tuplas (fecha, tipo, concepto, cantidad, monto)."""
    conn = get_connection()
    try:
        query_ordenes = """SELECT o.fecha, 'Orden de Servicio' as tipo, c.nombre as concepto, 1 as cantidad, o.total_final as monto
                          FROM ordenes_servicio o
                          LEFT JOIN clientes c ON o.cliente_id = c.id
                          WHERE 1=1"""
        params = []
        if fecha_desde:
            query_ordenes += " AND date(o.fecha) >= date(?)"
            params.append(fecha_desde)
        if fecha_hasta:
            query_ordenes += " AND date(o.fecha) <= date(?)"
            params.append(fecha_hasta)
        query_ordenes += " ORDER BY o.fecha DESC"
        ordenes = conn.execute(query_ordenes, params).fetchall()

        query_movs = """SELECT m.fecha, 'Venta (stock)' as tipo, p.nombre as concepto, m.cantidad, (m.cantidad * p.precio_venta) as monto
                       FROM movimientos_stock m
                       JOIN productos p ON m.producto_id = p.id
                       WHERE m.tipo = 'venta'"""
        params2 = []
        if fecha_desde:
            query_movs += " AND date(m.fecha) >= date(?)"
            params2.append(fecha_desde)
        if fecha_hasta:
            query_movs += " AND date(m.fecha) <= date(?)"
            params2.append(fecha_hasta)
        movs = conn.execute(query_movs, params2).fetchall()
        return list(ordenes) + list(movs)
    finally:
        conn.close()

def get_reporte_inventario():
    """Reporte de inventario actual: productos con stock y valorizacion."""
    conn = get_connection()
    try:
        inventario = conn.execute("""SELECT p.id, p.nombre, p.stock_actual, p.stock_minimo, p.precio_costo, p.precio_venta,
                                            c.nombre as categoria,
                                            (p.stock_actual * p.precio_costo) as valor_costo,
                                            (p.stock_actual * p.precio_venta) as valor_venta
                                     FROM productos p
                                     LEFT JOIN categorias c ON p.categoria_id = c.id
                                     WHERE p.activo = 1
                                     ORDER BY p.nombre""").fetchall()
        return inventario
    finally:
        conn.close()



def update_categoria(id, nombre):
    """Actualiza el nombre de una categoría existente."""
    if not nombre or not nombre.strip():
        return False
    conn = get_connection()
    try:
        cursor = conn.execute("""
            UPDATE categorias 
            SET nombre = ?
            WHERE id = ?
        """, (nombre.strip(), id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        # Nombre ya existe
        return False
    finally:
        conn.close()


def update_proveedor(id, nombre, contacto, telefono, condiciones_pago):
    """Actualiza los datos de un proveedor existente."""
    if not nombre or not nombre.strip():
        return False
    if condiciones_pago not in (
        'Contado', 
        'Cuenta Corriente (7 días)', 
        'Cuenta Corriente (15 días)', 
        'Cuenta Corriente (30 días)', 
        'Otro'
    ):
        return False
    conn = get_connection()
    try:
        cursor = conn.execute("""
            UPDATE proveedores 
            SET nombre = ?, contacto = ?, telefono = ?, condiciones_pago = ?
            WHERE id = ?
        """, (nombre.strip(), contacto, telefono, condiciones_pago, id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError as e:
        # Handle unique constraint violation on nombre
        if 'UNIQUE constraint failed' in str(e):
            return False  # Nombre de proveedor ya existe
        raise
    finally:
        conn.close()


def update_producto(id, codigo_interno, codigo_barras, nombre, descripcion, categoria_id, proveedor_id, tipo_unidad, stock_minimo, precio_costo, precio_venta):
    """Actualiza los datos de un producto existente."""
    # Validaciones básicas
    if not nombre or not nombre.strip():
        return False
    if tipo_unidad not in ('Entero', 'Fraccionable'):
        return False
    try:
        stock_minimo = float(stock_minimo)
        precio_costo = float(precio_costo)
        precio_venta = float(precio_venta)
        if stock_minimo < 0 or precio_costo < 0 or precio_venta < 0:
            return False
    except ValueError:
        return False
    
    conn = get_connection()
    try:
        cursor = conn.execute("""
            UPDATE productos 
            SET codigo_interno = ?, codigo_barras = ?, nombre = ?, descripcion = ?, 
                categoria_id = ?, proveedor_id = ?, tipo_unidad = ?, 
                stock_minimo = ?, precio_costo = ?, precio_venta = ?
            WHERE id = ?
        """, (
            codigo_interno.strip() if codigo_interno else None,
            codigo_barras.strip() if codigo_barras else None,
            nombre.strip(),
            descripcion,
            categoria_id,
            proveedor_id,
            tipo_unidad,
            max(0.0, stock_minimo),
            max(0.0, precio_costo),
            max(0.0, precio_venta),
            id
        ))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError as e:
        # Handle unique constraint violations
        if 'UNIQUE constraint failed' in str(e):
            return False  # Código interno o de barras duplicado
        raise
    finally:
        conn.close()


def update_cliente(id, nombre, telefono, email):
    """Actualiza los datos de un cliente existente."""
    if not nombre or not nombre.strip():
        return False
    conn = get_connection()
    try:
        cursor = conn.execute("""
            UPDATE clientes 
            SET nombre = ?, telefono = ?, email = ?
            WHERE id = ?
        """, (nombre.strip(), telefono, email, id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def update_vehiculo(id, cliente_id, patente, marca, modelo, anio):
    """Actualiza los datos de un vehículo existente."""
    if not patente or not patente.strip():
        return False
    try:
        anio_int = int(anio) if anio else None
        if anio_int and (anio_int < 1900 or anio_int > 2100):
            return False
    except ValueError:
        return False
    
    conn = get_connection()
    try:
        cursor = conn.execute("""
            UPDATE vehiculos 
            SET cliente_id = ?, patente = ?, marca = ?, modelo = ?, anio = ?
            WHERE id = ?
        """, (cliente_id, patente.strip(), marca, modelo, anio_int, id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        # Patente duplicada
        return False
    finally:
        conn.close()


def update_servicio(id, nombre, precio):
    """Actualiza los datos de un servicio existente."""
    if not nombre or not nombre.strip():
        return False
    try:
        precio_float = float(precio)
        if precio_float < 0:
            return False
    except ValueError:
        return False
    
    conn = get_connection()
    try:
        cursor = conn.execute("""
            UPDATE servicios 
            SET nombre = ?, precio = ?
            WHERE id = ?
        """, (nombre.strip(), precio_float, id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        # Nombre duplicado
        return False
    finally:
        conn.close()
def get_reporte_ingresos_egresos(fecha_desde=None, fecha_hasta=None):
    """Reporte de ingresos vs egresos.
    Ingresos = precio_venta * cantidad FROM movimientos_stock de tipo venta
    + total_final FROM ordenes_servicio  (los movimientos venta pueden duplicarse? ver nora).
    Egresos = precio_costo * cantidad FROM movimientos_stock donde tipo = compra."""
    conn = get_connection()
    try:
        egresos_query = """SELECT p.nombre as concepto, m.cantidad, (m.cantidad * p.precio_costo) as monto, m.fecha
                           FROM movimientos_stock m
                           JOIN productos p ON m.producto_id = p.id
                           WHERE m.tipo = 'compra'"""
        params_e = []
        if fecha_desde:
            egresos_query += " AND date(m.fecha) >= date(?)"
            params_e.append(fecha_desde)
        if fecha_hasta:
            egresos_query += " AND date(m.fecha) <= date(?)"
            params_e.append(fecha_hasta)
        egresos = conn.execute(egresos_query, params_e).fetchall()

        ingresos_query = """SELECT c.nombre as concepto, o.total_final as monto, o.fecha
                            FROM ordenes_servicio o
                            LEFT JOIN clientes c ON o.cliente_id = c.id"""
        params_i = []
        if fecha_desde:
            ingresos_query += " WHERE date(o.fecha) >= date(?)"
            params_i.append(fecha_desde)
            if fecha_hasta:
                ingresos_query += " AND date(o.fecha) <= date(?)"
                params_i.append(fecha_hasta)
        elif fecha_hasta:
            ingresos_query += " WHERE date(o.fecha) <= date(?)"
            params_i.append(fecha_hasta)
        ingresos = conn.execute(ingresos_query, params_i).fetchall()
        return list(ingresos), list(egresos)
    finally:
        conn.close()


# --- Funciones de Ventas ---
def get_ultimo_numero_comprobante(tipo_comprobante, punto_venta='0001'):
    """Obtiene el último número de comprobante para un tipo y punto de venta."""
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT MAX(numero_comprobante) FROM ventas 
            WHERE tipo_comprobante = ? AND punto_venta = ?
        """, (tipo_comprobante, punto_venta)).fetchone()
        return row[0] if row and row[0] else 0
    finally:
        conn.close()


def crear_venta(cliente_id, tipo_comprobante, items, metodo_pago, usuario_id):
    """
    Crea una venta completa con items, actualiza stock y registra movimiento.
    items: lista de dicts {producto_id, cantidad, precio_unitario}
    Retorna (venta_id, numero_comprobante, error_msg) donde error_msg es None si exito.
    """
    if not items:
        return None, None, "No hay items en la venta"
    if not isinstance(items, list):
        return None, None, "Items debe ser una lista"
    
    conn = get_connection()
    try:
        # Validar stock para todos los items antes de empezar (misma conexion)
        for item in items:
            if not isinstance(item, dict):
                return None, None, "Cada item debe ser un diccionario"
            if 'producto_id' not in item or 'cantidad' not in item or 'precio_unitario' not in item:
                return None, None, "Cada item debe tener producto_id, cantidad y precio_unitario"
            
            row = conn.execute("SELECT stock_actual, nombre FROM productos WHERE id = ? AND activo = 1", 
                             (item['producto_id'],)).fetchone()
            if not row:
                return None, None, f"Producto inactivo o inexistente (id={item['producto_id']})"
            stock_actual = float(row[0])
            nombre = row[1]
            cantidad = float(item['cantidad'])
            if stock_actual < cantidad:
                return None, None, f"Stock insuficiente de \"{nombre}\": solicitado {cantidad}, disponible {stock_actual}"
        
        # Calcular totales
        total = sum(float(item['cantidad']) * float(item['precio_unitario']) for item in items)
        if tipo_comprobante == 'factura_a':
            subtotal = round(total / 1.21, 2)
            iva = round(total - subtotal, 2)
        else:
            subtotal = round(total, 2)
            iva = 0.0
        
        # Obtener siguiente número de comprobante
        punto_venta = '0001'
        numero_comprobante = get_ultimo_numero_comprobante(tipo_comprobante, punto_venta) + 1
        
        # Insertar venta
        cursor = conn.execute("""
            INSERT INTO ventas (cliente_id, tipo_comprobante, punto_venta, numero_comprobante,
                              subtotal, iva, total, metodo_pago, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cliente_id, tipo_comprobante, punto_venta, numero_comprobante,
              subtotal, iva, total, metodo_pago, usuario_id))
        venta_id = cursor.lastrowid
        
        # Insertar items y actualizar stock
        for item in items:
            cantidad = float(item['cantidad'])
            precio_unitario = float(item['precio_unitario'])
            subtotal_item = round(cantidad * precio_unitario, 2)
            
            conn.execute("""
                INSERT INTO venta_items (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (venta_id, item['producto_id'], cantidad, precio_unitario, subtotal_item))
            
            # Registrar movimiento de venta (descuenta stock) usando la misma conexion
            if not add_movimiento(item['producto_id'], 'venta', cantidad, f'Venta #{venta_id}', conn=conn):
                conn.rollback()
                return None, None, f"Error al registrar movimiento de venta para producto {item['producto_id']}"
        
        # Si es cuenta corriente, registrar deuda
        if metodo_pago == 'cuenta_corriente' and cliente_id:
            # Obtener saldo anterior
            row = conn.execute("""
                SELECT COALESCE(SUM(monto), 0) FROM cuenta_corriente WHERE cliente_id = ?
            """, (cliente_id,)).fetchone()
            saldo_anterior = float(row[0]) if row else 0.0
            saldo_nuevo = saldo_anterior + total
            
            conn.execute("""
                INSERT INTO cuenta_corriente (cliente_id, venta_id, monto, saldo_anterior, saldo_nuevo)
                VALUES (?, ?, ?, ?, ?)
            """, (cliente_id, venta_id, total, saldo_anterior, saldo_nuevo))
        
        conn.commit()
        return venta_id, numero_comprobante, None
    except Exception as e:
        conn.rollback()
        return None, None, f"Error al procesar la venta: {str(e)}"
    finally:
        conn.close()


def get_ventas(limit=50, fecha_desde=None, fecha_hasta=None, cliente_id=None, tipo_comprobante=None):
    """Obtiene lista de ventas con filtros opcionales."""
    conn = get_connection()
    try:
        query = """SELECT v.id, v.cliente_id, v.tipo_comprobante, v.punto_venta, v.numero_comprobante,
                          v.subtotal, v.iva, v.total, v.metodo_pago, v.usuario_id, v.creado_en,
                          c.nombre as cliente_nombre, u.nombre as usuario_nombre
                   FROM ventas v
                   LEFT JOIN clientes c ON v.cliente_id = c.id
                   LEFT JOIN usuarios u ON v.usuario_id = u.id
                   WHERE 1=1"""
        params = []
        
        if fecha_desde:
            query += " AND date(v.creado_en) >= date(?)"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND date(v.creado_en) <= date(?)"
            params.append(fecha_hasta)
        if cliente_id:
            query += " AND v.cliente_id = ?"
            params.append(cliente_id)
        if tipo_comprobante:
            query += " AND v.tipo_comprobante = ?"
            params.append(tipo_comprobante)
        
        query += " ORDER BY v.creado_en DESC LIMIT ?"
        params.append(limit)
        
        ventas = conn.execute(query, params).fetchall()
        return ventas
    finally:
        conn.close()


def get_venta_detalle(venta_id):
    """Obtiene el detalle de una venta."""
    conn = get_connection()
    try:
        items = conn.execute("""
            SELECT vi.id, vi.producto_id, vi.cantidad, vi.precio_unitario, vi.subtotal,
                   p.nombre as producto_nombre, p.codigo_barras
            FROM venta_items vi
            JOIN productos p ON vi.producto_id = p.id
            WHERE vi.venta_id = ?
        """, (venta_id,)).fetchall()
        return items
    finally:
        conn.close()


def get_venta_completa(venta_id):
    """Obtiene venta completa con cabecera y items."""
    conn = get_connection()
    try:
        venta = conn.execute("""
            SELECT v.*, c.nombre as cliente_nombre, c.telefono as cliente_telefono,
                   c.email as cliente_email, u.nombre as usuario_nombre
            FROM ventas v
            LEFT JOIN clientes c ON v.cliente_id = c.id
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            WHERE v.id = ?
        """, (venta_id,)).fetchone()
        
        if not venta:
            return None
        
        items = get_venta_detalle(venta_id)
        return {'venta': venta, 'items': items}
    finally:
        conn.close()


# --- Funciones de Ajustes Stock ---
def crear_ajuste_stock(producto_id, stock_nuevo, motivo, usuario_id):
    """Crea un ajuste de stock con auditoría.
    Inserta el movimiento en la misma transacción (sin llamar a add_movimiento
    para no duplicar la actualización de stock ni romper la atomicidad)."""
    if not motivo or not motivo.strip():
        return False
    if producto_id is None or usuario_id is None:
        return False
    try:
        stock_nuevo = float(stock_nuevo)
    except (ValueError, TypeError):
        return False
    if stock_nuevo < 0:
        return False

    conn = get_connection()
    try:
        row = conn.execute("SELECT stock_actual FROM productos WHERE id = ?", (producto_id,)).fetchone()
        if not row:
            return False

        stock_anterior = float(row[0])
        diferencia = stock_nuevo - stock_anterior

        # Registrar ajuste (auditoría)
        conn.execute("""
            INSERT INTO ajustes_stock (producto_id, stock_anterior, stock_nuevo, diferencia, motivo, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (producto_id, stock_anterior, stock_nuevo, diferencia, motivo.strip(), usuario_id))

        # Actualizar stock del producto
        conn.execute("UPDATE productos SET stock_actual = ? WHERE id = ?", (stock_nuevo, producto_id))

        # Registrar movimiento de tipo ajuste en la misma transacción
        # (delta = diferencia: positivo si sube, negativo si baja)
        conn.execute("""
            INSERT INTO movimientos_stock (producto_id, tipo, cantidad, fecha, motivo)
            VALUES (?, 'ajuste', ?, ?, ?)
        """, (producto_id, diferencia, datetime.now(), f'Ajuste: {motivo.strip()}'))

        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def get_ajustes_stock(limit=50, fecha_desde=None, fecha_hasta=None, producto_id=None):
    """Obtiene historial de ajustes de stock."""
    conn = get_connection()
    try:
        query = """SELECT a.id, a.producto_id, a.stock_anterior, a.stock_nuevo, a.diferencia,
                          a.motivo, a.usuario_id, a.creado_en,
                          p.nombre as producto_nombre, u.nombre as usuario_nombre
                   FROM ajustes_stock a
                   JOIN productos p ON a.producto_id = p.id
                   JOIN usuarios u ON a.usuario_id = u.id
                   WHERE 1=1"""
        params = []
        
        if fecha_desde:
            query += " AND date(a.creado_en) >= date(?)"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND date(a.creado_en) <= date(?)"
            params.append(fecha_hasta)
        if producto_id:
            query += " AND a.producto_id = ?"
            params.append(producto_id)
        
        query += " ORDER BY a.creado_en DESC LIMIT ?"
        params.append(limit)
        
        ajustes = conn.execute(query, params).fetchall()
        return ajustes
    finally:
        conn.close()


# --- Funciones de Compras a Proveedores ---

def crear_compra(proveedor_id, items, observaciones=""):
    """Crea una compra a proveedor con múltiples items.
    Actualiza stock de cada producto y registra movimientos tipo 'compra'.
    items: lista de dicts [{'producto_id': int, 'cantidad': float, 'precio_unitario': float}, ...]
    Retorna el ID de la compra o None si falla."""
    if not items:
        return None
    if proveedor_id is None:
        return None

    conn = get_connection()
    try:
        # Calcular total
        total = 0.0
        for item in items:
            try:
                cantidad = float(item['cantidad'])
                precio = float(item['precio_unitario'])
            except (ValueError, TypeError):
                return None
            if cantidad <= 0 or precio < 0:
                return None
            item['cantidad'] = cantidad
            item['precio_unitario'] = precio
            item['subtotal'] = round(cantidad * precio, 2)
            total = round(total + item['subtotal'], 2)

        # Insertar cabecera de compra
        cursor = conn.execute("""
            INSERT INTO compras (proveedor_id, fecha, total, observaciones, estado)
            VALUES (?, ?, ?, ?, 'confirmada')
        """, (proveedor_id, datetime.now(), total, observaciones.strip() if observaciones else None))
        compra_id = cursor.lastrowid

        # Insertar items y actualizar stock
        now = datetime.now()
        for item in items:
            conn.execute("""
                INSERT INTO detalle_compras (compra_id, producto_id, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (compra_id, item['producto_id'], item['cantidad'], item['precio_unitario'], item['subtotal']))

            # Actualizar stock del producto
            conn.execute("""
                UPDATE productos SET stock_actual = stock_actual + ? WHERE id = ?
            """, (item['cantidad'], item['producto_id']))

            # Registrar movimiento de compra
            conn.execute("""
                INSERT INTO movimientos_stock (producto_id, tipo, cantidad, fecha, motivo)
                VALUES (?, 'compra', ?, ?, ?)
            """, (item['producto_id'], item['cantidad'], now, f'Compra a proveedor #{compra_id}'))

        conn.commit()
        return compra_id
    except Exception:
        conn.rollback()
        return None
    finally:
        conn.close()


def get_compras(limit=50):
    """Obtiene listado de compras con información del proveedor."""
    conn = get_connection()
    try:
        compras = conn.execute("""
            SELECT c.id, c.proveedor_id, p.nombre as proveedor, c.fecha, c.total,
                   c.observaciones, c.estado
            FROM compras c
            JOIN proveedores p ON c.proveedor_id = p.id
            ORDER BY c.fecha DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return compras
    finally:
        conn.close()


def get_detalle_compra(compra_id):
    """Obtiene el detalle de una compra con información del producto."""
    conn = get_connection()
    try:
        items = conn.execute("""
            SELECT d.id, d.producto_id, p.nombre as producto, p.codigo_barras,
                   d.cantidad, d.precio_unitario, d.subtotal
            FROM detalle_compras d
            JOIN productos p ON d.producto_id = p.id
            WHERE d.compra_id = ?
            ORDER BY d.id
        """, (compra_id,)).fetchall()
        return items
    finally:
        conn.close()


def anular_compra(compra_id):
    """Anula una compra revirtiendo el stock de cada producto.
    Retorna True si se anuló exitosamente, False si ya estaba anulada."""
    conn = get_connection()
    try:
        # Verificar que la compra exista y no esté anulada
        row = conn.execute("SELECT estado FROM compras WHERE id = ?", (compra_id,)).fetchone()
        if not row or row[0] == 'anulada':
            return False

        # Obtener items de la compra
        items = conn.execute("""
            SELECT producto_id, cantidad FROM detalle_compras WHERE compra_id = ?
        """, (compra_id,)).fetchall()

        if not items:
            return False

        # Revertir stock de cada producto y registrar movimiento
        now = datetime.now()
        for producto_id, cantidad in items:
            conn.execute("""
                UPDATE productos SET stock_actual = stock_actual - ? WHERE id = ?
            """, (cantidad, producto_id))

            conn.execute("""
                INSERT INTO movimientos_stock (producto_id, tipo, cantidad, fecha, motivo)
                VALUES (?, 'ajuste', ?, ?, ?)
            """, (producto_id, -cantidad, now, f'Anulación compra #{compra_id}'))

        # Marcar compra como anulada
        conn.execute("UPDATE compras SET estado = 'anulada' WHERE id = ?", (compra_id,))

        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


# --- Funciones Cuenta Corriente ---
def get_cuenta_corriente_cliente(cliente_id):
    """Obtiene el saldo actual de cuenta corriente de un cliente."""
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT COALESCE(SUM(monto), 0) FROM cuenta_corriente WHERE cliente_id = ?
        """, (cliente_id,)).fetchone()
        return float(row[0]) if row else 0.0
    finally:
        conn.close()


def get_movimientos_cuenta_corriente(cliente_id, limit=50):
    """Obtiene movimientos de cuenta corriente de un cliente."""
    conn = get_connection()
    try:
        movimientos = conn.execute("""
            SELECT cc.id, cc.venta_id, cc.monto, cc.saldo_anterior, cc.saldo_nuevo, cc.creado_en,
                   v.tipo_comprobante, v.punto_venta, v.numero_comprobante
            FROM cuenta_corriente cc
            JOIN ventas v ON cc.venta_id = v.id
            WHERE cc.cliente_id = ?
            ORDER BY cc.creado_en DESC
            LIMIT ?
        """, (cliente_id, limit)).fetchall()
        return movimientos
    finally:
        conn.close()


def get_clientes_con_deuda():
    """Obtiene clientes que tienen deuda en cuenta corriente."""
    conn = get_connection()
    try:
        clientes = conn.execute("""
            SELECT c.id, c.nombre, c.telefono, c.email,
                   COALESCE(SUM(cc.monto), 0) as deuda_total
            FROM clientes c
            JOIN cuenta_corriente cc ON c.id = cc.cliente_id
            GROUP BY c.id, c.nombre, c.telefono, c.email
            HAVING deuda_total > 0
            ORDER BY deuda_total DESC
        """).fetchall()
        return clientes
    finally:
        conn.close()


# --- Funciones de Reportes extendidas ---
def get_reporte_ventas_detallado(fecha_desde=None, fecha_hasta=None):
    """Reporte de ventas con detalle de items."""
    conn = get_connection()
    try:
        query = """SELECT v.id, v.creado_en, v.tipo_comprobante, v.punto_venta, v.numero_comprobante,
                          v.subtotal, v.iva, v.total, v.metodo_pago,
                          c.nombre as cliente_nombre,
                          vi.producto_id, p.nombre as producto_nombre, vi.cantidad, vi.precio_unitario, vi.subtotal as item_subtotal
                   FROM ventas v
                   LEFT JOIN clientes c ON v.cliente_id = c.id
                   JOIN venta_items vi ON v.id = vi.venta_id
                   JOIN productos p ON vi.producto_id = p.id
                   WHERE 1=1"""
        params = []
        if fecha_desde:
            query += " AND date(v.creado_en) >= date(?)"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND date(v.creado_en) <= date(?)"
            params.append(fecha_hasta)
        query += " ORDER BY v.creado_en DESC"
        
        return conn.execute(query, params).fetchall()
    finally:
        conn.close()