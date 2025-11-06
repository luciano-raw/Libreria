import customtkinter as ctk
from tkinter import ttk 
import tkinter as tk 
from tkinter import messagebox 

import os
from tkinter import messagebox
import customtkinter as ctk
from cotizacion_pdf import generar_pdf_cotizacion

# --- AÑADIDO: Importaciones para iconos ---
from PIL import Image
import os
# --- FIN DE AÑADIDOS ---

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

from ticket import imprimir_boleta 


# Configuración global de la librería
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
        

class App(ctk.CTk):

    # --- FUNCIÓN AUXILIAR NUEVA ---
    def load_icon(self, name, size=(24, 24)):
        """Carga un icono desde la carpeta 'assets' de forma segura."""
        path = os.path.join(self.assets_path, name)
        try:
            # Carga la imagen usando Pillow y luego la convierte a CTkImage
            img = Image.open(path)
            return ctk.CTkImage(img, size=size)
        except Exception as e:
            print(f"Error cargando icono '{name}': {e}. Se usará un placeholder gris.")
            # Retorna un placeholder gris si el archivo falta o está corrupto
            placeholder = Image.new("RGB", size, "gray")
            return ctk.CTkImage(placeholder, size=size)
    # --- FIN DE FUNCIÓN AUXILIAR ---

    def __init__(self):
        super().__init__()

        # --- Variables del Carrito y Venta ---
        self.carrito = [] 
        self.total_venta = ctk.StringVar(value="0.00") 
        self.selected_product_id = None
        self.selected_quote_id = None
        
        # --- Configuración principal de la ventana ---
        self.title("Sistema POS para Librería")
        self.geometry("1100x580")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Barra Lateral (Navigation Frame) ---
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1) 
        
        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, 
                                                   text="📚 Librería POS", 
                                                   compound="left", 
                                                   font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # --- INICIO DE MODIFICACIÓN: Carga de Iconos ---
        
        # 1. Definir la ruta a la carpeta de assets
        self.assets_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        
        # 2. Crear la carpeta 'assets' si no existe
        if not os.path.exists(self.assets_path):
            os.makedirs(self.assets_path)
            print(f"Se ha creado la carpeta 'assets' en: {self.assets_path}")
            print("Por favor, añade los iconos .png a esta carpeta.")

        # 3. Cargar imágenes (AHORA DE FORMA INDIVIDUAL Y SEGURA)
        self.icon_sales = self.load_icon("icon_sales.png")
        self.icon_inventory = self.load_icon("icon_inventory.png")
        self.icon_quotes = self.load_icon("icon_quotes.png")
        self.icon_reports = self.load_icon("icon_reports.png")
        
        # --- FIN DE LA CARGA MODIFICADA ---


        # 4. Modificar Botones para incluir iconos
        self.home_button = ctk.CTkButton(self.navigation_frame, 
                                         corner_radius=0, height=40, 
                                         border_spacing=10, 
                                         text="Ventas (POS)", 
                                         fg_color="transparent", 
                                         text_color=("gray10", "gray90"), 
                                         hover_color=("gray60", "gray40"), 
                                         anchor="w", 
                                         image=self.icon_sales, # <-- AÑADIDO
                                         compound="left",      # <-- AÑADIDO
                                         command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = ctk.CTkButton(self.navigation_frame, 
                                            corner_radius=0, height=40, 
                                            border_spacing=10, 
                                            text="Gestión de Inventario", 
                                            fg_color="transparent", 
                                            text_color=("gray10", "gray90"), 
                                            hover_color=("gray60", "gray40"), 
                                            anchor="w", 
                                            image=self.icon_inventory, # <-- AÑADIDO
                                            compound="left",         # <-- AÑADIDO
                                            command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.quotes_button = ctk.CTkButton(self.navigation_frame, 
                                            corner_radius=0, height=40, 
                                            border_spacing=10, 
                                            text="Gestión de Cotizaciones", 
                                            fg_color="transparent", 
                                            text_color=("gray10", "gray90"), 
                                            hover_color=("gray60", "gray40"), 
                                            anchor="w", 
                                            image=self.icon_quotes, # <-- AÑADIDO
                                            compound="left",      # <-- AÑADIDO
                                            command=self.quotes_button_event)
        self.quotes_button.grid(row=3, column=0, sticky="ew")
        
        # --- Botón de Reportes (preparado para el futuro) ---
        self.reports_button = ctk.CTkButton(self.navigation_frame, 
                                            corner_radius=0, height=40, 
                                            border_spacing=10, 
                                            text="Reportes (Próximamente)", 
                                            fg_color="transparent", 
                                            text_color=("gray50", "gray50"), 
                                            hover_color=("gray60", "gray40"), 
                                            anchor="w", 
                                            image=self.icon_reports, # <-- AÑADIDO
                                            compound="left",      # <-- AÑADIDO
                                            state="disabled") # Deshabilitado por ahora
        self.reports_button.grid(row=4, column=0, sticky="ew")
        
        # --- FIN DE MODIFICACIÓN ---


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

    def actualizar_carrito_gui(self):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()

        self.cart_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.cart_frame, text="Producto", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, sticky="w")
        ctk.CTkLabel(self.cart_frame, text="Cant.", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5)
        ctk.CTkLabel(self.cart_frame, text="Precio", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5)
        ctk.CTkLabel(self.cart_frame, text="Subtotal", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, sticky="e")
        ctk.CTkLabel(self.cart_frame, text=" ", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5) 

        for i, item in enumerate(self.carrito):
            row = i + 1 
            subtotal = item['precio'] * item['cantidad']
            
            ctk.CTkLabel(self.cart_frame, text=item['nombre']).grid(row=row, column=0, padx=5, pady=2, sticky="w")
            ctk.CTkLabel(self.cart_frame, text=str(item['cantidad'])).grid(row=row, column=1, padx=5, pady=2)
            ctk.CTkLabel(self.cart_frame, text=f"${item['precio']:.2f}").grid(row=row, column=2, padx=5, pady=2)
            ctk.CTkLabel(self.cart_frame, text=f"${subtotal:.2f}").grid(row=row, column=3, padx=5, pady=2, sticky="e")
            
            remove_button = ctk.CTkButton(self.cart_frame, text="🗑️", width=30, height=20, 
                                          command=lambda item_id=item['id']: self.remover_item_carrito(item_id))
            remove_button.grid(row=row, column=4, padx=5, pady=2)

        self.total_venta.set(f"{self.calcular_total():.2f}")

    def remover_item_carrito(self, item_id):
        self.carrito = [item for item in self.carrito if item['id'] != item_id]
        self.actualizar_carrito_gui()
        
    def agregar_producto_al_carrito(self, codigo_barras, cantidad=1):
        producto_data = buscar_producto_por_codigo(codigo_barras)
        
        if not producto_data:
            print(f"Error: Producto con código {codigo_barras} no encontrado.")
            return
            
        producto_id = producto_data['id']
        precio = producto_data['precio_venta']
        
        # Verificar si el producto ya está en el carrito
        for item in self.carrito:
            if item['id'] == producto_id:
                item['cantidad'] += cantidad
                self.actualizar_carrito_gui()
                return

        # Si no está, agregarlo como un nuevo ítem
        self.carrito.append({
            'id': producto_id,
            'nombre': producto_data['nombre'],
            'cantidad': cantidad, # Usar la cantidad especificada
            'precio': precio,
        })
        
        self.actualizar_carrito_gui()
        
    # --- Manejadores de Venta/Cotización ---
    
    def process_sale(self):
        if not self.carrito:
            print("El carrito está vacío.")
            return

        carrito_db = [{'id': item['id'], 'cantidad': item['cantidad'], 'precio_unitario': item['precio']} for item in self.carrito]
        total = self.calcular_total()
        
        venta_id = registrar_venta(carrito_db, total)
        
        if venta_id:
            print(f"Venta registrada con éxito. ID: {venta_id}. TOTAL: ${total:.2f}")
            
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
            print("ERROR: Fallo al procesar la venta.")
            
    def generate_quote(self):
        if not self.carrito:
            print("El carrito está vacío.")
            messagebox.showwarning("Carrito Vacío", "No se puede generar una cotización con el carrito vacío.")
            return

        dialog = ctk.CTkInputDialog(text="Ingrese el nombre del cliente para la cotización:", 
                                    title="Generar Cotización")
        
        cliente_nombre = dialog.get_input() 
        
        if not cliente_nombre:
            print("Generación de cotización cancelada por el usuario.")
            return

        carrito_db = [{'id': item['id'], 'cantidad': item['cantidad'], 'precio_unitario': item['precio']} for item in self.carrito]
        total = self.calcular_total()
        
        cotizacion_id = registrar_cotizacion(carrito_db, total, cliente=cliente_nombre)
        
        if cotizacion_id:
            print(f"Cotización ID {cotizacion_id} registrada para '{cliente_nombre}'.")

            pdf_data = {
                'id': cotizacion_id,
                'cliente_nombre': cliente_nombre,
                'total': total,
                'detalle': [{'nombre': item['nombre'], 
                             'cantidad': item['cantidad'], 
                             'precio_unitario': item['precio']} 
                            for item in self.carrito]
            }

            ruta_pdf = generar_pdf_cotizacion(pdf_data)
            
            if ruta_pdf:
                respuesta = messagebox.askyesno("Éxito", 
                                                f"Cotización para '{cliente_nombre}' generada exitosamente.\n\n¿Desea abrir la carpeta de cotizaciones?",
                                                icon='info')
                if respuesta:
                    try:
                        os.startfile(os.path.dirname(ruta_pdf))
                    except AttributeError:
                        print(f"No se pudo abrir la carpeta automáticamente. Acceda manualmente a: {os.path.dirname(ruta_pdf)}")
                    except Exception as e:
                        print(f"Error al intentar abrir la carpeta: {e}")
            else:
                messagebox.showerror("Error de PDF", "La cotización se guardó en la base de datos, pero falló la generación del archivo PDF.")

            self.carrito = [] 
            self.actualizar_carrito_gui()
            
        else:
            print("ERROR: Fallo al registrar la cotización en la BD.")
            messagebox.showerror("Error de Base de Datos", "Fallo grave: No se pudo registrar la cotización en la base de datos.")

    # --- Creación de Vistas ---

    def create_home_view(self):
        self.home_frame.grid_columnconfigure(0, weight=3)
        self.home_frame.grid_columnconfigure(1, weight=1)
        self.home_frame.grid_rowconfigure(1, weight=1) 
        
        self.scan_entry = ctk.CTkEntry(self.home_frame, 
                                       placeholder_text="Escanear Código o Buscar por Nombre...",
                                       height=40,
                                       font=ctk.CTkFont(size=14))
        self.scan_entry.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="new")
        self.scan_entry.bind("<Return>", self.handle_scan_or_search)
        
        self.cart_frame = ctk.CTkScrollableFrame(self.home_frame, 
                                                 label_text="Productos en Carrito",
                                                 corner_radius=10)
        self.cart_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.cart_frame.grid_columnconfigure(0, weight=1)
        
        self.actualizar_carrito_gui()
        
        self.summary_frame = ctk.CTkFrame(self.home_frame, corner_radius=10)
        self.summary_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.summary_frame.grid_columnconfigure(0, weight=1)
        self.summary_frame.grid_rowconfigure(4, weight=1) 
        
        ctk.CTkLabel(self.summary_frame, 
                     text="TOTAL A PAGAR", 
                     font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=(15, 5))

        ctk.CTkLabel(self.summary_frame, 
                     textvariable=self.total_venta, 
                     text_color="#FFD700" if ctk.get_appearance_mode() == "Dark" else "#D32F2F", 
                     font=ctk.CTkFont(size=36, weight="bold")).grid(row=1, column=0, pady=(0, 20))
        
        self.sell_button = ctk.CTkButton(self.summary_frame, 
                                         text="✅ PROCESAR VENTA", 
                                         height=50, 
                                         fg_color="#4CAF50", 
                                         hover_color="#45a049",
                                         font=ctk.CTkFont(size=16, weight="bold"),
                                         command=self.process_sale) 
        self.sell_button.grid(row=5, column=0, padx=15, pady=(10, 5), sticky="s")
        
        self.quote_button = ctk.CTkButton(self.summary_frame, 
                                          text="📋 GENERAR COTIZACIÓN", 
                                          height=50, 
                                          fg_color="#2196F3", 
                                          hover_color="#1e88e5",
                                          command=self.generate_quote) 
        self.quote_button.grid(row=6, column=0, padx=15, pady=(5, 15), sticky="s")


    def create_inventory_view(self):
        for widget in self.inventory_frame.winfo_children():
            widget.destroy()
            
        self.inventory_frame.grid_columnconfigure(0, weight=1)
        self.inventory_frame.grid_rowconfigure(0, weight=0)
        self.inventory_frame.grid_rowconfigure(1, weight=0)
        self.inventory_frame.grid_rowconfigure(2, weight=1)

        form_frame = ctk.CTkFrame(self.inventory_frame, corner_radius=10)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        form_frame.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(form_frame, text="Código Barras:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.inv_entry_codigo = ctk.CTkEntry(form_frame, placeholder_text="Código...")
        self.inv_entry_codigo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Nombre:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.inv_entry_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombre del producto...")
        self.inv_entry_nombre.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Descripción (Opcional):").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.inv_entry_desc = ctk.CTkEntry(form_frame, placeholder_text="Descripción...")
        self.inv_entry_desc.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Precio Venta:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.inv_entry_precio = ctk.CTkEntry(form_frame, placeholder_text="Ej: 1500.00")
        self.inv_entry_precio.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Stock Inicial:").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.inv_entry_stock = ctk.CTkEntry(form_frame, placeholder_text="Ej: 100")
        self.inv_entry_stock.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        action_frame = ctk.CTkFrame(self.inventory_frame, corner_radius=0, fg_color="transparent")
        action_frame.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")
        action_frame.grid_columnconfigure(3, weight=1)

        self.add_button = ctk.CTkButton(action_frame, text="➕ Agregar Producto", 
                                   command=self.on_agregar_producto,
                                   fg_color="#4CAF50", hover_color="#45a049")
        self.add_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.edit_button = ctk.CTkButton(action_frame, text="💾 Guardar Cambios", 
                                    command=self.on_editar_producto,
                                    fg_color="#FF9800", hover_color="#FB8C00")
        self.edit_button.grid(row=0, column=1, padx=5, pady=5)

        self.delete_button = ctk.CTkButton(action_frame, text="❌ Eliminar Producto", 
                                      command=self.on_eliminar_producto,
                                      fg_color="#f44336", hover_color="#d32f2f")
        self.delete_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.clear_button = ctk.CTkButton(action_frame, text="🧹 Limpiar Formulario", 
                                     command=self.on_limpiar_formulario,
                                     fg_color="gray", hover_color="gray25")
        self.clear_button.grid(row=0, column=3, padx=5, pady=5, sticky="e")

        tree_frame = ctk.CTkFrame(self.inventory_frame, corner_radius=10)
        tree_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("id", "codigo", "nombre", "precio", "stock")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=50, stretch=False, anchor="center")
        self.tree.heading("codigo", text="Código Barras")
        self.tree.column("codigo", width=150, anchor="w")
        self.tree.heading("nombre", text="Nombre")
        self.tree.column("nombre", width=300, stretch=True, anchor="w")
        self.tree.heading("precio", text="Precio Venta")
        self.tree.column("precio", width=100, anchor="e")
        self.tree.heading("stock", text="Stock")
        self.tree.column("stock", width=80, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.on_select_producto)
        self.actualizar_lista_productos()
        self.on_limpiar_formulario()


    # --- Funciones para la Vista de Gestión de Cotizaciones ---

    def create_quotes_view(self):
        for widget in self.quotes_frame.winfo_children():
            widget.destroy()
            
        self.selected_quote_id = None
        
        self.quotes_frame.grid_columnconfigure(0, weight=1)
        self.quotes_frame.grid_columnconfigure(1, weight=1)
        self.quotes_frame.grid_rowconfigure(0, weight=1)
        
        # --- Columna Izquierda: Lista de Cotizaciones ---
        quotes_list_frame = ctk.CTkFrame(self.quotes_frame, corner_radius=10)
        quotes_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        quotes_list_frame.grid_rowconfigure(1, weight=1)
        quotes_list_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(quotes_list_frame, text="Cotizaciones Pendientes", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        quotes_tree_frame = ctk.CTkFrame(quotes_list_frame)
        quotes_tree_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0,10), sticky="nsew")
        quotes_tree_frame.grid_rowconfigure(0, weight=1)
        quotes_tree_frame.grid_columnconfigure(0, weight=1)
        
        q_columns = ("id", "fecha", "cliente", "total")
        self.quotes_tree = ttk.Treeview(quotes_tree_frame, columns=q_columns, show="headings")
        
        self.quotes_tree.heading("id", text="ID")
        self.quotes_tree.column("id", width=50, stretch=False, anchor="center")
        self.quotes_tree.heading("fecha", text="Fecha")
        self.quotes_tree.column("fecha", width=150, anchor="w")
        self.quotes_tree.heading("cliente", text="Cliente")
        self.quotes_tree.column("cliente", width=200, stretch=True, anchor="w")
        self.quotes_tree.heading("total", text="Total")
        self.quotes_tree.column("total", width=100, anchor="e")
        
        self.quotes_tree.grid(row=0, column=0, sticky="nsew")
        
        q_scrollbar = ttk.Scrollbar(quotes_tree_frame, orient=tk.VERTICAL, command=self.quotes_tree.yview)
        self.quotes_tree.configure(yscrollcommand=q_scrollbar.set)
        q_scrollbar.grid(row=0, column=1, sticky="ns")
        
        refresh_button = ctk.CTkButton(quotes_list_frame, text="Actualizar Lista", command=self.update_quotes_list)
        refresh_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # --- Columna Derecha: Detalle de Cotización ---
        quote_detail_frame = ctk.CTkFrame(self.quotes_frame, corner_radius=10)
        quote_detail_frame.grid(row=0, column=1, padx=(0,10), pady=10, sticky="nsew")
        quote_detail_frame.grid_rowconfigure(1, weight=1)
        quote_detail_frame.grid_columnconfigure(0, weight=1)

        self.quote_detail_label = ctk.CTkLabel(quote_detail_frame, text="Seleccione una cotización", font=ctk.CTkFont(size=16, weight="bold"))
        self.quote_detail_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        detail_tree_frame = ctk.CTkFrame(quote_detail_frame)
        detail_tree_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0,10), sticky="nsew")
        detail_tree_frame.grid_rowconfigure(0, weight=1)
        detail_tree_frame.grid_columnconfigure(0, weight=1)
        
        d_columns = ("producto", "cantidad", "precio_unit", "subtotal")
        self.quote_detail_tree = ttk.Treeview(detail_tree_frame, columns=d_columns, show="headings")
        
        self.quote_detail_tree.heading("producto", text="Producto")
        self.quote_detail_tree.column("producto", width=200, stretch=True, anchor="w")
        self.quote_detail_tree.heading("cantidad", text="Cant.")
        self.quote_detail_tree.column("cantidad", width=50, stretch=False, anchor="center")
        self.quote_detail_tree.heading("precio_unit", text="Precio Unit.")
        self.quote_detail_tree.column("precio_unit", width=100, anchor="e")
        self.quote_detail_tree.heading("subtotal", text="Subtotal")
        self.quote_detail_tree.column("subtotal", width=100, anchor="e")
        
        self.quote_detail_tree.grid(row=0, column=0, sticky="nsew")
        
        d_scrollbar = ttk.Scrollbar(detail_tree_frame, orient=tk.VERTICAL, command=self.quote_detail_tree.yview)
        self.quote_detail_tree.configure(yscrollcommand=d_scrollbar.set)
        d_scrollbar.grid(row=0, column=1, sticky="ns")

        # --- Botones de Acción (con Duplicar) ---
        action_buttons_frame = ctk.CTkFrame(quote_detail_frame, fg_color="transparent")
        action_buttons_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        action_buttons_frame.grid_columnconfigure((0, 1, 2, 3), weight=1) # 4 columnas
        
        self.convert_quote_button = ctk.CTkButton(action_buttons_frame, text="✅ Convertir a Venta", 
                                             fg_color="#4CAF50", hover_color="#45a049",
                                             command=self.on_convert_quote_to_sale)
        self.convert_quote_button.grid(row=0, column=0, padx=(0,5), sticky="ew")
        
        self.modify_quote_button = ctk.CTkButton(action_buttons_frame, text="✏️ Modificar",
                                            fg_color="#FF9800", hover_color="#FB8C00",
                                            command=self.on_modify_quote)
        self.modify_quote_button.grid(row=0, column=1, padx=5, sticky="ew")

        self.duplicate_quote_button = ctk.CTkButton(action_buttons_frame, text="📋 Duplicar",
                                            fg_color="#00BCD4", hover_color="#00ACC1",
                                            command=self.on_duplicate_quote)
        self.duplicate_quote_button.grid(row=0, column=2, padx=5, sticky="ew")

        self.delete_quote_button = ctk.CTkButton(action_buttons_frame, text="❌ Eliminar",
                                            fg_color="#f44336", hover_color="#d32f2f",
                                            command=self.on_delete_quote)
        self.delete_quote_button.grid(row=0, column=3, padx=(5,0), sticky="ew")
        
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
        self.quote_detail_label.configure(text=f"Detalle Cotización #{quote_id} - {cliente}")
        
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
            
        # Habilitar los 4 botones
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
            
        # Deshabilitar los 4 botones
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
        
        print(f"Cargando {len(detalles)} productos al carrito...")
        for item in detalles:
            self.agregar_producto_al_carrito(item['codigo_barras'], item['cantidad'])
        
        print("Carrito cargado. Eliminando cotización antigua...")

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
        """
        Manejador para 'Duplicar Cotización'.
        Carga la cotización al carrito de ventas pero NO la elimina.
        """
        if self.selected_quote_id is None:
            return

        # 1. Confirmar
        cliente_nombre = self.quotes_tree.item(self.quotes_tree.selection()[0])['values'][2]
        confirmar = messagebox.askyesno("Confirmar Duplicación",
                                        f"¿Desea duplicar la Cotización #{self.selected_quote_id} de '{cliente_nombre}'?\n\nLa cotización original se conservará y sus productos se cargarán en el carrito de ventas.")
        if not confirmar:
            return

        # 2. Obtener detalles
        detalles = obtener_detalle_cotizacion(self.selected_quote_id)
        if not detalles:
            messagebox.showerror("Error", "No se pudieron cargar los detalles de esta cotización.")
            return

        # 3. Limpiar el carrito de ventas actual
        self.carrito = []
        
        # 4. Llenar el carrito de ventas con los productos de la cotización
        print(f"Cargando {len(detalles)} productos al carrito para duplicación...")
        for item in detalles:
            self.agregar_producto_al_carrito(item['codigo_barras'], item['cantidad'])
        
        print("Carrito cargado.")
            
        # 5. Deseleccionar la cotización en la pestaña de gestión
        self.clear_quote_details()
        
        # 6. Cambiar a la pestaña de Ventas
        self.select_frame_by_name("home")
        
        # 7. Informar al usuario
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
            print(f"Búsqueda por código exitosa: {producto_por_codigo['nombre']}")
            self.agregar_producto_al_carrito(producto_por_codigo['codigo_barras'])
            self.scan_entry.delete(0, 'end')
            self.scan_entry.focus_set()
            return

        print(f"Búsqueda por código falló. Buscando por nombre: '{termino}'...")
        productos_por_nombre = buscar_productos_por_nombre(termino)
        
        if not productos_por_nombre:
            print("Producto no encontrado por nombre.")
            messagebox.showwarning("Búsqueda Fallida", f"No se encontró ningún producto con el código o nombre: '{termino}'")
            return
            
        if len(productos_por_nombre) == 1:
            producto_encontrado = productos_por_nombre[0]
            print(f"Búsqueda por nombre exitosa (1 resultado): {producto_encontrado['nombre']}")
            self.agregar_producto_al_carrito(producto_encontrado['codigo_barras'])
            self.scan_entry.delete(0, 'end')
            self.scan_entry.focus_set()
            return
            
        if len(productos_por_nombre) > 1:
            print(f"Búsqueda por nombre encontró {len(productos_por_nombre)} resultados. Abriendo pop-up...")
            self.open_search_popup(productos_por_nombre)

    def open_search_popup(self, productos):
        popup = ctk.CTkToplevel(self)
        popup.title("Resultados de Búsqueda")
        popup.geometry("400x300")
        
        popup.transient(self)
        popup.grab_set()
        
        popup.grid_columnconfigure(0, weight=1)
        popup.grid_rowconfigure(0, weight=1)

        scroll_frame = ctk.CTkScrollableFrame(popup, label_text="Seleccione un producto")
        scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        for producto in productos:
            texto_boton = f"{producto['nombre']} (Stock: {producto['stock']})"
            btn = ctk.CTkButton(scroll_frame, 
                                text=texto_boton,
                                anchor="w",
                                command=lambda cod=producto['codigo_barras'], p=popup: self.add_from_popup(cod, p))
            btn.grid(row=productos.index(producto), column=0, padx=5, pady=3, sticky="ew")
            
        if scroll_frame.winfo_children():
            scroll_frame.winfo_children()[0].focus_set()

    def add_from_popup(self, codigo_barras, popup_window):
        print(f"Producto seleccionado desde pop-up: {codigo_barras}")
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
            messagebox.showerror("Error al Eliminar", "No se pudo eliminar el producto. Es probable que ya esté incluido en una venta registrada (restricción de clave foránea).")
            
    def actualizar_lista_productos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        productos = obtener_productos()
        
        for p in productos:
            self.tree.insert("", tk.END, values=(
                p['id'],
                p['codigo_barras'],
                p['nombre'],
                f"${p['precio_venta']:.2f}",
                p['stock']
            ))

    def on_agregar_producto(self):
        codigo = self.inv_entry_codigo.get()
        nombre = self.inv_entry_nombre.get()
        desc = self.inv_entry_desc.get()
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
        active_color = ("gray60", "gray40") 
        
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
            
        # --- Lógica para la futura pestaña de reportes ---
        # if name == "reports":
        #     self.reports_frame.grid(row=0, column=1, sticky="nsew")
        #     self.create_reports_view()
        # else:
        #     self.reports_frame.grid_forget()


    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("inventory")
        
    def quotes_button_event(self):
        self.select_frame_by_name("quotes")
        

if __name__ == "__main__":
    app = App()
    app.mainloop()