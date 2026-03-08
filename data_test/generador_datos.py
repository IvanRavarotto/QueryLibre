import pandas as pd
import numpy as np
import os

# 1. Creamos un diccionario con datos base limpios (y algunos nulos intencionales)
datos = {
    'ID_Transaccion': ['TRX-001', 'TRX-002', 'TRX-003', 'TRX-004', 'TRX-005'],
    'Producto': ['Laptop Dell XPS', 'Monitor LG 27"', np.nan, 'Teclado Mecánico', 'Mouse Inalámbrico'],
    'Cantidad': [2, 5, 1, np.nan, 10],
    'Precio_Unitario': [1200.50, 250.00, 15.99, 85.50, 25.00],
    'Cliente': ['Empresa A', 'Empresa B', 'Empresa C', np.nan, 'Empresa A']
}

df_base = pd.DataFrame(datos)

# 2. Forzamos filas duplicadas (Copiamos las transacciones 001 y 002 al final)
df_sucios = pd.concat([df_base, df_base.iloc[[0, 1]]], ignore_index=True)

# 3. Añadimos una fila completamente vacía (puro NaN)
fila_vacia = pd.DataFrame([[np.nan] * 5], columns=df_base.columns)
df_final = pd.concat([df_sucios, fila_vacia], ignore_index=True)

# 4. Desordenamos un poco el índice para que sea más realista
df_final = df_final.sample(frac=1).reset_index(drop=True)

# ---- NUEVA LÓGICA DE CARPETAS ----

# Definimos el nombre de la carpeta
carpeta_destino = 'data_test'

# Le decimos a Python: "Si la carpeta no existe, créala"
os.makedirs(carpeta_destino, exist_ok=True)

# Unimos la carpeta con el nombre del archivo
ruta_archivo = os.path.join(carpeta_destino, 'datos_prueba_sucios.csv')

# Exportamos el resultado
df_final.to_csv(ruta_archivo, index=False)

# Verificamos la ruta final
ruta_absoluta = os.path.abspath(ruta_archivo)
print("-" * 40)
print(f"✅ ¡Datos generados y guardados correctamente!")
print(f"📁 Carpeta: {carpeta_destino}/")
print(f"📄 Archivo: datos_prueba_sucios.csv")
print(f"📍 Ruta exacta: {ruta_absoluta}")
print("-" * 40)