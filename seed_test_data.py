#!/usr/bin/env python3
"""Genera datos de prueba para verificación manual de v0.5.0.
Ejecutar: python3 seed_test_data.py
Usa la DB configurada en database.DB_NAME (lubricentro.db)."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
from datetime import datetime, timedelta
import random

random.seed(42)

database.init_db()


def print_header(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")


print_header("POBLANDO BASE PARA PRUEBAS v0.5.0")

CATEGORIAS = [
    "Aceites de Motor", "Filtros", "Lubricantes Industriales",
    "Grasas", "Refrigerantes", "Líquido de Frenos",
    "Correas", "Bujías", "Pastillas de Freno", "Baterías",
]
for cat in CATEGORIAS:
    database.add_categoria(cat)

PROVEEDORES = [
    ("YPF Lubricantes", "Carlos", "011-4123-4501", "Contado"),
    ("Bosch Argentina", "Diego", "011-4123-4506", "Contado"),
    ("Filtros Mann", "Luis", "011-4123-4505", "Cuenta Corriente (15 días)"),
    ("Varta Baterías", "Laura", "011-4123-4507", "Cuenta Corriente (30 días)"),
]
for p in PROVEEDORES:
    database.add_proveedor(*p)

categorias = {c[1]: c[0] for c in database.get_categorias()}
provs = {p[1]: p[0] for p in database.get_proveedores()}

PRODUCTOS = [
    # (codigo_barras, nombre, desc, cat, prov, tipo, stock_min, p_costo, p_venta, stock)
    ("7790010000011", "Aceite YPF 5W30 4L", "Sintético naftero", "Aceites de Motor", "YPF Lubricantes", "Entero", 10, 4800, 7200, 45),
    ("7790010000028", "Aceite YPF 15W40 4L", "Semisintético diesel", "Aceites de Motor", "YPF Lubricantes", "Entero", 10, 3200, 5100, 30),
    ("7790060000061", "Bujía Bosch Super WR7DC", "Estándar", "Bujías", "Bosch Argentina", "Entero", 20, 350, 650, 100),
    ("7790060000078", "Bujía Bosch Platinum WR7DP", "Platino", "Bujías", "Bosch Argentina", "Entero", 15, 700, 1300, 60),
    ("7790050000015", "Filtro Aceite Mann W712/80", "VW/Ford", "Filtros", "Filtros Mann", "Entero", 20, 850, 1500, 80),
    ("7790050000022", "Filtro Aceite Mann W914/2", "Renault", "Filtros", "Filtros Mann", "Entero", 20, 750, 1300, 65),
    ("7790070000010", "Batería Varta Blue 60Ah", "12V 60Ah", "Baterías", "Varta Baterías", "Entero", 3, 18000, 28000, 10),
    ("7790070000027", "Batería Varta Blue 75Ah", "12V 75Ah", "Baterías", "Varta Baterías", "Entero", 3, 22000, 34000, 7),
    ("7790010000301", "Refrigerante YPF 50/50 4L", "Listo para usar", "Refrigerantes", "YPF Lubricantes", "Entero", 10, 1500, 2500, 40),
    ("7790010000400", "Líquido Frenos YPF DOT4 500ml", "Alta performance", "Líquido de Frenos", "YPF Lubricantes", "Entero", 8, 900, 1600, 35),
    ("7790010000707", "Grasa YPF G-EP1 20Kg", "Industrial 20Kg", "Grasas", "YPF Lubricantes", "Entero", 2, 18000, 28000, 3),
    ("7790010000608", "Lubricante YPF EP-68 20L", "Hidráulico 20L", "Lubricantes Industriales", "YPF Lubricantes", "Entero", 5, 12000, 18500, 8),
    ("7790060000047", "Correa Distrib Bosch 530055610", "Motor 1.6", "Correas", "Bosch Argentina", "Entero", 5, 2500, 4200, 10),
    ("7790050000046", "Pastillas Freno Mann MP802", "Delantero", "Pastillas de Freno", "Filtros Mann", "Entero", 5, 3500, 5800, 15),
    ("7790010000509", "Aditivo YPF Limpia Inyectores 300ml", "Limpia inyectores", "Refrigerantes", "YPF Lubricantes", "Entero", 10, 600, 1100, 50),
]
for prod in PRODUCTOS:
    cod_bar, nom, desc, cat_nom, prov_nom, tipo, smin, costo, venta, stock = prod
    cid = categorias[cat_nom]
    pid = provs[prov_nom]
    database.add_producto(cod_bar, nom, desc, cid, pid, tipo, smin, costo, venta, stock_inicial=stock)
prods = database.get_productos()
print(f"Productos creados: {len(prods)}")

CLIENTES = [
    ("Juan Pérez", "011-4567-8901", "juan@mail.com"),
    ("María García", "011-4567-8902", "maria@mail.com"),
    ("Transportes El Rápido SRL", "011-4000-1001", "compras@transelrapido.com"),
    ("Taller Mecánico El Turco", "011-4000-1002", "elturco@taller.com"),
    ("Carlos Martínez", "011-4567-8903", None),
]
for c in CLIENTES:
    database.add_cliente(*c)
clientes = database.get_clientes()
print(f"Clientes creados: {len(clientes)}")

VEHICULOS = [
    (1, "AB123CD", "Ford", "Focus", 2019),
    (2, "BC234DE", "VW", "Gol Trend", 2020),
    (3, "CD345EF", "Iveco", "Daily", 2021),
    (4, "DE456FG", "Ford", "Transit", 2019),
]
for v in VEHICULOS:
    database.add_vehiculo(*v)
print(f"Vehículos creados: {len(database.get_vehiculos())}")

SERVICIOS = [
    ("Cambio de Aceite (hasta 4L)", 3500),
    ("Cambio de Filtro de Aceite", 1500),
    ("Diagnóstico Computarizado", 5000),
    ("Alineación y Balanceo", 8000),
    ("Cambio de Pastillas de Freno (eje)", 12000),
]
for s in SERVICIOS:
    database.add_servicio(*s)
servs = database.get_servicios()
print(f"Servicios creados: {len(servs)}")


print_header("CREANDO VENTAS (con caja abierta)")
database.abrir_caja(50000.0, 1)

p = {pr[0]: {"id": pr[0], "precio": pr[10]} for pr in prods}
pidx = list(p.keys())

ventas_ok = 0
ventas_def = [
    ([pidx[0], pidx[1], pidx[4]], "ticket", "efectivo", None),
    ([pidx[2], pidx[3]], "ticket", "tarjeta", None),
    ([pidx[5], pidx[6]], "factura_a", "cuenta_corriente", 1),
    ([pidx[0], pidx[2], pidx[4]], "ticket", "efectivo", None),
    ([pidx[1], pidx[3], pidx[5]], "factura_b", "cuenta_corriente", 3),
    ([pidx[7], pidx[8]], "ticket", "efectivo", None),
    ([pidx[9], pidx[10]], "ticket", "tarjeta", None),
    ([pidx[0], pidx[1]], "factura_a", "cuenta_corriente", 5),
    ([pidx[11], pidx[12]], "ticket", "efectivo", None),
    ([pidx[13], pidx[14]], "factura_b", "cuenta_corriente", 4),
    ([pidx[0], pidx[1], pidx[2]], "ticket", "efectivo", None),
    ([pidx[3], pidx[4]], "ticket", "efectivo", None),
]
for prod_ids, tipo, metodo, cli_id in ventas_def:
    items = [{"producto_id": pid, "cantidad": 1, "precio_unitario": p[pid]["precio"]} for pid in prod_ids]
    vid = cli_id if cli_id else None
    venta_id, comp, err = database.crear_venta(vid, tipo, items, metodo, 1)
    if venta_id:
        ventas_ok += 1
print(f"Ventas creadas: {ventas_ok}")


print_header("CREANDO COMPRAS A PROVEEDORES")
proveedores = database.get_proveedores()
compras_ok = 0
compras_def = [
    (0, [(0, 20), (1, 15)]),
    (0, [(8, 10), (9, 8)]),
    (1, [(2, 50), (3, 30)]),
    (2, [(4, 30), (5, 25)]),
    (3, [(6, 8), (7, 5)]),
    (0, [(10, 3), (11, 5)]),
    (1, [(12, 10), (13, 10)]),
]
for prov_idx, items_def in compras_def:
    prov_id = proveedores[prov_idx][0]
    items = [{"producto_id": pidx[prod_idx], "cantidad": cant, "precio_unitario": p[pidx[prod_idx]]["precio"]} for prod_idx, cant in items_def]
    compra_id = database.crear_compra(prov_id, items)
    if compra_id:
        compras_ok += 1
print(f"Compras creadas: {compras_ok}")


print_header("REGISTRANDO PAGOS CC")
database.registrar_pago_cc(1, 15000.0, "efectivo", "Pago parcial", 1)
database.registrar_pago_cc(3, 30000.0, "transferencia", "Pago total factura", 1)
database.registrar_pago_cc(5, 5000.0, "efectivo", "Seña", 1)
print("Pagos CC registrados")


print_header("CREANDO ORDENES DE SERVICIO")
ord_count = 0
ordenes_def = [
    (0, 0, [(0, 4, 1), (1, 0, 1)], "Cambio aceite + filtro"),
    (4, 2, [(2, 0, 1), (3, 0, 1)], "Diagnóstico + alineación"),
    (0, 0, [(4, 4, 1), (1, 0, 1)], "Filtro + cambio aceite"),
]
for cli_idx, veh_idx, items_def, obs in ordenes_def:
    cid = clientes[cli_idx][0] if cli_idx < len(clientes) else clientes[0][0]
    vid = database.get_vehiculos()[veh_idx][0] if veh_idx < len(database.get_vehiculos()) else None
    oid = database.add_orden_servicio(cid, vid)
    if oid:
        for prod_idx, serv_idx, cant in items_def:
            if prod_idx >= 0:
                database.add_orden_detalle(oid, producto_id=pidx[prod_idx], cantidad=cant)
            if serv_idx >= 0:
                database.add_orden_detalle(oid, servicio_id=servs[serv_idx][0], cantidad=cant)
        ord_count += 1
print(f"Órdenes creadas: {ord_count}")


print_header("CERRANDO Y REABRIENDO CAJA")
caja = database.get_caja_abierta()
if caja:
    database.cerrar_caja(caja[0], 250000.0, 1)
    print("Caja cerrada con saldo $250,000.00")
database.abrir_caja(80000.0, 1)
caja_nueva = database.get_caja_abierta()
if caja_nueva:
    print(f"Caja nueva abierta: ID={caja_nueva[0]}, saldo=${caja_nueva[2]:.2f}")


print_header("VERIFICACION FINAL")
print(f"Categorías:     {len(database.get_categorias())}")
print(f"Proveedores:    {len(database.get_proveedores())}")
print(f"Productos:      {len(database.get_productos())}")
print(f"Clientes:       {len(database.get_clientes())}")
print(f"Vehículos:      {len(database.get_vehiculos())}")
print(f"Servicios:      {len(database.get_servicios())}")
print(f"Ventas creadas: {ventas_ok}")
print(f"Compras creadas: {compras_ok}")
print()
print("Script completado. Base lista para pruebas manuales.")
