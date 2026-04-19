# Registro de Cambios / Changelog

All notable changes to the **QueryLibre** project will be documented in this file.
Todos los cambios notables en el proyecto **QueryLibre** serán documentados en este archivo.

## [1.7.0] - 2026-04-18
### English
#### Added
* **Interactive Correlation (BI):** New Scatter Plot tool to analyze relationships between numeric columns.
* **View Synchronization:** Clicking a point on the scatter plot automatically navigates the main data grid to the exact row and highlights it.
* **Custom Navigation Toolbar:** Fully integrated, Spanish-translated Matplotlib controls (Zoom, Pan, Home) matching the dark theme.
* **Export Insights:** Users can now export generated plots directly to `.png` or `.pdf`.

### Español
#### Añadido
* **Correlación Interactiva (BI):** Nueva herramienta de Gráfico de Dispersión para analizar relaciones entre variables numéricas.
* **Sincronización de Vistas:** Al hacer clic en un punto del gráfico, la cuadrícula de datos principal viaja automáticamente a esa fila y la resalta.
* **Barra de Navegación Personalizada:** Controles de Matplotlib (Zoom, Mover) traducidos al español e integrados al tema oscuro nativo.
* **Exportación de Reportes:** Los usuarios ahora pueden descargar los gráficos generados en formato `.png` o `.pdf`.

---

## [1.6.4] - 2026-04-18
### English
#### Added
* **Time Travel (Redo Stack):** Implemented full `Ctrl+Y` functionality, allowing users to restore undone actions securely.
* **Scatter Plot Scaffold:** Prepared the UI architecture for the upcoming interactive correlation charts.

#### Fixed
* **State Management:** Fixed the "dirty flag" bug where the app incorrectly prompted to save when undoing back to the original load state.
* **Loader Optimization:** Removed a duplicate initialization step (Ninja bug) that could crash the engine when loading non-CSV files.

### Español
#### Añadido
* **Viaje en el Tiempo (Rehacer):** Se implementó la funcionalidad `Ctrl+Y`, permitiendo recuperar acciones deshechas de forma segura.
* **Estructura Scatter Plot:** Se preparó la arquitectura de la interfaz para los próximos gráficos interactivos de correlación.

#### Corregido
* **Gestión de Estados:** Se corrigió el error del "asterisco" que pedía guardar cambios al deshacer todo hasta el archivo original.
* **Optimización de Carga:** Se eliminó un paso de inicialización duplicado que podía generar cierres inesperados al cargar archivos Excel.

---

## [1.6.3] - 2026-04-16
### English
#### Added
* **Health Check Dashboard:** Automated data profiling showing RAM usage, health percentage, and data types upon loading.
* **Intelligent Auto-Cast:** Two-step assistant that detects potential numeric/date conversions and asks for confirmation.
* **Fault-Tolerant Macros:** Macros now skip incompatible steps (e.g., missing columns) instead of aborting the entire process.
* **Project Refactor:** Unified testing environment under a single `tests/` directory following industry standards.

#### Fixed
* **Memory Optimization:** Reduced RAM peak by 35% during auto-casting by avoiding full dataset cloning.
* **UI Collision:** Fixed a bug where "Auto-Detect Types" would trigger the wrong menu action.

### Español
#### Añadido
* **Dashboard de Salud:** Perfilado automático que muestra uso de RAM, % de salud y tipos de datos al cargar el archivo.
* **Auto-Casteo Inteligente:** Asistente de dos pasos que detecta conversiones a números/fechas y solicita confirmación del usuario.
* **Macros Resilientes:** Las macros ahora saltan pasos incompatibles (ej. columnas faltantes) en lugar de abortar todo el proceso.
* **Refactorización:** Unificación del entorno de pruebas bajo una única carpeta `tests/` siguiendo estándares profesionales.

