import time
from escpos.printer import Usb

# --- CONFIGURACIÓN DE IMPRESORA ---
# Debes encontrar los Vendor ID y Product ID de tu impresora térmica.
# En Windows, lo encuentras en el Administrador de Dispositivos (Propiedades > Detalles > Id. de hardware).
# Si usas una impresora de red o serial, la configuración es diferente.
# Ejemplo de IDs comunes para una impresora genérica
VID = 0x04B8 # Vendor ID (Ejemplo EPSON)
PID = 0x0202 # Product ID (Ejemplo TM-T88IV)

# Si tu impresora es de RED, usarías:
# from escpos.printer import Network
# p = Network("192.168.1.100", port=9100)

def imprimir_boleta(venta_data):
    """
    Formatea e imprime una boleta a la impresora térmica.
    :param venta_data: Diccionario con la información de la venta.
    """
    
    # 1. Conexión a la Impresora
    try:
        # Intenta conectar vía USB
        p = Usb(VID, PID, in_ep=0x82, out_ep=0x01) # in_ep/out_ep son opcionales
        print("Conexión a impresora exitosa.")
    except Exception as e:
        print(f"ERROR: No se pudo conectar a la impresora USB. Revisar VID/PID o si está encendida. {e}")
        # Si no hay impresora, imprimimos a la consola para pruebas.
        imprimir_simulacion(venta_data) 
        return

    # 2. Formateo e Impresión
    p.set(align='center', font='b', height=1, width=1)
    p.text("--- LIBRERÍA LOS ÁNGELES ---\n")
    p.text("Calle Principal #1234, Ciudad\n")
    p.text("Teléfono: (555) 123-4567\n")
    p.text("--------------------------------\n")

    p.set(align='left')
    p.text(f"FECHA: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    p.text(f"FOLIO VENTA: {venta_data.get('id', 'N/A')}\n")
    p.text("--------------------------------\n")
    
    # Encabezados de tabla
    p.text("DESCRIPCIÓN      CANT.  PRECIO  TOTAL\n")
    p.text("--------------------------------\n")

    # Detalle de Productos
    for item in venta_data['detalle']:
        nombre = item['nombre'][:17].ljust(17) # Truncar a 17 chars
        cantidad = str(item['cantidad']).center(5)
        precio_unitario = f"{item['precio_unitario']:.2f}".rjust(6)
        total_item = f"{item['cantidad'] * item['precio_unitario']:.2f}".rjust(6)
        
        p.text(f"{nombre} {cantidad} {precio_unitario} {total_item}\n")
        
    p.text("--------------------------------\n")
    
    # Totales
    p.set(align='right', font='b', height=2, width=2)
    p.text(f"TOTAL: ${venta_data['total']:.2f}\n")
    p.set(align='center', font='a', height=1, width=1) # Volver a fuente normal
    
    p.text("\n¡GRACIAS POR SU COMPRA!\n")
    p.text("\n") # Espacio extra
    p.cut() # Cortar el papel
    
    print("Boleta enviada a impresora.")
    
def imprimir_simulacion(venta_data):
    """Función de respaldo para imprimir el formato en consola."""
    print("\n--- SIMULACIÓN DE BOLETA (Consola) ---")
    print("LIBRERÍA LOS ÁNGELES")
    print("--------------------------------")
    print(f"FOLIO VENTA: {venta_data.get('id', 'N/A')}")
    print("--------------------------------")
    print("DESCRIPCIÓN      CANT.  PRECIO  TOTAL")
    for item in venta_data['detalle']:
        nombre = item['nombre'][:17].ljust(17)
        cantidad = str(item['cantidad']).center(5)
        precio_unitario = f"{item['precio_unitario']:.2f}".rjust(6)
        total_item = f"{item['cantidad'] * item['precio_unitario']:.2f}".rjust(6)
        print(f"{nombre} {cantidad} {precio_unitario} {total_item}")
    print("--------------------------------")
    print(f"TOTAL: ${venta_data['total']:.2f}")
    print("--------------------------------\n")

# Bloque de prueba (Opcional)
if __name__ == '__main__':
    # Datos simulados de una venta
    test_data = {
        'id': 105,
        'total': 2100.00,
        'detalle': [
            {'nombre': 'Lápiz HB', 'cantidad': 3, 'precio_unitario': 500.00},
            {'nombre': 'Goma de borrar XL', 'cantidad': 2, 'precio_unitario': 300.00},
            {'nombre': 'Cuaderno Profesional 100h', 'cantidad': 1, 'precio_unitario': 600.00},
        ]
    }
    imprimir_boleta(test_data)