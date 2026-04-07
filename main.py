# Librerías estándar
import os
import sys
import math
import json
import re
import ctypes
import logging
from logging.handlers import RotatingFileHandler
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk

# IMPORTAMOS NUESTRO CEREBRO
from core.data_engine import MotorDatos

# Logging global con rotación
LOGGER = logging.getLogger("QueryLibre")
if not LOGGER.handlers:
    LOGGER.setLevel(logging.INFO)
    handler = RotatingFileHandler("querylibre.log", maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    LOGGER.addHandler(handler)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def obtener_ruta(ruta_relativa):
    try:
        ruta_base = sys._MEIPASS
    except AttributeError:
        ruta_base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(ruta_base, ruta_relativa)


# =========================================================================
# CLASE PESTAÑA (WORKSPACE)
# =========================================================================
class PestañaTrabajo(ctk.CTkFrame):
    ALLOWED_MACRO_ACTIONS = {
        "eliminar_duplicados",
        "limpiar_nulos",
        "eliminar_columna",
        "renombrar_columna",
        "editar_celda",
        "calcular_columna",
        "combinar_columnas",
        "dividir_columna",
        "filtrar_datos",
        "cambiar_tipo_dato",
        "aplicar_union",
        "agrupar_datos",
        "buscar_reemplazar",
    }

    DISALLOWED_MACRO_PARAM_KEYS = {
        "__class__", "__dict__", "__bases__", "__globals__", "__code__",
        "__closure__", "__func__", "__self__", "__module__"
    }

    def __init__(self, master, app_root):
        super().__init__(master, fg_color="transparent")
        self.app_root = app_root 
        
        self.motor = MotorDatos()
        self.pagina_actual = 1
        self.filas_por_pagina = 200

        # --- Panel Derecho: Historial y Macros ---
        self.history_frame = ctk.CTkFrame(self, width=220)
        self.history_frame.pack_propagate(False)
        self.history_frame.pack(side="right", fill="y", padx=(10, 0))

        self.history_label = ctk.CTkLabel(self.history_frame, text="📋 Pasos Aplicados", font=ctk.CTkFont(weight="bold"))
        self.history_label.pack(pady=(10, 5))

        self.history_text = ctk.CTkTextbox(self.history_frame, font=("Arial", 11), state="disabled", width=200)
        self.history_text.pack(expand=True, fill="both", padx=10, pady=5)

        self.btn_deshacer = ctk.CTkButton(self.history_frame, text="↩️ Deshacer", command=self.deshacer_paso, state="disabled", fg_color="#e74c3c", hover_color="#c0392b")
        self.btn_deshacer.pack(pady=(5, 5), padx=10, fill="x")

        # --- BOTÓN DESPLEGABLE DE MACRO ---
        self.macro_frame = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.macro_frame.pack(side="bottom", fill="x", pady=(0, 10), padx=10)

        self.btn_macro = ctk.CTkOptionMenu(
            self.macro_frame, fg_color="#27ae60", button_color="#2ecc71", dynamic_resizing=False,
            values=["💾 Guardar Macro actual", "▶️ Ejecutar Macro en Dataset"], # Quitamos el título de las opciones
            command=self.dispatch_macro
        )
        self.btn_macro.set("🤖 Macros") # Título forzado
        self.btn_macro.pack(pady=2, fill="x")

        # --- Panel Izquierdo: Tabla de Datos ---
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(side="left", expand=True, fill="both")

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

    # --- Funciones Internas de la Pestaña ---
    def dispatch_macro(self, eleccion):
        self.btn_macro.set("🤖 Macros") 
        if "Guardar" in eleccion: self.guardar_macro()
        elif "Ejecutar" in eleccion: self.ejecutar_macro()

    def refrescar_interfaz(self):
        self.actualizar_vista_previa()
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        for i, paso in enumerate(self.motor.historial_pasos, 1):
            self.history_text.insert("end", f"{i}. {paso}\n\n")
        self.history_text.configure(state="disabled")
        self.btn_deshacer.configure(state="normal" if len(self.motor.historial_pasos) > 1 else "disabled")
        self.app_root.actualizar_lbl_dimensiones()

    def actualizar_vista_previa(self):
        self.tree.delete(*self.tree.get_children())
        if self.motor.df is not None and not self.motor.df.empty:
            total_filas = len(self.motor.df)
            total_paginas = math.ceil(total_filas / self.filas_por_pagina)
            if self.pagina_actual > total_paginas: self.pagina_actual = max(1, total_paginas)
            
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
                self.tree.insert("", "end", values=[i] + list(row))

            self.lbl_pagina.configure(text=f"Página {self.pagina_actual} de {total_paginas}")
            self.btn_prev_page.configure(state="normal" if self.pagina_actual > 1 else "disabled")
            self.btn_next_page.configure(state="normal" if self.pagina_actual < total_paginas else "disabled")
        else:
            self.lbl_pagina.configure(text="Página 0 de 0")
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

    def guardar_macro(self):
        if not self.motor.macro_steps: return 
        carpeta_docs = os.path.join(os.path.expanduser('~'), 'Documents')
        carpeta_macros = os.path.join(carpeta_docs, 'Macros_QueryLibre')
        if not os.path.exists(carpeta_macros):
            try: os.makedirs(carpeta_macros)
            except: carpeta_macros = os.path.expanduser('~') 
            
        file_path = filedialog.asksaveasfilename(
            initialdir=carpeta_macros, defaultextension=".json", 
            filetypes=[("QueryLibre Macro", "*.json")], title="Guardar Macro"
        )
        if file_path:
            import json
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.motor.macro_steps, f, indent=4)
                self.motor.registrar_paso(f"🤖 Macro Guardada: {os.path.basename(file_path)}")
                self.refrescar_interfaz()
            except Exception as e:
                LOGGER.error(f"Error al guardar macro: {e}")

    def _is_safe_value(self, value):
        """Valida que el valor sea de tipo seguro para evitar inyección."""
        if isinstance(value, (str, int, float, bool)):
            return True
        elif isinstance(value, list):
            return all(self._is_safe_value(item) for item in value)
        elif isinstance(value, dict):
            return all(isinstance(k, str) and self._is_safe_value(v) for k, v in value.items())
        return False

    def _apply_macro_steps(self, pasos):
        backup_df = self.motor.df.copy(deep=True)
        backup_history = list(self.motor.df_history)
        backup_steps = list(self.motor.macro_steps)
        backup_historial_pasos = list(self.motor.historial_pasos)

        try:
            for paso in pasos:
                nombre_funcion = paso.get("action")
                parametros = paso.get("params", {})

                if nombre_funcion not in self.ALLOWED_MACRO_ACTIONS:
                    LOGGER.error(f"Macro bloqueada por seguridad: acción no permitida {nombre_funcion}")
                    continue

                if not isinstance(parametros, dict):
                    LOGGER.error(f"Macro bloqueada por seguridad: params inválidos para acción {nombre_funcion}")
                    continue

                if any(
                    not isinstance(key, str) or key.startswith("__") or key in self.DISALLOWED_MACRO_PARAM_KEYS
                    for key in parametros.keys()
                ):
                    LOGGER.error(f"Macro bloqueada por seguridad: parámetros maliciosos en acción {nombre_funcion}")
                    continue

                if not all(self._is_safe_value(v) for v in parametros.values()):
                    LOGGER.error(f"Macro bloqueada por seguridad: valores de parámetros no seguros en acción {nombre_funcion}")
                    continue

                if hasattr(self.motor, nombre_funcion):
                    metodo = getattr(self.motor, nombre_funcion)
                    metodo(**parametros)
        except Exception:
            self.motor.df = backup_df
            self.motor.df_history = backup_history
            self.motor.macro_steps = backup_steps
            self.motor.historial_pasos = backup_historial_pasos
            raise

    def ejecutar_macro(self):
        if self.motor.df is None:
            return

        carpeta_docs = os.path.join(os.path.expanduser('~'), 'Documents')
        carpeta_macros = os.path.join(carpeta_docs, 'Macros_QueryLibre')
        if not os.path.exists(carpeta_macros):
            carpeta_macros = os.path.expanduser('~')

        file_path = filedialog.askopenfilename(
            initialdir=carpeta_macros, title="Seleccionar Macro",
            filetypes=[("QueryLibre Macro", "*.json")]
        )
        if file_path:
            import json
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    pasos = json.load(f)

                self._apply_macro_steps(pasos)
                self.refrescar_interfaz()
            except Exception as e:
                LOGGER.error(f"Error al ejecutar macro: {e}")
                messagebox.showerror("Error al ejecutar macro", f"Macro abortada y estado restaurado.\n\n{e}")
                self.refrescar_interfaz()


