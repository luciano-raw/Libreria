import time
import os
import json
from escpos.printer import Usb

# Intentar importar Bluetooth (puede no estar disponible en todas las versiones)
try:
    from escpos.printer import Bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False

# --- CONFIGURACIÓN DE IMPRESORA ---
CONFIG_FILE = "config_impresora.json"

def cargar_configuracion_impresora():
    """Carga la configuración de la impresora desde el archivo"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    # Valores por defecto si no hay configuración
    return {
        'tipo': 'USB',
        'vid': 0x04B8,
        'pid': 0x0202
    }

def imprimir_boleta(venta_data):
    """
    Formatea e imprime una boleta a la impresora térmica.
    :param venta_data: Diccionario con la información de la venta.
    """
    
    # 1. Conexión a la Impresora
    config = cargar_configuracion_impresora()
    
    try:
        if config.get('tipo') == 'Bluetooth':
            # Conexión Bluetooth
            if not BLUETOOTH_AVAILABLE:
                raise Exception("Soporte Bluetooth no disponible. Instala la versión correcta de python-escpos o usa USB.")
            mac = config.get('mac', '')
            if not mac:
                raise Exception("Dirección MAC no configurada")
            p = Bluetooth(mac)
            print("Conexión a impresora Bluetooth exitosa.")
        else:
            # Conexión USB (por defecto)
            vid = config.get('vid', 0x04B8)
            pid = config.get('pid', 0x0202)
            p = Usb(vid, pid, in_ep=0x82, out_ep=0x01)
            print("Conexión a impresora USB exitosa.")
    except Exception as e:
        print(f"ERROR: No se pudo conectar a la impresora. {e}")
        print("Revisa la configuración en config_impresora.py o ejecuta config_impresora.py")
        # Si no hay impresora, imprimimos a la consola para pruebas.
        imprimir_simulacion(venta_data) 
        return

    # 2. Formateo e Impresión
    p.set(align='center', font='b', height=1, width=1)
    p.text("--- LIBRERÍA AGOSTO 7 ---\n")
    p.text("Sistema POS\n")
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
    print("LIBRERÍA AGOSTO 7")
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