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

## 🚀 Características Principales (v1.4.3)

> **Patch v1.4.3:** Hardening de macros, sanitización mejorada de exportación (fórmulas con `'`), validación de carga más estricta y UI de filas inválidas con copy/export.

* **Arquitectura Escalable (MVC):** Motor de datos (`core/data_engine.py`) completamente desacoplado de la interfaz gráfica.
* **Sistema de Pestañas (Workspace):** Soporte nativo para importar y trabajar con múltiples datasets en simultáneo en la misma sesión, sin colisión de datos.
* **Automatización con Macros:** Graba pipelines de transformación completos, expórtalos en formato `.json` y ejecútalos con un clic sobre nuevos datasets sucios.
* **Data Cleaning a un Clic (Ribbon UI):**
    * Eliminación automática de filas duplicadas y valores nulos (`NaN` / `Null`).
    * Eliminación y renombrado intuitivo de columnas mediante menús desplegables blindados.
    * **Casteo Inteligente de Tipos:** Conversión forzada de texto a números enteros/decimales o fechas, con un *Smart Parser* que esquiva errores causados por símbolos (`$`, `,`) o celdas vacías.
* **Feature Engineering Avanzado:**
    * **Radiografía de Datos (Profiling):** Panel estadístico en tiempo real por columna (Valores únicos, % de nulos, min/max, promedios).
    * **Calculadora Mágica:** Operaciones matemáticas vectorizadas entre columnas.
    * **Dividir y Combinar Columnas:** Herramientas de parsing de texto por delimitadores.
    * **Filtrado Condicional:** Segmentación de filas mediante operadores lógicos.
* **Interacción Directa:** Modificación de celdas individuales al estilo Excel (Doble clic).
* **Integración Relacional (Merge/JOIN):** Cruce visual de tablas dimensionales (Left Join, Inner Join).
* **Sistema de Auditoría (Time Travel):** Historial en tiempo real de transformaciones (Pila LIFO) para deshacer acciones paso a paso.
* **Exportación Industrial:** Descarga de los datos en `.csv`, `.xlsx` o bases de datos `.db` (SQLite).

---

## 🗺️ Roadmap (Próximas Funcionalidades - v1.5.0+)
El motor de QueryLibre está diseñado para crecer hacia el estándar "Enterprise". Lo siguiente en la lista es:

- [ ] **Agrupación y Resumen (Group By):** Creación de tablas dinámicas con funciones de agregación (Suma, Promedio, etc.).
- [ ] **Panel de Salud Global (Quality Score):** Dashboard en la barra lateral con métricas globales del dataset (Filas, % total de nulos, Memoria RAM usada).
- [ ] **Buscar y Reemplazar Global:** Búsqueda y reemplazo masivo de valores mediante texto o Regex.
- [ ] **Pestañas Avanzadas:** Cierre de pestañas individual, reordenamiento dinámico e indicador de "cambios sin guardar".
- [ ] **Visualizaciones Inline:** Integración de gráficos rápidos (Histogramas/Boxplots) en la ventana de Radiografía.

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
- 6 passed, 1 warning

> Nota: se muestra un warning de pandas para `pd.to_datetime` que termina siendo no bloqueante, solo informativo.