# =========================================================================
# APP PRINCIPAL (CONTENEDOR Y MENÚS DESPLEGABLES)
# =========================================================================
class QueryLibreApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.pestañas = {} 

        self.title("QueryLibre - Motor de Transformación de Datos")
        self.geometry("1100x650")
        self.minsize(900, 500)
        
        # --- PARCHE DE ÍCONOS GLOBALES ---
        try: 
            self.ruta_icono = obtener_ruta(os.path.join("assets", "main.ico"))
            self.iconbitmap(self.ruta_icono)
        except: pass
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---- 1. PANEL LATERAL ----
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="QueryLibre", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Logging setup global en LOGGER definido a nivel de módulo
        LOGGER.info("Iniciando QueryLibre")

        self.btn_cargar = ctk.CTkButton(self.sidebar_frame, text="📁 Cargar Archivo", command=self.cargar_archivo)
        self.btn_cargar.grid(row=1, column=0, padx=20, pady=10)

        self.btn_transformar = ctk.CTkButton(self.sidebar_frame, text="🔗 Unir Datasets", state="disabled", command=self.unir_datasets)
        self.btn_transformar.grid(row=2, column=0, padx=20, pady=10)

        self.btn_exportar = ctk.CTkButton(self.sidebar_frame, text="💾 Exportar Datos", state="disabled", command=self.exportar_datos)
        self.btn_exportar.grid(row=3, column=0, padx=20, pady=10)
        
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text="QueryLibre v1.5.0", font=ctk.CTkFont(size=11), text_color="gray")
        self.version_label.grid(row=4, column=0, padx=20, pady=20, sticky="s")

        # ---- 2. ÁREA DE TRABAJO PRINCIPAL ----
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.welcome_label = ctk.CTkLabel(self.main_frame, text="Bienvenido a QueryLibre\nCarga un dataset para comenzar.", font=ctk.CTkFont(size=16))
        self.welcome_label.pack(expand=True)

        # ---- 3. BARRA DE HERRAMIENTAS AGRUPADA (RIBBON) ----
        self.toolbar_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        self.menu_limpieza = ctk.CTkOptionMenu(
            self.toolbar_frame, width=150, fg_color="#34495e", button_color="#2c3e50", dynamic_resizing=False,
            values=["Eliminar Duplicados", "Limpiar Nulos", "Eliminar Columna"], # Sin título en las opciones
            command=self.dispatch_limpieza
        )
        self.menu_limpieza.set("🧹 Limpieza")
        self.menu_limpieza.pack(side="left", padx=5)

        self.menu_estructura = ctk.CTkOptionMenu(
            self.toolbar_frame, width=150, fg_color="#2980b9", button_color="#1f618d", dynamic_resizing=False,
            values=["Renombrar Columna", "Cambiar Tipo", "Dividir Columna", "Combinar Columnas"],
            command=self.dispatch_estructura
        )
        self.menu_estructura.set("🏗️ Estructura")
        self.menu_estructura.pack(side="left", padx=5)

        self.menu_analisis = ctk.CTkOptionMenu(
            self.toolbar_frame, width=150, fg_color="#8e44ad", button_color="#732d91", dynamic_resizing=False,
            values=["Calcular Columna", "Filtrar Datos", "Agrupar Datos", "Buscar/Reemplazar", "Radiografía de Datos"],
            command=self.dispatch_analisis
        )
        self.menu_analisis.set("🔬 Análisis")
        self.menu_analisis.pack(side="left", padx=5)

        # ---- 4. GESTOR DE PESTAÑAS ----
        self.tabview = ctk.CTkTabview(self.main_frame, command=self.actualizar_lbl_dimensiones)
        
        self.lbl_dimensiones = ctk.CTkLabel(self.main_frame, text="", text_color="gray", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_dimensiones.pack(side="bottom", anchor="e", padx=20, pady=5)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[('active', '#343638')])

        self.btn_acerca_de = ctk.CTkButton(self.sidebar_frame, text="ℹ️ Acerca de", command=self.mostrar_acerca_de, fg_color="transparent", text_color="gray")
        self.btn_acerca_de.grid(row=10, column=0, pady=(50, 20), sticky="s")

    # =========================================================================
    # ENRUTADORES DE MENÚS (Dispatchers)
    # =========================================================================
    def dispatch_limpieza(self, eleccion):
        self.menu_limpieza.set("🧹 Limpieza") # Resetea el texto visual
        if "Duplicados" in eleccion: self.eliminar_duplicados()
        elif "Nulos" in eleccion: self.limpiar_nulos()
        elif "Eliminar Columna" in eleccion: self.eliminar_columna()

    def dispatch_estructura(self, eleccion):
        self.menu_estructura.set("🏗️ Estructura")
        if "Renombrar" in eleccion: self.renombrar_columna()
        elif "Tipo" in eleccion: self.cambiar_tipo_dato()
        elif "Dividir" in eleccion: self.dividir_columna()
        elif "Combinar" in eleccion: self.combinar_columnas()

    def dispatch_analisis(self, eleccion):
        self.menu_analisis.set("🔬 Análisis")
        if eleccion == "🔬 Análisis": return
        
        if "Calcular" in eleccion: self.calcular_columna()
        elif "Filtrar" in eleccion: self.filtrar_datos()
        elif "Agrupar" in eleccion: self.agrupar_datos()
        elif "Buscar" in eleccion: self.buscar_reemplazar()
        elif "Radiografía" in eleccion: self.mostrar_radiografia()

    # =========================================================================
    # LÓGICA DE CONTROLADORES Y UTILS
    # =========================================================================
    def fijar_icono(self, ventana):
        """Inyecta el ícono a la fuerza en las ventanas secundarias (Toplevels)"""
        try: ventana.after(200, lambda: ventana.iconbitmap(self.ruta_icono))
        except: pass

    def obtener_pestaña_activa(self):
        if not self.pestañas: return None
        return self.pestañas.get(self.tabview.get())

    def actualizar_lbl_dimensiones(self):
        tab = self.obtener_pestaña_activa()
        if tab and tab.motor.df is not None:
            self.lbl_dimensiones.configure(text=f"Filas: {len(tab.motor.df)} | Columnas: {len(tab.motor.df.columns)}")
        else:
            self.lbl_dimensiones.configure(text="")

    def cargar_archivo(self):
        file_path = filedialog.askopenfilename(title="Seleccionar Dataset", filetypes=[("Archivos", "*.csv *.xlsx *.xls")])
        if file_path:
            try:
                nombre_archivo = os.path.basename(file_path)
                nombre_tab = nombre_archivo
                contador = 1
                while nombre_tab in self.pestañas:
                    nombre_tab = f"{nombre_archivo} ({contador})"
                    contador += 1

                if len(self.pestañas) == 0:
                    self.welcome_label.pack_forget()
                    self.toolbar_frame.pack(fill="x", padx=10, pady=(10, 0))
                    self.tabview.pack(expand=True, fill="both", padx=20, pady=10)
                    self.btn_transformar.configure(state="normal")
                    self.btn_exportar.configure(state="normal")

                self.tabview.add(nombre_tab)
                nueva_pestaña = PestañaTrabajo(self.tabview.tab(nombre_tab), self)
                nueva_pestaña.pack(expand=True, fill="both")
                
                self.pestañas[nombre_tab] = nueva_pestaña
                nueva_pestaña.motor.cargar_archivo(file_path)
                nueva_pestaña.refrescar_interfaz()
                self.tabview.set(nombre_tab)
                self.actualizar_lbl_dimensiones()

            except Exception as e:
                LOGGER.error(f"Error al cargar: {e}")

    # --- Funciones Delegadas (Modales) ---
    def eliminar_duplicados(self):
        tab = self.obtener_pestaña_activa()
        if tab and tab.motor.df is not None: tab.motor.eliminar_duplicados(); tab.refrescar_interfaz()

    def limpiar_nulos(self):
        tab = self.obtener_pestaña_activa()
        if not tab or tab.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Limpieza"); dialog.geometry("350x220"); dialog.transient(self); dialog.grab_set()
        self.fijar_icono(dialog)
        
        ctk.CTkLabel(dialog, text="¿Qué filas deseas eliminar?", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        def ejecutar(modo): tab.motor.limpiar_nulos(modo); tab.refrescar_interfaz(); dialog.destroy()
        ctk.CTkButton(dialog, text="Solo completamente vacías", command=lambda: ejecutar('all')).pack(pady=10)
        ctk.CTkButton(dialog, text="Con algún dato faltante", command=lambda: ejecutar('any'), fg_color="#c0392b").pack(pady=10)

    def eliminar_columna(self):
        tab = self.obtener_pestaña_activa()
        if not tab or tab.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Eliminar Columna"); dialog.geometry("350x200"); dialog.transient(self); dialog.grab_set()
        self.fijar_icono(dialog)

        ctk.CTkLabel(dialog, text="Selecciona la columna a eliminar:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        col_combo = ctk.CTkComboBox(dialog, values=list(tab.motor.df.columns))
        col_combo.pack(pady=10)

        def ejecutar():
            col = col_combo.get()
            if col and tab.motor.eliminar_columna(col): tab.refrescar_interfaz()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Eliminar", command=ejecutar, fg_color="#c0392b", hover_color="#922b21").pack(pady=15)

    def renombrar_columna(self):
        tab = self.obtener_pestaña_activa()
        if not tab or tab.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Renombrar Columna"); dialog.geometry("350x250"); dialog.transient(self); dialog.grab_set()
        self.fijar_icono(dialog)

        ctk.CTkLabel(dialog, text="Columna ACTUAL:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0))
        col_combo = ctk.CTkComboBox(dialog, values=list(tab.motor.df.columns))
        col_combo.pack(pady=5)

        ctk.CTkLabel(dialog, text="NUEVO nombre:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0))
        new_name_entry = ctk.CTkEntry(dialog, placeholder_text="Ej: Fecha_Venta")
        new_name_entry.pack(pady=5)

        err = ctk.CTkLabel(dialog, text="", text_color="red")
        err.pack(pady=2)

        def ejecutar():
            old = col_combo.get(); new = new_name_entry.get()
            if not new: return err.configure(text="Escribe un nombre válido.")
            if new in tab.motor.df.columns: return err.configure(text="Ese nombre ya existe.")
            if tab.motor.renombrar_columna(old, new): tab.refrescar_interfaz()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Aplicar Renombre", command=ejecutar, fg_color="#2980b9").pack(pady=10)
                    
    def cambiar_tipo_dato(self):
        tab = self.obtener_pestaña_activa()
        if not tab or tab.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Cambiar Tipo de Dato"); dialog.geometry("350x260"); dialog.grab_set()
        self.fijar_icono(dialog)
        
        columnas = list(tab.motor.df.columns)
        ctk.CTkLabel(dialog, text="Columna:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        col_combo = ctk.CTkComboBox(dialog, values=columnas); col_combo.pack(pady=5)
        if columnas:
            col_combo.set(columnas[0])

        ctk.CTkLabel(dialog, text="Convertir a:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 5))
        tipos = ["Texto", "Número Entero", "Número Decimal", "Fecha"]
        tipo_combo = ctk.CTkComboBox(dialog, values=tipos); tipo_combo.pack(pady=5)
        tipo_combo.set("Número Entero")

        err = ctk.CTkLabel(dialog, text="", text_color="#e74c3c"); err.pack(pady=5)

        info_invalid = ctk.CTkLabel(dialog, text="", text_color="#e67e22")
        info_invalid.pack(pady=(0, 5))

        table_frame = ctk.CTkFrame(dialog)
        table_frame.pack(fill="both", expand=False, padx=10, pady=(0, 10))
        table_frame.pack_forget()

        tree = ttk.Treeview(table_frame, columns=("fila","valor"), show="headings", height=8)
        tree.heading("fila", text="Fila")
        tree.heading("valor", text="Valor inválido")
        tree.column("fila", width=70, anchor="center")
        tree.column("valor", width=420, anchor="w")
        tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        copy_button = ctk.CTkButton(dialog, text="Copiar lista inválidos al portapapeles", fg_color="#16a085", hover_color="#1abc9c", width=260)
        copy_button.pack(pady=(0, 8))
        copy_button.pack_forget()

        def parse_invalid_values(message):
            match = re.search(r"Ejemplo \(fila, valor\): \[(.*)\]", message)
            if not match:
                return []
            data = match.group(1)
            items = re.findall(r"\((\d+), '((?:[^']|\\')*)'\)", data)
            # Retornar los 100 primeros para evitar UI pesada
            return items[:100]

        def show_invalid_table(items):
            for i in tree.get_children():
                tree.delete(i)
            if not items:
                table_frame.pack_forget()
                copy_button.pack_forget()
                info_invalid.configure(text="")
                return
            count = len(items)
            table_frame.pack(fill="both", expand=False, padx=10, pady=(0, 10))
            copy_button.pack(pady=(0, 8))
            info_invalid.configure(text=f"{count} filas mostradas (hasta 100): usa el botón para copiar al portapapeles")
            for fila, valor in items:
                tree.insert("", "end", values=(fila, valor))

            def copy_to_clipboard():
                text = "Fila\tValor inválido\n" + "\n".join(f"{fila}\t{valor}" for fila, valor in items)
                dialog.clipboard_clear()
                dialog.clipboard_append(text)
                info_invalid.configure(text="Copiado al portapapeles.")

            copy_button.configure(command=copy_to_clipboard)

        def ejecutar():
            try:
                tab.motor.cambiar_tipo_dato(col_combo.get(), tipo_combo.get())
                tab.refrescar_interfaz()
                dialog.destroy()
            except Exception as e:
                mensaje = f"Error al convertir los datos: {e}"
                err.configure(text=mensaje)
                print(f"Error Casting: {e}")
                items = parse_invalid_values(str(e))
                show_invalid_table(items)

        ctk.CTkButton(dialog, text="Aplicar Conversión", command=ejecutar, fg_color="#2980b9").pack(pady=15)

    def calcular_columna(self):
        tab = self.obtener_pestaña_activa()
        if not tab or tab.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Calcular"); dialog.geometry("400x380"); dialog.grab_set()
        self.fijar_icono(dialog)
        
        cols = list(tab.motor.df.columns)
        c1 = ctk.CTkComboBox(dialog, values=cols); c1.pack(pady=5)
        op = ctk.CTkComboBox(dialog, values=["+", "-", "*", "/"]); op.pack(pady=5)
        c2 = ctk.CTkComboBox(dialog, values=cols); c2.pack(pady=5)
        new_col = ctk.CTkEntry(dialog, placeholder_text="Nueva_Columna"); new_col.pack(pady=5)
        err = ctk.CTkLabel(dialog, text="", text_color="red"); err.pack()
        
        def ejecutar():
            if not new_col.get() or new_col.get() in tab.motor.df.columns: return err.configure(text="Nombre inválido.")
            tab.motor.calcular_columna(c1.get(), op.get(), c2.get(), new_col.get()); tab.refrescar_interfaz(); dialog.destroy()
        ctk.CTkButton(dialog, text="Aplicar", command=ejecutar).pack(pady=20)

    def combinar_columnas(self):
        tab = self.obtener_pestaña_activa()
        if not tab or tab.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Combinar"); dialog.geometry("400x410"); dialog.grab_set()
        self.fijar_icono(dialog)
        
        cols = list(tab.motor.df.columns)
        c1 = ctk.CTkComboBox(dialog, values=cols); c1.pack(pady=5)
        sep = ctk.CTkComboBox(dialog, values=["Espacio", "Guion (-)", "Coma (,)", "Sin separador"]); sep.pack(pady=5)
        c2 = ctk.CTkComboBox(dialog, values=cols); c2.pack(pady=5)
        new_col = ctk.CTkEntry(dialog, placeholder_text="Nueva_Columna"); new_col.pack(pady=5)
        err = ctk.CTkLabel(dialog, text="", text_color="red"); err.pack()
        
        def ejecutar():
            if not new_col.get() or new_col.get() in tab.motor.df.columns: return err.configure(text="Nombre inválido.")
            tab.motor.combinar_columnas(c1.get(), sep.get(), c2.get(), new_col.get()); tab.refrescar_interfaz(); dialog.destroy()
        ctk.CTkButton(dialog, text="Aplicar", command=ejecutar).pack(pady=20)

    def dividir_columna(self):
        tab = self.obtener_pestaña_activa()
        if not tab or tab.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Dividir"); dialog.geometry("350x300"); dialog.grab_set()
        self.fijar_icono(dialog)
        
        col = ctk.CTkComboBox(dialog, values=list(tab.motor.df.columns)); col.pack(pady=15)
        sep = ctk.CTkComboBox(dialog, values=["Espacio", "Coma (,)", "Guion (-)", "Barra (/)"]); sep.pack(pady=10)
        
        def ejecutar(): tab.motor.dividir_columna(col.get(), sep.get()); tab.refrescar_interfaz(); dialog.destroy()
        ctk.CTkButton(dialog, text="Aplicar", command=ejecutar).pack(pady=15)

    def filtrar_datos(self):
        tab = self.obtener_pestaña_activa()
        if not tab or tab.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Filtrar"); dialog.geometry("400x380"); dialog.grab_set()
        self.fijar_icono(dialog)
        
        col = ctk.CTkComboBox(dialog, values=list(tab.motor.df.columns)); col.pack(pady=10)
        cond = ctk.CTkComboBox(dialog, values=["Es Igual a", "Contiene el texto", "Es Mayor que (>)", "Es Menor que (<)", "Está Vacío (Nulo)"]); cond.pack(pady=10)
        val = ctk.CTkEntry(dialog); val.pack(pady=10)
        err = ctk.CTkLabel(dialog, text="", text_color="red"); err.pack()
        
        def ejecutar():
            try:
                tab.motor.filtrar_datos(col.get(), cond.get(), val.get()); tab.pagina_actual = 1
                tab.refrescar_interfaz(); dialog.destroy()
            except ValueError: err.configure(text="Usa números para Mayor/Menor.")
        ctk.CTkButton(dialog, text="Aplicar", command=ejecutar).pack(pady=15)

    def agrupar_datos(self):
        tab = self.obtener_pestaña_activa()
        if not tab or tab.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agrupar Datos"); dialog.geometry("400x350"); dialog.grab_set()
        self.fijar_icono(dialog)
        
        cols = list(tab.motor.df.columns)
        ctk.CTkLabel(dialog, text="Columna para agrupar:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        col_agrupar = ctk.CTkComboBox(dialog, values=cols); col_agrupar.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Columna para calcular:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        col_valor = ctk.CTkComboBox(dialog, values=cols); col_valor.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Función de agregación:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        funcion = ctk.CTkComboBox(dialog, values=["suma", "promedio", "conteo", "mínimo", "máximo"]); funcion.pack(pady=5)
        funcion.set("suma")
        
        err = ctk.CTkLabel(dialog, text="", text_color="red"); err.pack(pady=5)
        
        def ejecutar():
            try:
                tab.motor.agrupar_datos(col_agrupar.get(), col_valor.get(), funcion.get())
                tab.refrescar_interfaz(); dialog.destroy()
            except Exception as e:
                err.configure(text=f"Error: {str(e)}")
        
        ctk.CTkButton(dialog, text="Aplicar Agrupación", command=ejecutar, fg_color="#8e44ad").pack(pady=20)

    def buscar_reemplazar(self):
        tab = self.obtener_pestaña_activa()
        if not tab or tab.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Buscar y Reemplazar"); dialog.geometry("450x400"); dialog.grab_set()
        self.fijar_icono(dialog)
        
        cols = ["Todo el dataset"] + list(tab.motor.df.columns)
        ctk.CTkLabel(dialog, text="Buscar en:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        columna = ctk.CTkComboBox(dialog, values=cols); columna.pack(pady=5)
        columna.set("Todo el dataset")
        
        ctk.CTkLabel(dialog, text="Texto a buscar:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        buscar_entry = ctk.CTkEntry(dialog, placeholder_text="Texto a buscar"); buscar_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Reemplazar con:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        reemplazar_entry = ctk.CTkEntry(dialog, placeholder_text="Texto de reemplazo"); reemplazar_entry.pack(pady=5)
        
        regex_var = ctk.BooleanVar()
        regex_check = ctk.CTkCheckBox(dialog, text="Usar expresiones regulares", variable=regex_var)
        regex_check.pack(pady=10)
        
        err = ctk.CTkLabel(dialog, text="", text_color="red"); err.pack(pady=5)
        
        def ejecutar():
            try:
                col_param = None if columna.get() == "Todo el dataset" else columna.get()
                tab.motor.buscar_reemplazar(buscar_entry.get(), reemplazar_entry.get(), col_param, regex_var.get())
                tab.refrescar_interfaz(); dialog.destroy()
            except Exception as e:
                err.configure(text=f"Error: {str(e)}")
        
        ctk.CTkButton(dialog, text="Aplicar Reemplazo", command=ejecutar, fg_color="#8e44ad").pack(pady=20)

    def unir_datasets(self):
        tab = self.obtener_pestaña_activa()
        if not tab or tab.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Unir Datasets (Merge / JOIN)"); dialog.geometry("650x650"); dialog.transient(self); dialog.grab_set()
        self.fijar_icono(dialog)
        
        ctk.CTkLabel(dialog, text="1. Cargar Segundo Dataset", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        lbl_info = ctk.CTkLabel(dialog, text="Ningún archivo cargado", text_color="gray")
        btn_cargar = ctk.CTkButton(dialog, text="📁 Buscar Archivo 2", fg_color="#8e44ad")
        btn_cargar.pack(pady=5); lbl_info.pack(pady=5)
        
        preview_frame = ctk.CTkFrame(dialog, height=120)
        preview_frame.pack(fill="x", padx=20, pady=5)
        s_y = ctk.CTkScrollbar(preview_frame); s_y.pack(side="right", fill="y")
        s_x = ctk.CTkScrollbar(preview_frame, orientation="horizontal"); s_x.pack(side="bottom", fill="x")
        tree2 = ttk.Treeview(preview_frame, height=4, yscrollcommand=s_y.set, xscrollcommand=s_x.set, selectmode="none")
        tree2.pack(expand=True, fill="both")
        s_y.configure(command=tree2.yview); s_x.configure(command=tree2.xview)
        
        opc_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        
        def on_cargar():
            file_path = filedialog.askopenfilename(title="Seleccionar Dataset 2", filetypes=[("Archivos", "*.csv *.xlsx *.xls")])
            if file_path:
                try:
                    tab.motor.cargar_df2(file_path)
                    lbl_info.configure(text=f"✅ Listo: {os.path.basename(file_path)}", text_color="#27ae60")
                    tree2.delete(*tree2.get_children()) 
                    df_preview = tab.motor.df2.head(5).fillna("") 
                    tree2["column"] = list(df_preview.columns); tree2["show"] = "headings"
                    for c in tree2["column"]: tree2.heading(c, text=c); tree2.column(c, width=100, anchor="center")
                    for i, r in df_preview.iterrows(): tree2.insert("", "end", values=list(r))
                    c2_combo.configure(values=list(tab.motor.df2.columns)); c2_combo.set(list(tab.motor.df2.columns)[0]) 
                    opc_frame.pack(fill="both", expand=True, padx=20, pady=10)
                except Exception as e: lbl_info.configure(text=f"❌ Error: {str(e)}", text_color="red")
        
        btn_cargar.configure(command=on_cargar)
        
        ctk.CTkLabel(opc_frame, text="2. Configurar el Cruce", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 10))
        c1_combo = ctk.CTkComboBox(opc_frame, values=list(tab.motor.df.columns)); c1_combo.pack(pady=5)
        c2_combo = ctk.CTkComboBox(opc_frame, values=["Esperando..."]); c2_combo.pack(pady=5)
        t_combo = ctk.CTkComboBox(opc_frame, values=["Izquierda (Left Join)", "Interna (Inner Join)"]); t_combo.pack(pady=5)
        err = ctk.CTkLabel(opc_frame, text="", text_color="#e74c3c"); err.pack(pady=(10, 5))
        
        def aplicar():
            if tab.motor.df2 is None: return
            try:
                tab.motor.aplicar_union(c1_combo.get(), c2_combo.get(), t_combo.get())
                tab.refrescar_interfaz(); dialog.destroy()
            except: err.configure(text="⚠️ Error en llaves."); tab.motor.df_history.pop() 
        ctk.CTkButton(opc_frame, text="Aplicar Unión", command=aplicar, fg_color="#27ae60").pack(pady=15)

    def exportar_datos(self):
        tab = self.obtener_pestaña_activa()
        if not tab or tab.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Exportar"); dialog.geometry("400x300"); dialog.transient(self); dialog.grab_set() 
        self.fijar_icono(dialog)
             
        ctk.CTkLabel(dialog, text="💾 Formato de exportación", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        formato = ctk.CTkComboBox(dialog, values=["Archivo CSV (.csv)", "Archivo Excel (.xlsx)", "Base de Datos SQLite (.db)"])
        formato.pack(pady=10)
        err = ctk.CTkLabel(dialog, text="", text_color="#e74c3c"); err.pack(pady=5)
        
        def guardar():
            fmt = formato.get()
            ext = ".csv" if "CSV" in fmt else ".xlsx" if "Excel" in fmt else ".db"
            file_path = filedialog.asksaveasfilename(defaultextension=ext)
            if file_path:
                try: tab.motor.exportar_archivo(fmt, file_path); tab.refrescar_interfaz(); dialog.destroy()
                except Exception as e: err.configure(text=f"⚠️ Error al guardar."); print(e)
        ctk.CTkButton(dialog, text="Guardar Como...", command=guardar, fg_color="#2980b9").pack(pady=15)
        
    def mostrar_acerca_de(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Acerca de QueryLibre")
        dialog.geometry("400x480") 
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        self.fijar_icono(dialog)
        
        ctk.CTkLabel(dialog, text="QueryLibre v1.5.0", font=ctk.CTkFont(weight="bold", size=20)).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="Motor de Transformación de Datos", text_color="gray").pack(pady=(0, 15))
        ctk.CTkLabel(dialog, text="📜 Licencias y Herramientas:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        legal_text = ("Este software se distribuye bajo la Licencia MIT.\nConstruido con orgullo utilizando:\n• Python\n• Pandas\n• CustomTkinter\n• SQLite\n\nVersión 1.5.0")
        ctk.CTkLabel(dialog, text=legal_text, text_color="gray", justify="center").pack(pady=(0, 15))
        ctk.CTkLabel(dialog, text="Desarrollado por Iván Tomás Ravarotto", font=ctk.CTkFont(size=11), text_color="gray").pack(side="bottom", pady=(0, 10))
        ctk.CTkButton(dialog, text="¡Entendido!", command=dialog.destroy, fg_color="#2980b9", hover_color="#1f618d").pack(side="bottom", pady=15)
    
    def mostrar_radiografia(self):
        tab = self.obtener_pestaña_activa()
        if not tab or tab.motor.df is None: return
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Radiografía de Datos")
        dialog.geometry("380x450")
        dialog.grab_set() # <--- ¡Sin transient! Todo oscuro y perfecto
        self.fijar_icono(dialog)
        
        ctk.CTkLabel(dialog, text="Selecciona una columna a auditar:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        
        # El cuadro de texto donde aparecerá el reporte
        textbox = ctk.CTkTextbox(dialog, width=340, height=320, font=("Consolas", 13))
        
        # Esta función se dispara automáticamente cada vez que el usuario cambia la opción en el menú
        def actualizar_reporte(seleccion):
            reporte = tab.motor.obtener_radiografia(seleccion)
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            textbox.insert("end", reporte)
            textbox.configure(state="disabled")

        col_combo = ctk.CTkComboBox(dialog, values=list(tab.motor.df.columns), command=actualizar_reporte)
        col_combo.pack(pady=5)
        textbox.pack(pady=15, padx=20)
        
        # Forzamos a que cargue la info de la primera columna por defecto al abrir la ventana
        actualizar_reporte(col_combo.get())

if __name__ == "__main__":
    app = QueryLibreApp()
    app.mainloop()