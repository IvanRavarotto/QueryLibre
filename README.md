# 🔍 QueryLibre - Motor de Transformación de Datos (ETL)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458.svg?logo=pandas&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-GUI-darkgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

QueryLibre es una aplicación de escritorio ligera e independiente, desarrollada 100% en Python, diseñada para democratizar la limpieza y transformación de datos. Permite a los usuarios cargar, procesar, unir y exportar bases de datos sin necesidad de escribir código o depender de software pesado.

> **💡 Motivación:** Llevar la potencia del procesamiento vectorizado de Pandas a una interfaz gráfica intuitiva, similar a Power Query, pero en un entorno de código abierto y ejecución local.

---

## 📸 Interfaz de Usuario

**Pantalla de Bienvenida (Estado Inicial)**
![Inicio](assets/Inicio.JPG)

**Entorno de Trabajo (Dataset Cargado y Herramientas Activas)**
![Dataset Cargado](assets/DatasetCargado.JPG)

---

## 🚀 Características Principales

* **Carga Universal:** Soporte nativo para importar datasets en formatos `.csv`, `.xlsx` y `.xls`.
* **Data Cleaning a un Clic:**
    * Eliminación automática de filas duplicadas.
    * Depuración de valores nulos (`NaN` / `Null`).
    * Eliminación y renombrado intuitivo de columnas con validación de seguridad.
* **Feature Engineering Avanzado:**
    * **Calculadora Mágica:** Operaciones matemáticas (+, -, *, /) entre columnas numéricas con un *Smart Parser* que limpia formatos de moneda automáticamente.
    * **Fusión de Textos:** Combinación de columnas de texto con separadores personalizados y limpieza de artefactos.
* **Integración Relacional (Merge/JOIN):** Cruce visual de tablas dimensionales (Left Join, Inner Join) con pre-visualización de datos (Progressive Disclosure) y validación de llaves.
* **Sistema de Auditoría (Time Travel):** Historial en tiempo real de transformaciones aplicadas (Pila LIFO) que permite "Deshacer" acciones paso a paso y visualizar el pipeline ETL.
* **Exportación Industrial:** Descarga de los datos limpios en `.csv`, `.xlsx` o inyección directa a una base de datos relacional `.db` (SQLite).

---

## 🗺️ Roadmap (Próximas Funcionalidades)
El motor de QueryLibre está en constante evolución. Las siguientes características están planificadas para las versiones 1.1 y 2.0:

- [ ] **Dividir Columna (Split):** Separar textos en múltiples columnas mediante delimitadores.
- [ ] **Buscar y Reemplazar:** Reemplazo masivo de valores específicos en todo el dataset.
- [ ] **Filtrado Condicional:** Mantener o eliminar filas basándose en operadores lógicos (`>`, `<`, `==`).
- [ ] **Casteo de Tipos (Data Types):** Conversión visual entre Texto, Número Entero, Decimal y Fecha (`datetime`).
- [ ] **Agrupación y Resumen (Group By):** Creación de tablas dinámicas con funciones de agregación (Suma, Promedio, Conteo).

---

## 🛠️ Tecnologías Utilizadas

* **Motor Lógico:** `pandas` (Manipulación intensiva y vectorizada de DataFrames).
* **Interfaz Gráfica (GUI):** `customtkinter` (Diseño moderno, modo oscuro nativo) y `tkinter` (`Treeview` estilizado).
* **Sistema de I/O:** `os`, `sys`, `sqlite3`.
* **Empaquetado:** `pyinstaller` (Compilación a binario ejecutable `.exe` standalone).

---

## 📦 Instalación y Uso (Para usuarios finales)

No es necesario instalar Python ni librerías para usar QueryLibre.

1. Ve a la sección de **Releases** en este repositorio (panel derecho).
2. Descarga el archivo `QueryLibre.exe`.
3. Ejecútalo haciendo doble clic. *(Si Windows Defender muestra una advertencia de SmartScreen, haz clic en "Más información" -> "Ejecutar de todas formas").*

---

## 💻 Para Desarrolladores

Si deseas clonar el proyecto para auditar el código o contribuir:

1. Clona este repositorio: 
   ```bash
   git clone [https://github.com/IvanRavarotto/QueryLibre.git](https://github.com/IvanRavarotto/QueryLibre.git)