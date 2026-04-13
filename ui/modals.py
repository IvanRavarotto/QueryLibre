import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ModalesUI:
    """Clase estática para gestionar todas las ventanas emergentes de QueryLibre"""

    @staticmethod
    def mostrar_acerca_de(app_root):
        """Muestra la ventana de información del proyecto."""
        dialog = ctk.CTkToplevel(app_root)
        dialog.title("Acerca de QueryLibre")
        dialog.geometry("400x520") 
        dialog.resizable(False, False)
        dialog.transient(app_root)
        dialog.grab_set()
        
        # Intentamos usar el método del icono si existe en app_root
        if hasattr(app_root, 'fijar_icono'):
            app_root.fijar_icono(dialog)
        
        ctk.CTkLabel(dialog, text="QueryLibre v1.6.0", font=ctk.CTkFont(weight="bold", size=20)).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="Motor de Transformación de Datos", text_color="gray").pack(pady=(0, 15))
        
        ctk.CTkLabel(dialog, text="📜 Licencias y Herramientas:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 5))
        legal_text = ("Este software se distribuye bajo la Licencia MIT.\nConstruido con orgullo utilizando:\n• Python\n• Pandas\n• CustomTkinter\n• SQLite")
        ctk.CTkLabel(dialog, text=legal_text, text_color="gray", justify="center").pack(pady=(0, 10))
        
        ctk.CTkLabel(dialog, text="🚀 ROADMAP (Próximas funciones):", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 5))
        roadmap_text = ("• v1.6.0: Panel de Salud Global (RAM y Nulos).\n• v1.6.0: Pestañas Avanzadas (Indicador '*' de cambios).\n• v1.7.0: Conexión directa a BD SQL.")
        ctk.CTkLabel(dialog, text=roadmap_text, text_color="gray", justify="left").pack(pady=(0, 15))

        ctk.CTkButton(dialog, text="¡Entendido!", command=dialog.destroy, fg_color="#2980b9", hover_color="#1f618d").pack(side="bottom", pady=15)
        ctk.CTkLabel(dialog, text="Desarrollado por Iván Tomás Ravarotto", font=ctk.CTkFont(size=11), text_color="gray").pack(side="bottom", pady=(0, 5))

    @staticmethod
    def mostrar_radiografia(app_root, tab):
        """Muestra el diálogo con estadísticas de columna y gráficos interactivos."""
        if not tab or tab.motor.df is None: return

        dialog = ctk.CTkToplevel(app_root)
        dialog.title("Radiografía de Datos e Insights")
        # La hacemos mucho más ancha para que entre el gráfico
        dialog.geometry("900x550") 
        dialog.grab_set()
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)
        
        # --- LAYOUT DE DOS COLUMNAS ---
        dialog.grid_columnconfigure(0, weight=1) # Columna de texto
        dialog.grid_columnconfigure(1, weight=2) # Columna de gráfico (más ancha)
        dialog.grid_rowconfigure(1, weight=1)

        # --- SELECTOR SUPERIOR ---
        frame_top = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_top.grid(row=0, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        ctk.CTkLabel(frame_top, text="🔍 Analizar Columna:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
        col_combo = ctk.CTkComboBox(frame_top, values=list(tab.motor.df.columns), width=250)
        col_combo.pack(side="left")

        # --- PANEL IZQUIERDO (TEXTO) ---
        frame_texto = ctk.CTkFrame(dialog)
        frame_texto.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")
        
        lbl_resultado = ctk.CTkLabel(frame_texto, text="Selecciona una columna para ver su radiografía...", justify="left", font=ctk.CTkFont(family="Consolas", size=13))
        lbl_resultado.pack(padx=15, pady=15, anchor="nw")

        # --- PANEL DERECHO (GRÁFICO MATPLOTLIB) ---
        frame_grafico = ctk.CTkFrame(dialog)
        frame_grafico.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")

        def actualizar_vista(choice):
            # 1. Actualizar Texto (Usando el motor)
            reporte = tab.motor.obtener_radiografia(choice)
            lbl_resultado.configure(text=reporte)

            # 2. Limpiar el gráfico anterior
            for widget in frame_grafico.winfo_children():
                widget.destroy()

            # 3. Generar el nuevo Gráfico
            try:
                serie = tab.motor.df[choice].dropna()
                if serie.empty:
                    ctk.CTkLabel(frame_grafico, text="Columna vacía o con datos no graficables.").pack(expand=True)
                    return

                # Configuración de figura con estilo oscuro de CustomTkinter
                fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
                fig.patch.set_facecolor('#2b2b2b') # Fondo oscuro de la ventana
                ax.set_facecolor('#333333') # Fondo del gráfico
                ax.tick_params(colors='white')
                for spine in ax.spines.values():
                    spine.set_color('gray')

                # Inteligencia de Decisión de Gráfico
                if pd.api.types.is_numeric_dtype(serie) and not pd.api.types.is_bool_dtype(serie):
                    # Si es número, Histograma
                    ax.hist(serie, bins=20, color='#1f538d', edgecolor='white', alpha=0.8)
                    ax.set_title(f'Distribución de {choice}', color='white', pad=10)
                    ax.set_ylabel('Frecuencia', color='gray')
                else:
                    # Si es texto o categoría, Top 10 Gráfico de Barras
                    counts = serie.value_counts().head(10)
                    counts.plot(kind='bar', ax=ax, color='#1f538d', edgecolor='white', alpha=0.8)
                    ax.set_title(f'Top 10 Frecuencias en {choice}', color='white', pad=10)
                    plt.xticks(rotation=45, ha='right')

                fig.tight_layout()

                # Incrustar en Tkinter
                canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)

            except Exception as e:
                ctk.CTkLabel(frame_grafico, text=f"Error al generar gráfico:\n{e}").pack(expand=True)

        col_combo.configure(command=actualizar_vista)
        
        # Disparar la vista con la primera columna por defecto
        if len(tab.motor.df.columns) > 0:
            actualizar_vista(tab.motor.df.columns[0])
            
    @staticmethod
    def cambiar_tipo_dato(app_root, tab):
        """Muestra el diálogo inteligente para cambiar el tipo de dato."""
        if not tab or tab.motor.df is None: return

        dialog = ctk.CTkToplevel(app_root)
        dialog.title("Cambiar Tipo de Dato")
        dialog.geometry("400x300")
        dialog.grab_set()
        
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog) # ¡Ícono arreglado!

        ctk.CTkLabel(dialog, text="Columna:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 0))
        col_combo = ctk.CTkComboBox(dialog, values=list(tab.motor.df.columns), width=250)
        col_combo.pack(pady=5)

        ctk.CTkLabel(dialog, text="Nuevo Tipo:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0))
        tipo_combo = ctk.CTkComboBox(dialog, values=["Número Entero", "Número Decimal", "Texto", "Fecha"], width=250)
        tipo_combo.pack(pady=5)

        def ejecutar_simulacion():
            col = col_combo.get()
            nuevo_tipo = tipo_combo.get()
            
            # 1. Simular la conversión antes de tocar los datos
            errores = tab.motor.previsualizar_casteo(col, nuevo_tipo)
            
            if not errores:
                # Todo limpio, ejecutar normal
                app_root.ejecutar_tarea_pesada(tab.motor.cambiar_tipo_dato, col, nuevo_tipo)
                dialog.destroy()
            else:
                # 2. Hay errores: Mostrar la tabla de advertencia
                mostrar_vista_previa(col, nuevo_tipo, errores)

        btn_aplicar = ctk.CTkButton(dialog, text="Aplicar Cambio", command=ejecutar_simulacion, fg_color="#27ae60")
        btn_aplicar.pack(pady=20)

        def mostrar_vista_previa(col, nuevo_tipo, errores):
            # Limpiamos la ventana y la hacemos más grande
            for widget in dialog.winfo_children(): widget.destroy()
            dialog.geometry("500x550")
            dialog.title("⚠️ Advertencia de Conversión")

            ctk.CTkLabel(dialog, text="⚠️ Peligro de Pérdida de Datos", font=ctk.CTkFont(weight="bold", size=18), text_color="#e74c3c").pack(pady=(15,5))
            
            info_text = f"Se detectaron {len(errores)} (o más) valores que no son compatibles con '{nuevo_tipo}'.\nSi decides forzar la conversión, estos valores se borrarán (NaN)."
            ctk.CTkLabel(dialog, text=info_text, justify="center", wraplength=450).pack(pady=10)

            # --- Tabla de Vista Previa ---
            import tkinter.ttk as ttk
            frame_tabla = ctk.CTkFrame(dialog)
            frame_tabla.pack(fill="both", expand=True, padx=20, pady=5)
            
            s_y = ctk.CTkScrollbar(frame_tabla)
            s_y.pack(side="right", fill="y")
            
            tree_errores = ttk.Treeview(frame_tabla, columns=("Fila", "Valor Original Inválido"), show="headings", yscrollcommand=s_y.set)
            tree_errores.heading("Fila", text="Nº Fila")
            tree_errores.column("Fila", width=80, anchor="center")
            tree_errores.heading("Valor Original Inválido", text="Valor Original Inválido")
            tree_errores.column("Valor Original Inválido", width=300, anchor="center")
            tree_errores.pack(fill="both", expand=True)
            s_y.configure(command=tree_errores.yview)

            # Insertar los errores en la tabla
            for err in errores:
                tree_errores.insert("", "end", values=(err["fila"], err["valor"]))

            # --- Botones de Decisión ---
            frame_btns = ctk.CTkFrame(dialog, fg_color="transparent")
            frame_btns.pack(fill="x", pady=15, padx=20)
            
            ctk.CTkButton(frame_btns, text="Cancelar", command=dialog.destroy, fg_color="#7f8c8d", hover_color="#95a5a6").pack(side="left", expand=True, padx=5)
            
            def forzar_conversion():
                # Le pasamos forzar=True al motor
                app_root.ejecutar_tarea_pesada(tab.motor.cambiar_tipo_dato, col, nuevo_tipo, True)
                dialog.destroy()

            ctk.CTkButton(frame_btns, text="Forzar Conversión (Perder datos)", command=forzar_conversion, fg_color="#c0392b", hover_color="#922b21").pack(side="right", expand=True, padx=5)
        
    @staticmethod
    @staticmethod
    def limpiar_nulos(app_root, tab):
        dialog = ctk.CTkToplevel(app_root)
        dialog.title("Limpieza")
        dialog.geometry("350x220")
        
        # Estas dos líneas obligan a Windows a heredar las propiedades visuales
        dialog.transient(app_root) 
        dialog.grab_set()
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)

        ctk.CTkLabel(dialog, text="¿Qué filas deseas eliminar?", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        
        def ejecutar(modo):
            # Llamamos al hilo desde app_root
            app_root.ejecutar_tarea_pesada(tab.motor.limpiar_nulos, modo)
            dialog.destroy()

        ctk.CTkButton(dialog, text="Solo completamente vacías", command=lambda: ejecutar('all')).pack(pady=10)
        ctk.CTkButton(dialog, text="Con algún dato faltante", command=lambda: ejecutar('any'), fg_color="#c0392b").pack(pady=10)
        
    @staticmethod
    def eliminar_columna(app_root, tab):
        """Muestra el diálogo para eliminar una columna."""
        if not tab or tab.motor.df is None: return

        dialog = ctk.CTkToplevel(app_root)
        dialog.title("Eliminar Columna")
        dialog.geometry("350x180")
        dialog.grab_set()
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)

        ctk.CTkLabel(dialog, text="Selecciona la columna a eliminar:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        col_combo = ctk.CTkComboBox(dialog, values=list(tab.motor.df.columns), width=250)
        col_combo.pack(pady=5)

        def ejecutar():
            col = col_combo.get()
            if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar '{col}'?"):
                # IMPORTANTE: app_root DEBE ser la instancia de QueryLibreApp
                app_root.ejecutar_tarea_pesada(tab.motor.eliminar_columna, col)
                dialog.destroy()

        ctk.CTkButton(dialog, text="Eliminar", command=ejecutar, fg_color="#c0392b").pack(pady=20)

    @staticmethod
    def renombrar_columna(app_root, tab):
        """Muestra el diálogo para renombrar una columna."""
        if not tab or tab.motor.df is None: return

        dialog = ctk.CTkToplevel(app_root)
        dialog.title("Renombrar Columna")
        dialog.geometry("350x250")
        dialog.grab_set()
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)

        ctk.CTkLabel(dialog, text="Columna actual:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 0))
        col_combo = ctk.CTkComboBox(dialog, values=list(tab.motor.df.columns), width=250)
        col_combo.pack(pady=5)

        ctk.CTkLabel(dialog, text="Nuevo nombre:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0))
        entry_nuevo = ctk.CTkEntry(dialog, width=250, placeholder_text="Escribe el nuevo nombre...")
        entry_nuevo.pack(pady=5)

        def ejecutar():
            viejo = col_combo.get()
            nuevo = entry_nuevo.get().strip()
            if nuevo:
                app_root.ejecutar_tarea_pesada(tab.motor.renombrar_columna, viejo, nuevo)
                dialog.destroy()
            else:
                messagebox.showwarning("Atención", "El nuevo nombre no puede estar vacío.")

        ctk.CTkButton(dialog, text="Renombrar", command=ejecutar, fg_color="#27ae60").pack(pady=20)
        
    @staticmethod
    def mostrar_asistente_limpieza(app_root, tab):
        """Muestra las sugerencias inteligentes generadas por el motor."""
        if not tab or tab.motor.df is None: return

        sugerencias = tab.motor.generar_sugerencias_limpieza()
        
        if not sugerencias:
            messagebox.showinfo("Asistente Inteligente", "¡Tu dataset luce impecable! No encontré problemas obvios para sugerir.")
            return

        dialog = ctk.CTkToplevel(app_root)
        dialog.title("✨ Asistente de Limpieza Automática")
        dialog.geometry("500x450")
        dialog.grab_set()
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)

        ctk.CTkLabel(dialog, text="✨ Sugerencias Inteligentes", font=ctk.CTkFont(weight="bold", size=18)).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="He analizado tu dataset y encontré estas oportunidades de mejora:", text_color="gray").pack(pady=(0, 15))

        # Panel scrolleable para las sugerencias
        scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # Diccionario para guardar qué checkboxes marca el usuario
        variables_checkbox = {}

        for sug in sugerencias:
            card = ctk.CTkFrame(scroll_frame, fg_color="#343638", corner_radius=8)
            card.pack(fill="x", pady=5, ipady=5)
            
            var = ctk.BooleanVar(value=True) # Marcado por defecto
            variables_checkbox[sug["id"]] = (var, sug)
            
            chk = ctk.CTkCheckBox(card, text=sug["titulo"], variable=var, font=ctk.CTkFont(weight="bold"), text_color="#3498db")
            chk.pack(anchor="w", padx=10, pady=(10, 0))
            
            ctk.CTkLabel(card, text=sug["descripcion"], text_color="silver", justify="left", wraplength=380).pack(anchor="w", padx=35, pady=(0, 10))

        def aplicar_sugerencias():
            seleccionadas = [data for var, data in variables_checkbox.values() if var.get()]
            if not seleccionadas:
                dialog.destroy()
                return
            
            def tarea_limpieza():
                # Ejecutamos cada sugerencia aprobada
                for sug in seleccionadas:
                    sug["accion"](**sug["kwargs"])
            
            # Usamos el sistema de hilos de la app principal
            app_root.ejecutar_tarea_pesada(tarea_limpieza)
            dialog.destroy()

        ctk.CTkButton(dialog, text=f"Aplicar Seleccionadas", command=aplicar_sugerencias, fg_color="#27ae60", height=40).pack(pady=20, padx=20, fill="x")