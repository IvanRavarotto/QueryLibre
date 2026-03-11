import pandas as pd
import numpy as np
import os
import random

# 1. Generamos una base más grande (20 registros)
random.seed(42)
np.random.seed(42)
n_records = 20

productos = ['Laptop Dell XPS', 'Monitor LG 27"', 'Teclado Mecánico', 'Mouse Inalámbrico', 'Auriculares Sony']
clientes = ['Empresa A', 'Empresa B', 'Empresa C', 'Startup X', 'Corporación Y']

# Creamos columnas con errores típicos de formato
datos = {
    ' ID Transaccion ': [f'TRX-{str(i).zfill(3)}' for i in range(1, n_records + 1)], # Espacios molestos al inicio y final
    'Producto_Nombre': [random.choice(productos) for _ in range(n_records)],
    'Cantidad': [str(random.randint(1, 10)) for _ in range(n_records)], # Guardado como texto en vez de número
    'precio_unitario_usd': [f"${random.uniform(15.0, 1500.0):.2f}" for _ in range(n_records)], # Trae el símbolo "$" incrustado
    'Fecha Compra': pd.date_range(start='2026-01-01', periods=n_records).strftime('%Y-%m-%d').tolist(), # Espacio en el nombre
    'Cliente': [random.choice(clientes) for _ in range(n_records)],
    'Notas_Internas': ['Borrar esta columna' for _ in range(n_records)] # Columna inútil para probar "Eliminar Columna"
}

df_base = pd.DataFrame(datos)

# 2. Ensuciamos los datos a propósito
# Añadimos Nulos
df_base.loc[2, 'Producto_Nombre'] = np.nan
df_base.loc[5, 'Cantidad'] = np.nan
df_base.loc[12, 'Cliente'] = np.nan

# Rompemos el formato de algunas fechas
df_base.loc[1, 'Fecha Compra'] = '01/01/2026' 
df_base.loc[8, 'Fecha Compra'] = '15-01-2026'

# 3. Forzamos duplicados (Copiamos 3 transacciones al azar al final)
df_sucios = pd.concat([df_base, df_base.iloc[[0, 4, 7]]], ignore_index=True)

# 4. Desordenamos todo
df_final = df_sucios.sample(frac=1).reset_index(drop=True)

# 5. Guardamos en la carpeta data_test
carpeta_destino = 'data_test'
os.makedirs(carpeta_destino, exist_ok=True)
ruta_archivo = os.path.join(carpeta_destino, 'dataset_caotico_v2.csv')

df_final.to_csv(ruta_archivo, index=False)

print("-" * 50)
print(f"✅ ¡Nuevo dataset caótico generado con éxito!")
print(f"📁 Archivo: {ruta_archivo}")
print(f"📊 Total de filas para probar: {len(df_final)}")
print("-" * 50)