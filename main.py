import customtkinter as ctk
from tkinter import filedialog  # Necesario para abrir el explorador de archivos
import pandas as pd             # El motor de QueryLibre
import os

# Configuración inicial del tema (estilo Power BI / Moderno)
ctk.set_appearance_mode("System")  # Se adapta al tema de Windows (Dark/Light)
ctk.set_default_color_theme("blue") # Color de acento para los botones

class QueryLibreApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Variable para almacenar los datos globalmente en la app
        self.df = None 

        # Configuración de la ventana principal
        self.title("QueryLibre - Motor de Transformación de Datos")
        self.geometry("900x600")
        self.minsize(800, 500)

        # ---- LAYOUT PRINCIPAL (Sistema de grilla) ----
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---- PANEL LATERAL (Menú) ----
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Título del panel lateral
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="QueryLibre", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botones del menú
        self.btn_cargar = ctk.CTkButton(self.sidebar_frame, text="📁 Cargar Archivo", command=self.cargar_archivo)
        self.btn_cargar.grid(row=1, column=0, padx=20, pady=10)

        self.btn_transformar = ctk.CTkButton(self.sidebar_frame, text="⚙️ Transformar", state="disabled")
        self.btn_transformar.grid(row=2, column=0, padx=20, pady=10)

        self.btn_exportar = ctk.CTkButton(self.sidebar_frame, text="💾 Exportar a MySQL", state="disabled")
        self.btn_exportar.grid(row=3, column=0, padx=20, pady=10)

        # ---- ÁREA PRINCIPAL ----
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Mensaje de bienvenida
        self.welcome_label = ctk.CTkLabel(self.main_frame, text="Bienvenido a QueryLibre\nCarga un dataset para comenzar.", font=ctk.CTkFont(size=16))
        self.welcome_label.pack(expand=True)

        # NUEVO: Barra de herramientas (oculta al inicio)
        self.toolbar_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        # Botones de transformación rápida
        self.btn_dup = ctk.CTkButton(self.toolbar_frame, text="Eliminar Duplicados", 
                                     command=self.eliminar_duplicados, width=140, fg_color="#34495e")
        self.btn_dup.pack(side="left", padx=5)

        self.btn_nulos = ctk.CTkButton(self.toolbar_frame, text="Limpiar Nulos", 
                                       command=self.limpiar_nulos, width=140, fg_color="#34495e")
        self.btn_nulos.pack(side="left", padx=5)

        # Cuadro de texto para la vista previa (oculto al inicio)
        self.preview_text = ctk.CTkTextbox(self.main_frame, font=("Consolas", 11), state="disabled")

    # ---- MÉTODOS DE LA APLICACIÓN ----

    def cargar_archivo(self):
        # Filtramos para aceptar tanto CSV como Excel
        file_path = filedialog.askopenfilename(
            title="Seleccionar Dataset",
            filetypes=[("Archivos de datos", "*.csv *.xlsx *.xls"), ("Todos los archivos", "*.*")]
        )

        if file_path:
            try:
                # Detectar extensión y leer correctamente
                extension = os.path.splitext(file_path)[1].lower()
                
                if extension == '.csv':
                    self.df = pd.read_csv(file_path)
                else:
                    self.df = pd.read_excel(file_path) # Requiere openpyxl

                # 1. Quitar el mensaje de bienvenida y mostrar la interfaz
                self.welcome_label.pack_forget()
                self.toolbar_frame.pack(fill="x", padx=20, pady=(10, 0)) 
                self.preview_text.pack(expand=True, fill="both", padx=20, pady=20)

                # 2. Actualizar estado de la interfaz
                nombre_archivo = os.path.basename(file_path)
                print(f"✅ {nombre_archivo} cargado con éxito.")
                self.btn_transformar.configure(state="normal")
                
                # 3. Mostrar los datos
                self.actualizar_vista_previa()
                
            except Exception as e:
                self.welcome_label.pack(expand=True) # Vuelve a mostrar el texto en caso de error
                self.welcome_label.configure(text=f"❌ Error al cargar:\n{str(e)}", text_color="red")
        else:
            print("Operación cancelada.")

    def actualizar_vista_previa(self):
        """Refresca el cuadro de texto con el estado actual de self.df"""
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        if self.df is not None:
            # Mostramos las primeras 15 filas de forma legible
            self.preview_text.insert("1.0", self.df.head(15).to_string())
        self.preview_text.configure(state="disabled")

    def eliminar_duplicados(self):
        if self.df is not None:
            antes = len(self.df)
            self.df = self.df.drop_duplicates()
            despues = len(self.df)
            print(f"Transformación: Se eliminaron {antes - despues} filas duplicadas.")
            self.actualizar_vista_previa()

    def limpiar_nulos(self):
        if self.df is not None:
            self.df = self.df.dropna()
            print("Transformación: Filas con valores nulos eliminadas.")
            self.actualizar_vista_previa()

if __name__ == "__main__":
    app = QueryLibreApp()
    app.mainloop()