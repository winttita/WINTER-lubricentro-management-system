"""Tests basados en propiedades (Hypothesis) para database.py.

Verifican invariantes que deben cumplirse para TODAS las entradas generadas
automaticamente, no para casos puntuales. Cada test define una hipotesis:
si la hipotesis no se cumple, Hypothesis encuentra el contraejemplo minimo.

Hipotesis cubiertas:
1. Round-trip: crear + leer devuelve exactamente lo creado.
2. Ledger de stock: stock_actual == inicial + suma(signo * movimientos).
3. No-corrupcion: NaN/Inf nunca deben entrar a la DB ni corromper stock.
4. Ventas: descuentan stock exacto y rechazan valores extremos.
5. Ajustes: establecen stock exacto y rechazan invalidos sin cambiar estado.
6. Compra -> anulacion: round-trip exacto del stock (restauracion).
7. Cuenta corriente: pagos reducen la deuda exactamente (parcial y exceso).
8. Reportes: consistencia entre get_reporte_inventario y get_productos.
"""
import os
import sqlite3
import tempfile
import uuid

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

import database


@pytest.fixture(autouse=True)
def temp_db_autouse(monkeypatch):
    """Apunta database.DB_NAME a un archivo temporal limpio por cada test.

    Autouse (no como parametro de @given): la DB se crea una vez por funcion
    de test y los ejemplos generados acumulan datos unicos, nunca conflicto.
    """
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr(database, "DB_NAME", path)
    database.init_db()
    yield path
    if os.path.exists(path):
        os.remove(path)


# --- Estrategias base -------------------------------------------------------

MONTO = st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False)
CANTIDAD = st.floats(min_value=0.01, max_value=1e4, allow_nan=False, allow_infinity=False)
# Cantidad acotada al stock de los tests de venta (500) para evitar filtrado excesivo
CANTIDAD_VENTA = st.floats(min_value=0.01, max_value=500.0, allow_nan=False, allow_infinity=False)
STOCK_NUEVO = st.floats(min_value=0, max_value=1e5, allow_nan=False, allow_infinity=False)
VALORES_EXTREMOS = [float("nan"), float("inf"), float("-inf"), -1.0, 0.0, 1e308]

settings.register_profile(
    "profundo",
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
settings.load_profile("profundo")


# --- Helpers ----------------------------------------------------------------

def nombre_unico() -> str:
    return f"prop-{uuid.uuid4().hex[:12]}"


def crear_producto_id(stock_inicial=0.0, tipo_unidad="Fraccionable",
                      stock_minimo=0.0, precio_costo=10.0, precio_venta=20.0) -> int:
    codigo = nombre_unico()
    assert database.add_producto(
        codigo_barras=codigo,
        nombre=nombre_unico(),
        descripcion=None,
        categoria_id=None,
        proveedor_id=None,
        tipo_unidad=tipo_unidad,
        stock_minimo=stock_minimo,
        precio_costo=precio_costo,
        precio_venta=precio_venta,
        stock_inicial=stock_inicial,
    ) is True
    for p in database.get_productos():
        if p[1] == codigo:
            return p[0]
    raise AssertionError("producto recien creado no encontrado")


def stock_de(producto_id):
    """Devuelve stock_actual crudo (puede ser None si quedo corrupto en DB)."""
    conn = database.get_connection()
    try:
        row = conn.execute(
            "SELECT stock_actual FROM productos WHERE id = ?", (producto_id,)
        ).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def buscar_producto(producto_id):
    for p in database.get_productos():
        if p[0] == producto_id:
            return p
    return None


def crear_cliente_id() -> int:
    nombre = nombre_unico()
    assert database.add_cliente(nombre, None, None) is True
    for c in database.get_clientes():
        if c[1] == nombre:
            return c[0]
    raise AssertionError("cliente recien creado no encontrado")


def crear_proveedor_id() -> int:
    nombre = nombre_unico()
    assert database.add_proveedor(nombre, None, None, None) is True
    for prov in database.get_proveedores():
        if prov[1] == nombre:
            return prov[0]
    raise AssertionError("proveedor recien creado no encontrado")


def contar_movimientos(producto_id) -> int:
    conn = database.get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM movimientos_stock WHERE producto_id = ?",
            (producto_id,),
        ).fetchone()
        return row[0]
    finally:
        conn.close()


