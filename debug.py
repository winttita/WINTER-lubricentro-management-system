import tempfile, os, sys
sys.path.insert(0, '.')
import database
from database import get_connection, init_db, add_categoria, add_proveedor, add_producto, add_movimiento

fd, path = tempfile.mkstemp(suffix='.db')
os.close(fd)
database.DB_NAME = path
init_db()
add_categoria('Aceites')
add_proveedor('YPF','Juan','123','Contado')
cat_id = database.get_categorias()[0][0]
prov_id = database.get_proveedores()[0][0]
add_producto('P2','CB002','Producto A','', cat_id, prov_id, 'Entero',0,10.0,121.0,10)
conn = get_connection()
# simulate crear_venta up to movements
cliente_id = None
tipo_comprobante = 'factura_a'
items = [{'producto_id': 1, 'cantidad': 1, 'precio_unitario': 121.0}]
metodo_pago = 'efectivo'
usuario_id = 1
# validate items
if not items:
    print('no items')
if not isinstance(items, list):
    print('items not list')
for item in items:
    if not isinstance(item, dict):
        print('item not dict')
    if 'producto_id' not in item or 'cantidad' not in item or 'precio_unitario' not in item:
        print('missing keys')
    row = conn.execute('SELECT stock_actual, nombre FROM productos WHERE id = ? AND activo = 1', (item['producto_id'],)).fetchone()
    if not row:
        print('product not found or inactive')
        sys.exit(1)
    stock_actual = float(row[0])
    nombre = row[1]
    cantidad = float(item['cantidad'])
    print(f'product {nombre} stock {stock_actual}, requesting {cantidad}')
    if stock_actual < cantidad:
        print('stock insufficient')
        sys.exit(1)
# calculate totals
total = sum(float(item['cantidad']) * float(item['precio_unitario']) for item in items)
if tipo_comprobante == 'factura_a':
    subtotal = round(total / 1.21, 2)
    iva = round(total - subtotal, 2)
else:
    subtotal = round(total, 2)
    iva = 0.0
print(f'total {total}, subtotal {subtotal}, iva {iva}')
# get next numero
punto_venta = '0001'
numero = conn.execute("SELECT MAX(numero_comprobante) FROM ventas WHERE tipo_comprobante = ? AND punto_venta = ?", (tipo_comprobante, punto_venta)).fetchone()[0]
if numero is None:
    numero = 0
numero += 1
print(f'numero comprobante: {numero}')
# insert venta
cursor = conn.execute("""
    INSERT INTO ventas (cliente_id, tipo_comprobante, punto_venta, numero_comprobante,
                      subtotal, iva, total, metodo_pago, usuario_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (cliente_id, tipo_comprobante, punto_venta, numero,
      subtotal, iva, total, metodo_pago, usuario_id))
venta_id = cursor.lastrowid
print(f'venta_id: {venta_id}')
# insert items and movimientos
for item in items:
    cantidad = float(item['cantidad'])
    precio_unitario = float(item['precio_unitario'])
    subtotal_item = round(cantidad * precio_unitario, 2)
    conn.execute("""
        INSERT INTO venta_items (venta_id, producto_id, cantidad, precio_unitario, subtotal)
        VALUES (?, ?, ?, ?, ?)
    """, (venta_id, item['producto_id'], cantidad, precio_unitario, subtotal_item))
    print(f'about to call add_movimiento for product {item[\"producto_id\"]}, cantidad {cantidad}')
    # call add_movimiento
    if not add_movimiento(item['producto_id'], 'venta', cantidad, f'Venta #{venta_id}'):
        print('add_movimiento returned False')
        # let's check stock again
        row2 = conn.execute('SELECT stock_actual FROM productos WHERE id = ?', (item['producto_id'],)).fetchone()
        print(f'stock after attempt: {row2[0] if row2 else None}')
        break
else:
    print('all movements succeeded')
    conn.commit()
    print('committed')
conn.close()