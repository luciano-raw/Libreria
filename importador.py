import pandas as pd
from logica import agregar_producto

def importar_inventario_desde_excel(ruta_archivo):
    """
    Lee un archivo Excel y carga los productos en la base de datos.
    Retorna un diccionario con el resumen del proceso.
    """
    resumen = {
        "total_leidos": 0,
        "exitos": 0,
        "errores": 0,
        "mensaje": ""
    }

    try:
        # 1. Leer el Excel
        # dtype=str fuerza a que todo se lea como texto al principio para evitar problemas con códigos que empiezan con 0
        df = pd.read_excel(ruta_archivo, dtype=str)
        
        resumen["total_leidos"] = len(df)

        # 2. Validar columnas mínimas (convertimos a minúsculas para ser flexibles)
        # El usuario debe tener columnas como: "codigo", "nombre", "precio", "stock"
        df.columns = [c.strip().lower() for c in df.columns]
        
        columnas_necesarias = ['codigo', 'nombre', 'precio', 'stock']
        if not all(col in df.columns for col in columnas_necesarias):
            resumen["mensaje"] = f"Faltan columnas. El Excel DEBE tener: {', '.join(columnas_necesarias)}"
            return resumen

        # 3. Iterar y Guardar
        for index, row in df.iterrows():
            # Limpieza básica de datos
            codigo = str(row['codigo']).strip()
            nombre = str(row['nombre']).strip()
            
            # Manejo de precio (quitar signos $ o comas si las hubiera)
            try:
                precio_limpio = str(row['precio']).replace('$', '').replace(',', '.')
                precio = float(precio_limpio)
            except ValueError:
                precio = 0.0

            # Manejo de stock
            try:
                stock = int(float(row['stock'])) # float primero por si viene como "10.0"
            except ValueError:
                stock = 0
            
            # Descripción es opcional
            desc = str(row['descripcion']).strip() if 'descripcion' in df.columns else ""
            
            # Marca es opcional
            marca = str(row['marca']).strip() if 'marca' in df.columns else ""

            # Llamar a la lógica existente (reutilizamos tu código probado)
            # Si el código existe, la función agregar_producto devuelve False (controlado en logica.py)
            exito = agregar_producto(codigo, nombre, desc, marca, precio, stock)
            
            if exito:
                resumen["exitos"] += 1
            else:
                resumen["errores"] += 1

        resumen["mensaje"] = "Proceso completado."
        return resumen

    except Exception as e:
        resumen["mensaje"] = f"Error crítico al leer el archivo: {str(e)}"
        return resumen