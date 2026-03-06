import customtkinter as ctk

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

    # ---- FUNCIONES (Lógica de los botones) ----
    def cargar_archivo(self):
        print("Botón presionado: Aquí abriremos el explorador de archivos")
        self.welcome_label.configure(text="Abriendo explorador de archivos...")

if __name__ == "__main__":
    app = QueryLibreApp()
    app.mainloop()