# --- 1. Round-trip ----------------------------------------------------------

@given(st.text(min_size=1, max_size=30))
def test_categoria_roundtrip(nombre):
    nombre = f"{nombre[:20]}-{uuid.uuid4().hex[:6]}"
    assert database.add_categoria(nombre) is True
    assert any(c[1] == nombre.strip() for c in database.get_categorias())


@given(MONTO, MONTO, MONTO, STOCK_NUEVO)
def test_producto_roundtrip( stock_minimo, precio_costo, precio_venta, stock_inicial):
    codigo = nombre_unico()
    assert database.add_producto(
        codigo_barras=codigo, nombre="Aceite Prop", descripcion=None,
        categoria_id=None, proveedor_id=None, tipo_unidad="Fraccionable",
        stock_minimo=stock_minimo, precio_costo=precio_costo,
        precio_venta=precio_venta, stock_inicial=stock_inicial,
    ) is True
    ps = [p for p in database.get_productos() if p[1] == codigo]
    assert len(ps) == 1
    p = ps[0]
    assert p[2] == "Aceite Prop"
    assert p[7] == pytest.approx(stock_inicial)
    assert p[8] == pytest.approx(stock_minimo)
    assert p[9] == pytest.approx(precio_costo)
    assert p[10] == pytest.approx(precio_venta)


@given(MONTO, MONTO)
def test_update_producto_refleja_cambios( costo, venta):
    pid = crear_producto_id()
    assert database.update_producto(
        pid, nombre_unico(), "nuevo nombre", None, None, None,
        "Fraccionable", 5.0, costo, venta,
    ) is True
    p = buscar_producto(pid)
    assert p is not None
    assert p[2] == "nuevo nombre"
    assert p[8] == pytest.approx(5.0)
    assert p[9] == pytest.approx(costo)
    assert p[10] == pytest.approx(venta)


# --- 2. Ledger de stock (invariante central) --------------------------------

TIPOS_SUMAN = {"compra", "devolucion"}
TIPOS_RESTAN = {"venta", "uso_interno"}
TIPOS_VALIDOS = ["compra", "venta", "devolucion", "uso_interno", "ajuste"]


@given(
    st.lists(
        st.tuples(st.sampled_from(TIPOS_VALIDOS), CANTIDAD),
        max_size=25,
    )
)
def test_ledger_stock_consistente( movimientos):
    """Hipotesis: stock_actual == stock_inicial + suma(signo * cantidad)
    para cualquier secuencia de movimientos; nunca negativo; y cada
    movimiento exitoso registra exactamente una fila en movimientos_stock."""
    stock_inicial = 100.0
    pid = crear_producto_id(stock_inicial=stock_inicial)
    esperado = stock_inicial
    # add_producto registra 1 movimiento ("Stock inicial al crear producto")
    movimientos_esperados = 1
    for tipo, cantidad in movimientos:
        if tipo in TIPOS_SUMAN:
            delta = cantidad
        elif tipo in TIPOS_RESTAN:
            delta = -cantidad
        else:  # ajuste: la cantidad lleva su propio signo
            delta = cantidad
        resultado = database.add_movimiento(pid, tipo, cantidad, "prop-test")
        if esperado + delta < 0:
            assert resultado is False, f"movimiento que deja stock negativo aceptado: {tipo} {cantidad}"
        else:
            assert resultado is True, f"movimiento valido rechazado: {tipo} {cantidad}"
            esperado += delta
            movimientos_esperados += 1
        stock = stock_de(pid)
        assert stock is not None
        assert stock == pytest.approx(esperado)
        assert stock >= 0
    assert contar_movimientos(pid) == movimientos_esperados


# --- 3. No-corrupcion con NaN/Inf ------------------------------------------

