import sqlite3
import os

def reiniciar_base_de_datos():
    print("⚠️  ¡ADVERTENCIA DE BORRADO TOTAL! ⚠️")
    print("Este script borrará TODOS los datos de la base de datos:")
    print(" - Historial de Ventas y Detalles")
    print(" - Historial de Cotizaciones y Detalles")
    print(" - Todo el Inventario de Productos")
    print("Los contadores de ID se reiniciarán a 1.")
    print("---------------------------------------")
    
    confirmacion = input("Escribe 'BORRAR TODO' (en mayúsculas) para confirmar: ")
    
    if confirmacion != "BORRAR TODO":
        print("❌ Operación cancelada por seguridad.")
        return

    db_file = "libreria.db"
    
    if not os.path.exists(db_file):
        print(f"❌ No se encontró el archivo '{db_file}'.")
        return

    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            
            # 1. Desactivar claves foráneas para poder borrar sin orden específico
            cursor.execute("PRAGMA foreign_keys = OFF;")
            
            # Lista de tablas a limpiar
            tablas = [
                "Detalle_Ventas", 
                "Ventas", 
                "Detalle_Cotizaciones", 
                "Cotizaciones", 
                "Productos"
            ]
            
            print("\nLimpiando tablas...")
            
            for tabla in tablas:
                # Borrar todos los datos de la tabla
                cursor.execute(f"DELETE FROM {tabla};")
                
                # Reiniciar el contador de auto-incremento (ID)
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{tabla}';")
                print(f"✅ Tabla '{tabla}' vaciada y reiniciada.")
            
            conn.commit()
            
            # Opcional: Optimizar el archivo de la base de datos para reducir su tamaño
            cursor.execute("VACUUM;")
            
            print("\n✨ ¡Base de datos reiniciada exitosamente! ✨")
            print("El sistema está listo como si fuera una instalación nueva.")

    except sqlite3.Error as e:
        print(f"\n❌ Ocurrió un error con la base de datos: {e}")

if __name__ == "__main__":
    reiniciar_base_de_datos()
    input("\nPresiona Enter para salir...")


    