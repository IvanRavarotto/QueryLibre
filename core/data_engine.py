import logging
import pandas as pd
import os
import sqlite3
import re
import shutil
import tempfile
import zipfile  
import json      
import io
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
import urllib.parse

LOGGER = logging.getLogger("QueryLibre")
class MotorDatos:
    """
    Cerebro de QueryLibre.
    Se encarga exclusivamente de la lógica de procesamiento de datos con Pandas.
    Aislado completamente de la interfaz gráfica (Tkinter).
    """
    def __init__(self):
        self.df = None
        self.df2 = None  
        self.historial_pasos = []
        self.macro_steps = []
        self.hay_cambios = False
        
        # Pilas de Deshacer (Undo)
        self.df_history = []
        
        # Pilas de Rehacer (Redo)
        self.redo_history = []
        self.redo_historial_pasos = []
        self.redo_macro_steps = []

        self.step_counter = 0 
        master_cache = os.path.join(tempfile.gettempdir(), "QueryLibre_Cache")
        self.cache_dir = os.path.join(master_cache, f"tab_{id(self)}")
        os.makedirs(self.cache_dir, exist_ok=True)

    def registrar_paso(self, descripcion):
        self.historial_pasos.append(descripcion)
        self.hay_cambios = True

    def _savepoint(self, limpiar_redo=True):
        if self.df is None: return
        
        if limpiar_redo:
            self.redo_history.clear()
            self.redo_historial_pasos.clear()
            self.redo_macro_steps.clear()
        
        self.step_counter += 1
        file_path = os.path.join(self.cache_dir, f"undo_{self.step_counter}.parquet")
        
        try:
            self.df.to_parquet(file_path)
        except Exception as e:
            # Si hay tipos mixtos, PyArrow falla. Forzamos todo lo que sea 'object' a texto.
            LOGGER.warning(f"Tipos mixtos detectados, forzando a string para Parquet: {e}")
            for col in self.df.select_dtypes(include=['object']).columns:
                self.df[col] = self.df[col].astype(str)
            self.df.to_parquet(file_path)
        
        self.df_history.append(file_path)

        if len(self.df_history) > 10:
            old_file = self.df_history.pop(0)
            if os.path.exists(old_file):
                os.remove(old_file)

    def deshacer(self):
        """Retrocede al estado anterior guardando el actual en la pila de rehacer."""
        if len(self.df_history) <= 1: # Mantenemos al menos el estado inicial
            return False
        
        # 1. Guardar el presente en REDO
        archivo_presente = os.path.join(self.cache_dir, f"redo_{len(self.redo_history)}.parquet")
        self.df.to_parquet(archivo_presente)
        self.redo_history.append(archivo_presente)
        
        if self.historial_pasos: self.redo_historial_pasos.append(self.historial_pasos.pop())
        if self.macro_steps: self.redo_macro_steps.append(self.macro_steps.pop())
        
        # 2. Recuperar el pasado de UNDO
        self.df_history.pop() # Eliminamos el 'yo' actual de la pila de historia
        archivo_pasado = self.df_history[-1] # El nuevo tope es el pasado real
        self.df = pd.read_parquet(archivo_pasado)
        
        self.hay_cambios = len(self.historial_pasos) > 1
        
        return True

    def rehacer(self):
        """Avanza al estado futuro recuperando desde la pila de rehacer."""
        if not self.redo_history:
            return False
            
        # 1. Guardar el presente de vuelta en UNDO (SIN destruir el REDO)
        self._savepoint(limpiar_redo=False)
        
        # 2. Cargar el futuro desde REDO
        archivo_futuro = self.redo_history.pop()
        self.df = pd.read_parquet(archivo_futuro)
        
        if self.redo_historial_pasos: self.historial_pasos.append(self.redo_historial_pasos.pop())
        if self.redo_macro_steps: self.macro_steps.append(self.redo_macro_steps.pop())
        
        self.hay_cambios = len(self.historial_pasos) > 1
        
        return True
    
    def _rollback_error(self):
        """Restaura el DataFrame desde el disco si una operación falla a la mitad."""
        if self.df_history:
            last_file = self.df_history.pop()
            if os.path.exists(last_file):
                self.df = pd.read_parquet(last_file)
                os.remove(last_file)
    
    def _check_df(self):
        if self.df is None:
            raise ValueError("No hay dataset cargado.")

    def _normalize_columns(self):
        if self.df is not None:
            self.df.columns = self._normalize_columns_generic(self.df.columns)

    def _normalize_columns_df2(self):
        if self.df2 is not None:
            self.df2.columns = self._normalize_columns_generic(self.df2.columns)

    def _normalize_columns_generic(self, columns):
        new_columns = []
        counts = {}
        for col in columns:
            if isinstance(col, str):
                col_normal = col.strip()
                col_normal = re.sub(r"[^\w\s]+", "_", col_normal)
                if col_normal == "":
                    col_normal = "columna"
                if col_normal in counts:
                    counts[col_normal] += 1
                    col_normal = f"{col_normal}_{counts[col_normal]}"
                else:
                    counts[col_normal] = 1
                new_columns.append(col_normal)
            else:
                new_columns.append(col)
        return new_columns

    def _validate_loader_path(self, file_path):
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"No es un archivo válido: {file_path}")

        normalized_path = file_path.replace('\\', '/').strip()
        if not os.path.isabs(file_path) and '..' in normalized_path.split('/'):
            raise ValueError("Ruta de archivo inválida: no se permiten referencias relativas")

        cleaned = os.path.normpath(file_path)
        if any(part == '..' for part in cleaned.split(os.sep)):
            # solo ocurrirá en paths absolutos directos; cuánto seguro, aún validamos
            raise ValueError("Ruta de archivo inválida: no se permiten referencias relativas")

        if re.search(r'[\x00-\x1f]', file_path):
            raise ValueError("Ruta de archivo inválida: contiene caracteres no permitidos")

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.csv', '.xls', '.xlsx']:
            raise ValueError(f"Formato de archivo no soportado: {ext}")

        return ext

    def _sanitize_for_export(self, df):
        # Evita CSV/Excel injection de fórmulas iniciadas en = + - @ y protege casos con prefijo ' en datasources maliciosas
        df_copy = df.copy()
        for c in df_copy.columns:
            if df_copy[c].dtype == object or pd.api.types.is_string_dtype(df_copy[c]):
                def protect(v):
                    if isinstance(v, str):
                        starts = v.lstrip()
                        if starts.startswith(('=', '+', '-', '@')):
                            return "'" + v
                        if v.startswith("'") and len(v) > 1 and v[1] in ('=', '+', '-', '@'):
                            return "'" + v
                    return v
                df_copy[c] = df_copy[c].apply(protect)
        return df_copy

    def cargar_archivo(self, filepath):
        ext = self._validate_loader_path(filepath)
        self.nombre_archivo = os.path.basename(filepath)

        if ext == '.csv':
            try:
                self.df = pd.read_csv(filepath, encoding='utf-8')
            except Exception:
                self.df = pd.read_csv(filepath, encoding='latin-1')
        elif ext in ['.xls', '.xlsx']:
            self.df = pd.read_excel(filepath, engine='openpyxl')

        self._normalize_columns()
        self.historial_pasos = []
        self.df_history = []
        self.macro_steps = []
        
        # 1. Guardamos el estado inicial en la memoria (Undo)
        self._savepoint()
        
        # 2. Registramos el paso (Esto pondrá hay_cambios en True temporalmente)
        self.registrar_paso(f"Origen: {self.nombre_archivo}")
        
        # 3. Restauramos la bandera para que no marque el asterisco (*) recién abierto
        self.hay_cambios = False

    def eliminar_duplicados(self):
        self._check_df()
        self._savepoint()

        antes = len(self.df)
        self.df = self.df.drop_duplicates()
        eliminadas = antes - len(self.df)

        self.registrar_paso(f"Se eliminaron {eliminadas} filas duplicadas" if eliminadas > 0 else "Eliminar duplicados (0 filas)")
        self.macro_steps.append({"action": "eliminar_duplicados", "params": {}})
        return eliminadas

    def limpiar_nulos(self, modo):
        self._check_df()
        if modo not in ['all', 'any']:
            raise ValueError("Modo de limpieza inválido")

        self._savepoint()
        antes = len(self.df)
        self.df = self.df.dropna(how=modo)
        eliminadas = antes - len(self.df)

        tipo = "completamente vacías" if modo == 'all' else "con datos faltantes"
        self.registrar_paso(f"Se eliminaron {eliminadas} filas {tipo}" if eliminadas > 0 else f"Limpieza de nulos (0 filas {tipo})")
        self.macro_steps.append({"action": "limpiar_nulos", "params": {"modo": modo}})

    def limpiar_cache(self):
        """Borra la carpeta temporal de la sesión."""
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
    
    def eliminar_columna(self, col_name):
        self._check_df()
        if col_name in self.df.columns:
            self._savepoint() # <--- Guarda el .parquet en .ql_cache
            self.df = self.df.drop(columns=[col_name])
            self.registrar_paso(f"Columna eliminada: '{col_name}'") # <--- Esto actualiza la lista
            return True
        return False

    def renombrar_columna(self, old_name, new_name):
        self._check_df()
        if old_name in self.df.columns and new_name:
            if new_name in self.df.columns:
                raise ValueError("El nombre de columna ya existe")
            self._savepoint()
            self.df = self.df.rename(columns={old_name: new_name})
            self.registrar_paso(f"Columna renombrada: '{old_name}' ➔ '{new_name}'")
            self.macro_steps.append({"action": "renombrar_columna", "params": {"old_name": old_name, "new_name": new_name}})
            return True
        return False

    def editar_celda(self, indice_real, col_name, nuevo_valor):
        self._check_df()
        if col_name not in self.df.columns:
            raise KeyError("Columna inexistente")

        if indice_real < 0 or indice_real >= len(self.df):
            raise IndexError("Índice de fila fuera de rango")

        self._savepoint()
        col_idx = self.df.columns.get_loc(col_name)

        if isinstance(nuevo_valor, str) and nuevo_valor.strip() == "":
            valor_final = pd.NA
        else:
            valor_final = nuevo_valor

        self.df.iat[indice_real, col_idx] = valor_final
        self.registrar_paso(f"Edición manual: Fila {indice_real + 1}, Col. '{col_name}'")
        self.macro_steps.append({"action": "editar_celda", "params": {"indice_real": indice_real, "col_name": col_name, "nuevo_valor": nuevo_valor}})

    def calcular_columna(self, c1, op, c2, new_col):
        self._check_df()

        if not c1 or not c2 or not new_col:
            raise ValueError("Columnas inválidas")
        if c1 not in self.df.columns or c2 not in self.df.columns:
            raise KeyError("Columna de origen no encontrada")
        if new_col in self.df.columns:
            raise ValueError("La columna destino ya existe")

        self._savepoint()

        def limpiar_y_convertir(serie):
            serie_limpia = serie.astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
            return pd.to_numeric(serie_limpia, errors='coerce')

        s1 = limpiar_y_convertir(self.df[c1])
        s2 = limpiar_y_convertir(self.df[c2])

        if op == "+":
            resultado = s1 + s2
        elif op == "-":
            resultado = s1 - s2
        elif op == "*":
            resultado = s1 * s2
        elif op == "/":
            resultado = s1 / s2.replace(0, pd.NA)
        else:
            raise ValueError("Operación no soportada")

        self.df[new_col] = resultado
        self.registrar_paso(f"Cálculo: '{new_col}' = '{c1}' {op} '{c2}'")
        self.macro_steps.append({"action": "calcular_columna", "params": {"c1": c1, "op": op, "c2": c2, "new_col": new_col}})

    def combinar_columnas(self, c1, sep_texto, c2, new_col):
        self._check_df()
        if c1 not in self.df.columns or c2 not in self.df.columns:
            raise KeyError("Columna de origen no encontrada")
        if not new_col:
            raise ValueError("Nombre de columna destino inválido")

        separadores = {
            "Espacio": " ",
            "Guion (-)": " - ",
            "Coma (,)": ", ",
            "Sin separador": "",
        }
        separador = separadores.get(sep_texto, "")

        self._savepoint()
        nueva_serie = self.df[c1].astype(str).fillna("") + separador + self.df[c2].astype(str).fillna("")
        self.df[new_col] = nueva_serie.str.replace('nan', '', case=False).str.strip()

        self.registrar_paso(f"Combinar: '{c1}' y '{c2}' ➔ '{new_col}'")
        self.macro_steps.append({"action": "combinar_columnas", "params": {"c1": c1, "sep_texto": sep_texto, "c2": c2, "new_col": new_col}})

    def dividir_columna(self, col, sep_texto):
        self._check_df()
        if col not in self.df.columns:
            raise KeyError("Columna a dividir no existe")

        separadores = {
            "Espacio": " ",
            "Coma (,)": ",",
            "Guion (-)": "-",
            "Barra (/)": "/",
        }
        separador = separadores.get(sep_texto, sep_texto)

        self._savepoint()
        df_split = self.df[col].astype(str).str.split(separador, expand=True)
        df_split.columns = [f"{col}_{i+1}" for i in range(df_split.shape[1])]
        self.df = pd.concat([self.df, df_split], axis=1)

        self.registrar_paso(f"División: Columna '{col}' por '{separador}'")
        self.macro_steps.append({"action": "dividir_columna", "params": {"col": col, "sep_texto": sep_texto}})

    def filtrar_datos(self, col, cond, val):
        self._check_df()
        if col not in self.df.columns:
            raise KeyError("Columna de filtro no encontrada")

        self._savepoint()
        antes = len(self.df)

        if cond == "Es Igual a":
            self.df = self.df[self.df[col].astype(str).str.lower() == str(val).lower()]
        elif cond == "Contiene el texto":
            self.df = self.df[self.df[col].astype(str).str.contains(str(val), case=False, na=False, regex=False)]
        elif cond == "Es Mayor que (>)":
            val_num = pd.to_numeric(val, errors='coerce')
            if pd.isna(val_num):
                raise ValueError("Filtro numérico inválido")
            self.df = self.df[pd.to_numeric(self.df[col], errors='coerce') > val_num]
        elif cond == "Es Menor que (<)":
            val_num = pd.to_numeric(val, errors='coerce')
            if pd.isna(val_num):
                raise ValueError("Filtro numérico inválido")
            self.df = self.df[pd.to_numeric(self.df[col], errors='coerce') < val_num]
        elif cond == "Está Vacío (Nulo)":
            self.df = self.df[self.df[col].isna() | (self.df[col].astype(str) == "")]
        else:
            raise ValueError("Condición de filtro desconocida")

        eliminadas = antes - len(self.df)
        self.registrar_paso(f"Filtro: '{col}' {cond} '{val}' (-{eliminadas} filas)")
        self.macro_steps.append({"action": "filtrar_datos", "params": {"col": col, "cond": cond, "val": val}})

    def cambiar_tipo_dato(self, col_name, nuevo_tipo, forzar=False):
        """Cambia el tipo de dato. Si forzar=True, ignora los errores y los convierte en NaN."""
        self._check_df()
        if col_name not in self.df.columns:
            raise KeyError("Columna no encontrada")

        self._savepoint()

        try:
            if nuevo_tipo == "Texto":
                self.df[col_name] = self.df[col_name].astype(str).fillna("").replace('nan', '')

            elif nuevo_tipo in ["Número Entero", "Número Decimal"]:
                s = self.df[col_name].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
                s = s.replace(['', 'nan', 'None', '<NA>'], pd.NA)
                converted = pd.to_numeric(s, errors='coerce')
                total_non_null = s.notna().sum()
                valid = converted.notna().sum()
                invalid = total_non_null - valid
                
                # Si hay inválidos y no forzamos, lanzamos el error (protección activa)
                if invalid > 0 and not forzar:
                    raise RuntimeError(f"No se pudo convertir a número: {invalid} valores inválidos. Ejemplo (fila, valor): [...]")

                if nuevo_tipo == "Número Entero":
                    self.df[col_name] = converted.round().astype('Int64')
                else:
                    self.df[col_name] = converted.astype('float64')

            elif nuevo_tipo == "Fecha":
                converted = pd.to_datetime(self.df[col_name], errors='coerce')
                total_non_null = self.df[col_name].notna().sum()
                valid = converted.notna().sum()
                invalid = total_non_null - valid
                
                if invalid > 0 and not forzar:
                    raise RuntimeError(f"No se pudo convertir a Fecha: {invalid} valores inválidos. Ejemplo (fila, valor): [...]")
                    
                self.df[col_name] = converted

            else:
                raise ValueError("Tipo de conversión desconocido")

            self.registrar_paso(f"Tipo cambiado: '{col_name}' ➔ {nuevo_tipo}")
            self.macro_steps.append({"action": "cambiar_tipo_dato", "params": {"col_name": col_name, "nuevo_tipo": nuevo_tipo, "forzar": forzar}})
            return True

        except Exception as e:
            self._rollback_error() 
            raise e 

    def previsualizar_casteo(self, col_name, nuevo_tipo):
        """Simula el casteo en memoria RAM y devuelve un listado de valores que van a fallar."""
        self._check_df()
        if col_name not in self.df.columns or nuevo_tipo == "Texto": return []

        serie = self.df[col_name]
        errores = []

        if nuevo_tipo in ["Número Entero", "Número Decimal"]:
            s = serie.astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
            s = s.replace(['', 'nan', 'None', '<NA>'], pd.NA)
            converted = pd.to_numeric(s, errors='coerce')
            invalid_mask = s.notna() & converted.isna()
        elif nuevo_tipo == "Fecha":
            converted = pd.to_datetime(serie, errors='coerce')
            invalid_mask = serie.notna() & converted.isna()

        if invalid_mask.any():
            idx_malos = self.df.index[invalid_mask].tolist()
            val_malos = serie.loc[invalid_mask].astype(str).tolist()
            # Tomamos hasta 100 errores para mostrar en la tabla sin congelar la pantalla
            errores = [{"fila": i+1, "valor": v} for i, v in zip(idx_malos[:100], val_malos[:100])]
        
        return errores                # 2. Lanzamos el error EXACTO sin envolverlo


    # =========================================================
    # INTEGRACIÓN Y EXPORTACIÓN
    # =========================================================
    def cargar_df2(self, file_path):
        ext = self._validate_loader_path(file_path)

        if ext == '.csv':
            try:
                self.df2 = pd.read_csv(file_path, encoding='utf-8')
            except Exception:
                self.df2 = pd.read_csv(file_path, encoding='latin-1')
        elif ext in ['.xls', '.xlsx']:
            self.df2 = pd.read_excel(file_path, engine='openpyxl')

        self._normalize_columns_df2()

    def aplicar_union(self, k1, k2, tipo_str):
        self._check_df()
        if self.df2 is None:
            raise ValueError("No hay segundo dataset cargado para la unión")
        if k1 not in self.df.columns or k2 not in self.df2.columns:
            raise KeyError("Llave de unión inválida")

        self._savepoint()
        how_join = "left" if "Left" in tipo_str else "inner"

        try:
            self.df = pd.merge(self.df, self.df2, left_on=k1, right_on=k2, how=how_join)
        except ValueError as e:
            # Si hay incompatibilidad de tipos (str vs int etc.), forzamos ambos lados a string y volvemos a intentar.
            # Esto permite un comportamiento más robusto en datasets mixtos generados con datos "caóticos".
            if k1 in self.df.columns and k2 in self.df2.columns:
                self.df[k1] = self.df[k1].astype(str).replace('nan', '', regex=False)
                self.df2[k2] = self.df2[k2].astype(str).replace('nan', '', regex=False)
                try:
                    self.df = pd.merge(self.df, self.df2, left_on=k1, right_on=k2, how=how_join)
                except Exception as e2:
                    if self.df_history:
                        self.df = self._rollback_error()
                    raise e2
            else:
                if self.df_history:
                    self.df = self._rollback_error()
                raise e
        except Exception as e:
            if self.df_history:
                self.df = self._rollback_error()
            raise e

        self.registrar_paso(f"Unión ({how_join}): usando '{k1}' = '{k2}'")
        self.macro_steps.append({"action": "aplicar_union", "params": {"k1": k1, "k2": k2, "tipo_str": tipo_str}})

    def exportar_archivo(self, formato, file_path):
        self._check_df()

        if "CSV" in formato:
            df_sanitizado = self._sanitize_for_export(self.df)
            df_sanitizado.to_csv(file_path, index=False)
        elif "Excel" in formato:
            df_sanitizado = self._sanitize_for_export(self.df)
            df_sanitizado.to_excel(file_path, index=False)
        elif "SQLite" in formato:
            conn = sqlite3.connect(file_path)
            self.df.to_sql("datos_limpios", conn, if_exists="replace", index=False)
            conn.close()
        else:
            raise ValueError("Formato de exportación no soportado")

        self.hay_cambios = False
        
        tipo_save = formato.split(' ')[1] if ' ' in formato else formato
        self.registrar_paso(f"💾 Exportado a {tipo_save}: {os.path.basename(file_path)}")
        
    def agrupar_datos(self, col_agrupar, col_valor, funcion):
        """Agrupa los datos y realiza una operación matemática, forzando valores numéricos."""
        self._check_df()
        self._savepoint()
        
        # Copiamos para no dañar el original si algo falla
        temp_df = self.df.copy()
        
        # Limpieza forzada: Quitamos $, quitamos comas, y convertimos a número. Lo que no sirva se vuelve 0.
        temp_df[col_valor] = pd.to_numeric(
            temp_df[col_valor].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False), 
            errors='coerce'
        ).fillna(0)
        
        funciones_map = {'suma': 'sum', 'promedio': 'mean', 'conteo': 'count', 'mínimo': 'min', 'máximo': 'max'}
        
        # Realizamos la agrupación
        res = temp_df.groupby(col_agrupar)[col_valor].agg(funciones_map[funcion]).reset_index()
        
        # Renombramos la columna de resultado para mayor claridad
        res.columns = [col_agrupar, f"{funcion}_{col_valor}"]
        
        # Aplicamos el resultado y registramos
        self.df = res
        self.registrar_paso(f"Agrupar: '{col_agrupar}' por '{funcion}' en '{col_valor}'")
    
    def buscar_reemplazar(self, buscar, reemplazar, columna=None, usar_regex=False):
        """Reemplaza valores. Si usar_regex es True, valida la expresión primero."""
        self._check_df()
        self._savepoint()

        if usar_regex:
            try:
                # Validamos que la regex sea sintácticamente correcta
                re.compile(buscar)
            except re.error as e:
                raise ValueError(f"Expresión Regular inválida: {e}")

        if columna:
            if columna not in self.df.columns:
                raise ValueError(f"Columna '{columna}' no existe.")
            
            # Aplicamos el reemplazo
            self.df[columna] = self.df[columna].astype(str).replace(
                buscar, reemplazar, regex=usar_regex
            )
            self.registrar_paso(f"Buscar/Reemplazar en '{columna}': '{buscar}' ➔ '{reemplazar}'")
        else:
            # Reemplazo global
            self.df = self.df.replace(buscar, reemplazar, regex=usar_regex)
            self.registrar_paso(f"Buscar/Reemplazar global: '{buscar}' ➔ '{reemplazar}'")
        
        self.macro_steps.append({
            "action": "buscar_reemplazar", 
            "params": {"buscar": buscar, "reemplazar": reemplazar, "columna": columna, "usar_regex": usar_regex}
        })
    
    def obtener_radiografia(self, col_name):
        """Genera un reporte estadístico de la columna solicitada."""
        if self.df is None or col_name not in self.df.columns: return "Sin datos"
        
        serie = self.df[col_name]
        total = len(serie)
        nulos = serie.isna().sum()
        unicos = serie.nunique()
        tipo = str(serie.dtype)

        reporte = f"📈 RADIOGRAFÍA: {col_name}\n"
        reporte += f"========================\n\n"
        reporte += f"• Tipo de Dato: {tipo}\n"
        reporte += f"• Total de Filas: {total}\n"
        reporte += f"• Valores Nulos: {nulos} ({(nulos/total)*100:.1f}%)\n"
        reporte += f"• Valores Únicos: {unicos}\n"

        # Si Pandas detecta que la columna es matemática, agregamos más datos
        if pd.api.types.is_numeric_dtype(serie):
            reporte += f"\n🔢 ESTADÍSTICAS:\n"
            reporte += f"------------------------\n"
            reporte += f"• Mínimo: {serie.min()}\n"
            reporte += f"• Máximo: {serie.max()}\n"
            reporte += f"• Promedio: {serie.mean():.2f}\n"

        return reporte
    
    def guardar_proyecto(self, filepath):
        """Empaqueta el DataFrame y el historial en un archivo .qlp (ZIP comprimido)."""
        if self.df is None:
            raise ValueError("No hay datos para guardar.")

        if not filepath.endswith('.qlp'):
            filepath += '.qlp'

        # 1. Preparamos el "Cerebro" (Historial y metadatos)
        metadata = {
            "nombre_archivo": getattr(self, 'nombre_archivo', 'Proyecto_QueryLibre'),
            "historial_pasos": self.historial_pasos,
            "macro_steps": self.macro_steps,
            "step_counter": getattr(self, 'step_counter', 0)
        }

        # 2. Preparamos el "Cuerpo" (La tabla de datos) en la memoria RAM
        parquet_buffer = io.BytesIO()
        self.df.to_parquet(parquet_buffer)

        # 3. Metemos todo en la "Caja" (.qlp)
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('data.parquet', parquet_buffer.getvalue())
            zf.writestr('metadata.json', json.dumps(metadata, ensure_ascii=False, indent=4))
        
        # 4. Reseteamos la bandera de seguridad porque ya está guardado
        self.registrar_paso(f"📦 Proyecto guardado: {os.path.basename(filepath)}")
        self.hay_cambios = False 

    def cargar_proyecto(self, filepath):
        """Desempaqueta un archivo .qlp y restaura la sesión (Protección Zip Bomb)."""
        if not zipfile.is_zipfile(filepath):
            raise ValueError("El archivo está corrupto o no es un proyecto (.qlp)")

        # Límite de seguridad: 500 MB máximo de descompresión en RAM
        MAX_SIZE = 500 * 1024 * 1024 

        with zipfile.ZipFile(filepath, 'r') as zf:
            # 1. Validar y extraer el historial
            info_meta = zf.getinfo('metadata.json')
            if info_meta.file_size > MAX_SIZE: raise ValueError("Metadatos demasiado grandes.")
            with zf.open(info_meta) as f:
                metadata = json.load(f)
            
            # 2. Validar y extraer la tabla (Aquí está el riesgo de Zip Bomb)
            info_data = zf.getinfo('data.parquet')
            if info_data.file_size > MAX_SIZE: raise ValueError("Datos exceden el límite de seguridad.")
            with zf.open(info_data) as f:
                self.df = pd.read_parquet(io.BytesIO(f.read()))

        # 3. Restauramos la memoria del motor
        self.nombre_archivo = metadata.get("nombre_archivo", os.path.basename(filepath))
        self.historial_pasos = metadata.get("historial_pasos", [])
        self.macro_steps = metadata.get("macro_steps", [])
        self.step_counter = metadata.get("step_counter", 0)
        
        # 4. Limpiamos y creamos el primer punto de guardado
        self.df_history = []
        self._savepoint() 
        self.hay_cambios = False
        
    def generar_sugerencias_limpieza(self):
        """Escanea el dataset y devuelve una lista de sugerencias de limpieza inteligente."""
        if self.df is None or self.df.empty: return []
        sugerencias = []

        # 1. Detectar filas duplicadas
        duplicados = self.df.duplicated().sum()
        if duplicados > 0:
            sugerencias.append({
                "id": "duplicados",
                "titulo": "Eliminar Duplicados",
                "descripcion": f"Se detectaron {duplicados} filas exactamente iguales.",
                "accion": self.eliminar_duplicados,
                "kwargs": {}
            })

        # 2. Detectar columnas inútiles (Más del 50% nulos o 1 solo valor)
        umbral_nulos = len(self.df) * 0.5
        for col in self.df.columns:
            nulos = self.df[col].isna().sum()
            unicos = self.df[col].nunique()

            if nulos > umbral_nulos:
                porcentaje = (nulos / len(self.df)) * 100
                sugerencias.append({
                    "id": f"nulos_{col}",
                    "titulo": f"Borrar '{col}' (Casi vacía)",
                    "descripcion": f"Tiene un {porcentaje:.1f}% de valores nulos (vacíos).",
                    "accion": self.eliminar_columna,
                    "kwargs": {"col_name": col}
                })
            elif unicos == 1 and nulos == 0:
                sugerencias.append({
                    "id": f"constante_{col}",
                    "titulo": f"Borrar '{col}' (Constante)",
                    "descripcion": "Todos los valores de esta columna son idénticos. No aporta información.",
                    "accion": self.eliminar_columna,
                    "kwargs": {"col_name": col}
                })

        return sugerencias

    def exportar_csv_seguro(self, filepath):
        """Exporta el DataFrame a CSV en bloques de 100k filas para evitar congelamiento."""
        self._check_df()
        
        chunk_size = 100000 # 100k filas por bloque
        total_filas = len(self.df)
        
        for i in range(0, total_filas, chunk_size):
            bloque = self.df.iloc[i : i + chunk_size]
            
            # Si es el primer bloque (i==0), escribimos el archivo y la cabecera.
            # Para los siguientes bloques, "adjuntamos" (append mode 'a') sin la cabecera.
            modo_escritura = 'w' if i == 0 else 'a'
            escribir_cabecera = True if i == 0 else False
            
            bloque.to_csv(filepath, mode=modo_escritura, header=escribir_cabecera, index=False, encoding='utf-8')
            
    def generar_reporte_salud(self):
        """Genera un diccionario con métricas globales de salud del dataset (Data Profiling)."""
        if self.df is None or self.df.empty: return None
        
        total_filas = len(self.df)
        total_cols = len(self.df.columns)
        total_celdas = total_filas * total_cols
        celdas_nulas = self.df.isna().sum().sum()
        
        # Calcular el porcentaje de celdas con datos reales
        porcentaje_nulos = (celdas_nulas / total_celdas) * 100 if total_celdas > 0 else 0
        
        cols_numericas = len(self.df.select_dtypes(include='number').columns)
        cols_texto = total_cols - cols_numericas
        
        # Calcular cuánto pesa este dataframe en la memoria RAM
        memoria_mb = self.df.memory_usage(deep=False).sum() / (1024 * 1024)

        return {
            "Filas": f"{total_filas:,}".replace(',', '.'),
            "Columnas": total_cols,
            "Salud": f"{100 - porcentaje_nulos:.1f}%",
            "Numéricas": cols_numericas,
            "Texto": cols_texto,
            "Memoria": f"{memoria_mb:.2f} MB"
        }
    
    def detectar_autocasteo(self):
        """Escanea el dataset sin modificarlo y devuelve un diccionario con sugerencias seguras."""
        self._check_df()
        propuestas = {}
        
        for col in self.df.columns:
            if self.df[col].dtype == 'object' or pd.api.types.is_string_dtype(self.df[col]):
                # 1. Probar Números (Limpiando $ y comas temporalmente en la serie)
                s = self.df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
                s = s.replace(['', 'nan', 'None', '<NA>', 'NaN'], pd.NA)
                
                s_numeric = pd.to_numeric(s, errors='coerce')
                datos_reales = s.notna().sum()
                
                if datos_reales > 0 and s_numeric.notna().sum() == datos_reales:
                    propuestas[col] = "Número"
                    continue
                
                # 2. Probar Fechas
                s_date = pd.to_datetime(self.df[col], errors='coerce')
                validos_orig_date = self.df[col].notna().sum()
                if validos_orig_date > 0 and s_date.notna().sum() == validos_orig_date:
                    propuestas[col] = "Fecha"
                    
        return propuestas

    def aplicar_autocasteo_confirmado(self, propuestas):
        """Aplica los casteos que el usuario aprobó en la interfaz."""
        if not propuestas: return
        self._savepoint()
        
        for col, tipo in propuestas.items():
            if tipo == "Número":
                s = self.df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
                s = s.replace(['', 'nan', 'None', '<NA>', 'NaN'], pd.NA)
                self.df[col] = pd.to_numeric(s, errors='coerce')
            elif tipo == "Fecha":
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                
        self.registrar_paso(f"✨ Auto-Casteo: {len(propuestas)} columnas")
        self.macro_steps.append({"action": "aplicar_autocasteo_confirmado", "params": {"propuestas": propuestas}})
        
    def probar_conexion_sql(self, motor_bd, host, puerto, usuario, password, base_datos):
        """Intenta establecer una conexión con el servidor SQL y devuelve un mensaje de estado."""
        
        # Codificamos la contraseña para que los caracteres especiales (@, #, /, etc.) no rompan la URL
        pass_segura = urllib.parse.quote_plus(password) if password else ""
        
        if motor_bd == "MySQL":
            url = f"mysql+pymysql://{usuario}:{pass_segura}@{host}:{puerto}/{base_datos}"
        elif motor_bd == "PostgreSQL":
            url = f"postgresql://{usuario}:{pass_segura}@{host}:{puerto}/{base_datos}"
        elif motor_bd == "SQL Server":
            url = f"mssql+pyodbc://{usuario}:{pass_segura}@{host}:{puerto}/{base_datos}?driver=ODBC+Driver+17+for+SQL+Server"
        else:
            return False, "Motor de base de datos no soportado."

        try:
            engine = create_engine(url, connect_args={'connect_timeout': 5})
            # Inspeccionamos el motor para extraer los nombres de las tablas
            inspector = inspect(engine)
            tablas = inspector.get_table_names()
            return True, tablas
        except SQLAlchemyError as e:
            # Corrección: Un solo corchete [-1] para acceder al último elemento de la lista
            mensaje_limpio = str(e).split(']')[-1].strip() if ']' in str(e) else str(e)
            return False, f"Error de conexión:\n{mensaje_limpio}"
        
    def importar_tabla_sql(self, motor_bd, host, puerto, usuario, password, base_datos, tabla):
        """Conecta a la base de datos e importa la tabla seleccionada al DataFrame principal."""
        pass_segura = urllib.parse.quote_plus(password) if password else ""

        if motor_bd == "MySQL":
            url = f"mysql+pymysql://{usuario}:{pass_segura}@{host}:{puerto}/{base_datos}"
        elif motor_bd == "PostgreSQL":
            url = f"postgresql://{usuario}:{pass_segura}@{host}:{puerto}/{base_datos}"
        elif motor_bd == "SQL Server":
            url = f"mssql+pyodbc://{usuario}:{pass_segura}@{host}:{puerto}/{base_datos}?driver=ODBC+Driver+17+for+SQL+Server"
        else:
            raise ValueError("Motor de base de datos no soportado.")

        # Creamos el motor de conexión
        engine = create_engine(url)

        # ¡AQUÍ OCURRE LA MAGIA! Pandas lee directamente desde SQL
        self.df = pd.read_sql_table(tabla, con=engine)

        # Reseteamos el entorno como si fuera un archivo nuevo
        self.nombre_archivo = f"SQL: {base_datos}.{tabla}"
        self._normalize_columns()
        self.historial_pasos = []
        self.df_history = []
        self.redo_history.clear()
        self.macro_steps = []

        self._savepoint()
        self.registrar_paso(f"Origen SQL: {tabla}")
        self.hay_cambios = False