import customtkinter as ctk
from tkinter import filedialog
import pandas as pd
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class QueryLibreApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Variables de estado de la aplicación
        self.df = None 
        self.historial_pasos = [] # NUEVO: Memoria de los pasos aplicados

        # Configuración de la ventana principal
        self.title("QueryLibre - Motor de Transformación de Datos")
        self.geometry("1000x600") # Un poco más ancha para que entre el panel
        self.minsize(900, 500)

        # ---- LAYOUT PRINCIPAL ----
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---- PANEL LATERAL (Menú) ----
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="QueryLibre", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_cargar = ctk.CTkButton(self.sidebar_frame, text="📁 Cargar Archivo", command=self.cargar_archivo)
        self.btn_cargar.grid(row=1, column=0, padx=20, pady=10)

        self.btn_transformar = ctk.CTkButton(self.sidebar_frame, text="⚙️ Transformar", state="disabled")
        self.btn_transformar.grid(row=2, column=0, padx=20, pady=10)

        self.btn_exportar = ctk.CTkButton(self.sidebar_frame, text="💾 Exportar a MySQL", state="disabled")
        self.btn_exportar.grid(row=3, column=0, padx=20, pady=10)

        # ---- ÁREA PRINCIPAL ----
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.welcome_label = ctk.CTkLabel(self.main_frame, text="Bienvenido a QueryLibre\nCarga un dataset para comenzar.", font=ctk.CTkFont(size=16))
        self.welcome_label.pack(expand=True)

        # Barra de herramientas (oculta al inicio)
        self.toolbar_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        self.btn_dup = ctk.CTkButton(self.toolbar_frame, text="Eliminar Duplicados", 
                                     command=self.eliminar_duplicados, width=140, fg_color="#34495e")
        self.btn_dup.pack(side="left", padx=5)

        self.btn_nulos = ctk.CTkButton(self.toolbar_frame, text="Limpiar Nulos", 
                                       command=self.limpiar_nulos, width=140, fg_color="#34495e")
        self.btn_nulos.pack(side="left", padx=5)

        # NUEVO: Contenedor dividido para Tabla + Historial
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        # 1. Tabla de Vista Previa (Izquierda) - Le agregamos wrap="none" para que las tablas no se rompan
        self.preview_text = ctk.CTkTextbox(self.content_frame, font=("Consolas", 11), state="disabled", wrap="none")

        # 2. Panel de Pasos Aplicados (Derecha)
        self.history_frame = ctk.CTkFrame(self.content_frame, width=200)
        self.history_label = ctk.CTkLabel(self.history_frame, text="📋 Pasos Aplicados", font=ctk.CTkFont(weight="bold"))
        self.history_label.pack(pady=(10, 5))
        self.history_text = ctk.CTkTextbox(self.history_frame, font=("Arial", 11), state="disabled", width=200)
        self.history_text.pack(expand=True, fill="both", padx=10, pady=(0, 10))

    # ---- MÉTODOS DE LA APLICACIÓN ----

    def registrar_paso(self, descripcion):
        """Agrega un paso al historial visual y a la memoria."""
        self.historial_pasos.append(descripcion)
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        
        # Escribimos todos los pasos numerados
        for i, paso in enumerate(self.historial_pasos, 1):
            self.history_text.insert("end", f"{i}. {paso}\n\n")
            
        self.history_text.configure(state="disabled")

    def cargar_archivo(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar Dataset",
            filetypes=[("Archivos de datos", "*.csv *.xlsx *.xls"), ("Todos los archivos", "*.*")]
        )

        if file_path:
            try:
                extension = os.path.splitext(file_path)[1].lower()
                if extension == '.csv':
                    self.df = pd.read_csv(file_path)
                else:
                    self.df = pd.read_excel(file_path)

                # Reiniciamos el historial al cargar un archivo nuevo
                self.historial_pasos = []

                # Ocultamos bienvenida y mostramos la interfaz de trabajo
                self.welcome_label.pack_forget()
                self.toolbar_frame.pack(fill="x", padx=20, pady=(10, 0)) 
                self.content_frame.pack(expand=True, fill="both", padx=20, pady=20)
                
                # Empaquetamos Tabla a la izquierda e Historial a la derecha
                self.preview_text.pack(side="left", expand=True, fill="both", padx=(0, 10))
                self.history_frame.pack(side="right", fill="y")

                self.btn_transformar.configure(state="normal")
                self.actualizar_vista_previa()
                
                # Registramos el primer paso
                nombre_archivo = os.path.basename(file_path)
                self.registrar_paso(f"Origen: {nombre_archivo}")
                
            except Exception as e:
                self.welcome_label.pack(expand=True)
                self.welcome_label.configure(text=f"❌ Error al cargar:\n{str(e)}", text_color="red")

    def actualizar_vista_previa(self):
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        if self.df is not None:
            self.preview_text.insert("1.0", self.df.head(15).to_string())
        self.preview_text.configure(state="disabled")

    def eliminar_duplicados(self):
        if self.df is not None:
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
            antes = len(self.df)
            self.df = self.df.dropna()
            despues = len(self.df)
            filas_eliminadas = antes - despues
            
            if filas_eliminadas > 0:
                self.registrar_paso(f"Se eliminaron {filas_eliminadas} filas con nulos")
            else:
                self.registrar_paso("Limpiar nulos (0 filas)")
                
            self.actualizar_vista_previa()

if __name__ == "__main__":
    app = QueryLibreApp()
    app.mainloop()