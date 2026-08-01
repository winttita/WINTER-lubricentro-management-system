"""Test that the legacy DB migration (removing codigo_interno) works correctly."""
import sqlite3
import tempfile
import os
import pytest


def test_migration_legacy_db_removes_codigo_interno():
    """
    Test that init_db() correctly migrates a DB with the old schema
    (codigo_interno UNIQUE column) to the new schema without that column,
    preserving all data.
    """
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name

    try:
        # Create old schema with codigo_interno UNIQUE (v0.4.3 style)
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE proveedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                contacto TEXT,
                telefono TEXT,
                condiciones_pago TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_barras TEXT UNIQUE,
                codigo_interno TEXT UNIQUE,
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

        # Insert test data
        cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", ('Lubricantes',))
        cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", ('Filtros',))
        cursor.execute("INSERT INTO proveedores (nombre, contacto, telefono) VALUES (?, ?, ?)",
                       ('YPF', 'Juan', '123456789'))
        cursor.execute("INSERT INTO proveedores (nombre, contacto, telefono) VALUES (?, ?, ?)",
                       ('Mann', 'Pedro', '987654321'))

        cursor.execute("""
            INSERT INTO productos (codigo_barras, codigo_interno, nombre, descripcion, categoria_id, proveedor_id,
                                   tipo_unidad, stock_actual, stock_minimo, precio_costo, precio_venta, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('7791234567890', 'INT-001', 'Aceite 5W30 1L', 'Aceite sintético', 1, 1,
              'Entero', 10.0, 2.0, 1500.0, 2500.0, 1))

        cursor.execute("""
            INSERT INTO productos (codigo_barras, codigo_interno, nombre, descripcion, categoria_id, proveedor_id,
                                   tipo_unidad, stock_actual, stock_minimo, precio_costo, precio_venta, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('7791234567891', 'INT-002', 'Filtro de aceite', 'Filtro para motor', 2, 2,
              'Entero', 5.0, 1.0, 800.0, 1500.0, 1))

        cursor.execute("""
            INSERT INTO productos (codigo_barras, codigo_interno, nombre, descripcion, categoria_id, proveedor_id,
                                   tipo_unidad, stock_actual, stock_minimo, precio_costo, precio_venta, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('7791234567892', 'INT-003', 'Grasa lithium', 'Grasa multipropósito', 1, 1,
              'Fraccionable', 20.0, 5.0, 500.0, 900.0, 1))

        conn.commit()

        # Verify old schema has codigo_interno
        cursor.execute("PRAGMA table_info(productos)")
        old_columns = [row[1] for row in cursor.fetchall()]
        assert 'codigo_interno' in old_columns, "Old schema should have codigo_interno column"

        # Store original data for comparison
        cursor.execute("""
            SELECT id, codigo_barras, nombre, descripcion, categoria_id, proveedor_id,
                   tipo_unidad, stock_actual, stock_minimo, precio_costo, precio_venta, activo
            FROM productos ORDER BY id
        """)
        original_data = cursor.fetchall()
        assert len(original_data) == 3

        conn.close()

        # Now run the migration via init_db()
        import database as db
        original_db_name = db.DB_NAME
        db.DB_NAME = test_db
        try:
            db.init_db()

            # Verify get_productos() returns correct structure (14 columns with joins)
            from database import get_productos
            productos = get_productos()
            assert len(productos) == 3, f"Expected 3 products, got {len(productos)}"
            for p in productos:
                # Should have 14 columns: 12 from productos + categoria_nombre + proveedor_nombre
                assert len(p) == 14, f"get_productos should return 14 columns, got {len(p)}"
        finally:
            db.DB_NAME = original_db_name

        # Verify new schema
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(productos)")
        new_columns = [row[1] for row in cursor.fetchall()]
        assert 'codigo_interno' not in new_columns, "codigo_interno should be removed after migration"

        # Verify expected columns exist (11 columns without codigo_interno)
        expected_columns = [
            'id', 'codigo_barras', 'nombre', 'descripcion', 'categoria_id',
            'proveedor_id', 'tipo_unidad', 'stock_actual', 'stock_minimo',
            'precio_costo', 'precio_venta', 'activo'
        ]
        for col in expected_columns:
            assert col in new_columns, f"Expected column {col} missing after migration"

        # Verify data is preserved
        cursor.execute("""
            SELECT id, codigo_barras, nombre, descripcion, categoria_id, proveedor_id,
                   tipo_unidad, stock_actual, stock_minimo, precio_costo, precio_venta, activo
            FROM productos ORDER BY id
        """)
        migrated_data = cursor.fetchall()

        assert len(migrated_data) == 3, "Should have 3 products after migration"

        # Compare each field (excluding codigo_interno which is gone)
        for orig, migr in zip(original_data, migrated_data):
            assert orig == migr, f"Data mismatch: original={orig}, migrated={migr}"

        conn.close()

    finally:
        os.unlink(test_db)


def test_migration_idempotent():
    """Test that running init_db twice on the same DB doesn't cause errors."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name

    try:
        import database as db
        original_db_name = db.DB_NAME
        db.DB_NAME = test_db

        # Run init_db twice
        db.init_db()
        db.init_db()  # Should not raise

        # Verify schema is correct
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(productos)")
        columns = [row[1] for row in cursor.fetchall()]
        assert 'codigo_interno' not in columns
        assert len(columns) == 12  # id + 11 data columns
        conn.close()

        db.DB_NAME = original_db_name

    finally:
        os.unlink(test_db)