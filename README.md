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

## 🚀 Características Principales (v2.0.0)

* **✨ Analista IA Integrado:** Un chat interactivo potenciado por Google Gemini capaz de leer el contexto de tus datos y sugerir transformaciones automatizadas.
* **🔒 Bóveda Segura (AES-256):** Almacenamiento encriptado con grado militar para proteger tus API Keys y credenciales locales usando una Contraseña Maestra.
* **🖱️ Menú Contextual Rápido:** Clic derecho sobre cualquier columna para transformaciones de texto masivas (MAYÚSCULAS, minúsculas, Título).
* **↕️ Ordenamiento Interactivo (Sort):** Ordena alfabética o numéricamente todo tu dataset con solo hacer clic en la cabecera de la columna.
* **🧠 Smart Data Profiling:** Genera análisis estadísticos y gráficos de distribución automáticos para cualquier columna con un solo clic.
* **🔀 Columnas Condicionales (IF-THEN-ELSE):** Crea nuevas columnas dinámicas basadas en reglas lógicas vectorizadas con Numpy.
* **🔄 Unpivot Horizontal a Vertical:** Transforma datos anchos a formato largo para motores de bases de datos.
* **⏳ Viaje en el Tiempo (Caché Parquet):** Sistema robusto de Deshacer/Rehacer (`Ctrl+Z` / `Ctrl+Y`) respaldado en disco para no saturar la memoria RAM.
* **🗃️ Conector SQL Integrado:** Importa tablas directamente desde MySQL, PostgreSQL y SQL Server.
* **🚀 Novedad v2.1.0:** ¡Ahora con soporte para Big Data! Procesamiento ultrarrápido con PyArrow y exportación profesional a formatos Parquet y JSON.

---

## PRÓXIMAMENTE (v2.2.0):
* **Workspaces Totales:** Puntos de guardado que incluyen el historial de chat de la IA.
* **Autoguardado Inteligente:** Respaldo automático de tu progreso en segundo plano.
* **Bóveda Transparente:** Opción de encriptación vinculada al Hardware ID (sin contraseña).
* **Patrón de Relocalización:** Recuperación automática de rutas de archivos movidos.
* **Gráficos Avanzados:** Visualización estadística integrada en el Health Check.

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