@given(st.sampled_from(VALORES_EXTREMOS))
def test_movimiento_extremo_no_corrompe_stock( cantidad):
    """Hipotesis: jamas se acepta un movimiento que deje el stock en NaN/Inf/None."""
    pid = crear_producto_id(stock_inicial=10.0)
    antes = stock_de(pid)
    resultado = database.add_movimiento(pid, "compra", cantidad, "prop-test")
    despues = stock_de(pid)
    assert despues is not None, f"stock corrompido a NULL (movimiento aceptado={resultado})"
    assert despues == despues, "stock corrompido a NaN"
    assert despues not in (float("inf"), float("-inf")), "stock corrompido a Inf"
    if resultado is True:
        assert despues == pytest.approx(antes + cantidad)


@given(st.sampled_from([float("nan"), float("inf"), float("-inf"), -5.0, 0.0]))
def test_ajuste_extremo_no_corrompe_stock( stock_nuevo):
    """Hipotesis: un ajuste con stock_nuevo NaN/Inf no debe corromper el stock."""
    pid = crear_producto_id(stock_inicial=50.0)
    antes = stock_de(pid)
    database.crear_ajuste_stock(pid, stock_nuevo, "prop-test", 1)
    despues = stock_de(pid)
    assert despues is not None, "stock corrompido a NULL"
    assert despues == despues, "stock corrompido a NaN"
    assert despues not in (float("inf"), float("-inf")), "stock corrompido a Inf"
    if stock_nuevo < 0:
        assert despues == pytest.approx(antes)


# --- 4. Ventas --------------------------------------------------------------

@given(CANTIDAD_VENTA, MONTO)
def test_venta_descuenta_stock_exacto(cantidad, precio):
    """Hipotesis: una venta exitosa descuenta del stock exactamente lo vendido."""
    pid = crear_producto_id(stock_inicial=500.0)
    venta_id, numero, err = database.crear_venta(
        None, "ticket",
        [{"producto_id": pid, "cantidad": cantidad, "precio_unitario": precio}],
        "efectivo", 1,
    )
    assert err is None, err
    assert venta_id is not None
    assert stock_de(pid) == pytest.approx(500.0 - cantidad)


@given(CANTIDAD_VENTA, MONTO)
def test_venta_total_consistente_con_items(cantidad, precio):
    """Hipotesis: el total de la venta guardada es la suma de cantidad * precio."""
    pid = crear_producto_id(stock_inicial=500.0)
    venta_id, numero, err = database.crear_venta(
        None, "factura_c",
        [{"producto_id": pid, "cantidad": cantidad, "precio_unitario": precio}],
        "efectivo", 1,
    )
    assert err is None, err
    completa = database.get_venta_completa(venta_id)
    venta = completa["venta"]
    items = completa["items"]
    total_esperado = sum(i[2] * i[3] for i in items)  # cantidad * precio_unitario
    total_guardado = venta[7]  # columna total de ventas
    assert total_guardado == pytest.approx(total_esperado, abs=0.02)


@given(st.sampled_from([float("nan"), float("inf"), float("-inf")]))
def test_venta_precio_extremo_rechazado( precio):
    """Hipotesis: una venta con precio NaN/Inf se rechaza sin tocar el stock."""
    pid = crear_producto_id(stock_inicial=100.0)
    antes = stock_de(pid)
    venta_id, numero, err = database.crear_venta(
        None, "ticket",
        [{"producto_id": pid, "cantidad": 5.0, "precio_unitario": precio}],
        "efectivo", 1,
    )
    assert err is not None, f"venta con precio {precio} aceptada"
    assert venta_id is None
    assert stock_de(pid) == pytest.approx(antes)


@given(st.sampled_from([float("nan"), float("inf"), float("-inf")]))
def test_venta_cantidad_extrema_rechazada( cantidad):
    """Hipotesis: una venta con cantidad NaN/Inf se rechaza sin tocar el stock."""
    pid = crear_producto_id(stock_inicial=100.0)
    antes = stock_de(pid)
    venta_id, numero, err = database.crear_venta(
        None, "ticket",
        [{"producto_id": pid, "cantidad": cantidad, "precio_unitario": 10.0}],
        "efectivo", 1,
    )
    assert err is not None, f"venta con cantidad {cantidad} aceptada"
    assert venta_id is None
    assert stock_de(pid) == pytest.approx(antes)


# --- 5. Ajustes -------------------------------------------------------------