#### Corregido
* **Optimización de Memoria:** Reducción del pico de RAM en un 35% durante el auto-casteo al evitar clonaciones innecesarias.
* **Colisión de UI:** Se corrigió el error donde "Auto-Detectar Tipos" activaba la acción de menú incorrecta.

---

## [1.6.2] - 2026-04-15
### English
#### Added
* **Advanced Navigation:** Added a "Go-To" page jump input and a rapid column search bar for massive datasets.
* **Chunked Export:** Implemented asynchronous CSV export in blocks of 100,000 rows to prevent UI freezing (Not Responding) on Big Data.
* **Smart Progress UI:** Replaced static loading text with a dynamic progress bar and a final success summary (rows/columns loaded).

#### Fixed
* **Concurrency:** Fixed an issue where the success message overlapped with the loading screen by ensuring UI cleanup runs first in the main thread.
* **Treeview Rendering:** Fixed the visual `#` index column disappearing when applying column search filters.

### Español
#### Añadido
* **Navegación Avanzada:** Se agregó un campo de "Salto de Página" (Go-To) y un buscador rápido de columnas para datasets masivos.
* **Exportación Fragmentada:** Implementación de exportación CSV asíncrona en bloques de 100.000 filas para evitar el congelamiento de la interfaz (Big Data).
* **UI de Progreso Inteligente:** Se reemplazó el texto estático por una barra de progreso dinámica y un resumen final de éxito (filas/columnas cargadas).

#### Corregido
* **Concurrencia:** Se solucionó un problema donde el mensaje de éxito se superponía a la pantalla de carga, asegurando la limpieza previa en el hilo principal.
* **Renderizado de Treeview:** Se corrigió la desaparición de la columna visual de índice `#` al aplicar filtros de búsqueda de columnas.

---

## [1.6.1] - 2026-04-14 (En Desarrollo)
### English
#### Added
* **Safe Close Protocol:** Implemented a Save/Don't Save/Cancel dialog when closing the app with unsaved changes.
* **Keyboard Shortcuts:** Added global hotkeys for Save (Ctrl+S), Undo (Ctrl+Z), and Redo (Ctrl+Y).

#### Fixed
* **Memory Leak:** Fixed RAM accumulation in the Profiling panel by explicitly clearing Matplotlib figures.
* **Technical Debt:** Cleaned up test generation artifacts and removed deprecated `fix_tests.py`.

### Español
#### Añadido
* **Cierre Seguro:** Se implementó un diálogo de Guardar/No Guardar/Cancelar al cerrar la app con cambios pendientes.
* **Atajos de Teclado:** Se agregaron atajos globales para Guardar (Ctrl+S), Deshacer (Ctrl+Z) y Rehacer (Ctrl+Y).

#### Corregido
* **Fuga de Memoria:** Se solucionó la acumulación de memoria RAM en el panel de Radiografía cerrando las figuras de Matplotlib explícitamente.
* **Deuda Técnica:** Limpieza de artefactos de generación de pruebas y eliminación del archivo obsoleto `fix_tests.py`.

---

