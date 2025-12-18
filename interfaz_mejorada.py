import os
import sys

# Configurar las rutas de Tcl/Tk para que funcionen en el entorno virtual
python_dir = os.path.dirname(sys.executable)
if '.venv' in python_dir or 'venv' in python_dir or 'Scripts' in python_dir:
    current_path = python_dir
    for _ in range(5):
        current_path = os.path.dirname(current_path)
        tcl_dir = os.path.join(current_path, "tcl")
        if os.path.exists(tcl_dir):
            tcl_lib = os.path.join(tcl_dir, "tcl8.6")
            tk_lib = os.path.join(tcl_dir, "tk8.6")
            if os.path.exists(tcl_lib) and os.path.exists(tk_lib):
                os.environ["TCL_LIBRARY"] = tcl_lib
                os.environ["TK_LIBRARY"] = tk_lib
                break
    if "TCL_LIBRARY" not in os.environ:
        common_paths = [
            r"C:\Users\Luciano\AppData\Local\Programs\Python\Python313",
            r"C:\Program Files\Python313",
            r"C:\Python313",
        ]
        for base_python in common_paths:
            tcl_dir = os.path.join(base_python, "tcl")
            if os.path.exists(tcl_dir):
                tcl_lib = os.path.join(tcl_dir, "tcl8.6")
                tk_lib = os.path.join(tcl_dir, "tk8.6")
                if os.path.exists(tcl_lib) and os.path.exists(tk_lib):
                    os.environ["TCL_LIBRARY"] = tcl_lib
                    os.environ["TK_LIBRARY"] = tk_lib
                    break

import customtkinter as ctk
from tkinter import ttk 
import tkinter as tk 
from tkinter import messagebox 
from PIL import Image

# --- Importaciones Propias ---
from cotizacion_pdf import generar_pdf_cotizacion
from ticket import imprimir_boleta 

# Importamos la lógica de base de datos
from logica import (
    obtener_productos, 
    buscar_producto_por_codigo, 
    registrar_venta,
    registrar_cotizacion,
    agregar_producto,
    editar_producto,
    eliminar_producto,
    buscar_productos_por_nombre,
    obtener_todas_las_cotizaciones,
    obtener_detalle_cotizacion,
    eliminar_cotizacion_completa,
    convertir_cotizacion_a_venta
)

# --- AÑADIDO: Importaciones para el Excel ---
from tkinter import filedialog
from importador import importar_inventario_desde_excel
# --- FIN DE AÑADIDOS ---

# --- Importación para configurador de impresora ---
import subprocess
import platform


# Configuración global de la librería - Tema más profesional
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Colores personalizados para un look más profesional
COLORS = {
    'primary': '#2563EB',      # Azul profesional
    'primary_hover': '#1D4ED8',
    'success': '#10B981',      # Verde éxito
    'success_hover': '#059669',
    'warning': '#F59E0B',      # Naranja
    'warning_hover': '#D97706',
    'danger': '#EF4444',       # Rojo
    'danger_hover': '#DC2626',
    'info': '#3B82F6',         # Azul info
    'info_hover': '#2563EB',
    'sidebar': '#1E293B',       # Gris oscuro para sidebar
    'sidebar_hover': '#334155',
    'bg_light': '#F8FAFC',      # Fondo claro
    'bg_dark': '#0F172A',       # Fondo oscuro
    'text_primary': '#1E293B',
    'text_secondary': '#64748B',
    'border': '#E2E8F0',
}


