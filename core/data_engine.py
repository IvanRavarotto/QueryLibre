import pandas as pd
import os
import sqlite3
import re

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
        self.df_history = []
        self.macro_steps = []

    def registrar_paso(self, descripcion):
        self.historial_pasos.append(descripcion)

    def _savepoint(self):
        if self.df is None:
            return
        self.df_history.append(self.df.copy(deep=True))

    def deshacer(self):
        if not self.df_history or len(self.historial_pasos) <= 1:
            return False

        self.df = self.df_history.pop()
        if self.historial_pasos:
            self.historial_pasos.pop()
        if self.macro_steps:
            self.macro_steps.pop()

        return True

    def _check_df(self):
        if self.df is None:
            raise ValueError("No hay dataset cargado.")

    def _normalize_columns(self):
        if self.df is not None:
            new_columns = []
            for col in self.df.columns:
                if isinstance(col, str):
                    col_normal = col.strip()
                    # Reemplaza caracteres especiales exceptuando espacios para evitar ruptura de nombres actuales
                    col_normal = re.sub(r"[^\w\s]+", "_", col_normal)
                    new_columns.append(col_normal)
                else:
                    new_columns.append(col)
            self.df.columns = new_columns

    def _normalize_columns_df2(self):
        if self.df2 is not None:
            new_columns = []
            for col in self.df2.columns:
                if isinstance(col, str):
                    col_normal = col.strip()
                    col_normal = re.sub(r"[^\w\s]+", "_", col_normal)
                    new_columns.append(col_normal)
                else:
                    new_columns.append(col)
            self.df2.columns = new_columns

    def _sanitize_column_name(self, col):
        if not isinstance(col, str):
            return col
        normalized = col.strip()
        normalized = re.sub(r"[^\w]+", "_", normalized)
        if normalized == "":
            normalized = "columna"
        return normalized

    def _sanitize_for_export(self, df):
        # Evita CSV/Excel injection de fórmulas iniciadas en = + - @
        df_copy = df.copy()
        for c in df_copy.columns:
            if df_copy[c].dtype == object or pd.api.types.is_string_dtype(df_copy[c]):
                df_copy[c] = df_copy[c].apply(
                    lambda v: f"'{v}" if isinstance(v, str) and v.startswith(('=', '+', '-', '@')) else v
                )
        return df_copy

    def cargar_archivo(self, file_path):
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv':
            try:
                self.df = pd.read_csv(file_path, encoding='utf-8')
            except Exception:
                self.df = pd.read_csv(file_path, encoding='latin-1')
        elif ext in ['.xls', '.xlsx']:
            self.df = pd.read_excel(file_path, engine='openpyxl')
        else:
            raise ValueError(f"Formato de archivo no soportado: {ext}")

        self._normalize_columns()
        self.historial_pasos = []
        self.df_history = []
        self.macro_steps = []
        self.registrar_paso(f"Origen: {os.path.basename(file_path)}")

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

    def eliminar_columna(self, col_name):
        self._check_df()
        if col_name in self.df.columns:
            self._savepoint()
            self.df = self.df.drop(columns=[col_name])
            self.registrar_paso(f"Columna eliminada: '{col_name}'")
            self.macro_steps.append({"action": "eliminar_columna", "params": {"col_name": col_name}})
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

    def cambiar_tipo_dato(self, col_name, nuevo_tipo):
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
                invalid_mask = s.notna() & converted.isna()
                invalid_indices = self.df.index[invalid_mask].tolist()
                invalid_values = self.df[col_name].loc[invalid_mask].astype(str).tolist()
                if valid == 0:
                    raise ValueError("No se pudo convertir a número: no hay valores numéricos válidos")
                if invalid > 0:
                    muestra = list(zip(invalid_indices[:10], invalid_values[:10]))
                    raise ValueError(
                        f"No se pudo convertir a número: {invalid} valores inválidos. "
                        f"Ejemplo (fila, valor): {muestra}"
                    )

                if nuevo_tipo == "Número Entero":
                    # Conservamos NaN como <NA> en Int64
                    self.df[col_name] = converted.round().astype('Int64')
                else:
                    self.df[col_name] = converted.astype('float64')

            elif nuevo_tipo == "Fecha":
                converted = pd.to_datetime(self.df[col_name], errors='coerce')
                total_non_null = self.df[col_name].notna().sum()
                valid = converted.notna().sum()
                invalid = total_non_null - valid
                invalid_mask = self.df[col_name].notna() & converted.isna()
                invalid_indices = self.df.index[invalid_mask].tolist()
                invalid_values = self.df[col_name].loc[invalid_mask].astype(str).tolist()
                if valid == 0:
                    raise ValueError("No se pudo convertir a Fecha: no hay valores válidos")
                if invalid > 0:
                    muestra = list(zip(invalid_indices[:10], invalid_values[:10]))
                    raise ValueError(
                        f"No se pudo convertir a Fecha: {invalid} valores inválidos. "
                        f"Ejemplo (fila, valor): {muestra}"
                    )
                self.df[col_name] = converted

            else:
                raise ValueError("Tipo de conversión desconocido")

            self.registrar_paso(f"Tipo cambiado: '{col_name}' ➔ {nuevo_tipo}")
            self.macro_steps.append({"action": "cambiar_tipo_dato", "params": {"col_name": col_name, "nuevo_tipo": nuevo_tipo}})
            return True

        except Exception as e:
            if self.df_history:
                self.df = self.df_history.pop()
            raise RuntimeError(f"Error en cambiar_tipo_dato: {e}") from e


    # =========================================================
    # INTEGRACIÓN Y EXPORTACIÓN
    # =========================================================
    def cargar_df2(self, file_path):
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv':
            try:
                self.df2 = pd.read_csv(file_path, encoding='utf-8')
            except Exception:
                self.df2 = pd.read_csv(file_path, encoding='latin-1')
        elif ext in ['.xls', '.xlsx']:
            self.df2 = pd.read_excel(file_path, engine='openpyxl')
        else:
            raise ValueError(f"Formato de archivo no soportado: {ext}")

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
                        self.df = self.df_history.pop()
                    raise e2
            else:
                if self.df_history:
                    self.df = self.df_history.pop()
                raise e
        except Exception as e:
            if self.df_history:
                self.df = self.df_history.pop()
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

        tipo_save = formato.split(' ')[1] if ' ' in formato else formato
        self.registrar_paso(f"💾 Exportado a {tipo_save}: {os.path.basename(file_path)}")
        
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