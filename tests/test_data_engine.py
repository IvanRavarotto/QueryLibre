import os
import sys
import pandas as pd
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.data_engine import MotorDatos
from main import PestañaTrabajo

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


def test_aplicar_union_sin_df2_rechaza():
    motor = MotorDatos()
    motor.cargar_archivo(VENTAS)
    with pytest.raises(ValueError, match="No hay segundo dataset cargado"):
        motor.aplicar_union('ID_Cliente', 'Cliente_ID', 'Izquierda (Left Join)')


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

def test_cambiar_tipo_dato_indica_posiciones_invalidas():
    motor = MotorDatos()
    motor.df = pd.DataFrame({'x': ['1', 'unknown', '3', 'bad', '5']})
    with pytest.raises(RuntimeError) as exc:
        motor.cambiar_tipo_dato('x', 'Número Entero')
    texto = str(exc.value)
    assert 'valores inválidos' in texto
    assert 'Ejemplo (fila, valor)' in texto


def test_cambiar_tipo_fecha_indica_posiciones_invalidas():
    motor = MotorDatos()
    motor.df = pd.DataFrame({'f': ['2024-01-01', 'not a date', '2024-03-10']})
    with pytest.raises(RuntimeError) as exc:
        motor.cambiar_tipo_dato('f', 'Fecha')
    texto = str(exc.value)
    assert 'valores inválidos' in texto
    assert 'Ejemplo (fila, valor)' in texto

def test_macro_whitelist_no_methods_maliciosas():
    assert 'eliminar_duplicados' in PestañaTrabajo.ALLOWED_MACRO_ACTIONS
    assert '__init__' not in PestañaTrabajo.ALLOWED_MACRO_ACTIONS
    assert '__dict__' not in PestañaTrabajo.ALLOWED_MACRO_ACTIONS


def test_editar_celda_fuera_rango_lanza_indexerror():
    motor = MotorDatos()
    motor.cargar_archivo(VENTAS)
    with pytest.raises(IndexError):
        motor.editar_celda(-1, 'ID_Cliente', '100')
    with pytest.raises(IndexError):
        motor.editar_celda(len(motor.df), 'ID_Cliente', '100')


def test_filtrar_datos_contiene_escapa_regex():
    motor = MotorDatos()
    motor.cargar_archivo(VENTAS)
    # si se usa un patrón regex peligroso, no se interpreta como regex en la búsqueda
    motor.filtrar_datos('Categoria_Prod', 'Contiene el texto', '.*')
    assert len(motor.df) == 0 or '.*' in motor.df['Categoria_Prod'].astype(str).str.cat(sep=' ')


def test_exportar_csv_formula_injection_escapado(tmp_path):
    motor = MotorDatos()
    motor.df = pd.DataFrame({'a': ['=1+1', '+2', 'normal', '@cmd'], 'b': ['x', 'y', 'z', 'w']})
    out_file = tmp_path / 'salida.csv'
    motor.exportar_archivo('CSV', str(out_file))

    contenido = out_file.read_text(encoding='utf-8')
    assert "'=1+1" in contenido
    assert "'+2" in contenido
    assert "'@cmd" in contenido


def test_exportar_csv_formula_injection_escapado_comillas_como_prefijo(tmp_path):
    motor = MotorDatos()
    motor.df = pd.DataFrame({'a': ["'=1", "'@cmd", "normal"]})
    out_file = tmp_path / 'salida2.csv'
    motor.exportar_archivo('CSV', str(out_file))

    contenido = out_file.read_text(encoding='utf-8')
    assert "''=1" in contenido
    assert "''@cmd" in contenido


def test_cargar_archivo_formato_no_soportado(tmp_path):
    motor = MotorDatos()
    bad_file = tmp_path / 'mal.txt'
    bad_file.write_text('x')
    with pytest.raises(ValueError):
        motor.cargar_archivo(str(bad_file))


def test_cargar_df2_ruta_relativa_invalida(tmp_path):
    motor = MotorDatos()
    subdir = tmp_path / 'subdir'
    subdir.mkdir()
    file_path = subdir / 'mal.csv'
    file_path.write_text('id\n1')

    # ruta relativa con '..' (desde la carpeta actual) debe fallar por seguridad
    bad = os.path.relpath(str(file_path), start=os.getcwd())
    assert '..' in bad
    with pytest.raises(ValueError):
        motor.cargar_df2(bad)
