import sqlite3
from datetime import datetime

# El nombre de la base de datos que creamos en el Paso 1
DB_NAME = "libreria.db"

def get_db_connection():
    """Crea una conexión a la BD. 
       Configurada para devolver filas como diccionarios (sqlite3.Row)
       y para activar las claves foráneas (foreign keys)."""
    conn = sqlite3.connect(DB_NAME)
    # PRAGMA foreign_keys = ON; es crucial para que las relaciones (FOREIGN KEY) 
    # realmente funcionen y den error si intentas, por ej.,
    # vender un producto que no existe.
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row  # Esto nos permite acceder a las columnas por nombre
    return conn

# -----------------------------------------------
# --- 1. CRUD (Create, Read, Update, Delete) de Productos
# -----------------------------------------------

def agregar_producto(codigo_barras, nombre, descripcion, marca, precio_venta, stock):
    """Agrega un nuevo producto al inventario."""
    sql = """
    INSERT INTO Productos (codigo_barras, nombre, descripcion, marca, precio_venta, stock)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (codigo_barras, nombre, descripcion, marca, precio_venta, stock))
            conn.commit()
            print(f"Producto '{nombre}' agregado exitosamente.")
            return True
    except sqlite3.IntegrityError as e:
        # Esto saltará si el codigo_barras ya existe (por la restricción UNIQUE)
        print(f"Error de integridad: Es probable que el código de barras '{codigo_barras}' ya exista. {e}")
        return False
    except sqlite3.Error as e:
        print(f"Error al agregar producto: {e}")
        return False

def obtener_productos():
    """Obtiene una lista de todos los productos en el inventario."""
    sql = "SELECT * FROM Productos ORDER BY nombre"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            productos = cursor.fetchall()
            # fetchall() con row_factory devuelve una lista de objetos 'Row' (parecidos a dicts)
            return [dict(p) for p in productos]
    except sqlite3.Error as e:
        print(f"Error al obtener productos: {e}")
        return []

def buscar_producto_por_codigo(codigo_barras):
    """Busca un producto específico por su código de barras."""
    sql = "SELECT * FROM Productos WHERE codigo_barras = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (codigo_barras,))
            producto = cursor.fetchone() # fetchone() devuelve un solo resultado o None
            if producto:
                return dict(producto)
            else:
                return None
    except sqlite3.Error as e:
        print(f"Error al buscar producto: {e}")
        return None


def buscar_productos_por_nombre(termino_busqueda):
    """
    Busca productos que coincidan con el término en el nombre.
    Retorna una LISTA de productos.
    """
    sql = "SELECT * FROM Productos WHERE nombre LIKE ? ORDER BY nombre"
    # Usamos '%' para que busque el término en cualquier parte del nombre
    termino_like = f"%{termino_busqueda}%" 
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (termino_like,))
            productos = cursor.fetchall()
            # Retornamos una lista de diccionarios
            return [dict(p) for p in productos]
    except sqlite3.Error as e:
        print(f"Error al buscar productos por nombre: {e}")
        return []

def editar_producto(id_producto, nombre, descripcion, marca, precio_venta, stock, codigo_barras):
    """Actualiza los datos de un producto existente por su ID."""
    sql = """
    UPDATE Productos
    SET nombre = ?, descripcion = ?, marca = ?, precio_venta = ?, stock = ?, codigo_barras = ?
    WHERE id = ?
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Asegúrate de que el orden de los parámetros coincida
            cursor.execute(sql, (nombre, descripcion, marca, precio_venta, stock, codigo_barras, id_producto))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Producto ID {id_producto} actualizado.")
                return True
            else:
                print(f"Producto ID {id_producto} no encontrado.")
                return False
    except sqlite3.IntegrityError as e:
        print(f"Error de integridad: Es probable que el código de barras '{codigo_barras}' ya exista. {e}")
        return False
    except sqlite3.Error as e:
        print(f"Error al editar producto: {e}")
        return False

