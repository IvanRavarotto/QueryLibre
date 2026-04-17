import pandas as pd
import numpy as np
import os
import random

# Configuramos la semilla para que los errores sean siempre los mismos en cada prueba
random.seed(42)
np.random.seed(42)

# Subimos la base para pasar las 200 filas de la paginación
n_records = 450 # Llegará a 500 exactos con los duplicados

# --- 1. DATASET PRINCIPAL (CAÓTICO) ---
productos = ['Laptop Dell XPS', 'Monitor LG 27"', 'Teclado Mecánico', 'Mouse Inalámbrico', 'Auriculares Sony', 'Silla Ergonomica', 'Escritorio Standing']
categorias = ['Electronica', 'Perifericos', 'Mobiliario']

datos_ventas = {
    ' ID Transaccion ': [f'TRX-{str(i).zfill(4)}' for i in range(1, n_records + 1)], # Espacios molestos
    'ID_Cliente': [random.randint(1, 50) for _ in range(n_records)], # Clientes del 1 al 50
    'Producto_Nombre': [random.choice(productos) for _ in range(n_records)],
    'Categoria_Prod': [random.choice(categorias) for _ in range(n_records)],
    'Sub_Cat': ['Genérica' for _ in range(n_records)], 
    'Cantidad ': [str(random.randint(1, 15)) for _ in range(n_records)], # Guardado como texto
    'precio_unitario_usd': [f"${random.uniform(15.0, 2500.0):,.2f}" for _ in range(n_records)], # Símbolo y comas (Ej: $1,500.00)
    # Generamos fechas distribuidas a lo largo del año
    'Fecha Compra': pd.date_range(start='2024-01-01', periods=n_records).strftime('%Y-%m-%d').tolist(),
    'Notas_Internas': ['Borrar esta columna' for _ in range(n_records)] # Columna inútil
}

df_ventas = pd.DataFrame(datos_ventas)
# forzamos dtype objet para inyección de casos no numéricos
for col in ['ID_Cliente', 'Cantidad ', 'precio_unitario_usd', 'Fecha Compra']:
    if col in df_ventas.columns:
        df_ventas[col] = df_ventas[col].astype(object)

# --- ENSUCIAR EL DATASET PRINCIPAL ---
# 1. Inyectar Nulos (NaN) aleatorios (Escalados a la nueva cantidad de filas)
for _ in range(35): df_ventas.loc[random.randint(0, n_records-1), 'Producto_Nombre'] = np.nan
for _ in range(25): df_ventas.loc[random.randint(0, n_records-1), 'Cantidad '] = np.nan
for _ in range(20): df_ventas.loc[random.randint(0, n_records-1), 'ID_Cliente'] = np.nan

# 2. Romper el formato de fechas (distribuidos en distintas páginas)
df_ventas.loc[10, 'Fecha Compra'] = '01/15/2024'
df_ventas.loc[250, 'Fecha Compra'] = '15-01-2024'
df_ventas.loc[420, 'Fecha Compra'] = '2024/02/28'

# 3. Forzar Duplicados (Copiamos 50 filas al azar y las pegamos al final)
indices_duplicar = random.sample(range(n_records), 50)
df_ventas = pd.concat([df_ventas, df_ventas.iloc[indices_duplicar]], ignore_index=True)

# 3.5. Añadir casos extremos para pruebas exigentes
for idx in random.sample(list(df_ventas.index), 30):
    # Valores de ID cliente no numéricos en algunas filas
    df_ventas.loc[idx, 'ID_Cliente'] = random.choice(['N/A', 'unknown', 'NULL', '999999999999999999999'])

for idx in random.sample(list(df_ventas.index), 25):
    # Cantidad con formatos inválidos
    df_ventas.loc[idx, 'Cantidad '] = random.choice(['', '0', '-5', '30.5', 'once'])

for idx in random.sample(list(df_ventas.index), 20):
    # Precio con símbolos o texto
    df_ventas.loc[idx, 'precio_unitario_usd'] = random.choice(['$', '15,00', '17.5.3', 'error', '2.099,99'])

for idx in random.sample(list(df_ventas.index), 20):
    # Fecha con formatos inapropiados
    df_ventas.loc[idx, 'Fecha Compra'] = random.choice(['2024-13-01', '31/02/2024', 'not a date', '', np.nan])

# 4. Desordenar filas para que los duplicados se mezclen en todas las páginas
df_ventas = df_ventas.sample(frac=1).reset_index(drop=True) 


# --- 2. DATASET SECUNDARIO (DIMENSIONAL PARA MERGE/JOIN) ---
# Creamos clientes del 1 al 60. (Nota: En ventas solo hay del 1 al 50, ideal para probar Left Join)
paises = ['Argentina', 'Chile', 'Colombia', 'Mexico', 'España', 'Uruguay', 'Perú']
suscripciones = ['Básico', 'Premium', 'Enterprise']

datos_clientes = {
    'Cliente_ID': range(1, 61), # ¡LLAVE DIFERENTE! ('Cliente_ID' vs 'ID_Cliente')
    'Nombre_Empresa': [f'Empresa_Cli_{i}' for i in range(1, 61)], # Nombres genéricos escalables
    'Pais_Origen': [random.choice(paises) for _ in range(60)],
    'Suscripcion': [random.choice(suscripciones) for _ in range(60)],
    'Descuento_Aprobado': [round(random.uniform(0.05, 0.30), 2) for _ in range(60)]
}

df_clientes = pd.DataFrame(datos_clientes)


# --- 3. GUARDAR LOS ARCHIVOS ---
# Guarda los archivos en una subcarpeta 'data' dentro de 'tests'
carpeta_destino = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(carpeta_destino, exist_ok=True)

ruta_ventas = os.path.join(carpeta_destino, 'ventas_caoticas.csv')
ruta_ventas_exigente = os.path.join(carpeta_destino, 'ventas_caoticas_exigente.csv')
ruta_clientes = os.path.join(carpeta_destino, 'clientes_dim.csv')

print("-" * 50)
print(f"Archivos de prueba generados con éxito en la carpeta '{carpeta_destino}'")
print(f"Dataset Original (Ventas): {len(df_ventas)} filas")
print(f"Dataset Exigente (Ventas_exigente): {len(df_ventas)} filas")
print(f"Dataset Secundario (Clientes): {len(df_clientes)} filas")
print("-" * 50)