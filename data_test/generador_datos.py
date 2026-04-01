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
carpeta_destino = 'data_test'
os.makedirs(carpeta_destino, exist_ok=True)

ruta_ventas = os.path.join(carpeta_destino, 'ventas_caoticas.csv')
ruta_ventas_exigente = os.path.join(carpeta_destino, 'ventas_caoticas_exigente.csv')
ruta_clientes = os.path.join(carpeta_destino, 'clientes_dim.csv')

df_ventas.to_csv(ruta_ventas, index=False)
df_ventas.to_csv(ruta_ventas_exigente, index=False)
df_clientes.to_csv(ruta_clientes, index=False)

print("-" * 50)
print(f"Archivos de prueba generados con éxito en la carpeta '{carpeta_destino}'")
print(f"Dataset Original (Ventas): {len(df_ventas)} filas")
print(f"Dataset Exigente (Ventas_exigente): {len(df_ventas)} filas")
print(f"Dataset Secundario (Clientes): {len(df_clientes)} filas")
print("-" * 50)

# --- 4. GENERAR ARCHIVO DE PRUEBAS (pytest) ---
carpeta_tests = 'tests'
os.makedirs(carpeta_tests, exist_ok=True)
ruta_tests = os.path.join(carpeta_tests, 'test_data_engine.py')

contenido_test = '''import os
import pytest
from core.data_engine import MotorDatos

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_test')
VENTAS = os.path.join(DATA_DIR, 'ventas_caoticas_exigente.csv')
CLIENTES = os.path.join(DATA_DIR, 'clientes_dim.csv')


def test_cargar_y_limpiar_csv():
    motor = MotorDatos()
    motor.cargar_archivo(VENTAS)
    assert motor.df is not None
    nantes = len(motor.df)
    motor.eliminar_duplicados()
    npost = len(motor.df)
    assert npost <= nantes


def test_cambiar_tipo_id_cliente_a_entero():
    motor = MotorDatos()
    motor.cargar_archivo(VENTAS)
    motor.df.loc[0, 'ID_Cliente'] = 'NoVal'
    with pytest.raises(RuntimeError):
        motor.cambiar_tipo_dato('ID_Cliente', 'Número Entero')
    assert motor.df.loc[0, 'ID_Cliente'] == 'NoVal' or str(motor.df.loc[0, 'ID_Cliente']) == 'NoVal'


def test_cambiar_tipo_fecha_compra_fallo_y_estado():
    motor = MotorDatos()
    motor.cargar_archivo(VENTAS)
    motor.df.loc[0, 'Fecha Compra'] = 'texto-mal'
    with pytest.raises(RuntimeError):
        motor.cambiar_tipo_dato('Fecha Compra', 'Fecha')


def test_union_datasets():
    motor = MotorDatos()
    motor.cargar_archivo(VENTAS)
    motor.cargar_df2(CLIENTES)
    motor.aplicar_union('ID_Cliente', 'Cliente_ID', 'Izquierda (Left Join)')
    assert 'Nombre_Empresa' in motor.df.columns


def test_pipeline_conversión_extrema():
    motor = MotorDatos()
    motor.cargar_archivo(VENTAS)

    # Se espera que, aunque existan valores rotos, el método falle con RuntimeError y no corrompa df.
    cadr = motor.df.copy(deep=True)
    with pytest.raises(RuntimeError):
        motor.cambiar_tipo_dato('ID_Cliente', 'Número Entero')

    # El dataset original debe permanecer igual tras el fallo
    assert motor.df.shape == cadr.shape

    # Validar que hay al menos una fecha inválida para hacer explosion de conversión
    assert (motor.df['Fecha Compra'].astype(str).str.contains('not a date|2024-13-01|31/02/2024', na=False)).any()

    # Intenta conversión de fecha (debe lanzar en dataset fuerte)
    with pytest.raises(RuntimeError):
        motor.cambiar_tipo_dato('Fecha Compra', 'Fecha')


def test_filtro_y_eliminar_duplicados_experto():
    motor = MotorDatos()
    motor.cargar_archivo(VENTAS)

    # Tras eliminar duplicados, siempre hay menos o igual filas
    original = len(motor.df)
    motor.eliminar_duplicados()
    assert len(motor.df) <= original

    # Filtrar por una categoría factible y validar que no explota.
    motor.cargar_archivo(VENTAS)
    motor.filtrar_datos('Categoria_Prod', 'Contiene el texto', 'Electronica')
    assert 'Electronica' in motor.df['Categoria_Prod'].astype(str).str.cat(sep=' ')
'''

with open(ruta_tests, 'w', encoding='utf-8') as f:
    f.write(contenido_test)

print(f"Archivo de tests generado en: {ruta_tests}")