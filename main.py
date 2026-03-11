import customtkinter as ctk
from tkinter import filedialog
import pandas as pd
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class QueryLibreApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.df = None 
        self.historial_pasos = []
        self.df_history = [] 

        self.title("QueryLibre - Motor de Transformación de Datos")
        self.geometry("1100x650") # Un poco más ancha para los nuevos botones
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

        # ---- BARRA DE HERRAMIENTAS (Arsenal Expandido) ----
        self.toolbar_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        self.btn_dup = ctk.CTkButton(self.toolbar_frame, text="Eliminar Duplicados", command=self.eliminar_duplicados, width=130, fg_color="#34495e")
        self.btn_dup.pack(side="left", padx=5)

        self.btn_nulos = ctk.CTkButton(self.toolbar_frame, text="Limpiar Nulos", command=self.limpiar_nulos, width=120, fg_color="#34495e")
        self.btn_nulos.pack(side="left", padx=5)

        # NUEVO: Botón Eliminar Columna
        self.btn_eliminar_col = ctk.CTkButton(self.toolbar_frame, text="🗑️ Eliminar Columna", command=self.eliminar_columna, width=140, fg_color="#c0392b", hover_color="#922b21")
        self.btn_eliminar_col.pack(side="left", padx=5)

        # NUEVO: Botón Renombrar Columna
        self.btn_renombrar_col = ctk.CTkButton(self.toolbar_frame, text="✏️ Renombrar Columna", command=self.renombrar_columna, width=150, fg_color="#2980b9", hover_color="#1f618d")
        self.btn_renombrar_col.pack(side="left", padx=5)

        # ---- CONTENEDOR TABLA + HISTORIAL ----
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        self.preview_text = ctk.CTkTextbox(self.content_frame, font=("Consolas", 11), state="disabled", wrap="none")

        self.history_frame = ctk.CTkFrame(self.content_frame, width=200)
        self.history_label = ctk.CTkLabel(self.history_frame, text="📋 Pasos Aplicados", font=ctk.CTkFont(weight="bold"))
        self.history_label.pack(pady=(10, 5))
        
        self.history_text = ctk.CTkTextbox(self.history_frame, font=("Arial", 11), state="disabled", width=200)
        self.history_text.pack(expand=True, fill="both", padx=10, pady=5)

        self.btn_deshacer = ctk.CTkButton(self.history_frame, text="↩️ Deshacer Último", command=self.deshacer_paso, state="disabled", fg_color="#e74c3c", hover_color="#c0392b")
        self.btn_deshacer.pack(pady=(5, 15), padx=10, fill="x")

    # ---- MÉTODOS DE LA APLICACIÓN ----

    def registrar_paso(self, descripcion):
        self.historial_pasos.append(descripcion)
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        
        for i, paso in enumerate(self.historial_pasos, 1):
            self.history_text.insert("end", f"{i}. {paso}\n\n")
            
        self.history_text.configure(state="disabled")

        if len(self.historial_pasos) > 1:
            self.btn_deshacer.configure(state="normal")

    def cargar_archivo(self):
        file_path = filedialog.askopenfilename(title="Seleccionar Dataset", filetypes=[("Archivos de datos", "*.csv *.xlsx *.xls"), ("Todos los archivos", "*.*")])

        if file_path:
            try:
                extension = os.path.splitext(file_path)[1].lower()
                if extension == '.csv':
                    self.df = pd.read_csv(file_path)
                else:
                    self.df = pd.read_excel(file_path)

                self.historial_pasos = []
                self.df_history = []
                self.btn_deshacer.configure(state="disabled")

                self.welcome_label.pack_forget()
                self.toolbar_frame.pack(fill="x", padx=20, pady=(10, 0)) 
                self.content_frame.pack(expand=True, fill="both", padx=20, pady=20)
                
                self.preview_text.pack(side="left", expand=True, fill="both", padx=(0, 10))
                self.history_frame.pack(side="right", fill="y")

                self.btn_transformar.configure(state="normal")
                self.actualizar_vista_previa()
                
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

    def deshacer_paso(self):
        if self.df_history and len(self.historial_pasos) > 1:
            self.df = self.df_history.pop()
            self.historial_pasos.pop()
            
            self.history_text.configure(state="normal")
            self.history_text.delete("1.0", "end")
            for i, paso in enumerate(self.historial_pasos, 1):
                self.history_text.insert("end", f"{i}. {paso}\n\n")
            self.history_text.configure(state="disabled")
            
            self.actualizar_vista_previa()
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

    # ---- NUEVAS FUNCIONES FASE 6 ----

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

if __name__ == "__main__":
    app = QueryLibreApp()
    app.mainloop()