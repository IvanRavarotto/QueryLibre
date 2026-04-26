# 🔍 QueryLibre - Motor de Transformación de Datos (ETL)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458.svg?logo=pandas&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-GUI-darkgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

QueryLibre es una aplicación de escritorio ligera e independiente, desarrollada 100% en Python, diseñada para democratizar la limpieza y transformación de datos. Permite a los usuarios cargar, procesar, unir y exportar bases de datos sin necesidad de escribir código o depender de software pesado.

> **💡 Motivación:** Llevar la potencia del procesamiento vectorizado de Pandas a una interfaz gráfica intuitiva, similar a Power Query, pero en un entorno de código abierto, escalable y de ejecución local.

---

## 📸 Interfaz de Usuario

**Entorno de Trabajo Multitarea (Ribbon UI y Pestañas)**
*(Inserta aquí tu captura más reciente de la v1.4.0)*

**Radiografía de Datos (Data Profiling)**
*(Inserta aquí la captura del panel oscuro de Radiografía)*

---

## 🚀 Características Principales (v1.8.0)

* **🧠 Smart Data Profiling (Radiografía de Datos):** Genera análisis estadísticos y gráficos de distribución automáticos para cualquier columna con un solo clic.
* **🔀 Columnas Condicionales (IF-THEN-ELSE):** Crea nuevas columnas dinámicas basadas en reglas matemáticas o de texto utilizando el procesamiento vectorizado de alto rendimiento de Numpy.
* **🔄 Unpivot Horizontal a Vertical:** Transforma datos de formato ancho (como meses en columnas) a formato largo, ideal para su ingesta en motores de bases de datos o herramientas de BI.
* **⏳ Viaje en el Tiempo (Caché Parquet):** Sistema robusto de Deshacer/Rehacer (`Ctrl+Z` / `Ctrl+Y`) respaldado por un caché en disco de formato `.parquet`, garantizando la recuperación ante errores sin saturar la memoria RAM.
* **📊 Correlación Interactiva:** Herramienta de Gráfico de Dispersión (Scatter Plot) bidireccional. Haz clic en un punto del gráfico y la cuadrícula principal navegará automáticamente hacia esa fila exacta.
* **🗃️ Conector SQL Integrado:** Importa datos directamente desde bases de datos relacionales sin configuraciones complejas.
* **🧹 Limpieza Automatizada:** Herramientas de un solo clic para eliminación de duplicados, gestión inteligente de nulos, búsqueda y reemplazo masivo, y auto-casteo de tipos de datos.
* **💾 Exportación Universal:** Guarda tus proyectos limpiados en formatos `.csv`, `.xlsx`, o bases de datos `.sqlite` listas para producción.

---

## Próximas Actualizaciones v1.9.0: Inteligencia Artificial y Optimización**

* ✨ **Panel lateral IA:**Creación del panel lateral para el "Analista IA" y la pestaña de configuración para la API Key.
* 🛡️ **Motor de Contexto**: Desarrollo de generar_resumen_ia() en el motor para extraer metadatos sin comprometer la privacidad ni la RAM.
* 📊 **Integración de la API:** de Gemini/OpenAI con la interfaz del chat.
* 🔌 **Conexiones SQL:** Implementación de perfiles de conexión guardados en conexiones.json.

---

## 🛠️ Tecnologías Utilizadas

* **Motor Lógico:** `pandas` (Manipulación intensiva y vectorizada).
* **Interfaz Gráfica (GUI):** `customtkinter` (Diseño moderno, modo oscuro puro) y `tkinter` (`Treeview`).
* **Automatización:** `json` para serialización de macros.
* **Sistema de I/O:** `os`, `sys`, `sqlite3`.
* **Empaquetado:** `pyinstaller` (Compilación a binario ejecutable `.exe` standalone).

---

## 📦 Instalación y Uso (Para usuarios finales)

No es necesario instalar Python ni librerías.

1. Ve a la sección de **Releases** en este repositorio.
2. Descarga el archivo `QueryLibre.exe`.
3. Ejecútalo haciendo doble clic. 

> ⚠️ **Nota de Seguridad (Windows SmartScreen):** > Al ser un proyecto de código abierto independiente sin un certificado digital de pago, es muy probable que Windows Defender muestre una pantalla azul indicando "Windows protegió su PC". 
> Para abrir la aplicación de forma segura, haz clic en **"Más información"** y luego en el botón **"Ejecutar de todas formas"**.

---

## 💻 Para Desarrolladores

Si deseas clonar el proyecto para auditar el código, explorar la separación de capas MVC o contribuir:

1. Clona este repositorio: 
   ```bash
   git clone https://github.com/IvanRavarotto/QueryLibre.git
   cd QueryLibre
   ```
2. Crea y activa un entorno virtual:
   (Windows)
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   (macOS/Linux)
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Instala dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta el archivo principal:
   ```bash
   python main.py
   ```

## 🧪 Pruebas unitarias

Este proyecto incluye una suite `pytest` para validar las funciones clave de transformaciones.

1. Genera el dataset de pruebas y el archivo `tests/test_data_engine.py`:
   ```bash
   python data_test/generador_datos.py
   ```
2. Ejecuta los tests:
   ```bash
   python -m pytest -q
   ```

Resultado esperado:
- 29 passed, 1 warning

> Nota: se muestra un warning de pandas para `pd.to_datetime` que termina siendo no bloqueante, solo informativo.