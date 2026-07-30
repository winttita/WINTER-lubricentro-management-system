import os
import platform
import subprocess
from datetime import datetime

PUNTO_VENTA = "0001"
IVA_PORCENTAJE = 0.21

ESC = b'\x1b'
GS = b'\x1d'

PRINTER_NAME = None

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


def obtener_impresoras_disponibles():
    """Devuelve lista de nombres de impresoras instaladas en Windows."""
    try:
        import win32print
        return [p[2] for p in win32print.EnumPrinters(2)]
    except ImportError:
        return []


def imprimir_comprobante(texto):
    """
    Imprime en impresora térmica usando comandos ESC/POS.
    En Windows usa win32print, en Linux usa lp.
    """
    try:
        sistema = platform.system()

        # Build ESC/POS payload
        payload = ESC + b'@'  # Initialize printer
        payload += texto.encode('cp1252' if sistema == 'Windows' else 'utf-8', errors='ignore')
        payload += b'\n' * 8
        payload += GS + b'V\x00'  # Full cut

        if sistema == "Windows":
            try:
                import win32print
                printer_name = PRINTER_NAME or win32print.GetDefaultPrinter()
                if not printer_name:
                    return False
                hPrinter = win32print.OpenPrinter(printer_name)
                try:
                    hJob = win32print.StartDocPrinter(hPrinter, 1, ("Comprobante", None, "RAW"))
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, payload)
                    win32print.EndPagePrinter(hPrinter)
                    win32print.EndDocPrinter(hPrinter)
                finally:
                    win32print.ClosePrinter(hPrinter)
                return True
            except ImportError:
                pass

        elif sistema == "Linux":
            try:
                proc = subprocess.Popen(['lp', '-d', PRINTER_NAME or 'default'], stdin=subprocess.PIPE)
                proc.communicate(input=payload)
                return proc.returncode == 0
            except Exception:
                pass

        return False
    except Exception:
        return False


def imprimir_prueba():
    """Imprime un ticket de prueba."""
    from datetime import datetime
    lineas = []
    lineas.append("=" * 40)
    lineas.append("  LUBRICENTRO WINTER".center(40))
    lineas.append("=" * 40)
    lineas.append("  PRUEBA DE IMPRESION".center(40))
    lineas.append("-" * 40)
    lineas.append(f"  Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    lineas.append(f"  Impresora: {PRINTER_NAME or 'Default'}")
    lineas.append("-" * 40)
    lineas.append("  Si ves este texto, la impresora")
    lineas.append("  funciona correctamente.")
    lineas.append("=" * 40)
    lineas.append("")
    return imprimir_comprobante("\n".join(lineas))


def abrir_cajon():
    """Abre el cajón de dinero usando ESC/POS."""
    sistema = platform.system()
    payload = ESC + b'@'  # Initialize
    payload += ESC + b'p\x00\x30\xff'  # Cash drawer pin 2
    payload += ESC + b'p\x01\x30\xff'  # Cash drawer pin 5

    if sistema == "Windows":
        try:
            import win32print
            printer_name = PRINTER_NAME or win32print.GetDefaultPrinter()
            if not printer_name:
                return False
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Cajon", None, "RAW"))
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, payload)
                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
            return True
        except ImportError:
            return False
    elif sistema == "Linux":
        try:
            proc = subprocess.Popen(['lp', '-d', PRINTER_NAME or 'default'], stdin=subprocess.PIPE)
            proc.communicate(input=payload)
            return proc.returncode == 0
        except Exception:
            return False
    return False