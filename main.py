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

        # Configuración de la ventana principal
        self.title("QueryLibre - Motor de Transformación de Datos")
        self.geometry("900x600")
        self.minsize(800, 500)

        # ---- LAYOUT PRINCIPAL (Sistema de grilla) ----
        # Dividimos la pantalla en 2 columnas: un panel lateral y el área principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---- PANEL LATERAL (Menú) ----
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Espacio vacío al fondo

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

        # ---- ÁREA PRINCIPAL (Visor de Datos) ----
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.welcome_label = ctk.CTkLabel(self.main_frame, text="Bienvenido a QueryLibre\nCarga un dataset para comenzar.", font=ctk.CTkFont(size=16))
        self.welcome_label.pack(expand=True)
        
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Mensaje de bienvenida
        self.welcome_label = ctk.CTkLabel(self.main_frame, text="Bienvenido a QueryLibre\nCarga un dataset para comenzar.", font=ctk.CTkFont(size=16))
        self.welcome_label.pack(expand=True)

        # NUEVO: Cuadro de texto para la vista previa (oculto al inicio)
        self.preview_text = ctk.CTkTextbox(self.main_frame, font=("Consolas", 11), state="disabled")

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

                # 1. Quitar el mensaje de bienvenida y mostrar la tabla
                self.welcome_label.pack_forget()
                self.preview_text.pack(expand=True, fill="both", padx=20, pady=(10, 20))

                # 2. Insertar vista previa de los datos
                self.preview_text.configure(state="normal")
                self.preview_text.delete("1.0", "end")
                # Mostramos las primeras 10 filas de forma legible
                self.preview_text.insert("1.0", self.df.head(10).to_string())
                self.preview_text.configure(state="disabled")

                # 3. Actualizar estado de la interfaz
                nombre_archivo = os.path.basename(file_path)
                print(f"✅ {nombre_archivo} cargado con éxito.")
                self.btn_transformar.configure(state="normal")
                
            except Exception as e:
                self.welcome_label.configure(text=f"❌ Error al cargar:\n{str(e)}", text_color="red")
        else:
            print("Operación cancelada.")

if __name__ == "__main__":
    app = QueryLibreApp()
    app.mainloop()
    
    