@given(STOCK_NUEVO)
def test_ajuste_establece_stock_exacto( stock_nuevo):
    """Hipotesis: un ajuste valido deja el stock exactamente en stock_nuevo."""
    pid = crear_producto_id(stock_inicial=50.0)
    assert database.crear_ajuste_stock(pid, stock_nuevo, "prop-test", 1) is True
    assert stock_de(pid) == pytest.approx(stock_nuevo)


# --- 6. Compra -> anulacion -------------------------------------------------

@given(CANTIDAD, MONTO)
def test_anular_compra_restaura_stock_exacto( cantidad, precio):
    """Hipotesis: compra suma stock exacto; anular la revierte exactamente;
    anular dos veces no vuelve a revertir (idempotencia)."""
    prov_id = crear_proveedor_id()
    pid = crear_producto_id(stock_inicial=30.0)
    compra_id = database.crear_compra(
        prov_id,
        [{"producto_id": pid, "cantidad": cantidad, "precio_unitario": precio}],
    )
    assert compra_id is not None
    assert stock_de(pid) == pytest.approx(30.0 + cantidad)
    assert database.anular_compra(compra_id) is True
    assert stock_de(pid) == pytest.approx(30.0)
    assert database.anular_compra(compra_id) is False
    assert stock_de(pid) == pytest.approx(30.0)


# --- 7. Cuenta corriente ----------------------------------------------------

@given(st.floats(min_value=-10, max_value=1e7, allow_nan=False, allow_infinity=False))
def test_pago_cc_consistente( monto):
    """Hipotesis: un pago reduce la deuda exactamente en monto (parcial o
    excedente -> saldo negativo); montos <= 0 se rechazan."""
    cliente_id = crear_cliente_id()
    pid = crear_producto_id(stock_inicial=1000.0)
    venta_id, numero, err = database.crear_venta(
        cliente_id, "factura_c",
        [{"producto_id": pid, "cantidad": 10.0, "precio_unitario": 123.45}],
        "cuenta_corriente", 1,
    )
    assert err is None, err
    deuda = database.get_cuenta_corriente_cliente(cliente_id)
    assert deuda == pytest.approx(1234.5, abs=0.02)
    if monto <= 0:
        assert database.registrar_pago_cc(cliente_id, monto, "efectivo", None, 1) is False
        assert database.get_cuenta_corriente_cliente(cliente_id) == pytest.approx(deuda, abs=0.02)
    else:
        assert database.registrar_pago_cc(cliente_id, monto, "efectivo", None, 1) is True
        saldo = database.get_cuenta_corriente_cliente(cliente_id)
        assert saldo == pytest.approx(deuda - monto, abs=0.02)


# --- 8. Reportes ------------------------------------------------------------

@given(st.integers(min_value=0, max_value=4), STOCK_NUEVO)
def test_reporte_inventario_consistente( n, stock):
    """Hipotesis: el reporte de inventario tiene la misma cantidad de productos
    y el mismo stock total que get_productos, y ningun stock negativo."""
    for _ in range(n):
        crear_producto_id(stock_inicial=stock)
    rep = database.get_reporte_inventario()
    prod = database.get_productos()
    assert len(rep) == len(prod)
    assert sum(r[2] for r in rep) == pytest.approx(sum(p[7] for p in prod))
    assert all(r[2] >= 0 for r in rep)


# --- 9. No-corrupcion en el resto de entry points ---------------------------

@given(st.sampled_from([float("nan"), float("inf"), float("-inf")]))
def test_add_producto_precios_extremos_rechazados(valor):
    """Hipotesis: add_producto rechaza precios/stock NaN/Inf sin crear fila."""
    codigo = nombre_unico()
    for campo in ("stock_minimo", "precio_costo", "precio_venta", "stock_inicial"):
        codigo = nombre_unico()
        kwargs = dict(
            codigo_barras=codigo, nombre="Prop", descripcion=None,
            categoria_id=None, proveedor_id=None, tipo_unidad="Fraccionable",
            stock_minimo=0.0, precio_costo=10.0, precio_venta=20.0, stock_inicial=0.0,
        )
        kwargs[campo] = valor
        assert database.add_producto(**kwargs) is False, f"{campo}={valor} aceptado"
        assert not any(p[1] == codigo for p in database.get_productos())


