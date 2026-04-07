import os

content = '''import os
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
    cadr = motor.df.copy(deep=True)
    with pytest.raises(RuntimeError):
        motor.cambiar_tipo_dato('ID_Cliente', 'Número Entero')
    assert motor.df.shape == cadr.shape
    assert (motor.df['Fecha Compra'].astype(str).str.contains('not a date|2024-13-01|31/02/2024', na=False)).any()
    with pytest.raises(RuntimeError):
        motor.cambiar_tipo_dato('Fecha Compra', 'Fecha')

def test_filtro_y_eliminar_duplicados_experto():
    motor = MotorDatos()
    motor.cargar_archivo(VENTAS)
    original = len(motor.df)
    motor.eliminar_duplicados()
    assert len(motor.df) <= original
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
    file_path.write_text('id\\n1')
    bad = os.path.relpath(str(file_path), start=os.getcwd())
    assert '..' in bad
    with pytest.raises(ValueError):
        motor.cargar_df2(bad)

def test_macro_rollback_en_error_de_paso():
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    tab = PestañaTrabajo(root, root)
    tab.motor.df = pd.DataFrame({'x': ['2024-01-01', 'not a date']})
    pasos = [
        {'action': 'editar_celda', 'params': {'indice_real': 0, 'col_name': 'x', 'nuevo_valor': '2024-01-01'}},
        {'action': 'cambiar_tipo_dato', 'params': {'col_name': 'x', 'nuevo_tipo': 'Fecha'}}
    ]
    original = tab.motor.df.copy(deep=True)
    with pytest.raises(RuntimeError):
        tab._apply_macro_steps(pasos)
    assert tab.motor.df.equals(original)
    root.destroy()

def test_normalize_columns_resuelve_duplicados():
    motor = MotorDatos()
    motor.df = pd.DataFrame([[1, 2]], columns=['col', 'col'])
    motor._normalize_columns()
    assert 'col' in motor.df.columns
    assert any(c.startswith('col_') for c in motor.df.columns if c != 'col')

def test_macro_fuzz_parametros_peligrosos():
    import unittest.mock as mock
    with mock.patch('tkinter.Tk'):
        with mock.patch('main.PestañaTrabajo.__init__', return_value=None):
            tab = PestañaTrabajo(None, None)
            tab.motor = MotorDatos()
            tab.motor.df = pd.DataFrame({'x': [1, 2]})
            tab.ALLOWED_MACRO_ACTIONS = {'eliminar_duplicados'}
            tab.DISALLOWED_MACRO_PARAM_KEYS = {'__class__', '__dict__', '__globals__'}
            pasos_peligrosos = [
                {'action': 'eliminar_duplicados', 'params': {'__class__': 'malicious'}},
                {'action': 'eliminar_duplicados', 'params': {'__dict__': 'bad'}},
                {'action': 'eliminar_duplicados', 'params': {'normal': 'ok', '__globals__': 'evil'}}
            ]
            for paso in pasos_peligrosos:
                original_df = tab.motor.df.copy()
                tab._apply_macro_steps([paso])
                assert tab.motor.df.equals(original_df)

def test_macro_accion_no_permitida():
    import unittest.mock as mock
    with mock.patch('tkinter.Tk'):
        with mock.patch('main.PestañaTrabajo.__init__', return_value=None):
            tab = PestañaTrabajo(None, None)
            tab.motor = MotorDatos()
            tab.motor.df = pd.DataFrame({'x': [1, 2]})
            tab.ALLOWED_MACRO_ACTIONS = {'eliminar_duplicados'}
            tab.DISALLOWED_MACRO_PARAM_KEYS = {'__class__', '__dict__'}
            pasos_invalidos = [
                {'action': '__init__', 'params': {}},
                {'action': 'borrar_archivo', 'params': {}}
            ]
            for paso in pasos_invalidos:
                original_df = tab.motor.df.copy()
                tab._apply_macro_steps([paso])
                assert tab.motor.df.equals(original_df)

def test_agrupar_datos_basico():
    motor = MotorDatos()
    motor.df = pd.DataFrame({'categoria': ['A', 'A', 'B', 'B'], 'valor': [1, 2, 3, 4]})
    motor.agrupar_datos('categoria', 'valor', 'suma')
    expected = pd.DataFrame({'categoria': ['A', 'B'], 'suma_valor': [3, 7]})
    pd.testing.assert_frame_equal(motor.df, expected)

def test_agrupar_datos_promedio():
    motor = MotorDatos()
    motor.df = pd.DataFrame({'grupo': ['X', 'X', 'Y'], 'numero': [10, 20, 30]})
    motor.agrupar_datos('grupo', 'numero', 'promedio')
    expected = pd.DataFrame({'grupo': ['X', 'Y'], 'promedio_numero': [15.0, 30.0]})
    pd.testing.assert_frame_equal(motor.df, expected)

def test_agrupar_datos_columna_invalida():
    motor = MotorDatos()
    motor.df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    with pytest.raises(ValueError, match="Columna de agrupación 'c' no existe"):
        motor.agrupar_datos('c', 'b', 'suma')

def test_agrupar_datos_funcion_invalida():
    motor = MotorDatos()
    motor.df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    with pytest.raises(ValueError, match="Función 'invalida' no válida"):
        motor.agrupar_datos('a', 'b', 'invalida')

def test_buscar_reemplazar_global():
    motor = MotorDatos()
    motor.df = pd.DataFrame({'a': ['hello', 'world'], 'b': ['hello', 'test']})
    motor.buscar_reemplazar('hello', 'hi')
    expected = pd.DataFrame({'a': ['hi', 'world'], 'b': ['hi', 'test']})
    pd.testing.assert_frame_equal(motor.df, expected)

def test_buscar_reemplazar_columna_especifica():
    motor = MotorDatos()
    motor.df = pd.DataFrame({'a': ['hello', 'world'], 'b': ['hello', 'test']})
    motor.buscar_reemplazar('hello', 'hi', 'a')
    expected = pd.DataFrame({'a': ['hi', 'world'], 'b': ['hello', 'test']})
    pd.testing.assert_frame_equal(motor.df, expected)

def test_buscar_reemplazar_regex():
    motor = MotorDatos()
    motor.df = pd.DataFrame({'a': ['test123', 'abc456'], 'b': ['test789', 'xyz000']})
    motor.buscar_reemplazar(r'test\\d+', 'replaced', usar_regex=True)
    expected = pd.DataFrame({'a': ['replaced', 'abc456'], 'b': ['replaced', 'xyz000']})
    pd.testing.assert_frame_equal(motor.df, expected)

def test_buscar_reemplazar_columna_inexistente():
    motor = MotorDatos()
    motor.df = pd.DataFrame({'a': [1, 2]})
    with pytest.raises(ValueError, match="Columna 'b' no existe"):
        motor.buscar_reemplazar('1', '2', 'b')
'''

os.remove('tests/test_data_engine.py')
with open('tests/test_data_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)