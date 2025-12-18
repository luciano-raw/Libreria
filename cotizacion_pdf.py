import os
from fpdf import FPDF
from datetime import datetime
from PIL import Image

# Definimos el directorio donde se guardarán las cotizaciones
OUTPUT_DIR = "cotizaciones"

# Paleta de colores del logo (adaptada para PDF)
COLORS = {
    'primary': (205, 180, 219),      # #cdb4db - Morado claro
    'secondary': (255, 200, 221),   # #ffc8dd - Rosa claro
    'accent': (255, 175, 204),      # #ffafcc - Rosa
    'info': (189, 224, 254),        # #bde0fe - Azul claro
    'highlight': (162, 210, 255),  # #a2d2ff - Azul
    'text_dark': (30, 41, 59),      # #1E293B - Texto oscuro
    'text_light': (241, 245, 249),  # #F1F5F9 - Texto claro
    'border': (226, 232, 240),      # #E2E8F0 - Borde
    'header_bg': (205, 180, 219),  # Fondo del encabezado
}

def hex_to_rgb(hex_color):
    """Convierte color hexadecimal a RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def generar_pdf_cotizacion(cotizacion_data):
    """
    Crea un archivo PDF profesional para una cotización.

    :param cotizacion_data: Un diccionario que contiene:
        'id': (int) El ID de la cotización desde la BD.
        'cliente_nombre': (str) El nombre del cliente.
        'total': (float) El total de la cotización.
        'detalle': (list) Una lista de diccionarios de productos:
                     [{'nombre': str, 'cantidad': int, 'precio_unitario': float, 
                       'codigo_barras': str, 'marca': str}, ...]
    :return: (str) La ruta al archivo PDF generado.
    """
    
    # 1. Asegurarse de que el directorio de salida exista
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Directorio '{OUTPUT_DIR}' creado.")

    # 2. Inicializar el PDF (FPDF)
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    
    # Configurar márgenes
    margin_left = 15
    margin_top = 15
    margin_right = 15
    page_width = 210 - margin_left - margin_right
    
    # --- ENCABEZADO CON LOGO ---
    logo_path = os.path.join("assets", "logo.png")
    logo_size = 35  # Tamaño del logo en mm
    
    # Dibujar fondo del encabezado
    pdf.set_fill_color(*COLORS['header_bg'])
    pdf.rect(margin_left, margin_top, page_width, 50, 'F')
    
    # Insertar logo si existe
    if os.path.exists(logo_path):
        try:
            # FPDF puede manejar PNG directamente en versiones recientes
            pdf.image(logo_path, x=margin_left + 5, y=margin_top + 7.5, w=logo_size, h=logo_size)
        except Exception as e:
            print(f"Error al cargar logo: {e}. Continuando sin logo.")
    
    # Título de la empresa
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(*COLORS['text_dark'])
    pdf.set_xy(margin_left + logo_size + 10, margin_top + 10)
    pdf.cell(0, 10, 'Librería Agosto 7', 0, 0, 'L')
    
    # Subtítulo
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_xy(margin_left + logo_size + 10, margin_top + 20)
    pdf.cell(0, 8, 'COTIZACIÓN', 0, 0, 'L')
    
    # Información de contacto (derecha)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(*COLORS['text_dark'])
    pdf.set_xy(margin_left + page_width - 60, margin_top + 15)
    pdf.cell(60, 5, 'Tel: (555) 123-4567', 0, 0, 'R')
    pdf.set_xy(margin_left + page_width - 60, margin_top + 20)
    pdf.cell(60, 5, 'Email: contacto@libreriaagosto7.com', 0, 0, 'R')
    pdf.set_xy(margin_left + page_width - 60, margin_top + 25)
    pdf.cell(60, 5, 'Calle Principal #1234', 0, 0, 'R')
    
    y_pos = margin_top + 55
    
    # --- INFORMACIÓN DEL CLIENTE Y COTIZACIÓN ---
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(*COLORS['text_dark'])
    pdf.set_fill_color(*COLORS['info'])
    pdf.rect(margin_left, y_pos, page_width, 8, 'F')
    
    pdf.set_xy(margin_left + 5, y_pos + 2)
    pdf.cell(0, 6, 'INFORMACIÓN DE LA COTIZACIÓN', 0, 0, 'L')
    
    y_pos += 12
    
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Información en dos columnas
    col1_width = page_width * 0.5
    col2_width = page_width * 0.5
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(*COLORS['text_dark'])
    pdf.set_xy(margin_left, y_pos)
    pdf.cell(col1_width, 7, f'Cliente: {cotizacion_data["cliente_nombre"]}', 0, 0, 'L')
    
    pdf.set_xy(margin_left + col1_width, y_pos)
    pdf.cell(col2_width, 7, f'Fecha: {fecha_hoy}', 0, 0, 'L')
    
    y_pos += 8
    
    pdf.set_xy(margin_left, y_pos)
    pdf.cell(col1_width, 7, f'Folio: #{cotizacion_data["id"]}', 0, 0, 'L')
    
    y_pos += 12
    
    # --- TABLA DE PRODUCTOS ---
    # Encabezados de tabla
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(*COLORS['text_light'])
    pdf.set_fill_color(*COLORS['primary'])
    
    header_height = 10
    col_widths = {
        'codigo': 30,
        'nombre': 70,
        'marca': 35,
        'cantidad': 20,
        'precio': 30,
        'subtotal': 25
    }
    
    # Dibujar encabezados
    x_start = margin_left
    pdf.rect(x_start, y_pos, page_width, header_height, 'F')
    
    pdf.set_xy(x_start + 2, y_pos + 3)
    pdf.cell(col_widths['codigo'], 6, 'Código', 0, 0, 'C')
    
    x_start += col_widths['codigo']
    pdf.set_xy(x_start + 2, y_pos + 3)
    pdf.cell(col_widths['nombre'], 6, 'Producto', 0, 0, 'C')
    
    x_start += col_widths['nombre']
    pdf.set_xy(x_start + 2, y_pos + 3)
    pdf.cell(col_widths['marca'], 6, 'Marca', 0, 0, 'C')
    
    x_start += col_widths['marca']
    pdf.set_xy(x_start + 2, y_pos + 3)
    pdf.cell(col_widths['cantidad'], 6, 'Cant.', 0, 0, 'C')
    
    x_start += col_widths['cantidad']
    pdf.set_xy(x_start + 2, y_pos + 3)
    pdf.cell(col_widths['precio'], 6, 'P. Unit.', 0, 0, 'C')
    
    x_start += col_widths['precio']
    pdf.set_xy(x_start + 2, y_pos + 3)
    pdf.cell(col_widths['subtotal'], 6, 'Subtotal', 0, 0, 'C')
    
    y_pos += header_height
    
    # Detalle de productos
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(*COLORS['text_dark'])
    
    row_num = 0
    for item in cotizacion_data['detalle']:
        subtotal = item['cantidad'] * item['precio_unitario']
        
        # Alternar color de fondo para mejor legibilidad
        if row_num % 2 == 0:
            pdf.set_fill_color(255, 255, 255)  # Blanco
        else:
            pdf.set_fill_color(250, 248, 252)  # Blanco con tinte morado muy claro
        
        # Calcular altura de la fila (puede ser multilínea si el nombre es largo)
        nombre = item.get('nombre', '')
        marca = item.get('marca', '') or 'N/A'
        codigo = item.get('codigo_barras', '') or 'N/A'
        
        # Calcular altura necesaria
        nombre_lines = max(1, len(nombre) // 25)  # Aproximadamente 25 caracteres por línea
        row_height = max(8, nombre_lines * 4 + 4)
        
        # Dibujar fondo de la fila
        pdf.rect(margin_left, y_pos, page_width, row_height, 'F')
        
        # Dibujar bordes
        pdf.set_draw_color(*COLORS['border'])
        pdf.rect(margin_left, y_pos, page_width, row_height, 'D')
        
        # Código
        x_start = margin_left + 2
        pdf.set_xy(x_start, y_pos + (row_height - 4) / 2)
        pdf.cell(col_widths['codigo'], 4, codigo[:12], 0, 0, 'L')
        
        # Nombre (puede ser multilínea)
        x_start += col_widths['codigo']
        pdf.set_xy(x_start + 2, y_pos + 2)
        pdf.multi_cell(col_widths['nombre'] - 4, 4, nombre, 0, 'L')
        
        # Marca
        x_start += col_widths['nombre']
        pdf.set_xy(x_start + 2, y_pos + (row_height - 4) / 2)
        pdf.cell(col_widths['marca'], 4, marca[:15], 0, 0, 'L')
        
        # Cantidad
        x_start += col_widths['marca']
        pdf.set_xy(x_start + 2, y_pos + (row_height - 4) / 2)
        pdf.cell(col_widths['cantidad'], 4, str(item['cantidad']), 0, 0, 'C')
        
        # Precio unitario
        x_start += col_widths['cantidad']
        pdf.set_xy(x_start + 2, y_pos + (row_height - 4) / 2)
        pdf.cell(col_widths['precio'], 4, f"${item['precio_unitario']:.2f}", 0, 0, 'R')
        
        # Subtotal
        x_start += col_widths['precio']
        pdf.set_xy(x_start + 2, y_pos + (row_height - 4) / 2)
        pdf.cell(col_widths['subtotal'], 4, f"${subtotal:.2f}", 0, 0, 'R')
        
        y_pos += row_height
        row_num += 1
        
        # Verificar si necesitamos una nueva página
        if y_pos > 270:  # Cerca del final de la página
            pdf.add_page()
            y_pos = margin_top
    
    # --- TOTAL ---
    y_pos += 5
    pdf.set_draw_color(*COLORS['primary'])
    pdf.set_line_width(0.5)
    pdf.line(margin_left, y_pos, margin_left + page_width, y_pos)
    
    y_pos += 8
    
    # Fila del total
    pdf.set_fill_color(*COLORS['highlight'])
    pdf.rect(margin_left + page_width - col_widths['precio'] - col_widths['subtotal'], 
             y_pos, col_widths['precio'] + col_widths['subtotal'], 12, 'F')
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(*COLORS['text_dark'])
    pdf.set_xy(margin_left + page_width - col_widths['precio'] - col_widths['subtotal'] - 40, y_pos + 2)
    pdf.cell(40, 8, 'TOTAL:', 0, 0, 'R')
    
    pdf.set_xy(margin_left + page_width - col_widths['subtotal'], y_pos + 2)
    pdf.cell(col_widths['subtotal'], 8, f"${cotizacion_data['total']:.2f}", 0, 0, 'R')
    
    # --- PIE DE PÁGINA ---
    y_pos = 280
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.set_xy(margin_left, y_pos)
    pdf.cell(page_width, 5, 'Cotización válida por 15 días a partir de la fecha de emisión.', 0, 0, 'C')
    
    y_pos += 5
    pdf.set_xy(margin_left, y_pos)
    pdf.cell(page_width, 5, 'Precios sujetos a cambio sin previo aviso. Todos los precios incluyen IVA.', 0, 0, 'C')
    
    # 3. Guardar el PDF
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
