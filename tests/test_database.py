import os
import sqlite3
import tempfile
import pytest

import database


@pytest.fixture
def temp_db(monkeypatch):
    """Apunta database.DB_NAME a un archivo temporal y lo inicializa limpio."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr(database, "DB_NAME", path)
    database.init_db()
    yield path
    if os.path.exists(path):
        os.remove(path)


# --- init_db ---
def test_init_db_crea_diez_tablas(temp_db):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    tablas = {row[0] for row in cursor.fetchall()}
    conn.close()
    esperadas = {
        "categorias", "proveedores", "productos", "catalogo_proveedor",
        "clientes", "vehiculos", "servicios", "movimientos_stock",
        "ordenes_servicio", "orden_detalle",
    }
    assert esperadas.issubset(tablas), f"Faltan tablas: {esperadas - tablas}"


# --- Categorías ---
def test_add_y_get_categorias(temp_db):
    assert database.add_categoria("Aceites") is True
    assert database.add_categoria("Filtros") is True
    cats = database.get_categorias()
    assert len(cats) == 2
    nombres = [c[1] for c in cats]
    assert "Aceites" in nombres and "Filtros" in nombres


def test_add_categoria_duplicado_devuelve_false(temp_db):
    assert database.add_categoria("Aceites") is True
    # Segundo intento con mismo nombre: debe atrapar IntegrityError y devolver False
    assert database.add_categoria("Aceites") is False
    assert len(database.get_categorias()) == 1


def test_add_categoria_null(temp_db):
    # add_categoria atrapa IntegrityError internamente y devuelve False,
    # incluyendo violaciones NOT NULL (no distingue duplicado de null).
    assert database.add_categoria(None) is False
    assert len(database.get_categorias()) == 0


def test_add_categoria_string_vacio(temp_db):
    # "" es válido para NOT NULL en SQLite
    assert database.add_categoria("") is True
    assert len(database.get_categorias()) == 1


# --- Proveedores ---
def test_add_y_get_proveedores(temp_db):
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    provs = database.get_proveedores()
    assert len(provs) == 1
    assert provs[0][1] == "YPF"
    assert provs[0][4] == "Contado"


def test_add_proveedor_condicion_pago_valida(temp_db):
    for cond in [
        "Contado",
        "Cuenta Corriente (7 días)",
        "Cuenta Corriente (15 días)",
        "Cuenta Corriente (30 días)",
        "Otro",
    ]:
        database.add_proveedor("Prov", "x", "x", cond)
    assert len(database.get_proveedores()) == 5


def test_add_proveedor_condicion_pago_invalida(temp_db):
    with pytest.raises(sqlite3.IntegrityError):
        database.add_proveedor("Shell", "x", "x", "Tarjeta 90 días")
    assert len(database.get_proveedores()) == 0


def test_add_proveedor_null_condicion(temp_db):
    # condiciones_pago admite NULL (no tiene NOT NULL), debe OK
    database.add_proveedor("X", "y", "z", None)
    assert len(database.get_proveedores()) == 1


# --- Productos ---
def _crear_dependencias():
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "123", "Contado")
    cat_id = database.get_categorias()[0][0]
    prov_id = database.get_proveedores()[0][0]
    return cat_id, prov_id


def test_add_y_get_productos(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto(
        "C001", "7790001", "Aceite 5W30", "Sintético", cat_id, prov_id,
        "Entero", 5, 1000, 1500
    )
    prods = database.get_productos()
    assert len(prods) == 1
    # nombre está en índice 3
    assert prods[0][3] == "Aceite 5W30"


def test_add_producto_tipo_unidad_invalido(temp_db):
    cat_id, prov_id = _crear_dependencias()
    with pytest.raises(sqlite3.IntegrityError):
        database.add_producto(
            "C002", "7790002", "Aceite", "desc", cat_id, prov_id,
            "Litro", 1, 10, 20
        )
    assert len(database.get_productos()) == 0


def test_add_producto_codigo_duplicado(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto("C001", "7790001", "A", "d", cat_id, prov_id, "Entero", 1, 1, 2)
    with pytest.raises(sqlite3.IntegrityError):
        database.add_producto("C001", "7790009", "B", "d", cat_id, prov_id, "Entero", 1, 1, 2)


def test_add_producto_codigo_barras_duplicado(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto("C010", "7790001", "A", "d", cat_id, prov_id, "Entero", 1, 1, 2)
    with pytest.raises(sqlite3.IntegrityError):
        database.add_producto("C011", "7790001", "B", "d", cat_id, prov_id, "Entero", 1, 1, 2)


def test_add_producto_fraccionable(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto(
        "C003", "7790003", "Limpiafondos", "desc", cat_id, prov_id,
        "Fraccionable", 0.5, 100, 150
    )
    assert len(database.get_productos()) == 1


def test_add_producto_stock_precio_cero(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto(
        "C004", "7790004", "Regalo", "desc", cat_id, prov_id,
        "Entero", 0, 0, 0
    )
    prods = database.get_productos()
    assert len(prods) == 1
    # stock_minimo índice 9, precio_costo 10, precio_venta 11
    assert prods[0][9] == 0
    assert prods[0][10] == 0
    assert prods[0][11] == 0


def test_add_producto_nombre_null(temp_db):
    cat_id, prov_id = _crear_dependencias()
    with pytest.raises(sqlite3.IntegrityError):
        database.add_producto(
            "C005", "7790005", None, "desc", cat_id, prov_id,
            "Entero", 1, 1, 2
        )


def test_get_productos_excluye_inactivos(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto("C100", "7790100", "Activo", "d", cat_id, prov_id, "Entero", 1, 1, 2)
    # marcamos uno inactivo directamente
    conn = database.get_connection()
    conn.execute("UPDATE productos SET activo=0 WHERE codigo_interno='C100'")
    conn.commit()
    conn.close()
    assert len(database.get_productos()) == 0


# --- backup_db ---
def test_backup_db_crea_archivo(temp_db, monkeypatch, tmp_path):
    monkeypatch.setattr(database, "BACKUP_DIR", str(tmp_path / "backups"))
    backup_path = database.backup_db()
    assert backup_path is not None
    assert os.path.exists(backup_path)
    assert os.path.getsize(backup_path) > 0


def test_backup_db_no_existe(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DB_NAME", "/no/existe/nuna.db")
    monkeypatch.setattr(database, "BACKUP_DIR", str(tmp_path / "backups"))
    assert database.backup_db() is None


# --- Funciones de Movimientos ---

def _crear_producto_con_stock():
    """Helper para crear un producto con categoría, proveedor y stock inicial"""
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "123", "Contado")
    cat_id = database.get_categorias()[0][0]
    prov_id = database.get_proveedores()[0][0]
    database.add_producto(
        "C001", "7790001", "Aceite 5W30", "Sintético", cat_id, prov_id,
        "Entero", 10, 1000, 1500  # stock_minimo=10, pero stock_actual empieza en 0
    )
    # Establecemos un stock inicial de 20 unidades
    conn = database.get_connection()
    conn.execute("UPDATE productos SET stock_actual = 20 WHERE codigo_interno = 'C001'")
    conn.commit()
    conn.close()
    return cat_id, prov_id


def test_get_movimientos_sin_movimientos(temp_db):
    """Debe devolver una lista vacía cuando no hay movimientos"""
    movimientos = database.get_movimientos()
    assert movimientos == []


def test_get_movimientos_con_datos(temp_db):
    """Debe devolver movimientos ordenados por fecha descendente y aplicar límite"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]  # Obtener el ID del producto creado
    
    # Agregar algunos movimientos
    database.add_movimiento(producto_id, "compra", 5, "Compra inicial")
    database.add_movimiento(producto_id, "venta", 2, "Venta al cliente")
    database.add_movimiento(producto_id, "ajuste", 1, "Ajuste de inventario")
    
    # Obtener movimientos (por defecto limit=10, deberíamos obtener los 3)
    movimientos = database.get_movimientos()
    assert len(movimientos) == 3
    
    # Verificar que estén ordenados por fecha descendente (más reciente primero)
    # El último agregado debería ser el primero en la lista
    assert movimientos[0][5] == "Ajuste de inventario"  # motivo
    assert movimientos[1][5] == "Venta al cliente"
    assert movimientos[2][5] == "Compra inicial"
    
    # Probar con límite
    movimientos_limitados = database.get_movimientos(limit=2)
    assert len(movimientos_limitados) == 2
    assert movimientos_limitados[0][5] == "Ajuste de inventario"
    assert movimientos_limitados[1][5] == "Venta al cliente"


