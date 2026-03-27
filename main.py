# Librerías estándar para el proyecto
import os
import sys
import ctypes
import tkinter as tk
from tkinter import filedialog, ttk

# Librerías que se necesitan instalar (pandas, customtkinter)
import pandas as pd
import customtkinter as ctk

# "set_appearance_mode" sirve para que siga el modo claro/oscuro del sistema operativo. Opciones: "light", "dark", "System".
ctk.set_appearance_mode("System") 
# "set_default_color_theme" sirve para botones, barras de progreso, etc. No afecta a la tabla (Treeview) porque es de ttk, no de customtkinter. Opciones: "blue", "dark-blue", "green".
ctk.set_default_color_theme("blue") 


# ---- FUNCIÓN AUXILIAR DE EMPAQUETADO ----
def obtener_ruta(ruta_relativa):
    """
    Obtiene la ruta absoluta a los recursos estáticos (como el ícono .ico).
    Esencial para la compatibilidad con PyInstaller:
    - En el .exe final, PyInstaller descomprime los 'assets' en una carpeta temporal (_MEIPASS).
    - En desarrollo (VS Code), utiliza la ruta normal del sistema de archivos.
    """
    try:
        # Intenta buscar la carpeta temporal creada por el .exe en tiempo de ejecución
        ruta_base = sys._MEIPASS
    except AttributeError:
        # Falla si estamos ejecutando el script .py directo; usa la ruta del archivo actual
        ruta_base = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(ruta_base, ruta_relativa)


