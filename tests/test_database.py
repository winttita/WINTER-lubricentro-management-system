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


# --- Pruebas de add_producto con stock inicial ---

def test_add_producto_con_stock_inicial(temp_db):
    """Debe crear producto con stock inicial y registrar movimiento."""
    database.add_categoria("Aceites")
    database.add_proveedor("YPF", "", "", "Contado")
    cat_id = database.get_categorias()[0][0]
    prov_id = database.get_proveedores()[0][0]

    database.add_producto("C100", "7790100", "Test Stock", "", cat_id, prov_id,
                          "Entero", 5, 100, 200, stock_inicial=25)

    productos = database.get_productos()
    p = productos[0]
    assert p[8] == 25.0, f"Stock esperado 25, obtenido {p[8]}"

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

    database.add_producto("C101", "7790101", "Test Sin Stock", "", cat_id, prov_id,
                          "Entero", 5, 100, 200)

    p = database.get_productos()[0]
    assert p[8] == 0.0

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
    database.add_producto("C200", "7790200", "Ajustable", "", cat_id, prov_id,
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
    database.add_producto("C300", "7790300", "Filtro Aceite", "", cat_id, prov_id,
                          "Entero", 10, 500, 800, stock_inicial=20)
    database.add_producto("C301", "7790301", "Filtro Aire", "", cat_id, prov_id,
                          "Entero", 10, 300, 500, stock_inicial=10)

    productos = database.get_productos()
    filtro_aceite = [p for p in productos if p[1] == "C300"][0]
    filtro_aire = [p for p in productos if p[1] == "C301"][0]

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
    assert abs(compras[0][4] - (10*450 + 5*280)) < 0.01

    # Verificar get_detalle_compra
    detalle = database.get_detalle_compra(compra_id)
    assert len(detalle) == 2


def test_anular_compra(temp_db):
    """Debe anular compra y revertir stock."""
    database.add_categoria("Filtros")
    database.add_proveedor("Mann Filter", "", "", "Contado")
    cat_id = database.get_categorias()[0][0]
    prov_id = database.get_proveedores()[0][0]
    database.add_producto("C400", "7790400", "Filtro Test", "", cat_id, prov_id,
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
    add_producto("P1", "CB001", "Producto Test", "", cat_id, prov_id, "Entero", 0, 10.0, 100.0, 5)
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
    add_producto("P2", "CB002", "Producto A", "", cat_id, prov_id, "Entero", 0, 10.0, 121.0, 10)
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
    add_producto("P3", "CB003", "Producto B", "", cat_id, prov_id, "Entero", 0, 10.0, 100.0, 10)
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
    add_producto("P4", "CB004", "Producto Inactivo", "", cat_id, prov_id, "Entero", 0, 10.0, 100.0, 10)
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
    add_producto("P5", "CB005", "Producto B", "", cat_id, prov_id, "Entero", 0, 10.0, 150.0, 10)
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
    add_producto("P6", "CB006", "Producto C", "", cat_id, prov_id, "Entero", 0, 10.0, 200.0, 10)
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
