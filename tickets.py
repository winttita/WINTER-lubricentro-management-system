import os
from datetime import datetime

PUNTO_VENTA = "0001"
IVA_PORCENTAJE = 0.21

def formatear_monto(monto):
    """Formatea un monto con 2 decimales."""
    return f"{float(monto):.2f}"

def generar_ticket_texto(venta, items, cliente=None):
    """
    Genera el texto de un ticket simple para impresora térmica 80mm.
    """
    lineas = []
    ancho = 40
    
    # Encabezado
    lineas.append("=" * ancho)
    lineas.append("    LUBRICENTRO WINTER".center(ancho))
    lineas.append("=" * ancho)
    lineas.append(f"Ticket #{venta['tipo_comprobante'].upper()} {venta['punto_venta']}-{venta['numero_comprobante']:08d}")
    lineas.append(f"Fecha: {venta['creado_en']}")
    lineas.append("-" * ancho)
    
    # Cliente
    if cliente and cliente.get('nombre'):
        lineas.append(f"Cliente: {cliente['nombre']}")
        if cliente.get('telefono'):
            lineas.append(f"Tel: {cliente['telefono']}")
    else:
        lineas.append("Cliente: Consumidor Final")
    lineas.append("-" * ancho)
    
    # Items
    lineas.append(f"{'Cant':>4} {'Producto':<24} {'Subtotal':>10}")
    lineas.append("-" * ancho)
    for item in items:
        nombre = item['producto_nombre'][:24]
        cantidad = formatear_monto(item['cantidad'])
        subtotal = formatear_monto(item['subtotal'])
        lineas.append(f"{cantidad:>4} {nombre:<24} {subtotal:>10}")
        lineas.append(f"     {item['precio_unitario']:.2f} x {cantidad}")
    lineas.append("-" * ancho)
    
    # Totales
    lineas.append(f"{'Subtotal:':<30} {formatear_monto(venta['subtotal']):>10}")
    lineas.append(f"{'IVA (21%):':<30} {formatear_monto(venta['iva']):>10}")
    lineas.append(f"{'TOTAL:':<30} {formatear_monto(venta['total']):>10}")
    lineas.append("=" * ancho)
    
    # Método de pago
    metodo_pago_nombre = {
        'efectivo': 'Efectivo',
        'tarjeta_debito': 'Tarjeta Débito',
        'tarjeta_credito': 'Tarjeta Crédito',
        'transferencia': 'Transferencia',
        'cuenta_corriente': 'Cuenta Corriente'
    }.get(venta['metodo_pago'], venta['metodo_pago'])
    lineas.append(f"Pago: {metodo_pago_nombre}")
    
    if venta['metodo_pago'] == 'efectivo':
        lineas.append(f"Recibido: $_______")
        lineas.append(f"Vuelto: $_______")
    
    lineas.append("=" * ancho)
    lineas.append("Gracias por su compra!".center(ancho))
    lineas.append("=" * ancho)
    lineas.append("")
    lineas.append("")
    
    return "\n".join(lineas)


def generar_factura_a_texto(venta, items, cliente):
    """
    Genera texto de Factura A (simulada, sin CAE real).
    """
    lineas = []
    ancho = 80
    
    lineas.append("=" * ancho)
    lineas.append("    FACTURA A".center(ancho))
    lineas.append("    LUBRICENTRO WINTER".center(ancho))
    lineas.append("=" * ancho)
    lineas.append(f"Punto de Venta: {venta['punto_venta']}  Comp. Nro: {venta['numero_comprobante']:08d}")
    lineas.append(f"Fecha: {venta['creado_en']}")
    lineas.append(f"CAE: NO DISPONIBLE (requiere integración AFIP)")
    lineas.append("-" * ancho)
    
    # Datos del cliente
    lineas.append("DATOS DEL CLIENTE:")
    lineas.append(f"  Razón Social: {cliente.get('nombre', 'Consumidor Final')}")
    if cliente.get('telefono'):
        lineas.append(f"  Teléfono: {cliente['telefono']}")
    if cliente.get('email'):
        lineas.append(f"  Email: {cliente['email']}")
    lineas.append("-" * ancho)
    
    # Items
    lineas.append(f"{'Cant':>6} {'Descripción':<38} {'P.Unit':>12} {'Subtotal':>12}")
    lineas.append("-" * ancho)
    for item in items:
        lineas.append(f"{item['cantidad']:>6.2f} {item['producto_nombre'][:38]:<38} {item['precio_unitario']:>12.2f} {item['subtotal']:>12.2f}")
    lineas.append("-" * ancho)
    
    # Totales
    lineas.append(f"{'Subtotal:':>68} {formatear_monto(venta['subtotal']):>12}")
    lineas.append(f"{'IVA 21%:':>68} {formatear_monto(venta['iva']):>12}")
    lineas.append(f"{'TOTAL:':>68} {formatear_monto(venta['total']):>12}")
    lineas.append("=" * ancho)
    lineas.append(f"Método de Pago: {metodo_pago_nombre(venta['metodo_pago'])}")
    lineas.append("=" * ancho)
    lineas.append("")
    
    return "\n".join(lineas)


def generar_factura_b_texto(venta, items, cliente):
    """Genera texto de Factura B (simulada)."""
    return generar_factura_a_texto(venta, items, cliente).replace("FACTURA A", "FACTURA B")


def generar_factura_c_texto(venta, items, cliente):
    """Genera texto de Factura C (simulada)."""
    return generar_factura_a_texto(venta, items, cliente).replace("FACTURA A", "FACTURA C")


def metodo_pago_nombre(metodo):
    return {
        'efectivo': 'Efectivo',
        'tarjeta_debito': 'Tarjeta Débito',
        'tarjeta_credito': 'Tarjeta Crédito',
        'transferencia': 'Transferencia',
        'cuenta_corriente': 'Cuenta Corriente'
    }.get(metodo, metodo)


def guardar_comprobante_archivo(texto, venta, tipo):
    """Guarda el comprobante en archivo para imprimir después."""
    os.makedirs("comprobantes", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comprobantes/{tipo}_{venta['punto_venta']}_{venta['numero_comprobante']:08d}_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(texto)
    return filename


def imprimir_comprobante(texto):
    """
    Intenta imprimir en impresora térmica.
    En Windows usa win32print, en Linux usa lp.
    """
    try:
        import platform
        sistema = platform.system()
        
        if sistema == "Windows":
            try:
                import win32print
                printer_name = win32print.GetDefaultPrinter()
                hPrinter = win32print.OpenPrinter(printer_name)
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Comprobante", None, "RAW"))
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, texto.encode('cp1252', errors='ignore'))
                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
                win32print.ClosePrinter(hPrinter)
                return True
            except ImportError:
                pass
        
        elif sistema == "Linux":
            try:
                import subprocess
                proc = subprocess.Popen(['lp', '-d', 'default'], stdin=subprocess.PIPE)
                proc.communicate(input=texto.encode('utf-8'))
                return proc.returncode == 0
            except:
                pass
        
        # Fallback: guardar archivo
        return False
    except:
        return False