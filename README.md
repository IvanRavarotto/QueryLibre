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

## 🚀 Características Principales (v1.6.0)

* **🧠 Smart Data Profiling:** Genera gráficos automáticos y estadísticas descriptivas según el tipo de columna.
* **✨ Asistente IA:** Escaneo proactivo que sugiere limpieza de duplicados y optimización de columnas.
* **🐘 Big Data Ready:** Motor optimizado para procesar millones de filas (v1.6.0 validada con 5.8M de registros).
* **🛡️ Integridad de Datos:** Sistema de previsualización de errores de conversión y guardado basado en `.parquet`.

---

## Próximas Actualizaciones (v1.6.1 - Rendimiento y UX):**

* 🧭 **Navegación Avanzada:** Implementación de "Salto de Página" (Go-To-Page) para recorrer rápidamente datasets masivos.
* ⏳ **Feedback Visual de Carga:** Barra de progreso real para operaciones pesadas y resumen de dimensiones (filas/columnas) al finalizar la carga.
* 🛡️ **Macros con Tolerancia a Fallos:** Sistema "Try-Continue" para que la ejecución de funciones en cadena (o el Asistente IA) ignore errores menores y continúe procesando.
* ✅ **Protección de Cierre:** Diálogo inteligente (Guardar / No Guardar / Cancelar) al intentar salir de la app con cambios pendientes. (Completado en Fase 1)

**A Mediano Plazo (v1.7.0+):**
* 🔌 **Conectores a Bases de Datos:** Importación directa de tablas desde servidores SQL Server, MySQL y PostgreSQL.
* 📊 **Exportación de Insights:** Capacidad de descargar los gráficos interactivos de Matplotlib en formato `.png` o `.pdf`.
* 🧲 **Inferencia de Tipos:** Botón "Auto-Detectar" para analizar y castear los tipos de datos de todo el dataset con un solo clic.

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
3. Ejecútalo haciendo doble clic. *(Si Windows Defender muestra una advertencia de SmartScreen, haz clic en "Más información" -> "Ejecutar de todas formas").*

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