class QueryLibreApp(ctk.CTk):
    """
    Clase principal de QueryLibre.
    Gestiona la interfaz gráfica de usuario (GUI), el estado de los datos en memoria (DataFrame)
    y el historial de transformaciones aplicadas.
    """
    def __init__(self):
        super().__init__()

        # ---- VARIABLES DE ESTADO (MEMORIA) ----
        self.df = None                 # DataFrame activo (los datos actuales en pantalla)
        self.historial_pasos = []      # Registro en texto de los cambios para mostrar en la interfaz
        self.df_history = []           # Copias del DataFrame para hacer funcionar el botón "Deshacer"
        
        # ---- CONFIGURACIÓN DE LA VENTANA PRINCIPAL ----
        self.title("QueryLibre - Motor de Transformación de Datos")
        self.geometry("1100x650") 
        self.minsize(900, 500)
        
        # ---- CARGA DEL ÍCONO ----
        ruta_icono = obtener_ruta(os.path.join("assets", "main.ico"))
        try:
            self.iconbitmap(ruta_icono) 
        except Exception as e:
            # Si el ícono falla (ej. problemas de Tkinter o SO diferente), avisamos pero no crasheamos
            print(f"Advertencia - Error con el ícono: {e}")

        # ---- INTEGRACIÓN CON WINDOWS (Barra de Tareas) ----
        # Evita que Windows agrupe la app bajo el ícono por defecto de Python.
        # Asignamos un AppUserModelID único para forzar el uso de nuestro 'main.ico'.
        try:
            myappid = 'ivanravarotto.querylibre.app.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except AttributeError:
            # Si el sistema operativo no es Windows (ej. Mac o Linux), ignoramos este paso
            pass
        
        # ---- LAYOUT PRINCIPAL (GRILLA) ----
        self.grid_columnconfigure(1, weight=1) # Obliga al área derecha a ocupar todo el ancho libre
        self.grid_rowconfigure(0, weight=1)    # Obliga a la ventana a ocupar todo el alto libre

        # ---- 1. PANEL LATERAL (SIDEBAR) ----
        # Contenedor principal del menú izquierdo. Su ancho es fijo y se estira verticalmente.
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew") # nsew: se adhiere a todos los bordes (North, South, East, West)
        
        # Al darle weight=1 a la fila 4, forzamos a que empuje su contenido hacia abajo
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # -- Logo / Título --
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="QueryLibre", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # -- Botones de Acción Principal --
        self.btn_cargar = ctk.CTkButton(self.sidebar_frame, text="📁 Cargar Archivo", command=self.cargar_archivo)
        self.btn_cargar.grid(row=1, column=0, padx=20, pady=10)

        # Los botones de transformación y exportación inician bloqueados ('disabled') 
        # hasta que se cargue exitosamente un archivo en memoria.
        self.btn_transformar = ctk.CTkButton(self.sidebar_frame, text="🔗 Unir Datasets", state="disabled", command=self.unir_datasets)
        self.btn_transformar.grid(row=2, column=0, padx=20, pady=10)

        self.btn_exportar = ctk.CTkButton(self.sidebar_frame, text="💾 Exportar Datos", state="disabled", command=self.exportar_datos)
        self.btn_exportar.grid(row=3, column=0, padx=20, pady=10)
        
        # -- Información de Versión --
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text="QueryLibre v1.1.0", font=ctk.CTkFont(size=11), text_color="gray")
        self.version_label.grid(row=4, column=0, padx=20, pady=20, sticky="s") # sticky="s" (South) lo ancla al borde inferior, otras opciones: n (top), e (right), w (left).
        
        # ---- 2. ÁREA DE TRABAJO PRINCIPAL ----
        # Contenedor central donde sucede toda la acción (Barra de herramientas, Tabla, Historial).
        # Ocupa la columna 1 (a la derecha del sidebar) y se expande en todas direcciones (nsew).
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # -- Mensaje de Bienvenida (Placeholder) --
        # Se muestra centrado al iniciar la app. 
        # Más adelante, la función cargar_archivo() usará 'pack_forget()' para ocultarlo 
        # y darle lugar a la tabla de datos real.
        self.welcome_label = ctk.CTkLabel(self.main_frame, text="Bienvenido a QueryLibre\nCarga un dataset para comenzar.", font=ctk.CTkFont(size=16))
        self.welcome_label.pack(expand=True) # expand=True lo centra perfectamente en todo el espacio vacío

        # ---- 3. BARRA DE HERRAMIENTAS (Transformaciones Rápidas) ----
        # Contenedor superior para los botones de acción. 
        # fg_color="transparent" permite que se funda con el fondo del main_frame.
        # IMPORTANTE: Este frame no se empaqueta (.pack) al iniciar. Permanece en memoria
        # y se muestra recién cuando cargar_archivo() inyecta los datos exitosamente.
        self.toolbar_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        # -- Grupo 1: Limpieza a nivel Filas (Data Cleaning) --
        # side="left" los apila de forma horizontal, uno al lado del otro.
        self.btn_dup = ctk.CTkButton(self.toolbar_frame, text="Eliminar Duplicados", command=self.eliminar_duplicados, width=130, fg_color="#34495e")
        self.btn_dup.pack(side="left", padx=5)

        self.btn_nulos = ctk.CTkButton(self.toolbar_frame, text="Limpiar Nulos", command=self.limpiar_nulos, width=120, fg_color="#34495e")
        self.btn_nulos.pack(side="left", padx=5)

        # -- Grupo 2: Gestión a nivel Columnas (Feature Engineering) --
        # Se aplican colores semánticos (Rojo = Destructivo, Azul = Edición) para guiar al usuario (UX).
        self.btn_eliminar_col = ctk.CTkButton(self.toolbar_frame, text="🗑️ Eliminar Columna", command=self.eliminar_columna, width=140, fg_color="#c0392b", hover_color="#922b21")
        self.btn_eliminar_col.pack(side="left", padx=5)

        self.btn_renombrar_col = ctk.CTkButton(self.toolbar_frame, text="✏️ Renombrar Columna", command=self.renombrar_columna, width=150, fg_color="#2980b9", hover_color="#1f618d")
        self.btn_renombrar_col.pack(side="left", padx=5)

        # -- Grupo 3: Creación de Nuevas Columnas (Feature Engineering Avanzado) --
        # Agrupamos lógicamente las funciones que generan nuevos datos a partir de los existentes.
        # Usamos colores distintivos (Morado = Matemáticas, Naranja = Textos) para diferenciarlas.
        self.btn_calcular = ctk.CTkButton(self.toolbar_frame, text="🧮 Calcular Columna", command=self.calcular_columna, width=150, fg_color="#8e44ad", hover_color="#732d91")
        self.btn_calcular.pack(side="left", padx=5)

        self.btn_combinar = ctk.CTkButton(self.toolbar_frame, text="🔗 Combinar Textos", command=self.combinar_columnas, width=150, fg_color="#d35400", hover_color="#a04000")
        self.btn_combinar.pack(side="left", padx=5)

        # ---- 4. ÁREA DE DATOS E HISTORIAL (Contenedor Inferior) ----
        # Contenedor para la tabla de datos y el panel de historial. 
        # Al igual que el toolbar, se mantiene oculto en memoria hasta que se carga un archivo.
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        # -- Panel Derecho: Historial de Pasos (Máquina del Tiempo) --
        # IMPORTANTE: Se empaqueta PRIMERO con side="right" para asegurar su posición
        # antes de que la tabla de datos ocupe todo el espacio sobrante.
        self.history_frame = ctk.CTkFrame(self.content_frame, width=220)
        # pack_propagate(False) evita que los widgets internos (como el TextBox) 
        # modifiquen el ancho fijo (220px) de este contenedor. Mantiene la UI estable.
        self.history_frame.pack_propagate(False) 
        self.history_frame.pack(side="right", fill="y")
        
        self.history_label = ctk.CTkLabel(self.history_frame, text="📋 Pasos Aplicados", font=ctk.CTkFont(weight="bold"))
        self.history_label.pack(pady=(10, 5))
        
        # Cuadro de texto para el registro continuo de acciones. 
        # Inicia en state="disabled" (Solo lectura) para que el usuario no pueda escribir en él manualmente.
        self.history_text = ctk.CTkTextbox(self.history_frame, font=("Arial", 11), state="disabled", width=200)
        self.history_text.pack(expand=True, fill="both", padx=10, pady=5)

        # Botón para deshacer acciones (Undo). 
        # Inicia deshabilitado porque en este punto el historial (df_history) está vacío.
        self.btn_deshacer = ctk.CTkButton(self.history_frame, text="↩️ Deshacer Último", command=self.deshacer_paso, state="disabled", fg_color="#e74c3c", hover_color="#c0392b")
        self.btn_deshacer.pack(pady=(5, 15), padx=10, fill="x")

        # -- Panel Izquierdo: Vista Previa de Datos (Tabla Interactiva) --
        # Se empaqueta DESPUÉS del historial con expand=True y fill="both". 
        # Esto hace que absorba fluidamente todo el espacio horizontal restante.
        self.tree_frame = ctk.CTkFrame(self.content_frame)
        self.tree_frame.pack(side="left", expand=True, fill="both", padx=(0, 10))
        
        # --- INDICADOR DE DIMENSIONES (Status Bar) ---
        self.lbl_dimensiones = ctk.CTkLabel(
            self.main_frame, # O el frame donde esté alojada tu tabla
            text="Filas: 0 | Columnas: 0", 
            text_color="gray", 
            font=ctk.CTkFont(size=12, weight="bold")
        )
        # Lo empaquetamos abajo a la derecha
        self.lbl_dimensiones.pack(side="bottom", anchor="e", padx=20, pady=5)

        # -- Barras de Desplazamiento (Scrollbars) --
        # IMPORTANTE (Jerarquía de Empaquetado): Las barras se deben empaquetar primero 
        # hacia los bordes (derecha y abajo) para asegurar su posición. Si empaquetamos 
        # la tabla primero, esta ocuparía todo el espacio y empujaría las barras fuera de la vista.
        self.tree_scroll_y = ctk.CTkScrollbar(self.tree_frame)
        self.tree_scroll_y.pack(side="right", fill="y")
        
        self.tree_scroll_x = ctk.CTkScrollbar(self.tree_frame, orientation="horizontal")
        self.tree_scroll_x.pack(side="bottom", fill="x")

        # -- Configuración de la Tabla de Datos (Treeview) --
        # Instanciamos la tabla y la conectamos a las barras de desplazamiento.
        # selectmode="extended" permite al usuario seleccionar múltiples filas (con Shift o Ctrl).
        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll_y.set, 
                                 xscrollcommand=self.tree_scroll_x.set, selectmode="extended")
        # Se empaqueta al final para que ocupe fluidamente todo el espacio que dejaron las scrollbars
        self.tree.pack(expand=True, fill="both")

        # Completamos el "Enlace Bidireccional" (Two-way binding).
        # El Treeview avisa a la barra si el usuario hace scroll con la rueda del mouse, 
        # y la barra avisa al Treeview si el usuario arrastra el deslizador.
        self.tree_scroll_y.configure(command=self.tree.yview)
        self.tree_scroll_x.configure(command=self.tree.xview)

        # -- Inyección de Estilos (Modo Oscuro Personalizado) --
        # CustomTkinter no estiliza los widgets clásicos de 'ttk'. Por lo tanto, 
        # debemos crear un motor de estilos manual para que la tabla no desentone visualmente.
        style = ttk.Style()
        
        # IMPORTANTE: Cambiar el tema a "default" es obligatorio para que Tkinter nos permita 
        # sobrescribir los colores nativos y rígidos del sistema operativo (especialmente en Windows).
        style.theme_use("default")
        
        # 1. Colores base del cuerpo de la tabla (Fondo oscuro, texto blanco, sin bordes feos)
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, 
                        fieldbackground="#2b2b2b", borderwidth=0)
        # 2. Comportamiento Dinámico: Cambio de color al seleccionar una fila (Azul)
        style.map('Treeview', background=[('selected', '#1f538d')]) 
        
        # 3. Diseño de las Cabeceras (Nombres de las columnas)
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        # 4. Efecto "Hover" al pasar el mouse o hacer clic sobre una cabecera
        style.map("Treeview.Heading", background=[('active', '#343638')])
        
        # --- TEASERS DE PRÓXIMAS FUNCIONES (v1.1) ---
        # Botones deshabilitados para generar expectativa en el usuario
        self.btn_dividir = ctk.CTkButton(self.toolbar_frame, text="🔒 Dividir Columna", state="disabled", fg_color="transparent", border_width=1, text_color="gray")
        self.btn_dividir.pack(side="left", padx=5)

        self.btn_filtrar = ctk.CTkButton(self.toolbar_frame, text="🔒 Filtrar Datos", state="disabled", fg_color="transparent", border_width=1, text_color="gray")
        self.btn_filtrar.pack(side="left", padx=5)
        
        # Botón de información y soporte
        self.btn_acerca_de = ctk.CTkButton(self.sidebar_frame, text="ℹ️ Acerca de / Roadmap", command=self.mostrar_acerca_de, fg_color="transparent", text_color="gray", hover_color="#333333")
        self.btn_acerca_de.grid(row=10, column=0, pady=(50, 20), sticky="s")
        
    # ---- MÉTODOS DEL MOTOR (LÓGICA Y TRANSFORMACIONES) ----

    def registrar_paso(self, descripcion):
        """
        Añade una acción al historial interno y actualiza el panel derecho de la UI.
        Funciona como un 'Logger' visual para que el usuario audite la trazabilidad de sus datos.
        """
        # 1. Guardamos la descripción en la lista en memoria
        self.historial_pasos.append(descripcion)
        
        # 2. Desbloqueamos temporalmente la caja de texto para inyectar el texto mediante código
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end") # Limpiamos desde la línea 1, carácter 0, hasta el final
        
        # 3. Reescribimos todo el historial. 
        # enumerate(..., 1) es una práctica Pythonica para que el índice 'i' arranque en 1.
        for i, paso in enumerate(self.historial_pasos, 1):
            self.history_text.insert("end", f"{i}. {paso}\n\n")
            
        # 4. Volvemos a bloquear la caja para mantener el modo "Solo Lectura"
        self.history_text.configure(state="disabled")

        # 5. Lógica del botón "Deshacer"
        # El Paso 1 siempre es "Origen: archivo.csv". Si hay más de 1 paso, 
        # significa que ya se aplicó alguna transformación y habilitamos el botón.
        if len(self.historial_pasos) > 1:
            self.btn_deshacer.configure(state="normal")

    def cargar_archivo(self):
        """
        El 'Motor de Arranque' de la app. 
        Abre el explorador de archivos, lee el dataset usando Pandas según su extensión,
        e inyecta los datos en la memoria del programa (self.df).
        Además, realiza la transición visual ocultando el mensaje de bienvenida 
        y revelando las herramientas de trabajo.
        """
        # 1. Diálogo del Sistema Operativo para elegir el archivo
        file_path = filedialog.askopenfilename(
            title="Seleccionar Dataset", 
            filetypes=[("Archivos de datos", "*.csv *.xlsx *.xls"), ("Todos los archivos", "*.*")]
        )

        # Si el usuario selecciona un archivo (y no cancela la ventana)
        if file_path:
            try:
                # 2. Lógica de Ingesta de Datos (Pandas)
                extension = os.path.splitext(file_path)[1].lower()
                if extension == '.csv':
                    self.df = pd.read_csv(file_path)
                else:
                    self.df = pd.read_excel(file_path) # Cubre tanto .xls como .xlsx

                # 3. Reseteo del Estado Interno
                # Limpiamos memorias previas por si el usuario carga un 2do archivo sin reiniciar la app
                self.historial_pasos = []
                self.df_history = []
                self.btn_deshacer.configure(state="disabled")

                # 4. Transición de la Interfaz Gráfica (UI/UX)
                self.welcome_label.pack_forget() # Ocultamos el placeholder de bienvenida
                
                # Desplegamos la barra superior y el contenedor de la tabla
                self.toolbar_frame.pack(fill="x", padx=20, pady=(10, 0)) 
                self.content_frame.pack(expand=True, fill="both", padx=20, pady=20)
                
                # 5. Habilitación de Funciones Secundarias
                self.btn_transformar.configure(state="normal")
                self.btn_exportar.configure(state="normal")
                
                # 6. Disparadores Finales
                self.actualizar_vista_previa() # Renderizamos la tabla con los datos
                
                # Registramos el origen de los datos como el "Paso 1"
                nombre_archivo = os.path.basename(file_path)
                self.registrar_paso(f"Origen: {nombre_archivo}")
                
            except Exception as e:
                # 7. Manejo de Errores a prueba de fallos
                # Si el archivo está corrupto o tiene otro formato, evitamos que la app "crashee"
                # y le devolvemos un mensaje visual al usuario.
                self.welcome_label.pack(expand=True)
                self.welcome_label.configure(text=f"❌ Error al cargar:\n{str(e)}", text_color="red")

    def actualizar_vista_previa(self):
        """
        Renderiza una muestra de los datos actuales en el Treeview (Tabla Visual).
        Se ejecuta automáticamente al cargar el archivo y después de cada transformación 
        para dar feedback visual en tiempo real al usuario.
        """
        # 1. Limpieza del Lienzo (Reset Visual)
        # get_children() obtiene los IDs de todas las filas actuales y delete() las borra.
        # Esto evita que los datos nuevos se sumen por debajo de los viejos.
        self.tree.delete(*self.tree.get_children())

        if self.df is not None:
            # 2. Muestreo de Datos (Optimización de Performance)
            # Extraemos solo las primeras 15 filas. Intentar renderizar miles de filas 
            # de golpe congelaría el hilo principal de la interfaz gráfica (Tkinter).
            df_preview = self.df.head(200)

            # 3. Construcción Dinámica de Columnas
            # Inyectamos los nombres de las columnas del DataFrame como cabeceras del Treeview.
            self.tree["column"] = list(df_preview.columns)
            
            # "show='headings'" oculta una columna fantasma vacía que Tkinter pone a la izquierda por defecto
            self.tree["show"] = "headings" 

            for col in self.tree["column"]:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120, anchor="center") # Ancho base de 120px y texto centrado

            # 4. Inserción de Datos (Filas)
            # Reemplazamos los valores nulos nativos de Pandas (NaN) por cadenas vacías ("").
            # Esto evita que el usuario vea la palabra 'NaN' repetida en la tabla, mejorando la estética.
            df_preview_filled = df_preview.fillna("") 
            
            # Iteramos fila por fila y la insertamos al final ("end") de la tabla
            for index, row in df_preview_filled.iterrows():
                self.tree.insert("", "end", values=list(row))
                
        # Actualizar el contador de dimensiones en la interfaz
        if hasattr(self, 'df') and self.df is not None:
            filas, columnas = self.df.shape
            self.lbl_dimensiones.configure(text=f"Filas: {filas} | Columnas: {columnas}")
    

    def deshacer_paso(self):
        """
        Revierte la última transformación aplicada al DataFrame.
        Funciona operando las listas de historial como una 'Pila' (Stack - LIFO), 
        extrayendo (pop) el último estado guardado en memoria y restaurándolo.
        """
        # Verificamos que haya copias de seguridad en df_history y 
        # que el historial de texto tenga más de 1 paso (el Paso 1 es intocable: el Origen)
        if self.df_history and len(self.historial_pasos) > 1:
            
            # 1. Reversión de los datos en memoria (Rollback)
            # .pop() saca el último elemento de la lista y lo asigna como el DataFrame activo
            self.df = self.df_history.pop() 
            
            # 2. Reversión del registro visual (borramos el último renglón)
            self.historial_pasos.pop()
            
            # 3. Re-dibujado de la caja de texto (Historial UI)
            self.history_text.configure(state="normal")
            self.history_text.delete("1.0", "end")
            
            for i, paso in enumerate(self.historial_pasos, 1):
                self.history_text.insert("end", f"{i}. {paso}\n\n")
                
            self.history_text.configure(state="disabled")
            
            # 4. Refrescar la tabla interactiva con los datos restaurados
            self.actualizar_vista_previa()
            
            # 5. Bloqueo de seguridad del botón
            # Si al deshacer volvimos al estado original (Paso 1), apagamos el botón "Deshacer"
            if len(self.historial_pasos) == 1:
                self.btn_deshacer.configure(state="disabled")

    def eliminar_duplicados(self):
        """
        Elimina las filas que sean copias exactas dentro del DataFrame activo.
        Guarda una instantánea del estado previo para permitir deshacer la acción,
        y calcula métricas de impacto (cuántas filas se borraron) para el historial.
        """
        if self.df is not None:
            # 1. Punto de Guardado (Savepoint)
            # Usamos .copy() para crear un clon exacto en memoria. Es vital para 
            # aislar el historial de la mutabilidad nativa de los DataFrames de Pandas.
            self.df_history.append(self.df.copy()) 
            
            # 2. Captura de métrica inicial
            antes = len(self.df)
            
            # 3. Transformación (Motor Pandas)
            # drop_duplicates() elimina las filas donde TODOS los valores coinciden con otra.
            self.df = self.df.drop_duplicates()
            
            # 4. Cálculo de impacto
            despues = len(self.df)
            filas_eliminadas = antes - despues
            
            # 5. Registro (Logger) y actualización visual
            if filas_eliminadas > 0:
                self.registrar_paso(f"Se eliminaron {filas_eliminadas} filas duplicadas")
            else:
                self.registrar_paso("Eliminar duplicados (0 filas)")
                
            self.actualizar_vista_previa()

    def limpiar_nulos(self):
        """
        Abre un cuadro de diálogo para que el usuario elija la agresividad de la limpieza.
        Opción A: Borrar solo si TODA la fila está vacía (how='all').
        Opción B: Borrar si falta AL MENOS UN dato (how='any').
        """
        if self.df is None:
            return

        # 1. Interfaz de Usuario (Ventana Modal)
        dialog = ctk.CTkToplevel(self)
        dialog.title("Opciones de Limpieza")
        dialog.geometry("350x220")
        dialog.transient(self)
        dialog.grab_set() # Bloquea la app principal

        ctk.CTkLabel(dialog, text="¿Qué filas deseas eliminar?", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(20, 10))

        # 2. Función interna que ejecuta la limpieza según la opción elegida
        def ejecutar_limpieza(modo):
            # Guardamos historial y capturamos métrica inicial
            self.df_history.append(self.df.copy())
            antes = len(self.df)

            # Ejecutamos el motor de Pandas con el modo seleccionado ('all' o 'any')
            self.df = self.df.dropna(how=modo)

            # Calculamos el impacto
            despues = len(self.df)
            filas_eliminadas = antes - despues
            
            # Texto dinámico para el historial según la decisión
            tipo_texto = "completamente vacías" if modo == 'all' else "con datos faltantes"
            
            # Registro visual
            if filas_eliminadas > 0:
                self.registrar_paso(f"Se eliminaron {filas_eliminadas} filas {tipo_texto}")
            else:
                self.registrar_paso(f"Limpieza de nulos (0 filas {tipo_texto})")

            # Actualizamos la tabla, el contador y cerramos la ventana
            self.actualizar_vista_previa()
            dialog.destroy()

        # 3. Botones de opciones para el usuario
        btn_all = ctk.CTkButton(dialog, text="Solo filas COMPLETAMENTE vacías", 
                                command=lambda: ejecutar_limpieza('all'), fg_color="#2980b9", hover_color="#1f618d")
        btn_all.pack(pady=10, padx=20, fill="x")

        btn_any = ctk.CTkButton(dialog, text="Filas con ALGÚN dato faltante", 
                                command=lambda: ejecutar_limpieza('any'), fg_color="#c0392b", hover_color="#922b21")
        btn_any.pack(pady=10, padx=20, fill="x")

    def eliminar_columna(self):
        """
        Elimina una columna completa del DataFrame activo.
        Utiliza un cuadro de diálogo (Input Dialog) para interactuar con el usuario 
        y cuenta con validación de existencia para prevenir errores de tipo 'KeyError' en Pandas.
        """
        if self.df is not None:
            # 1. Interfaz de Captura de Datos (Usuario)
            # Desplegamos un popup nativo de CustomTkinter pidiendo el nombre de la columna.
            dialog = ctk.CTkInputDialog(text="Escribe el nombre EXACTO de la columna a eliminar:", title="Eliminar Columna")
            col_name = dialog.get_input()
            
            # 2. Validación de Seguridad
            # Verificamos dos cosas: que el usuario no haya presionado "Cancelar" (col_name no esté vacío)
            # y que el nombre escrito coincida exactamente con una columna existente en memoria.
            if col_name and col_name in self.df.columns:
                
                # 3. Punto de Guardado (Savepoint)
                self.df_history.append(self.df.copy())
                
                # 4. Transformación (Motor Pandas)
                self.df = self.df.drop(columns=[col_name])
                
                # 5. Registro (Logger) y actualización visual
                self.registrar_paso(f"Columna eliminada: '{col_name}'")
                self.actualizar_vista_previa()
                
            elif col_name:
                # 6. Manejo de Errores Leves
                # Si escribió algo pero no existe (ej. error de tipeo o mayúsculas).
                # Nota técnica: Por ahora sale por consola, a futuro se podría cambiar por una alerta visual.
                print(f"La columna '{col_name}' no existe. Revisa espacios o mayúsculas.")

    def renombrar_columna(self):
        """
        Modifica el nombre de una columna existente en el DataFrame activo.
        Implementa un flujo interactivo de dos pasos (Two-Step Wizard) mediante cuadros de diálogo,
        validando la existencia de la columna original antes de solicitar el nuevo nombre.
        """
        if self.df is not None:
            # 1. Captura y validación del nombre original (Paso 1)
            dialog_old = ctk.CTkInputDialog(text="Nombre ACTUAL de la columna:", title="Renombrar Columna (Paso 1/2)")
            old_name = dialog_old.get_input()
            
            # Verificamos que el input no esté vacío y que la columna realmente exista en memoria
            if old_name and old_name in self.df.columns:
                
                # 2. Captura del nuevo nombre (Paso 2)
                # La f-string mejora la UX mostrándole al usuario qué columna está por modificar
                dialog_new = ctk.CTkInputDialog(text=f"NUEVO nombre para '{old_name}':", title="Renombrar Columna (Paso 2/2)")
                new_name = dialog_new.get_input()
                
                # Verificamos que el usuario haya escrito algo y no haya presionado "Cancelar"
                if new_name:
                    
                    # 3. Punto de Guardado (Savepoint)
                    self.df_history.append(self.df.copy())
                    
                    # 4. Transformación (Motor Pandas)
                    # El método rename exige un diccionario con el mapeo {nombre_viejo: nombre_nuevo}
                    self.df = self.df.rename(columns={old_name: new_name})
                    
                    # 5. Registro (Logger) y actualización visual
                    self.registrar_paso(f"Columna renombrada: '{old_name}' ➔ '{new_name}'")
                    self.actualizar_vista_previa()
                    
            elif old_name:
                # 6. Manejo de Errores Leves (Fallo en la validación del Paso 1)
                print(f"La columna '{old_name}' no existe. Revisa espacios o mayúsculas.")


    def calcular_columna(self):
        """
        Crea una nueva columna resultante de aplicar una operación matemática (+, -, *, /)
        entre dos columnas existentes. 
        Incluye un 'Smart Parser' para limpiar formatos de moneda y convertir textos a números.
        """
        if self.df is not None:
            # 1. Interfaz de Usuario (Ventana Modal)
            # CTkToplevel crea una ventana secundaria flotante.
            dialog = ctk.CTkToplevel(self)
            dialog.title("Nueva Columna Calculada")
            dialog.geometry("400x380")
            dialog.attributes("-topmost", True) # Fuerza a la ventana a estar siempre al frente
            
            # grab_set() bloquea la ventana principal hasta que el usuario cierre esta ventana secundaria.
            # Es vital para evitar que el usuario borre una columna en el fondo mientras intenta sumarla acá.
            dialog.grab_set() 

            # Obtenemos las opciones disponibles dinámicamente de los datos cargados
            columnas_actuales = list(self.df.columns)

            # -- Construcción del Formulario --
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

            # Contenedor dinámico para mostrar errores en rojo sin usar prints de consola
            error_label = ctk.CTkLabel(dialog, text="", text_color="#e74c3c", font=ctk.CTkFont(weight="bold"))
            error_label.pack(pady=(0, 5))

            # 2. Función Anidada de Ejecución
            def aplicar_calculo():
                error_label.configure(text="") # Limpia errores de intentos anteriores
                
                # Capturamos los valores del formulario
                c1 = col1_combo.get()
                op = op_combo.get()
                c2 = col2_combo.get()
                new_col = new_col_entry.get()

                # -- Validaciones de Seguridad --
                if not new_col:
                    error_label.configure(text="⚠️ Ingresa un nombre para la columna.")
                    return
                if new_col in self.df.columns:
                    error_label.configure(text=f"⚠️ La columna '{new_col}' ya existe.")
                    return
                
                try:
                    # Savepoint
                    self.df_history.append(self.df.copy())
                    
                    # --- SMART PARSER ---
                    # Los Excels suelen traer números con formato (ej: "$ 1,500.00"). Pandas los lee como texto.
                    # Esta sub-función limpia los caracteres sucios y fuerza la conversión a número (float/int).
                    def limpiar_y_convertir(serie):
                        # Convertimos a string, borramos '$' y comas, y quitamos espacios en los bordes.
                        serie_limpia = serie.astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
                        # to_numeric con 'coerce' convierte los valores rebeldes en NaN en lugar de crashear.
                        return pd.to_numeric(serie_limpia, errors='coerce')

                    # Extraemos las series (columnas) y las pasamos por el filtro limpiador
                    s1 = limpiar_y_convertir(self.df[c1])
                    s2 = limpiar_y_convertir(self.df[c2])
                    # --------------------

                    # -- Ejecución del Motor Pandas --
                    if op == "+": self.df[new_col] = s1 + s2
                    elif op == "-": self.df[new_col] = s1 - s2
                    elif op == "*": self.df[new_col] = s1 * s2
                    elif op == "/": self.df[new_col] = s1 / s2

                    # -- Cierre y Registro --
                    self.registrar_paso(f"Cálculo: '{new_col}' = '{c1}' {op} '{c2}'")
                    self.actualizar_vista_previa()
                    dialog.destroy() # Cerramos la ventana modal tras el éxito
                    
                except Exception as e:
                    # Rollback silencioso si falla algo matemático profundo (ej: división por cero no atajada)
                    print(f"Error en el cálculo: {e}")
                    self.df_history.pop()

            # Botón disparador dentro de la ventana modal
            btn_aplicar = ctk.CTkButton(dialog, text="Aplicar Cálculo", command=aplicar_calculo, fg_color="#27ae60", hover_color="#2ecc71")
            btn_aplicar.pack(pady=20)
                    
    def combinar_columnas(self):
        """
        Concatena el contenido de dos columnas en una sola, utilizando un separador elegido por el usuario.
        Fuerza la conversión a texto (str) para evitar errores de tipo si se mezclan números y letras,
        y cuenta con un filtro para limpiar los artefactos de 'NaN' que Pandas genera al convertir nulos a texto.
        """
        if self.df is not None:
            # 1. Interfaz de Usuario (Ventana Modal)
            dialog = ctk.CTkToplevel(self)
            dialog.title("Combinar Columnas de Texto")
            dialog.geometry("400x410")
            dialog.attributes("-topmost", True)
            dialog.grab_set() # Bloquea interacción con la ventana principal

            columnas_actuales = list(self.df.columns)

            # -- Construcción del Formulario --
            ctk.CTkLabel(dialog, text="Selecciona la Columna 1:").pack(pady=(10, 0))
            col1_combo = ctk.CTkComboBox(dialog, values=columnas_actuales)
            col1_combo.pack(pady=5)

            ctk.CTkLabel(dialog, text="Separador:").pack(pady=(5, 0))
            # Ofrecemos los separadores más comunes en limpieza de datos
            sep_combo = ctk.CTkComboBox(dialog, values=["Espacio", "Guion (-)", "Coma (,)", "Sin separador"])
            sep_combo.pack(pady=5)

            ctk.CTkLabel(dialog, text="Selecciona la Columna 2:").pack(pady=(5, 0))
            col2_combo = ctk.CTkComboBox(dialog, values=columnas_actuales)
            col2_combo.pack(pady=5)

            ctk.CTkLabel(dialog, text="Nombre de la Nueva Columna:").pack(pady=(5, 0))
            new_col_entry = ctk.CTkEntry(dialog, placeholder_text="Ej: Producto_Cliente")
            new_col_entry.pack(pady=5)

            error_label = ctk.CTkLabel(dialog, text="", text_color="#e74c3c", font=ctk.CTkFont(weight="bold"))
            error_label.pack(pady=(0, 5))

            # 2. Función Anidada de Ejecución
            def aplicar_combinacion():
                error_label.configure(text="") # Reset de mensajes de error
                
                # Captura de datos del formulario
                c1 = col1_combo.get()
                sep_texto = sep_combo.get()
                c2 = col2_combo.get()
                new_col = new_col_entry.get()

                # -- Validaciones de Seguridad --
                if not new_col:
                    error_label.configure(text="⚠️ Ingresa un nombre para la columna.")
                    return
                if new_col in self.df.columns:
                    error_label.configure(text=f"⚠️ La columna '{new_col}' ya existe.")
                    return
                
                # -- Traductor de Separadores --
                # Mapea la selección amigable del usuario al string literal que usará Pandas
                if sep_texto == "Espacio": separador = " "
                elif sep_texto == "Guion (-)": separador = " - "
                elif sep_texto == "Coma (,)": separador = ", "
                else: separador = ""

                try:
                    # Savepoint
                    self.df_history.append(self.df.copy())
                    
                    # -- Ejecución del Motor Pandas --
                    # 1. Fuerza la conversión de ambas columnas a String y las concatena con el separador.
                    self.df[new_col] = self.df[c1].astype(str) + separador + self.df[c2].astype(str)

                    # 2. Limpieza de Artefactos ('nan')
                    # Si había celdas vacías, al hacer .astype(str), Pandas inyecta la palabra literal "nan".
                    # La borramos y luego usamos .str.strip(separador) para limpiar si quedó un guion/coma suelto en los bordes.
                    self.df[new_col] = self.df[new_col].str.replace('nan', '', case=False).str.strip(separador)

                    # -- Cierre y Registro --
                    self.registrar_paso(f"Combinar: '{c1}' y '{c2}' ➔ '{new_col}'")
                    self.actualizar_vista_previa()
                    dialog.destroy()
                    
                except Exception as e:
                    print(f"Error al combinar: {e}")
                    self.df_history.pop() # Rollback silencioso

            # Botón disparador dentro de la ventana modal
            btn_aplicar = ctk.CTkButton(dialog, text="Aplicar Combinación", command=aplicar_combinacion, fg_color="#27ae60", hover_color="#2ecc71")
            btn_aplicar.pack(pady=20)
            
    # ---- INTEGRACIÓN DE DATOS (Merge / JOIN) ----

    def unir_datasets(self):
        """
        Permite fusionar el DataFrame activo con un segundo dataset (Tabla Dimensional).
        Despliega una interfaz avanzada con vista previa independiente para el segundo archivo
        y opciones para configurar el tipo de cruce (Left Join, Inner Join, etc.).
        """
        if self.df is not None:
            # 1. Configuración de la Ventana Modal Avanzada
            dialog = ctk.CTkToplevel(self)
            dialog.title("Unir Datasets (Merge / JOIN)")
            dialog.geometry("650x650") # 📏 Ventana más grande para acomodar la mini-tabla
            
            # transient() vincula esta ventana a la principal: si se minimiza la app, esta ventana también.
            dialog.transient(self)
            # grab_set() bloquea la app principal para evitar modificaciones de datos en segundo plano.
            dialog.grab_set()

            # Variable temporal para almacenar el segundo dataset en memoria sin pisar el principal
            self.df2 = None

            # -- Sección 1: Carga de Datos Dimensionales --
            ctk.CTkLabel(dialog, text="1. Cargar Segundo Dataset (Tabla Dimensional)", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(15, 5))
            
            lbl_df2_info = ctk.CTkLabel(dialog, text="Ningún archivo cargado", text_color="gray")
            
            btn_cargar_df2 = ctk.CTkButton(dialog, text="📁 Buscar Archivo 2", fg_color="#8e44ad", hover_color="#732d91")
            btn_cargar_df2.pack(pady=5)
            lbl_df2_info.pack(pady=5)

            # -- Sección 2: Mini Vista Previa (Dataset 2) --
            # Contenedor dedicado con altura fija para no deformar el resto del formulario
            preview_frame = ctk.CTkFrame(dialog, height=120)
            preview_frame.pack(fill="x", padx=20, pady=5)
            
            # Scrollbars bidireccionales de la mini-tabla
            tree_scroll_y2 = ctk.CTkScrollbar(preview_frame)
            tree_scroll_y2.pack(side="right", fill="y")
            tree_scroll_x2 = ctk.CTkScrollbar(preview_frame, orientation="horizontal")
            tree_scroll_x2.pack(side="bottom", fill="x")

            # Mini-tabla (Treeview) con altura reducida (height=4).
            # selectmode="none" impide que el usuario seleccione filas (es solo de lectura visual).
            tree2 = ttk.Treeview(preview_frame, height=4, yscrollcommand=tree_scroll_y2.set, xscrollcommand=tree_scroll_x2.set, selectmode="none")
            tree2.pack(expand=True, fill="both")
            
            tree_scroll_y2.configure(command=tree2.yview)
            tree_scroll_x2.configure(command=tree2.xview)

            # -- Sección 3: Contenedor de Opciones de Cruce --
            # Frame transparente que agrupará los selectores de columnas y tipo de JOIN (se llena más adelante)
            opciones_frame = ctk.CTkFrame(dialog, fg_color="transparent")

            # -- Función Anidada: Carga y Pre-visualización del Dataset 2 --
            def cargar_df2():
                """
                Abre el explorador de archivos para ingerir la Tabla Dimensional.
                Inyecta una muestra de 5 filas en la mini-tabla y revela dinámicamente
                las opciones de configuración del JOIN si la carga es exitosa.
                """
                file_path = filedialog.askopenfilename(title="Seleccionar Dataset 2", filetypes=[("Archivos de datos", "*.csv *.xlsx *.xls")])
                
                if file_path:
                    try:
                        # 1. Ingesta a memoria secundaria (self.df2)
                        ext = os.path.splitext(file_path)[1].lower()
                        if ext == '.csv':
                            self.df2 = pd.read_csv(file_path)
                        else:
                            self.df2 = pd.read_excel(file_path)
                        
                        # 2. Feedback visual (Metadatos del archivo)
                        nombre = os.path.basename(file_path)
                        lbl_df2_info.configure(text=f"✅ Archivo listo: {nombre} ({len(self.df2.columns)} columnas)", text_color="#27ae60")
                        
                        # 3. Renderizado de la Mini-Tabla (Vista Previa)
                        tree2.delete(*tree2.get_children()) # Limpiamos si el usuario subió otro archivo antes
                        
                        # Tomamos 5 filas y limpiamos los NaNs visuales
                        df_preview = self.df2.head(5).fillna("") 
                        
                        tree2["column"] = list(df_preview.columns)
                        tree2["show"] = "headings"
                        
                        for col in tree2["column"]:
                            tree2.heading(col, text=col)
                            tree2.column(col, width=100, anchor="center")
                            
                        for index, row in df_preview.iterrows():
                            tree2.insert("", "end", values=list(row))

                        # 4. Enlace Dinámico de Datos (Data Binding)
                        # Inyectamos las columnas recién descubiertas en el selector del formulario
                        col2_combo.configure(values=list(self.df2.columns))
                        col2_combo.set(list(self.df2.columns)[0]) # Dejamos la primera columna seleccionada por defecto
                        
                        # 5. Revelación Progresiva de la Interfaz (UX)
                        # El contenedor de opciones de JOIN estaba oculto en memoria. Ahora lo mostramos.
                        opciones_frame.pack(fill="both", expand=True, padx=20, pady=10)
                        
                    except Exception as e:
                        # Captura de errores amigable sin romper la aplicación principal
                        lbl_df2_info.configure(text=f"❌ Error al cargar: {str(e)}", text_color="red")
            
            # Conectamos el botón físico con la función lógica que acabamos de definir
            btn_cargar_df2.configure(command=cargar_df2)

            # -- Sección 4: Formulario de Configuración del Cruce (JOIN) --
            # Este frame (opciones_frame) se mantiene oculto hasta que la función cargar_df2() lo invoca.
            ctk.CTkLabel(opciones_frame, text="2. Configurar el Cruce (JOIN)", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(15, 10))

            # Selector de la Llave Primaria (Primary Key) del Dataset original
            ctk.CTkLabel(opciones_frame, text="Llave en Dataset Principal:").pack(pady=(5, 0))
            col1_combo = ctk.CTkComboBox(opciones_frame, values=list(self.df.columns))
            col1_combo.pack(pady=5)

            # Selector de la Llave Foránea (Foreign Key) del Dataset secundario
            # Excelente UX: Inicia con un texto de marcador de posición (placeholder) 
            # hasta que cargar_df2() reemplace este valor con las columnas reales.
            ctk.CTkLabel(opciones_frame, text="Llave en Dataset 2:").pack(pady=(5, 0))
            col2_combo = ctk.CTkComboBox(opciones_frame, values=["Esperando archivo..."])
            col2_combo.pack(pady=5)

            # Selector del Comportamiento del Motor de Cruce
            # - Left Join: Mantiene intacto el Dataset 1 y le "pega" las coincidencias del 2.
            # - Inner Join: Filtra y mantiene SOLO las filas donde las llaves coinciden en AMBOS datasets.
            ctk.CTkLabel(opciones_frame, text="Tipo de Unión (JOIN):").pack(pady=(5, 0))
            tipo_combo = ctk.CTkComboBox(opciones_frame, values=["Izquierda (Left Join)", "Interna (Inner Join)"])
            tipo_combo.pack(pady=5)

            # Etiqueta dinámica para atajar errores matemáticos o de tipo de datos
            error_label = ctk.CTkLabel(opciones_frame, text="", text_color="#e74c3c", font=ctk.CTkFont(weight="bold"))
            error_label.pack(pady=(10, 5))

            # -- Función Anidada: Ejecución del Motor Relacional --
            def aplicar_union():
                """
                Captura la configuración del usuario y ejecuta un pd.merge() 
                para cruzar ambos DataFrames. Atrapa errores comunes como 
                la incompatibilidad de tipos de datos (dtypes) entre las llaves.
                """
                error_label.configure(text="") # Limpieza de errores previos

                # Validación de seguridad: evitar que el usuario aplique sin cargar el archivo
                if self.df2 is None:
                    error_label.configure(text="⚠️ Primero debes cargar el Dataset 2.")
                    return
                
                # Captura de parámetros
                k1 = col1_combo.get()
                k2 = col2_combo.get()
                tipo_str = tipo_combo.get()
                
                # Traducción semántica para el motor de Pandas
                how_join = "left" if "Left" in tipo_str else "inner"

                try:
                    # 1. Punto de Guardado (Savepoint)
                    self.df_history.append(self.df.copy()) 
                    
                    # 2. Transformación Core (Álgebra Relacional con Pandas)
                    # pd.merge es el equivalente exacto a un JOIN de SQL. 
                    # left_on y right_on permiten cruzar tablas aunque las columnas clave se llamen distinto.
                    self.df = pd.merge(self.df, self.df2, left_on=k1, right_on=k2, how=how_join)
                    
                    # 3. Registro (Logger) y actualización visual
                    self.registrar_paso(f"Unión ({how_join}): usando '{k1}' = '{k2}'")
                    self.actualizar_vista_previa()
                    
                    # 4. Cierre exitoso
                    dialog.destroy()
                    
                except Exception as e:
                    # 5. Manejo de Errores Críticos (Rollback)
                    # Si el merge falla (ej: int vs str), mostramos alerta en UI y hacemos rollback del savepoint.
                    error_label.configure(text="⚠️ Error. Revisa que las llaves tengan el mismo tipo de dato.")
                    print(f"Error Merge: {e}")
                    self.df_history.pop() 

            # -- Botón Disparador Final --
            btn_aplicar = ctk.CTkButton(opciones_frame, text="Aplicar Unión", command=aplicar_union, fg_color="#27ae60", hover_color="#2ecc71")
            btn_aplicar.pack(pady=15)
            
    # ---- EXPORTACIÓN DE DATOS (Fase de Carga / Load) ----

    def exportar_datos(self):
        """
        Finaliza el proceso ETL permitiendo al usuario guardar el DataFrame 
        resultante y limpio en su disco local.
        Ofrece una interfaz para seleccionar entre múltiples formatos de salida 
        industriales (CSV, Excel, bases de datos SQLite).
        """
        # Validación temprana: Corta la ejecución si el usuario logró hacer clic 
        # en el botón sin tener un DataFrame activo en memoria.
        if self.df is None:
            return

        # 1. Configuración de la Ventana Modal de Exportación
        dialog = ctk.CTkToplevel(self)
        dialog.title("Exportar Datos")
        dialog.geometry("400x300")
        
        # Escudos de Interfaz (UX)
        dialog.transient(self) # Ancla esta ventana a la app principal
        dialog.grab_set()      # Bloquea la app de fondo para evitar alteraciones de última hora

        # 2. Interfaz de Selección de Formato
        ctk.CTkLabel(dialog, text="💾 Seleccionar formato de exportación", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(20, 10))

        # Menú desplegable con los tres formatos más utilizados en Data Science
        formato_combo = ctk.CTkComboBox(dialog, values=["Archivo CSV (.csv)", "Archivo Excel (.xlsx)", "Base de Datos SQLite (.db)"])
        formato_combo.pack(pady=10)

        # Etiqueta dinámica para el manejo de excepciones de I/O (Input/Output)
        # Fundamental para atajar errores como "Permiso Denegado" o "Archivo abierto en otro programa"
        error_label = ctk.CTkLabel(dialog, text="", text_color="#e74c3c", font=ctk.CTkFont(weight="bold"))
        error_label.pack(pady=5)

        # -- Función Anidada: Motor de Exportación (I/O) --
        def guardar():
                """
                Ejecuta la escritura física del archivo en el disco local.
                Traduce el formato seleccionado en la UI a la función de exportación
                correspondiente de Pandas (to_csv, to_excel, to_sql).
                """
                formato = formato_combo.get()
                
                try:
                    # 1. Exportación a Texto Plano (CSV)
                    if "CSV" in formato:
                        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivo CSV", "*.csv")])
                        if file_path:
                            # index=False es vital para no exportar la numeración de filas de Pandas
                            self.df.to_csv(file_path, index=False)
                            self.registrar_paso(f"💾 Exportado a CSV: {os.path.basename(file_path)}")
                            dialog.destroy()
                            
                    # 2. Exportación a Planilla de Cálculo (Excel)
                    elif "Excel" in formato:
                        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivo Excel", "*.xlsx")])
                        if file_path:
                            self.df.to_excel(file_path, index=False)
                            self.registrar_paso(f"💾 Exportado a Excel: {os.path.basename(file_path)}")
                            dialog.destroy()
                            
                    # 3. Exportación a Base de Datos Relacional (SQLite)
                    elif "SQLite" in formato:
                        file_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Base de Datos SQLite", "*.db")])
                        if file_path:
                            import sqlite3
                            # Conecta al archivo .db (o lo crea automáticamente si no existe)
                            conn = sqlite3.connect(file_path)
                            
                            # Magia de Pandas: Crea la tabla "datos_limpios", infiere los tipos de datos 
                            # (VARCHAR, INTEGER, etc.) y hace el INSERT de todas las filas.
                            self.df.to_sql("datos_limpios", conn, if_exists="replace", index=False)
                            conn.close()
                            
                            self.registrar_paso(f"💾 Exportado a SQLite: {os.path.basename(file_path)}")
                            dialog.destroy()
                            
                except Exception as e:
                    # Atrapa errores clásicos del sistema operativo, como intentar 
                    # sobrescribir un Excel que el usuario tiene abierto en otra pantalla.
                    error_label.configure(text=f"⚠️ Error al guardar. Revisa la consola.")
                    print(f"Error Export: {e}")

        # -- Botón Disparador de Exportación --
        btn_guardar = ctk.CTkButton(dialog, text="Guardar Como...", command=guardar, fg_color="#2980b9", hover_color="#1f618d")
        btn_guardar.pack(pady=15)
        
    def mostrar_acerca_de(self):
        """
        Ventana informativa que muestra la versión actual, el cumplimiento 
        de licencias Open Source y el Roadmap de futuras actualizaciones.
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Acerca de QueryLibre")
        dialog.geometry("400x520") 
        dialog.transient(self)
        dialog.grab_set()

        # --- Cabecera ---
        ctk.CTkLabel(dialog, text="QueryLibre v1.1", font=ctk.CTkFont(weight="bold", size=20)).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="Motor de Transformación de Datos", text_color="gray").pack(pady=(0, 15))

        # --- Sección Legal / Open Source ---
        ctk.CTkLabel(dialog, text="📜 Licencias y Herramientas:", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(10, 5))
        
        legal_text = (
            "Este software se distribuye bajo la Licencia MIT.\n"
            "Construido con orgullo utilizando:\n\n"
            "• Python (Python Software Foundation License)\n"
            "• Pandas (BSD 3-Clause License)\n"
            "• CustomTkinter (MIT License)\n"
            "• SQLite (Public Domain)"
        )
        ctk.CTkLabel(dialog, text=legal_text, text_color="gray", justify="center").pack(pady=(0, 15))

        # --- Sección de Expectativa (Roadmap) ---
        ctk.CTkLabel(dialog, text="🚀 Próximamente (v1.2+):", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(10, 5))

        funciones_futuras = [
            "✂️ Dividir Columna (Split)",
            "🔍 Buscar y Reemplazar",
            "🚦 Filtrado Condicional",
            "🔠 Cambiar Tipo de Dato",
            "📦 Agrupar y Resumir"
        ]

        for func in funciones_futuras:
            ctk.CTkLabel(dialog, text=func, anchor="w").pack(fill="x", padx=90, pady=2)

        # --- Pie de página y Apoyo ---
        ctk.CTkLabel(dialog, text="Desarrollado por Iván Tomás Ravarotto", font=ctk.CTkFont(size=11), text_color="gray").pack(side="bottom", pady=(0, 10))

        # Botón para cerrar
        ctk.CTkButton(dialog, text="¡Entendido!", command=dialog.destroy, fg_color="#2980b9", hover_color="#1f618d").pack(side="bottom", pady=15)

# ---- PUNTO DE ENTRADA (MAIN) ----

if __name__ == "__main__":
    # Instanciamos y arrancamos el bucle principal (Event Loop) de la interfaz gráfica
    app = QueryLibreApp()
    app.mainloop()
    