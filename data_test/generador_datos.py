import pandas as pd
import numpy as np
import os
import random

# Configuramos la semilla para que los errores sean siempre los mismos en cada prueba
random.seed(42)
np.random.seed(42)

n_records = 120 # Base de 120 registros (llegará a 135 con los duplicados)

# --- 1. DATASET PRINCIPAL (CAÓTICO) ---
productos = ['Laptop Dell XPS', 'Monitor LG 27"', 'Teclado Mecánico', 'Mouse Inalámbrico', 'Auriculares Sony', 'Silla Ergonomica', 'Escritorio Standing']
categorias = ['Electronica', 'Perifericos', 'Mobiliario']

datos_ventas = {
    ' ID Transaccion ': [f'TRX-{str(i).zfill(4)}' for i in range(1, n_records + 1)], # Espacios molestos
    'ID_Cliente': [random.randint(1, 15) for _ in range(n_records)], # Clientes del 1 al 15
    'Producto_Nombre': [random.choice(productos) for _ in range(n_records)],
    'Categoria_Prod': [random.choice(categorias) for _ in range(n_records)],
    'Sub_Cat': ['Genérica' for _ in range(n_records)], 
    'Cantidad ': [str(random.randint(1, 15)) for _ in range(n_records)], # Guardado como texto
    'precio_unitario_usd': [f"${random.uniform(15.0, 2500.0):,.2f}" for _ in range(n_records)], # Símbolo y comas (Ej: $1,500.00)
    'Fecha Compra': pd.date_range(start='2025-01-01', periods=n_records).strftime('%Y-%m-%d').tolist(),
    'Notas_Internas': ['Borrar esta columna' for _ in range(n_records)] # Columna inútil
}

df_ventas = pd.DataFrame(datos_ventas)

# --- ENSUCIAR EL DATASET PRINCIPAL ---
# 1. Inyectar Nulos (NaN) aleatorios
for _ in range(12): df_ventas.loc[random.randint(0, n_records-1), 'Producto_Nombre'] = np.nan
for _ in range(8): df_ventas.loc[random.randint(0, n_records-1), 'Cantidad '] = np.nan
for _ in range(5): df_ventas.loc[random.randint(0, n_records-1), 'ID_Cliente'] = np.nan

# 2. Romper el formato de fechas
df_ventas.loc[10, 'Fecha Compra'] = '01/15/2025'
df_ventas.loc[25, 'Fecha Compra'] = '15-01-2025'
df_ventas.loc[50, 'Fecha Compra'] = '2025/02/28'

# 3. Forzar Duplicados (Copiamos 15 filas al azar y las pegamos al final)
indices_duplicar = random.sample(range(n_records), 15)
df_ventas = pd.concat([df_ventas, df_ventas.iloc[indices_duplicar]], ignore_index=True)

# 4. Desordenar filas para que los duplicados se mezclen
df_ventas = df_ventas.sample(frac=1).reset_index(drop=True) 


# --- 2. DATASET SECUNDARIO (DIMENSIONAL PARA MERGE/JOIN) ---
# Creamos clientes del 1 al 20. (Nota: En ventas solo hay del 1 al 15, ideal para probar Left Join)
paises = ['Argentina', 'Chile', 'Colombia', 'Mexico', 'España', 'Uruguay']
suscripciones = ['Básico', 'Premium', 'Enterprise']

datos_clientes = {
    'Cliente_ID': range(1, 21), # ¡LLAVE DIFERENTE! ('Cliente_ID' vs 'ID_Cliente')
    'Nombre_Empresa': [f'Empresa {chr(65+i)}{chr(65+i)}' for i in range(20)],
    'Pais_Origen': [random.choice(paises) for _ in range(20)],
    'Suscripcion': [random.choice(suscripciones) for _ in range(20)],
    'Descuento_Aprobado': [round(random.uniform(0.05, 0.30), 2) for _ in range(20)]
}

df_clientes = pd.DataFrame(datos_clientes)


# --- 3. GUARDAR LOS ARCHIVOS ---
carpeta_destino = 'data_test'
os.makedirs(carpeta_destino, exist_ok=True)

ruta_ventas = os.path.join(carpeta_destino, 'ventas_caoticas.csv')
ruta_clientes = os.path.join(carpeta_destino, 'clientes_dim.csv')

df_ventas.to_csv(ruta_ventas, index=False)
df_clientes.to_csv(ruta_clientes, index=False)

print("-" * 50)
print(f"✅ ¡Archivos de prueba generados con éxito en la carpeta '{carpeta_destino}'!")
print(f"📊 Dataset Principal (Ventas): {len(df_ventas)} filas (Contiene duplicados y nulos)")
print(f"📘 Dataset Secundario (Clientes): {len(df_clientes)} filas (Tabla dimensional limpia)")
print("-" * 50)