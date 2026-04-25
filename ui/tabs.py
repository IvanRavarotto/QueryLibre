import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
import logging

from core.data_engine import MotorDatos

LOGGER = logging.getLogger("QueryLibre")

class PestanaTrabajo(ctk.CTkFrame):
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
        "aplicar_autocasteo_confirmado",
        "anular_dinamizacion",
        "agregar_columna_condicional" # <--- NUEVO
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

        # --- NUEVO: Salto de Página (v1.6.1) ---
        ctk.CTkLabel(self.pagination_frame, text="Página").pack(side="left", padx=(10, 2))
        
        self.entry_pagina = ctk.CTkEntry(self.pagination_frame, width=50, justify="center", height=28)
        self.entry_pagina.pack(side="left", padx=2)
        self.entry_pagina.bind("<Return>", self._saltar_a_pagina) 
        
        self.lbl_total_paginas = ctk.CTkLabel(self.pagination_frame, text="de ?")
        self.lbl_total_paginas.pack(side="left", padx=(2, 10))
        # ----------------------------------------

        self.btn_next_page = ctk.CTkButton(self.pagination_frame, text="Siguiente ▶", width=80, command=self.pagina_siguiente, state="disabled")
        self.btn_next_page.pack(side="right", padx=10)

        self.tree_scroll_y = ctk.CTkScrollbar(self.tree_frame)
        self.tree_scroll_y.pack(side="right", fill="y")
        self.tree_scroll_x = ctk.CTkScrollbar(self.tree_frame, orientation="horizontal")
        self.tree_scroll_x.pack(side="bottom", fill="x")

        # --- NUEVO: Buscador de Columnas (v1.6.2) ---
        self.frame_buscador_cols = ctk.CTkFrame(self.tree_frame, fg_color="transparent")
        self.frame_buscador_cols.pack(fill="x", padx=0, pady=(0, 5))
        
        ctk.CTkLabel(self.frame_buscador_cols, text="🔍 Buscar Columna:").pack(side="left", padx=(0,5))
        self.entry_buscar_col = ctk.CTkEntry(self.frame_buscador_cols, width=200, placeholder_text="Ej: ID_Cliente...", height=28)
        self.entry_buscar_col.pack(side="left")
        self.entry_buscar_col.bind("<KeyRelease>", self._filtrar_columnas_visibles)
        # --------------------------------------------

        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set, selectmode="extended")
        self.tree.pack(expand=True, fill="both")

        self.tree_scroll_y.configure(command=self.tree.yview)
        self.tree_scroll_x.configure(command=self.tree.xview)
        self.tree.bind("<Double-1>", self.editar_celda)

    # --- Funciones Internas de la Pestana ---
    def dispatch_macro(self, eleccion):
        self.btn_macro.set("🤖 Macros") 
        if "Guardar" in eleccion: self.guardar_macro()
        elif "Ejecutar" in eleccion: self.ejecutar_macro()

    def refrescar_interfaz(self):
        """Actualiza la tabla, el historial y los botones de la pestaña."""
        self.actualizar_vista_previa()
        
        # Actualizar cuadro de texto de historial
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        for i, paso in enumerate(self.motor.historial_pasos, 1):
            self.history_text.insert("end", f"{i}. {paso}\n\n")
        self.history_text.configure(state="disabled")
        
        # Habilitar deshacer si hay algo más que el origen
        self.btn_deshacer.configure(state="normal" if len(self.motor.historial_pasos) > 1 else "disabled")
        
        # Refrescar la barra de estado inferior
        self.app_root.actualizar_lbl_dimensiones()
        
        nombre_base = self.motor.nombre_archivo if hasattr(self.motor, 'nombre_archivo') else "Sin Título"
        if self.motor.hay_cambios:
            nuevo_titulo = f"{nombre_base} *"
        else:
            nuevo_titulo = nombre_base
            
        # Llamamos a un método de la app principal para renombrar el tab
        self.app_root.actualizar_titulo_pestana(self, nuevo_titulo)

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

            self.entry_pagina.delete(0, 'end')
            self.entry_pagina.insert(0, str(self.pagina_actual))
            self.lbl_total_paginas.configure(text=f"de {total_paginas}")

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

    def deshacer_paso(self, event=None):
        if self.motor.deshacer():
            self.refrescar_interfaz()

    def rehacer_paso(self, event=None):
        if self.motor.rehacer():
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

        errores_macro = [] # <-- Llevaremos un registro de los pasos que fallan

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
                    
                    # --- NUEVO: Bloque Try-Continue individual por paso ---
                    try:
                        metodo(**parametros)
                    except Exception as e:
                        LOGGER.warning(f"El paso '{nombre_funcion}' falló y fue omitido: {e}")
                        errores_macro.append(f"Paso '{nombre_funcion}' omitido: {e}")
                        continue # Salta este paso pero sigue ejecutando el resto de la macro

        except Exception as e:
            # Si ocurre un error catastrofico a nivel general, restauramos la memoria
            self.motor.df = backup_df
            self.motor.df_history = backup_history
            self.motor.macro_steps = backup_steps
            self.motor.historial_pasos = backup_historial_pasos
            raise e
            
        # Si la macro terminó pero hubo pasos omitidos, le avisamos al usuario amablemente
        if errores_macro:
            msg = "La macro se aplicó exitosamente, pero algunos pasos no eran compatibles con este archivo y fueron omitidos:\n\n• " + "\n• ".join(errores_macro[:5])
            if len(errores_macro) > 5:
                msg += f"\n... y {len(errores_macro) - 5} errores más."
            messagebox.showwarning("Macro finalizada con omisiones", msg)

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
                
    def _filtrar_columnas_visibles(self, event=None):
        """Oculta las columnas del Treeview que no coinciden con la búsqueda."""
        if self.motor.df is None: return
        busqueda = self.entry_buscar_col.get().lower()
        
        if busqueda.strip() == "":
            self.tree["displaycolumns"] = "#all" # Mostrar todas
        else:
            todas_las_cols = list(self.motor.df.columns)
            cols_filtradas = [col for col in todas_las_cols if busqueda in str(col).lower()]
            # --- CORRECCIÓN: Agregar la columna "#" estática al inicio de la lista ---
            self.tree["displaycolumns"] = ["#"] + cols_filtradas
    
    def _saltar_a_pagina(self, event=None):
        """Salta a la página ingresada por el usuario al presionar Enter."""
        if self.motor.df is None: return
        try:
            pag_deseada = int(self.entry_pagina.get())
            total_pags = math.ceil(len(self.motor.df) / self.filas_por_pagina)
            
            if 1 <= pag_deseada <= total_pags:
                self.pagina_actual = pag_deseada
                self.actualizar_vista_previa() # Llama a tu función que refresca el Treeview
            else:
                messagebox.showwarning("Página Inválida", f"Por favor, ingresa un número entre 1 y {total_pags}.")
                self.entry_pagina.delete(0, 'end')
                self.entry_pagina.insert(0, str(self.pagina_actual))
        except ValueError:
            pass # Si escribe letras, lo ignoramos