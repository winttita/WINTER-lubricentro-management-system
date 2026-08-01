#!/usr/bin/env python3
"""Genera datos de prueba para todos los módulos del sistema Lubricentro.
Ejecutar con: python3 seed_data.py
Usa la DB configurada en database.DB_NAME (por defecto lubricentro.db)."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
import random

random.seed(42)

# ─── Categorías ───
CATEGORIAS = [
    "Aceites de Motor", "Aceites de Transmisión", "Filtros de Aceite",
    "Filtros de Aire", "Filtros de Combustible", "Lubricantes Industriales",
    "Grasas", "Refrigerantes", "Líquido de Frenos", "Aditivos",
    "Correas", "Bujías", "Amortiguadores", "Pastillas de Freno",
    "Baterías", "Neumáticos", "Iluminación", "Escobillas",
]
for cat in CATEGORIAS:
    database.add_categoria(cat)

# ─── Proveedores ───
PROVEEDORES = [
    ("YPF Lubricantes", "Carlos Rodríguez", "011-4123-4501", "Contado"),
    ("Shell Argentina", "María López", "011-4123-4502", "Cuenta Corriente (30 días)"),
    ("TotalEnergies", "Pedro Gómez", "011-4123-4503", "Cuenta Corriente (15 días)"),
    ("Castrol", "Ana Martínez", "011-4123-4504", "Contado"),
    ("Filtros Mann", "Luis Fernández", "011-4123-4505", "Cuenta Corriente (7 días)"),
    ("Bosch Argentina", "Diego Pérez", "011-4123-4506", "Contado"),
    ("Varta Baterías", "Laura Sánchez", "011-4123-4507", "Cuenta Corriente (15 días)"),
    ("Trenmotivo", "Jorge Díaz", "011-4123-4508", "Otro"),
    ("Filtros Purolator", "Sofía Ruiz", "011-4123-4509", "Contado"),
    ("Lubrax", "Martín Álvarez", "011-4123-4510", "Cuenta Corriente (30 días)"),
]
for p in PROVEEDORES:
    database.add_proveedor(*p)

# ─── Catálogo de productos ───
categorias = database.get_categorias()
provs = database.get_proveedores()
cat_map = {c[1]: c[0] for c in categorias}
prov_map = {p[1]: p[0] for p in provs}

PRODUCTOS = [
    # (codigo_interno, codigo_barras, nombre, desc, cat, prov, tipo, stock_min, p_costo, p_venta, stock)
    ("ACE-001", "7790010000011", "Aceite YPF 5W30 4L", "Aceite sintético para motor naftero", "Aceites de Motor", "YPF Lubricantes", "Entero", 10, 4800, 7200, 45),
    ("ACE-002", "7790010000028", "Aceite YPF 15W40 4L", "Aceite semisintético motor diesel", "Aceites de Motor", "YPF Lubricantes", "Entero", 10, 3200, 5100, 30),
    ("ACE-003", "7790010000035", "Aceite YPF 20W50 4L", "Aceite mineral para motor", "Aceites de Motor", "YPF Lubricantes", "Entero", 8, 2800, 4500, 25),
    ("ACE-004", "7790020000012", "Aceite Shell Helix HX7 5W40 4L", "Aceite sintético premium", "Aceites de Motor", "Shell Argentina", "Entero", 8, 6200, 9500, 20),
    ("ACE-005", "7790020000029", "Aceite Shell Helix HX5 20W50 4L", "Aceite mineral multigrado", "Aceites de Motor", "Shell Argentina", "Entero", 10, 3500, 5500, 35),
    ("ACE-006", "7790030000013", "Aceite Total Quartz 9000 5W40 4L", "Aceite sintético de alto rendimiento", "Aceites de Motor", "TotalEnergies", "Entero", 5, 5800, 8900, 15),
    ("ACE-007", "7790030000020", "Aceite Total Quartz 7000 10W40 4L", "Aceite semisintético", "Aceites de Motor", "TotalEnergies", "Entero", 10, 3800, 5900, 22),
    ("ACE-008", "7790040000014", "Aceite Castrol EDGE 5W30 4L", "Aceite sintético con Fluid TITANIUM", "Aceites de Motor", "Castrol", "Entero", 5, 6500, 9900, 12),
    ("ACE-009", "7790040000021", "Aceite Castrol Magnatec 10W40 4L", "Aceite semisintético", "Aceites de Motor", "Castrol", "Entero", 8, 4200, 6500, 18),
    ("ACE-010", "7790100000010", "Aceite Lubrax Top Turbo 15W40 4L", "Aceite para motor diesel turbo", "Aceites de Motor", "Lubrax", "Entero", 6, 3000, 4800, 28),
    ("ATF-001", "7790010000103", "Aceite YPF ATF DEXRON III 1L", "Aceite para transmisiones automáticas", "Aceites de Transmisión", "YPF Lubricantes", "Entero", 5, 1800, 2900, 20),
    ("ATF-002", "7790010000110", "Aceite YPF ATF DEXRON VI 1L", "Aceite sintético para transmisiones", "Aceites de Transmisión", "YPF Lubricantes", "Entero", 5, 2200, 3500, 15),
    ("FIL-001", "7790050000015", "Filtro de Aceite Mann W712/80", "Filtro de aceite para VW/Ford", "Filtros de Aceite", "Filtros Mann", "Entero", 20, 850, 1500, 80),
    ("FIL-002", "7790050000022", "Filtro de Aceite Mann W914/2", "Filtro de aceite para Renault", "Filtros de Aceite", "Filtros Mann", "Entero", 20, 750, 1300, 65),
    ("FIL-003", "7790050000039", "Filtro de Aceite Mann W610/3", "Filtro de aceite para Toyota/Honda", "Filtros de Aceite", "Filtros Mann", "Entero", 15, 900, 1600, 55),
    ("FIL-004", "7790060000016", "Filtro de Aceite Bosch 0986AF0063", "Filtro de aceite universal", "Filtros de Aceite", "Bosch Argentina", "Entero", 25, 700, 1200, 100),
    ("FIL-005", "7790060000023", "Filtro de Aire Bosch 0986AF3020", "Filtro de aire para motor", "Filtros de Aire", "Bosch Argentina", "Entero", 15, 1100, 1900, 40),
    ("FIL-006", "7790060000030", "Filtro de Combustible Bosch 0986AF8127", "Filtro naftero", "Filtros de Combustible", "Bosch Argentina", "Entero", 10, 950, 1700, 35),
    ("FIL-007", "7790090000014", "Filtro Purolator PL14615", "Filtro de aceite universal", "Filtros de Aceite", "Filtros Purolator", "Entero", 15, 600, 1100, 90),
    ("FIL-008", "7790090000021", "Filtro Purolator A15106", "Filtro de aire", "Filtros de Aire", "Filtros Purolator", "Entero", 12, 850, 1500, 45),
    ("GRASA-001", "7790010000202", "Grasa YPF EP-2 1Kg", "Grasa multiuso con aditivos EP", "Grasas", "YPF Lubricantes", "Entero", 10, 1200, 2000, 30),
    ("GRASA-002", "7790100000027", "Grasa Lubrax NLGI 2 1Kg", "Grasa para rodamientos", "Grasas", "Lubrax", "Entero", 8, 1100, 1900, 25),
    ("REFRI-001", "7790010000301", "Refrigerante YPF 50/50 4L", "Líquido refrigerante listo para usar", "Refrigerantes", "YPF Lubricantes", "Entero", 10, 1500, 2500, 40),
    ("REFRI-002", "7790020000104", "Refrigerante Shell 50/50 4L", "Líquido refrigerante concentrado", "Refrigerantes", "Shell Argentina", "Entero", 8, 1800, 2900, 25),
    ("FRENO-001", "7790010000400", "Líquido de Frenos YPF DOT 4 500ml", "Líquido de frenos alta performance", "Líquido de Frenos", "YPF Lubricantes", "Entero", 8, 900, 1600, 35),
    ("FRENO-002", "7790020000203", "Líquido de Frenos Shell DOT 4 500ml", "Líquido de frenos premium", "Líquido de Frenos", "Shell Argentina", "Entero", 6, 1000, 1800, 28),
    ("ADIT-001", "7790010000509", "Aditivo YPF Limpia Inyectores 300ml", "Aditivo limpiador de inyectores", "Aditivos", "YPF Lubricantes", "Entero", 10, 600, 1100, 50),
    ("ADIT-002", "7790010000516", "Aditivo YPF Estabilizador de Combustible 300ml", "Estabilizador para combustible", "Aditivos", "YPF Lubricantes", "Entero", 5, 700, 1300, 30),
    ("CORR-001", "7790060000047", "Correa de Distribución Bosch 530055610", "Correa dentada para motor 1.6", "Correas", "Bosch Argentina", "Entero", 5, 2500, 4200, 10),
    ("CORR-002", "7790060000054", "Correa Poly-V Bosch 6PK1700", "Correa de accesorios", "Correas", "Bosch Argentina", "Entero", 8, 800, 1400, 25),
    ("BUJI-001", "7790060000061", "Bujía Bosch Super WR7DC", "Bujía de encendido estándar", "Bujías", "Bosch Argentina", "Entero", 20, 350, 650, 100),
    ("BUJI-002", "7790060000078", "Bujía Bosch Platinum WR7DP", "Bujía de platino", "Bujías", "Bosch Argentina", "Entero", 15, 700, 1300, 60),
    ("AMORT-001", "7790080000010", "Amortiguador Delantero Trenmotivo", "Amortiguador gas para Fiat Palio", "Amortiguadores", "Trenmotivo", "Entero", 4, 8500, 14000, 8),
    ("AMORT-002", "7790080000027", "Amortiguador Trasero Trenmotivo", "Amortiguador gas para Fiat Palio", "Amortiguadores", "Trenmotivo", "Entero", 4, 8000, 13500, 8),
    ("PAS-001", "7790050000046", "Pastillas de Freno Mann MP802", "Pastilla de freno delantero", "Pastillas de Freno", "Filtros Mann", "Entero", 5, 3500, 5800, 15),
    ("BAT-001", "7790070000010", "Batería Varta Blue Dynamic 60Ah", "Batería 12V 60Ah 540A", "Baterías", "Varta Baterías", "Entero", 3, 18000, 28000, 10),
    ("BAT-002", "7790070000027", "Batería Varta Blue Dynamic 75Ah", "Batería 12V 75Ah 680A", "Baterías", "Varta Baterías", "Entero", 3, 22000, 34000, 7),
    ("BAT-003", "7790070000034", "Batería Varta Silver Dynamic 95Ah", "Batería 12V 95Ah 800A AGM", "Baterías", "Varta Baterías", "Entero", 2, 35000, 52000, 5),
    ("LUB-001", "7790010000608", "Lubricante YPF Industrial EP-68 20L", "Aceite hidráulico 20L", "Lubricantes Industriales", "YPF Lubricantes", "Entero", 5, 12000, 18500, 8),
    ("LUB-002", "7790010000615", "Lubricante YPF Industrial EP-100 20L", "Aceite para engranajes 20L", "Lubricantes Industriales", "YPF Lubricantes", "Entero", 4, 13500, 21000, 6),
    ("GRASA-003", "7790010000707", "Grasa YPF G-EP1 20Kg", "Grasa industrial para rodamientos 20Kg", "Grasas", "YPF Lubricantes", "Entero", 2, 18000, 28000, 3),
]

for prod in PRODUCTOS:
    cod_int, cod_bar, nom, desc, cat_nom, prov_nom, tipo, smin, costo, venta, stock = prod
    cid = cat_map[cat_nom]
    pid = prov_map[prov_nom]
    try:
        database.add_producto(cod_int, cod_bar, nom, desc, cid, pid, tipo, smin, costo, venta, stock_inicial=stock)
    except Exception as e:
        print(f"  Error al crear {cod_int}: {e}")

print("Productos creados:", len(database.get_productos()))

# ─── Clientes ───
CLIENTES = [
    ("Juan Pérez", "011-4567-8901", "juanperez@gmail.com"),
    ("María García", "011-4567-8902", "mariagarcia@hotmail.com"),
    ("Carlos Martínez", "011-4567-8903", "carlosmtz@yahoo.com"),
    ("Ana Rodríguez", "011-4567-8904", "anarod@gmail.com"),
    ("Luis Fernández", "011-4567-8905", "luisfdez@outlook.com"),
    ("Laura Sánchez", "011-4567-8906", "laurita.sanchez@gmail.com"),
    ("Diego López", "011-4567-8907", "diego.lopez@empresa.com"),
    ("Sofía Díaz", "011-4567-8908", None),
    ("Martín González", "011-4567-8909", "marting@fibertel.com"),
    ("Valentina Álvarez", "011-4567-8910", None),
    ("Facundo Ruiz", "011-4567-8911", "facundo.ruiz@gmail.com"),
    ("Camila Torres", "011-4567-8912", "camila.torres@hotmail.com"),
    ("Nicolás Castro", "011-4567-8913", None),
    ("Florencia Vargas", "011-4567-8914", "flor.vargas@gmail.com"),
    ("Alejandro Ríos", "011-4567-8915", "alejandro.rios@empresa.com"),
    # Clientes empresa
    ("Transportes El Rápido SRL", "011-4000-1001", "compras@transelrapido.com"),
    ("Taller Mecánico El Turco", "011-4000-1002", "elturco@taller.com"),
    ("Taxi Premium SA", "011-4000-1003", "admin@taxipremium.com"),
    ("Fletes del Oeste", "011-4000-1004", "fletesoeste@gmail.com"),
    ("Municipalidad de San Miguel", "011-4000-1005", "compras@msanmiguel.gov.ar"),
]
for c in CLIENTES:
    database.add_cliente(*c)

clientes = database.get_clientes()
print("Clientes creados:", len(clientes))

# ─── Vehículos ───
VEHICULOS = [
    # (cliente_id, patente, marca, modelo, anio)
    (1, "AB123CD", "Ford", "Focus", 2019),
    (2, "BC234DE", "Volkswagen", "Gol Trend", 2018),
    (2, "CD345EF", "Renault", "Sandero", 2021),
    (3, "DE456FG", "Fiat", "Palio", 2017),
    (3, "EF567GH", "Toyota", "Corolla", 2022),
    (4, "FG678HI", "Chevrolet", "Cruze", 2020),
    (5, "GH789IJ", "Ford", "Ranger", 2021),
    (6, "HI890JK", "Volkswagen", "Amarok", 2022),
    (7, "IJ901KL", "Nissan", "Sentra", 2019),
    (8, "JK012LM", "Honda", "Civic", 2020),
    (9, "KL123MN", "Fiat", "Cronos", 2022),
    (9, "LM234NO", "Peugeot", "Partner", 2021),
    (10, "MN345OP", "Chevrolet", "S10", 2020),
    (11, "NO456PQ", "Toyota", "Hilux", 2023),
    (16, "OP567QR", "Iveco", "Daily", 2020),
    (16, "PQ678RS", "Mercedes Benz", "Sprinter", 2021),
    (17, "QR789ST", "Ford", "Transit", 2019),
    (18, "RS890TU", "Toyota", "Hilux", 2022),
    (19, "ST901UV", "Volkswagen", "Crafter", 2020),
    (20, "TU012VW", "Ford", "Ranger", 2023),
]
for v in VEHICULOS:
    database.add_vehiculo(*v)

print("Vehículos creados:", len(database.get_vehiculos()))

# ─── Servicios ───
SERVICIOS = [
    ("Cambio de Aceite (hasta 4L)", 3500),
    ("Cambio de Aceite (hasta 6L)", 4500),
    ("Cambio de Filtro de Aceite", 1500),
    ("Cambio de Filtro de Aire", 1200),
    ("Cambio de Filtro de Combustible", 1800),
    ("Diagnóstico Computarizado", 5000),
    ("Escaneo de Motor", 3000),
    ("Alineación y Balanceo", 8000),
    ("Balanceo de Ruedas (x2)", 4000),
    ("Alineación de Dirección", 5000),
    ("Cambio de Pastillas de Freno (eje)", 12000),
    ("Rectificación de Discos (x2)", 15000),
    ("Cambio de Amortiguadores (par)", 25000),
    ("Cambio de Bujías (kit 4)", 6000),
    ("Cambio de Correa de Distribución", 35000),
    ("Cambio de Batería", 5000),
    ("Lavado de Inyectores", 8000),
    ("Cambio de Líquido de Frenos", 4000),
    ("Cambio de Refrigerante", 3500),
    ("Rotación de Neumáticos", 3000),
    ("Revisión General 50 puntos", 15000),
    ("Limpieza de Filtro de Aire", 800),
    ("Engrase General", 2500),
    ("Cambio de Neumático (mano de obra)", 2000),
]
for s in SERVICIOS:
    database.add_servicio(*s)

print("Servicios creados:", len(database.get_servicios()))

# ─── Órdenes de Servicio ───
# Crear algunas órdenes con productos y servicios
prods = database.get_productos()
servicios = database.get_servicios()
clientes = database.get_clientes()
vehiculos = database.get_vehiculos()

ORDENES = [
    (1, 1, [("producto", 1, 4), ("servicio", 1, 1)], "Cambio de aceite y filtro"),
    (3, 3, [("producto", 2, 4), ("servicio", 1, 1), ("servicio", 2, 1)], "Cambio aceite + filtro + servicio"),
    (5, 5, [("servicio", 10, 1), ("servicio", 8, 1)], "Alineación y balanceo"),
    (7, 7, [("producto", 28, 1), ("servicio", 14, 1)], "Cambio bujías"),
    (9, 9, [("servicio", 15, 1), ("servicio", 12, 1)], "Cambio distribución + refrigerante"),
    (16, 15, [("producto", 1, 8), ("producto", 2, 8), ("servicio", 1, 1)], "Mantenimiento flota"),
    (17, 17, [("producto", 4, 4), ("servicio", 1, 1)], "Cambio aceite flota taller"),
]

print("Órdenes creadas:", end=" ")
ord_count = 0
for cli_idx, veh_idx, items, obs in ORDENES:
    cid = clientes[cli_idx - 1][0]
    vid = vehiculos[veh_idx - 1][0] if veh_idx else None
    oid = database.add_orden_servicio(cid, vid)
    if oid:
        ord_count += 1
        for tipo, idx, cant in items:
            if tipo == "producto":
                pid = prods[idx - 1][0]
                database.add_orden_detalle(oid, producto_id=pid, cantidad=cant)
            elif tipo == "servicio":
                sid = servicios[idx - 1][0]
                database.add_orden_detalle(oid, servicio_id=sid, cantidad=cant)
print(ord_count)

# ─── Ventas ───
# Abrir caja primero
database.abrir_caja(50000.0, 1)

VENTAS = [
    # (items, tipo_comprobante, metodo_pago, cliente_id)
    ([("producto", 1, 2), ("producto", 3, 1)], "ticket", "efectivo", None),
    ([("producto", 2, 3), ("producto", 13, 1)], "ticket", "efectivo", None),
    ([("producto", 4, 2), ("producto", 14, 1), ("producto", 16, 1)], "factura_a", "cuenta_corriente", 1),
    ([("producto", 5, 4), ("producto", 33, 1)], "ticket", "tarjeta", None),
    ([("producto", 6, 2), ("producto", 7, 2)], "factura_b", "cuenta_corriente", 3),
    ([("producto", 1, 6), ("producto", 2, 4), ("producto", 13, 3)], "factura_a", "cuenta_corriente", 16),
    ([("producto", 8, 1), ("producto", 34, 1), ("producto", 35, 1)], "factura_b", "cuenta_corriente", 5),
    ([("producto", 9, 3), ("producto", 18, 2)], "ticket", "efectivo", None),
    ([("producto", 10, 2), ("producto", 22, 2)], "ticket", "tarjeta", None),
    ([("producto", 37, 1), ("producto", 38, 2)], "factura_a", "cuenta_corriente", 20),
    ([("producto", 22, 3), ("producto", 30, 1)], "ticket", "efectivo", None),
    ([("producto", 1, 1), ("producto", 13, 1)], "ticket", "tarjeta", None),
]

ventas_ok = 0
for items_def, tipo, metodo, cli_id in VENTAS:
    items = []
    for tipo_item, idx, cant in items_def:
        pid = prods[idx - 1][0]
        pv = float(prods[idx - 1][11])
        items.append({"producto_id": pid, "cantidad": cant, "precio_unitario": pv})
    vid_or_none = cli_id if cli_id else None
    venta_id, comp, err = database.crear_venta(
        vid_or_none, tipo, items, metodo, 1
    )
    if venta_id:
        ventas_ok += 1
print(f"Ventas creadas: {ventas_ok}")

# ─── Compras a Proveedores ───
# Reponer stock de los más vendidos
COMPRAS = [
    (1, [(1, 20, 4800), (2, 15, 3200), (3, 12, 2800)]),
    (2, [(4, 10, 6200), (5, 20, 3500)]),
    (4, [(34, 50, 350), (35, 30, 700)]),
    (5, [(13, 30, 850), (14, 25, 750), (15, 20, 900)]),
    (7, [(37, 8, 18000), (38, 5, 22000), (39, 3, 35000)]),
]

compras_ok = 0
for prov_idx, items_def in COMPRAS:
    prov_id = provs[prov_idx - 1][0]
    items = []
    for prod_idx, cant, p_unit in items_def:
        pid = prods[prod_idx - 1][0]
        items.append({"producto_id": pid, "cantidad": cant, "precio_unitario": p_unit})
    compra_id = database.crear_compra(prov_id, items)
    if compra_id:
        compras_ok += 1
print(f"Compras creadas: {compras_ok}")

# ─── Cerrar caja ───
caja = database.get_caja_abierta()
if caja:
    database.cerrar_caja(caja[0], 120000.0, 1)
    print("Caja cerrada")

# ─── Abrir nueva caja para seguir operando ───
database.abrir_caja(80000.0, 1)
caja_nueva = database.get_caja_abierta()
if caja_nueva:
    print(f"Caja nueva abierta: ID={caja_nueva[0]}, saldo=${caja_nueva[2]:.2f}")

# ─── Pagos de cuenta corriente ───
database.registrar_pago_cc(1, 15000.0, "efectivo", "Pago parcial", 1)
database.registrar_pago_cc(3, 8500.0, "transferencia", "Pago total", 1)
database.registrar_pago_cc(16, 45000.0, "cheque", "Pago parcial flota", 1)

print()
print("=== DATOS DE PRUEBA GENERADOS ===")
print(f"Categorías: {len(database.get_categorias())}")
print(f"Proveedores: {len(database.get_proveedores())}")
print(f"Productos: {len(database.get_productos())}")
print(f"Clientes: {len(database.get_clientes())}")
print(f"Vehículos: {len(database.get_vehiculos())}")
print(f"Servicios: {len(database.get_servicios())}")
