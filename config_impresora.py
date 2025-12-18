"""
Configurador de Impresora Térmica
Permite detectar y configurar impresoras USB y Bluetooth
"""

import os
import sys
import json
import customtkinter as ctk
from tkinter import messagebox, ttk

# Importar usb.core de forma segura
try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    print("Advertencia: pyusb no está instalado. La detección USB no funcionará.")

# Configurar Tcl/Tk si es necesario
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

# Archivo de configuración
CONFIG_FILE = "config_impresora.json"

def cargar_configuracion():
    """Carga la configuración guardada"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_configuracion(config):
    """Guarda la configuración"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def detectar_impresoras_usb():
    """Detecta impresoras USB conectadas"""
    impresoras = []
    if not USB_AVAILABLE:
        return impresoras
    
    try:
        # Buscar dispositivos USB
        dispositivos = usb.core.find(find_all=True)
        
        for dispositivo in dispositivos:
            try:
                # Obtener información del dispositivo
                vid = dispositivo.idVendor
                pid = dispositivo.idProduct
                
                # Intentar obtener descripción
                try:
                    dispositivo.set_configuration()
                    descripcion = usb.util.get_string(dispositivo, dispositivo.iProduct)
                except:
                    descripcion = f"Dispositivo USB {hex(vid)}:{hex(pid)}"
                
                impresoras.append({
                    'tipo': 'USB',
                    'vid': vid,
                    'pid': pid,
                    'descripcion': descripcion,
                    'vid_hex': hex(vid),
                    'pid_hex': hex(pid)
                })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error detectando impresoras USB: {e}")
    
    return impresoras

def probar_impresora_usb(vid, pid):
    """Prueba la conexión con una impresora USB"""
    try:
        from escpos.printer import Usb
        p = Usb(vid, pid)
        # Intentar imprimir un test
        p.text("\n")
        p.text("TEST DE IMPRESORA\n")
        p.text("Libreria Agosto 7\n")
        p.text("\n")
        p.cut()
        p.close()
        return True, "Impresión de prueba exitosa"
    except Exception as e:
        return False, f"Error: {str(e)}"

def probar_impresora_bluetooth(mac_address):
    """Prueba la conexión con una impresora Bluetooth"""
    try:
        try:
            from escpos.printer import Bluetooth
        except ImportError:
            return False, "Soporte Bluetooth no disponible en esta versión de python-escpos. Usa USB o actualiza la librería."
        
        p = Bluetooth(mac_address)
        p.text("\n")
        p.text("TEST DE IMPRESORA\n")
        p.text("Libreria Agosto 7\n")
        p.text("\n")
        p.cut()
        p.close()
        return True, "Impresión de prueba exitosa"
    except Exception as e:
        return False, f"Error: {str(e)}"

