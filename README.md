# 🔍 QueryLibre - Enterprise Data Transformation & Analytics Workspace

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.2.0-150458.svg?logo=pandas&logoColor=white)
![PyArrow](https://img.shields.io/badge/PyArrow-Columnar_Engine-orange.svg)
![Cryptography](https://img.shields.io/badge/Cryptography-AES--256-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

QueryLibre es un entorno de escritorio avanzado diseñado para la optimización, limpieza y transformación estructural de grandes volúmenes de datos (ETL). Construida bajo el patrón arquitectónico **Model-View-Controller (MVC)**, la plataforma abstrae la potencia analítica vectorizada de Pandas y el almacenamiento columnar de PyArrow en una interfaz gráfica nativa de alto rendimiento, eliminando la necesidad de redactar código sintáctico para el procesamiento de datos masivos.

---

## 🛠️ Arquitectura del Sistema y Core Tecnológico

La aplicación está diseñada bajo principios de desacoplamiento estricto, garantizando estabilidad en el hilo principal de la interfaz de usuario y eficiencia extrema en el uso de memoria RAM:

* **Engine de Carga y Downcasting Automático:** Utiliza un motor de tipado inteligente que analiza los esquemas entrantes y ejecuta un sub-casteo numérico (ej. `int64` a `int8`) y conversiones a categorías cerradas (`category`), reduciendo el consumo de memoria RAM hasta en un 50%.
* **Persistencia Híbrida (.qlp Workspaces):** Los espacios de trabajo se consolidan en contenedores comprimidos de alta velocidad que empaquetan de forma nativa archivos estructurados en formato Apache Parquet (`data.parquet`) junto con esquemas relacionales y metadatos JSON (`metadata.json`).
* **Seguridad Criptográfica (Zero-Knowledge Vault):** Almacenamiento seguro de credenciales de bases de datos relacionales y API Keys utilizando cifrado simétrico **AES-256** mediante primitivas de derivación de claves PBKDF2HMAC con vectores de inicialización dinámicos (Salt).

---

## 🚀 Características Destacadas de la Versión 2.3.0

* **🤖 Analista IA Integrado:** Chatea con tus datos en lenguaje natural usando Groq o Gemini. La IA analiza, sugiere transformaciones y ejecuta macros directamente sobre tu dataset.
* **📝 Informes Ejecutivos Flotantes:** Redacta tus hallazgos en un entorno Markdown dedicado sin salir de la aplicación.
* **🛡️ Bóveda de Workspaces (.qlp):** Guarda tu progreso, historial de limpiezas y reportes en un solo archivo empaquetado. Configura si deseas proteger tus proyectos con encriptación y Contraseña Maestra o guardarlos de forma libre.

---

## 🚀 Próximas Mejoras (Roadmap v2.5.0)

El desarrollo de QueryLibre continúa de manera ágil. El próximo ciclo de iteración se enfocará en:
* **🖥️ Ventanas Desacoplables (Dual Monitor):** Separación dinámica del Chat IA y Reportes para aprovechar setups multi-pantalla.
* **🏠 Dashboard Centralizado de Bienvenida:** Panel de inicio rápido para conectar Bases de Datos SQL, cargar CSV o abrir un Workspace Reciente de inmediato.
* **📐 Cinta de Opciones Retráctil (Ribbon):** Capacidad de ocultar la barra superior para aprovechar el 100% del espacio vertical al explorar datasets masivos.
* **🔗 Relocalización Inteligente de Archivos:** Detección automática y re-vinculación si el archivo fuente original (`.csv` / `.xlsx`) cambia de carpeta en el sistema operativo.
* **💾 Autoguardado Silencioso:** Respaldo iterativo en segundo plano (caché) para prevenir cualquier pérdida de datos ante cortes de energía sin generar micro-congelamientos.

--

## 📦 Distribución y Despliegue de Producción

Para entornos donde no se disponga de intérpretes de Python configurados, QueryLibre se distribuye como un binario nativo e independiente de 64 bits optimizado para arquitecturas Windows.

### Instrucciones de Ejecución Binaria:
1. Dirígete a la sección de **Releases** en este repositorio de GitHub.
2. Descarga el paquete comprimido de la última versión estable.
3. Ejecuta el archivo binario independiente `QueryLibre_v2.2.0.exe`.

> **⚠️ Nota de Seguridad Operativa (Windows SmartScreen):** Al tratarse de un binario independiente de código abierto que no cuenta con una firma digital comercial paga, Windows Defender puede interrumpir preventivamente la primera ejecución. Para iniciar el software de forma segura, haga clic en *"Más información"* y seleccione el botón *"Ejecutar de todas formas"*.

---

## 💻 Entorno de Desarrollo y Auditoría de Código

Para clonar la solución, auditar las capas criptográficas o ejecutar contribuciones al núcleo del motor ETL, configure las dependencias siguiendo esta secuencia técnica:

1. **Clonación del Repositorio Institucional:**
   ```bash
   git clone [https://github.com/IvanRavarotto/QueryLibre.git](https://github.com/IvanRavarotto/QueryLibre.git)
   cd QueryLibre
   ```
2. **Aislamiento de Entorno Virtual (Venv):**
   En sistemas Windows (PowerShell):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   En sistemas Unix (macOS/Linux):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Instala dependencias necesarias:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Lanzamiento del Hilo Principal:**
   ```bash
   python main.py
   ```

## 🐧 Instalación en Linux (CachyOS / Arch Linux)

QueryLibre es nativamente compatible con entornos Linux. Para asegurar el correcto funcionamiento de la interfaz gráfica y el portapapeles, sigue estos pasos:

1. **Instalar dependencias del sistema:**
   Necesitarás las librerías gráficas de Tkinter y el gestor de portapapeles para poder copiar/pegar celdas.
   ```bash
   sudo pacman -S tk xclip
   ```
2. **Crear y activar el entorno virtual:**
   Clona el repositorio y crea un entorno aislado. (Nota: Si usas la terminal `fish`, asegúrate de usar el activador correcto).
   ```bash
   python -m venv venv source venv/bin/activate.fish  # Usa 'activate' a secas si usas bash o zsh
   ```
3. **Instalar dependencias del proyecto:**
   ```bash
   pip install -r requirements.txt
   ```
   Opcional: Si el sistema lanza advertencias de módulos no encontrados en tu editor, fuerza la instalación de los pilares gráficos y de IA:
   ```bash
   pip install customtkinter pandas numpy sqlalchemy cryptography openai
   ```

## 🧪 Suite de Pruebas Unitarias (QA)
El core analítico cuenta con una cobertura de pruebas lógicas automatizadas mediante pytest para blindar la integridad del motor ante nuevas actualizaciones.

**Para ejecutar los vectores de prueba de regresión:**
   ```Bash
   python -m pytest tests/
   ```