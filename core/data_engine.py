import pandas as pd
import os
import sqlite3

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
        self.df_history.append(self.df.copy())

    def deshacer(self):
        if self.df_history and len(self.historial_pasos) > 1:
            self.df = self.df_history.pop()
            self.historial_pasos.pop()
            self.macro_steps.pop() 
            return True
        return False

    def cargar_archivo(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv': self.df = pd.read_csv(file_path)
        else: self.df = pd.read_excel(file_path)
        
        self.historial_pasos = []
        self.df_history = []
        self.macro_steps = [] 
        self.registrar_paso(f"Origen: {os.path.basename(file_path)}")

    def eliminar_duplicados(self):
        self._savepoint()
        antes = len(self.df)
        self.df = self.df.drop_duplicates()
        eliminadas = antes - len(self.df)
        
        self.registrar_paso(f"Se eliminaron {eliminadas} filas duplicadas" if eliminadas > 0 else "Eliminar duplicados (0 filas)")
        self.macro_steps.append({"action": "eliminar_duplicados", "params": {}})
        return eliminadas

    def limpiar_nulos(self, modo):
        self._savepoint()
        antes = len(self.df)
        self.df = self.df.dropna(how=modo)
        eliminadas = antes - len(self.df)
        
        tipo = "completamente vacías" if modo == 'all' else "con datos faltantes"
        self.registrar_paso(f"Se eliminaron {eliminadas} filas {tipo}" if eliminadas > 0 else f"Limpieza de nulos (0 filas {tipo})")
        self.macro_steps.append({"action": "limpiar_nulos", "params": {"modo": modo}})

    def eliminar_columna(self, col_name):
        if col_name in self.df.columns:
            self._savepoint()
            self.df = self.df.drop(columns=[col_name])
            self.registrar_paso(f"Columna eliminada: '{col_name}'")
            self.macro_steps.append({"action": "eliminar_columna", "params": {"col_name": col_name}})
            return True
        return False

    def renombrar_columna(self, old_name, new_name):
        if old_name in self.df.columns:
            self._savepoint()
            self.df = self.df.rename(columns={old_name: new_name})
            self.registrar_paso(f"Columna renombrada: '{old_name}' ➔ '{new_name}'")
            self.macro_steps.append({"action": "renombrar_columna", "params": {"old_name": old_name, "new_name": new_name}})
            return True
        return False

    def editar_celda(self, indice_real, col_name, nuevo_valor):
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
        self._savepoint()
        def limpiar_y_convertir(serie):
            serie_limpia = serie.astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
            return pd.to_numeric(serie_limpia, errors='coerce')

        s1 = limpiar_y_convertir(self.df[c1])
        s2 = limpiar_y_convertir(self.df[c2])

        if op == "+": self.df[new_col] = s1 + s2
        elif op == "-": self.df[new_col] = s1 - s2
        elif op == "*": self.df[new_col] = s1 * s2
        elif op == "/": self.df[new_col] = s1 / s2

        self.registrar_paso(f"Cálculo: '{new_col}' = '{c1}' {op} '{c2}'")
        self.macro_steps.append({"action": "calcular_columna", "params": {"c1": c1, "op": op, "c2": c2, "new_col": new_col}})

    def combinar_columnas(self, c1, sep_texto, c2, new_col):
        self._savepoint()
        if sep_texto == "Espacio": separador = " "
        elif sep_texto == "Guion (-)": separador = " - "
        elif sep_texto == "Coma (,)": separador = ", "
        else: separador = ""

        self.df[new_col] = self.df[c1].astype(str) + separador + self.df[c2].astype(str)
        self.df[new_col] = self.df[new_col].str.replace('nan', '', case=False).str.strip(separador)
        self.registrar_paso(f"Combinar: '{c1}' y '{c2}' ➔ '{new_col}'")
        self.macro_steps.append({"action": "combinar_columnas", "params": {"c1": c1, "sep_texto": sep_texto, "c2": c2, "new_col": new_col}})

    def dividir_columna(self, col, sep_texto):
        self._savepoint()
        if sep_texto == "Espacio": separador = " "
        elif sep_texto == "Coma (,)": separador = ","
        elif sep_texto == "Guion (-)": separador = "-"
        elif sep_texto == "Barra (/)": separador = "/"
        else: separador = sep_texto

        df_split = self.df[col].astype(str).str.split(separador, expand=True)
        df_split.columns = [f"{col}_{i+1}" for i in range(df_split.shape[1])]
        self.df = pd.concat([self.df, df_split], axis=1)
        self.registrar_paso(f"División: Columna '{col}' por '{separador}'")
        self.macro_steps.append({"action": "dividir_columna", "params": {"col": col, "sep_texto": sep_texto}})

    def filtrar_datos(self, col, cond, val):
        self._savepoint()
        antes = len(self.df)

        if cond == "Es Igual a": self.df = self.df[self.df[col].astype(str).str.lower() == val.lower()]
        elif cond == "Contiene el texto": self.df = self.df[self.df[col].astype(str).str.contains(val, case=False, na=False)]
        elif cond == "Es Mayor que (>)": self.df = self.df[pd.to_numeric(self.df[col], errors='coerce') > float(val)]
        elif cond == "Es Menor que (<)": self.df = self.df[pd.to_numeric(self.df[col], errors='coerce') < float(val)]
        elif cond == "Está Vacío (Nulo)": self.df = self.df[self.df[col].isna() | (self.df[col] == "")]

        eliminadas = antes - len(self.df)
        self.registrar_paso(f"Filtro: '{col}' {cond} '{val}' (-{eliminadas} filas)")
        self.macro_steps.append({"action": "filtrar_datos", "params": {"col": col, "cond": cond, "val": val}})

    def cambiar_tipo_dato(self, col_name, nuevo_tipo):
        self._savepoint()
        try:
            if nuevo_tipo == "Texto":
                self.df[col_name] = self.df[col_name].astype(str).replace('nan', '')
                
            elif nuevo_tipo in ["Número Entero", "Número Decimal"]:
                # 1. Limpiamos símbolos y comas
                s = self.df[col_name].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
                # 2. FULMINAMOS textos vacíos y "nan" inyectados
                s = s.replace(['', 'nan', 'None', '<NA>'], pd.NA)
                # 3. Forzamos conversión numérica segura
                s = pd.to_numeric(s, errors='coerce')
                
                if nuevo_tipo == "Número Entero":
                    # Convertimos a float, redondeamos, y luego a Int64
                    self.df[col_name] = s.astype('float64').round().astype('Int64')
                else:
                    self.df[col_name] = s.astype('float64')
                    
            elif nuevo_tipo == "Fecha":
                self.df[col_name] = pd.to_datetime(self.df[col_name], errors='coerce')
            
            self.registrar_paso(f"Tipo cambiado: '{col_name}' ➔ {nuevo_tipo}")
            self.macro_steps.append({"action": "cambiar_tipo_dato", "params": {"col_name": col_name, "nuevo_tipo": nuevo_tipo}})
            return True
            
        except Exception as e:
            self.df_history.pop()
            raise e

    # =========================================================
    # INTEGRACIÓN Y EXPORTACIÓN
    # =========================================================
    def cargar_df2(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv': self.df2 = pd.read_csv(file_path)
        else: self.df2 = pd.read_excel(file_path)

    def aplicar_union(self, k1, k2, tipo_str):
        self._savepoint()
        how_join = "left" if "Left" in tipo_str else "inner"
        self.df = pd.merge(self.df, self.df2, left_on=k1, right_on=k2, how=how_join)
        self.registrar_paso(f"Unión ({how_join}): usando '{k1}' = '{k2}'")
        self.macro_steps.append({"action": "aplicar_union", "params": {"k1": k1, "k2": k2, "tipo_str": tipo_str}})

    def exportar_archivo(self, formato, file_path):
        if "CSV" in formato: self.df.to_csv(file_path, index=False)
        elif "Excel" in formato: self.df.to_excel(file_path, index=False)
        elif "SQLite" in formato:
            conn = sqlite3.connect(file_path)
            self.df.to_sql("datos_limpios", conn, if_exists="replace", index=False)
            conn.close()
        self.registrar_paso(f"💾 Exportado a {formato.split(' ')[1]}: {os.path.basename(file_path)}")
        
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