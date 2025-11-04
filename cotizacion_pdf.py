import os
from fpdf import FPDF
from datetime import datetime

# Definimos el directorio donde se guardarán las cotizaciones
OUTPUT_DIR = "cotizaciones"

def generar_pdf_cotizacion(cotizacion_data):
    """
    Crea un archivo PDF para una cotización.

    :param cotizacion_data: Un diccionario que contiene:
        'id': (int) El ID de la cotización desde la BD.
        'cliente_nombre': (str) El nombre del cliente.
        'total': (float) El total de la cotización.
        'detalle': (list) Una lista de diccionarios de productos:
                     [{'nombre': str, 'cantidad': int, 'precio_unitario': float}, ...]
    :return: (str) La ruta al archivo PDF generado.
    """
    
    # 1. Asegurarse de que el directorio de salida exista
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Directorio '{OUTPUT_DIR}' creado.")

    # 2. Inicializar el PDF (FPDF)
    # 'P' = Portrait (Vertical), 'mm' = milímetros, 'A4' = tamaño de hoja
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    
    # --- Encabezado ---
    pdf.set_font('Helvetica', 'B', 20) # Fuente: Helvetica, Negrita, Tamaño 20
    pdf.cell(0, 10, 'COTIZACIÓN', 0, 1, 'C') # 0 ancho (full), 10 alto, sin borde, 1 (salto línea), 'C' (centrado)
    pdf.ln(5) # Salto de línea de 5mm

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Librería Talca', 0, 1, 'L')
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, 'Calle Principal #1234, Ciudad', 0, 1, 'L')
    pdf.cell(0, 6, 'Teléfono: (555) 123-4567', 0, 1, 'L')
    pdf.ln(10)

    # --- Información del Cliente y Cotización ---
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(40, 7, 'Cliente:', 0, 0)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 7, cotizacion_data['cliente_nombre'], 0, 1)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(40, 7, 'Fecha de Emisión:', 0, 0)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 7, fecha_hoy, 0, 1)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(40, 7, 'Folio Cotización:', 0, 0)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 7, str(cotizacion_data['id']), 0, 1)
    pdf.ln(10)

    # --- Tabla de Productos (Encabezados) ---
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(230, 230, 230) # Color de fondo gris claro
    pdf.cell(100, 8, 'Descripción', 1, 0, 'C', True) # 1 (borde), True (fondo)
    pdf.cell(20, 8, 'Cant.', 1, 0, 'C', True)
    pdf.cell(35, 8, 'Precio Unit.', 1, 0, 'C', True)
    pdf.cell(35, 8, 'Subtotal', 1, 1, 'C', True)

    # --- Tabla de Productos (Detalle) ---
    pdf.set_font('Helvetica', '', 10)
    for item in cotizacion_data['detalle']:
        subtotal = item['cantidad'] * item['precio_unitario']
        
        # Usamos MultiCell para manejar nombres largos (permite que el texto salte de línea)
        # Guardamos la posición Y actual
        y1 = pdf.get_y()
        pdf.multi_cell(100, 8, item['nombre'], 1, 'L')
        # Calculamos la altura de la celda (por si el nombre usó varias líneas)
        y2 = pdf.get_y()
        h = y2 - y1
        
        # Volvemos a la posición Y inicial para dibujar las otras celdas
        pdf.set_xy(pdf.get_x() + 100, y1)
        
        pdf.cell(20, h, str(item['cantidad']), 1, 0, 'C')
        pdf.cell(35, h, f"${item['precio_unitario']:.2f}", 1, 0, 'R')
        pdf.cell(35, h, f"${subtotal:.2f}", 1, 1, 'R')

    # --- Total ---
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(155, 10, 'TOTAL:', 0, 0, 'R')
    pdf.set_fill_color(255, 255, 204) # Fondo amarillo claro para el total
    pdf.cell(35, 10, f"${cotizacion_data['total']:.2f}", 1, 1, 'R', True)

    # --- Pie de Página (Footer) ---
    pdf.ln(15)
    pdf.set_font('Helvetica', 'I', 9) # Itálica
    pdf.cell(0, 6, 'Cotización válida por 15 días.', 0, 1, 'C')
    pdf.cell(0, 6, 'Precios sujetos a cambio sin previo aviso.', 0, 1, 'C')

    # 3. Guardar el PDF
    # Limpiamos el nombre del cliente para usarlo en el archivo
    cliente_limpio = "".join(c for c in cotizacion_data['cliente_nombre'] if c.isalnum() or c in (' ', '_')).rstrip()
    filename = f"Cotizacion_{cotizacion_data['id']}_{cliente_limpio.replace(' ', '_')}.pdf"
    
    ruta_archivo = os.path.join(OUTPUT_DIR, filename)
    
    try:
        pdf.output(ruta_archivo)
        print(f"PDF generado exitosamente en: {ruta_archivo}")
        return ruta_archivo
    except Exception as e:
        print(f"Error al guardar el PDF: {e}")
        return None