def eliminar_producto(id_producto):
    """
    Elimina un producto de la base de datos usando su ID.
    NOTA: Esto fallará si el producto está referenciado en 'Detalle_Ventas'
    o 'Detalle_Cotizaciones' si las claves foráneas están activas.
    (Para un sistema real, en lugar de borrar, "desactivaríamos" el producto).
    """
    sql = "DELETE FROM Productos WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (id_producto,))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Producto ID {id_producto} eliminado exitosamente.")
                return True
            else:
                print(f"Producto ID {id_producto} no encontrado.")
                return False
    except sqlite3.Error as e:
        print(f"Error al eliminar producto (puede estar en uso en ventas): {e}")
        return False


# -----------------------------------------------
# --- 2. Lógica de Ventas y Cotizaciones
# -----------------------------------------------

def registrar_venta(carrito, total_venta):
    """
    Registra una venta. Esto es una TRANSACCIÓN.
    1. Inserta en 'Ventas'.
    2. Inserta cada item del carrito en 'Detalle_Ventas'.
    3. DESCUENTA el stock de la tabla 'Productos'.
    
    El 'carrito' debe ser una lista de diccionarios:
    [ {'id': 1, 'cantidad': 2, 'precio_unitario': 500}, ... ]
    """
    
    # 'with' en una conexión de sqlite3 maneja automáticamente 
    # las TRANSACCIONES. Si algo falla, hace ROLLBACK (deshace todo).
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Insertar en la tabla maestra 'Ventas'
            sql_venta = "INSERT INTO Ventas (total) VALUES (?)"
            cursor.execute(sql_venta, (total_venta,))
            
            # Obtener el ID de la venta que acabamos de crear
            venta_id = cursor.lastrowid
            
            # 2. Preparar datos para 'Detalle_Ventas' y 'Productos'
            sql_detalle = """
            INSERT INTO Detalle_Ventas (venta_id, producto_id, cantidad, precio_unitario_momento)
            VALUES (?, ?, ?, ?)
            """
            sql_update_stock = """
            UPDATE Productos SET stock = stock - ? WHERE id = ?
            """
            
            detalles_para_insertar = []
            stock_para_actualizar = []
            
            for item in carrito:
                detalles_para_insertar.append(
                    (venta_id, item['id'], item['cantidad'], item['precio_unitario'])
                )
                stock_para_actualizar.append(
                    (item['cantidad'], item['id'])
                )

            # 3. Insertar todos los detalles de la venta
            cursor.executemany(sql_detalle, detalles_para_insertar)
            
            # 4. Actualizar el stock de todos los productos
            cursor.executemany(sql_update_stock, stock_para_actualizar)
            
            # Si todo salió bien, la transacción se confirma (commit)
            conn.commit()
            print(f"Venta ID {venta_id} registrada exitosamente.")
            return venta_id
            
    except sqlite3.Error as e:
        print(f"Error al registrar la venta (Transacción revertida): {e}")
        return None

