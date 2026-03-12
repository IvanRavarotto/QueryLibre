# QueryLibre 📊
Una herramienta robusta de ETL inspirada en la potencia de Power Query, desarrollada íntegramente en Python.

## 🚀 Sobre el Proyecto
QueryLibre nace de la necesidad de automatizar procesos de limpieza, transformación y carga de datos (ETL) sin depender exclusivamente de software privativo. El objetivo es recrear la experiencia intuitiva de Power Query de Excel, aprovechando la flexibilidad de Python y la robustez de MySQL.

Este proyecto está diseñado tanto para uso personal en la optimización de flujos de trabajo como para demostrar habilidades avanzadas en ingeniería de datos y desarrollo de software.

## 🛠️ Tecnologías Principales
Lenguaje: Python 3.x

Entorno de Desarrollo: VS Code

Base de Datos: MySQL

Librerías Clave: Pandas (Procesamiento), SQLAlchemy (ORM/Conexión), PyYAML/Dotenv (Configuración).

## 📂 Estructura del Proyecto
Para mantener el código organizado y escalable, QueryLibre sigue esta arquitectura: <br>
QueryLibre <br>
├── src/ # Código fuente del motor de transformación<br>
│   ├── logic/ # Aquí irá el motor (lo que procesa los datos)<br>
│   │   └── extractor.py<br>
│   ├── gui/ # Aquí irá el código de la ventana<br>
│   │   └── main_window.py<br>
│   ├── extract/ # Conectores para CSV, Excel y SQL<br>
│   ├── transform/ # Lógica de limpieza y tipos de datos<br>
│   └── load/ # Scripts de carga a MySQL<br>
├── main.py # Este es el archivo que ejecutará todo<br>
├── config/ # Archivos de configuración y credenciales<br>
├── data/ # Muestras de datos para pruebas (CSVs/JSONs)<br>
├── notebooks/ # Prototipado rápido de funciones con Jupyter<br>
├── tests/ # Pruebas unitarias para validar las transformaciones<br>
├── requirements.txt # Dependencias del proyecto<br>
└── README.md

## 🎯 Objetivos de la Fase Inicial
Conectividad: Establecer un puente sólido entre archivos planos (CSV) y MySQL.

Modularidad: Crear funciones independientes para tareas comunes como eliminación de duplicados, tipado dinámico e imputación de nulos.

Interfaz: Implementar una lógica de "pasos aplicados" para auditar cada cambio en el dataset.

# ⚙️ QueryLibre - Motor de Transformación de Datos (ETL)

QueryLibre es una aplicación de escritorio desarrollada en Python, diseñada para simplificar y visualizar el proceso de Extracción y Transformación de datos (Fases E y T de un proceso ETL). Emula la lógica visual de herramientas como Power Query, permitiendo limpiar y estructurar datasets sin necesidad de escribir código en cada paso.

## 🚀 Funcionalidades Principales

* **Interfaz Gráfica Interactiva (GUI):** Desarrollada con `CustomTkinter`, ofrece un diseño moderno (Modo Oscuro nativo) y una grilla de datos interactiva (`Treeview`) para explorar el dataset en tiempo real.
* **Carga Multi-formato:** Extracción nativa de archivos `.csv`, `.xlsx` y `.xls` mediante Pandas.
* **Arsenal de Limpieza y Transformación:**
  * 🧹 Eliminación de valores nulos (NaN) y registros duplicados.
  * 🗑️ Eliminación y renombramiento dinámico de columnas.
  * 🧮 **Columnas Calculadas (Smart Parsing):** Motor matemático que detecta y limpia automáticamente símbolos de moneda (ej: `$`, `,`) antes de operar, previniendo errores de casteo.
  * 🔗 **Combinación de Textos:** Fusión de múltiples columnas de texto con selección de separadores personalizados.
* **Trazabilidad (Panel de Auditoría):** Registro secuencial y visual de cada transformación aplicada al dataset, fundamental para la transparencia del modelo de datos.
* **Máquina del Tiempo (Deshacer):** Implementación de una pila de estados (State Stack) en memoria que permite revertir cualquier transformación al instante sin pérdida de datos.
* **Protección Anti-Errores:** Escudos de validación que evitan la sobreescritura accidental de columnas y el colapso de la aplicación ante errores de formato.

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3.x
* **Manipulación de Datos:** Pandas, NumPy
* **Interfaz Gráfica:** CustomTkinter, Tkinter (Treeview)

## 📌 Próximos Pasos (En Desarrollo)
* [ ] Fase Load (L): Exportación directa del dataset limpio a una base de datos MySQL mediante SQLAlchemy.
* [ ] Creación de un instalador ejecutable (.exe).