import os
import sys
import shutil
import threading
import tempfile
import logging
from logging.handlers import RotatingFileHandler
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk

from ui.modals import ModalesUI
from ui.tabs import PestanaTrabajo

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

class QueryLibreApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.master_cache = os.path.join(tempfile.gettempdir(), "QueryLibre_Cache")
        if os.path.exists(self.master_cache):
            shutil.rmtree(self.master_cache, ignore_errors=True)
        
        self.pestanas = {} 

        self.title("QueryLibre - Motor de Transformación de Datos")
        self.geometry("1100x650")
        self.bind("<Control-w>", lambda e: self.cerrar_pestana_actual())
        self.minsize(900, 500)
    
        
        # Interceptar la X de la ventana para limpiar la basura
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
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

        # --- NUEVO: Botón de SQL en el panel lateral ---
        self.btn_sql_lateral = ctk.CTkButton(self.sidebar_frame, text="🔌 Importar BD SQL", command=self.iniciar_importacion_sql, fg_color="#1e3799", hover_color="#4a69bd")
        self.btn_sql_lateral.grid(row=2, column=0, padx=20, pady=(0, 10))

        # --- SE MUEVEN HACIA ABAJO (Ajuste de filas) ---
        self.btn_abrir_proj = ctk.CTkButton(self.sidebar_frame, text="📂 Abrir Proyecto", command=self.accion_abrir_proyecto)
        self.btn_abrir_proj.grid(row=3, column=0, padx=20, pady=(0, 5))

        self.btn_guardar_proj = ctk.CTkButton(self.sidebar_frame, text="📦 Guardar Proyecto", command=self.accion_guardar_proyecto)
        self.btn_guardar_proj.grid(row=4, column=0, padx=20, pady=5)

        self.btn_transformar = ctk.CTkButton(self.sidebar_frame, text="🔗 Unir Datasets", state="disabled", command=self.unir_datasets)
        self.btn_transformar.grid(row=5, column=0, padx=20, pady=10)

        self.btn_exportar = ctk.CTkButton(self.sidebar_frame, text="💾 Exportar Datos", state="disabled", command=self.exportar_datos)
        self.btn_exportar.grid(row=6, column=0, padx=20, pady=10)
        
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text="QueryLibre v1.7.0", font=ctk.CTkFont(size=11), text_color="gray")
        self.version_label.grid(row=7, column=0, padx=20, pady=20, sticky="s")

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
            values=["Renombrar Columna", "Cambiar Tipo", "Auto-Detectar Tipos", "Dividir Columna", "Combinar Columnas"],
            command=self.dispatch_estructura
        )
        self.menu_estructura.set("🏗️ Estructura")
        self.menu_estructura.pack(side="left", padx=5)

        self.menu_analisis = ctk.CTkOptionMenu(
            self.toolbar_frame, width=150, fg_color="#8e44ad", button_color="#732d91", dynamic_resizing=False,
            values=["Calcular Columna", "Filtrar Datos", "Agrupar Datos", "Buscar/Reemplazar", "Radiografía de Datos", "Gráfico de Correlación"],
            command=self.dispatch_analisis
        )
        self.menu_analisis.set("🔬 Análisis")
        self.menu_analisis.pack(side="left", padx=5)
        
        self.btn_sql = ctk.CTkButton(
            self.toolbar_frame, 
            text="🔌 Importar SQL", 
            command=self.abrir_conector_sql,
            width=140, 
            fg_color="#1e3799", 
            hover_color="#4a69bd"
        )
        self.btn_sql.pack(side="left", padx=5)
        
        # --- NUEVO BOTÓN ASISTENTE v1.6.0 ---
        self.btn_asistente = ctk.CTkButton(
            self.toolbar_frame, text="✨ Asistente IA", width=120,
            fg_color="#d35400", hover_color="#e67e22",
            command=lambda: ModalesUI.mostrar_asistente_limpieza(self, self.obtener_pestana_activa())
        )
        self.btn_asistente.pack(side="right", padx=10) # Lo ponemos a la derecha de todo
        
        # ---- 4. GESTOR DE PESTANAS ----
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
        
        # --- Atajos de Teclado Globales ---
        self.bind("<Control-s>", lambda event: self.accion_guardar_proyecto() if hasattr(self, 'accion_guardar_proyecto') else None)
        # Atajos en minúsculas y mayúsculas para asegurar captura
        self.bind("<Control-z>", lambda e: self._atajo_deshacer())
        self.bind("<Control-Z>", lambda e: self._atajo_deshacer())
        self.bind("<Control-y>", lambda e: self._atajo_rehacer())
        self.bind("<Control-Y>", lambda e: self._atajo_rehacer())

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
        elif "Cambiar Tipo" in eleccion: self.cambiar_tipo_dato() # <--- CORRECCIÓN: Ahora exige la frase completa
        elif "Auto-Detectar" in eleccion: self.auto_detectar_tipos() 
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
        elif "Gráfico de Correlación" in eleccion: self.abrir_grafico_correlacion()

    # =========================================================================
    # LÓGICA DE CONTROLADORES Y UTILS
    # =========================================================================
    def fijar_icono(self, ventana):
        """Inyecta el ícono a la fuerza en las ventanas secundarias (Toplevels)"""
        try: ventana.after(200, lambda: ventana.iconbitmap(self.ruta_icono))
        except: pass

    def obtener_pestana_activa(self):
        """Retorna el objeto PestanaTrabajo actual."""
        try:
            nombre_tab = self.tabview.get() # Esto devuelve el texto del Tab
            return self.pestanas.get(nombre_tab) # Buscamos el objeto en el diccionario
        except Exception:
            return None

    def actualizar_lbl_dimensiones(self):
        tab = self.obtener_pestana_activa()
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
                while nombre_tab in self.pestanas:
                    nombre_tab = f"{nombre_archivo} ({contador})"
                    contador += 1

                if len(self.pestanas) == 0:
                    self.welcome_label.pack_forget()
                    self.toolbar_frame.pack(fill="x", padx=10, pady=(10, 0))
                    self.tabview.pack(expand=True, fill="both", padx=20, pady=10)
                    self.btn_transformar.configure(state="normal")
                    self.btn_exportar.configure(state="normal")

                self.tabview.add(nombre_tab)
                nueva_pestana = PestanaTrabajo(self.tabview.tab(nombre_tab), self)
                nueva_pestana.pack(expand=True, fill="both")
                
                self.pestanas[nombre_tab] = nueva_pestana
                self.tabview.set(nombre_tab) # Enfocamos la pestaña primero
                
                # --- CORRECCIÓN: Enviar la carga pesada al hilo con barra de progreso ---
                self.ejecutar_tarea_pesada(nueva_pestana.motor.cargar_archivo, file_path)

            except Exception as e:
                LOGGER.error(f"Error al preparar carga: {e}")

    # --- Funciones Delegadas (Modales) ---
    def eliminar_duplicados(self):
        tab = self.obtener_pestana_activa()
        if tab and tab.motor.df is not None:
            # En lugar de llamarlo directo, usamos nuestro ejecutor de hilos
            self.ejecutar_tarea_pesada(tab.motor.eliminar_duplicados)

    def limpiar_nulos(self):
        """Llama al diálogo de limpieza desde el módulo UI."""
        tab = self.obtener_pestana_activa()
        if not tab or tab.motor.df is None:
            return
            
        # Llamamos al método estático que pegaste recién en modals.py
        # Le pasamos 'self' (que es la app principal) y 'tab' (donde están los datos)
        ModalesUI.limpiar_nulos(self, tab)

    def eliminar_columna(self):
        tab = self.obtener_pestana_activa()
        ModalesUI.eliminar_columna(self, tab)

    def renombrar_columna(self):
        tab = self.obtener_pestana_activa()
        ModalesUI.renombrar_columna(self, tab)
                    
    def cambiar_tipo_dato(self):
        tab = self.obtener_pestana_activa()
        # Llamamos a la "habitación nueva" (ui/modals.py)
        ModalesUI.cambiar_tipo_dato(self, tab)

    def calcular_columna(self):
        tab = self.obtener_pestana_activa()
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
        tab = self.obtener_pestana_activa()
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
        tab = self.obtener_pestana_activa()
        if not tab or tab.motor.df is None: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Dividir"); dialog.geometry("350x300"); dialog.grab_set()
        self.fijar_icono(dialog)
        
        col = ctk.CTkComboBox(dialog, values=list(tab.motor.df.columns)); col.pack(pady=15)
        sep = ctk.CTkComboBox(dialog, values=["Espacio", "Coma (,)", "Guion (-)", "Barra (/)"]); sep.pack(pady=10)
        
        def ejecutar(): tab.motor.dividir_columna(col.get(), sep.get()); tab.refrescar_interfaz(); dialog.destroy()
        ctk.CTkButton(dialog, text="Aplicar", command=ejecutar).pack(pady=15)

    def filtrar_datos(self):
        tab = self.obtener_pestana_activa()
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
        tab = self.obtener_pestana_activa()
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
        tab = self.obtener_pestana_activa()
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
        tab = self.obtener_pestana_activa()
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

    def abrir_grafico_correlacion(self):
        tab = self.obtener_pestana_activa()
        if tab:
            ModalesUI.mostrar_scatter(self, tab)

    def exportar_datos(self):
        tab = self.obtener_pestana_activa()
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
                try: 
                    # --- NUEVO: Exportación inteligente con Hilos ---
                    if "CSV" in fmt:
                        self.ejecutar_tarea_pesada(tab.motor.exportar_csv_seguro, file_path)
                    else:
                        self.ejecutar_tarea_pesada(tab.motor.exportar_archivo, fmt, file_path)
                    dialog.destroy()
                except Exception as e: 
                    err.configure(text=f"⚠️ Error al guardar.")
                    print(e)
        
    def mostrar_acerca_de(self):
        ModalesUI.mostrar_acerca_de(self)
    
    def mostrar_radiografia(self):
        tab = self.obtener_pestana_activa()
        ModalesUI.mostrar_radiografia(self, tab)
        
    def ejecutar_tarea_pesada(self, funcion, *args, **kwargs):
        """Ejecuta una tarea en un hilo separado mostrando un modal con barra de progreso."""
        pantalla_carga = ctk.CTkToplevel(self)
        pantalla_carga.title("Procesando...")
        pantalla_carga.geometry("300x150")
        pantalla_carga.resizable(False, False)
        pantalla_carga.transient(self)
        pantalla_carga.grab_set()
        
        if hasattr(self, 'fijar_icono'): self.fijar_icono(pantalla_carga)

        ctk.CTkLabel(pantalla_carga, text="Procesando Datos", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(25, 10))
        
        barra = ctk.CTkProgressBar(pantalla_carga, width=200, mode="indeterminate", fg_color="#34495e", progress_color="#3498db")
        barra.pack(pady=10)
        barra.start() 

        def tarea_hilo():
            error_msg = None
            try:
                funcion(*args, **kwargs)
            except Exception as e:
                error_msg = str(e)
                LOGGER.error(f"Error en tarea: {e}")

            # Esta sub-función se envía al hilo principal (GUI) para actualizar la pantalla sin trabarse
            def finalizar_ui():
                # 1. Destruimos la pantalla de carga INMEDIATAMENTE
                pantalla_carga.destroy() 
                
                # 2. Refrescamos la pestaña
                tab = self.obtener_pestana_activa()
                if tab: tab.refrescar_interfaz()
                
                # 3. Lanzamos los pop-ups de error o el Health Check al final
                if error_msg:
                    messagebox.showerror("Error", f"Ocurrió un error:\n{error_msg}")
                elif funcion.__name__ in ['cargar_archivo', 'cargar_proyecto'] and tab and tab.motor.df is not None:
                    # En lugar del mensaje básico, abrimos el Dashboard de BI
                    ModalesUI.mostrar_health_check(self, tab)

            # self.after(0) obliga a que finalizar_ui se ejecute en el hilo visual de Tkinter
            self.after(0, finalizar_ui)

        threading.Thread(target=tarea_hilo, daemon=True).start()

    def on_closing(self):
        """Maneja el evento de cierre de la ventana con opciones de guardado."""
        hay_cambios = any(tab.motor.hay_cambios for tab in self.pestanas.values())
        
        if hay_cambios:
            respuesta = messagebox.askyesnocancel(
                "Salir de QueryLibre", 
                "Tienes proyectos con cambios sin guardar.\n¿Deseas guardar antes de salir?"
            )
            
            if respuesta is None:  # Eligió Cancelar (o cerró la ventanita)
                return
            elif respuesta is True:  # Eligió Guardar
                # Asumimos que tienes una función global para guardar o guarda el actual
                if hasattr(self, 'accion_guardar_proyecto'):
                    self.accion_guardar_proyecto()
        
        # Limpieza global de la carpeta maestra de caché
        import shutil
        if os.path.exists(self.master_cache):
            try:
                shutil.rmtree(self.master_cache, ignore_errors=True)
            except Exception as e:
                LOGGER.error(f"Error al limpiar caché maestro al salir: {e}")
                
        self.destroy()
    
    def _finalizar_tarea_hilo(self, tab, error_msg):
        """Maneja el final del hilo en el proceso principal (Mainloop) de Tkinter."""
        # 1. Si hubo error, mostramos la ventana
        if error_msg:
            LOGGER.error(f"Error en tarea: {error_msg}")
            messagebox.showerror("Error", f"Ocurrió un problema:\n{error_msg}")
        
        # 2. Refrescar interfaz siempre (hace que no quede en blanco)
        try:
            tab.refrescar_interfaz()
        except Exception as e:
            LOGGER.error(f"Error al refrescar interfaz post-hilo: {e}")
        
        # 3. Limpiar estado visual de los botones y el "Procesando"
        self.configurar_estado_botones("normal")
        self.actualizar_lbl_dimensiones() # Esto sobreescribe el "Procesando..." con "Filas: X | Columnas: Y"
        self.lbl_dimensiones.configure(text_color="gray")

    def configurar_estado_botones(self, estado):
        """Habilita o deshabilita los botones principales durante el procesamiento."""
        self.btn_cargar.configure(state=estado)
        self.btn_transformar.configure(state=estado)
        self.btn_exportar.configure(state=estado)
        self.menu_limpieza.configure(state=estado)
        self.menu_estructura.configure(state=estado)
        self.menu_analisis.configure(state=estado)
    
    def cerrar_pestana_actual(self):
        """Cierra la pestaña activa validando si hay cambios sin guardar."""
        try:
            # Obtenemos el nombre de la pestaña que el usuario está mirando
            nombre_tab = self.tabview.get()
            tab = self.pestanas.get(nombre_tab)
        except Exception:
            return # Falla silenciosa si no hay tabview activo

        if not tab: return

        # VALIDACIÓN DE SEGURIDAD v1.5.4
        if getattr(tab.motor, 'hay_cambios', False):
            res = messagebox.askyesnocancel(
                "Cambios sin guardar", 
                f"La pestaña '{nombre_tab}' tiene cambios pendientes.\n\n¿Deseas exportar los datos antes de cerrar?"
            )
            
            if res is True: 
                # El usuario quiere guardar: disparamos la ventana de exportación
                self.exportar_datos()
                # Detenemos el cierre. Una vez que exporte exitosamente, 
                # el asterisco desaparecerá y podrá cerrar la pestaña con seguridad.
                return 
            elif res is None: 
                # El usuario apretó "Cancelar" o la 'X' del mensaje
                return 
        
        # Si llega acá (no hay cambios, o eligió 'No' guardar), borramos la pestaña
        self.tabview.delete(nombre_tab)
        tab.destroy()
        del self.pestanas[nombre_tab]
        
        # Limpieza de caché temporal delegada al motor
        tab.motor.limpiar_cache()

        # Si cerramos la última pestaña abierta, volvemos a la pantalla de bienvenida
        if not self.pestanas:
            self.welcome_label.pack(expand=True)
            self.tabview.pack_forget()
            # Ocultamos la barra de herramientas si existe
            if hasattr(self, 'toolbar_frame'):
                self.toolbar_frame.pack_forget()
                
            # APAGAMOS LOS BOTONES LATERALES
            self.btn_transformar.configure(state="disabled")
            self.btn_exportar.configure(state="disabled")
    
    def actualizar_titulo_pestana(self, objeto_pestana, nuevo_titulo):
        """Busca la pestaña por objeto y actualiza su texto visible."""
        for nombre_tab, obj in self.pestanas.items():
            if obj == objeto_pestana:
                # Intentamos renombrar en el Tabview
                try:
                    self.tabview._segmented_button._buttons_dict[nombre_tab].configure(text=nuevo_titulo)
                except Exception as e:
                    LOGGER.error(f"No se pudo actualizar el título visual: {e}")
                break
    
    def accion_guardar_proyecto(self):
        """Diálogo para guardar la sesión actual."""
        nombre_tab = self.tabview.get()
        tab = self.pestanas.get(nombre_tab)
        if not tab or getattr(tab.motor, 'df', None) is None: return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".qlp",
            filetypes=[("Proyecto QueryLibre", "*.qlp")],
            title="Guardar Proyecto"
        )
        if filepath:
            try:
                # Usamos el motor para empaquetar
                tab.motor.guardar_proyecto(filepath)
                # Refrescamos la interfaz para que desaparezca el asterisco (*)
                tab.refrescar_interfaz()
                messagebox.showinfo("Éxito", "Proyecto guardado correctamente.")
            except Exception as e:
                LOGGER.error(f"Error al guardar proyecto: {e}")
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def _crear_tab_ui(self, nombre_tab):
        """Crea la UI de una nueva pestaña y oculta la pantalla de bienvenida."""
        if len(self.pestanas) == 0:
            self.welcome_label.pack_forget()
            if hasattr(self, 'toolbar_frame'):
                self.toolbar_frame.pack(fill="x", padx=10, pady=(10, 0))
            self.tabview.pack(expand=True, fill="both", padx=20, pady=10)
            
            # Encender botones
            self.btn_transformar.configure(state="normal")
            self.btn_exportar.configure(state="normal")

        self.tabview.add(nombre_tab)
        nueva_pestana = PestanaTrabajo(self.tabview.tab(nombre_tab), self)
        nueva_pestana.pack(expand=True, fill="both")
        
        self.pestanas[nombre_tab] = nueva_pestana
        return nueva_pestana
    
    def abrir_conector_sql(self):
        """Llama al modal de conexión SQL para la pestaña activa."""
        tab = self.obtener_pestana_activa()
        if tab:
            ModalesUI.mostrar_conector_sql(self, tab)
            
    def iniciar_importacion_sql(self):
        """Crea una pestaña desde cero y abre directamente el conector SQL."""
        nombre_base = "Conexión SQL"
        nombre_tab = nombre_base
        contador = 1
        while nombre_tab in self.pestanas:
            nombre_tab = f"{nombre_base} ({contador})"
            contador += 1

        # Creamos la pestaña visualmente usando nuestra función DRY
        nueva_pestana = self._crear_tab_ui(nombre_tab)
        self.tabview.set(nombre_tab)
        
        # Invocamos el modal amarrándolo a esta pestaña nueva
        ModalesUI.mostrar_conector_sql(self, nueva_pestana)
    
    def accion_abrir_proyecto(self):
        """Diálogo para restaurar una sesión previa."""
        filepath = filedialog.askopenfilename(
            filetypes=[("Proyecto QueryLibre", "*.qlp")],
            title="Abrir Proyecto"
        )
        if filepath:
            nombre_archivo = os.path.basename(filepath)
            nombre_tab = nombre_archivo
            contador = 1
            while nombre_tab in self.pestanas:
                nombre_tab = f"{nombre_archivo} ({contador})"
                contador += 1

            # Usamos el nuevo método limpio (DRY)
            nueva_pestana = self._crear_tab_ui(nombre_tab)
            
            try:
                self.ejecutar_tarea_pesada(nueva_pestana.motor.cargar_proyecto, filepath)
                nueva_pestana.refrescar_interfaz()
                self.tabview.set(nombre_tab)
                if hasattr(self, 'actualizar_lbl_dimensiones'):
                    self.actualizar_lbl_dimensiones()
            except Exception as e:
                LOGGER.error(f"Error al abrir proyecto: {e}")
                self.cerrar_pestana_actual() # Se auto-limpia si falla
                messagebox.showerror("Error", f"Archivo corrupto o inválido:\n{e}")
    
    def _atajo_deshacer(self):
        tab = self.obtener_pestana_activa()
        if tab and hasattr(tab, 'deshacer_paso'): tab.deshacer_paso()

    def _atajo_rehacer(self):
        tab = self.obtener_pestana_activa()
        # Nota: Asegúrate de tener una función 'rehacer_paso' en PestanaTrabajo si la implementaste
        if tab and hasattr(tab, 'rehacer_paso'): tab.rehacer_paso()
    
    def auto_detectar_tipos(self):
        tab = self.obtener_pestana_activa()
        if not tab or tab.motor.df is None: return
        
        # Diccionario para guardar el resultado del hilo
        resultado = {"propuestas": {}}
        
        def tarea_deteccion():
            # Solo escanea, no modifica RAM pesada
            resultado["propuestas"] = tab.motor.detectar_autocasteo()
            
            def mostrar_decision():
                if resultado["propuestas"]:
                    # Si hay propuestas, abrimos el modal para preguntar
                    ModalesUI.mostrar_preview_autocasteo(self, tab, resultado["propuestas"])
                else:
                    messagebox.showinfo("Auto-Casteo", "No se detectaron columnas que requieran o puedan ser convertidas de forma 100% segura.")
            
            self.after(0, mostrar_decision)
            
        self.ejecutar_tarea_pesada(tarea_deteccion)
    
if __name__ == "__main__":
    app = QueryLibreApp()
    app.mainloop()