def registrar_cotizacion(carrito, total_cotizado, cliente=""):
    """
    Registra una cotización. Es similar a la venta, pero:
    1. Inserta en 'Cotizaciones' y 'Detalle_Cotizaciones'.
    2. NO descuenta el stock.
    
    'carrito' tiene el mismo formato:
    [ {'id': 1, 'cantidad': 2, 'precio_unitario': 500}, ... ]
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Insertar en 'Cotizaciones'
            sql_cotizacion = "INSERT INTO Cotizaciones (cliente_nombre, total) VALUES (?, ?)"
            cursor.execute(sql_cotizacion, (cliente, total_cotizado))
            
            cotizacion_id = cursor.lastrowid
            
            # 2. Preparar datos para 'Detalle_Cotizaciones'
            sql_detalle = """
            INSERT INTO Detalle_Cotizaciones (cotizacion_id, producto_id, cantidad, precio_unitario_momento)
            VALUES (?, ?, ?, ?)
            """
            
            detalles_para_insertar = []
            for item in carrito:
                detalles_para_insertar.append(
                    (cotizacion_id, item['id'], item['cantidad'], item['precio_unitario'])
                )
            
            # 3. Insertar todos los detalles
            cursor.executemany(sql_detalle, detalles_para_insertar)
            
            conn.commit()
            print(f"Cotización ID {cotizacion_id} registrada para '{cliente}'.")
            return cotizacion_id

    except sqlite3.Error as e:
        print(f"Error al registrar la cotización: {e}")
        return None


# -----------------------------------------------
# --- 3. Lógica de Gestión de Cotizaciones (¡SECCIÓN NUEVA!)
# -----------------------------------------------

def obtener_todas_las_cotizaciones():
    """
    Obtiene una lista de todas las cotizaciones pendientes (tabla 'Cotizaciones').
    """
    sql = "SELECT id, fecha_hora, cliente_nombre, total FROM Cotizaciones ORDER BY fecha_hora DESC"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            cotizaciones = cursor.fetchall()
            return [dict(c) for c in cotizaciones]
    except sqlite3.Error as e:
        print(f"Error al obtener cotizaciones: {e}")
        return []

# (En logica.py)

def obtener_detalle_cotizacion(cotizacion_id):
    """
    Obtiene los productos (el detalle) de una cotización específica.
    """
    sql = """
    SELECT 
        p.nombre, 
        dc.cantidad, 
        dc.precio_unitario_momento,
        dc.producto_id,
        p.codigo_barras,
        p.marca
    FROM Detalle_Cotizaciones dc
    JOIN Productos p ON dc.producto_id = p.id
    WHERE dc.cotizacion_id = ?
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (cotizacion_id,))
            detalles = cursor.fetchall()
            return [dict(d) for d in detalles]
    except sqlite3.Error as e:
        print(f"Error al obtener detalle de cotización: {e}")
        return []
    