def test_add_movimiento_compra_exitosa(temp_db):
    """Debe agregar una compra exitosamente y aumentar el stock"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    # Stock inicial es 20 (establecido en helper)
    resultado = database.add_movimiento(producto_id, "compra", 10, "Compra de prueba")
    assert resultado is True
    
    # Verificar que se creó el movimiento
    movimientos = database.get_movimientos()
    assert len(movimientos) == 1
    assert movimientos[0][2] == "compra"  # tipo
    assert movimientos[0][3] == 10        # cantidad
    assert movimientos[0][5] == "Compra de prueba"  # motivo
    
    # Verificar que el stock aumentó
    producto_actualizado = database.get_productos()[0]
    # stock_actual está en el índice 8 (según la consulta en get_productos)
    assert producto_actualizado[8] == 30  # 20 inicial + 10 compra


def test_add_movimiento_venta_exitosa(temp_db):
    """Debe agregar una venta exitosamente y disminuir el stock"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    # Stock inicial es 20
    resultado = database.add_movimiento(producto_id, "venta", 5, "Venta de prueba")
    assert resultado is True
    
    # Verificar que se creó el movimiento
    movimientos = database.get_movimientos()
    assert len(movimientos) == 1
    assert movimientos[0][2] == "venta"
    assert movimientos[0][3] == 5
    assert movimientos[0][5] == "Venta de prueba"
    
    # Verificar que el stock disminuyó
    producto_actualizado = database.get_productos()[0]
    assert producto_actualizado[8] == 15  # 20 inicial - 5 venta


