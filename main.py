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
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text="QueryLibre v1.0.0", font=ctk.CTkFont(size=11), text_color="gray")
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
            df_preview = self.df.head(15)

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
        if self.df is not None:
            self.df_history.append(self.df.copy()) 
            antes = len(self.df)
            self.df = self.df.drop_duplicates()
            despues = len(self.df)
            filas_eliminadas = antes - despues
            
            if filas_eliminadas > 0:
                self.registrar_paso(f"Se eliminaron {filas_eliminadas} filas duplicadas")
            else:
                self.registrar_paso("Eliminar duplicados (0 filas)")
            self.actualizar_vista_previa()

    def limpiar_nulos(self):
        if self.df is not None:
            self.df_history.append(self.df.copy())
            antes = len(self.df)
            self.df = self.df.dropna()
            despues = len(self.df)
            filas_eliminadas = antes - despues
            
            if filas_eliminadas > 0:
                self.registrar_paso(f"Se eliminaron {filas_eliminadas} filas con nulos")
            else:
                self.registrar_paso("Limpiar nulos (0 filas)")
            self.actualizar_vista_previa()

    def eliminar_columna(self):
        if self.df is not None:
            dialog = ctk.CTkInputDialog(text="Escribe el nombre EXACTO de la columna a eliminar:", title="Eliminar Columna")
            col_name = dialog.get_input()
            
            if col_name and col_name in self.df.columns:
                self.df_history.append(self.df.copy())
                self.df = self.df.drop(columns=[col_name])
                self.registrar_paso(f"Columna eliminada: '{col_name}'")
                self.actualizar_vista_previa()
            elif col_name:
                print(f"La columna '{col_name}' no existe. Revisa espacios o mayúsculas.")

    def renombrar_columna(self):
        if self.df is not None:
            dialog_old = ctk.CTkInputDialog(text="Nombre ACTUAL de la columna:", title="Renombrar Columna (Paso 1/2)")
            old_name = dialog_old.get_input()
            
            if old_name and old_name in self.df.columns:
                dialog_new = ctk.CTkInputDialog(text=f"NUEVO nombre para '{old_name}':", title="Renombrar Columna (Paso 2/2)")
                new_name = dialog_new.get_input()
                
                if new_name:
                    self.df_history.append(self.df.copy())
                    self.df = self.df.rename(columns={old_name: new_name})
                    self.registrar_paso(f"Columna renombrada: '{old_name}' ➔ '{new_name}'")
                    self.actualizar_vista_previa()
            elif old_name:
                print(f"La columna '{old_name}' no existe. Revisa espacios o mayúsculas.")

    # ---- NUEVA FUNCIÓN FASE 7: CALCULADORA ----
    def calcular_columna(self):
        if self.df is not None:
            # 1. Creamos la ventana emergente
            dialog = ctk.CTkToplevel(self)
            dialog.title("Nueva Columna Calculada")
            dialog.geometry("400x380")
            dialog.attributes("-topmost", True)
            dialog.grab_set() 

            columnas_actuales = list(self.df.columns)

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

            # --- NUEVO: Etiqueta para mensajes de error ---
            error_label = ctk.CTkLabel(dialog, text="", text_color="#e74c3c", font=ctk.CTkFont(weight="bold"))
            error_label.pack(pady=(0, 5))

            def aplicar_calculo():
                error_label.configure(text="") # Limpia errores anteriores
                c1 = col1_combo.get()
                op = op_combo.get()
                c2 = col2_combo.get()
                new_col = new_col_entry.get()

                if not new_col:
                    error_label.configure(text="⚠️ Ingresa un nombre para la columna.")
                    return
                if new_col in self.df.columns:
                    error_label.configure(text=f"⚠️ La columna '{new_col}' ya existe.")
                    return
                
                try:
                    self.df_history.append(self.df.copy())
                    
                    # --- SMART PARSER ---
                    def limpiar_y_convertir(serie):
                        serie_limpia = serie.astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
                        return pd.to_numeric(serie_limpia, errors='coerce')

                    s1 = limpiar_y_convertir(self.df[c1])
                    s2 = limpiar_y_convertir(self.df[c2])
                    # --------------------

                    if op == "+": self.df[new_col] = s1 + s2
                    elif op == "-": self.df[new_col] = s1 - s2
                    elif op == "*": self.df[new_col] = s1 * s2
                    elif op == "/": self.df[new_col] = s1 / s2

                    self.registrar_paso(f"Cálculo: '{new_col}' = '{c1}' {op} '{c2}'")
                    self.actualizar_vista_previa()
                    dialog.destroy()
                    
                except Exception as e:
                    print(f"Error en el cálculo: {e}")
                    self.df_history.pop()

            btn_aplicar = ctk.CTkButton(dialog, text="Aplicar Cálculo", command=aplicar_calculo, fg_color="#27ae60", hover_color="#2ecc71")
            btn_aplicar.pack(pady=20)
                    
    # ---- NUEVA FUNCIÓN: COMBINAR TEXTOS ----
    def combinar_columnas(self):
        if self.df is not None:
            dialog = ctk.CTkToplevel(self)
            dialog.title("Combinar Columnas de Texto")
            dialog.geometry("400x410")
            dialog.attributes("-topmost", True)
            dialog.grab_set() 

            columnas_actuales = list(self.df.columns)

            ctk.CTkLabel(dialog, text="Selecciona la Columna 1:").pack(pady=(10, 0))
            col1_combo = ctk.CTkComboBox(dialog, values=columnas_actuales)
            col1_combo.pack(pady=5)

            ctk.CTkLabel(dialog, text="Separador:").pack(pady=(5, 0))
            # Opciones de separación típicas en limpieza de datos
            sep_combo = ctk.CTkComboBox(dialog, values=["Espacio", "Guion (-)", "Coma (,)", "Sin separador"])
            sep_combo.pack(pady=5)

            ctk.CTkLabel(dialog, text="Selecciona la Columna 2:").pack(pady=(5, 0))
            col2_combo = ctk.CTkComboBox(dialog, values=columnas_actuales)
            col2_combo.pack(pady=5)

            ctk.CTkLabel(dialog, text="Nombre de la Nueva Columna:").pack(pady=(5, 0))
            new_col_entry = ctk.CTkEntry(dialog, placeholder_text="Ej: Producto_Cliente")
            new_col_entry.pack(pady=5)

            # --- NUEVO: Etiqueta para mensajes de error ---
            error_label = ctk.CTkLabel(dialog, text="", text_color="#e74c3c", font=ctk.CTkFont(weight="bold"))
            error_label.pack(pady=(0, 5))

            def aplicar_combinacion():
                error_label.configure(text="") # Limpia errores anteriores
                c1 = col1_combo.get()
                sep_texto = sep_combo.get()
                c2 = col2_combo.get()
                new_col = new_col_entry.get()

                if not new_col:
                    error_label.configure(text="⚠️ Ingresa un nombre para la columna.")
                    return
                if new_col in self.df.columns:
                    error_label.configure(text=f"⚠️ La columna '{new_col}' ya existe.")
                    return
                # Traducimos la selección del usuario al símbolo real
                if sep_texto == "Espacio": separador = " "
                elif sep_texto == "Guion (-)": separador = " - "
                elif sep_texto == "Coma (,)": separador = ", "
                else: separador = ""

                try:
                    self.df_history.append(self.df.copy())
                    
                    # Forzamos la conversión a texto (.astype(str)) para evitar errores 
                    # si intentan combinar un número con un texto.
                    self.df[new_col] = self.df[c1].astype(str) + separador + self.df[c2].astype(str)

                    # Si habían nulos, Pandas pondrá la palabra "nan". Los limpiamos:
                    self.df[new_col] = self.df[new_col].str.replace('nan', '', case=False).str.strip(separador)

                    self.registrar_paso(f"Combinar: '{c1}' y '{c2}' ➔ '{new_col}'")
                    self.actualizar_vista_previa()
                    dialog.destroy()
                    
                except Exception as e:
                    print(f"Error al combinar: {e}")
                    self.df_history.pop()

            btn_aplicar = ctk.CTkButton(dialog, text="Aplicar Combinación", command=aplicar_combinacion, fg_color="#27ae60", hover_color="#2ecc71")
            btn_aplicar.pack(pady=20)
            
    # ---- NUEVA FUNCIÓN FASE 8: UNIR DATASETS (MERGE / JOIN) ----
    def unir_datasets(self):
        if self.df is not None:
            dialog = ctk.CTkToplevel(self)
            dialog.title("Unir Datasets (Merge / JOIN)")
            dialog.geometry("650x650") # 📏 Ventana más grande para la mini-tabla
            dialog.transient(self)
            dialog.grab_set()

            self.df2 = None

            ctk.CTkLabel(dialog, text="1. Cargar Segundo Dataset (Tabla Dimensional)", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(15, 5))
            
            lbl_df2_info = ctk.CTkLabel(dialog, text="Ningún archivo cargado", text_color="gray")
            
            btn_cargar_df2 = ctk.CTkButton(dialog, text="📁 Buscar Archivo 2", fg_color="#8e44ad", hover_color="#732d91")
            btn_cargar_df2.pack(pady=5)
            lbl_df2_info.pack(pady=5)

            # --- NUEVO: Mini Vista Previa del Dataset 2 ---
            preview_frame = ctk.CTkFrame(dialog, height=120)
            preview_frame.pack(fill="x", padx=20, pady=5)
            
            tree_scroll_y2 = ctk.CTkScrollbar(preview_frame)
            tree_scroll_y2.pack(side="right", fill="y")
            tree_scroll_x2 = ctk.CTkScrollbar(preview_frame, orientation="horizontal")
            tree_scroll_x2.pack(side="bottom", fill="x")

            # Tabla pequeñita para no ocupar toda la pantalla
            tree2 = ttk.Treeview(preview_frame, height=4, yscrollcommand=tree_scroll_y2.set, xscrollcommand=tree_scroll_x2.set, selectmode="none")
            tree2.pack(expand=True, fill="both")
            tree_scroll_y2.configure(command=tree2.yview)
            tree_scroll_x2.configure(command=tree2.xview)
            # ---------------------------------------------

            opciones_frame = ctk.CTkFrame(dialog, fg_color="transparent")

            def cargar_df2():
                file_path = filedialog.askopenfilename(title="Seleccionar Dataset 2", filetypes=[("Archivos de datos", "*.csv *.xlsx *.xls")])
                if file_path:
                    try:
                        ext = os.path.splitext(file_path)[1].lower()
                        if ext == '.csv':
                            self.df2 = pd.read_csv(file_path)
                        else:
                            self.df2 = pd.read_excel(file_path)
                        
                        nombre = os.path.basename(file_path)
                        lbl_df2_info.configure(text=f"✅ Archivo listo: {nombre} ({len(self.df2.columns)} columnas)", text_color="#27ae60")
                        
                        # --- NUEVO: Llenar la mini tabla con los datos ---
                        tree2.delete(*tree2.get_children())
                        df_preview = self.df2.head(5).fillna("") # Mostramos 5 filas
                        tree2["column"] = list(df_preview.columns)
                        tree2["show"] = "headings"
                        for col in tree2["column"]:
                            tree2.heading(col, text=col)
                            tree2.column(col, width=100, anchor="center")
                        for index, row in df_preview.iterrows():
                            tree2.insert("", "end", values=list(row))
                        # -------------------------------------------------

                        col2_combo.configure(values=list(self.df2.columns))
                        col2_combo.set(list(self.df2.columns)[0])
                        
                        opciones_frame.pack(fill="both", expand=True, padx=20, pady=10)
                        
                    except Exception as e:
                        lbl_df2_info.configure(text=f"❌ Error al cargar: {str(e)}", text_color="red")
            
            btn_cargar_df2.configure(command=cargar_df2)

            # --- Opciones de Cruce (dentro del frame) ---
            ctk.CTkLabel(opciones_frame, text="2. Configurar el Cruce (JOIN)", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(15, 10))

            ctk.CTkLabel(opciones_frame, text="Llave en Dataset Principal:").pack(pady=(5, 0))
            col1_combo = ctk.CTkComboBox(opciones_frame, values=list(self.df.columns))
            col1_combo.pack(pady=5)

            ctk.CTkLabel(opciones_frame, text="Llave en Dataset 2:").pack(pady=(5, 0))
            col2_combo = ctk.CTkComboBox(opciones_frame, values=["Esperando archivo..."])
            col2_combo.pack(pady=5)

            ctk.CTkLabel(opciones_frame, text="Tipo de Unión (JOIN):").pack(pady=(5, 0))
            tipo_combo = ctk.CTkComboBox(opciones_frame, values=["Izquierda (Left Join)", "Interna (Inner Join)"])
            tipo_combo.pack(pady=5)

            error_label = ctk.CTkLabel(opciones_frame, text="", text_color="#e74c3c", font=ctk.CTkFont(weight="bold"))
            error_label.pack(pady=(10, 5))

            def aplicar_union():
                error_label.configure(text="")
                if self.df2 is None:
                    error_label.configure(text="⚠️ Primero debes cargar el Dataset 2.")
                    return
                
                k1 = col1_combo.get()
                k2 = col2_combo.get()
                tipo_str = tipo_combo.get()
                
                how_join = "left" if "Left" in tipo_str else "inner"

                try:
                    self.df_history.append(self.df.copy()) 
                    
                    self.df = pd.merge(self.df, self.df2, left_on=k1, right_on=k2, how=how_join)
                    
                    self.registrar_paso(f"Unión ({how_join}): usando '{k1}' = '{k2}'")
                    self.actualizar_vista_previa()
                    dialog.destroy()
                except Exception as e:
                    error_label.configure(text="⚠️ Error. Revisa que las llaves tengan el mismo tipo de dato.")
                    print(f"Error Merge: {e}")
                    self.df_history.pop()

            btn_aplicar = ctk.CTkButton(opciones_frame, text="Aplicar Unión", command=aplicar_union, fg_color="#27ae60", hover_color="#2ecc71")
            btn_aplicar.pack(pady=15)
            
    # ---- NUEVA FUNCIÓN FASE 9: EXPORTAR DATOS (LOAD) ----
    def exportar_datos(self):
        if self.df is None:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Exportar Datos")
        dialog.geometry("400x300")
        dialog.transient(self) # Escudo anti-ventanas invasivas
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="💾 Seleccionar formato de exportación", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(20, 10))

        # Menú desplegable con los tres formatos estrella
        formato_combo = ctk.CTkComboBox(dialog, values=["Archivo CSV (.csv)", "Archivo Excel (.xlsx)", "Base de Datos SQLite (.db)"])
        formato_combo.pack(pady=10)

        error_label = ctk.CTkLabel(dialog, text="", text_color="#e74c3c", font=ctk.CTkFont(weight="bold"))
        error_label.pack(pady=5)

        def guardar():
            formato = formato_combo.get()
            
            try:
                if "CSV" in formato:
                    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivo CSV", "*.csv")])
                    if file_path:
                        self.df.to_csv(file_path, index=False)
                        self.registrar_paso(f"💾 Exportado a CSV: {os.path.basename(file_path)}")
                        dialog.destroy()
                        
                elif "Excel" in formato:
                    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivo Excel", "*.xlsx")])
                    if file_path:
                        self.df.to_excel(file_path, index=False)
                        self.registrar_paso(f"💾 Exportado a Excel: {os.path.basename(file_path)}")
                        dialog.destroy()
                        
                elif "SQLite" in formato:
                    file_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Base de Datos SQLite", "*.db")])
                    if file_path:
                        import sqlite3
                        # Conecta al archivo .db (o lo crea mágicamente si no existe)
                        conn = sqlite3.connect(file_path)
                        # Pandas hace la magia de crear la tabla y meter los datos
                        self.df.to_sql("datos_limpios", conn, if_exists="replace", index=False)
                        conn.close()
                        self.registrar_paso(f"💾 Exportado a SQLite: {os.path.basename(file_path)}")
                        dialog.destroy()
            except Exception as e:
                error_label.configure(text=f"⚠️ Error al guardar. Revisa la consola.")
                print(f"Error Export: {e}")

        btn_guardar = ctk.CTkButton(dialog, text="Guardar Como...", command=guardar, fg_color="#2980b9", hover_color="#1f618d")
        btn_guardar.pack(pady=15)
if __name__ == "__main__":
    app = QueryLibreApp()
    app.mainloop()
    