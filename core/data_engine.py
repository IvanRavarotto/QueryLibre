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
        # Memoria del motor
        self.df = None
        self.df2 = None  # Dataset temporal para uniones (JOIN)
        self.historial_pasos = []
        self.df_history = []

    def registrar_paso(self, descripcion):
        self.historial_pasos.append(descripcion)

    def _savepoint(self):
        """Método interno para guardar el estado antes de una transformación."""
        self.df_history.append(self.df.copy())

    def deshacer(self):
        """Restaura el DataFrame al estado anterior."""
        if self.df_history and len(self.historial_pasos) > 1:
            self.df = self.df_history.pop()
            self.historial_pasos.pop()
            return True
        return False

    def cargar_archivo(self, file_path):
        """Ingesta el dataset principal a memoria."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv':
            self.df = pd.read_csv(file_path)
        else:
            self.df = pd.read_excel(file_path)
        
        # Reset de seguridad
        self.historial_pasos = []
        self.df_history = []
        self.registrar_paso(f"Origen: {os.path.basename(file_path)}")

    def eliminar_duplicados(self):
        self._savepoint()
        antes = len(self.df)
        self.df = self.df.drop_duplicates()
        eliminadas = antes - len(self.df)
        
        texto = f"Se eliminaron {eliminadas} filas duplicadas" if eliminadas > 0 else "Eliminar duplicados (0 filas)"
        self.registrar_paso(texto)
        return eliminadas

    def limpiar_nulos(self, modo):
        self._savepoint()
        antes = len(self.df)
        self.df = self.df.dropna(how=modo)
        eliminadas = antes - len(self.df)
        
        tipo = "completamente vacías" if modo == 'all' else "con datos faltantes"
        texto = f"Se eliminaron {eliminadas} filas {tipo}" if eliminadas > 0 else f"Limpieza de nulos (0 filas {tipo})"
        self.registrar_paso(texto)

    def eliminar_columna(self, col_name):
        if col_name in self.df.columns:
            self._savepoint()
            self.df = self.df.drop(columns=[col_name])
            self.registrar_paso(f"Columna eliminada: '{col_name}'")
            return True
        return False

    def renombrar_columna(self, old_name, new_name):
        if old_name in self.df.columns:
            self._savepoint()
            self.df = self.df.rename(columns={old_name: new_name})
            self.registrar_paso(f"Columna renombrada: '{old_name}' ➔ '{new_name}'")
            return True
        return False

    def editar_celda(self, indice_real, col_name, nuevo_valor):
        self._savepoint()
        col_idx = self.df.columns.get_loc(col_name)
        self.df.iat[indice_real, col_idx] = nuevo_valor
        self.registrar_paso(f"Edición manual: Fila {indice_real + 1}, Col. '{col_name}'")

    def calcular_columna(self, c1, op, c2, new_col):
        self._savepoint()
        
        # Smart Parser interno
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

    def combinar_columnas(self, c1, sep_texto, c2, new_col):
        self._savepoint()
        if sep_texto == "Espacio": separador = " "
        elif sep_texto == "Guion (-)": separador = " - "
        elif sep_texto == "Coma (,)": separador = ", "
        else: separador = ""

        self.df[new_col] = self.df[c1].astype(str) + separador + self.df[c2].astype(str)
        self.df[new_col] = self.df[new_col].str.replace('nan', '', case=False).str.strip(separador)
        self.registrar_paso(f"Combinar: '{c1}' y '{c2}' ➔ '{new_col}'")

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

    def filtrar_datos(self, col, cond, val):
        self._savepoint()
        antes = len(self.df)

        if cond == "Es Igual a":
            self.df = self.df[self.df[col].astype(str).str.lower() == val.lower()]
        elif cond == "Contiene el texto":
            self.df = self.df[self.df[col].astype(str).str.contains(val, case=False, na=False)]
        elif cond == "Es Mayor que (>)":
            self.df = self.df[pd.to_numeric(self.df[col], errors='coerce') > float(val)]
        elif cond == "Es Menor que (<)":
            self.df = self.df[pd.to_numeric(self.df[col], errors='coerce') < float(val)]
        elif cond == "Está Vacío (Nulo)":
            self.df = self.df[self.df[col].isna() | (self.df[col] == "")]

        eliminadas = antes - len(self.df)
        self.registrar_paso(f"Filtro: '{col}' {cond} '{val}' (-{eliminadas} filas)")

    # ---- MÉTODOS DE INTEGRACIÓN Y EXPORTACIÓN ----
    
    def cargar_df2(self, file_path):
        """Ingesta el dataset dimensional secundario."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv':
            self.df2 = pd.read_csv(file_path)
        else:
            self.df2 = pd.read_excel(file_path)

    def aplicar_union(self, k1, k2, tipo_str):
        self._savepoint()
        how_join = "left" if "Left" in tipo_str else "inner"
        self.df = pd.merge(self.df, self.df2, left_on=k1, right_on=k2, how=how_join)
        self.registrar_paso(f"Unión ({how_join}): usando '{k1}' = '{k2}'")

    def exportar_archivo(self, formato, file_path):
        if "CSV" in formato:
            self.df.to_csv(file_path, index=False)
        elif "Excel" in formato:
            self.df.to_excel(file_path, index=False)
        elif "SQLite" in formato:
            conn = sqlite3.connect(file_path)
            self.df.to_sql("datos_limpios", conn, if_exists="replace", index=False)
            conn.close()
            
        self.registrar_paso(f"💾 Exportado a {formato.split(' ')[1]}: {os.path.basename(file_path)}")