# ⚙️ QueryLibre - Motor de Transformación de Datos (ETL)

QueryLibre es una aplicación de escritorio desarrollada en Python, diseñada para simplificar y visualizar el proceso de Extracción, Transformación y Carga de datos (ETL). Emula la lógica visual de herramientas como Power Query, permitiendo limpiar y estructurar datasets sin necesidad de escribir código en cada paso.

## 🚀 Funcionalidades Principales

* **Interfaz Gráfica Interactiva (GUI):** Desarrollada con `CustomTkinter`, ofrece un diseño moderno (Modo Oscuro nativo) y una grilla de datos interactiva (`Treeview`) para explorar el dataset en tiempo real.
* **Extracción Multi-formato (Fase E):** Carga nativa de archivos `.csv`, `.xlsx` y `.xls` mediante Pandas.
* **Arsenal de Transformación (Fase T):**
  * 🧹 Eliminación de valores nulos (NaN) y registros duplicados.
  * 🗑️ Eliminación y renombramiento dinámico de columnas.
  * 🧮 **Columnas Calculadas (Smart Parsing):** Motor matemático que detecta y limpia automáticamente símbolos de moneda antes de operar.
  * 🔗 **Cruce de Datos (Merge/JOIN):** Unión relacional de múltiples datasets con previsualización de tablas en tiempo real.
  * 🛡️ **Máquina del Tiempo (Deshacer):** Pila de estados en memoria que permite revertir transformaciones sin pérdida de datos.
* **Exportación Universal (Fase L):** Guardado del dataset procesado y limpio en formatos `.csv`, `.xlsx` o inyección directa a una base de datos relacional local `.db` (SQLite).

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3.x
* **Manipulación de Datos:** Pandas, NumPy
* **Interfaz Gráfica:** CustomTkinter, Tkinter (Treeview)
* **Bases de Datos:** SQLite, SQLAlchemy

## 📌 Próximos Pasos
* [ ] Compilación y empaquetado del proyecto en un instalador ejecutable (.exe) para uso independiente (Standalone).