import customtkinter as ctk
from tkinter import messagebox

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
        
        ctk.CTkLabel(dialog, text="QueryLibre v1.5.2", font=ctk.CTkFont(weight="bold", size=20)).pack(pady=(20, 5))
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
    @staticmethod
    def mostrar_radiografia(app_root, tab):
        """Muestra el panel de perfilado de datos."""
        if not tab or tab.motor.df is None: 
            return
        
        dialog = ctk.CTkToplevel(app_root)
        dialog.title("Radiografía de Datos")
        dialog.geometry("400x520") # Aumentamos un poco para que respire
        dialog.grab_set()
        
        if hasattr(app_root, 'fijar_icono'):
            app_root.fijar_icono(dialog)
        
        # Título
        ctk.CTkLabel(dialog, text="Selecciona una columna a auditar:", 
                     font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        
        # El cuadro de texto DEBE crearse y empaquetarse primero
        textbox = ctk.CTkTextbox(dialog, width=360, height=350, font=("Consolas", 13))
        
        def actualizar_reporte(seleccion):
            reporte = tab.motor.obtener_radiografia(seleccion)
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            textbox.insert("end", reporte)
            textbox.configure(state="disabled")

        # ComboBox de columnas
        col_combo = ctk.CTkComboBox(dialog, values=list(tab.motor.df.columns), 
                                    command=actualizar_reporte, width=200)
        col_combo.pack(pady=5)
        
        # Empaquetamos el textbox al final pero con padding
        textbox.pack(pady=(10, 20), padx=20)
        
        # Forzamos la carga inicial
        if len(tab.motor.df.columns) > 0:
            col_combo.set(tab.motor.df.columns[0])
            actualizar_reporte(tab.motor.df.columns[0])
            
    @staticmethod
    def cambiar_tipo_dato(app_root, tab):
        """Muestra el diálogo para cambiar el tipo de dato de una columna."""
        if not tab or tab.motor.df is None: return

        dialog = ctk.CTkToplevel(app_root)
        dialog.title("Cambiar Tipo de Dato")
        dialog.geometry("400x300")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Columna:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 0))
        col_combo = ctk.CTkComboBox(dialog, values=list(tab.motor.df.columns), width=250)
        col_combo.pack(pady=5)

        ctk.CTkLabel(dialog, text="Nuevo Tipo:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0))
        tipo_combo = ctk.CTkComboBox(dialog, values=["Número Entero", "Número Decimal", "Texto", "Fecha"], width=250)
        tipo_combo.pack(pady=5)

        def ejecutar():
            col = col_combo.get()
            nuevo_tipo = tipo_combo.get()
            # Aquí usamos el "ayudante" (Threading) que creamos antes
            app_root.ejecutar_tarea_pesada(tab.motor.cambiar_tipo_dato, col, nuevo_tipo)
            dialog.destroy()

        ctk.CTkButton(dialog, text="Aplicar Cambio", command=ejecutar, fg_color="#27ae60").pack(pady=20)
        
    @staticmethod
    def limpiar_nulos(app_root, tab):
        dialog = ctk.CTkToplevel(app_root)
        dialog.title("Limpieza")
        dialog.geometry("350x220")
        dialog.grab_set()

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

        ctk.CTkLabel(dialog, text="Selecciona la columna a eliminar:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        col_combo = ctk.CTkComboBox(dialog, values=list(tab.motor.df.columns), width=250)
        col_combo.pack(pady=5)

        def ejecutar():
            col = col_combo.get()
            # Seguridad: Confirmación antes de borrar
            if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar la columna '{col}'?"):
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