class App(ctk.CTk):

    def load_icon(self, name, size=(24, 24)):
        """Carga un icono desde la carpeta 'assets' de forma segura."""
        path = os.path.join(self.assets_path, name)
        try:
            img = Image.open(path)
            return ctk.CTkImage(img, size=size)
        except Exception as e:
            print(f"Error cargando icono '{name}': {e}. Se usará un placeholder gris.")
            placeholder = Image.new("RGB", size, "gray")
            return ctk.CTkImage(placeholder, size=size)

    def __init__(self):
        super().__init__()

        # --- Variables del Carrito y Venta ---
        self.carrito = [] 
        self.total_venta = ctk.StringVar(value="0.00") 
        self.selected_product_id = None
        self.selected_quote_id = None
        
        # --- Configuración principal de la ventana ---
        self.title("Librería Agosto 7 - Sistema POS")
        self.geometry("1400x750")
        self.minsize(1200, 600)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Carga de Iconos y Logo (ANTES de crear la barra lateral) ---
        self.assets_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        if not os.path.exists(self.assets_path):
            os.makedirs(self.assets_path)
            print(f"Se ha creado la carpeta 'assets' en: {self.assets_path}")

        self.icon_sales = self.load_icon("icon_sales.png", size=(22, 22))
        self.icon_inventory = self.load_icon("icon_inventory.png", size=(22, 22))
        self.icon_quotes = self.load_icon("icon_quotes.png", size=(22, 22))
        self.icon_reports = self.load_icon("icon_reports.png", size=(22, 22))
        
        # Cargar logo si existe (más grande)
        logo_path = os.path.join(self.assets_path, "logo.png")
        self.logo_image = None
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path)
                self.logo_image = ctk.CTkImage(logo_img, size=(120, 120))
            except Exception as e:
                print(f"Error cargando logo: {e}")

        # --- Barra Lateral (Navigation Frame) - Mejorada ---
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS['sidebar'], width=220)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_propagate(False)
        self.navigation_frame.grid_rowconfigure(7, weight=1)  # Ajustado para el botón de respaldo 
        
        # Logo (solo imagen, sin texto)
        if self.logo_image:
            self.navigation_frame_label = ctk.CTkLabel(
                self.navigation_frame, 
                text="", 
                image=self.logo_image
            )
            self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=(25, 30), sticky="")
        else:
            # Si no hay logo, mostrar texto como fallback
            self.navigation_frame_label = ctk.CTkLabel(
                self.navigation_frame, 
                text="Librería\nAgosto 7", 
                font=ctk.CTkFont(size=22, weight="bold", family="Segoe UI"),
                text_color="white",
                justify="center"
            )
            self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=(25, 30), sticky="")

        # Separador
        separator1 = ctk.CTkFrame(self.navigation_frame, height=1, fg_color="#334155")
        separator1.grid(row=0, column=0, sticky="ew", padx=15, pady=(80, 0))
        
        # --- Botones de Navegación - Mejorados ---
        nav_button_style = {
            'corner_radius': 8,
            'height': 48,
            'border_spacing': 12,
            'fg_color': "transparent",
            'text_color': ("#CBD5E1", "#F1F5F9"),
            'hover_color': COLORS['sidebar_hover'],
            'anchor': "w",
            'font': ctk.CTkFont(size=15, weight="normal")
        }
        
        self.home_button = ctk.CTkButton(
            self.navigation_frame, 
            text="Ventas", 
            image=self.icon_sales,
            compound="left",
            command=self.home_button_event,
            **nav_button_style
        )
        self.home_button.grid(row=1, column=0, sticky="ew", padx=12, pady=4)

        self.frame_2_button = ctk.CTkButton(
            self.navigation_frame, 
            text="Inventario", 
            image=self.icon_inventory,
            compound="left",
            command=self.frame_2_button_event,
            **nav_button_style
        )
        self.frame_2_button.grid(row=2, column=0, sticky="ew", padx=12, pady=4)

        self.quotes_button = ctk.CTkButton(
            self.navigation_frame, 
            text="Cotizaciones", 
            image=self.icon_quotes,
            compound="left",
            command=self.quotes_button_event,
            **nav_button_style
        )
        self.quotes_button.grid(row=3, column=0, sticky="ew", padx=12, pady=4)
        
        self.reports_button = ctk.CTkButton(
            self.navigation_frame, 
            text="Reportes", 
            image=self.icon_reports,
            compound="left",
            state="disabled",
            **nav_button_style
        )
        self.reports_button.grid(row=4, column=0, sticky="ew", padx=12, pady=4)
        
        # Separador antes del botón de respaldo
        separator_backup = ctk.CTkFrame(self.navigation_frame, height=1, fg_color="#334155")
        separator_backup.grid(row=5, column=0, sticky="ew", padx=15, pady=(10, 5))
        
        # Botón de Respaldo de Base de Datos
        self.backup_button = ctk.CTkButton(
            self.navigation_frame,
            text="💾 Respaldo BD",
            command=self.exportar_base_datos,
            corner_radius=8,
            height=48,
            border_spacing=12,
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            text_color="white",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="normal")
        )
        self.backup_button.grid(row=6, column=0, sticky="ew", padx=12, pady=4)

        # --- Frames de Contenido ---
        self.home_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.inventory_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.quotes_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        
        self.create_home_view() 
        self.select_frame_by_name("home")


    # --- Lógica del Carrito ---
    
    def calcular_total(self):
        total = sum(item['precio'] * item['cantidad'] for item in self.carrito)
        return total
    
    def verificar_bajo_stock(self):
        """Verifica productos con bajo stock (≤10) y muestra alerta"""
        productos = obtener_productos()
        productos_bajo_stock = [p for p in productos if p.get('stock', 0) <= 10 and p.get('stock', 0) > 0]
        productos_sin_stock = [p for p in productos if p.get('stock', 0) == 0]
        
        # Crear frame de alerta si no existe
        if not hasattr(self, 'alerta_frame') or not self.alerta_frame.winfo_exists():
            self.alerta_frame = ctk.CTkFrame(self.home_frame, corner_radius=12, fg_color="#FEF3C7", border_width=2, border_color="#F59E0B")
            self.alerta_frame.grid(row=0, column=0, padx=20, pady=(10, 10), sticky="ew", columnspan=2)
            self.alerta_frame.grid_columnconfigure(0, weight=1)
        
        # Limpiar contenido anterior
        for widget in self.alerta_frame.winfo_children():
            widget.destroy()
        
        if productos_bajo_stock or productos_sin_stock:
            alerta_texto = "⚠️ ALERTA DE STOCK: "
            productos_lista = []
            
            if productos_sin_stock:
                productos_lista.extend([f"{p['nombre']} (SIN STOCK)" for p in productos_sin_stock[:5]])
            
            if productos_bajo_stock:
                productos_lista.extend([f"{p['nombre']} ({p['stock']} unidades)" for p in productos_bajo_stock[:5]])
            
            if len(productos_bajo_stock) + len(productos_sin_stock) > 5:
                alerta_texto += ", ".join(productos_lista) + f" y {len(productos_bajo_stock) + len(productos_sin_stock) - 5} más..."
            else:
                alerta_texto += ", ".join(productos_lista)
            
            ctk.CTkLabel(
                self.alerta_frame,
                text=alerta_texto,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#92400E",
                anchor="w",
                justify="left"
            ).grid(row=0, column=0, padx=15, pady=12, sticky="ew")
            
            # Botón para ver detalles
            btn_ver = ctk.CTkButton(
                self.alerta_frame,
                text="Ver Inventario",
                width=120,
                height=30,
                fg_color="#F59E0B",
                hover_color="#D97706",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda: self.select_frame_by_name("inventory")
            )
            btn_ver.grid(row=0, column=1, padx=15, pady=12)
        else:
            # Ocultar frame si no hay alertas
            self.alerta_frame.grid_remove()

    def actualizar_carrito_gui(self):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()

        # Encabezados de tabla mejorados
        header_frame = ctk.CTkFrame(self.cart_frame, fg_color="transparent", height=40)
        header_frame.grid(row=0, column=0, columnspan=5, sticky="ew", padx=0, pady=(0, 8))
        header_frame.grid_columnconfigure(0, weight=3)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=1)
        header_frame.grid_columnconfigure(3, weight=1)
        header_frame.grid_columnconfigure(4, weight=1)
        
        ctk.CTkLabel(header_frame, text="Producto", font=ctk.CTkFont(size=13, weight="bold"), 
                    text_color=COLORS['text_secondary']).grid(row=0, column=0, padx=12, sticky="w")
        ctk.CTkLabel(header_frame, text="Cant.", font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS['text_secondary']).grid(row=0, column=1, padx=8)
        ctk.CTkLabel(header_frame, text="Precio", font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS['text_secondary']).grid(row=0, column=2, padx=8)
        ctk.CTkLabel(header_frame, text="Subtotal", font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS['text_secondary']).grid(row=0, column=3, padx=8, sticky="e")
        # Columna vacía para el botón de eliminar
        header_frame.grid_columnconfigure(4, minsize=50)

        # Separador
        separator = ctk.CTkFrame(self.cart_frame, height=1, fg_color=COLORS['border'])
        separator.grid(row=1, column=0, columnspan=5, sticky="ew", padx=0, pady=(0, 12))

        for i, item in enumerate(self.carrito):
            row = i + 2
            subtotal = item['precio'] * item['cantidad']
            
            # Frame para cada item del carrito
            item_frame = ctk.CTkFrame(self.cart_frame, fg_color="transparent", height=45)
            item_frame.grid(row=row, column=0, columnspan=5, sticky="ew", padx=0, pady=4)
            item_frame.grid_columnconfigure(0, weight=3)
            item_frame.grid_columnconfigure(1, weight=1)
            item_frame.grid_columnconfigure(2, weight=1)
            item_frame.grid_columnconfigure(3, weight=1)
            item_frame.grid_columnconfigure(4, weight=1)
            
            ctk.CTkLabel(item_frame, text=item['nombre'], font=ctk.CTkFont(size=14),
                        anchor="w").grid(row=0, column=0, padx=12, sticky="w")
            
            # Frame para cantidad con botones +/-
            cantidad_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            cantidad_frame.grid(row=0, column=1, padx=8)
            
            btn_menos = ctk.CTkButton(
                cantidad_frame,
                text="-",
                width=30,
                height=30,
                fg_color=COLORS['warning'],
                hover_color=COLORS['warning_hover'],
                font=ctk.CTkFont(size=16, weight="bold"),
                command=lambda item_id=item['id']: self.modificar_cantidad_carrito(item_id, -1)
            )
            btn_menos.grid(row=0, column=0, padx=(0, 5))
            
            cantidad_label = ctk.CTkLabel(cantidad_frame, text=str(item['cantidad']), 
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         width=40)
            cantidad_label.grid(row=0, column=1, padx=5)
            
            btn_mas = ctk.CTkButton(
                cantidad_frame,
                text="+",
                width=30,
                height=30,
                fg_color=COLORS['success'],
                hover_color=COLORS['success_hover'],
                font=ctk.CTkFont(size=16, weight="bold"),
                command=lambda item_id=item['id']: self.modificar_cantidad_carrito(item_id, 1)
            )
            btn_mas.grid(row=0, column=2, padx=(5, 0))
            
            ctk.CTkLabel(item_frame, text=f"${item['precio']:.2f}", font=ctk.CTkFont(size=14)).grid(row=0, column=2, padx=8)
            ctk.CTkLabel(item_frame, text=f"${subtotal:.2f}", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=3, padx=8, sticky="e")
            
            remove_button = ctk.CTkButton(
                item_frame, 
                text="✕", 
                width=35, 
                height=35,
                fg_color=COLORS['danger'],
                hover_color=COLORS['danger_hover'],
                font=ctk.CTkFont(size=16, weight="bold"),
                command=lambda item_id=item['id']: self.remover_item_carrito(item_id)
            )
            remove_button.grid(row=0, column=4, padx=8)

        self.total_venta.set(f"{self.calcular_total():.2f}")

    def remover_item_carrito(self, item_id):
        self.carrito = [item for item in self.carrito if item['id'] != item_id]
        self.actualizar_carrito_gui()
    
    def modificar_cantidad_carrito(self, item_id, cambio):
        """Modifica la cantidad de un item en el carrito (+1 o -1)"""
        for item in self.carrito:
            if item['id'] == item_id:
                nueva_cantidad = item['cantidad'] + cambio
                if nueva_cantidad <= 0:
                    self.remover_item_carrito(item_id)
                else:
                    item['cantidad'] = nueva_cantidad
                self.actualizar_carrito_gui()
                return
        
    def agregar_producto_al_carrito(self, codigo_barras, cantidad=1):
        producto_data = buscar_producto_por_codigo(codigo_barras)
        
        if not producto_data:
            print(f"Error: Producto con código {codigo_barras} no encontrado.")
            return
            
        producto_id = producto_data['id']
        precio = producto_data['precio_venta']
        
        for item in self.carrito:
            if item['id'] == producto_id:
                item['cantidad'] += cantidad
                self.actualizar_carrito_gui()
                return

        self.carrito.append({
            'id': producto_id,
            'nombre': producto_data['nombre'],
            'cantidad': cantidad,
            'precio': precio,
        })
        
        self.actualizar_carrito_gui()
        
    # --- Manejadores de Venta/Cotización ---
    
    def process_sale(self):
        if not self.carrito:
            messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito para procesar.")
            return

        carrito_db = [{'id': item['id'], 'cantidad': item['cantidad'], 'precio_unitario': item['precio']} for item in self.carrito]
        total = self.calcular_total()
        
        venta_id = registrar_venta(carrito_db, total)
        
        if venta_id:
            messagebox.showinfo("Venta Exitosa", f"Venta #{venta_id} registrada correctamente.\nTotal: ${total:.2f}")
            
            boleta_data = {
                'id': venta_id,
                'total': total,
                'detalle': [{'nombre': item['nombre'], 
                             'cantidad': item['cantidad'], 
                             'precio_unitario': item['precio']} 
                            for item in self.carrito]
            }

            imprimir_boleta(boleta_data) 
            
            self.carrito = [] 
            self.actualizar_carrito_gui()
            
        else:
            messagebox.showerror("Error", "No se pudo procesar la venta. Intente nuevamente.")
            
    def generate_quote(self):
        if not self.carrito:
            messagebox.showwarning("Carrito Vacío", "No se puede generar una cotización con el carrito vacío.")
            return

        dialog = ctk.CTkInputDialog(text="Ingrese el nombre del cliente para la cotización:", 
                                    title="Generar Cotización")
        
        cliente_nombre = dialog.get_input() 
        
        if not cliente_nombre:
            return

        carrito_db = [{'id': item['id'], 'cantidad': item['cantidad'], 'precio_unitario': item['precio']} for item in self.carrito]
        total = self.calcular_total()
        
        cotizacion_id = registrar_cotizacion(carrito_db, total, cliente=cliente_nombre)
        
        if cotizacion_id:
            # Obtener datos completos de productos para el PDF
            productos_completos = obtener_productos()
            detalle_completo = []
            for item in self.carrito:
                producto_info = next((p for p in productos_completos if p['id'] == item['id']), None)
                if producto_info:
                    detalle_completo.append({
                        'nombre': item['nombre'],
                        'cantidad': item['cantidad'],
                        'precio_unitario': item['precio'],
                        'codigo_barras': producto_info.get('codigo_barras', ''),
                        'marca': producto_info.get('marca', '')
                    })
                else:
                    # Fallback si no se encuentra el producto
                    detalle_completo.append({
                        'nombre': item['nombre'],
                        'cantidad': item['cantidad'],
                        'precio_unitario': item['precio'],
                        'codigo_barras': '',
                        'marca': ''
                    })
            
            pdf_data = {
                'id': cotizacion_id,
                'cliente_nombre': cliente_nombre,
                'total': total,
                'detalle': detalle_completo
            }

            ruta_pdf = generar_pdf_cotizacion(pdf_data)
            
            if ruta_pdf:
                respuesta = messagebox.askyesno("Éxito", 
                                                f"Cotización #{cotizacion_id} generada exitosamente.\n\n¿Desea abrir la carpeta de cotizaciones?")
                if respuesta:
                    try:
                        # Abrir carpeta de forma multiplataforma
                        import platform
                        carpeta = os.path.dirname(ruta_pdf)
                        if platform.system() == "Windows":
                            os.startfile(carpeta)
                        elif platform.system() == "Darwin":  # macOS
                            subprocess.Popen(["open", carpeta])
                        else:  # Linux
                            subprocess.Popen(["xdg-open", carpeta])
                    except Exception as e:
                        print(f"Error al intentar abrir la carpeta: {e}")

            self.carrito = [] 
            self.actualizar_carrito_gui()
            
        else:
            messagebox.showerror("Error", "No se pudo registrar la cotización en la base de datos.")
    
    def abrir_configurador_impresora(self):
        """Abre la ventana de configuración de impresora"""
        try:
            # Obtener ruta del configurador de forma multiplataforma
            if getattr(sys, 'frozen', False):
                # Si está empaquetado, buscar en el mismo directorio
                base_path = os.path.dirname(sys.executable)
                config_path = os.path.join(base_path, "config_impresora.py")
            else:
                # Si es script, usar ruta relativa
                config_path = "config_impresora.py"
            
            # Abrir el configurador en un proceso separado
            subprocess.Popen([sys.executable, config_path])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el configurador de impresora.\n\nError: {str(e)}")
    
    def exportar_base_datos(self):
        """Exporta la base de datos como respaldo"""
        from datetime import datetime
        import shutil
        
        # Nombre del archivo con fecha y hora
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"libreria_backup_{fecha_hora}.db"
        
        # Abrir diálogo para seleccionar dónde guardar
        ruta_destino = filedialog.asksaveasfilename(
            title="Guardar Respaldo de Base de Datos",
            defaultextension=".db",
            filetypes=[("Archivos de Base de Datos", "*.db"), ("Todos los archivos", "*.*")],
            initialfile=nombre_archivo
        )
        
        if not ruta_destino:
            return  # Usuario canceló
        
        try:
            # Copiar el archivo de base de datos
            ruta_origen = "libreria.db"
            if not os.path.exists(ruta_origen):
                messagebox.showerror("Error", "No se encontró el archivo de base de datos 'libreria.db'")
                return
            
            shutil.copy2(ruta_origen, ruta_destino)
            
            # Obtener el tamaño del archivo
            tamaño = os.path.getsize(ruta_destino)
            tamaño_mb = tamaño / (1024 * 1024)
            
            messagebox.showinfo(
                "Respaldo Exitoso",
                f"Base de datos exportada correctamente.\n\n"
                f"Ubicación: {ruta_destino}\n"
                f"Tamaño: {tamaño_mb:.2f} MB"
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar la base de datos.\n\nError: {str(e)}")

    # --- Creación de Vistas ---

    def create_home_view(self):
        self.home_frame.grid_columnconfigure(0, weight=3)
        self.home_frame.grid_columnconfigure(1, weight=1)
        self.home_frame.grid_rowconfigure(0, weight=0)  # Alerta
        self.home_frame.grid_rowconfigure(1, weight=0)  # Búsqueda
        self.home_frame.grid_rowconfigure(2, weight=1)  # Carrito 
        
        # Frame superior con búsqueda mejorada
        search_frame = ctk.CTkFrame(self.home_frame, corner_radius=12, fg_color="transparent")
        search_frame.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(search_frame, text="Buscar Producto", 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS['text_secondary']).grid(row=0, column=0, sticky="w", padx=5, pady=(0, 8))
        
        self.scan_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Escanear código de barras o buscar por nombre...",
            height=50,
            font=ctk.CTkFont(size=15),
            corner_radius=10,
            border_width=2
        )
        self.scan_entry.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self.scan_entry.bind("<Return>", self.handle_scan_or_search)
        
        # Alerta de bajo stock
        self.verificar_bajo_stock()
        
        # Carrito mejorado
        cart_container = ctk.CTkFrame(self.home_frame, corner_radius=12)
        cart_container.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        cart_container.grid_columnconfigure(0, weight=1)
        cart_container.grid_rowconfigure(0, weight=1)
        
        ctk.CTkLabel(cart_container, text="Carrito de Compras", 
                    font=ctk.CTkFont(size=16, weight="bold"),
                    anchor="w").grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        self.cart_frame = ctk.CTkScrollableFrame(cart_container, corner_radius=0, fg_color="transparent")
        self.cart_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.cart_frame.grid_columnconfigure(0, weight=1)
        
        self.actualizar_carrito_gui()
        
        # Panel de resumen mejorado
        self.summary_frame = ctk.CTkFrame(self.home_frame, corner_radius=12)
        self.summary_frame.grid(row=0, column=1, rowspan=3, padx=(0, 20), pady=20, sticky="nsew")
        self.summary_frame.grid_columnconfigure(0, weight=1)
        self.summary_frame.grid_rowconfigure(2, weight=1) 
        
        ctk.CTkLabel(
            self.summary_frame, 
            text="TOTAL", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_secondary']
        ).grid(row=0, column=0, pady=(25, 8))

        total_label = ctk.CTkLabel(
            self.summary_frame, 
            textvariable=self.total_venta, 
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=COLORS['primary']
        )
        total_label.grid(row=1, column=0, pady=(0, 30))
        
        # Separador
        separator = ctk.CTkFrame(self.summary_frame, height=2, fg_color=COLORS['border'])
        separator.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        
        self.sell_button = ctk.CTkButton(
            self.summary_frame, 
            text="PROCESAR VENTA", 
            height=55, 
            fg_color=COLORS['success'], 
            hover_color=COLORS['success_hover'],
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10,
            command=self.process_sale
        ) 
        self.sell_button.grid(row=3, column=0, padx=20, pady=(10, 10), sticky="ew")
        
        self.quote_button = ctk.CTkButton(
            self.summary_frame, 
            text="GENERAR COTIZACIÓN", 
            height=55, 
            fg_color=COLORS['info'], 
            hover_color=COLORS['info_hover'],
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10,
            command=self.generate_quote
        ) 
        self.quote_button.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Botón de configuración de impresora
        self.printer_button = ctk.CTkButton(
            self.summary_frame,
            text="🖨️ Configurar Impresora",
            height=45,
            fg_color="#64748B",
            hover_color="#475569",
            font=ctk.CTkFont(size=13, weight="normal"),
            corner_radius=8,
            command=self.abrir_configurador_impresora
        )
        self.printer_button.grid(row=5, column=0, padx=20, pady=(0, 25), sticky="ew")


    def create_inventory_view(self):
        for widget in self.inventory_frame.winfo_children():
            widget.destroy()
            
        self.inventory_frame.grid_columnconfigure(0, weight=1)
        self.inventory_frame.grid_rowconfigure(0, weight=0)  # Formulario
        self.inventory_frame.grid_rowconfigure(1, weight=0)  # Buscador/Filtros
        self.inventory_frame.grid_rowconfigure(2, weight=0)  # Botones
        self.inventory_frame.grid_rowconfigure(3, weight=1)  # Tabla

        # --- Frame del Formulario (Arriba) - Mejorado ---
        form_frame = ctk.CTkFrame(self.inventory_frame, corner_radius=12)
        form_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="new")
        form_frame.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(form_frame, text="Código Barras:", 
                    font=ctk.CTkFont(size=13, weight="normal")).grid(row=0, column=0, padx=15, pady=12, sticky="e")
        self.inv_entry_codigo = ctk.CTkEntry(form_frame, placeholder_text="Código...", height=38, corner_radius=8)
        self.inv_entry_codigo.grid(row=0, column=1, padx=10, pady=12, sticky="ew")

        ctk.CTkLabel(form_frame, text="Nombre:", 
                    font=ctk.CTkFont(size=13, weight="normal")).grid(row=1, column=0, padx=15, pady=12, sticky="e")
        self.inv_entry_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombre del producto...", height=38, corner_radius=8)
        self.inv_entry_nombre.grid(row=1, column=1, padx=10, pady=12, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Descripción:", 
                    font=ctk.CTkFont(size=13, weight="normal")).grid(row=1, column=2, padx=15, pady=12, sticky="e")
        self.inv_entry_desc = ctk.CTkEntry(form_frame, placeholder_text="Descripción...", height=38, corner_radius=8)
        self.inv_entry_desc.grid(row=1, column=3, padx=10, pady=12, sticky="ew")

        ctk.CTkLabel(form_frame, text="Marca:", 
                    font=ctk.CTkFont(size=13, weight="normal")).grid(row=2, column=0, padx=15, pady=12, sticky="e")
        self.inv_entry_marca = ctk.CTkEntry(form_frame, placeholder_text="Marca del producto...", height=38, corner_radius=8)
        self.inv_entry_marca.grid(row=2, column=1, padx=10, pady=12, sticky="ew")

        ctk.CTkLabel(form_frame, text="Precio Venta:", 
                    font=ctk.CTkFont(size=13, weight="normal")).grid(row=2, column=2, padx=15, pady=12, sticky="e")
        self.inv_entry_precio = ctk.CTkEntry(form_frame, placeholder_text="Ej: 1500.00", height=38, corner_radius=8)
        self.inv_entry_precio.grid(row=2, column=3, padx=10, pady=12, sticky="ew")

        ctk.CTkLabel(form_frame, text="Stock Inicial:", 
                    font=ctk.CTkFont(size=13, weight="normal")).grid(row=3, column=0, padx=15, pady=12, sticky="e")
        self.inv_entry_stock = ctk.CTkEntry(form_frame, placeholder_text="Ej: 100", height=38, corner_radius=8)
        self.inv_entry_stock.grid(row=3, column=1, padx=10, pady=12, sticky="ew")
        
        self.inv_entry_stock.bind('<Return>', lambda event: self.on_agregar_producto())

        # --- Frame de Búsqueda y Filtros ---
        search_filter_frame = ctk.CTkFrame(self.inventory_frame, corner_radius=12)
        search_filter_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        search_filter_frame.grid_columnconfigure(1, weight=1)
        search_filter_frame.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(search_filter_frame, text="Buscar:", 
                    font=ctk.CTkFont(size=13, weight="normal")).grid(row=0, column=0, padx=15, pady=12, sticky="e")
        self.inv_search_entry = ctk.CTkEntry(search_filter_frame, placeholder_text="Buscar por nombre, código o marca...", 
                                            height=38, corner_radius=8)
        self.inv_search_entry.grid(row=0, column=1, padx=10, pady=12, sticky="ew")
        self.inv_search_entry.bind('<KeyRelease>', lambda event: self.filtrar_productos())
        
        ctk.CTkLabel(search_filter_frame, text="Filtrar por:", 
                    font=ctk.CTkFont(size=13, weight="normal")).grid(row=0, column=2, padx=15, pady=12, sticky="e")
        self.inv_filter_var = ctk.StringVar(value="Todos")
        filter_menu = ctk.CTkOptionMenu(search_filter_frame, values=["Todos", "Con Stock", "Sin Stock", "Bajo Stock (<10)"],
                                        variable=self.inv_filter_var, height=38, corner_radius=8,
                                        command=lambda x: self.filtrar_productos())
        filter_menu.grid(row=0, column=3, padx=10, pady=12, sticky="ew")

        # --- Frame de Botones de Acción (Centro) - Mejorados ---
        action_frame = ctk.CTkFrame(self.inventory_frame, corner_radius=0, fg_color="transparent")
        action_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        action_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1) 

        self.add_button = ctk.CTkButton(
            action_frame, 
            text="Agregar", 
            command=self.on_agregar_producto,
            fg_color=COLORS['success'], 
            hover_color=COLORS['success_hover'],
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.add_button.grid(row=0, column=0, padx=6, pady=5)
        
        self.edit_button = ctk.CTkButton(
            action_frame, 
            text="Guardar", 
            command=self.on_editar_producto,
            fg_color=COLORS['warning'], 
            hover_color=COLORS['warning_hover'],
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.edit_button.grid(row=0, column=1, padx=6, pady=5)

        self.delete_button = ctk.CTkButton(
            action_frame, 
            text="Eliminar", 
            command=self.on_eliminar_producto,
            fg_color=COLORS['danger'], 
            hover_color=COLORS['danger_hover'],
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.delete_button.grid(row=0, column=2, padx=6, pady=5)
        
        self.clear_button = ctk.CTkButton(
            action_frame, 
            text="Limpiar", 
            command=self.on_limpiar_formulario,
            fg_color="#64748B", 
            hover_color="#475569",
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.clear_button.grid(row=0, column=3, padx=6, pady=5)

        self.import_button = ctk.CTkButton(
            action_frame, 
            text="Importar Excel", 
            command=self.on_import_excel,
            fg_color=COLORS['info'], 
            hover_color=COLORS['info_hover'],
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.import_button.grid(row=0, column=4, padx=6, pady=5)

        # --- Frame de la Tabla (Abajo) - Mejorado ---
        tree_frame = ctk.CTkFrame(self.inventory_frame, corner_radius=12)
        tree_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("id", "codigo", "nombre", "marca", "precio", "stock")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Custom.Treeview")
        
        # Estilo para la tabla - Modo oscuro
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview", 
                       background="#1E293B",      # Fondo oscuro
                       foreground="#E2E8F0",       # Texto claro
                       fieldbackground="#1E293B",   # Fondo de campos oscuro
                       rowheight=35,
                       font=('Segoe UI', 11))
        style.configure("Custom.Treeview.Heading",
                       background="#334155",       # Encabezado gris oscuro
                       foreground="#F1F5F9",       # Texto encabezado claro
                       font=('Segoe UI', 11, 'bold'),
                       relief="flat")
        style.map("Custom.Treeview",
                 background=[("selected", COLORS['primary'])],
                 foreground=[("selected", "white")])
        
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=60, stretch=False, anchor="center")
        self.tree.heading("codigo", text="Código Barras")
        self.tree.column("codigo", width=150, anchor="w")
        self.tree.heading("nombre", text="Nombre")
        self.tree.column("nombre", width=300, stretch=True, anchor="w")
        self.tree.heading("marca", text="Marca")
        self.tree.column("marca", width=150, anchor="w")
        self.tree.heading("precio", text="Precio Venta")
        self.tree.column("precio", width=120, anchor="e")
        self.tree.heading("stock", text="Stock")
        self.tree.column("stock", width=100, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.on_select_producto)
        self.productos_completos = []  # Inicializar lista de productos
        self.actualizar_lista_productos()
        self.on_limpiar_formulario()

    # --- AÑADIDO: Función para manejar la importación de Excel ---
    def on_import_excel(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de inventario",
            filetypes=[("Archivos de Excel", "*.xlsx *.xls")]
        )
        
        if not file_path:
            return

        confirmar = messagebox.askyesno("Importar Inventario", 
                                        "Se cargarán los productos del archivo seleccionado.\n\n¿Desea continuar?")
        if not confirmar:
            return

        resumen = importar_inventario_desde_excel(file_path)
        
        if resumen["mensaje"] == "Proceso completado.":
            mensaje_final = (f"Importación finalizada.\n\n"
                             f"✅ Leídos: {resumen['total_leidos']}\n"
                             f"✅ Agregados: {resumen['exitos']}\n"
                             f"⚠️ Errores/Duplicados: {resumen['errores']}")
            messagebox.showinfo("Resumen", mensaje_final)
            self.actualizar_lista_productos()
        else:
            messagebox.showerror("Error", resumen["mensaje"])

    # --- Funciones para la Vista de Gestión de Cotizaciones ---

    def create_quotes_view(self):
        for widget in self.quotes_frame.winfo_children():
            widget.destroy()
            
        self.selected_quote_id = None
        
        self.quotes_frame.grid_columnconfigure(0, weight=1)
        self.quotes_frame.grid_columnconfigure(1, weight=1)
        self.quotes_frame.grid_rowconfigure(0, weight=1)
        
        # --- Columna Izquierda: Lista de Cotizaciones - Mejorada ---
        quotes_list_frame = ctk.CTkFrame(self.quotes_frame, corner_radius=12)
        quotes_list_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        quotes_list_frame.grid_rowconfigure(1, weight=1)
        quotes_list_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(quotes_list_frame, text="Cotizaciones Pendientes", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        quotes_tree_frame = ctk.CTkFrame(quotes_list_frame, fg_color="transparent")
        quotes_tree_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0,15), sticky="nsew")
        quotes_tree_frame.grid_rowconfigure(0, weight=1)
        quotes_tree_frame.grid_columnconfigure(0, weight=1)
        
        q_columns = ("id", "fecha", "cliente", "total")
        self.quotes_tree = ttk.Treeview(quotes_tree_frame, columns=q_columns, show="headings", style="Custom.Treeview")
        
        self.quotes_tree.heading("id", text="ID")
        self.quotes_tree.column("id", width=60, stretch=False, anchor="center")
        self.quotes_tree.heading("fecha", text="Fecha")
        self.quotes_tree.column("fecha", width=150, anchor="w")
        self.quotes_tree.heading("cliente", text="Cliente")
        self.quotes_tree.column("cliente", width=250, stretch=True, anchor="w")
        self.quotes_tree.heading("total", text="Total")
        self.quotes_tree.column("total", width=120, anchor="e")
        
        self.quotes_tree.grid(row=0, column=0, sticky="nsew")
        
        q_scrollbar = ttk.Scrollbar(quotes_tree_frame, orient=tk.VERTICAL, command=self.quotes_tree.yview)
        self.quotes_tree.configure(yscrollcommand=q_scrollbar.set)
        q_scrollbar.grid(row=0, column=1, sticky="ns")

        refresh_button = ctk.CTkButton(
            quotes_list_frame, 
            text="Actualizar Lista", 
            command=self.update_quotes_list,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        refresh_button.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")

        # --- Columna Derecha: Detalle de Cotización - Mejorada ---
        quote_detail_frame = ctk.CTkFrame(self.quotes_frame, corner_radius=12)
        quote_detail_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        quote_detail_frame.grid_rowconfigure(1, weight=1)
        quote_detail_frame.grid_columnconfigure(0, weight=1)

        self.quote_detail_label = ctk.CTkLabel(
            quote_detail_frame, 
            text="Seleccione una cotización", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.quote_detail_label.grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")

        detail_tree_frame = ctk.CTkFrame(quote_detail_frame, fg_color="transparent")
        detail_tree_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0,15), sticky="nsew")
        detail_tree_frame.grid_rowconfigure(0, weight=1)
        detail_tree_frame.grid_columnconfigure(0, weight=1)
        
        d_columns = ("producto", "cantidad", "precio_unit", "subtotal")
        self.quote_detail_tree = ttk.Treeview(detail_tree_frame, columns=d_columns, show="headings", style="Custom.Treeview")
        
        self.quote_detail_tree.heading("producto", text="Producto")
        self.quote_detail_tree.column("producto", width=250, stretch=True, anchor="w")
        self.quote_detail_tree.heading("cantidad", text="Cant.")
        self.quote_detail_tree.column("cantidad", width=70, stretch=False, anchor="center")
        self.quote_detail_tree.heading("precio_unit", text="Precio Unit.")
        self.quote_detail_tree.column("precio_unit", width=120, anchor="e")
        self.quote_detail_tree.heading("subtotal", text="Subtotal")
        self.quote_detail_tree.column("subtotal", width=120, anchor="e")
        
        self.quote_detail_tree.grid(row=0, column=0, sticky="nsew")
        
        d_scrollbar = ttk.Scrollbar(detail_tree_frame, orient=tk.VERTICAL, command=self.quote_detail_tree.yview)
        self.quote_detail_tree.configure(yscrollcommand=d_scrollbar.set)
        d_scrollbar.grid(row=0, column=1, sticky="ns")

        # --- Botones de Acción - Mejorados ---
        action_buttons_frame = ctk.CTkFrame(quote_detail_frame, fg_color="transparent")
        action_buttons_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        action_buttons_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.convert_quote_button = ctk.CTkButton(
            action_buttons_frame, 
            text="Convertir a Venta", 
            fg_color=COLORS['success'], 
            hover_color=COLORS['success_hover'],
            command=self.on_convert_quote_to_sale,
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.convert_quote_button.grid(row=0, column=0, padx=(0,6), sticky="ew")
        
        self.modify_quote_button = ctk.CTkButton(
            action_buttons_frame, 
            text="Modificar",
            fg_color=COLORS['warning'], 
            hover_color=COLORS['warning_hover'],
            command=self.on_modify_quote,
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.modify_quote_button.grid(row=0, column=1, padx=6, sticky="ew")

        self.duplicate_quote_button = ctk.CTkButton(
            action_buttons_frame, 
            text="Duplicar",
            fg_color=COLORS['info'], 
            hover_color=COLORS['info_hover'],
            command=self.on_duplicate_quote,
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.duplicate_quote_button.grid(row=0, column=2, padx=6, sticky="ew")

        self.delete_quote_button = ctk.CTkButton(
            action_buttons_frame, 
            text="Eliminar",
            fg_color=COLORS['danger'], 
            hover_color=COLORS['danger_hover'],
            command=self.on_delete_quote,
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.delete_quote_button.grid(row=0, column=3, padx=(6,0), sticky="ew")
        
        self.quotes_tree.bind("<<TreeviewSelect>>", self.on_select_quote)
        self.update_quotes_list()
        self.clear_quote_details()
    
    
    def update_quotes_list(self):
        for item in self.quotes_tree.get_children():
            self.quotes_tree.delete(item)
            
        cotizaciones = obtener_todas_las_cotizaciones()
        
        for q in cotizaciones:
            fecha_simple = q['fecha_hora'].split(" ")[0]
            self.quotes_tree.insert("", tk.END, values=(
                q['id'],
                fecha_simple,
                q['cliente_nombre'],
                f"${q['total']:.2f}"
            ))

    def on_select_quote(self, event):
        selected_items = self.quotes_tree.selection()
        if not selected_items:
            return
            
        quote_id = self.quotes_tree.item(selected_items[0])['values'][0]
        self.selected_quote_id = int(quote_id)
        
        cliente = self.quotes_tree.item(selected_items[0])['values'][2]
        self.quote_detail_label.configure(text=f"Cotización #{quote_id} - {cliente}")
        
        for item in self.quote_detail_tree.get_children():
            self.quote_detail_tree.delete(item)
            
        detalles = obtener_detalle_cotizacion(self.selected_quote_id)
        for d in detalles:
            subtotal = d['cantidad'] * d['precio_unitario_momento']
            self.quote_detail_tree.insert("", tk.END, values=(
                d['nombre'],
                d['cantidad'],
                f"${d['precio_unitario_momento']:.2f}",
                f"${subtotal:.2f}"
            ))
            
        self.convert_quote_button.configure(state="normal")
        self.modify_quote_button.configure(state="normal")
        self.duplicate_quote_button.configure(state="normal")
        self.delete_quote_button.configure(state="normal")

    def clear_quote_details(self):
        self.selected_quote_id = None
        self.quote_detail_label.configure(text="Seleccione una cotización")
        
        for item in self.quote_detail_tree.get_children():
            self.quote_detail_tree.delete(item)
            
        if self.quotes_tree.selection():
            self.quotes_tree.selection_remove(self.quotes_tree.selection())
            
        self.convert_quote_button.configure(state="disabled")
        self.modify_quote_button.configure(state="disabled")
        self.duplicate_quote_button.configure(state="disabled")
        self.delete_quote_button.configure(state="disabled")
        
    def on_convert_quote_to_sale(self):
        if self.selected_quote_id is None:
            return
        
        confirmar = messagebox.askyesno("Confirmar Conversión",
                                        f"¿Está seguro de que desea convertir la Cotización #{self.selected_quote_id} en una VENTA?\n\nEl stock será descontado y la cotización será eliminada.")
        if not confirmar:
            return
            
        exito, mensaje = convertir_cotizacion_a_venta(self.selected_quote_id)
        
        if exito:
            messagebox.showinfo("Éxito", f"¡Conversión exitosa!\n{mensaje}")
            self.update_quotes_list()
            self.clear_quote_details()
        else:
            messagebox.showerror("Error de Conversión", f"No se pudo completar la conversión.\n\nMotivo: {mensaje}\n(La cotización NO fue eliminada).")

    def on_modify_quote(self):
        if self.selected_quote_id is None:
            return

        cliente_nombre = self.quotes_tree.item(self.quotes_tree.selection()[0])['values'][2]
        confirmar = messagebox.askyesno("Confirmar Modificación",
                                        f"¿Desea modificar la Cotización #{self.selected_quote_id} para '{cliente_nombre}'?\n\nLa cotización actual será ELIMINADA y sus productos se cargarán en el carrito de ventas para que pueda editarlos.")
        if not confirmar:
            return

        detalles = obtener_detalle_cotizacion(self.selected_quote_id)
        if not detalles:
            messagebox.showerror("Error", "No se pudieron cargar los detalles de esta cotización.")
            return

        self.carrito = []
        
        for item in detalles:
            self.agregar_producto_al_carrito(item['codigo_barras'], item['cantidad'])

        exito_eliminar = eliminar_cotizacion_completa(self.selected_quote_id)
        
        if not exito_eliminar:
            messagebox.showerror("Error", "No se pudo eliminar la cotización antigua. Abortando modificación.")
            self.carrito = [] 
            self.actualizar_carrito_gui()
            return
            
        self.update_quotes_list()
        self.clear_quote_details()
        
        self.select_frame_by_name("home")
        
        messagebox.showinfo("Listo para Modificar", 
                            f"Los productos de la cotización #{self.selected_quote_id} están en el carrito.\n\nRealice sus cambios y presione 'Generar Cotización' para guardarla como una nueva.")

    def on_duplicate_quote(self):
        if self.selected_quote_id is None:
            return

        cliente_nombre = self.quotes_tree.item(self.quotes_tree.selection()[0])['values'][2]
        confirmar = messagebox.askyesno("Confirmar Duplicación",
                                        f"¿Desea duplicar la Cotización #{self.selected_quote_id} de '{cliente_nombre}'?\n\nLa cotización original se conservará y sus productos se cargarán en el carrito de ventas.")
        if not confirmar:
            return

        detalles = obtener_detalle_cotizacion(self.selected_quote_id)
        if not detalles:
            messagebox.showerror("Error", "No se pudieron cargar los detalles de esta cotización.")
            return

        self.carrito = []
        
        for item in detalles:
            self.agregar_producto_al_carrito(item['codigo_barras'], item['cantidad'])
            
        self.clear_quote_details()
        self.select_frame_by_name("home")
        
        messagebox.showinfo("Listo para Duplicar", 
                            f"Los productos de la cotización #{self.selected_quote_id} están en el carrito.\n\nPresione 'Generar Cotización' para guardarla con un nuevo nombre de cliente.")

    def on_delete_quote(self):
        if self.selected_quote_id is None:
            return
            
        confirmar = messagebox.askyesno("Confirmar Eliminación",
                                        f"¿Está seguro de que desea ELIMINAR permanentemente la Cotización #{self.selected_quote_id}?\n\nEsta acción no se puede deshacer.")
        if not confirmar:
            return

        exito = eliminar_cotizacion_completa(self.selected_quote_id)
        
        if exito:
            messagebox.showinfo("Éxito", f"Cotización #{self.selected_quote_id} eliminada correctamente.")
            self.update_quotes_list()
            self.clear_quote_details()
        else:
            messagebox.showerror("Error", "No se pudo eliminar la cotización.")


    # --- Funciones de Búsqueda en POS ---
    
    def handle_scan_or_search(self, event=None):
        termino = self.scan_entry.get()
        if not termino:
            return

        producto_por_codigo = buscar_producto_por_codigo(termino)
        
        if producto_por_codigo:
            self.agregar_producto_al_carrito(producto_por_codigo['codigo_barras'])
            self.scan_entry.delete(0, 'end')
            self.scan_entry.focus_set()
            return

        productos_por_nombre = buscar_productos_por_nombre(termino)
        
        if not productos_por_nombre:
            messagebox.showwarning("Búsqueda Fallida", f"No se encontró ningún producto con el código o nombre: '{termino}'")
            return
            
        if len(productos_por_nombre) == 1:
            producto_encontrado = productos_por_nombre[0]
            self.agregar_producto_al_carrito(producto_encontrado['codigo_barras'])
            self.scan_entry.delete(0, 'end')
            self.scan_entry.focus_set()
            return
            
        if len(productos_por_nombre) > 1:
            self.open_search_popup(productos_por_nombre)

    def open_search_popup(self, productos):
        popup = ctk.CTkToplevel(self)
        popup.title("Resultados de Búsqueda")
        popup.geometry("500x400")
        
        popup.transient(self)
        popup.grab_set()
        
        popup.grid_columnconfigure(0, weight=1)
        popup.grid_rowconfigure(0, weight=1)

        scroll_frame = ctk.CTkScrollableFrame(popup, label_text="Seleccione un producto", corner_radius=10)
        scroll_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        for producto in productos:
            texto_boton = f"{producto['nombre']} (Stock: {producto['stock']})"
            btn = ctk.CTkButton(
                scroll_frame, 
                text=texto_boton,
                anchor="w",
                height=45,
                corner_radius=8,
                font=ctk.CTkFont(size=13),
                command=lambda cod=producto['codigo_barras'], p=popup: self.add_from_popup(cod, p)
            )
            btn.grid(row=productos.index(producto), column=0, padx=5, pady=4, sticky="ew")
            
        if scroll_frame.winfo_children():
            scroll_frame.winfo_children()[0].focus_set()

    def add_from_popup(self, codigo_barras, popup_window):
        self.agregar_producto_al_carrito(codigo_barras)
        
        self.scan_entry.delete(0, 'end')
        self.scan_entry.focus_set()
        
        popup_window.destroy()
    

    # --- Métodos de la Vista de Inventario (CRUD) ---
    
    def on_select_producto(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        producto_id = self.tree.item(selected_items[0])['values'][0]
        
        productos = obtener_productos()
        producto_data = None
        for p in productos:
            if p['id'] == producto_id:
                producto_data = p
                break
        
        if not producto_data:
            self.on_limpiar_formulario()
            return

        self.inv_entry_codigo.delete(0, 'end')
        self.inv_entry_codigo.insert(0, producto_data.get('codigo_barras', ''))
        self.inv_entry_nombre.delete(0, 'end')
        self.inv_entry_nombre.insert(0, producto_data.get('nombre', ''))
        self.inv_entry_desc.delete(0, 'end')
        self.inv_entry_desc.insert(0, producto_data.get('descripcion', ''))
        self.inv_entry_marca.delete(0, 'end')
        self.inv_entry_marca.insert(0, producto_data.get('marca', ''))
        self.inv_entry_precio.delete(0, 'end')
        self.inv_entry_precio.insert(0, str(producto_data.get('precio_venta', 0.0)))
        self.inv_entry_stock.delete(0, 'end')
        self.inv_entry_stock.insert(0, str(producto_data.get('stock', 0)))
        
        self.selected_product_id = producto_id
        
        self.add_button.configure(state="disabled")
        self.edit_button.configure(state="normal")
        self.delete_button.configure(state="normal")

    def on_limpiar_formulario(self):
        self.inv_entry_codigo.delete(0, 'end')
        self.inv_entry_nombre.delete(0, 'end')
        self.inv_entry_desc.delete(0, 'end')
        self.inv_entry_marca.delete(0, 'end')
        self.inv_entry_precio.delete(0, 'end')
        self.inv_entry_stock.delete(0, 'end')
        
        self.selected_product_id = None
        
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        
        self.add_button.configure(state="normal")
        self.edit_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")
        
        self.inv_entry_codigo.focus_set()

    def on_editar_producto(self):
        if self.selected_product_id is None:
            return

        codigo = self.inv_entry_codigo.get()
        nombre = self.inv_entry_nombre.get()
        desc = self.inv_entry_desc.get()
        marca = self.inv_entry_marca.get()
        precio_str = self.inv_entry_precio.get()
        stock_str = self.inv_entry_stock.get()
        
        if not codigo or not nombre or not precio_str or not stock_str:
            messagebox.showerror("Error de Formulario", "Código, Nombre, Precio y Stock son obligatorios.")
            return
        try:
            precio = float(precio_str)
            stock = int(stock_str)
        except ValueError:
            messagebox.showerror("Error de Formulario", "El Precio y el Stock deben ser números.")
            return

        exito = editar_producto(id_producto=self.selected_product_id,
                                nombre=nombre,
                                descripcion=desc,
                                marca=marca,
                                precio_venta=precio,
                                stock=stock,
                                codigo_barras=codigo)
        
        if exito:
            messagebox.showinfo("Éxito", f"Producto '{nombre}' actualizado correctamente.")
            self.actualizar_lista_productos()
            self.on_limpiar_formulario()
        else:
            messagebox.showwarning("Error de Base de Datos", "No se pudo actualizar el producto. Es posible que el Código de Barras ya exista.")

    def on_eliminar_producto(self):
        if self.selected_product_id is None:
            return
            
        nombre_producto = self.inv_entry_nombre.get()
        confirmar = messagebox.askyesno("Confirmar Eliminación", 
                                           f"¿Está seguro de que desea eliminar el producto '{nombre_producto}'?\n\nEsta acción no se puede deshacer.")
        
        if not confirmar:
            return

        exito = eliminar_producto(self.selected_product_id)
        
        if exito:
            messagebox.showinfo("Éxito", f"Producto '{nombre_producto}' eliminado.")
            self.actualizar_lista_productos()
            self.on_limpiar_formulario()
        else:
            messagebox.showerror("Error al Eliminar", "No se pudo eliminar el producto. Es probable que ya esté incluido en una venta registrada.")
            
    def actualizar_lista_productos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        productos = obtener_productos()
        self.productos_completos = productos  # Guardar para filtrado
        
        for p in productos:
            self.tree.insert("", tk.END, values=(
                p['id'],
                p['codigo_barras'],
                p['nombre'],
                p.get('marca', ''),
                f"${p['precio_venta']:.2f}",
                p['stock']
            ))
    
    def filtrar_productos(self):
        """Filtra los productos según el término de búsqueda y el filtro seleccionado"""
        termino = self.inv_search_entry.get().lower()
        filtro = self.inv_filter_var.get()
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filtrar productos
        productos_filtrados = []
        for p in self.productos_completos:
            # Filtro de búsqueda
            coincide_busqueda = (
                not termino or
                termino in p.get('nombre', '').lower() or
                termino in p.get('codigo_barras', '').lower() or
                termino in p.get('marca', '').lower()
            )
            
            # Filtro de stock
            coincide_filtro = True
            if filtro == "Con Stock":
                coincide_filtro = p.get('stock', 0) > 0
            elif filtro == "Sin Stock":
                coincide_filtro = p.get('stock', 0) == 0
            elif filtro == "Bajo Stock (<10)":
                coincide_filtro = 0 < p.get('stock', 0) < 10
            
            if coincide_busqueda and coincide_filtro:
                productos_filtrados.append(p)
        
        # Mostrar productos filtrados
        for p in productos_filtrados:
            self.tree.insert("", tk.END, values=(
                p['id'],
                p['codigo_barras'],
                p['nombre'],
                p.get('marca', ''),
                f"${p['precio_venta']:.2f}",
                p['stock']
            ))

    def on_agregar_producto(self):
        codigo = self.inv_entry_codigo.get()
        nombre = self.inv_entry_nombre.get()
        desc = self.inv_entry_desc.get()
        marca = self.inv_entry_marca.get()
        precio_str = self.inv_entry_precio.get()
        stock_str = self.inv_entry_stock.get()

        if not codigo or not nombre or not precio_str or not stock_str:
            messagebox.showerror("Error de Formulario", "Código, Nombre, Precio y Stock son obligatorios.")
            return
            
        try:
            precio = float(precio_str)
            stock = int(stock_str)
        except ValueError:
            messagebox.showerror("Error de Formulario", "El Precio (Ej: 1500.0) y el Stock (Ej: 100) deben ser números.")
            return

        exito = agregar_producto(codigo_barras=codigo, 
                                 nombre=nombre, 
                                 descripcion=desc,
                                 marca=marca,
                                 precio_venta=precio, 
                                 stock=stock)

        if exito:
            messagebox.showinfo("Éxito", f"Producto '{nombre}' agregado correctamente.")
            self.actualizar_lista_productos()
            self.on_limpiar_formulario()
        else:
            messagebox.showwarning("Error de Base de Datos", "No se pudo agregar el producto. Es posible que el Código de Barras ya exista.")


    # --- Métodos de Navegación ---
    
    def select_frame_by_name(self, name):
        active_color = COLORS['sidebar_hover']
        
        self.home_button.configure(fg_color=active_color if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=active_color if name == "inventory" else "transparent")
        self.quotes_button.configure(fg_color=active_color if name == "quotes" else "transparent")
        self.reports_button.configure(fg_color=active_color if name == "reports" else "transparent")

        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
            self.scan_entry.focus_set() 
        else:
            self.home_frame.grid_forget()

        if name == "inventory":
            self.inventory_frame.grid(row=0, column=1, sticky="nsew")
            self.create_inventory_view() 
        else:
            self.inventory_frame.grid_forget()
            
        if name == "quotes":
            self.quotes_frame.grid(row=0, column=1, sticky="nsew")
            self.create_quotes_view()
        else:
            self.quotes_frame.grid_forget()


    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("inventory")
        
    def quotes_button_event(self):
        self.select_frame_by_name("quotes")
        

if __name__ == "__main__":
    app = App()
    app.mainloop()