@given(st.sampled_from([float("nan"), float("inf"), float("-inf")]))
def test_update_producto_precios_extremos_rechazados(valor):
    """Hipotesis: update_producto rechaza precios NaN/Inf y no cambia el producto."""
    pid = crear_producto_id()
    antes = buscar_producto(pid)
    resultado = database.update_producto(
        pid, None, "Prop", None, None, None, "Fraccionable", valor, 10.0, 20.0,
    )
    assert resultado is False
    despues = buscar_producto(pid)
    assert despues == antes


@given(st.sampled_from([float("nan"), float("inf"), float("-inf")]))
def test_servicio_precio_extremo_rechazado(valor):
    """Hipotesis: add/update servicio rechaza precios NaN/Inf."""
    assert database.add_servicio(nombre_unico(), valor) is False
    assert database.add_servicio("Serv Prop", 100.0) is True
    assert database.update_servicio(1, "Serv Prop", valor) is False


@given(st.sampled_from([float("nan"), float("inf"), float("-inf")]))
def test_pago_cc_extremo_rechazado(valor):
    """Hipotesis: registrar_pago_cc rechaza montos NaN/Inf sin tocar el saldo."""
    cliente_id = crear_cliente_id()
    pid = crear_producto_id(stock_inicial=1000.0)
    venta_id, numero, err = database.crear_venta(
        cliente_id, "factura_c",
        [{"producto_id": pid, "cantidad": 10.0, "precio_unitario": 123.45}],
        "cuenta_corriente", 1,
    )
    assert err is None, err
    deuda = database.get_cuenta_corriente_cliente(cliente_id)
    assert database.registrar_pago_cc(cliente_id, valor, "efectivo", None, 1) is False
    assert database.get_cuenta_corriente_cliente(cliente_id) == pytest.approx(deuda, abs=0.02)


@given(st.sampled_from([float("nan"), float("inf"), float("-inf")]))
def test_compra_item_extremo_rechazado(valor):
    """Hipotesis: crear_compra rechaza items con cantidad/precio NaN/Inf."""
    prov_id = crear_proveedor_id()
    pid = crear_producto_id(stock_inicial=30.0)
    for campo in ("cantidad", "precio_unitario"):
        antes = stock_de(pid)
        item = {"producto_id": pid, "cantidad": 5.0, "precio_unitario": 10.0}
        item[campo] = valor
        compra_id = database.crear_compra(prov_id, [item])
        assert compra_id is None, f"compra con {campo}={valor} aceptada"
        assert stock_de(pid) == pytest.approx(antes)


@given(st.sampled_from([float("nan"), float("inf"), float("-inf")]))
def test_abrir_caja_extremo_rechazado(valor):
    """Hipotesis: abrir_caja rechaza saldo NaN/Inf y no deja caja abierta."""
    assert database.abrir_caja(valor, 1) is None
    assert database.get_caja_abierta() is None


@given(st.sampled_from([float("nan"), float("inf"), float("-inf")]))
def test_aumentar_precios_extremo_rechazado(valor):
    """Hipotesis: los aumentos rechazan porcentaje NaN/Inf sin tocar precios."""
    pid = crear_producto_id(precio_venta=100.0)
    assert database.aumentar_precios_por_lista([pid], valor) == 0
    assert buscar_producto(pid)[10] == pytest.approx(100.0)
    assert database.aumentar_precios_proveedor(None, valor) is False
    assert database.aumentar_precios_por_categoria(None, valor, None) == 0


@given(st.sampled_from([float("nan"), float("inf"), float("-inf")]))
def test_orden_detalle_cantidad_extrema_rechazada(valor):
    """Hipotesis: add_orden_detalle rechaza cantidad NaN/Inf y como string."""
    assert database.add_orden_detalle(1, producto_id=1, cantidad=valor) is False
    assert database.add_orden_detalle(1, producto_id=1, cantidad="abc") is False
    assert database.add_orden_detalle(1, producto_id=1, cantidad=2.5) is False  # orden inexistente
