QueryLibre 📊
Una herramienta robusta de ETL inspirada en la potencia de Power Query, desarrollada íntegramente en Python.

🚀 Sobre el Proyecto
QueryLibre nace de la necesidad de automatizar procesos de limpieza, transformación y carga de datos (ETL) sin depender exclusivamente de software privativo. El objetivo es recrear la experiencia intuitiva de Power Query de Excel, aprovechando la flexibilidad de Python y la robustez de MySQL.

Este proyecto está diseñado tanto para uso personal en la optimización de flujos de trabajo como para demostrar habilidades avanzadas en ingeniería de datos y desarrollo de software.

🛠️ Tecnologías Principales
Lenguaje: Python 3.x

Entorno de Desarrollo: VS Code

Base de Datos: MySQL

Librerías Clave: Pandas (Procesamiento), SQLAlchemy (ORM/Conexión), PyYAML/Dotenv (Configuración).

📂 Estructura del Proyecto
Para mantener el código organizado y escalable, QueryLibre sigue esta arquitectura: <br>
QueryLibre <br>
├── src/ # Código fuente del motor de transformación<br>
│   ├── extract/ # Conectores para CSV, Excel y SQL<br>
│   ├── transform/ # Lógica de limpieza y tipos de datos<br>
│   └── load/ # Scripts de carga a MySQL<br>
├── config/ # Archivos de configuración y credenciales<br>
├── data/ # Muestras de datos para pruebas (CSVs/JSONs)<br>
├── notebooks/ # Prototipado rápido de funciones con Jupyter<br>
├── tests/ # Pruebas unitarias para validar las transformaciones<br>
├── requirements.txt # Dependencias del proyecto<br>
└── README.md

🎯 Objetivos de la Fase Inicial
Conectividad: Establecer un puente sólido entre archivos planos (CSV) y MySQL.

Modularidad: Crear funciones independientes para tareas comunes como eliminación de duplicados, tipado dinámico e imputación de nulos.

Interfaz: Implementar una lógica de "pasos aplicados" para auditar cada cambio en el dataset.