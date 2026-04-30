import customtkinter as ctk
from tkinter import messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


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
        
        ctk.CTkLabel(dialog, text="QueryLibre v1.8.0", font=ctk.CTkFont(weight="bold", size=20)).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="Motor de Transformación de Datos", text_color="gray").pack(pady=(0, 15))
        
        ctk.CTkLabel(dialog, text="📜 Licencias y Herramientas:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 5))
        legal_text = ("Este software se distribuye bajo la Licencia MIT.\nConstruido con orgullo utilizando:\n• Python\n• Pandas\n• CustomTkinter\n• SQLite")
        ctk.CTkLabel(dialog, text=legal_text, text_color="gray", justify="center").pack(pady=(0, 10))
        
        # Título de la sección
        ctk.CTkLabel(dialog, text="🚀 ROADMAP (Próxima Versión 2.0.0):", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))

        # Texto del Roadmap estructurado por fases
        roadmap_text = (
            "• Interfaz del Analista IA (Panel lateral y Configuración).\n"
            "• Motor de Metadatos (Resumen del contexto para la IA).\n"
            "• Integración de API (Conexión con Gemini/OpenAI).\n"
            "• Perfiles SQL (Historial de conexiones guardadas).\n"
            "• Refactorización estructural y Deuda Técnica."
        )

        ctk.CTkLabel(dialog, text=roadmap_text, text_color="gray", justify="left").pack(pady=(0, 20))

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

        figura_actual = plt.gcf()
        
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
            
        def al_cerrar_radiografia():
            # Cerramos SOLO la figura de esta ventana para no borrar otros gráficos
            plt.close(figura_actual)
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", al_cerrar_radiografia)
            
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
    
    @staticmethod
    def mostrar_health_check(app_root, tab):
        """Muestra el dashboard inicial de salud del dataset."""
        if not tab or tab.motor.df is None: return

        reporte = tab.motor.generar_reporte_salud()
        if not reporte: return

        dialog = ctk.CTkToplevel(app_root)
        
        # CORRECCIÓN 1: Quitamos el emoji del título para evitar el "doble icono" en Windows
        dialog.title("Health Check del Dataset")
        dialog.geometry("450x350")
        dialog.transient(app_root)
        dialog.grab_set()
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)

        # CORRECCIÓN 2: Función y botón flotante de Ayuda (?)
        def mostrar_ayuda():
            texto_ayuda = (
                "📌 Diccionario de Métricas:\n\n"
                "• Datos Completos: Porcentaje de celdas con información real. "
                "Si está en rojo (menor a 80%), tu dataset tiene demasiados nulos y necesita limpieza.\n\n"
                "• Peso en RAM: Memoria física que ocupa el dataset en tu computadora. Útil para "
                "prevenir cuelgues si te acercas a tu límite.\n\n"
                "• Dimensiones: Cantidad total de filas (registros) y columnas (variables).\n\n"
                "• Tipos Detectados: Diferencia entre columnas numéricas (para cálculos estadísticos) y "
                "columnas de texto (para agrupaciones o categorías)."
            )
            messagebox.showinfo("¿Qué significan estos datos?", texto_ayuda)

        # Ubicamos el botón de forma absoluta (place) arriba a la derecha
        btn_ayuda = ctk.CTkButton(dialog, text="❓", width=30, height=30, 
                                  fg_color="transparent", hover_color="#34495e", text_color="#3498db",
                                  font=ctk.CTkFont(size=16), command=mostrar_ayuda)
        btn_ayuda.place(x=400, y=10)

        ctk.CTkLabel(dialog, text="📊 Resumen de Salud del Dataset", font=ctk.CTkFont(weight="bold", size=18)).pack(pady=(20, 10))
        
        # Crear un frame tipo "Grid" para las tarjetas
        frame_cards = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_cards.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Fila 1: Salud y Memoria
        salud_float = float(reporte["Salud"].replace('%', ''))
        color_salud = "#27ae60" if salud_float >= 80.0 else "#c0392b"
        
        card_salud = ctk.CTkFrame(frame_cards, fg_color=color_salud, corner_radius=10)
        card_salud.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card_salud, text="Datos Completos", font=ctk.CTkFont(size=12)).pack(pady=(10,0))
        ctk.CTkLabel(card_salud, text=reporte["Salud"], font=ctk.CTkFont(weight="bold", size=24)).pack(pady=(0,10))
        
        card_memoria = ctk.CTkFrame(frame_cards, fg_color="#2c3e50", corner_radius=10)
        card_memoria.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card_memoria, text="Peso en RAM", font=ctk.CTkFont(size=12)).pack(pady=(10,0))
        ctk.CTkLabel(card_memoria, text=reporte["Memoria"], font=ctk.CTkFont(weight="bold", size=24)).pack(pady=(0,10))

        # Fila 2: Dimensiones
        card_dim = ctk.CTkFrame(frame_cards, fg_color="#34495e", corner_radius=10)
        card_dim.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        texto_dim = f"Dimensiones: {reporte['Filas']} filas × {reporte['Columnas']} columnas"
        ctk.CTkLabel(card_dim, text=texto_dim, font=ctk.CTkFont(weight="bold", size=14)).pack(pady=12)

        # Fila 3: Tipos de datos
        card_tipos = ctk.CTkFrame(frame_cards, fg_color="#34495e", corner_radius=10)
        card_tipos.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        texto_tipos = f"Tipos detectados: {reporte['Numéricas']} Numéricas  |  {reporte['Texto']} Texto/Categorías"
        ctk.CTkLabel(card_tipos, text=texto_tipos, font=ctk.CTkFont(size=13)).pack(pady=12)

        # Configurar las columnas para que tengan el mismo ancho
        frame_cards.columnconfigure(0, weight=1)
        frame_cards.columnconfigure(1, weight=1)

        ctk.CTkButton(dialog, text="Comenzar a Trabajar", command=dialog.destroy, width=200).pack(pady=15)
    
    @staticmethod
    def mostrar_preview_autocasteo(app_root, tab, propuestas):
        """Muestra un diálogo para que el usuario confirme los casteos detectados."""
        dialog = ctk.CTkToplevel(app_root)
        dialog.title("Confirmar Auto-Casteo")
        dialog.geometry("450x450")
        dialog.grab_set()
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)

        ctk.CTkLabel(dialog, text="✨ Conversiones Seguras Detectadas", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(20, 10))
        ctk.CTkLabel(dialog, text="El motor detectó que las siguientes columnas\npueden optimizarse sin perder datos:", text_color="gray").pack(pady=(0, 15))

        # Panel scrolleable con los cambios
        scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color="#2b2b2b", height=120)
        scroll_frame.pack(fill="x", padx=20, pady=5)

        for col, tipo in propuestas.items():
            ctk.CTkLabel(scroll_frame, text=f"• '{col}' ➔ {tipo}", font=ctk.CTkFont(weight="bold", size=13), text_color="#3498db").pack(anchor="w", pady=2, padx=10)

        def confirmar():
            # Si dice que sí, mandamos la ejecución pesada al hilo
            app_root.ejecutar_tarea_pesada(tab.motor.aplicar_autocasteo_confirmado, propuestas)
            dialog.destroy()

        # Botones de decisión
        frame_btns = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_btns.pack(fill="x", pady=20, padx=20)
        
        ctk.CTkButton(frame_btns, text="Cancelar", command=dialog.destroy, fg_color="#7f8c8d", hover_color="#95a5a6").pack(side="left", expand=True, padx=5)
        ctk.CTkButton(frame_btns, text="Aplicar Cambios", command=confirmar, fg_color="#27ae60").pack(side="right", expand=True, padx=5)
        
    @staticmethod
    def mostrar_scatter(app_root, tab):
        """Muestra un gráfico de dispersión con tooltips, zoom, exportación y sincronización de vistas."""
        if not tab or tab.motor.df is None: return
        df_completo = tab.motor.df

        cols_numericas = df_completo.select_dtypes(include='number').columns.tolist()
        if len(cols_numericas) < 2:
            messagebox.showwarning("Faltan Datos", "Necesitas al menos 2 columnas numéricas para generar un gráfico de correlación. Intenta usar 'Estructura > Auto-Detectar Tipos' primero.")
            return

        dialog = ctk.CTkToplevel(app_root)
        dialog.title("Análisis de Correlación Interactivo")
        dialog.geometry("900x700") 
        dialog.transient(app_root)
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)

        if len(df_completo) > 10000:
            df = df_completo.sample(n=10000, random_state=42)
            lbl_aviso = f"⚠️ Mostrando muestra de 10k puntos (de {len(df_completo):,})"
        else:
            df = df_completo
            lbl_aviso = f"📊 Mostrando {len(df):,} puntos de datos"

        # --- Panel Superior: Controles ---
        panel_ctrl = ctk.CTkFrame(dialog, fg_color="#2b2b2b", corner_radius=10)
        panel_ctrl.pack(fill="x", padx=20, pady=15, ipady=5)

        ctk.CTkLabel(panel_ctrl, text="Eje X:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(15, 5))
        combo_x = ctk.CTkComboBox(panel_ctrl, values=cols_numericas, width=150)
        combo_x.pack(side="left", padx=5)
        combo_x.set(cols_numericas[0])

        ctk.CTkLabel(panel_ctrl, text="Eje Y:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(15, 5))
        combo_y = ctk.CTkComboBox(panel_ctrl, values=cols_numericas, width=150)
        combo_y.pack(side="left", padx=5)
        combo_y.set(cols_numericas[1])

        ctk.CTkLabel(panel_ctrl, text=lbl_aviso, text_color="gray", font=ctk.CTkFont(size=11)).pack(side="left", padx=15)

        def exportar_grafico():
            if not estado_grafico["figura"]: return
            filepath = filedialog.asksaveasfilename(
                title="Exportar Gráfico", defaultextension=".png",
                filetypes=[("Imagen PNG", "*.png"), ("Documento PDF", "*.pdf")]
            )
            if filepath:
                try:
                    estado_grafico["figura"].savefig(filepath, dpi=300, bbox_inches='tight', facecolor='#242424')
                    messagebox.showinfo("✅ Éxito", f"Gráfico exportado correctamente en:\n{filepath}")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo exportar el gráfico:\n{e}")

        btn_graficar = ctk.CTkButton(panel_ctrl, text="📊 Graficar", fg_color="#27ae60", hover_color="#2ecc71", width=110)
        btn_graficar.pack(side="right", padx=(10, 15))
        
        btn_exportar = ctk.CTkButton(panel_ctrl, text="💾 Exportar", command=exportar_grafico, fg_color="#8e44ad", hover_color="#9b59b6", width=110)
        btn_exportar.pack(side="right", padx=(10, 0))

        # --- Lienzo para Matplotlib ---
        frame_grafico = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_grafico.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        estado_grafico = {"canvas": None, "figura": None, "toolbar": None, "custom_toolbar": None}

        def generar_grafico():
            col_x = combo_x.get()
            col_y = combo_y.get()
            
            if estado_grafico["canvas"]: estado_grafico["canvas"].get_tk_widget().destroy()
            if estado_grafico["toolbar"]: estado_grafico["toolbar"].destroy()
            if estado_grafico["custom_toolbar"]: estado_grafico["custom_toolbar"].destroy()
            if estado_grafico["figura"]: plt.close(estado_grafico["figura"])
                
            fig, ax = plt.subplots(figsize=(8, 5), facecolor='#242424')
            ax.set_facecolor('#2b2b2b')
            
            # El parámetro picker=5 da un margen de error de 5 píxeles para facilitar el clic
            scatter = ax.scatter(df[col_x], df[col_y], alpha=0.7, color='#3498db', edgecolors='white', linewidth=0.5, picker=5)
            
            ax.set_xlabel(col_x, color='white', fontweight='bold')
            ax.set_ylabel(col_y, color='white', fontweight='bold')
            ax.tick_params(colors='gray')
            ax.grid(True, linestyle='--', alpha=0.2, color='white')
            for spine in ax.spines.values(): spine.set_edgecolor('#404040')

            annot = ax.annotate("", xy=(0,0), xytext=(15,15), textcoords="offset points",
                                bbox=dict(boxstyle="round,pad=0.4", fc="#1e1e1e", ec="#3498db", lw=1),
                                arrowprops=dict(arrowstyle="->", color="#3498db"))
            annot.set_visible(False)
            annot.set_color("white")

            def update_annot(ind):
                idx_grafico = ind["ind"][0] 
                pos = scatter.get_offsets()[idx_grafico]
                annot.xy = pos
                idx_real = df.index[idx_grafico]
                val_x = df[col_x].iloc[idx_grafico]
                val_y = df[col_y].iloc[idx_grafico]
                annot.set_text(f"Fila: {idx_real}\n{col_x}: {val_x}\n{col_y}: {val_y}")
                annot.get_bbox_patch().set_alpha(0.9)

            def hover(event):
                vis = annot.get_visible()
                if event.inaxes == ax:
                    cont, ind = scatter.contains(event)
                    if cont:
                        update_annot(ind)
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                    elif vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

            # --- NUEVO: NAVEGACIÓN RÁPIDA AL HACER CLIC ---
            def on_click(event):
                # Extraemos qué punto se hizo clic
                ind = event.ind[0] 
                idx_real = df.index[ind] 
                
                try:
                    # 1. Buscamos en qué posición (iloc) de la tabla general está este dato
                    iloc_pos = tab.motor.df.index.get_loc(idx_real)
                    
                    # Por si hay índices duplicados en datos caóticos (devuelve slice o array)
                    if not isinstance(iloc_pos, int):
                        import numpy as np
                        iloc_pos = iloc_pos.start if isinstance(iloc_pos, slice) else np.where(iloc_pos)[0][0]
                    
                    # 2. Calculamos en qué página de la interfaz cae esa fila
                    pagina_destino = (iloc_pos // tab.filas_por_pagina) + 1
                    pos_relativa = iloc_pos % tab.filas_por_pagina
                    
                    # 3. Viajamos a la página si no estamos en ella
                    if tab.pagina_actual != pagina_destino:
                        tab.pagina_actual = pagina_destino
                        tab.actualizar_vista_previa()
                    
                    # 4. Seleccionamos visualmente la fila en el Treeview
                    items = tab.tree.get_children()
                    if pos_relativa < len(items):
                        item_id = items[pos_relativa]
                        tab.tree.selection_set(item_id)  # Lo pinta de azul
                        tab.tree.focus(item_id)         # Le da el foco
                        tab.tree.see(item_id)           # Hace scroll automático hasta esa fila
                        
                except Exception as e:
                    print(f"Sincronización de vista falló: {e}")

            fig.canvas.mpl_connect("motion_notify_event", hover)
            fig.canvas.mpl_connect("pick_event", on_click) # Escucha el clic
            fig.tight_layout()

            # Inyectamos el gráfico
            canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            toolbar = NavigationToolbar2Tk(canvas, frame_grafico)
            toolbar.update()
            toolbar.pack_forget() 
            
            custom_toolbar = ctk.CTkFrame(frame_grafico, fg_color="#2b2b2b", height=40, corner_radius=8)
            custom_toolbar.pack(side="bottom", fill="x", pady=(10, 0))
            
            ctk.CTkButton(custom_toolbar, text="🏠 Vista Original", width=100, fg_color="#34495e", hover_color="#2c3e50", command=toolbar.home).pack(side="left", padx=5, pady=5)
            ctk.CTkButton(custom_toolbar, text="⬅️ Atrás", width=80, fg_color="#34495e", hover_color="#2c3e50", command=toolbar.back).pack(side="left", padx=5, pady=5)
            ctk.CTkButton(custom_toolbar, text="➡️ Adelante", width=80, fg_color="#34495e", hover_color="#2c3e50", command=toolbar.forward).pack(side="left", padx=5, pady=5)
            ctk.CTkButton(custom_toolbar, text="🤚 Mover", width=100, fg_color="#2980b9", hover_color="#1f618d", command=toolbar.pan).pack(side="left", padx=(20, 5), pady=5)
            ctk.CTkButton(custom_toolbar, text="🔍 Zoom", width=100, fg_color="#2980b9", hover_color="#1f618d", command=toolbar.zoom).pack(side="left", padx=5, pady=5)

            estado_grafico["canvas"] = canvas
            estado_grafico["figura"] = fig
            estado_grafico["toolbar"] = toolbar
            estado_grafico["custom_toolbar"] = custom_toolbar

        btn_graficar.configure(command=generar_grafico)
        generar_grafico()

        def on_close():
            if estado_grafico["figura"]: plt.close(estado_grafico["figura"])
            dialog.destroy()
            
        dialog.protocol("WM_DELETE_WINDOW", on_close)
    
    @staticmethod
    def mostrar_conector_sql(app_root, tab):
        """Muestra la ventana para configurar la conexión a bases de datos SQL."""
        dialog = ctk.CTkToplevel(app_root)
        dialog.title("🔌 Conectar a Base de Datos SQL")
        dialog.geometry("450x580")
        dialog.resizable(False, False)
        dialog.transient(app_root)
        dialog.grab_set()
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)

        ctk.CTkLabel(dialog, text="Configuración del Servidor", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(20, 15))

        # --- Selección de Motor ---
        ctk.CTkLabel(dialog, text="Motor de Base de Datos:").pack(anchor="w", padx=40)
        combo_motor = ctk.CTkOptionMenu(dialog, values=["MySQL", "PostgreSQL", "SQL Server"], width=320)
        combo_motor.pack(pady=(5, 15))

        # --- Host y Puerto ---
        frame_red = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_red.pack(fill="x", padx=40)

        # Hacemos que las columnas sean elásticas (Host toma 2 partes, Puerto 1 parte)
        frame_red.grid_columnconfigure(0, weight=2)
        frame_red.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_red, text="Host / IP:").grid(row=0, column=0, sticky="w")
        entry_host = ctk.CTkEntry(frame_red, placeholder_text="localhost")
        entry_host.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(5, 10))

        ctk.CTkLabel(frame_red, text="Puerto:").grid(row=0, column=1, sticky="w")
        entry_port = ctk.CTkEntry(frame_red, placeholder_text="3306")
        entry_port.grid(row=1, column=1, sticky="ew", pady=(5, 10))

        # --- Credenciales ---
        ctk.CTkLabel(dialog, text="Usuario:").pack(anchor="w", padx=40)
        entry_user = ctk.CTkEntry(dialog, width=320)
        entry_user.pack(pady=(5, 10))

        ctk.CTkLabel(dialog, text="Contraseña:").pack(anchor="w", padx=40)
        entry_pass = ctk.CTkEntry(dialog, width=320, show="*")
        entry_pass.pack(pady=(5, 10))

        ctk.CTkLabel(dialog, text="Nombre de la Base de Datos:").pack(anchor="w", padx=40)
        entry_db = ctk.CTkEntry(dialog, width=320, placeholder_text="schema_name")
        entry_db.pack(pady=(5, 20))

        # --- NUEVO: Selector de Tablas (Oculto inicialmente) ---
        frame_tablas = ctk.CTkFrame(dialog, fg_color="transparent")
        ctk.CTkLabel(frame_tablas, text="Selecciona la tabla a importar:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=40)
        combo_tablas = ctk.CTkOptionMenu(frame_tablas, width=320, values=[""])
        combo_tablas.pack(pady=(5, 10))

        def test_conexion():
            motor_bd = combo_motor.get()
            host = entry_host.get().strip() or "localhost"
            puerto_default = "3306" if motor_bd == "MySQL" else "5432" if motor_bd == "PostgreSQL" else "1433"
            puerto = entry_port.get().strip() or puerto_default
            usuario = entry_user.get().strip()
            password = entry_pass.get().strip()
            base_datos = entry_db.get().strip()

            if not usuario or not base_datos:
                messagebox.showwarning("Faltan Datos", "Usuario y Base de Datos son obligatorios.")
                return

            btn_test.configure(state="disabled", text="⏳ Conectando...")
            dialog.update()

            def ejecutar_prueba():
                try:
                    # Si es exitoso, 'mensaje' ahora es la lista de tablas
                    exito, mensaje = tab.motor.probar_conexion_sql(motor_bd, host, puerto, usuario, password, base_datos)
                except Exception as e:
                    print(f"\n--- ERROR SQL CRÍTICO ---\n{e}\n-------------------------\n")
                    exito, mensaje = False, f"Falta una librería o error crítico:\n{str(e)}"
                    
                def restaurar_ui():
                    btn_test.configure(state="normal", text="⚡ Probar Conexión")
                    if exito:
                        # Hacemos visible el selector ANTES del contenedor de botones
                        frame_tablas.pack(before=frame_botones, fill="x", pady=(5, 10))
                        combo_tablas.configure(values=mensaje)
                        combo_tablas.set(mensaje[0] if mensaje else "Sin tablas")
                        btn_conectar.configure(state="normal")
                        messagebox.showinfo("✅ Éxito", f"¡Conexión establecida!\nSe detectaron {len(mensaje)} tablas en '{base_datos}'.")
                    else:
                        messagebox.showerror("❌ Error de Conexión", mensaje)
                
                app_root.after(0, restaurar_ui)

            app_root.ejecutar_tarea_pesada(ejecutar_prueba)

        def realizar_importacion():
            tabla_seleccionada = combo_tablas.get()
            if not tabla_seleccionada or tabla_seleccionada == "Sin tablas":
                return

            motor_bd = combo_motor.get()
            host = entry_host.get().strip() or "localhost"
            puerto_default = "3306" if motor_bd == "MySQL" else "5432" if motor_bd == "PostgreSQL" else "1433"
            puerto = entry_port.get().strip() or puerto_default
            usuario = entry_user.get().strip()
            password = entry_pass.get().strip()
            base_datos = entry_db.get().strip()

            btn_conectar.configure(state="disabled", text="⏳ Importando...")
            dialog.update()

            def tarea_ingesta():
                try:
                    tab.motor.importar_tabla_sql(motor_bd, host, puerto, usuario, password, base_datos, tabla_seleccionada)
                    exito = True
                    error_msg = ""
                except Exception as e:
                    exito = False
                    error_msg = str(e)

                def finalizar_ui():
                    # 1. ¡DESTRUIR EL DIÁLOGO PRIMERO! Esto libera el bloqueo y evita el Deadlock
                    dialog.destroy()
                    
                    if exito:
                        tab.pagina_actual = 1
                        if hasattr(tab, 'actualizar_vista_previa'): tab.actualizar_vista_previa()
                        if hasattr(tab, 'refrescar_interfaz'): tab.refrescar_interfaz()
                        if hasattr(app_root, 'actualizar_estado'): app_root.actualizar_estado()
                    else:
                        # 2. Forzamos que el mensaje aparezca sobre la ventana principal
                        messagebox.showerror("❌ Error", f"No se pudo crear la columna:\n{error_msg}", parent=app_root)

                app_root.after(0, finalizar_ui)

            app_root.ejecutar_tarea_pesada(tarea_ingesta)
        
        # --- NUEVO: Botones de Acción Lado a Lado ---
        frame_botones = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_botones.pack(pady=10, fill="x", padx=40)

        btn_test = ctk.CTkButton(frame_botones, text="⚡ Probar Conexión", command=test_conexion, fg_color="#34495e", hover_color="#2c3e50")
        btn_test.pack(side="left", expand=True, padx=(0, 5))

        btn_conectar = ctk.CTkButton(frame_botones, text="🔗 Importar Tabla", command=realizar_importacion, fg_color="#27ae60", hover_color="#2ecc71", state="disabled")
        btn_conectar.pack(side="right", expand=True, padx=(5, 0))
        
        def al_cerrar_ventana():
            dialog.destroy()
            # Si el usuario cierra con la 'X' y no llegó a importar nada, limpiamos la pestaña vacía
            if tab.motor.df is None:
                for nombre, t in app_root.pestanas.items():
                    if t == tab:
                        app_root.tabview.set(nombre)
                        app_root.cerrar_pestana_actual()
                        break

        dialog.protocol("WM_DELETE_WINDOW", al_cerrar_ventana)
        
    @staticmethod
    def mostrar_unpivot(app_root, tab):
        """Muestra la ventana para Anular Dinamización (Unpivot)."""
        if not tab or tab.motor.df is None: return

        dialog = ctk.CTkToplevel(app_root)
        dialog.title("🔄 Anular Dinamización (Unpivot)")
        dialog.geometry("500x550")
        dialog.transient(app_root)
        dialog.grab_set()
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)

        ctk.CTkLabel(dialog, text="Configuración de Unpivot", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="Selecciona qué columnas mantener fijas (Anclas).\nLas que NO selecciones, se transformarán en filas.", text_color="gray").pack(pady=(0, 15))

        columnas = list(tab.motor.df.columns)
        vars_ancla = {}

        # --- Lista interactiva de columnas ---
        frame_lista = ctk.CTkFrame(dialog, fg_color="#2b2b2b", corner_radius=10)
        frame_lista.pack(fill="both", expand=True, padx=30, pady=5)
        
        ctk.CTkLabel(frame_lista, text="📌 Seleccionar Columnas Ancla:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        scroll_ancla = ctk.CTkScrollableFrame(frame_lista, height=150, fg_color="transparent")
        scroll_ancla.pack(fill="both", expand=True, padx=5, pady=5)

        for col in columnas:
            var = ctk.BooleanVar(value=False)
            vars_ancla[col] = var
            chk = ctk.CTkCheckBox(scroll_ancla, text=col, variable=var, checkbox_width=20, checkbox_height=20)
            chk.pack(anchor="w", pady=4, padx=10)

        # --- Nombres de las nuevas columnas ---
        frame_nombres = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_nombres.pack(fill="x", padx=30, pady=15)
        frame_nombres.grid_columnconfigure(0, weight=1)
        frame_nombres.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_nombres, text="Nombre nueva col. 'Atributo':").grid(row=0, column=0, sticky="w", padx=5)
        entry_var = ctk.CTkEntry(frame_nombres, placeholder_text="Ej: Mes")
        entry_var.grid(row=1, column=0, padx=5, sticky="ew")

        ctk.CTkLabel(frame_nombres, text="Nombre nueva col. 'Valor':").grid(row=0, column=1, sticky="w", padx=5)
        entry_val = ctk.CTkEntry(frame_nombres, placeholder_text="Ej: Ventas")
        entry_val.grid(row=1, column=1, padx=5, sticky="ew")

        def aplicar_unpivot():
            anclas = [col for col, var in vars_ancla.items() if var.get()]
            valores = [col for col in columnas if col not in anclas]

            if not anclas:
                messagebox.showwarning("Faltan Datos", "Debes seleccionar al menos una columna fija (Ancla).")
                return
            if not valores:
                messagebox.showwarning("Faltan Datos", "No quedan columnas restantes para desdinamizar.")
                return

            n_var = entry_var.get().strip() or "Atributo"
            n_val = entry_val.get().strip() or "Valor"

            def tarea_unpivot():
                # El motor hace el trabajo pesado
                tab.motor.anular_dinamizacion(anclas, valores, n_var, n_val)
                tab.pagina_actual = 1

            # Lo enviamos al hilo de carga para que no se congele la PC
            # Esto automáticamente llamará a tab.refrescar_interfaz() al terminar
            app_root.ejecutar_tarea_pesada(tarea_unpivot)
            dialog.destroy()

        ctk.CTkButton(dialog, text="✅ Aplicar Unpivot", command=aplicar_unpivot, fg_color="#27ae60", hover_color="#2ecc71").pack(pady=20)
        
    @staticmethod
    def mostrar_columna_condicional(app_root, tab):
        """Muestra la ventana para crear Columnas Condicionales (IF-THEN-ELSE)."""
        if not tab or tab.motor.df is None: return

        dialog = ctk.CTkToplevel(app_root)
        dialog.title("🔀 Columna Condicional (IF-THEN-ELSE)")
        dialog.geometry("450x580")
        dialog.transient(app_root)
        dialog.grab_set()
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)

        columnas = list(tab.motor.df.columns)
        
        ctk.CTkLabel(dialog, text="Lógica Condicional", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(20, 5))
        
        frame_form = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_form.pack(fill="both", expand=True, padx=30, pady=5)

        # --- Formulario Paso a Paso ---
        ctk.CTkLabel(frame_form, text="1. Si la columna:").pack(anchor="w", pady=(5, 0))
        combo_columna = ctk.CTkOptionMenu(frame_form, values=columnas)
        combo_columna.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame_form, text="2. Es:").pack(anchor="w")
        combo_operador = ctk.CTkOptionMenu(frame_form, values=["==", "!=", ">", "<", ">=", "<="])
        combo_operador.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame_form, text="3. A este valor:").pack(anchor="w")
        entry_condicion = ctk.CTkEntry(frame_form, placeholder_text="Ej: 100 o 'Aprobado'")
        entry_condicion.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(frame_form, text="4. Entonces escribir (Verdadero):").pack(anchor="w")
        entry_verdadero = ctk.CTkEntry(frame_form, placeholder_text="Ej: Alto")
        entry_verdadero.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame_form, text="5. Sino escribir (Falso):").pack(anchor="w")
        entry_falso = ctk.CTkEntry(frame_form, placeholder_text="Ej: Bajo")
        entry_falso.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(frame_form, text="6. Nombre de la nueva columna:").pack(anchor="w")
        entry_nueva_col = ctk.CTkEntry(frame_form, placeholder_text="Ej: Categoria_Ventas")
        entry_nueva_col.pack(fill="x", pady=(0, 20))

        def aplicar_condicion():
            col = combo_columna.get()
            op = combo_operador.get()
            val_cond = entry_condicion.get().strip()
            val_true = entry_verdadero.get().strip()
            val_false = entry_falso.get().strip()
            nueva_col = entry_nueva_col.get().strip()

            if not all([col, op, val_cond, val_true, val_false, nueva_col]):
                # Agregamos parent=dialog para que el aviso no quede oculto atrás
                messagebox.showwarning("Faltan Datos", "Por favor completa todos los campos del formulario.", parent=dialog)
                return

            btn_aplicar.configure(state="disabled", text="⏳ Procesando...")
            dialog.update()

            def tarea_condicional():
                try:
                    tab.motor.agregar_columna_condicional(col, op, val_cond, val_true, val_false, nueva_col)
                    exito = True
                    error_msg = ""
                except Exception as e:
                    exito = False
                    error_msg = str(e)
                    
                def finalizar_ui():
                    # 1. Liberamos el foco y ocultamos la ventana para que parezca instantáneo
                    dialog.grab_release()
                    dialog.withdraw()
                    
                    if exito:
                        tab.pagina_actual = 1
                        if hasattr(tab, 'actualizar_vista_previa'): tab.actualizar_vista_previa()
                        if hasattr(tab, 'refrescar_interfaz'): tab.refrescar_interfaz()
                        if hasattr(app_root, 'actualizar_estado'): app_root.actualizar_estado()
                    else:
                        # 2. Mostramos el error de forma segura sobre la ventana principal
                        messagebox.showerror("❌ Error", f"No se pudo crear la columna:\n{error_msg}", parent=app_root)
                    
                    # 3. Destruimos la ventana en la memoria 250ms después 
                    # Esto evita el 'TclError' interno de CustomTkinter
                    app_root.after(250, dialog.destroy)
                        
                app_root.after(0, finalizar_ui)

            app_root.ejecutar_tarea_pesada(tarea_condicional)

        btn_aplicar = ctk.CTkButton(dialog, text="✅ Crear Columna", command=aplicar_condicion, fg_color="#27ae60", hover_color="#2ecc71")
        btn_aplicar.pack(pady=(0, 20))
        
    @staticmethod
    def mostrar_config_ia(app_root):
        """Muestra la ventana para configurar la API Key integrándose a la Bóveda Segura."""
        dialog = ctk.CTkToplevel(app_root)
        dialog.title("⚙️ Configuración del Analista IA")
        dialog.geometry("500x280") 
        dialog.transient(app_root)
        dialog.grab_set()
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)

        ctk.CTkLabel(dialog, text="Conexión con el Cerebro IA", font=ctk.CTkFont(weight="bold", size=16), text_color=("#1a1a1a", "#f5f6fa")).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="Ingresa tu clave de API. Puedes guardarla en tu equipo\no conectarla solo por esta sesión.", text_color="gray").pack(pady=(0, 15))

        frame_form = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_form.pack(fill="x", padx=40)

        ctk.CTkLabel(frame_form, text="API Key:").grid(row=0, column=0, sticky="w", pady=5)
        entry_key = ctk.CTkEntry(frame_form, placeholder_text="Pega tu API Key aquí...", show="*")
        entry_key.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Leer desde la sesión o las credenciales cargadas
        if hasattr(app_root, 'api_key_session') and app_root.api_key_session:
            entry_key.insert(0, app_root.api_key_session)
        elif "api_key_ia" in app_root.credenciales:
            entry_key.insert(0, app_root.credenciales["api_key_ia"])

        frame_form.grid_columnconfigure(1, weight=1)

        def conectar_temporal():
            clave = entry_key.get().strip()
            if not clave: return messagebox.showwarning("Advertencia", "Ingresa una API Key válida.")
            app_root.api_key_session = clave 
            messagebox.showinfo("✅ Conectado", "API Key conectada solo por esta sesión. No se guardará en tu equipo.")
            dialog.destroy()

        def guardar_permanente():
            clave = entry_key.get().strip()
            if not clave: return messagebox.showwarning("Advertencia", "Ingresa una API Key válida.")
            
            app_root.api_key_session = clave 
            
            # Sub-función que ejecuta el cifrado
            def ejecutar_guardado_seguro(pwd):
                app_root.password_maestra = pwd
                app_root.credenciales["api_key_ia"] = clave
                try:
                    app_root.boveda.guardar_datos(pwd, app_root.credenciales)
                    messagebox.showinfo("💾 Guardado Seguro", "API Key encriptada con grado militar (AES-256) y guardada exitosamente.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo encriptar:\n{e}")

            if app_root.password_maestra:
                # Si ya desbloqueó la bóveda en esta sesión, guardamos directo
                ejecutar_guardado_seguro(app_root.password_maestra)
                dialog.destroy()
            else:
                # Si no tiene bóveda, lo mandamos a crear una Contraseña Maestra
                dialog.destroy()
                ModalesUI.crear_password_maestra(app_root, callback=ejecutar_guardado_seguro)

        frame_btns = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_btns.pack(pady=20, fill="x", padx=20)
        
        ctk.CTkButton(frame_btns, text="Cancelar", command=dialog.destroy, fg_color="#7f8c8d", hover_color="#95a5a6", width=100).pack(side="left", padx=5)
        ctk.CTkButton(frame_btns, text="💾 Guardar", command=guardar_permanente, fg_color="#8e44ad", hover_color="#9b59b6", width=120).pack(side="right", padx=5)
        ctk.CTkButton(frame_btns, text="🔌 Conectar (Temporal)", command=conectar_temporal, fg_color="#2980b9", hover_color="#3498db", width=150).pack(side="right", padx=5)
        
    @staticmethod
    def pedir_password_maestra(app_root):
        """Muestra un modal para desbloquear la bóveda al iniciar la app."""
        dialog = ctk.CTkToplevel(app_root)
        dialog.title("🔒 Bóveda Bloqueada")
        dialog.geometry("350x200")
        dialog.transient(app_root)
        dialog.grab_set()
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)
        
        ctk.CTkLabel(dialog, text="Desbloquear Bóveda", font=ctk.CTkFont(weight="bold", size=16), text_color=("#1a1a1a", "#f5f6fa")).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="Ingresa tu Contraseña Maestra:", text_color="gray").pack()
        
        entry_pass = ctk.CTkEntry(dialog, show="*", width=250)
        entry_pass.pack(pady=15)
        entry_pass.focus()
        
        def intentar_desbloqueo(event=None):
            pwd = entry_pass.get()
            try:
                datos = app_root.boveda.leer_datos(pwd)
                app_root.credenciales = datos
                app_root.password_maestra = pwd
                # Restauramos la API Key a la sesión activa automáticamente
                app_root.api_key_session = datos.get("api_key_ia")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Contraseña incorrecta o bóveda corrupta.", parent=dialog)
                entry_pass.delete(0, 'end')
                
        entry_pass.bind("<Return>", intentar_desbloqueo)
        ctk.CTkButton(dialog, text="🔓 Desbloquear", command=intentar_desbloqueo, fg_color="#2980b9", hover_color="#3498db").pack(pady=5)

    @staticmethod
    def crear_password_maestra(app_root, callback):
        """Muestra un modal para crear la Contraseña Maestra por primera vez."""
        dialog = ctk.CTkToplevel(app_root)
        dialog.title("🛡️ Crear Bóveda")
        dialog.geometry("350x250")
        dialog.transient(app_root)
        dialog.grab_set()
        if hasattr(app_root, 'fijar_icono'): app_root.fijar_icono(dialog)
        
        ctk.CTkLabel(dialog, text="Crear Contraseña Maestra", font=ctk.CTkFont(weight="bold", size=16), text_color=("#1a1a1a", "#f5f6fa")).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="Esta contraseña encriptará tus datos.\n¡Si la olvidas, perderás lo guardado!", text_color="#e74c3c").pack()
        
        entry_pass = ctk.CTkEntry(dialog, show="*", width=250, placeholder_text="Nueva contraseña...")
        entry_pass.pack(pady=(15, 5))
        
        entry_confirm = ctk.CTkEntry(dialog, show="*", width=250, placeholder_text="Confirmar contraseña...")
        entry_confirm.pack(pady=5)
        
        def guardar():
            p1 = entry_pass.get()
            p2 = entry_confirm.get()
            if not p1 or p1 != p2:
                messagebox.showwarning("Error", "Las contraseñas no coinciden o están vacías.", parent=dialog)
                return
            dialog.destroy()
            callback(p1) # Llamamos a la función de guardado con la nueva contraseña
            
        ctk.CTkButton(dialog, text="💾 Crear Bóveda", command=guardar, fg_color="#27ae60", hover_color="#2ecc71").pack(pady=15)