def test_add_movimiento_ajuste_positivo(temp_db):
    """Debe manejar un ajuste positivo correctamente"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    # Stock inicial es 20
    resultado = database.add_movimiento(producto_id, "ajuste", 5, "Ajuste positivo")
    assert resultado is True
    
    # Verificar que el stock aumentó (para ajuste, la cantidad se suma directamente)
    producto_actualizado = database.get_productos()[0]
    assert producto_actualizado[8] == 25  # 20 inicial + 5 ajuste


def test_add_movimiento_ajuste_negativo(temp_db):
    """Debe manejar un ajuste negativo correctamente"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    # Stock inicial es 20
    resultado = database.add_movimiento(producto_id, "ajuste", -5, "Ajuste negativo")
    assert resultado is True
    
    # Verificar que el stock disminuyó
    producto_actualizado = database.get_productos()[0]
    assert producto_actualizado[8] == 15  # 20 inicial + (-5) ajuste


def test_add_movimiento_devolucion(temp_db):
    """Debe manejar una devolución como entrada de stock"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    # Stock inicial es 20
    resultado = database.add_movimiento(producto_id, "devolucion", 3, "Devolución de cliente")
    assert resultado is True
    
    # Verificar que el stock aumentó (igual que compra)
    producto_actualizado = database.get_productos()[0]
    assert producto_actualizado[8] == 23  # 20 inicial + 3 devolucion


def test_add_movimiento_uso_interno(temp_db):
    """Debe manejar el uso interno como salida de stock"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    # Stock inicial es 20
    resultado = database.add_movimiento(producto_id, "uso_interno", 4, "Uso en taller")
    assert resultado is True
    
    # Verificar que el stock disminuyó (igual que venta)
    producto_actualizado = database.get_productos()[0]
    assert producto_actualizado[8] == 16  # 20 inicial - 4 uso_interno


def test_add_movimiento_stock_insuficiente(temp_db):
    """Debe fallar cuando no hay suficiente stock para una salida"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    # Stock inicial es 20, intentar retirar 25
    resultado = database.add_movimiento(producto_id, "venta", 25, "Intento de venta excesiva")
    assert resultado is False
    
    # Verificar que no se creó ningún movimiento
    movimientos = database.get_movimientos()
    assert len(movimientos) == 0
    
    # Verificar que el stock no cambió
    producto_actualizado = database.get_productos()[0]
    assert producto_actualizado[8] == 20  # Stock unchanged


def test_add_movimiento_producto_inexistente(temp_db):
    """Debe fallar cuando el producto_id no existe"""
    resultado = database.add_movimiento(99999, "compra", 5, "Producto inexistente")
    assert resultado is False


def test_add_movimiento_tipo_invalido(temp_db):
    """Debe fallar cuando el tipo de movimiento no es válido"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    resultado = database.add_movimiento(producto_id, "tipo_invalido", 5, "Tipo inválido")
    assert resultado is False


def test_add_movimiento_cantidad_invalida(temp_db):
    """Debe fallar cuando la cantidad no es válida"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    # Cantidad que no se puede convertir a float
    resultado = database.add_movimiento(producto_id, "compra", "abc", "Cantidad inválida")
    assert resultado is False
    
    # Cantidad None
    resultado = database.add_movimiento(producto_id, "compra", None, "Cantidad None")
    assert resultado is False


def test_add_movimiento_producto_id_nulo(temp_db):
    """Debe fallar cuando producto_id es None"""
    resultado = database.add_movimiento(None, "compra", 5, "Producto ID nulo")
    assert resultado is False


def test_add_movimiento_tipo_nulo(temp_db):
    """Debe fallar cuando tipo es None"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    resultado = database.add_movimiento(producto_id, None, 5, "Tipo nulo")
    assert resultado is False


def test_add_movimiento_cantidad_nula(temp_db):
    """Debe fallar cuando cantidad es None"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    resultado = database.add_movimiento(producto_id, "compra", None, "Cantidad nula")
    assert resultado is False


def test_add_movimiento_fecha_personalizada(temp_db):
    """Debe aceptar una fecha personalizada"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    from datetime import datetime
    fecha_personalizada = datetime(2023, 1, 1, 12, 0, 0)
    
    resultado = database.add_movimiento(producto_id, "compra", 5, "Compra con fecha", fecha_personalizada)
    assert resultado is True
    
    # Verificar que se creó el movimiento
    movimientos = database.get_movimientos()
    assert len(movimientos) == 1
    # La fecha debería ser la que proporcionamos (aunque el formato en la BD pueda variar)
    # Solo verificamos que se creó un movimiento
    assert movimientos[0][2] == "compra"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
