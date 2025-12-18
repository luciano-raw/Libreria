# Guía de Configuración de Impresora Térmica

## 📋 Preparación

### 1. Instalar Dependencias

Primero, instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

O manualmente:
```bash
pip install python-escpos pyusb
```

### 2. Permisos en Windows (USB)

Si usas Windows y tienes problemas con USB, puede que necesites instalar drivers adicionales o ejecutar como administrador.

## 🔌 Tipos de Conexión

### USB (Recomendado)
- **Ventajas**: Más estable, no requiere emparejamiento
- **Desventajas**: Requiere cable USB
- **Uso**: Ideal para uso en caja fija

### Bluetooth
- **Ventajas**: Sin cables, más flexible
- **Desventajas**: Requiere emparejamiento previo, puede tener latencia
- **Uso**: Ideal para impresoras portátiles o cuando no hay puertos USB disponibles

## 🚀 Pasos para Configurar

### Opción 1: Usar la Interfaz Gráfica (Recomendado)

1. **Ejecuta el configurador:**
   ```bash
   python config_impresora.py
   ```

2. **Para USB:**
   - Haz clic en "🔍 Detectar Impresoras USB"
   - Selecciona tu impresora de la lista
   - O ingresa manualmente el VID y PID
   - Haz clic en "🖨️ Probar Impresión"
   - Si funciona, haz clic en "💾 Guardar Configuración"

3. **Para Bluetooth:**
   - Selecciona "Bluetooth"
   - Empareja la impresora con tu computadora primero (desde Configuración de Windows)
   - Ingresa la dirección MAC de la impresora (formato: 00:11:22:33:44:55)
   - Haz clic en "🖨️ Probar Impresión"
   - Si funciona, haz clic en "💾 Guardar Configuración"

### Opción 2: Configuración Manual

Si prefieres configurar manualmente, edita el archivo `config_impresora.json`:

**Para USB:**
```json
{
  "tipo": "USB",
  "vid": 1208,
  "pid": 514
}
```

**Para Bluetooth:**
```json
{
  "tipo": "Bluetooth",
  "mac": "00:11:22:33:44:55"
}
```

## 🔍 Encontrar VID y PID (USB)

### En Windows:

1. Conecta la impresora por USB
2. Abre el **Administrador de Dispositivos**
3. Busca tu impresora (puede estar en "Impresoras" o "Dispositivos USB")
4. Clic derecho > **Propiedades**
5. Ve a la pestaña **Detalles**
6. En "Propiedad", selecciona **"Id. de hardware"**
7. Verás algo como: `USB\VID_04B8&PID_0202`
   - `VID_04B8` = Vendor ID (0x04B8 en hexadecimal)
   - `PID_0202` = Product ID (0x0202 en hexadecimal)

### En Linux/Mac:

```bash
lsusb
```

Busca tu impresora y verás algo como:
```
Bus 001 Device 002: ID 04b8:0202 Seiko Epson Corp. TM-T88IV
```

Donde `04b8:0202` es `VID:PID`

## 🖨️ Probar la Impresora

Después de configurar, puedes probar desde la interfaz o ejecutando:

```bash
python ticket.py
```

Esto imprimirá una boleta de prueba.

## ⚠️ Solución de Problemas

### Error: "No se pudo conectar a la impresora USB"

1. **Verifica que la impresora esté encendida**
2. **Verifica que el cable USB esté conectado**
3. **Revisa los VID/PID** - Pueden ser diferentes a los de ejemplo
4. **En Windows**: Puede necesitar ejecutar como administrador
5. **Instala drivers**: Algunas impresoras necesitan drivers específicos

### Error: "No se pudo conectar a la impresora Bluetooth"

1. **Empareja primero** la impresora desde Configuración de Windows
2. **Verifica la dirección MAC** - Debe estar en formato correcto (00:11:22:33:44:55)
3. **Asegúrate de que Bluetooth esté activado** en ambos dispositivos
4. **Algunas impresoras Bluetooth** requieren estar en "modo descubrible"

### La impresora imprime pero el formato está mal

Edita el archivo `ticket.py` para ajustar:
- Ancho de columnas
- Fuentes
- Espaciado
- Información de la librería

## 📝 Notas Importantes

- **La configuración se guarda** en `config_impresora.json`
- **No edites manualmente** este archivo a menos que sepas lo que haces
- **Siempre prueba** antes de usar en producción
- **Algunas impresoras** pueden requerir configuración adicional (velocidad, encoding, etc.)

## 🎯 Impresoras Comunes y sus IDs

| Marca/Modelo | VID | PID |
|-------------|-----|-----|
| Epson TM-T88IV | 0x04B8 | 0x0202 |
| Epson TM-T20 | 0x04B8 | 0x0202 |
| Star TSP100 | 0x0519 | 0x0001 |
| Bixolon SRP-350 | 0x1504 | 0x0006 |

*Nota: Estos son ejemplos. Tu impresora puede tener IDs diferentes.*

