import customtkinter as ctk
import threading
import re
import json
import logging
from tkinter import messagebox

LOGGER = logging.getLogger("QueryLibre")

class ChatIAHandler:
    """Gestiona la interfaz y lógica del chat con la IA."""
    
    def __init__(self, parent_tab, app_root):
        self.parent_tab = parent_tab
        self.app_root = app_root
        self.motor = parent_tab.motor
        
        self.chat_scroll = None
        self.frame_acciones_ia = None
        self.entry_ia = None
        self.btn_enviar_ia = None
    
    def build_ui(self, parent_frame):
        """Construye los widgets del chat dentro del frame dado."""
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(1, weight=0)
        parent_frame.grid_rowconfigure(2, weight=0)
        parent_frame.grid_rowconfigure(3, weight=0)
        parent_frame.grid_rowconfigure(4, weight=0)
        parent_frame.grid_columnconfigure(0, weight=1)
        
        self.chat_scroll = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        self.chat_scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.frame_acciones_ia = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.frame_acciones_ia.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        frame_input_ia = ctk.CTkFrame(parent_frame, fg_color="transparent")
        frame_input_ia.grid(row=2, column=0, sticky="ew", padx=5, pady=(5, 10))
        
        self.entry_ia = ctk.CTkTextbox(frame_input_ia, height=60, wrap="word")
        self.entry_ia.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_enviar_ia = ctk.CTkButton(
            frame_input_ia, text="➤", width=40, height=60,
            fg_color="#8e44ad", hover_color="#9b59b6", command=self.enviar_mensaje_ia
        )
        self.btn_enviar_ia.pack(side="right")
        
        self.entry_ia.bind("<Return>", self._on_enter_pressed)
        self.entry_ia.bind("<Shift-Return>", self._on_shift_enter_pressed)
        
        self._agregar_burbuja_chat("¡Hola! Soy tu Analista IA. Configura tu API Key para empezar a trabajar con tus datos.", "ia")
    
    def _agregar_burbuja_chat(self, texto, emisor="usuario"):
        frame_burbuja = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        frame_burbuja.pack(fill="x", pady=5, padx=5)
        if emisor == "usuario":
            bg_color = "#1f538d"
            alineacion = "e"
            etiqueta = "Tú"
        else:
            bg_color = "#2b2b2b"
            alineacion = "w"
            etiqueta = "🤖 IA"
        burbuja = ctk.CTkFrame(frame_burbuja, fg_color=bg_color, corner_radius=10)
        burbuja.pack(side="right" if alineacion == "e" else "left", fill="x", expand=False)
        ctk.CTkLabel(burbuja, text=etiqueta, font=ctk.CTkFont(weight="bold", size=10), text_color="gray").pack(anchor=alineacion, padx=10, pady=(5, 0))
        lbl_texto = ctk.CTkLabel(burbuja, text=texto, justify="left", wraplength=220)
        lbl_texto.pack(anchor=alineacion, padx=15, pady=(0, 10))
        self.parent_tab.update_idletasks()
        self.chat_scroll._parent_canvas.yview_moveto(1.0)
    
    def enviar_mensaje_ia(self, event=None):
        pregunta = self.entry_ia.get("1.0", "end-1c").strip()
        if not pregunta: 
            return "break"
        
        # Limpiamos botones de acciones anteriores para evitar acumulaciones
        for widget in self.frame_acciones_ia.winfo_children():
            widget.destroy()
            
        self._agregar_burbuja_chat(pregunta, "usuario")
        self.entry_ia.delete("1.0", "end")
        self.btn_enviar_ia.configure(state="disabled", text="⏳")
        
        import threading
        def tarea_ia():
            try:
                # 1. Recuperamos el perfil seleccionado y las llaves desde la aplicación
                # (Se asume que estas variables se setean al configurar la API o elegir el perfil)
                perfil_actual = getattr(self.app_root, 'perfil_ia_activo', 'Gemini Flash (Procesamiento Rápido)')
                api_key = getattr(self.app_root, 'api_key_actual', '')

                # 2. Construcción dinámica del contexto del dataset
                if self.motor.df is not None and not self.motor.df.empty:
                    esquema = self.motor.df.dtypes.to_string()
                    muestra = self.motor.df.head(5).to_csv(index=False)
                    contexto = f"Dataset: {len(self.motor.df)} filas\nEsquema:\n{esquema}\nMuestra:\n{muestra}"
                else:
                    contexto = "No hay ningún dataset cargado actualmente en el espacio de trabajo."

                prompt_sistema = (
                    "Eres un analista de datos experto para la aplicación QueryLibre. "
                    "Si sugieres cambios estructurales o limpiezas sobre el dataset, incluye siempre "
                    "la estructura JSON correspondiente al inicio o final de tu respuesta."
                )
                prompt_final = f"{prompt_sistema}\n\nContexto:\n{contexto}\nPregunta: {pregunta}"

                # 3. ENRUTADOR MULTI-IA (Aquí se integra el nuevo bloque)
                if "Gemini" in perfil_actual:
                    from google import genai
                    client = genai.Client(api_key=api_key)
                    # Selección del modelo según la variante del perfil
                    modelo_target = 'gemini-2.0-pro-exp-02-15' if "Pro" in perfil_actual else 'gemini-2.0-flash'
                    
                    respuesta = client.models.generate_content(
                        model=modelo_target, 
                        contents=prompt_final
                    )
                    texto_ia = respuesta.text

                elif "DeepSeek" in perfil_actual:
                    # Requiere la instalación previa del SDK compatible: pip install openai
                    from openai import OpenAI
                    
                    client = OpenAI(
                        api_key=api_key,
                        base_url="https://api.deepseek.com"
                    )
                    respuesta = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "user", "content": prompt_final}
                        ],
                        stream=False
                    )
                    texto_ia = respuesta.choices[0].message.content

                else:
                    texto_ia = "🔒 Modo Local Activo: Los datos no han sido enviados a servidores externos por motivos de privacidad."

            except Exception as e:
                texto_ia = f"Error en la comunicación con el proveedor de IA:\n{str(e)}"
                
            def actualizar():
                self._agregar_burbuja_chat(texto_ia, "ia")
                # Aquí se llama al validador de macros para inyectar los botones dinámicos si aplica
                if hasattr(self, '_procesar_posible_macro'):
                    self._procesar_posible_macro(texto_ia)
                self.btn_enviar_ia.configure(state="normal", text="➤")
                
            self.app_root.after(0, actualizar)
            
        threading.Thread(target=tarea_ia, daemon=True).start()
    
    def _on_enter_pressed(self, event):
        if self.entry_ia.get("1.0", "end-1c").strip():
            self.enviar_mensaje_ia()
        return "break"
    
    def _on_shift_enter_pressed(self, event):
        self.entry_ia.insert("insert", "\n")
        return "break"