## [1.6.0] - 2026-04-13
### English
#### Added
* **Data Visualization:** Integrated Matplotlib for dynamic histograms and bar charts in the "Radiografía" panel.
* **Smart Cleaning Assistant:** New module that scans datasets for duplicates and useless columns, suggesting automatic fixes.
* **Safe Type Casting:** Added a "Simulate & Preview" feature that detects conversion errors before applying changes.
* **Big Data Support:** Confirmed stable processing of 5.8M+ rows (exceeding Excel's 1M limit).

#### Fixed
* **PyArrow Engine:** Fixed "Expected bytes, got int" error by forcing string conversion for mixed types during savepoints.
* **UI/UX:** Fixed missing app icons in secondary modals and added memory cleanup for Matplotlib figures.

### Español
#### Añadido
* **Visualización de Datos:** Integración de Matplotlib para histogramas y gráficos de barras dinámicos en el panel de Radiografía.
* **Asistente de Limpieza Inteligente:** Nuevo módulo que escanea el dataset buscando duplicados y columnas inútiles, sugiriendo arreglos automáticos.
* **Casteo de Datos Seguro:** Función de "Simular y Previsualizar" que detecta errores de conversión antes de aplicar cambios.
* **Soporte Big Data:** Procesamiento estable confirmado de más de 5.8M de filas (superando el límite de 1M de Excel).

#### Corregido
* **Motor PyArrow:** Corregido error de tipos mixtos en el guardado de seguridad (_savepoint) mediante conversión forzada a texto.
* **UI/UX:** Se agregaron íconos faltantes en modales secundarios y limpieza de memoria RAM en los gráficos.
  
---

## [1.5.5] - 2026-04-11
### English
#### Fixed
* **Security (Zip Bomb):** Added a 500MB RAM decompression limit when loading `.qlp` projects to prevent malicious files from freezing the system.
* **Memory Leak:** Fixed an issue where closing tabs did not free up physical RAM by explicitly destroying the Tkinter widgets before deletion.

#### Changed
* **Code Refactoring (DRY):** Unified the tab creation logic into a single internal method (`_crear_tab_ui`) to improve code maintainability and prevent duplicate UI bugs.

### Español
#### Corregido
* **Seguridad (Zip Bomb):** Se agregó un límite de descompresión en RAM de 500MB al cargar proyectos `.qlp` para evitar que archivos maliciosos congelen el sistema.
* **Fuga de Memoria (Memory Leak):** Se solucionó un problema por el cual cerrar pestañas no liberaba la memoria RAM física, destruyendo explícitamente los widgets de Tkinter antes de borrarlos.

#### Cambios
* **Refactorización de Código (DRY):** Se unificó la lógica de creación de pestañas en un único método interno (`_crear_tab_ui`) para mejorar el mantenimiento del código y prevenir bugs de UI duplicados.

---

## [1.5.4] - 2026-04-10
### English
#### Added
* **Project System (.qlp):** Introduced a custom compressed file format to save and load entire workspaces (Datasets + Macro History).
* **Dirty Flag Indicator:** Tabs now display an asterisk (`*`) when there are unsaved changes.
* **Safe Close Protocols:** Added warning dialogs when closing a specific tab (Ctrl+W) or the entire application with unsaved changes.

#### Changed
* **Isolated Caching:** Refactored the temporary cache system to use nested subdirectories (`tab_<id>`) inside a master cache folder, preventing memory conflicts between multiple open datasets.

#### Fixed
* **Sidebar Styling:** Restored visual consistency for the new Project buttons in the UI.

### Español
#### Añadido
* **Sistema de Proyectos (.qlp):** Introducción de un formato de archivo comprimido personalizado para guardar y cargar espacios de trabajo completos (Datasets + Historial de Macros).
* **Indicador de Cambios:** Las pestañas ahora muestran un asterisco (`*`) cuando hay cambios sin guardar en el motor.
* **Protocolos de Cierre Seguro:** Se agregaron diálogos de advertencia al intentar cerrar una pestaña específica (Ctrl+W) o la aplicación completa con cambios pendientes.

#### Cambios
* **Caché Aislada:** Se refactorizó el sistema de caché temporal para usar subcarpetas anidadas (`tab_<id>`) dentro de una carpeta maestra, evitando conflictos de memoria entre múltiples datasets abiertos.

#### Corregido
* **Estilos del Panel Lateral:** Se restauró la consistencia visual de los nuevos botones de Proyecto en la interfaz.

---

## [1.5.3] - 2026-04-09
### English
#### Added
* **Disk-Based Caching:** Migrated the Undo history from RAM to temporary `.parquet` files using `pyarrow`, eliminating memory bottlenecks for large datasets.
* **Garbage Collection:** Added an `on_closing` protocol to automatically clean up temporary `.ql_cache` directories upon application exit.
* **Security (ReDoS):** Implemented regex syntax validation in the Search/Replace engine to prevent CPU freezing from malicious expressions.

#### Fixed
* **Thread Stability & UI Recovery:** Overhauled the multi-threading error handler to prevent the UI from freezing or turning blank when a Pandas operation fails.
* **Silent Rollback:** Fixed a critical bug where failed data casting operations corrupted the internal DataFrame structure.

#### Changed
* **Architecture Refactoring:** Extracted the massive `PestanaTrabajo` class from `main.py` into a dedicated `ui/tabs.py` module, improving code maintainability.

### Español
#### Añadido
* **Caché en Disco:** Migración del historial de Deshacer de la memoria RAM a archivos `.parquet` temporales usando `pyarrow`, eliminando cuellos de botella de memoria en datasets gigantes.
* **Recolección de Basura:** Se agregó un protocolo `on_closing` para limpiar automáticamente la carpeta temporal `.ql_cache` al cerrar la aplicación.
* **Seguridad (ReDoS):** Implementación de validación de sintaxis Regex en el motor de Buscar/Reemplazar para evitar el congelamiento de CPU por expresiones infinitas.

#### Corregido
* **Estabilidad de Hilos y Recuperación UI:** Se reescribió el manejador de errores del multithreading para evitar que la interfaz se quede en blanco o trabada al fallar una operación de Pandas.
* **Rollback Silencioso:** Se corrigió un error crítico donde un fallo al convertir tipos de datos corrompía la estructura interna del DataFrame.

#### Cambios
* **Refactorización de Arquitectura:** Se extrajo la clase `PestanaTrabajo` de `main.py` a su propio archivo `ui/tabs.py`, reduciendo drásticamente la complejidad del código principal.

---

## [1.5.2] - 2026-04-08
### English
#### Fixed
* **Infrastructure Refactoring:** Modularized UI dialogs (About, Profiling, Cleaning, etc.) into a dedicated `ui/modals.py` for improved code maintainability.
* **Async Processing:** Implemented multi-threading (Async) for all data transformation tasks to prevent UI freezing ("Not Responding") on long-running processes.
* **Button Lock Logic:** Fixed a deadlock issue where UI controls remained disabled after quick background tasks.

### Español
#### Corregido
* **Refactorización de Infraestructura:** Se modularizaron los diálogos de la interfaz (Acerca de, Radiografía, Limpieza, etc.) en un archivo dedicado `ui/modals.py` para mejorar el mantenimiento del código.
* **Procesamiento Asíncrono:** Implementación de multihilos (Threading) para todas las tareas de transformación de datos, evitando que la interfaz se congele ("No responde") en procesos largos.
* **Lógica de Bloqueo:** Se corrigió un error de bloqueo donde los controles de la interfaz permanecían desactivados tras finalizar tareas rápidas en segundo plano.

---

## [1.5.1] - 2026-04-07
### English
#### Fixed
* **Memory Optimization:** Added a 10-step limit to the Undo history (`df_history`) to prevent Out of Memory (OOM) crashes on large datasets.
* **State Management:** Added internal logic to track unsaved changes in the workspace (preparation for visual Dirty Flag).

### Español
#### Corregido
* **Optimización de Memoria:** Se agregó un límite de 10 pasos al historial de Deshacer (`df_history`) para evitar bloqueos por falta de memoria RAM en datasets grandes.
* **Gestión de Estado:** Se agregó lógica interna para rastrear cambios no guardados en el espacio de trabajo (preparación para el indicador visual).

---

## [1.5.0] - 2026-04-05
### English
#### Added
* New Group By feature: `agrupar_datos()` method supporting aggregation functions (sum, mean, count, min, max) with column validation.
* New Search/Replace feature: `buscar_reemplazar()` method supporting global or column-specific text replacement with optional regex support.
* Updated macro whitelist to include `agrupar_datos` and `buscar_reemplazar` actions.
* Comprehensive test suite expanded with 8 new tests covering Group By and Search/Replace functionality, including edge cases and error handling.

#### Fixed
* Resolved test failures by implementing missing methods and updating security configurations.

### Español
#### Añadido
* Nueva función Group By: método `agrupar_datos()` que soporta funciones de agregación (suma, promedio, conteo, mínimo, máximo) con validación de columnas.
* Nueva función Buscar/Reemplazar: método `buscar_reemplazar()` que soporta reemplazo de texto global o específico por columna con soporte opcional para expresiones regulares.
* Lista blanca de macros actualizada para incluir acciones `agrupar_datos` y `buscar_reemplazar`.
* Suite de pruebas completa expandida con 8 nuevas pruebas que cubren funcionalidad de Group By y Buscar/Reemplazar, incluyendo casos límite y manejo de errores.

#### Corregido
* Resueltos fallos en pruebas implementando métodos faltantes y actualizando configuraciones de seguridad.

---

## [1.4.5] - 2026-04-04
### English
#### Added
* Macro parameter type validation: only allows safe value types (str, int, float, bool, list, dict) to prevent injection attacks.
* Additional security tests for macro parameter fuzzing with unsafe values.

#### Fixed
* Enhanced macro execution security against complex object injection.

### Español
#### Añadido
* Validación de tipos de parámetros de macros: solo permite tipos de valores seguros (str, int, float, bool, list, dict) para prevenir ataques de inyección.
* Pruebas de seguridad adicionales para fuzzing de parámetros de macros con valores inseguros.

#### Corregido
* Seguridad mejorada en ejecución de macros contra inyección de objetos complejos.

---

## [1.4.4] - 2026-04-03
### English
#### Added
* Macro execution rollback on failed step; restores dataset state if a macro run crashes.
* Column normalization now converts spaces to underscores and resolves duplicate column names in `core/data_engine.py`.
* App version updated to `v1.4.4` in the UI and About dialog.
* Enhanced macro security: fuzz-resistant parameter validation rejecting dangerous keys like `__class__`, `__dict__`.
* Additional tests for macro fuzzing and invalid action blocking.
* Macro parameter value validation: only allows safe types (str, int, float, bool, list, dict) to prevent injection.

#### Fixed
* `aplicar_union` now supports normalized column names with potential conflicts after cleaning.
* Added tests for macro rollback and normalized join conflict.
* Updated dependencies to mitigate known vulnerabilities (pillow, pygments, requests, tornado, urllib3).

### Español
#### Añadido
* Ejecución de macros ahora hace rollback si un paso falla y restaura el estado previo del dataset.
* Normalización de columnas en `core/data_engine.py` convierte espacios a guiones bajos y resuelve duplicados con sufijos.
* Actualización de versión a `v1.4.4` en la UI y en el panel Acerca de.
* Seguridad de macros mejorada: validación de parámetros resistente a fuzz, rechazando claves peligrosas como `__class__`, `__dict__`.
* Pruebas adicionales para fuzzing de macros y bloqueo de acciones inválidas.
* Validación de valores de parámetros de macros: solo permite tipos seguros (str, int, float, bool, list, dict) para evitar inyección.

#### Corregido
* `aplicar_union` ahora maneja columnas normalizadas con potenciales conflictos.
* Se agregaron pruebas para rollback de macro y conflicto de columnas en unión.
* Dependencias actualizadas para mitigar vulnerabilidades conocidas (pillow, pygments, requests, tornado, urllib3).

---

## [1.4.3] - 2026-04-02
### English
#### Added
* Macro execution now rejects parameter keys starting with `__` and known dangerous keys in `main.py` for safer JSON macro playback.
* Export sanitization in `core/data_engine.py` expanded to handle `'`-escaped formulas (`'=...`) and formula-like values with leading spaces.
* Loader hardening for `cargar_archivo`/`cargar_df2`: path normalization checks, no `..` in relative paths, only `.csv`, `.xls`, `.xlsx`.
* UI: conversion modal (`Cambiar Tipo`) now display invalid rows table with adaptive height/scroll and “Copiar al portapapeles”.
* Global logging via RotatingFileHandler written to `querylibre.log`.

#### Fixed
* `MotorDatos._validate_loader_path` now da friendly ValueError for invalid extension or relative traversal attempts.
* `MotorDatos.aplicar_union` includes guard `ValueError` when `df2` no está cargado; test agregado.
* Combinado con test suite: 16 tests pasados.

### Español
#### Añadido
* Ejecución de macros ahora rechaza keys de parámetros que comienzan con `__` y claves peligrosas en `main.py`.
* Sanitización de exportación en `core/data_engine.py` extendida para valores tipo fórmula `'=...` y casos con espacios iniciales.
* Hardening de cargadores `cargar_archivo`/`cargar_df2`: normalización de ruta, no `..` en rutas relativas, soporta solo `.csv`, `.xls`, `.xlsx`.
* UI: modal de conversión (`Cambiar Tipo`) muestra tabla de filas inválidas con altura adaptable, scroll y botón “Copiar al portapapeles”.
* Logging global en `querylibre.log` con rotación de archivos.

#### Corregido
* `MotorDatos._validate_loader_path` devuelve `ValueError` claro para extensión inválida o intentos de traversal relativo.
* `MotorDatos.aplicar_union` lanza guard `ValueError` cuando no hay `df2` cargado; test añadido.
* Validación de flujo via tests: 16 pruebas pasadas.

---

## [1.4.2] - 2026-04-01
### English
#### Added
* Enhanced macro engine security: macro action whitelist in `main.py` to avoid execution of not-permitted actions (hardening against modified macro JSONs).
* Safe export sanitization in `core/data_engine.py`: CSV/Excel formula injection mitigation (`=`, `+`, `-`, `@`).
* Robust file validation on loader functions `cargar_archivo` and `cargar_df2` (path exist, extension check, friendly errors).
* CLI/GUI version bump to **v1.4.2** in status label and About panel.

#### Fixed
* Logging improved in `main.py`; captures errors with `logging.error` for file open/save/macro operations.
* `MotorDatos.editar_celda` now validates row index and raises `IndexError` when está fuera de rango.
* `filtrar_datos` now usa `regex=False` en `Contiene el texto` para evitar inyección de expresiones regulares.
* `exportar_archivo` pre-validación de nombre de paso para no fallar con `formato` sin espacio.

#### Changed
* `requirements.txt` now defines pinned versions for reproducibility y seguridad.

### Español
#### Añadido
* Seguridad de macros: whitelist de acciones en `main.py` para evitar ejecución arbitraria desde JSON de macros.
* Sanitización de exportación: `core/data_engine.py` evita inyección de fórmulas en CSV/Excel.
* Validaciones de datos de entrada en los cargadores (`cargar_archivo`, `cargar_df2`).
* Actualización de versión a **v1.4.2** en interfaz y ventana Acerca de.

#### Corregido
* Errores en carga/guardado de macros se registran con `logging.error`.
* Validación de rango en `editar_celda`, fallo con `IndexError` en índice inválido.
* `filtrar_datos` con `Contiene el texto` no interpreta regex peligrosas.
* `exportar_archivo` registra correctamente el formato incluso con etiquetas simples.

#### Cambios
* `requirements.txt` ahora usa versiones fijas de librerías para evitar comandos inesperados por upgrades.

#### En progreso
* Mejorar el modal de conversión para mostrar el listado de filas inválidas de forma integrada y evitar depender del texto largo de error. La tabla actual está construida, pero requiere ajustes finos (scroll automático / tamaño adaptativo) para no degradar la UX cuando hay muchos valores inválidos.

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