# Registro de Cambios / Changelog

All notable changes to the **QueryLibre** project will be documented in this file.
Todos los cambios notables en el proyecto **QueryLibre** serán documentados en este archivo.

---

## [1.4.1] - 2026-03-31
### English
#### Added
* **Stress data generator:** New `data_test/generador_datos.py` writes `ventas_caoticas_exigente.csv` with edge-case corrupt values (strings in numeric columns, malformed dates, price anomalies, duplicates, nans).
* **Robust tests:** `tests/test_data_engine.py` uses the new “exigente” dataset and checks rollback on failed type conversions (ID_Cliente number conversion + Fecha conversion), operator pipeline, filter+dedupe and merge behavior.

#### Fixed
* `MotorDatos.cambiar_tipo_dato` now uses safe coercion and reverts state on failure, plus throws informative `RuntimeError`.
* `MotorDatos.aplicar_union` now recovers `df` on merge faults.
* `cargar_archivo` normalizes whitespace in column names (`str.strip`) for robust loading.
* UI `cambiar_tipo_dato` insert error label and better failure messages.
* Removed console emoji print causing `UnicodeEncodeError` on cp1252 environments (Windows) in `generador_datos.py`.

#### Changed
* Updated app version label in UI from 1.4.0 to 1.4.1.
* Added explicit integer/object dtype coercion paths for demanding sample data; format parser tolerates $ and comma separators.

#### Future Steps
* Add `pytest` to the `requirements.txt` and CI pipeline.
* Add a dedicated spec for `test_data_engine.py` to assert macro serialization and undo stack + history consistency.
* Implement column type inference preview before cast in GUI to reduce user risk.

### Español
#### Añadido
* **Generador de datos exigentes:** `data_test/generador_datos.py` genera `ventas_caoticas_exigente.csv` con valores extremos y corruptos.
* **Tests resilientes:** `tests/test_data_engine.py` ataca el pipeline completo y fuerza errores de conversión y rollback.

#### Corregido
* `MotorDatos.cambiar_tipo_dato`: ahora hace rollback si falla y lanza `RuntimeError` claro.
* `MotorDatos.aplicar_union`: restauración de df si hay error de unión.
* `cargar_archivo`: limpieza de espacios en nombres de columnas.
* `main.py`: mejor manejo de errores de conversión en el modal y texto de error.
* `generador_datos.py`: quitado emoji en salida para evitar `UnicodeEncodeError` en Windows.

#### Cambios
* Etiqueta de versión en UI `QueryLibre v1.4.1`.
* Se añadió parsing de `ID_Cliente`, `Cantidad`, `precio_unitario_usd`, `Fecha Compra` con validaciones.

#### Pasos Futuros
* Instalar `pytest` en requirements y flujo CI.
* Añadir test de macro + undo histórico.
* Añadir aviso de preview antes de casteo en GUI.

---

## [1.4.0] - 2026-03-30
### English
#### Added
* **Workspace Tabs:** New architecture to work with multiple datasets simultaneously. Each tab maintains its own engine and history.
* **Macro Engine (JSON):** Automation tool that records transformations and allows saving/loading them for future datasets.
* **Data Profiling:** Real-time analysis panel for column auditing (Nulls, Unique values, Min/Max/Average).
* **Smart Data Casting:** Forced conversion of data types (Text, Int, Decimal, Date) with a smart currency parser.

#### Changed
* **Ribbon UI:** Restructured toolbar into categorized drop-down menus (Cleaning, Structure, Analysis).
* **Consistent Dark Mode:** Removed transient dependencies to force native dark mode in Windows 11 dialogs.
* **Icon Propagation:** Implemented a native patch to ensure all child windows inherit the application logo.

### Español
#### Añadido
* **Sistema de Pestañas (Workspace Tabs):** Arquitectura renovada que permite cargar y trabajar con múltiples datasets en simultáneo.
* **Motor de Macros (JSON):** Herramienta de automatización que graba transformaciones y permite guardarlas/cargarlas para nuevos datasets.
* **Radiografía de Datos (Data Profiling):** Panel de análisis en tiempo real para auditar columnas (Nulos, Únicos, Mínimo/Máximo/Promedio).
* **Casteo Inteligente de Datos:** Conversión forzada de tipos de datos (Texto, Entero, Decimal, Fecha) con parser de moneda inteligente.

#### Cambios
* **Interfaz Agrupada (Ribbon UI):** Se reestructuró la barra de herramientas en menús desplegables categorizados (Limpieza, Estructura, Análisis).
* **Modo Oscuro Consistente:** Eliminación de dependencias transitorias para forzar el modo oscuro en diálogos de Windows 11.
* **Propagación de Íconos:** Parche nativo para garantizar que todas las ventanas hereden el logo de la aplicación.

---

## [1.3.0] - 2026-03-29
### English
#### Added
* **Inline Cell Editing:** Directly modify cell values with double-click and undo support.
* **Advanced Transforms:** Added `✂️ Split Column` and `🚦 Filter Data` (conditional filtering).

#### Changed
* **MVC Pattern:** Full decoupling of Pandas logic from the GUI into a dedicated `data_engine.py`.

### Español
#### Añadido
* **Edición Directa:** Modificación de celdas mediante doble clic con soporte para deshacer (Undo).
* **Transformaciones Avanzadas:** Se sumaron las funciones de `✂️ Dividir Columna` y `🚦 Filtrar Datos`.

#### Cambios
* **Patrón MVC:** Desacoplamiento total de la lógica de Pandas de la interfaz gráfica en un motor dedicado.

---

## [1.2.0] - 2026-03-27
### English
#### Added
* **Data Pagination:** New navigation system (200 rows per page) for fluid exploration of large datasets.
* **Visual Row Index:** Added a static `#` column for easier data tracking.

#### Fixed
* **Layout Refinement:** Improved scrollbar integration with pagination controls.

### Español
#### Añadido
* **Paginación de Datos:** Sistema de navegación (200 filas por hoja) para explorar datasets grandes de forma fluida.
* **Índice Visual:** Columna estática `#` para facilitar el seguimiento de registros.

#### Corregido
* **Refinamiento de UI:** Mejor integración de barras de desplazamiento con los controles de paginación.

---

## [1.1.1] - 2026-03-26
### English
#### Added
* **Dynamic Dimensions Indicator:** Real-time row and column counter in the status bar.

#### Changed
* **Interactive Null Cleaning:** UX improvement to choose between "All" or "Any" null removal.

### Español
#### Añadido
* **Indicador de Dimensiones:** Contador de filas y columnas en tiempo real en la barra de estado.

#### Cambios
* **Limpieza de Nulos Interactiva:** Mejora en la UX para elegir entre eliminar filas con algún nulo o solo las vacías.

---

## [1.1.0] - 2026-03-26
### English
#### Added
* "About" window with project info and Roadmap.

### Español
#### Añadido
* Ventana de "Acerca de" con información del proyecto y Roadmap.

---

## [1.0.0] - 2026-03-23
### English
#### Added
* Initial release of the ETL engine.
* Universal loader (.csv, .xlsx, .xls) and multi-format export (CSV, Excel, SQLite).
* Basic cleaning: duplicates, nulls, rename/drop columns.
* Math calculator, text merging, and visual Merge/JOIN.

### Español
#### Añadido
* Lanzamiento inicial del motor ETL.
* Carga universal (.csv, .xlsx, .xls) y exportación multiformato (CSV, Excel, SQLite).
* Limpieza básica: duplicados, nulos, renombrar/eliminar columnas.
* Calculadora matemática, combinación de textos y Merge/JOIN visual.