class ConfiguradorImpresora(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Configuración de Impresora Térmica - Librería Agosto 7")
        self.geometry("700x600")
        
        self.configuracion = cargar_configuracion()
        
        # Variables
        self.tipo_conexion = ctk.StringVar(value=self.configuracion.get('tipo', 'USB'))
        self.vid_var = ctk.StringVar(value=str(self.configuracion.get('vid', '0x04B8')))
        self.pid_var = ctk.StringVar(value=str(self.configuracion.get('pid', '0x0202')))
        self.mac_var = ctk.StringVar(value=self.configuracion.get('mac', ''))
        
        self.crear_interfaz()
        self.actualizar_lista_impresoras()
    
    def crear_interfaz(self):
        # Título
        titulo = ctk.CTkLabel(
            self, 
            text="Configuración de Impresora Térmica",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titulo.pack(pady=20)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tipo de conexión
        tipo_frame = ctk.CTkFrame(main_frame)
        tipo_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            tipo_frame, 
            text="Tipo de Conexión:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        usb_radio = ctk.CTkRadioButton(
            tipo_frame,
            text="USB",
            variable=self.tipo_conexion,
            value="USB",
            command=self.on_tipo_cambio
        )
        usb_radio.pack(side="left", padx=20, pady=10)
        
        bluetooth_radio = ctk.CTkRadioButton(
            tipo_frame,
            text="Bluetooth",
            variable=self.tipo_conexion,
            value="Bluetooth",
            command=self.on_tipo_cambio
        )
        bluetooth_radio.pack(side="left", padx=20, pady=10)
        
        # Frame para USB
        self.usb_frame = ctk.CTkFrame(main_frame)
        self.usb_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Botón detectar USB
        detectar_btn = ctk.CTkButton(
            self.usb_frame,
            text="🔍 Detectar Impresoras USB",
            command=self.actualizar_lista_impresoras,
            height=35
        )
        detectar_btn.pack(pady=10)
        
        # Lista de impresoras USB
        ctk.CTkLabel(
            self.usb_frame,
            text="Impresoras USB Detectadas:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Treeview para lista
        tree_frame = ctk.CTkFrame(self.usb_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("descripcion", "vid", "pid")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        self.tree.heading("descripcion", text="Dispositivo")
        self.tree.heading("vid", text="VID")
        self.tree.heading("pid", text="PID")
        self.tree.column("descripcion", width=300)
        self.tree.column("vid", width=150)
        self.tree.column("pid", width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_seleccionar_impresora)
        
        # Campos manuales USB
        manual_frame = ctk.CTkFrame(self.usb_frame)
        manual_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(manual_frame, text="O ingresar manualmente:").pack(anchor="w", padx=10, pady=5)
        
        vid_frame = ctk.CTkFrame(manual_frame, fg_color="transparent")
        vid_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(vid_frame, text="VID (hex):", width=100).pack(side="left")
        vid_entry = ctk.CTkEntry(vid_frame, textvariable=self.vid_var, width=150)
        vid_entry.pack(side="left", padx=5)
        
        pid_frame = ctk.CTkFrame(manual_frame, fg_color="transparent")
        pid_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(pid_frame, text="PID (hex):", width=100).pack(side="left")
        pid_entry = ctk.CTkEntry(pid_frame, textvariable=self.pid_var, width=150)
        pid_entry.pack(side="left", padx=5)
        
        # Frame para Bluetooth
        self.bluetooth_frame = ctk.CTkFrame(main_frame)
        
        ctk.CTkLabel(
            self.bluetooth_frame,
            text="Dirección MAC de la Impresora:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        mac_entry = ctk.CTkEntry(
            self.bluetooth_frame,
            textvariable=self.mac_var,
            placeholder_text="Ej: 00:11:22:33:44:55",
            width=300
        )
        mac_entry.pack(padx=15, pady=10)
        
        ctk.CTkLabel(
            self.bluetooth_frame,
            text="Nota: Asegúrate de que la impresora esté emparejada con tu computadora",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(padx=15, pady=5)
        
        # Botones de acción
        botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botones_frame.pack(fill="x", padx=15, pady=15)
        
        probar_btn = ctk.CTkButton(
            botones_frame,
            text="🖨️ Probar Impresión",
            command=self.probar_impresora,
            height=40,
            fg_color="#10B981",
            hover_color="#059669"
        )
        probar_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        guardar_btn = ctk.CTkButton(
            botones_frame,
            text="💾 Guardar Configuración",
            command=self.guardar_config,
            height=40,
            fg_color="#2563EB",
            hover_color="#1D4ED8"
        )
        guardar_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        self.on_tipo_cambio()
    
    def on_tipo_cambio(self):
        """Actualiza la interfaz según el tipo de conexión"""
        if self.tipo_conexion.get() == "USB":
            self.usb_frame.pack(fill="both", expand=True, padx=15, pady=10)
            self.bluetooth_frame.pack_forget()
        else:
            self.usb_frame.pack_forget()
            self.bluetooth_frame.pack(fill="both", expand=True, padx=15, pady=10)
    
    def actualizar_lista_impresoras(self):
        """Actualiza la lista de impresoras USB detectadas"""
        # Limpiar lista
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Detectar impresoras
        impresoras = detectar_impresoras_usb()
        
        if not impresoras:
            self.tree.insert("", "end", values=("No se detectaron impresoras USB", "", ""))
        else:
            for imp in impresoras:
                self.tree.insert("", "end", values=(
                    imp['descripcion'],
                    imp['vid_hex'],
                    imp['pid_hex']
                ))
    
    def on_seleccionar_impresora(self, event):
        """Cuando se selecciona una impresora de la lista"""
        seleccion = self.tree.selection()
        if seleccion:
            item = self.tree.item(seleccion[0])
            vid_hex = item['values'][1]
            pid_hex = item['values'][2]
            
            if vid_hex and pid_hex:
                self.vid_var.set(vid_hex)
                self.pid_var.set(pid_hex)
    
    def probar_impresora(self):
        """Prueba la conexión con la impresora"""
        if self.tipo_conexion.get() == "USB":
            try:
                vid = int(self.vid_var.get(), 16)
                pid = int(self.pid_var.get(), 16)
                exito, mensaje = probar_impresora_usb(vid, pid)
            except ValueError:
                messagebox.showerror("Error", "VID y PID deben ser números hexadecimales (ej: 0x04B8)")
                return
        else:
            mac = self.mac_var.get().strip()
            if not mac:
                messagebox.showerror("Error", "Ingresa la dirección MAC de la impresora")
                return
            exito, mensaje = probar_impresora_bluetooth(mac)
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
        else:
            messagebox.showerror("Error", mensaje)
    
    def guardar_config(self):
        """Guarda la configuración"""
        config = {
            'tipo': self.tipo_conexion.get()
        }
        
        if self.tipo_conexion.get() == "USB":
            try:
                config['vid'] = int(self.vid_var.get(), 16)
                config['pid'] = int(self.pid_var.get(), 16)
            except ValueError:
                messagebox.showerror("Error", "VID y PID deben ser números hexadecimales válidos")
                return
        else:
            config['mac'] = self.mac_var.get().strip()
            if not config['mac']:
                messagebox.showerror("Error", "Ingresa la dirección MAC de la impresora")
                return
        
        guardar_configuracion(config)
        messagebox.showinfo("Éxito", "Configuración guardada correctamente")
        self.configuracion = config

if __name__ == "__main__":
    app = ConfiguradorImpresora()
    app.mainloop()

