import os
import math
import tkinter as tk
from ui.modals import ModalesUI
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
import logging

from ui.chat_ia_handler import ChatIAHandler
from ui.macro_manager import MacroManager
from core.data_engine import MotorDatos

LOGGER = logging.getLogger("QueryLibre")

class PestanaTrabajo(ctk.CTkFrame):
    def __init__(self, master, app_root):
        super().__init__(master, fg_color="transparent")
        self.app_root = app_root
        
        
        # Le pasamos nuestra función oyente al motor
        self.motor = MotorDatos(on_change_callback=self._actualizar_titulo_pestana)
        self.chat_handler = ChatIAHandler(self, self.app_root)
        self.macro_manager = MacroManager(self.motor, self.app_root)
        self.pagina_actual = 1
        self.filas_por_pagina = 200

        # --- Panel Derecho: Tabview (Historial / IA) ---
        self.right_panel = ctk.CTkTabview(self, width=280)
        self.right_panel.pack(side="right", fill="y", padx=(10, 0), pady=0)
        self.right_panel.add("Historial")
        self.right_panel.add("✨ Analista IA")

        # ========== PESTAÑA HISTORIAL ==========
        self.history_text = ctk.CTkTextbox(self.right_panel.tab("Historial"), font=("Arial", 11), state="disabled", wrap="word")
        self.history_text.pack(expand=True, fill="both", padx=5, pady=5)

        self.btn_deshacer = ctk.CTkButton(
            self.right_panel.tab("Historial"), text="↩️ Deshacer",
            command=self.deshacer_paso, state="disabled",
            fg_color="#e74c3c", hover_color="#c0392b"
        )
        self.btn_deshacer.pack(pady=(5,5), padx=5, fill="x")

        self.btn_macro = ctk.CTkOptionMenu(
            self.right_panel.tab("Historial"),
            values=["💾 Guardar Macro actual", "▶️ Ejecutar Macro en Dataset"],
            command=self.dispatch_macro,
            fg_color="#27ae60", button_color="#2ecc71", dynamic_resizing=False
        )
        self.btn_macro.set("🤖 Macros")
        self.btn_macro.pack(pady=(2,10), padx=5, fill="x")

        # ========== PESTAÑA ANALISTA IA ==========
        tab_ia = self.right_panel.tab("✨ Analista IA")
        # El handler construye todo el chat (burbujas, entrada, botón)
        self.chat_handler.build_ui(tab_ia)

        # Agregar los botones adicionales (Informe y Configuración)
        # Usamos grid en la misma pestaña, respetando la estructura del handler.
        # El handler ya usó las filas 0,1,2 para chat_scroll, frame_acciones, input.
        # Nosotros usamos filas 3 y 4.
        tab_ia.grid_rowconfigure(3, weight=0)
        tab_ia.grid_rowconfigure(4, weight=0)
        
        self.btn_abrir_informe = ctk.CTkButton(
            tab_ia, text="📝 Redactar Informe Ejecutivo",
            fg_color="#2e4053", command=self.abrir_modulo_informe
        )
        self.btn_abrir_informe.grid(row=3, column=0, sticky="ew", padx=5, pady=(5,0))
        
        self.btn_config_ia = ctk.CTkButton(
            tab_ia, text="⚙️ Configurar API Key",
            fg_color="#34495e", command=lambda: ModalesUI.mostrar_config_ia(self.app_root)
        )
        self.btn_config_ia.grid(row=4, column=0, sticky="ew", padx=5, pady=(5,10))

        # ========== PANEL PRINCIPAL (TABLA) ==========
        self.tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tree_frame.pack(side="left", expand=True, fill="both", padx=(10,5), pady=10)

        # Variables del informe
        self.ventana_informe = None
        self.texto_informe_cache = (
            "# 📊 RESUMEN EJECUTIVO\n====================\n\n"
            "**Fecha:** \n**Dataset:** \n\n### 1. Hallazgos Principales:\n- \n\n"
            "### 2. Análisis de Calidad de Datos:\n- \n\n### 3. Conclusiones:\n- \n"
        )

        # --- Paginación ---
        self.pagination_frame = ctk.CTkFrame(self.tree_frame, fg_color="transparent")
        self.pagination_frame.pack(side="bottom", fill="x", pady=(10,15))

        self.btn_prev_page = ctk.CTkButton(self.pagination_frame, text="◀ Anterior", width=80, command=self.pagina_anterior, state="disabled")
        self.btn_prev_page.pack(side="left", padx=10)

        ctk.CTkLabel(self.pagination_frame, text="Página").pack(side="left", padx=(10,2))
        self.entry_pagina = ctk.CTkEntry(self.pagination_frame, width=50, justify="center", height=28)
        self.entry_pagina.pack(side="left", padx=2)
        self.entry_pagina.bind("<Return>", self._saltar_a_pagina)

        self.lbl_total_paginas = ctk.CTkLabel(self.pagination_frame, text="de ?")
        self.lbl_total_paginas.pack(side="left", padx=(2,10))

        self.btn_next_page = ctk.CTkButton(self.pagination_frame, text="Siguiente ▶", width=80, command=self.pagina_siguiente, state="disabled")
        self.btn_next_page.pack(side="right", padx=10)

        # Scrollbars
        self.tree_scroll_y = ctk.CTkScrollbar(self.tree_frame)
        self.tree_scroll_y.pack(side="right", fill="y")
        self.tree_scroll_x = ctk.CTkScrollbar(self.tree_frame, orientation="horizontal")
        self.tree_scroll_x.pack(side="bottom", fill="x")

        # --- Buscador de columnas ---
        self.frame_buscador_cols = ctk.CTkFrame(self.tree_frame, fg_color="transparent")
        self.frame_buscador_cols.pack(fill="x", padx=10, pady=(10,5))
        ctk.CTkLabel(self.frame_buscador_cols, text="🔍 Buscar Columna:").pack(side="left", padx=(0,5))
        self.entry_buscar_col = ctk.CTkEntry(self.frame_buscador_cols, width=200, placeholder_text="Ej: ID_Cliente...", height=28)
        self.entry_buscar_col.pack(side="left")
        self.entry_buscar_col.bind("<KeyRelease>", self._filtrar_columnas_visibles)

        # --- Treeview ---
        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set, selectmode="extended")
        self.tree.pack(expand=True, fill="both")
        self.tree.bind("<ButtonPress-1>", self._on_tree_press)
        self.tree.bind("<ButtonRelease-1>", self._on_tree_release)
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree_scroll_y.configure(command=self.tree.yview)
        self.tree_scroll_x.configure(command=self.tree.xview)

        # Menú contextual
        self.tree.bind("<Button-3>", self._mostrar_menu_contextual)
        self.menu_contextual = tk.Menu(self.tree_frame, tearoff=0, bg="#2b2b2b", fg="white", activebackground="#1f538d", font=("Arial",10))
        self.menu_contextual.add_command(label="✏️ Editar Celda", command=self._menu_editar_celda)
        self.menu_contextual.add_command(label="📋 Copiar Valor", command=self._menu_copiar_valor)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🏷️ Renombrar Columna", command=self._menu_renombrar_columna)
        self.menu_contextual.add_command(label="❌ Eliminar Columna", command=self._menu_eliminar_columna)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🗑️ Eliminar Fila", command=self._menu_eliminar_fila)

        self.columna_seleccionada_menu = None
        self.fila_seleccionada_menu = None

    # -------------------- Macros --------------------
    def dispatch_macro(self, eleccion):
        self.btn_macro.set("🤖 Macros")
        if "Guardar" in eleccion:
            self.after(150, lambda: self.macro_manager.guardar_macro(self.motor.macro_steps))
        elif "Ejecutar" in eleccion:
            self.after(150, self.macro_manager.ejecutar_macro)

    # -------------------- Actualización de UI --------------------
    def refrescar_interfaz(self):
        self.actualizar_vista_previa()
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        for i, paso in enumerate(self.motor.historial_pasos, 1):
            self.history_text.insert("end", f"{i}. {paso}\n\n")
        self.history_text.configure(state="disabled")
        self.btn_deshacer.configure(state="normal" if len(self.motor.historial_pasos) > 1 else "disabled")
        self.app_root.actualizar_lbl_dimensiones()
        nombre_base = getattr(self.motor, 'nombre_archivo', "Sin Título")
        nuevo_titulo = f"{nombre_base} *" if self.motor.hay_cambios else nombre_base
        self.app_root.actualizar_titulo_pestana(self, nuevo_titulo)

    def actualizar_vista_previa(self):
        self.tree.selection_remove(self.tree.selection())
        self.tree.delete(*self.tree.get_children())
        if self.motor.df is not None and not self.motor.df.empty:
            total_filas = len(self.motor.df)
            total_paginas = math.ceil(total_filas / self.filas_por_pagina)
            if self.pagina_actual > total_paginas:
                self.pagina_actual = max(1, total_paginas)
            inicio = (self.pagina_actual - 1) * self.filas_por_pagina
            fin = inicio + self.filas_por_pagina
            df_pagina = self.motor.df.iloc[inicio:fin].copy()
            for col in df_pagina.select_dtypes(['category']).columns:
                df_pagina[col] = df_pagina[col].astype('object')
            df_pagina = df_pagina.fillna("")
            columnas_visuales = ["#"] + list(df_pagina.columns)
            self.tree["column"] = columnas_visuales
            self.tree["show"] = "headings"
            self.tree.heading("#", text="#")
            self.tree.column("#", width=40, anchor="center", stretch=False)
            for col in df_pagina.columns:
                self.tree.heading(col, text=col, command=lambda c=col: self._ordenar_columna(c))
                self.tree.column(col, width=120, anchor="center")
            for i, (_, row) in enumerate(df_pagina.iterrows(), start=inicio + 1):
                self.tree.insert("", "end", values=[i] + list(row))
            self.entry_pagina.delete(0, 'end')
            self.entry_pagina.insert(0, str(self.pagina_actual))
            self.lbl_total_paginas.configure(text=f"de {total_paginas}")
            self.btn_prev_page.configure(state="normal" if self.pagina_actual > 1 else "disabled")
            self.btn_next_page.configure(state="normal" if self.pagina_actual < total_paginas else "disabled")
        else:
            # Si no hay datos, mostramos un mensaje en el treeview (opcional)
            self.tree["column"] = ["#"]
            self.tree["show"] = "headings"
            self.tree.heading("#", text="Sin datos")
            self.tree.insert("", "end", values=["Carga un dataset..."])
            self.btn_prev_page.configure(state="disabled")
            self.btn_next_page.configure(state="disabled")
            self.entry_pagina.delete(0, 'end')
            self.entry_pagina.insert(0, "1")
            self.lbl_total_paginas.configure(text="de 0")

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_vista_previa()

    def pagina_siguiente(self):
        self.pagina_actual += 1
        self.actualizar_vista_previa()

    def _saltar_a_pagina(self, event=None):
        if self.motor.df is None:
            return
        try:
            pag = int(self.entry_pagina.get())
            total = math.ceil(len(self.motor.df) / self.filas_por_pagina)
            if 1 <= pag <= total:
                self.pagina_actual = pag
                self.actualizar_vista_previa()
            else:
                messagebox.showwarning("Página Inválida", f"Ingresa un número entre 1 y {total}.")
                self.entry_pagina.delete(0, 'end')
                self.entry_pagina.insert(0, str(self.pagina_actual))
        except ValueError:
            pass

    # -------------------- Deshacer/Rehacer --------------------
    def deshacer_paso(self, event=None):
        if self.motor.deshacer():
            self.refrescar_interfaz()

    def rehacer_paso(self, event=None):
        if self.motor.rehacer():
            self.refrescar_interfaz()

    # -------------------- Edición y menú contextual --------------------
    def editar_celda(self, event):
        if self.motor.df is None:
            return
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        col_id = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)
        if not col_id or not row_id:
            return
        col_index = int(col_id.replace('#', '')) - 1
        if col_index == 0:
            return  # columna índice
        col_name = self.tree["column"][col_index]
        valores = self.tree.item(row_id, "values")
        indice_real = int(valores[0]) - 1
        x, y, w, h = self.tree.bbox(row_id, col_id)
        valor_actual = self.tree.set(row_id, col_id)
        entry = ttk.Entry(self.tree, font=("Arial",10))
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, valor_actual)
        entry.focus()
        entry.select_range(0, 'end')
        def guardar(e=None):
            nuevo = entry.get()
            if nuevo != str(valor_actual):
                self.motor.editar_celda(indice_real, col_name, nuevo)
                self.refrescar_interfaz()
            entry.destroy()
        entry.bind("<Return>", guardar)
        entry.bind("<FocusOut>", guardar)
        entry.bind("<Escape>", lambda e: entry.destroy())

    def _mostrar_menu_contextual(self, event):
        if self.motor.df is None:
            return
        region = self.tree.identify_region(event.x, event.y)
        if region not in ("cell", "heading", "tree"):
            return
        col_id = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)
        if col_id == '#1':
            return
        if not col_id:
            return
        col_index = int(col_id.replace('#', '')) - 1
        if col_index >= len(self.tree["column"]):
            return
        self.columna_seleccionada_menu = self.tree["column"][col_index]
        self.fila_seleccionada_menu = row_id
        if row_id:
            self.tree.selection_set(row_id)
            self.tree.focus(row_id)
        self.menu_contextual.tk_popup(event.x_root, event.y_root)

    def _menu_editar_celda(self):
        if not self.fila_seleccionada_menu or not self.columna_seleccionada_menu:
            return
        valores = self.tree.item(self.fila_seleccionada_menu, "values")
        indice_real = int(valores[0]) - 1
        idx_col = list(self.tree["columns"]).index(self.columna_seleccionada_menu)
        valor_actual = valores[idx_col + 1]
        dialog = ctk.CTkInputDialog(text=f"Nuevo valor para {self.columna_seleccionada_menu}:", title="✏️ Editar Celda")
        nuevo = dialog.get_input()
        if nuevo is not None and str(nuevo) != str(valor_actual):
            self.motor.editar_celda(indice_real, self.columna_seleccionada_menu, nuevo)
            self.refrescar_interfaz()

    def _menu_copiar_valor(self):
        if not self.fila_seleccionada_menu or not self.columna_seleccionada_menu:
            return
        valores = self.tree.item(self.fila_seleccionada_menu, "values")
        idx_col = list(self.tree["columns"]).index(self.columna_seleccionada_menu)
        valor = str(valores[idx_col + 1])
        self.app_root.clipboard_clear()
        self.app_root.clipboard_append(valor)
        messagebox.showinfo("Copiado", f"Valor copiado:\n{valor}")

    def _menu_renombrar_columna(self):
        if not self.columna_seleccionada_menu:
            return
        dialog = ctk.CTkInputDialog(text="Ingresa el nuevo nombre:", title="Renombrar Columna")
        nuevo = dialog.get_input()
        if nuevo and nuevo != self.columna_seleccionada_menu:
            self.motor.renombrar_columna(self.columna_seleccionada_menu, nuevo)
            self.refrescar_interfaz()

    def _menu_eliminar_columna(self):
        if not self.columna_seleccionada_menu:
            return
        if messagebox.askyesno("Eliminar Columna", f"¿Eliminar '{self.columna_seleccionada_menu}'?"):
            self.motor.eliminar_columna(self.columna_seleccionada_menu)
            self.refrescar_interfaz()

    def _menu_eliminar_fila(self):
        if not self.fila_seleccionada_menu:
            return
        valores = self.tree.item(self.fila_seleccionada_menu, "values")
        indice_real = int(valores[0]) - 1
        if messagebox.askyesno("Eliminar Fila", f"¿Eliminar fila {indice_real+1}?"):
            self.motor.df_history.append(self.motor.df.copy())
            self.motor.df = self.motor.df.drop(indice_real).reset_index(drop=True)
            self.motor.registrar_paso(f"🗑️ Fila {indice_real+1} eliminada")
            self.refrescar_interfaz()

    # -------------------- Ordenamiento y drag&drop --------------------
    def _ordenar_columna(self, col_name):
        if self.motor.df is None or col_name not in self.motor.df.columns:
            return
        ascendente = True
        if hasattr(self, '_ultima_columna_ordenada') and self._ultima_columna_ordenada == col_name:
            ascendente = not getattr(self, '_ultimo_orden_ascendente', True)
        try:
            self.app_root.configurar_estado_botones("disabled")
            self.motor.df = self.motor.df.sort_values(by=col_name, ascending=ascendente, na_position='last')
            self._ultima_columna_ordenada = col_name
            self._ultimo_orden_ascendente = ascendente
            self.pagina_actual = 1
            self.refrescar_interfaz()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo ordenar:\n{e}")
        finally:
            self.app_root.configurar_estado_botones("normal")

    def _on_tree_press(self, event):
        if self.tree.identify_region(event.x, event.y) == "heading":
            self._drag_col = self.tree.identify_column(event.x)
        else:
            self._drag_col = None

    def _on_tree_release(self, event):
        if getattr(self, '_drag_col', None) is None:
            return
        if self.tree.identify_region(event.x, event.y) == "heading":
            target = self.tree.identify_column(event.x)
            if target and target != self._drag_col:
                cols = list(self.tree["displaycolumns"])
                if not cols or cols[0] == "#all":
                    cols = list(self.tree["columns"])
                try:
                    src = cols.index(self._drag_col)
                    dst = cols.index(target)
                    cols.insert(dst, cols.pop(src))
                    self.tree["displaycolumns"] = cols
                except ValueError:
                    pass
            else:
                col_name = self.tree.heading(self._drag_col)["text"]
                self._ordenar_columna(col_name)
        self._drag_col = None

    def on_tree_double_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "separator":
            col_id = self.tree.identify_column(event.x)
            col_name = self.tree.heading(col_id)["text"]
            if self.motor.df is not None and col_name in self.motor.df.columns:
                muestra = self.motor.df[col_name].head(200).astype(str)
                max_len = muestra.map(len).max() if not muestra.empty else 0
                max_len = max(len(col_name), max_len)
                nuevo_ancho = min((max_len * 9) + 20, 500)
                self.tree.column(col_id, width=int(nuevo_ancho))
            return "break"
        elif region in ("cell", "tree"):
            self.editar_celda(event)

    # -------------------- Funciones auxiliares --------------------
    def _filtrar_columnas_visibles(self, event=None):
        if self.motor.df is None:
            return
        busqueda = self.entry_buscar_col.get().lower().strip()
        if not busqueda:
            self.tree["displaycolumns"] = "#all"
        else:
            todas = list(self.motor.df.columns)
            filtradas = [c for c in todas if busqueda in str(c).lower()]
            self.tree["displaycolumns"] = ["#"] + filtradas

    def abrir_modulo_informe(self):
        if self.ventana_informe and self.ventana_informe.winfo_exists():
            self.ventana_informe.lift()
            self.ventana_informe.focus()
            return
        self.ventana_informe = ctk.CTkToplevel(self)
        self.ventana_informe.title("📝 Editor de Informe Ejecutivo - QueryLibre")
        self.ventana_informe.geometry("650x500")
        self.ventana_informe.transient(self.app_root)
        if hasattr(self.app_root, 'fijar_icono'):
            self.app_root.fijar_icono(self.ventana_informe)
        frame_ctrls = ctk.CTkFrame(self.ventana_informe, fg_color="transparent")
        frame_ctrls.pack(fill="x", padx=15, pady=(15,0))
        ctk.CTkLabel(frame_ctrls, text="Redacta tus hallazgos (Soporta Markdown)", text_color="gray").pack(side="left")
        ctk.CTkButton(frame_ctrls, text="💾 Exportar", width=140, fg_color="#27ae60", command=self.exportar_informe).pack(side="right", padx=5)
        self.editor_informe = ctk.CTkTextbox(self.ventana_informe, wrap="word", font=ctk.CTkFont(family="Helvetica",size=14), fg_color="#1e1e1e", text_color="#e0e0e0")
        self.editor_informe.pack(fill="both", expand=True, padx=15, pady=15)
        contenido = getattr(self.motor, 'informe_ejecutivo', self.texto_informe_cache)
        self.editor_informe.insert("1.0", contenido)
        def al_cerrar():
            self.motor.informe_ejecutivo = self.editor_informe.get("1.0", "end-1c")
            self.ventana_informe.destroy()
        self.ventana_informe.protocol("WM_DELETE_WINDOW", al_cerrar)

    def exportar_informe(self):
        if not hasattr(self, 'editor_informe') or not self.editor_informe.winfo_exists():
            return
        texto = self.editor_informe.get("1.0", "end-1c").strip()
        if not texto:
            messagebox.showwarning("Informe Vacío", "No hay contenido para exportar.")
            return
        archivo = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown","*.md"),("Texto","*.txt")])
        if archivo:
            try:
                with open(archivo, "w", encoding="utf-8") as f:
                    f.write(texto)
                messagebox.showinfo("Éxito", "Informe exportado.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
                
    def _actualizar_titulo_pestana(self, hay_cambios):
        """Escucha al Motor de Datos y actualiza el título visualmente usando la función existente de la app."""
        if hasattr(self.app_root, 'actualizar_titulo_pestana'):
            nombre_base = getattr(self.motor, 'nombre_archivo', "Sin Título")
            nuevo_titulo = f"{nombre_base} *" if hay_cambios else nombre_base
            # Envolvemos en .after() por seguridad de hilos en Tkinter
            self.app_root.after(0, lambda: self.app_root.actualizar_titulo_pestana(self, nuevo_titulo))