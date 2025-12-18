import sqlite3

def crear_tablas():
    """
    Crea las tablas necesarias en la base de datos 'libreria.db'.
    Si las tablas ya existen, no hace nada.
    """
    
    # Usamos 'with' para manejar la conexión y el commit/rollback automáticamente
    try:
        with sqlite3.connect("libreria.db") as conn:
            cursor = conn.cursor()
            
            # Usamos ''' para definir un string de múltiples líneas
            sql_script = """
            -- PRAGMA foreign_keys = ON;  -- (Lo activaremos en la lógica, no aquí)

            -- Tabla de Productos: El inventario
            CREATE TABLE IF NOT EXISTS Productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_barras TEXT UNIQUE,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                marca TEXT,
                precio_venta REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0
            );

            -- Tabla de Ventas: Un registro de cada transacción
            CREATE TABLE IF NOT EXISTS Ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                total REAL NOT NULL
            );

            -- Tabla de Detalle_Ventas: Qué productos se vendieron en cada venta
            CREATE TABLE IF NOT EXISTS Detalle_Ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario_momento REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES Ventas (id),
                FOREIGN KEY (producto_id) REFERENCES Productos (id)
            );

            -- Tabla de Cotizaciones
            CREATE TABLE IF NOT EXISTS Cotizaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                cliente_nombre TEXT,
                total REAL NOT NULL
            );

            -- Tabla de Detalle_Cotizaciones: Qué productos se cotizaron
            CREATE TABLE IF NOT EXISTS Detalle_Cotizaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cotizacion_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario_momento REAL NOT NULL,
                FOREIGN KEY (cotizacion_id) REFERENCES Cotizaciones (id),
                FOREIGN KEY (producto_id) REFERENCES Productos (id)
            );
            """
            
            # executescript puede ejecutar múltiples sentencias SQL a la vez
            cursor.executescript(sql_script)
            
            # Añadir columna 'marca' si no existe (para bases de datos existentes)
            try:
                cursor.execute("ALTER TABLE Productos ADD COLUMN marca TEXT")
                print("Columna 'marca' añadida a la tabla Productos.")
            except sqlite3.OperationalError:
                # La columna ya existe, no hacer nada
                pass
            
            print("Base de datos y tablas creadas exitosamente.")
            
    except sqlite3.Error as e:
        print(f"Error al crear la base de datos: {e}")

# --- Este bloque permite ejecutar el script directamente ---
if __name__ == "__main__":
    crear_tablas()