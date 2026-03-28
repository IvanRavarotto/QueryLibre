# Librerías estándar para el proyecto
import os
import sys
import math 
import ctypes
import tkinter as tk
from tkinter import filedialog, ttk

# CustomTkinter para la UI
import customtkinter as ctk

# IMPORTAMOS NUESTRO CEREBRO (El Motor de Datos)
from core.data_engine import MotorDatos

ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("blue") 

# ---- FUNCIÓN AUXILIAR DE EMPAQUETADO ----
def obtener_ruta(ruta_relativa):
    try:
        ruta_base = sys._MEIPASS
    except AttributeError:
        ruta_base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(ruta_base, ruta_relativa)


class QueryLibreApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ---- CONEXIÓN CON EL MOTOR DE DATOS (MVC) ----
        # ¡Toda la memoria (df, historial) ahora vive acá adentro!
        self.motor = MotorDatos()
        
        self.pagina_actual = 1
        self.filas_por_pagina = 200
        
        # ---- CONFIGURACIÓN DE LA VENTANA PRINCIPAL ----
        self.title("QueryLibre - Motor de Transformación de Datos")
        self.geometry("1100x650") 
        self.minsize(900, 500)
        
        ruta_icono = obtener_ruta(os.path.join("assets", "main.ico"))
        try:
            self.iconbitmap(ruta_icono) 
        except Exception as e:
            print(f"Advertencia - Error con el ícono: {e}")

        try:
            myappid = 'ivanravarotto.querylibre.app.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except AttributeError:
            pass
        
        # ---- LAYOUT PRINCIPAL ----
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)    

        # ---- 1. PANEL LATERAL (SIDEBAR) ----
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew") 
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="QueryLibre", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_cargar = ctk.CTkButton(self.sidebar_frame, text="📁 Cargar Archivo", command=self.cargar_archivo)
        self.btn_cargar.grid(row=1, column=0, padx=20, pady=10)

        self.btn_transformar = ctk.CTkButton(self.sidebar_frame, text="🔗 Unir Datasets", state="disabled", command=self.unir_datasets)
        self.btn_transformar.grid(row=2, column=0, padx=20, pady=10)

        self.btn_exportar = ctk.CTkButton(self.sidebar_frame, text="💾 Exportar Datos", state="disabled", command=self.exportar_datos)
        self.btn_exportar.grid(row=3, column=0, padx=20, pady=10)
        
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text="QueryLibre v1.3.0", font=ctk.CTkFont(size=11), text_color="gray")
        self.version_label.grid(row=4, column=0, padx=20, pady=20, sticky="s") 
        
        # ---- 2. ÁREA DE TRABAJO PRINCIPAL ----
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.welcome_label = ctk.CTkLabel(self.main_frame, text="Bienvenido a QueryLibre\nCarga un dataset para comenzar.", font=ctk.CTkFont(size=16))
        self.welcome_label.pack(expand=True)

        # ---- 3. BARRA DE HERRAMIENTAS ----
        self.toolbar_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        self.btn_dup = ctk.CTkButton(self.toolbar_frame, text="Eliminar Duplicados", command=self.eliminar_duplicados, width=130, fg_color="#34495e")
        self.btn_dup.pack(side="left", padx=5)

        self.btn_nulos = ctk.CTkButton(self.toolbar_frame, text="Limpiar Nulos", command=self.limpiar_nulos, width=120, fg_color="#34495e")
        self.btn_nulos.pack(side="left", padx=5)

        self.btn_eliminar_col = ctk.CTkButton(self.toolbar_frame, text="🗑️ Eliminar Columna", command=self.eliminar_columna, width=140, fg_color="#c0392b", hover_color="#922b21")
        self.btn_eliminar_col.pack(side="left", padx=5)

        self.btn_renombrar_col = ctk.CTkButton(self.toolbar_frame, text="✏️ Renombrar Columna", command=self.renombrar_columna, width=150, fg_color="#2980b9", hover_color="#1f618d")
        self.btn_renombrar_col.pack(side="left", padx=5)

        self.btn_calcular = ctk.CTkButton(self.toolbar_frame, text="🧮 Calcular Columna", command=self.calcular_columna, width=150, fg_color="#8e44ad", hover_color="#732d91")
        self.btn_calcular.pack(side="left", padx=5)

        self.btn_combinar = ctk.CTkButton(self.toolbar_frame, text="🔗 Combinar Textos", command=self.combinar_columnas, width=150, fg_color="#d35400", hover_color="#a04000")
        self.btn_combinar.pack(side="left", padx=5)

        self.btn_dividir = ctk.CTkButton(self.toolbar_frame, text="✂️ Dividir Columna", command=self.dividir_columna, width=140, fg_color="#f39c12", hover_color="#d68910")
        self.btn_dividir.pack(side="left", padx=5)

        self.btn_filtrar = ctk.CTkButton(self.toolbar_frame, text="🚦 Filtrar Datos", command=self.filtrar_datos, width=130, fg_color="#16a085", hover_color="#117a65")
        self.btn_filtrar.pack(side="left", padx=5)
        
        # ---- 4. ÁREA DE DATOS E HISTORIAL ----
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        self.history_frame = ctk.CTkFrame(self.content_frame, width=220)
        self.history_frame.pack_propagate(False) 
        self.history_frame.pack(side="right", fill="y")
        
        self.history_label = ctk.CTkLabel(self.history_frame, text="📋 Pasos Aplicados", font=ctk.CTkFont(weight="bold"))
        self.history_label.pack(pady=(10, 5))
        
        self.history_text = ctk.CTkTextbox(self.history_frame, font=("Arial", 11), state="disabled", width=200)
        self.history_text.pack(expand=True, fill="both", padx=10, pady=5)

        self.btn_deshacer = ctk.CTkButton(self.history_frame, text="↩️ Deshacer Último", command=self.deshacer_paso, state="disabled", fg_color="#e74c3c", hover_color="#c0392b")
        self.btn_deshacer.pack(pady=(5, 15), padx=10, fill="x")

        self.tree_frame = ctk.CTkFrame(self.content_frame)
        self.tree_frame.pack(side="left", expand=True, fill="both", padx=(0, 10))
        
        self.lbl_dimensiones = ctk.CTkLabel(self.main_frame, text="Filas: 0 | Columnas: 0", text_color="gray", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_dimensiones.pack(side="bottom", anchor="e", padx=20, pady=5)

        self.pagination_frame = ctk.CTkFrame(self.tree_frame, fg_color="transparent")
        self.pagination_frame.pack(side="bottom", fill="x", pady=(5, 0))
        
        self.btn_prev_page = ctk.CTkButton(self.pagination_frame, text="◀ Anterior", width=80, command=self.pagina_anterior, state="disabled")
        self.btn_prev_page.pack(side="left", padx=10)

        self.lbl_pagina = ctk.CTkLabel(self.pagination_frame, text="Página 1 de 1", font=ctk.CTkFont(weight="bold"))
        self.lbl_pagina.pack(side="left", expand=True)

        self.btn_next_page = ctk.CTkButton(self.pagination_frame, text="Siguiente ▶", width=80, command=self.pagina_siguiente, state="disabled")
        self.btn_next_page.pack(side="right", padx=10)

        self.tree_scroll_y = ctk.CTkScrollbar(self.tree_frame)
        self.tree_scroll_y.pack(side="right", fill="y")
        
        self.tree_scroll_x = ctk.CTkScrollbar(self.tree_frame, orientation="horizontal")
        self.tree_scroll_x.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set, selectmode="extended")
        self.tree.pack(expand=True, fill="both")

        self.tree_scroll_y.configure(command=self.tree.yview)
        self.tree_scroll_x.configure(command=self.tree.xview)
        
        self.tree.bind("<Double-1>", self.editar_celda)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')]) 
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[('active', '#343638')])
        
        self.btn_acerca_de = ctk.CTkButton(self.sidebar_frame, text="ℹ️ Acerca de / Roadmap", command=self.mostrar_acerca_de, fg_color="transparent", text_color="gray", hover_color="#333333")
        self.btn_acerca_de.grid(row=10, column=0, pady=(50, 20), sticky="s")
        
        
    # ---- MÉTODOS DE LA INTERFAZ Y COMUNICACIÓN CON EL MOTOR ----

    def refrescar_interfaz(self):
        """
        Función maestra que sincroniza lo que el usuario ve (UI) 
        con lo que el MotorDatos tiene en su memoria.
        """
        self.actualizar_vista_previa()
        
        # Sincronizamos el historial de texto
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        for i, paso in enumerate(self.motor.historial_pasos, 1):
            self.history_text.insert("end", f"{i}. {paso}\n\n")
        self.history_text.configure(state="disabled")

        # Control del botón deshacer
        estado_deshacer = "normal" if len(self.motor.historial_pasos) > 1 else "disabled"
        self.btn_deshacer.configure(state=estado_deshacer)


    def cargar_archivo(self):
        file_path = filedialog.askopenfilename(title="Seleccionar Dataset", filetypes=[("Archivos de datos", "*.csv *.xlsx *.xls"), ("Todos los archivos", "*.*")])
        if file_path:
            try:
                # Delegamos el trabajo pesado al motor
                self.motor.cargar_archivo(file_path)
                
                # Reseteamos UI
                self.pagina_actual = 1
                self.welcome_label.pack_forget()
                self.toolbar_frame.pack(fill="x", padx=20, pady=(10, 0)) 
                self.content_frame.pack(expand=True, fill="both", padx=20, pady=20)
                self.btn_transformar.configure(state="normal")
                self.btn_exportar.configure(state="normal")
                
                self.refrescar_interfaz()
            except Exception as e:
                self.welcome_label.pack(expand=True)
                self.welcome_label.configure(text=f"❌ Error al cargar:\n{str(e)}", text_color="red")

    def actualizar_vista_previa(self):
        self.tree.delete(*self.tree.get_children())

        # Leemos el df directo desde la memoria del motor
        if self.motor.df is not None and not self.motor.df.empty:
            total_filas = len(self.motor.df)
            total_paginas = math.ceil(total_filas / self.filas_por_pagina)
            
            if self.pagina_actual > total_paginas:
                self.pagina_actual = max(1, total_paginas)

            inicio = (self.pagina_actual - 1) * self.filas_por_pagina
            fin = inicio + self.filas_por_pagina
            
            df_preview = self.motor.df.iloc[inicio:fin]

            columnas_visuales = ["#"] + list(df_preview.columns)
            self.tree["column"] = columnas_visuales
            self.tree["show"] = "headings" 

            self.tree.heading("#", text="#")
            self.tree.column("#", width=40, anchor="center", stretch=False)

            for col in df_preview.columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120, anchor="center")

            df_preview_filled = df_preview.fillna("") 
            
            for i, (index, row) in enumerate(df_preview_filled.iterrows(), start=inicio + 1):
                valores_fila = [i] + list(row)
                self.tree.insert("", "end", values=valores_fila)
                
            self.lbl_pagina.configure(text=f"Página {self.pagina_actual} de {total_paginas}")
            self.lbl_dimensiones.configure(text=f"Filas: {total_filas} | Columnas: {len(self.motor.df.columns)}")

            self.btn_prev_page.configure(state="normal" if self.pagina_actual > 1 else "disabled")
            self.btn_next_page.configure(state="normal" if self.pagina_actual < total_paginas else "disabled")
            
        elif self.motor.df is not None and self.motor.df.empty:
            self.lbl_pagina.configure(text="Página 0 de 0")
            self.lbl_dimensiones.configure(text=f"Filas: 0 | Columnas: {len(self.motor.df.columns)}")
            self.btn_prev_page.configure(state="disabled")
            self.btn_next_page.configure(state="disabled")

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_vista_previa()

    def pagina_siguiente(self):
        self.pagina_actual += 1
        self.actualizar_vista_previa()
    
    def deshacer_paso(self):
        if self.motor.deshacer():
            self.refrescar_interfaz()

    def eliminar_duplicados(self):
        if self.motor.df is not None:
            self.motor.eliminar_duplicados()
            self.refrescar_interfaz()

    def limpiar_nulos(self):
        if self.motor.df is None: return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Opciones de Limpieza")
        dialog.geometry("350x220")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="¿Qué filas deseas eliminar?", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(20, 10))

        def ejecutar(modo):
            self.motor.limpiar_nulos(modo)
            self.refrescar_interfaz()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Solo filas COMPLETAMENTE vacías", command=lambda: ejecutar('all'), fg_color="#2980b9").pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(dialog, text="Filas con ALGÚN dato faltante", command=lambda: ejecutar('any'), fg_color="#c0392b").pack(pady=10, padx=20, fill="x")

    def eliminar_columna(self):
        if self.motor.df is not None:
            dialog = ctk.CTkInputDialog(text="Escribe el nombre EXACTO de la columna a eliminar:", title="Eliminar Columna")
            col_name = dialog.get_input()
            if col_name:
                if self.motor.eliminar_columna(col_name):
                    self.refrescar_interfaz()
                else:
                    print(f"La columna '{col_name}' no existe.")

    def renombrar_columna(self):
        if self.motor.df is not None:
            old_name = ctk.CTkInputDialog(text="Nombre ACTUAL de la columna:", title="Renombrar Columna (Paso 1/2)").get_input()
            if old_name and old_name in self.motor.df.columns:
                new_name = ctk.CTkInputDialog(text=f"NUEVO nombre para '{old_name}':", title="Renombrar Columna (Paso 2/2)").get_input()
                if new_name:
                    self.motor.renombrar_columna(old_name, new_name)
                    self.refrescar_interfaz()
            elif old_name:
                print(f"La columna '{old_name}' no existe.")

    def editar_celda(self, event):
        if self.motor.df is None or self.motor.df.empty: return
            
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell": return 

        col_id = self.tree.identify_column(event.x) 
        row_id = self.tree.identify_row(event.y)    

        if not col_id or not row_id: return

        col_index_visual = int(col_id.replace('#', '')) - 1 
        if col_index_visual == 0: return 
            
        col_name = self.tree["column"][col_index_visual]
        valores_fila = self.tree.item(row_id, "values")
        indice_real = int(valores_fila[0]) - 1

        x, y, width, height = self.tree.bbox(row_id, col_id)
        valor_actual = self.tree.set(row_id, col_id)

        entry = ttk.Entry(self.tree, font=("Arial", 10))
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, valor_actual)
        entry.focus()
        entry.select_range(0, 'end')

        def guardar_edicion(e=None):
            nuevo_valor = entry.get()
            if nuevo_valor != str(valor_actual):
                self.motor.editar_celda(indice_real, col_name, nuevo_valor)
                self.refrescar_interfaz()
            entry.destroy()

        entry.bind("<Return>", guardar_edicion)   
        entry.bind("<FocusOut>", guardar_edicion) 
        entry.bind("<Escape>", lambda e: entry.destroy()) 

    def calcular_columna(self):
        if self.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nueva Columna Calculada")
        dialog.geometry("400x380")
        dialog.attributes("-topmost", True) 
        dialog.grab_set() 

        columnas_actuales = list(self.motor.df.columns)

        ctk.CTkLabel(dialog, text="Selecciona la Columna 1:").pack(pady=(10, 0))
        col1_combo = ctk.CTkComboBox(dialog, values=columnas_actuales)
        col1_combo.pack(pady=5)

        ctk.CTkLabel(dialog, text="Operación Matemática:").pack(pady=(5, 0))
        op_combo = ctk.CTkComboBox(dialog, values=["+", "-", "*", "/"])
        op_combo.pack(pady=5)

        ctk.CTkLabel(dialog, text="Selecciona la Columna 2:").pack(pady=(5, 0))
        col2_combo = ctk.CTkComboBox(dialog, values=columnas_actuales)
        col2_combo.pack(pady=5)

        ctk.CTkLabel(dialog, text="Nombre de la Nueva Columna:").pack(pady=(5, 0))
        new_col_entry = ctk.CTkEntry(dialog, placeholder_text="Ej: Total_Venta")
        new_col_entry.pack(pady=5)

        error_label = ctk.CTkLabel(dialog, text="", text_color="#e74c3c")
        error_label.pack(pady=(0, 5))

        def ejecutar():
            error_label.configure(text="") 
            c1, op, c2, new_col = col1_combo.get(), op_combo.get(), col2_combo.get(), new_col_entry.get()

            if not new_col:
                error_label.configure(text="⚠️ Ingresa un nombre para la columna.")
                return
            if new_col in self.motor.df.columns:
                error_label.configure(text=f"⚠️ La columna '{new_col}' ya existe.")
                return
            
            self.motor.calcular_columna(c1, op, c2, new_col)
            self.refrescar_interfaz()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Aplicar Cálculo", command=ejecutar, fg_color="#27ae60").pack(pady=20)
                    
    def combinar_columnas(self):
        if self.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Combinar Columnas")
        dialog.geometry("400x410")
        dialog.attributes("-topmost", True)
        dialog.grab_set()

        columnas_actuales = list(self.motor.df.columns)

        ctk.CTkLabel(dialog, text="Selecciona la Columna 1:").pack(pady=(10, 0))
        col1_combo = ctk.CTkComboBox(dialog, values=columnas_actuales)
        col1_combo.pack(pady=5)

        ctk.CTkLabel(dialog, text="Separador:").pack(pady=(5, 0))
        sep_combo = ctk.CTkComboBox(dialog, values=["Espacio", "Guion (-)", "Coma (,)", "Sin separador"])
        sep_combo.pack(pady=5)

        ctk.CTkLabel(dialog, text="Selecciona la Columna 2:").pack(pady=(5, 0))
        col2_combo = ctk.CTkComboBox(dialog, values=columnas_actuales)
        col2_combo.pack(pady=5)

        ctk.CTkLabel(dialog, text="Nombre de la Nueva Columna:").pack(pady=(5, 0))
        new_col_entry = ctk.CTkEntry(dialog, placeholder_text="Ej: Producto_Cliente")
        new_col_entry.pack(pady=5)

        error_label = ctk.CTkLabel(dialog, text="", text_color="#e74c3c")
        error_label.pack(pady=(0, 5))

        def ejecutar():
            error_label.configure(text="") 
            c1, sep_texto, c2, new_col = col1_combo.get(), sep_combo.get(), col2_combo.get(), new_col_entry.get()

            if not new_col:
                error_label.configure(text="⚠️ Ingresa un nombre para la columna.")
                return
            if new_col in self.motor.df.columns:
                error_label.configure(text=f"⚠️ La columna '{new_col}' ya existe.")
                return
            
            self.motor.combinar_columnas(c1, sep_texto, c2, new_col)
            self.refrescar_interfaz()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Aplicar Combinación", command=ejecutar, fg_color="#27ae60").pack(pady=20)
            
    def dividir_columna(self):
        if self.motor.df is None: return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Dividir Columna")
        dialog.geometry("350x300")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Columna a dividir:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        col_combo = ctk.CTkComboBox(dialog, values=list(self.motor.df.columns))
        col_combo.pack(pady=5)

        ctk.CTkLabel(dialog, text="Símbolo separador:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        sep_combo = ctk.CTkComboBox(dialog, values=["Espacio", "Coma (,)", "Guion (-)", "Barra (/)"])
        sep_combo.pack(pady=5)
        
        def ejecutar():
            self.motor.dividir_columna(col_combo.get(), sep_combo.get())
            self.refrescar_interfaz()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Aplicar División", command=ejecutar, fg_color="#f39c12").pack(pady=15)

    def filtrar_datos(self):
        if self.motor.df is None: return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Filtrar Datos")
        dialog.geometry("400x380")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="1. Selecciona la columna:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        col_combo = ctk.CTkComboBox(dialog, values=list(self.motor.df.columns))
        col_combo.pack(pady=5)

        ctk.CTkLabel(dialog, text="2. Condición:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 5))
        cond_combo = ctk.CTkComboBox(dialog, values=["Es Igual a", "Contiene el texto", "Es Mayor que (>)", "Es Menor que (<)", "Está Vacío (Nulo)"])
        cond_combo.pack(pady=5)

        ctk.CTkLabel(dialog, text="3. Valor buscado:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 5))
        valor_entry = ctk.CTkEntry(dialog, placeholder_text="Ej: Monitor")
        valor_entry.pack(pady=5)

        error_label = ctk.CTkLabel(dialog, text="", text_color="#e74c3c")
        error_label.pack(pady=5)

        def ejecutar():
            try:
                self.motor.filtrar_datos(col_combo.get(), cond_combo.get(), valor_entry.get())
                self.pagina_actual = 1 
                self.refrescar_interfaz()
                dialog.destroy()
            except ValueError:
                error_label.configure(text="⚠️ Usa 'Mayor/Menor' solo con números.")

        ctk.CTkButton(dialog, text="Aplicar Filtro", command=ejecutar, fg_color="#16a085").pack(pady=15)

    def unir_datasets(self):
        if self.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Unir Datasets (Merge / JOIN)")
        dialog.geometry("650x650") 
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="1. Cargar Segundo Dataset (Tabla Dimensional)", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        lbl_df2_info = ctk.CTkLabel(dialog, text="Ningún archivo cargado", text_color="gray")
        btn_cargar_df2 = ctk.CTkButton(dialog, text="📁 Buscar Archivo 2", fg_color="#8e44ad")
        btn_cargar_df2.pack(pady=5)
        lbl_df2_info.pack(pady=5)

        preview_frame = ctk.CTkFrame(dialog, height=120)
        preview_frame.pack(fill="x", padx=20, pady=5)
        
        tree_scroll_y2 = ctk.CTkScrollbar(preview_frame)
        tree_scroll_y2.pack(side="right", fill="y")
        tree_scroll_x2 = ctk.CTkScrollbar(preview_frame, orientation="horizontal")
        tree_scroll_x2.pack(side="bottom", fill="x")

        tree2 = ttk.Treeview(preview_frame, height=4, yscrollcommand=tree_scroll_y2.set, xscrollcommand=tree_scroll_x2.set, selectmode="none")
        tree2.pack(expand=True, fill="both")
        
        tree_scroll_y2.configure(command=tree2.yview)
        tree_scroll_x2.configure(command=tree2.xview)

        opciones_frame = ctk.CTkFrame(dialog, fg_color="transparent")

        def cargar_df2():
            file_path = filedialog.askopenfilename(title="Seleccionar Dataset 2", filetypes=[("Archivos", "*.csv *.xlsx *.xls")])
            if file_path:
                try:
                    self.motor.cargar_df2(file_path)
                    lbl_df2_info.configure(text=f"✅ Archivo listo: {os.path.basename(file_path)}", text_color="#27ae60")
                    
                    tree2.delete(*tree2.get_children()) 
                    df_preview = self.motor.df2.head(5).fillna("") 
                    
                    tree2["column"] = list(df_preview.columns)
                    tree2["show"] = "headings"
                    for col in tree2["column"]:
                        tree2.heading(col, text=col)
                        tree2.column(col, width=100, anchor="center")
                    for index, row in df_preview.iterrows():
                        tree2.insert("", "end", values=list(row))

                    col2_combo.configure(values=list(self.motor.df2.columns))
                    col2_combo.set(list(self.motor.df2.columns)[0]) 
                    opciones_frame.pack(fill="both", expand=True, padx=20, pady=10)
                except Exception as e:
                    lbl_df2_info.configure(text=f"❌ Error: {str(e)}", text_color="red")
        
        btn_cargar_df2.configure(command=cargar_df2)

        ctk.CTkLabel(opciones_frame, text="2. Configurar el Cruce (JOIN)", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 10))
        ctk.CTkLabel(opciones_frame, text="Llave en Dataset Principal:").pack(pady=(5, 0))
        col1_combo = ctk.CTkComboBox(opciones_frame, values=list(self.motor.df.columns))
        col1_combo.pack(pady=5)

        ctk.CTkLabel(opciones_frame, text="Llave en Dataset 2:").pack(pady=(5, 0))
        col2_combo = ctk.CTkComboBox(opciones_frame, values=["Esperando archivo..."])
        col2_combo.pack(pady=5)

        ctk.CTkLabel(opciones_frame, text="Tipo de Unión (JOIN):").pack(pady=(5, 0))
        tipo_combo = ctk.CTkComboBox(opciones_frame, values=["Izquierda (Left Join)", "Interna (Inner Join)"])
        tipo_combo.pack(pady=5)

        error_label = ctk.CTkLabel(opciones_frame, text="", text_color="#e74c3c")
        error_label.pack(pady=(10, 5))

        def aplicar_union():
            if self.motor.df2 is None: return
            try:
                self.motor.aplicar_union(col1_combo.get(), col2_combo.get(), tipo_combo.get())
                self.refrescar_interfaz()
                dialog.destroy()
            except Exception as e:
                error_label.configure(text="⚠️ Error en llaves.")
                self.motor.df_history.pop() 

        ctk.CTkButton(opciones_frame, text="Aplicar Unión", command=aplicar_union, fg_color="#27ae60").pack(pady=15)

    def exportar_datos(self):
        if self.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Exportar Datos")
        dialog.geometry("400x300")
        dialog.transient(self) 
        dialog.grab_set()      

        ctk.CTkLabel(dialog, text="💾 Seleccionar formato de exportación", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        formato_combo = ctk.CTkComboBox(dialog, values=["Archivo CSV (.csv)", "Archivo Excel (.xlsx)", "Base de Datos SQLite (.db)"])
        formato_combo.pack(pady=10)

        error_label = ctk.CTkLabel(dialog, text="", text_color="#e74c3c")
        error_label.pack(pady=5)

        def guardar():
            formato = formato_combo.get()
            ext = ".csv" if "CSV" in formato else ".xlsx" if "Excel" in formato else ".db"
            file_path = filedialog.asksaveasfilename(defaultextension=ext)
            if file_path:
                try:
                    self.motor.exportar_archivo(formato, file_path)
                    self.refrescar_interfaz()
                    dialog.destroy()
                except Exception as e:
                    error_label.configure(text=f"⚠️ Error al guardar.")
                    print(e)

        ctk.CTkButton(dialog, text="Guardar Como...", command=guardar, fg_color="#2980b9").pack(pady=15)
        
    def mostrar_acerca_de(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Acerca de QueryLibre")
        dialog.geometry("400x520") 
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="QueryLibre v1.2.0", font=ctk.CTkFont(weight="bold", size=20)).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="Motor de Transformación de Datos", text_color="gray").pack(pady=(0, 15))

        ctk.CTkLabel(dialog, text="📜 Licencias y Herramientas:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        legal_text = ("Licencia MIT.\nConstruido con:\n• Python\n• Pandas\n• CustomTkinter\n• SQLite")
        ctk.CTkLabel(dialog, text=legal_text, text_color="gray", justify="center").pack(pady=(0, 15))

        ctk.CTkLabel(dialog, text="🚀 Próximamente:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        for func in ["🔍 Buscar y Reemplazar", "🔠 Cambiar Tipo de Dato", "📦 Agrupar y Resumir"]:
            ctk.CTkLabel(dialog, text=func, anchor="w").pack(fill="x", padx=90, pady=2)

        ctk.CTkLabel(dialog, text="Desarrollado por Iván Tomás Ravarotto", font=ctk.CTkFont(size=11), text_color="gray").pack(side="bottom", pady=(0, 10))
        ctk.CTkButton(dialog, text="¡Entendido!", command=dialog.destroy, fg_color="#2980b9").pack(side="bottom", pady=15)

if __name__ == "__main__":
    app = QueryLibreApp()
    app.mainloop()