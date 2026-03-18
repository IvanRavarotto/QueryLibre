# 🔍 QueryLibre - Motor de Transformación de Datos (ETL)

QueryLibre es una aplicación de escritorio ligera e independiente, desarrollada 100% en Python, diseñada para democratizar la limpieza y transformación de datos. Permite a los usuarios cargar, procesar, unir y exportar bases de datos sin necesidad de escribir una sola línea de código o usar software pesado como Excel o Power Query.

## 🚀 Características Principales

* **Carga Universal:** Soporte nativo para importar datasets en formatos `.csv`, `.xlsx` y `.xls`.
* **Limpieza de Datos con un Clic:**
    * Eliminación automática de filas duplicadas.
    * Depuración de valores nulos (NaN/Null).
    * Eliminación y renombrado intuitivo de columnas.
* **Ingeniería de Características (Feature Engineering):**
    * Calculadora de columnas: Operaciones matemáticas (+, -, *, /) entre columnas numéricas con parseo inteligente.
    * Fusión de textos: Combinación de columnas de texto con separadores personalizados.
* **Cruce de Datos (Merge/JOIN):** Integración de tablas dimensionales secundarias mediante cruces relacionales (Left Join, Inner Join) de forma visual.
* **Historial de Pasos (Time Travel):** Sistema de registro de transformaciones que permite visualizar el pipeline aplicado y "Deshacer" (Undo) acciones paso a paso.
* **Exportación Multiformato:** Descarga de los datos limpios en `.csv`, `.xlsx` o directamente inyectados en una base de datos relacional `.db` (SQLite).

## 🛠️ Tecnologías Utilizadas

* **Lógica de Datos:** `Pandas` (Manipulación intensiva y vectorizada de DataFrames).
* **Interfaz Gráfica (GUI):** `CustomTkinter` (Diseño moderno, modo oscuro nativo) y `Tkinter` (Treeview para renderizado de tablas).
* **Sistema y Archivos:** `os`, `sys`, `sqlite3`.
* **Empaquetado:** `PyInstaller` (Compilación a binario ejecutable `.exe` standalone).

## 📦 Instalación y Uso (Para usuarios sin Python)

No es necesario instalar Python ni librerías para usar QueryLibre.

1. Ve a la sección de **Releases** en este repositorio (lado derecho de la pantalla).
2. Descarga el archivo `QueryLibre.exe`.
3. Haz doble clic para ejecutarlo (Si Windows Defender muestra una advertencia, haz clic en "Más información" -> "Ejecutar de todas formas").

## 💻 Para Desarrolladores

Si deseas clonar el proyecto para ver el código o contribuir:

1. Clona este repositorio: `git clone https://github.com/IvanRavarotto/QueryLibre.git`
2. Instala las dependencias: `pip install -r requirements.txt`
3. Ejecuta la aplicación: `python main.py`