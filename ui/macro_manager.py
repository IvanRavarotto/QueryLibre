import json
import logging
import os
from tkinter import filedialog, messagebox

LOGGER = logging.getLogger("QueryLibre")

class MacroManager:
    ALLOWED_MACRO_ACTIONS = {
        "eliminar_duplicados", "limpiar_nulos", "eliminar_columna", "renombrar_columna",
        "editar_celda", "calcular_columna", "combinar_columnas", "dividir_columna",
        "filtrar_datos", "cambiar_tipo_dato", "aplicar_union", "agrupar_datos",
        "buscar_reemplazar", "aplicar_autocasteo_confirmado", "anular_dinamizacion",
        "agregar_columna_condicional", "transformar_texto"
    }
    DISALLOWED_MACRO_PARAM_KEYS = {
        "__class__", "__dict__", "__bases__", "__globals__", "__code__",
        "__closure__", "__func__", "__self__", "__module__"
    }
    
    def __init__(self, motor, app_root):
        self.motor = motor
        self.app_root = app_root
    
    def guardar_macro(self, macro_steps):
        if not macro_steps:
            messagebox.showinfo("Macros", "No hay acciones registradas.")
            return
        carpeta_macros = os.path.join(os.path.expanduser('~'), 'Documents', 'QueryLibre', 'Macros')
        os.makedirs(carpeta_macros, exist_ok=True)
        file_path = filedialog.asksaveasfilename(
            initialdir=carpeta_macros, defaultextension=".json",
            filetypes=[("QueryLibre Macro", "*.json")], title="Guardar Macro"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(macro_steps, f, indent=4)
                self.motor.registrar_paso(f"🤖 Macro guardada: {os.path.basename(file_path)}")
                messagebox.showinfo("Éxito", "Macro guardada.")
            except Exception as e:
                LOGGER.error(f"Error guardando macro: {e}")
    
    def ejecutar_macro(self):
        if self.motor.df is None:
            messagebox.showinfo("Macros", "Carga un dataset primero.")
            return
        carpeta_macros = os.path.join(os.path.expanduser('~'), 'Documents', 'QueryLibre', 'Macros')
        os.makedirs(carpeta_macros, exist_ok=True)
        file_path = filedialog.askopenfilename(
            initialdir=carpeta_macros, title="Seleccionar Macro",
            filetypes=[("QueryLibre Macro", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    pasos = json.load(f)
                self._apply_macro_steps(pasos)
                # Refrescar la pestaña activa
                if hasattr(self.app_root, 'actualizar_lbl_dimensiones'):
                    self.app_root.actualizar_lbl_dimensiones()
            except Exception as e:
                LOGGER.error(f"Error ejecutando macro: {e}")
                messagebox.showerror("Error", f"Macro abortada.\n{e}")
    
    def _apply_macro_steps(self, pasos):
        backup_df = self.motor.df.copy(deep=True)
        backup_history = list(self.motor.df_history)
        backup_steps = list(self.motor.macro_steps)
        backup_historial = list(self.motor.historial_pasos)
        errores = []
        try:
            for paso in pasos:
                nombre = paso.get("action")
                params = paso.get("params", {})
                if nombre not in self.ALLOWED_MACRO_ACTIONS:
                    LOGGER.error(f"Acción no permitida: {nombre}")
                    continue
                if not isinstance(params, dict):
                    continue
                if any(key.startswith("__") or key in self.DISALLOWED_MACRO_PARAM_KEYS for key in params.keys()):
                    LOGGER.error("Parámetros maliciosos")
                    continue
                # Validar rutas maliciosas
                peligroso = False
                for k, v in params.items():
                    if isinstance(v, str) and any(bad in v for bad in ["..", ":", "/", "\\", "C:", "D:"]):
                        LOGGER.error(f"Ruta maliciosa en {k}: {v}")
                        peligroso = True
                        break
                if peligroso:
                    continue
                if hasattr(self.motor, nombre):
                    try:
                        getattr(self.motor, nombre)(**params)
                    except Exception as e:
                        LOGGER.warning(f"Paso omitido {nombre}: {e}")
                        errores.append(f"{nombre}: {e}")
        except Exception as e:
            self.motor.df = backup_df
            self.motor.df_history = backup_history
            self.motor.macro_steps = backup_steps
            self.motor.historial_pasos = backup_historial
            raise e
        if errores:
            messagebox.showwarning("Macro con omisiones", "\n".join(errores[:5]))
    
    def _is_safe_value(self, value):
        if isinstance(value, (str, int, float, bool)):
            return True
        elif isinstance(value, list):
            return all(self._is_safe_value(v) for v in value)
        elif isinstance(value, dict):
            return all(isinstance(k, str) and self._is_safe_value(v) for k, v in value.items())
        return False