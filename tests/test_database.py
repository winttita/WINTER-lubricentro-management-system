import os
import sqlite3
import tempfile
import hashlib
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
def test_init_db_crea_tablas(temp_db):
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
        "ordenes_servicio", "orden_detalle", "usuarios", "ajustes_stock",
        "ventas", "venta_items", "cuenta_corriente", "compras", "detalle_compras",
        "caja", "movimientos_caja",
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
    assert database.add_categoria("") is False
    assert database.add_categoria("   ") is False
    assert len(database.get_categorias()) == 0


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
        "7790001", "Aceite 5W30", "Sintético", cat_id, prov_id,
        "Entero", 5, 1000, 1500
    )
    prods = database.get_productos()
    assert len(prods) == 1
    # nombre está en índice 2
    assert prods[0][2] == "Aceite 5W30"


def test_add_producto_tipo_unidad_invalido(temp_db):
    cat_id, prov_id = _crear_dependencias()
    with pytest.raises(sqlite3.IntegrityError):
        database.add_producto(
            "7790002", "Aceite", "desc", cat_id, prov_id,
            "Litro", 1, 10, 20
        )
    assert len(database.get_productos()) == 0


def test_add_producto_codigo_barras_duplicado(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto("7790001", "A", "d", cat_id, prov_id, "Entero", 1, 1, 2)
    with pytest.raises(sqlite3.IntegrityError):
        database.add_producto("7790001", "B", "d", cat_id, prov_id, "Entero", 1, 1, 2)


def test_add_producto_fraccionable(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto(
        "7790003", "Limpiafondos", "desc", cat_id, prov_id,
        "Fraccionable", 0.5, 100, 150
    )
    assert len(database.get_productos()) == 1


def test_add_producto_stock_precio_cero(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto(
        "7790004", "Regalo", "desc", cat_id, prov_id,
        "Entero", 0, 0, 0
    )
    prods = database.get_productos()
    assert len(prods) == 1
    # stock_minimo índice 8, precio_costo 9, precio_venta 10
    assert prods[0][8] == 0
    assert prods[0][9] == 0
    assert prods[0][10] == 0


def test_add_producto_nombre_null(temp_db):
    cat_id, prov_id = _crear_dependencias()
    assert database.add_producto(
        "7790005", None, "desc", cat_id, prov_id,
        "Entero", 1, 1, 2
    ) is False


def test_get_productos_excluye_inactivos(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto("7790100", "Activo", "d", cat_id, prov_id, "Entero", 1, 1, 2)
    # marcamos uno inactivo directamente
    conn = database.get_connection()
    conn.execute("UPDATE productos SET activo=0 WHERE id=1")
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
        "7790001", "Aceite 5W30", "Sintético", cat_id, prov_id,
        "Entero", 10, 1000, 1500
    )
    conn = database.get_connection()
    conn.execute("UPDATE productos SET stock_actual = 20 WHERE id = 1")
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
    assert producto_actualizado[7] == 30  # 20 inicial + 10 compra


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
    assert producto_actualizado[7] == 15  # 20 inicial - 5 venta


def test_add_movimiento_ajuste_positivo(temp_db):
    """Debe manejar un ajuste positivo correctamente"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    # Stock inicial es 20
    resultado = database.add_movimiento(producto_id, "ajuste", 5, "Ajuste positivo")
    assert resultado is True
    
    # Verificar que el stock aumentó (para ajuste, la cantidad se suma directamente)
    producto_actualizado = database.get_productos()[0]
    assert producto_actualizado[7] == 25  # 20 inicial + 5 ajuste


def test_add_movimiento_ajuste_negativo(temp_db):
    """Debe manejar un ajuste negativo correctamente"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    # Stock inicial es 20
    resultado = database.add_movimiento(producto_id, "ajuste", -5, "Ajuste negativo")
    assert resultado is True
    
    # Verificar que el stock disminuyó
    producto_actualizado = database.get_productos()[0]
    assert producto_actualizado[7] == 15  # 20 inicial + (-5) ajuste


def test_add_movimiento_devolucion(temp_db):
    """Debe manejar una devolución como entrada de stock"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    # Stock inicial es 20
    resultado = database.add_movimiento(producto_id, "devolucion", 3, "Devolución de cliente")
    assert resultado is True
    
    # Verificar que el stock aumentó (igual que compra)
    producto_actualizado = database.get_productos()[0]
    assert producto_actualizado[7] == 23  # 20 inicial + 3 devolucion


def test_add_movimiento_uso_interno(temp_db):
    """Debe manejar el uso interno como salida de stock"""
    cat_id, prov_id = _crear_producto_con_stock()
    producto_id = database.get_productos()[0][0]
    
    # Stock inicial es 20
    resultado = database.add_movimiento(producto_id, "uso_interno", 4, "Uso en taller")
    assert resultado is True
    
    # Verificar que el stock disminuyó (igual que venta)
    producto_actualizado = database.get_productos()[0]
    assert producto_actualizado[7] == 16  # 20 inicial - 4 uso_interno


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
    assert producto_actualizado[7] == 20  # Stock unchanged


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


# --- Pruebas de add_producto con stock inicial ---

def test_add_producto_con_stock_inicial(temp_db):
    """Debe crear producto con stock inicial y registrar movimiento."""
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "", "", "Contado")
    cat_id = database.get_categorias()[0][0]
    prov_id = database.get_proveedores()[0][0]

    database.add_producto("7790100", "Test Stock", "", cat_id, prov_id,
                          "Entero", 5, 100, 200, stock_inicial=25)

    productos = database.get_productos()
    p = productos[0]
    assert p[7] == 25.0, f"Stock esperado 25, obtenido {p[7]}"

    conn = database.get_connection()
    movs = conn.execute("SELECT tipo, cantidad, motivo FROM movimientos_stock").fetchall()
    conn.close()
    assert len(movs) == 1
    assert movs[0][0] == "compra"
    assert movs[0][1] == 25.0


def test_add_producto_sin_stock_inicial(temp_db):
    """Debe crear producto con stock 0 por defecto y sin movimiento."""
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "", "", "Contado")
    cat_id = database.get_categorias()[0][0]
    prov_id = database.get_proveedores()[0][0]

    database.add_producto("7790101", "Test Sin Stock", "", cat_id, prov_id,
                          "Entero", 5, 100, 200)

    p = database.get_productos()[0]
    assert p[7] == 0.0

    conn = database.get_connection()
    movs = conn.execute("SELECT tipo, cantidad FROM movimientos_stock").fetchall()
    conn.close()
    assert len(movs) == 0


# --- Pruebas de crear_ajuste_stock ---

def test_crear_ajuste_stock_con_movimiento(temp_db):
    """Debe crear ajuste y registrar movimiento en la misma transacción."""
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "", "", "Contado")
    cat_id = database.get_categorias()[0][0]
    prov_id = database.get_proveedores()[0][0]
    database.add_producto("7790200", "Ajustable", "", cat_id, prov_id,
                          "Entero", 5, 100, 200, stock_inicial=50)

    p = database.get_productos()[0]
    ok = database.crear_ajuste_stock(p[0], 30, "reducción por merma", 1)
    assert ok is True

    conn = database.get_connection()
    p_actualizado = conn.execute("SELECT stock_actual FROM productos WHERE id = ?", (p[0],)).fetchone()
    conn.close()
    assert p_actualizado[0] == 30.0

    conn = database.get_connection()
    movs = conn.execute(
        "SELECT tipo, cantidad, motivo FROM movimientos_stock WHERE producto_id = ? AND tipo='ajuste'",
        (p[0],)
    ).fetchall()
    conn.close()
    assert len(movs) == 1
    assert movs[0][1] == -20.0  # 30 - 50 = -20


# --- Pruebas de Compras a Proveedores ---

def test_crear_y_get_compras(temp_db):
    """Debe crear una compra, actualizar stock y registrar movimientos."""
    database.add_categoria("Filtros")
    database.add_proveedor("Mann Filter", "", "", "Contado")
    cat_id = database.get_categorias()[0][0]
    prov_id = database.get_proveedores()[0][0]
    database.add_producto("7790300", "Filtro Aceite", "", cat_id, prov_id,
                          "Entero", 10, 500, 800, stock_inicial=20)
    database.add_producto("7790301", "Filtro Aire", "", cat_id, prov_id,
                          "Entero", 10, 300, 500, stock_inicial=10)

    productos = database.get_productos()
    filtro_aceite = [p for p in productos if p[2] == "Filtro Aceite"][0]
    filtro_aire = [p for p in productos if p[2] == "Filtro Aire"][0]

    items = [
        {'producto_id': filtro_aceite[0], 'cantidad': 10, 'precio_unitario': 450},
        {'producto_id': filtro_aire[0], 'cantidad': 5, 'precio_unitario': 280},
    ]

    compra_id = database.crear_compra(prov_id, items, "Compra mensual")
    assert compra_id is not None

    # Verificar stock actualizado
    conn = database.get_connection()
    stock_aceite = conn.execute("SELECT stock_actual FROM productos WHERE id = ?", (filtro_aceite[0],)).fetchone()[0]
    stock_aire = conn.execute("SELECT stock_actual FROM productos WHERE id = ?", (filtro_aire[0],)).fetchone()[0]
    assert stock_aceite == 30.0  # 20 + 10
    assert stock_aire == 15.0    # 10 + 5

    # Verificar movimientos de compra
    movs = conn.execute(
        "SELECT tipo, cantidad FROM movimientos_stock WHERE tipo='compra' AND motivo LIKE ?",
        (f'%#{compra_id}',)
    ).fetchall()
    assert len(movs) == 2

    # Verificar get_compras
    conn.close()
    compras = database.get_compras()
    assert len(compras) == 1
    assert compras[0][2] == "Mann Filter"
    # total ahora incluye IVA (21%): neto * 1.21
    neto = 10*450 + 5*280
    total_con_iva = round(neto * 1.21, 2)
    assert abs(compras[0][4] - total_con_iva) < 0.01, f"Total debería ser {total_con_iva}, es {compras[0][4]}"
    # Verificar que IVA se registró
    conn = database.get_connection()
    row = conn.execute("SELECT total, iva FROM compras WHERE id = ?", (compra_id,)).fetchone()
    conn.close()
    assert row[1] > 0, "IVA debe ser > 0"
    assert abs(row[1] - round(neto * 0.21, 2)) < 0.01

    # Verificar get_detalle_compra
    detalle = database.get_detalle_compra(compra_id)
    assert len(detalle) == 2


def test_anular_compra(temp_db):
    """Debe anular compra y revertir stock."""
    database.add_categoria("Filtros")
    database.add_proveedor("Mann Filter", "", "", "Contado")
    cat_id = database.get_categorias()[0][0]
    prov_id = database.get_proveedores()[0][0]
    database.add_producto("7790400", "Filtro Test", "", cat_id, prov_id,
                          "Entero", 5, 100, 200, stock_inicial=10)

    p = database.get_productos()[0]
    items = [{'producto_id': p[0], 'cantidad': 20, 'precio_unitario': 90}]
    compra_id = database.crear_compra(prov_id, items, "Compra test")
    assert compra_id is not None

    # Verificar stock post-compra
    conn = database.get_connection()
    stock = conn.execute("SELECT stock_actual FROM productos WHERE id = ?", (p[0],)).fetchone()[0]
    assert stock == 30.0  # 10 + 20

    # Anular compra
    ok = database.anular_compra(compra_id)
    assert ok is True

    # Verificar stock revertido
    stock = conn.execute("SELECT stock_actual FROM productos WHERE id = ?", (p[0],)).fetchone()[0]
    assert stock == 10.0  # 30 - 20

    # Verificar que no se pueda anular dos veces
    ok = database.anular_compra(compra_id)
    assert ok is False

    # Verificar estado de la compra
    estado = conn.execute("SELECT estado FROM compras WHERE id = ?", (compra_id,)).fetchone()[0]
    assert estado == "anulada"
    conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# --- Tests nuevos para crear_venta v0.2.5 (firma extendida y correcciones) ---

def _crear_dependencias():
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "123", "Contado")
    cat_id = database.get_categorias()[0][0]
    prov_id = database.get_proveedores()[0][0]
    return cat_id, prov_id


def test_crear_venta_stock_insuficiente_retorna_mensaje_especifico(temp_db):
    """Stock insuficiente debe retornar mensaje especifico, no (None, None)."""
    from database import crear_venta, add_producto
    cat_id, prov_id = _crear_dependencias()
    # Setup: crear producto con stock 5
    add_producto("CB001", "Producto Test", "", cat_id, prov_id, "Entero", 0, 10.0, 100.0, 5)
    items = [{"producto_id": 1, "cantidad": 10, "precio_unitario": 100.0}]
    venta_id, numero, error = crear_venta(None, "ticket", items, "efectivo", 1)
    assert venta_id is None
    assert error is not None
    assert "Stock insuficiente" in error
    assert "disponible 5" in error
    assert "solicitado 10" in error


def test_crear_venta_factura_a_calculo_iva_incluido(temp_db):
    """Factura A: precio_venta ya incluye IVA. Total = subtotal_neto + iva = precio_final."""
    from database import crear_venta, add_producto
    cat_id, prov_id = _crear_dependencias()
    add_producto("CB002", "Producto A", "", cat_id, prov_id, "Entero", 0, 10.0, 121.0, 10)
    items = [{"producto_id": 1, "cantidad": 1, "precio_unitario": 121.0}]
    venta_id, numero, error = crear_venta(None, "factura_a", items, "efectivo", 1)
    print(f"DEBUG: venta_id={venta_id}, numero={numero}, error={error}")
    assert venta_id is not None
    assert error is None
    # Verificar en BD
    import database as db
    conn = db.get_connection()
    row = conn.execute("SELECT subtotal, iva, total FROM ventas WHERE id = ?", (venta_id,)).fetchone()
    conn.close()
    assert row[2] == 121.0  # total = precio final
    assert row[1] == 21.0   # iva = 121 - (121/1.21)
    assert row[0] == 100.0  # subtotal = 121/1.21


def test_crear_venta_ticket_sin_iva(temp_db):
    """Ticket: sin IVA, subtotal = total = precio_venta."""
    from database import crear_venta, add_producto
    cat_id, prov_id = _crear_dependencias()
    add_producto("CB003", "Producto B", "", cat_id, prov_id, "Entero", 0, 10.0, 100.0, 10)
    items = [{"producto_id": 1, "cantidad": 2, "precio_unitario": 100.0}]
    venta_id, numero, error = crear_venta(None, "ticket", items, "efectivo", 1)
    assert venta_id is not None
    assert error is None
    import database as db
    conn = db.get_connection()
    row = conn.execute("SELECT subtotal, iva, total FROM ventas WHERE id = ?", (venta_id,)).fetchone()
    conn.close()
    assert row[2] == 200.0  # total
    assert row[1] == 0.0    # iva
    assert row[0] == 200.0  # subtotal


def test_crear_venta_producto_inactivo_retorna_error(temp_db):
    """Producto inactivo debe retornar error especifico."""
    from database import crear_venta, add_producto
    cat_id, prov_id = _crear_dependencias()
    add_producto("CB004", "Producto Inactivo", "", cat_id, prov_id, "Entero", 0, 10.0, 100.0, 10)
    # Desactivar producto
    import database as db
    conn = db.get_connection()
    conn.execute("UPDATE productos SET activo = 0 WHERE id = 1")
    conn.commit()
    conn.close()
    items = [{"producto_id": 1, "cantidad": 1, "precio_unitario": 100.0}]
    venta_id, numero, error = crear_venta(None, "ticket", items, "efectivo", 1)
    assert venta_id is None
    assert error is not None
    assert "inactivo o inexistente" in error


def test_crear_venta_items_vacios_retorna_error(temp_db):
    """Items vacios debe retornar error especifico."""
    from database import crear_venta
    venta_id, numero, error = crear_venta(None, "ticket", [], "efectivo", 1)
    assert venta_id is None
    assert error == "No hay items en la venta"


def test_crear_venta_factura_b_sin_iva(temp_db):
    """Factura B: sin IVA desglosado."""
    from database import crear_venta, add_producto
    cat_id, prov_id = _crear_dependencias()
    add_producto("CB005", "Producto B", "", cat_id, prov_id, "Entero", 0, 10.0, 150.0, 10)
    items = [{"producto_id": 1, "cantidad": 1, "precio_unitario": 150.0}]
    venta_id, numero, error = crear_venta(None, "factura_b", items, "efectivo", 1)
    assert venta_id is not None
    assert error is None
    import database as db
    conn = db.get_connection()
    row = conn.execute("SELECT subtotal, iva, total FROM ventas WHERE id = ?", (venta_id,)).fetchone()
    conn.close()
    assert row[2] == 150.0
    assert row[1] == 0.0
    assert row[0] == 150.0


def test_crear_venta_factura_c_sin_iva(temp_db):
    """Factura C: sin IVA desglosado."""
    from database import crear_venta, add_producto
    cat_id, prov_id = _crear_dependencias()
    add_producto("CB006", "Producto C", "", cat_id, prov_id, "Entero", 0, 10.0, 200.0, 10)
    items = [{"producto_id": 1, "cantidad": 1, "precio_unitario": 200.0}]
    venta_id, numero, error = crear_venta(None, "factura_c", items, "efectivo", 1)
    assert venta_id is not None
    assert error is None
    import database as db
    conn = db.get_connection()
    row = conn.execute("SELECT subtotal, iva, total FROM ventas WHERE id = ?", (venta_id,)).fetchone()
    conn.close()
    assert row[2] == 200.0
    assert row[1] == 0.0
    assert row[0] == 200.0


# --- Tests de seguridad y validación (auditoría) ---


def test_init_db_admin_no_password_vacio(temp_db):
    """El usuario admin por defecto no debe tener password_hash vacío."""
    conn = database.get_connection()
    row = conn.execute(
        "SELECT password_hash FROM usuarios WHERE username = 'admin'"
    ).fetchone()
    conn.close()
    assert row is not None, "Debe existir un usuario admin por defecto"
    assert row[0] != "", "El password_hash del admin no debe estar vacío"
    assert row[0] is not None, "El password_hash del admin no debe ser None"


def test_crear_venta_rechaza_cantidad_negativa(temp_db):
    """crear_venta debe rechazar cantidades negativas o cero."""
    from database import crear_venta, add_producto
    cat_id, prov_id = _crear_producto_con_stock()
    items = [{"producto_id": 1, "cantidad": -5, "precio_unitario": 100.0}]
    venta_id, numero, error = crear_venta(None, "factura_c", items, "efectivo", 1)
    assert venta_id is None
    assert error is not None
    assert "cantidad" in error.lower() or "inválido" in error.lower() or "invalid" in error.lower()


def test_crear_venta_rechaza_precio_negativo(temp_db):
    """crear_venta debe rechazar precios negativos."""
    from database import crear_venta
    cat_id, prov_id = _crear_producto_con_stock()
    items = [{"producto_id": 1, "cantidad": 1, "precio_unitario": -50.0}]
    venta_id, numero, error = crear_venta(None, "factura_c", items, "efectivo", 1)
    assert venta_id is None
    assert error is not None


def test_crear_venta_rechaza_tipo_comprobante_invalido(temp_db):
    """crear_venta debe rechazar tipos de comprobante no válidos."""
    from database import crear_venta
    cat_id, prov_id = _crear_producto_con_stock()
    items = [{"producto_id": 1, "cantidad": 1, "precio_unitario": 100.0}]
    venta_id, numero, error = crear_venta(None, "Factura_A", items, "efectivo", 1)
    assert venta_id is None
    assert error is not None


def test_crear_venta_cuenta_corriente_sin_cliente_rechaza(temp_db):
    """Venta con cuenta corriente pero sin cliente_id debe rechazarse."""
    from database import crear_venta
    cat_id, prov_id = _crear_producto_con_stock()
    items = [{"producto_id": 1, "cantidad": 1, "precio_unitario": 100.0}]
    venta_id, numero, error = crear_venta(None, "factura_c", items, "cuenta_corriente", 1)
    assert venta_id is None
    assert error is not None
    assert "cliente" in error.lower()


def test_crear_compra_actualiza_precio_costo(temp_db):
    """crear_compra debe actualizar productos.precio_costo con el precio de compra."""
    from database import crear_compra, get_productos
    cat_id, prov_id = _crear_producto_con_stock()
    # Precio_costo inicial = 10.0 (de _crear_producto_con_stock)
    items = [{"producto_id": 1, "cantidad": 5, "precio_unitario": 1200.0}]
    compra_id = crear_compra(prov_id, items)
    assert compra_id is not None
    prods = get_productos()
    prod = next((p for p in prods if p[0] == 1), None)
    assert prod is not None
    # precio_costo está en índice 9 (p.*: id, codigo_barras, nombre, descripcion, 
    # categoria_id, proveedor_id, tipo_unidad, stock_actual, stock_minimo, precio_costo, precio_venta, ...)
    assert prod[9] == 1200.0, f"precio_costo debería ser 1200.0, es {prod[9]}"


def test_crear_compra_registra_iva(temp_db):
    """crear_compra debe registrar IVA de la compra."""
    from database import crear_compra
    cat_id, prov_id = _crear_producto_con_stock()
    items = [{"producto_id": 1, "cantidad": 5, "precio_unitario": 1210.0}]
    compra_id = crear_compra(prov_id, items)
    conn = database.get_connection()
    row = conn.execute("SELECT total, iva FROM compras WHERE id = ?", (compra_id,)).fetchone()
    conn.close()
    assert row is not None
    # total debería incluir IVA: 5*1210 = 6050, con IVA 21% = 6050*1.21 = 7320.5
    # O alternativamente, total = subtotal + iva
    assert row[1] > 0, "La compra debe registrar IVA > 0"


def test_get_reporte_ingresos_egresos_no_cuenta_stock_inicial(temp_db):
    """El reporte de egresos no debe contar 'Stock inicial' como egreso real."""
    from database import get_reporte_ingresos_egresos
    cat_id, prov_id = _crear_producto_con_stock()
    # _crear_producto_con_stock inserta un movimiento 'compra' con motivo 'Stock inicial'
    ingresos, egresos = get_reporte_ingresos_egresos()
    # No debe haber egresos porque el stock inicial no es una compra real
    total_egresos = sum(e[2] for e in egresos) if egresos else 0
    assert total_egresos == 0, f"Egresos deberían ser 0, son {total_egresos} (stock inicial contado como egreso)"


def test_anular_compra_evita_stock_negativo(temp_db):
    """anular_compra debe rechazar si el stock resultante sería negativo."""
    from database import crear_compra, anular_compra, add_movimiento
    cat_id, prov_id = _crear_producto_con_stock()
    # Compra 10 unidades
    items = [{"producto_id": 1, "cantidad": 10, "precio_unitario": 1000.0}]
    compra_id = crear_compra(prov_id, items)
    assert compra_id is not None
    # Vender 25 (más de lo que hay: 20 iniciales + 10 comprados = 30, vender 25 deja 5)
    add_movimiento(1, 'venta', 25, 'Venta test')
    # Ahora stock = 5. Anular compra de 10 -> stock = 5 - 10 = -5 (debe rechazarse)
    resultado = anular_compra(compra_id)
    assert resultado is False, "Anular compra con stock insuficiente debe retornar False"


def test_anular_compra_registra_devolucion_no_ajuste(temp_db):
    """anular_compra debe registrar el movimiento como 'devolucion', no 'ajuste'."""
    from database import crear_compra, anular_compra
    cat_id, prov_id = _crear_producto_con_stock()
    items = [{"producto_id": 1, "cantidad": 5, "precio_unitario": 1000.0}]
    compra_id = crear_compra(prov_id, items)
    anular_compra(compra_id)
    conn = database.get_connection()
    row = conn.execute(
        "SELECT tipo FROM movimientos_stock WHERE motivo LIKE ? ORDER BY id DESC LIMIT 1",
        (f"Anulación compra #{compra_id}%",)
    ).fetchone()
    conn.close()
    assert row is not None, "Debe existir un movimiento de anulación"
    assert row[0] == 'devolucion', f"Tipo debería ser 'devolucion', es '{row[0]}'"


def test_get_connection_tiene_busy_timeout(temp_db):
    """get_connection debe configurar busy_timeout para evitar 'database is locked'."""
    conn = database.get_connection()
    row = conn.execute("PRAGMA busy_timeout").fetchone()
    conn.close()
    assert row[0] > 0, f"busy_timeout debería ser > 0, es {row[0]}"


# --- Autenticación (Login) ---

def test_hash_password_con_salt_aleatorio(temp_db):
    """hash_password usa scrypt con salt aleatorio: no determinista y verificable."""
    h1 = database.hash_password("winter1234")
    h2 = database.hash_password("winter1234")
    assert h1 != h2  # salt aleatorio: mismo password, hashes distintos
    assert h1.startswith("scrypt$16384$8$1$")
    assert h1 != "winter1234"  # no debe ser texto plano
    assert database._verify_password("winter1234", h1)
    assert not database._verify_password("clave_incorrecta", h1)


def test_verify_password_soporta_hash_legacy_sha256(temp_db):
    """_verify_password debe validar hashes SHA-256 legacy (sin salt)."""
    legacy = hashlib.sha256(b"winter1234").hexdigest()
    assert database._verify_password("winter1234", legacy)
    assert not database._verify_password("otra", legacy)


def test_hash_password_diferente_para_distintas_entradas(temp_db):
    """hash_password deve devolver hashes distintos para passwords distintas."""
    h1 = database.hash_password("winter1234")
    h2 = database.hash_password("otra_clave")
    assert h1 != h2


def test_init_db_crea_usuario_admin_por_defecto(temp_db):
    """init_db debe crear el usuario 'admin' si no existe ninguno."""
    conn = database.get_connection()
    row = conn.execute("SELECT username, password_hash, rol FROM usuarios WHERE username = 'admin'").fetchone()
    conn.close()
    assert row is not None, "Debe existir el usuario admin por defecto"
    assert row[0] == "admin"
    assert row[1] != "FORCE_CHANGE", "El password_hash debe ser un hash real, no FORCE_CHANGE"
    assert row[2] == "admin"


def test_verificar_login_admin_correcto(temp_db):
    """verificar_login debe devolver info del usuario admin cuando las credenciales son correctas."""
    result = database.verificar_login("admin", "winter1234")
    assert result is not None, "Login admin/winter1234 debe ser exitoso"
    assert result["user_id"] == 1
    assert result["nombre"] == "Administrador"
    assert result["rol"] == "admin"


def test_verificar_login_password_incorrecta(temp_db):
    """verificar_login deve devolver None cuando la contraseña es incorrecta."""
    result = database.verificar_login("admin", "clave_errada")
    assert result is None, "Login con clave incorrecta debe fallar"


def test_verificar_login_usuario_inexistente(temp_db):
    """verificar_login deve devolver None cuando el usuario no existe."""
    result = database.verificar_login("no_existe", "winter1234")
    assert result is None, "Login con usuario inexistente debe fallar"


def test_verificar_login_usuario_inactivo(temp_db):
    """verificar_login deve devolver None cuando el usuario está inactivo."""
    conn = database.get_connection()
    conn.execute("UPDATE usuarios SET activo = 0 WHERE username = 'admin'")
    conn.commit()
    conn.close()
    result = database.verificar_login("admin", "winter1234")
    assert result is None, "Login de usuario inactivo debe fallar"


def test_cambiar_password_actualiza_hash(temp_db):
    """cambiar_password debe actualizar el password_hash en la BD."""
    user = database.verificar_login("admin", "winter1234")
    assert database.cambiar_password(user["user_id"], "nueva_clave_456") is True
    # Login con clave vieja debe fallar
    assert database.verificar_login("admin", "winter1234") is None
    # Login con clave nueva debe funcionar
    result = database.verificar_login("admin", "nueva_clave_456")
    assert result is not None
    assert result["nombre"] == "Administrador"


def test_cambiar_password_usuario_inexistente(temp_db):
    """cambiar_password debe devolver False si el usuario no existe."""
    assert database.cambiar_password(9999, "nueva_clave") is False


# --- Cuenta Corriente: Pagos y Antigüedad ---

def test_registrar_pago_cc_reduce_deuda(temp_db):
    """registrar_pago_cc debe insertar un movimiento negativo y reducir el saldo."""
    from database import add_cliente, crear_venta, registrar_pago_cc, get_cuenta_corriente_cliente
    add_cliente("Juan Pérez", "1234", "juan@mail.com")
    # Generar deuda: venta a cuenta corriente
    database.add_categoria("Aceites")
    database.add_proveedor("Prov", None, None, "Contado")
    database.add_producto(None, "Aceite 5W30", "", 1, 1, "Entero", 5, 100, 200, stock_inicial=10)
    items = [{'producto_id': 1, 'cantidad': 2, 'precio_unitario': 200}]
    venta_id, _, _ = crear_venta(1, 'ticket', items, 'cuenta_corriente', 1)
    assert venta_id is not None
    # Deuda inicial 400
    assert get_cuenta_corriente_cliente(1) == 400.0
    # Pago parcial de 150
    ok = registrar_pago_cc(1, 150.0, 'efectivo', 'Pago parcial', 1)
    assert ok is True
    # Deuda debe haber bajado a 250
    assert get_cuenta_corriente_cliente(1) == 250.0


def test_registrar_pago_cc_pago_total_saldando(temp_db):
    """registrar_pago_cc con monto = deuda total debe dejar saldo en 0."""
    from database import add_cliente, crear_venta, registrar_pago_cc, get_cuenta_corriente_cliente
    add_cliente("Ana", "111", "ana@mail.com")
    database.add_categoria("Filtros")
    database.add_proveedor("Prov2", None, None, "Contado")
    database.add_producto(None, "Filtro", "", 1, 1, "Entero", 2, 50, 100, stock_inicial=20)
    items = [{'producto_id': 1, 'cantidad': 3, 'precio_unitario': 100}]
    crear_venta(1, 'ticket', items, 'cuenta_corriente', 1)
    # Deuda 300, pago total 300
    registrar_pago_cc(1, 300.0, 'transferencia', 'Pago total', 1)
    assert get_cuenta_corriente_cliente(1) == 0.0


def test_registrar_pago_cc_monto_negativo_devuelve_false(temp_db):
    """registrar_pago_cc no debe aceptar montos negativos."""
    from database import add_cliente, registrar_pago_cc
    add_cliente("Cliente", None, None)
    ok = registrar_pago_cc(1, -100.0, 'efectivo', 'Test', 1)
    assert ok is False


def test_registrar_pago_cc_cliente_inexistente_devuelve_false(temp_db):
    """registrar_pago_cc debe devolver False si el cliente no existe."""
    ok = database.registrar_pago_cc(9999, 100.0, 'efectivo', 'Test', 1)
    assert ok is False


def test_registrar_pago_cc_registra_tipo_movimiento_pago(temp_db):
    """El movimiento de pago debe tener tipo_movimiento='pago'."""
    from database import add_cliente, crear_venta, registrar_pago_cc, get_connection
    add_cliente("Cliente", None, None)
    database.add_categoria("Cat")
    database.add_proveedor("Prov", None, None, "Contado")
    database.add_producto(None, "Prod", "", 1, 1, "Entero", 1, 10, 20, stock_inicial=5)
    crear_venta(1, 'ticket', [{'producto_id': 1, 'cantidad': 1, 'precio_unitario': 20}], 'cuenta_corriente', 1)
    registrar_pago_cc(1, 20.0, 'efectivo', 'Pago', 1)
    conn = get_connection()
    row = conn.execute("SELECT tipo_movimiento FROM cuenta_corriente WHERE cliente_id=1 ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    assert row is not None
    assert row[0] == 'pago'


def test_crear_venta_cuenta_corriente_registra_tipo_venta(temp_db):
    """crear_venta a cuenta corriente debe registrar tipo_movimiento='venta'."""
    from database import add_cliente, crear_venta, get_connection
    add_cliente("Cliente", None, None)
    database.add_categoria("Cat")
    database.add_proveedor("Prov", None, None, "Contado")
    database.add_producto(None, "Prod", "", 1, 1, "Entero", 1, 10, 20, stock_inicial=5)
    crear_venta(1, 'ticket', [{'producto_id': 1, 'cantidad': 1, 'precio_unitario': 20}], 'cuenta_corriente', 1)
    conn = get_connection()
    row = conn.execute("SELECT tipo_movimiento FROM cuenta_corriente WHERE cliente_id=1 ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    assert row is not None
    assert row[0] == 'venta'


def test_get_clientes_con_deuda_incluye_antiguedad(temp_db):
    """get_clientes_con_deuda debe incluir antigüedad en días."""
    from database import add_cliente, crear_venta
    add_cliente("Cliente Antiguo", None, None)
    database.add_categoria("Cat")
    database.add_proveedor("Prov", None, None, "Contado")
    database.add_producto(None, "Prod", "", 1, 1, "Entero", 1, 10, 20, stock_inicial=5)
    crear_venta(1, 'ticket', [{'producto_id': 1, 'cantidad': 1, 'precio_unitario': 20}], 'cuenta_corriente', 1)
    deudores = database.get_clientes_con_deuda()
    assert len(deudores) == 1
    # Debe tener al menos 5 columnas extras: id, nombre, telefono, email, deuda, antiguedad_dias
    assert len(deudores[0]) >= 6, f"Debe incluir antigüedad, got {len(deudores[0])} cols"


def test_get_movimientos_cuenta_corriente_incluye_tipo_y_metodo(temp_db):
    """get_movimientos_cuenta_corriente debe incluir tipo_movimiento y metodo_pago."""
    from database import add_cliente, crear_venta, registrar_pago_cc
    add_cliente("Cliente", None, None)
    database.add_categoria("Cat")
    database.add_proveedor("Prov", None, None, "Contado")
    database.add_producto(None, "Prod", "", 1, 1, "Entero", 1, 10, 20, stock_inicial=10)
    crear_venta(1, 'ticket', [{'producto_id': 1, 'cantidad': 1, 'precio_unitario': 20}], 'cuenta_corriente', 1)
    registrar_pago_cc(1, 10.0, 'transferencia', 'Pago parcial', 1)
    movs = database.get_movimientos_cuenta_corriente(1)
    assert len(movs) == 2  # 1 venta + 1 pago
    # Columna 9 = tipo_movimiento (ver SELECT en get_movimientos_cuenta_corriente)
    tipos = [m[9] for m in movs]
    assert 'venta' in tipos
    assert 'pago' in tipos


# --- Aumento % por proveedor ---

def test_aumentar_precios_proveedor(temp_db):
    """aumentar_precios_proveedor debe actualizar precio_venta de productos del proveedor."""
    from database import add_proveedor, add_categoria, add_producto, get_productos, aumentar_precios_proveedor
    assert add_categoria("Cat") is True
    assert add_proveedor("ProvX", None, None, "Contado") is True
    # productos del proveedor
    assert add_producto(None, "Producto UNO", "", 1, 1, "Entero", 1, 100.0, 200.0, stock_inicial=5)
    assert add_producto(None, "Producto DOS", "", 1, 1, "Entero", 1, 50.0, 100.0, stock_inicial=5)
    # producto de OTRO proveedor (no debe cambiar)
    assert add_proveedor("ProvY", None, None, "Contado") is True
    assert add_producto(None, "Producto TRES", "", 1, 2, "Entero", 1, 80.0, 160.0, stock_inicial=5)

    # Aumentar 10% al proveedor 1
    ok = aumentar_precios_proveedor(1, 10.0)
    assert ok is True

    prods = get_productos()
    precios = {p[2]: p[10] for p in prods}  # p[10] = precio_venta
    assert precios["Producto UNO"] == 220.0, f"Producto UNO deberia ser 220.0, es {precios.get('Producto UNO')}"
    assert precios["Producto DOS"] == 110.0, f"Producto DOS deberia ser 110.0, es {precios.get('Producto DOS')}"
    assert precios["Producto TRES"] == 160.0, f"Producto TRES NO deberia cambiar, es {precios.get('Producto TRES')}"


def test_aumentar_precios_proveedor_proveedor_inexistente(temp_db):
    """aumentar_precios_proveedor debe devolver False si el proveedor no existe."""
    ok = database.aumentar_precios_proveedor(9999, 10.0)
    assert ok is False


def test_aumentar_precios_proveedor_porcentaje_negativo(temp_db):
    """aumentar_precios_proveedor no debe aceptar porcentaje negativo."""
    from database import add_proveedor, aumentar_precios_proveedor
    add_proveedor("Prov", None, None, "Contado")
    ok = aumentar_precios_proveedor(1, -10.0)
    assert ok is False


# --- Aumento % por lista de IDs ---

def test_aumentar_precios_por_lista_happy_path(temp_db):
    """aumentar_precios_por_lista debe actualizar el precio de los productos indicados."""
    from database import (add_categoria, add_proveedor, add_producto,
                          get_productos, aumentar_precios_por_lista)
    add_categoria("Cat")
    add_proveedor("Prov", "C", "0", "Contado")
    add_producto("001", "P1", "", 1, 1, "Entero", 0, 10.0, 100.0, 10)
    add_producto("002", "P2", "", 1, 1, "Entero", 0, 10.0, 200.0, 10)
    result = aumentar_precios_por_lista([1, 2], 10.0)
    assert result == 2
    prods = get_productos()
    assert prods[0][10] == 110.0
    assert prods[1][10] == 220.0


def test_aumentar_precios_por_lista_lista_vacia(temp_db):
    """aumentar_precios_por_lista con lista vacia debe devolver 0."""
    result = database.aumentar_precios_por_lista([], 10.0)
    assert result == 0


def test_aumentar_precios_por_lista_porcentaje_negativo(temp_db):
    """aumentar_precios_por_lista con porcentaje negativo debe devolver 0."""
    from database import add_categoria, add_proveedor, add_producto
    add_categoria("Cat")
    add_proveedor("Prov", "C", "0", "Contado")
    add_producto("001", "P1", "", 1, 1, "Entero", 0, 10.0, 100.0, 10)
    result = database.aumentar_precios_por_lista([1], -10.0)
    assert result == 0


def test_aumentar_precios_por_lista_ids_inexistentes(temp_db):
    """aumentar_precios_por_lista con IDs que no existen debe devolver 0."""
    result = database.aumentar_precios_por_lista([999, 888], 10.0)
    assert result == 0


# --- Productos por proveedor ---

def test_get_productos_por_proveedor_happy_path(temp_db):
    """get_productos_por_proveedor debe devolver solo los productos del proveedor indicado."""
    database.add_categoria("Cat")
    database.add_proveedor("ProvA", "C", "0", "Contado")
    database.add_proveedor("ProvB", "C", "1", "Contado")
    database.add_producto("001", "ProdA1", "", 1, 1, "Entero", 0, 10.0, 100.0, 10)
    database.add_producto("002", "ProdA2", "", 1, 1, "Entero", 0, 10.0, 200.0, 10)
    database.add_producto("003", "ProdB1", "", 1, 2, "Entero", 0, 10.0, 300.0, 10)
    prods = database.get_productos_por_proveedor(1)
    assert len(prods) == 2
    assert all(p[1] in ("ProdA1", "ProdA2") for p in prods)


def test_get_productos_por_proveedor_con_busqueda(temp_db):
    """get_productos_por_proveedor con busqueda debe filtrar por nombre."""
    database.add_categoria("Cat")
    database.add_proveedor("Prov", "C", "0", "Contado")
    database.add_producto("001", "Aceite Motor", "", 1, 1, "Entero", 0, 10.0, 100.0, 10)
    database.add_producto("002", "Filtro Aceite", "", 1, 1, "Entero", 0, 10.0, 200.0, 10)
    database.add_producto("003", "Bujia", "", 1, 1, "Entero", 0, 10.0, 300.0, 10)
    prods = database.get_productos_por_proveedor(1, busqueda="Filtro")
    assert len(prods) == 1
    assert prods[0][1] == "Filtro Aceite"


def test_get_productos_por_proveedor_proveedor_inexistente(temp_db):
    """get_productos_por_proveedor con proveedor inexistente debe devolver lista vacia."""
    prods = database.get_productos_por_proveedor(9999)
    assert prods == []


def test_get_productos_por_proveedor_sin_busqueda(temp_db):
    """get_productos_por_proveedor sin busqueda debe devolver todos los productos del proveedor."""
    database.add_categoria("Cat")
    database.add_proveedor("Prov", "C", "0", "Contado")
    database.add_producto("001", "Prod1", "", 1, 1, "Entero", 0, 10.0, 100.0, 10)
    database.add_producto("002", "Prod2", "", 1, 1, "Entero", 0, 10.0, 200.0, 10)
    prods = database.get_productos_por_proveedor(1)
    assert len(prods) == 2
    names = [p[1] for p in prods]
    assert "Prod1" in names
    assert "Prod2" in names


# --- Cuenta Corriente: Selección de tickets a pagar ---

def test_get_ventas_pendientes_cc(temp_db):
    """get_ventas_pendientes_cc debe devolver ventas a crédito con saldo pendiente."""
    from database import add_cliente, crear_venta
    add_cliente("Cliente", None, None)
    database.add_categoria("Cat")
    database.add_proveedor("Prov", None, None, "Contado")
    database.add_producto(None, "Prod", "", 1, 1, "Entero", 1, 10, 20, stock_inicial=20)
    crear_venta(1, 'ticket', [{'producto_id': 1, 'cantidad': 2, 'precio_unitario': 20}], 'cuenta_corriente', 1)
    crear_venta(1, 'ticket', [{'producto_id': 1, 'cantidad': 1, 'precio_unitario': 50}], 'cuenta_corriente', 1)
    pendientes = database.get_ventas_pendientes_cc(1)
    assert len(pendientes) == 2
    # Cada item: (venta_id, tipo_comprobante, punto_venta, numero, total, ya_pagado, pendiente)
    v1 = next(p for p in pendientes if p[0] == 1)
    assert v1[4] == 40  # total
    assert v1[5] == 0.0  # ya_pagado
    assert v1[6] == 40.0  # pendiente


def test_get_ventas_pendientes_cc_tras_pago_parcial(temp_db):
    """get_ventas_pendientes_cc debe reflejar pagos parciales aplicados a una venta."""
    from database import add_cliente, crear_venta, registrar_pago_cc_con_ventas
    add_cliente("Cliente", None, None)
    database.add_categoria("Cat")
    database.add_proveedor("Prov", None, None, "Contado")
    database.add_producto(None, "Prod", "", 1, 1, "Entero", 1, 10, 20, stock_inicial=30)
    crear_venta(1, 'ticket', [{'producto_id': 1, 'cantidad': 2, 'precio_unitario': 20}], 'cuenta_corriente', 1)
    # Pago parcial de 15 aplicado a venta #1
    registrar_pago_cc_con_ventas(1, 15.0, 'efectivo', 'Pago parcial', 1, [1])
    pendientes = database.get_ventas_pendientes_cc(1)
    v1 = pendientes[0]
    assert v1[4] == 40  # total
    assert v1[5] == 15.0  # ya_pagado
    assert v1[6] == 25.0  # pendiente


def test_registrar_pago_cc_con_ventas_imputa_pago(temp_db):
    """registrar_pago_cc_con_ventas debe imputar el pago a las ventas indicadas."""
    from database import add_cliente, crear_venta, registrar_pago_cc_con_ventas, get_connection
    add_cliente("Cliente", None, None)
    database.add_categoria("Cat")
    database.add_proveedor("Prov", None, None, "Contado")
    database.add_producto(None, "Prod", "", 1, 1, "Entero", 1, 10, 20, stock_inicial=20)
    crear_venta(1, 'ticket', [{'producto_id': 1, 'cantidad': 2, 'precio_unitario': 20}], 'cuenta_corriente', 1)
    # Pago total de 40 aplicado a venta #1
    ok = registrar_pago_cc_con_ventas(1, 40.0, 'efectivo', 'Pago total', 1, [1])
    assert ok is True
    # Verificar que el pago tiene asociada la venta #1
    conn = get_connection()
    row = conn.execute("SELECT ventas_imputadas, monto FROM cuenta_corriente WHERE tipo_movimiento='pago' ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    assert row is not None
    assert '1' in (row[0] or '')
    assert row[1] == -40.0


def test_registrar_pago_cc_con_ventas_monto_negativo_devuelve_false(temp_db):
    """registrar_pago_cc_con_ventas no debe aceptar monto negativo."""
    from database import add_cliente, registrar_pago_cc_con_ventas
    add_cliente("Cliente", None, None)
    ok = registrar_pago_cc_con_ventas(1, -10.0, 'efectivo', 'Test', 1, [1])
    assert ok is False


# --- Reportes ---

def test_reporte_inventario_vacio(temp_db):
    """Cuando no hay productos activos, el reporte de inventario debe estar vacío."""
    inv = database.get_reporte_inventario()
    assert inv == []


def test_reporte_inventario_con_datos(temp_db):
    """Verifica que get_reporte_inventario devuelva datos correctos con valorización."""
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_producto(
        "7790001", "Aceite 5W30", "Sintético",
        1, 1, "Entero", 5, 100, 150, stock_inicial=20
    )
    inv = database.get_reporte_inventario()
    assert len(inv) == 1
    row = inv[0]
    # (id, nombre, stock_actual, stock_minimo, precio_costo, precio_venta, categoria, valor_costo, valor_venta)
    assert row[1] == "Aceite 5W30"
    assert row[2] == 20.0       # stock_actual
    assert row[3] == 5          # stock_minimo
    assert row[4] == 100        # precio_costo
    assert row[5] == 150        # precio_venta
    assert row[6] == "Aceites"  # categoria
    assert row[7] == 2000.0     # valor_costo = 20 * 100
    assert row[8] == 3000.0     # valor_venta = 20 * 150


def test_reporte_inventario_excluye_productos_inactivos(temp_db):
    """Productos desactivados (activo=0) no deben aparecer en el reporte."""
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_producto(
        "7790001", "Aceite 5W30", "Sintético",
        1, 1, "Entero", 5, 100, 150, stock_inicial=20
    )
    conn = database.get_connection()
    conn.execute("UPDATE productos SET activo = 0 WHERE id = 1")
    conn.commit()
    conn.close()
    inv = database.get_reporte_inventario()
    assert inv == []


# --- Caja ---
def test_abrir_caja_exitoso(temp_db):
    caja_id = database.abrir_caja(1000.0, 1)
    assert caja_id is not None
    assert isinstance(caja_id, int)
    caja = database.get_caja_abierta()
    assert caja is not None
    assert caja[0] == caja_id
    assert caja[1] == 1000.0  # saldo_inicial
    assert caja[2] == 1000.0  # saldo_actual
    assert caja[6] == 1       # abierta


def test_abrir_caja_saldo_negativo(temp_db):
    caja_id = database.abrir_caja(-100.0, 1)
    assert caja_id is None
    assert database.get_caja_abierta() is None


def test_abrir_caja_ya_abierta_devuelve_none(temp_db):
    database.abrir_caja(1000.0, 1)
    segundo = database.abrir_caja(500.0, 1)
    assert segundo is None
    # Solo debe haber una caja abierta
    assert database.get_caja_abierta() is not None


def test_get_caja_abierta_sin_caja(temp_db):
    assert database.get_caja_abierta() is None


def test_cerrar_caja_exitoso(temp_db):
    caja_id = database.abrir_caja(1000.0, 1)
    assert caja_id is not None
    ok = database.cerrar_caja(caja_id, 1500.0, 1)
    assert ok is True
    # No debe aparecer como abierta
    assert database.get_caja_abierta() is None
    # Verificar que se registró movimiento de cierre
    conn = database.get_connection()
    mov = conn.execute(
        "SELECT tipo, monto, saldo_anterior, saldo_nuevo FROM movimientos_caja WHERE caja_id = ?",
        (caja_id,)
    ).fetchall()
    conn.close()
    assert len(mov) >= 2  # apertura + cierre
    assert mov[-1][0] == 'cierre'


def test_cerrar_caja_ya_cerrada(temp_db):
    caja_id = database.abrir_caja(1000.0, 1)
    database.cerrar_caja(caja_id, 1000.0, 1)
    ok = database.cerrar_caja(caja_id, 1000.0, 1)
    assert ok is False


def test_cerrar_caja_inexistente(temp_db):
    ok = database.cerrar_caja(9999, 1000.0, 1)
    assert ok is False


def test_registrar_movimiento_caja_exitoso(temp_db):
    caja_id = database.abrir_caja(1000.0, 1)
    ok = database.registrar_movimiento_caja(caja_id, 'ajuste', 200.0, 1000.0, 1200.0, 'Ajuste manual', 1)
    assert ok is True
    conn = database.get_connection()
    mov = conn.execute(
        "SELECT tipo, monto, saldo_anterior, saldo_nuevo, observacion FROM movimientos_caja WHERE caja_id = ? AND tipo = 'ajuste'",
        (caja_id,)
    ).fetchone()
    conn.close()
    assert mov is not None
    assert mov[0] == 'ajuste'
    assert mov[1] == 200.0
    assert mov[4] == 'Ajuste manual'


def test_registrar_movimiento_caja_tipo_invalido(temp_db):
    caja_id = database.abrir_caja(1000.0, 1)
    ok = database.registrar_movimiento_caja(caja_id, 'tipo_invalido', 100.0, 1000.0, 1100.0, 'Test', 1)
    assert ok is False


def test_crear_venta_con_caja_abierta_registra_ingreso(temp_db):
    """Verifica que crear_venta registre automáticamente un movimiento ingreso_venta en la caja abierta."""
    # Setup: caja abierta, productos, etc.
    database.abrir_caja(5000.0, 1)
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_producto("779001", "Aceite 20W50", "", 1, 1, "Entero", 5, 50, 100, stock_inicial=100)
    items = [{'producto_id': 1, 'cantidad': 2, 'precio_unitario': 100.0}]
    venta_id, num, error = database.crear_venta(None, 'ticket', items, 'efectivo', 1)
    assert venta_id is not None
    assert error is None
    conn = database.get_connection()
    mov = conn.execute(
        "SELECT tipo, monto, saldo_anterior, saldo_nuevo FROM movimientos_caja WHERE tipo = 'ingreso_venta'"
    ).fetchone()
    conn.close()
    assert mov is not None
    assert mov[0] == 'ingreso_venta'
    assert mov[1] == 200.0  # total de la venta
    assert mov[2] == 5000.0  # saldo anterior
    assert mov[3] == 5200.0  # saldo nuevo


def test_crear_venta_sin_caja_abierta_no_registra_ingreso(temp_db):
    """Si no hay caja abierta, crear_venta no debe registrar movimiento de caja."""
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_producto("779001", "Aceite 20W50", "", 1, 1, "Entero", 5, 50, 100, stock_inicial=100)
    items = [{'producto_id': 1, 'cantidad': 2, 'precio_unitario': 100.0}]
    venta_id, num, error = database.crear_venta(None, 'ticket', items, 'efectivo', 1)
    assert venta_id is not None
    conn = database.get_connection()
    count = conn.execute("SELECT COUNT(*) FROM movimientos_caja").fetchone()[0]
    conn.close()
    assert count == 0


# --- Soft delete de clientes ---
def test_desactivar_cliente(temp_db):
    database.add_cliente("Juan Pérez", "1234", "juan@test.com")
    clientes = database.get_clientes()
    assert len(clientes) == 1
    cliente_id = clientes[0][0]
    ok = database.desactivar_cliente(cliente_id)
    assert ok is True
    # No debe aparecer en get_clientes() por defecto
    clientes_activos = database.get_clientes()
    assert len(clientes_activos) == 0
    # Debe aparecer con incluir_inactivos=True
    todos = database.get_clientes(incluir_inactivos=True)
    assert len(todos) == 1
    assert todos[0][4] == 0  # activo = 0


def test_reactivar_cliente(temp_db):
    database.add_cliente("Juan Pérez", "1234", "juan@test.com")
    cliente_id = database.get_clientes()[0][0]
    database.desactivar_cliente(cliente_id)
    ok = database.reactivar_cliente(cliente_id)
    assert ok is True
    clientes = database.get_clientes()
    assert len(clientes) == 1
    assert clientes[0][0] == cliente_id


def test_desactivar_cliente_inexistente(temp_db):
    ok = database.desactivar_cliente(9999)
    assert ok is False


def test_reactivar_cliente_inexistente(temp_db):
    ok = database.reactivar_cliente(9999)
    assert ok is False


# --- Lista de precios ---
def test_get_precios_para_lista_solo_activos_con_stock(temp_db):
    """Solo productos activos con stock > 0 deben aparecer en la lista de precios."""
    database.add_categoria("Aceites")
    database.add_categoria("Filtros")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_proveedor("Shell", "Ana", "5678", "Contado")
    # Producto YPF Aceites con stock
    database.add_producto("779001", "Aceite 5W30 YPF", "", 1, 1, "Entero", 5, 100, 150, stock_inicial=20)
    # Producto Shell Filtros con stock
    database.add_producto("779002", "Filtro Aceite Shell", "", 2, 2, "Entero", 5, 200, 300, stock_inicial=10)
    # Producto YPF sin stock (no debe aparecer)
    database.add_producto("779003", "Aceite 10W40 YPF", "", 1, 1, "Entero", 5, 100, 180, stock_inicial=0)
    # Producto inactivo con stock (no debe aparecer)
    database.add_producto("779004", "Filtro Aire YPF", "", 2, 1, "Entero", 5, 100, 200, stock_inicial=15)
    conn = database.get_connection()
    conn.execute("UPDATE productos SET activo = 0 WHERE id = 4")
    conn.commit()
    conn.close()

    lista = database.get_precios_para_lista()
    nombres = [p[1] for p in lista]
    assert "Aceite 5W30 YPF" in nombres
    assert "Filtro Aceite Shell" in nombres
    assert "Aceite 10W40 YPF" not in nombres  # sin stock
    assert "Filtro Aire YPF" not in nombres  # inactivo


def test_get_precios_para_lista_ordenado_por_proveedor(temp_db):
    """La lista debe estar ordenada por proveedor y luego por nombre de producto."""
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_proveedor("Shell", "Ana", "5678", "Contado")
    database.add_producto("779003", "Z-Aceite B YPF", "", 1, 1, "Entero", 5, 100, 150, stock_inicial=5)
    database.add_producto("779001", "A-Aceite A YPF", "", 1, 1, "Entero", 5, 100, 150, stock_inicial=5)
    database.add_producto("779002", "A-Aceite Shell", "", 1, 2, "Entero", 5, 100, 150, stock_inicial=5)

    lista = database.get_precios_para_lista()
    # Ordenado por proveedor, Shell < YPF
    assert lista[0][0] == "Shell"
    assert lista[1][0] == "YPF"
    # Dentro de YPF, ordenado por nombre: A-Aceite A < Z-Aceite B
    nombres_ypf = [p[1] for p in lista if p[0] == "YPF"]
    assert nombres_ypf == ["A-Aceite A YPF", "Z-Aceite B YPF"]


def test_get_precios_para_lista_incluye_precio_venta(temp_db):
    """La lista debe incluir el precio de venta correcto."""
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_producto("779001", "Aceite YPF", "", 1, 1, "Entero", 5, 100, 150.50, stock_inicial=10)
    lista = database.get_precios_para_lista()
    assert len(lista) == 1
    assert lista[0][3] == 150.50


# --- Categorias por proveedor ---
def test_get_categorias_por_proveedor(temp_db):
    database.add_categoria("Aceites")
    database.add_categoria("Filtros")
    database.add_categoria("Lubricantes")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_producto("779001", "Aceite YPF", "", 1, 1, "Entero", 5, 100, 150, stock_inicial=10)
    database.add_producto("779002", "Filtro YPF", "", 2, 1, "Entero", 5, 100, 150, stock_inicial=10)
    # P003 sin categoria ( categoria_id = NULL )
    database.add_producto("779003", "Sin Cat YPF", "", None, 1, "Entero", 5, 100, 150, stock_inicial=10)
    cats = database.get_categorias_por_proveedor(1)
    cat_nombres = [c[1] for c in cats]
    assert "Aceites" in cat_nombres
    assert "Filtros" in cat_nombres
    assert "Lubricantes" not in cat_nombres  # YPF no tiene productos en Lubricantes
    # Debe estar ordenado alfabeticamente
    assert cat_nombres == sorted(cat_nombres)


def test_get_categorias_por_proveedor_sin_productos(temp_db):
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    cats = database.get_categorias_por_proveedor(1)
    assert cats == []


def test_get_categorias_por_proveedor_proveedor_inexistente(temp_db):
    cats = database.get_categorias_por_proveedor(9999)
    assert cats == []


# --- Aumentar precios por categoria ---
def test_aumentar_precios_por_categoria(temp_db):
    """Solo los productos del proveedor Y categoria especificados deben actualizarse."""
    database.add_categoria("Aceites")
    database.add_categoria("Filtros")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_proveedor("Shell", "Ana", "5678", "Contado")
    database.add_producto("779001", "Aceite YPF", "", 1, 1, "Entero", 5, 100, 150, stock_inicial=10)
    database.add_producto("779002", "Filtro YPF", "", 2, 1, "Entero", 5, 100, 200, stock_inicial=10)
    database.add_producto("779003", "Aceite Shell", "", 1, 2, "Entero", 5, 100, 300, stock_inicial=10)

    # Aumentar 10% solo Aceites de YPF (proveedor_id=1, categoria_id=1)
    actualizados = database.aumentar_precios_por_categoria(1, 10.0, 1)
    assert actualizados == 1  # solo P001 es YPF + Aceites
    conn = database.get_connection()
    p1 = conn.execute("SELECT precio_venta FROM productos WHERE id = 1").fetchone()[0]
    p2 = conn.execute("SELECT precio_venta FROM productos WHERE id = 2").fetchone()[0]
    p3 = conn.execute("SELECT precio_venta FROM productos WHERE id = 3").fetchone()[0]
    conn.close()
    assert p1 == 165.0  # 150 * 1.10
    assert p2 == 200.0  # sin cambios (distinta categoria)
    assert p3 == 300.0  # sin cambios (distinto proveedor)


def test_aumentar_precios_por_categoria_multiples_productos(temp_db):
    """Si el proveedor tiene varios productos en la categoria, todos se actualizan."""
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_producto("779001", "Aceite A YPF", "", 1, 1, "Entero", 5, 100, 150, stock_inicial=10)
    database.add_producto("779002", "Aceite B YPF", "", 1, 1, "Entero", 5, 100, 200, stock_inicial=10)
    database.add_producto("779003", "Filtro YPF", "", None, 1, "Entero", 5, 100, 100, stock_inicial=10)

    actualizados = database.aumentar_precios_por_categoria(1, 20.0, 1)
    assert actualizados == 2  # P001 y P002 son Aceites de YPF


def test_aumentar_precios_por_categoria_proveedor_inexistente(temp_db):
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_producto("779001", "Aceite YPF", "", 1, 1, "Entero", 5, 100, 150, stock_inicial=10)
    actualizados = database.aumentar_precios_por_categoria(9999, 10.0, 1)
    assert actualizados == 0


def test_aumentar_precios_por_categoria_categoria_sin_productos(temp_db):
    database.add_categoria("Aceites")
    database.add_categoria("Filtros")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_producto("779001", "Aceite YPF", "", 1, 1, "Entero", 5, 100, 150, stock_inicial=10)
    # No existen productos en categoria Filtros (id=2) para YPF
    actualizados = database.aumentar_precios_por_categoria(1, 10.0, 2)
    assert actualizados == 0


def test_aumentar_precios_por_categoria_porcentaje_negativo(temp_db):
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_producto("779001", "Aceite YPF", "", 1, 1, "Entero", 5, 100, 150, stock_inicial=10)
    actualizados = database.aumentar_precios_por_categoria(1, -10.0, 1)
    assert actualizados == 0


def test_aumentar_precios_por_categoria_porcentaje_invalido(temp_db):
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "Juan", "1234", "Contado")
    database.add_producto("779001", "Aceite YPF", "", 1, 1, "Entero", 5, 100, 150, stock_inicial=10)
    actualizados = database.aumentar_precios_por_categoria(1, "abc", 1)
    assert actualizados == 0


# =============================================================================
# Edge cases — validaciones de entrada en clientes, vehículos, servicios,
# productos (empty name), proveedores (empty name), compras vacías,
# órdenes de servicio, y caja.
# =============================================================================


# --- Clientes: add_cliente con nombre vacío ---
def test_add_cliente_nombre_vacio(temp_db):
    assert database.add_cliente("", "123", "a@b.com") is False
    assert database.add_cliente("   ", "123", "a@b.com") is False
    assert database.add_cliente(None, "123", "a@b.com") is False
    assert len(database.get_clientes()) == 0


def test_add_cliente_sin_telefono_email(temp_db):
    assert database.add_cliente("Juan", None, None) is True
    assert database.add_cliente("Pedro", "", "") is True
    assert len(database.get_clientes()) == 2


# --- Vehículos ---
def test_add_vehiculo_patente_vacia(temp_db):
    assert database.add_vehiculo(None, "", "Ford", "Fiesta", 2020) is False
    assert database.add_vehiculo(None, "   ", "Ford", "Fiesta", 2020) is False


def test_add_vehiculo_patente_duplicada(temp_db):
    database.add_cliente("Juan", "123", "")
    cliente_id = database.get_clientes()[0][0]
    assert database.add_vehiculo(cliente_id, "ABC123", "Ford", "Fiesta", 2020) is True
    assert database.add_vehiculo(cliente_id, "ABC123", "Chev", "Corsa", 2019) is False
    assert len(database.get_vehiculos()) == 1


def test_add_vehiculo_sin_cliente(temp_db):
    assert database.add_vehiculo(None, "XYZ789", "Ford", "Fiesta", 2020) is True


# --- Servicios ---
def test_add_servicio_nombre_vacio(temp_db):
    assert database.add_servicio("", 100) is False
    assert database.add_servicio("   ", 100) is False
    assert database.add_servicio(None, 100) is False
    assert len(database.get_servicios()) == 0


def test_add_servicio_precio_negativo(temp_db):
    assert database.add_servicio("Alineación", -1) is False
    assert database.add_servicio("Balanceo", 0) is True


def test_add_servicio_precio_invalido(temp_db):
    assert database.add_servicio("Test", "abc") is False
    assert database.add_servicio("Test", None) is False


# --- Productos: empty name (no null) ---
def test_add_producto_nombre_vacio(temp_db):
    cat_id, prov_id = _crear_dependencias()
    assert database.add_producto("7790999", "", "desc", cat_id, prov_id, "Entero", 1, 10, 20) is False
    assert database.add_producto("7790998", "   ", "desc", cat_id, prov_id, "Entero", 1, 10, 20) is False


# --- Proveedores: empty name ---
def test_add_proveedor_nombre_vacio(temp_db):
    assert database.add_proveedor("", "Juan", "123", "Contado") is False
    assert database.add_proveedor("   ", "Ana", "456", "Contado") is False
    assert database.add_proveedor(None, "Luis", "789", "Contado") is False
    assert len(database.get_proveedores()) == 0


# --- Stock: crear_ajuste_stock sin motivo ---
def test_crear_ajuste_stock_sin_motivo(temp_db):
    cat_id, prov_id = _crear_dependencias()
    assert database.add_producto("7790100", "Test", "", cat_id, prov_id, "Entero", 1, 10, 20, stock_inicial=10) is True
    prod_id = database.get_productos()[0][0]
    assert database.crear_ajuste_stock(prod_id, 15, "", 1) is False
    assert database.crear_ajuste_stock(prod_id, 15, "   ", 1) is False


# --- Órdenes de servicio: add_orden_detalle edge cases ---
def test_add_orden_detalle_cantidad_cero(temp_db):
    database.add_cliente("Juan", "123", "")
    cliente_id = database.get_clientes()[0][0]
    orden_id = database.add_orden_servicio(cliente_id, None)
    assert orden_id is not None
    cat_id, prov_id = _crear_dependencias()
    database.add_producto("7790200", "Prod", "", cat_id, prov_id, "Entero", 1, 10, 20, stock_inicial=10)
    prod_id = database.get_productos()[0][0]
    assert database.add_orden_detalle(orden_id, producto_id=prod_id, cantidad=0) is False
    assert database.add_orden_detalle(orden_id, producto_id=prod_id, cantidad=-1) is False


def test_add_orden_detalle_producto_inexistente(temp_db):
    database.add_cliente("Juan", "123", "")
    cliente_id = database.get_clientes()[0][0]
    orden_id = database.add_orden_servicio(cliente_id, None)
    assert orden_id is not None
    assert database.add_orden_detalle(orden_id, producto_id=99999) is False


def test_add_orden_detalle_servicio_inexistente(temp_db):
    database.add_cliente("Juan", "123", "")
    cliente_id = database.get_clientes()[0][0]
    orden_id = database.add_orden_servicio(cliente_id, None)
    assert orden_id is not None
    assert database.add_orden_detalle(orden_id, servicio_id=99999) is False


def test_add_orden_detalle_sin_producto_ni_servicio(temp_db):
    database.add_cliente("Juan", "123", "")
    cliente_id = database.get_clientes()[0][0]
    orden_id = database.add_orden_servicio(cliente_id, None)
    assert orden_id is not None
    assert database.add_orden_detalle(orden_id) is False


# --- Compras: edge cases ---
def test_crear_compra_sin_items(temp_db):
    database.add_proveedor("YPF", "Juan", "123", "Contado")
    prov_id = database.get_proveedores()[0][0]
    assert database.crear_compra(prov_id, []) is None
    assert database.crear_compra(prov_id, None) is None


def test_crear_compra_proveedor_none(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto("7790300", "Prod", "", cat_id, prov_id, "Entero", 1, 10, 20, stock_inicial=0)
    prod_id = database.get_productos()[0][0]
    items = [{"producto_id": prod_id, "cantidad": 5, "precio_unitario": 10}]
    assert database.crear_compra(None, items) is None


def test_crear_compra_producto_stock_actualizado(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto("7790301", "Prod", "", cat_id, prov_id, "Entero", 1, 10, 20, stock_inicial=5)
    prod_id = database.get_productos()[0][0]
    items = [{"producto_id": prod_id, "cantidad": 10, "precio_unitario": 15}]
    compra_id = database.crear_compra(prov_id, items)
    assert compra_id is not None
    prods = database.get_productos()
    assert float(prods[0][7]) == 15.0


# --- Caja: movimiento tipo ajuste ---
def test_registrar_movimiento_caja_tipo_ajuste(temp_db):
    caja_id = database.abrir_caja(1000.0, 1)
    assert caja_id is not None
    caja = database.get_caja_abierta()
    assert caja is not None
    ok = database.registrar_movimiento_caja(caja_id, "ajuste", 500.0, 1000.0, 1500.0, "Ajuste manual", 1)
    assert ok is True


# --- Ventas: cantidad = 0 explícitamente ---
def test_crear_venta_rechaza_cantidad_cero(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.abrir_caja(1000.0, 1)
    database.add_producto("7790400", "Prod", "", cat_id, prov_id, "Entero", 1, 10, 20, stock_inicial=10)
    prod_id = database.get_productos()[0][0]
    items = [{"producto_id": prod_id, "cantidad": 0, "precio_unitario": 20}]
    venta_id, _, msg = database.crear_venta(None, "ticket", items, "efectivo", 1)
    assert venta_id is None
    assert msg is not None


# --- Búsqueda de productos por código / nombre ---
def test_buscar_producto_por_codigo_happy_path(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto("7791001", "Aceite 20W50", "", cat_id, prov_id, "Entero", 1, 1, 2)
    database.add_producto("F0001", "Aceite suelto", "", cat_id, prov_id, "Fraccionable", 1, 1, 2)
    p = database.buscar_producto_por_codigo("f0001")
    assert p is not None
    assert p[2] == "Aceite suelto"


def test_buscar_producto_por_codigo_inexistente_devuelve_none(temp_db):
    cat_id, prov_id = _crear_dependencias()
    assert database.buscar_producto_por_codigo("9999999") is None


def test_buscar_productos_por_nombre_filtra_y_ordena(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto("1", "Aceite hidraulico 20L", "", cat_id, prov_id, "Entero", 1, 1, 2)
    database.add_producto("2", "Aceite suelto", "", cat_id, prov_id, "Fraccionable", 1, 1, 2)
    database.add_producto("3", "Filtro de aire", "", cat_id, prov_id, "Entero", 1, 1, 2)
    res = database.buscar_productos_por_nombre("aceite")
    assert len(res) == 2
    assert res[0][2] == "Aceite hidraulico 20L"


def test_buscar_productos_por_nombre_excluye_inactivos(temp_db):
    cat_id, prov_id = _crear_dependencias()
    database.add_producto("1", "Activo", "", cat_id, prov_id, "Entero", 1, 1, 2)
    database.add_producto("2", "Inactivo", "", cat_id, prov_id, "Entero", 1, 1, 2)
    conn = database.get_connection()
    conn.execute("UPDATE productos SET activo = 0 WHERE codigo_barras = '2'")
    conn.commit()
    conn.close()
    res = database.buscar_productos_por_nombre("vo")
    assert [p[2] for p in res] == ["Activo"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