def eliminar_cotizacion_completa(cotizacion_id):
    """
    Elimina una cotización y todos sus detalles (transacción).
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Eliminar los detalles
            cursor.execute("DELETE FROM Detalle_Cotizaciones WHERE cotizacion_id = ?", (cotizacion_id,))
            
            # 2. Eliminar la cotización principal
            cursor.execute("DELETE FROM Cotizaciones WHERE id = ?", (cotizacion_id,))
            
            conn.commit()
            print(f"Cotización ID {cotizacion_id} eliminada exitosamente.")
            return True
    except sqlite3.Error as e:
        print(f"Error al eliminar la cotización: {e}")
        return False

def convertir_cotizacion_a_venta(cotizacion_id):
    """
    Convierte una cotización existente en una venta.
    1. Obtiene los detalles de la cotización.
    2. Prepara el 'carrito' y el total.
    3. Llama a 'registrar_venta' (que descuenta stock).
    4. Si la venta es exitosa, elimina la cotización original.
    """
    
    # 1. Obtener detalles (usando nuestra función modificada)
    detalles = obtener_detalle_cotizacion(cotizacion_id)
    if not detalles:
        print(f"Error: No se encontraron detalles para la cotización ID {cotizacion_id}")
        return False, "No se encontraron detalles de la cotización."

    # 2. Preparar carrito y total
    carrito_para_venta = []
    total_para_venta = 0
    
    for item in detalles:
        carrito_para_venta.append({
            'id': item['producto_id'], # <-- ¡Por esto modificamos la función anterior!
            'cantidad': item['cantidad'],
            'precio_unitario': item['precio_unitario_momento']
        })
        total_para_venta += item['cantidad'] * item['precio_unitario_momento']
    
    # 3. Registrar la venta
    print(f"Intentando convertir Cotización ID {cotizacion_id} a Venta...")
    venta_id = registrar_venta(carrito_para_venta, total_para_venta)
    
    if venta_id:
        print(f"Venta ID {venta_id} creada desde Cotización ID {cotizacion_id}.")
        
        # 4. Eliminar la cotización (usando la función que ya teníamos)
        print(f"Eliminando Cotización ID {cotizacion_id} (ya convertida)...")
        eliminar_cotizacion_completa(cotizacion_id)
        return True, f"Venta {venta_id} registrada. Cotización {cotizacion_id} eliminada."
    else:
        print(f"Error: Fallo al registrar la venta para la Cotización ID {cotizacion_id}.")
        # Posible causa: Falta de stock.
        return False, "Error al registrar la venta. Verifique el stock de los productos."


# -----------------------------------------------
# --- BLOQUE DE PRUEBAS (se ejecuta solo si corres 'python logica.py')
# -----------------------------------------------
if __name__ == "__main__":
    
    print("--- INICIANDO PRUEBAS DE LOGICA.PY ---")
    
    # Asegúrate de que las tablas existan (importamos y usamos la función del Paso 1)
    try:
        from database import crear_tablas
        crear_tablas()
    except ImportError:
        print("Asegúrate de que 'database.py' esté en la misma carpeta.")
        exit()

    print("\n--- Prueba 1: Agregando productos ---")
    agregar_producto("123456", "Lápiz HB", "Lápiz de grafito", "Faber-Castell", 500.0, 100)
    agregar_producto("123457", "Goma de borrar", "Goma blanca", "Pelikan", 300.0, 50)
    agregar_producto("123456", "Lápiz (Duplicado)", "Intento fallido", "Test", 1.0, 1) # Esto debería fallar

    print("\n--- Prueba 2: Obteniendo productos ---")
    productos = obtener_productos()
    for p in productos:
        print(f"ID: {p['id']}, Nombre: {p['nombre']}, Stock: {p['stock']}")

    print("\n--- Prueba 3: Buscando producto por código ---")
    producto_buscado = buscar_producto_por_codigo("123457") # Goma
    if producto_buscado:
        print(f"Producto encontrado: {producto_buscado['nombre']}")
    else:
        print("Producto no encontrado.")

    print("\n--- Prueba 4: Registrando una VENTA ---")
    
    # Simulamos un carrito. Usamos los datos del producto buscado.
    # El usuario quiere 2 gomas de borrar (ID 2, Stock 50)
    
    # (En un caso real, obtendríamos los IDs de la base de datos)
    # Suponiendo que Lápiz es ID 1 y Goma es ID 2:
    
    carrito_simulado = [
        {'id': 1, 'cantidad': 3, 'precio_unitario': 500.0}, # 3 Lápices
        {'id': 2, 'cantidad': 2, 'precio_unitario': 300.0}  # 2 Gomas
    ]
    total_simulado = (3 * 500.0) + (2 * 300.0) # 1500 + 600 = 2100
    
    registrar_venta(carrito_simulado, total_simulado)

    print("\n--- Prueba 5: Verificando el STOCK después de la venta ---")
    productos_despues_venta = obtener_productos()
    for p in productos_despues_venta:
        # Lápiz (ID 1) debería tener 100 - 3 = 97
        # Goma (ID 2) debería tener 50 - 2 = 48
        print(f"ID: {p['id']}, Nombre: {p['nombre']}, Stock: {p['stock']}")
        
    print("\n--- Prueba 6: Registrando una COTIZACIÓN ---")
    # Usamos el mismo carrito
    registrar_cotizacion(carrito_simulado, total_simulado, "Cliente Ejemplo S.A.")

    print("\n--- Prueba 7: Verificando el STOCK después de cotización ---")
    productos_despues_cot = obtener_productos()
    for p in productos_despues_cot:
        # Los stocks deben seguir iguales que en la Prueba 5
        print(f"ID: {p['id']}, Nombre: {p['nombre']}, Stock: {p['stock']}")

    print("\n--- FIN DE PRUEBAS ---")