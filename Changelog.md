# Registro de Cambios (Changelog)

Todos los cambios notables en el proyecto **QueryLibre** serán documentados en este archivo.

## [1.2.0] - 2026-03-27
### Añadido (Added)
* **Paginación de Datos:** Nuevo sistema de navegación por páginas (200 filas por hoja) con controles de Anterior/Siguiente. Permite explorar datasets grandes de manera fluida y sin sobrecargar la interfaz gráfica.
* **Índice Visual de Filas:** Se incorporó una columna estática (`#`) en la vista previa de la tabla para facilitar la lectura, el seguimiento y la ubicación de los registros. Esta columna es de ayuda puramente visual y no altera el dataset al exportar.

### Correcciones (Fixed)
* **Refinamiento de Interfaz (UI):** Se corrigió la jerarquía de empaquetado visual (layout) de la tabla de datos. Ahora las barras de desplazamiento (scrollbars) se integran perfectamente a los bordes sin superponerse ni ocultar los controles de paginación.

## [1.1.1] - 2026-03-26
### Mejoras (Changed)
* **Vista previa ampliada:** Se incrementó el límite de renderizado en la tabla interactiva de 15 a 200 filas, permitiendo una exploración de datos mucho más profunda sin comprometer el rendimiento de la interfaz (Tkinter).
* **Limpieza de Nulos interactiva:** Se mejoró la UX del botón "Limpiar Nulos", implementando un cuadro de diálogo que otorga al usuario el control para decidir la agresividad de la limpieza (eliminar filas completamente vacías vs. eliminar filas con algún dato faltante).

### Añadido (Added)
* **Indicador de dimensiones dinámico:** Se incorporó un contador en tiempo real en la barra inferior derecha que refleja la cantidad total de filas y columnas en memoria, brindando transparencia instantánea tras ejecutar limpiezas de datos masivas (como nulos y duplicados ocultos).

---

## [1.1.0] - 2026-03-26
### Añadido
- Ventana de "Acerca de" con información del proyecto, hoja de ruta (Roadmap) y cumplimientos de licencias Open Source.
- Botones de anticipación (Teasers) en la barra de herramientas principal para generar expectativa sobre las futuras funciones de Feature Engineering (Dividir Columna, Filtrar Datos).

---

## [1.0.0] - 2026-03-23
### Añadido
* Lanzamiento de la primera versión estable del motor ETL.
* Módulo de carga universal de archivos (`.csv`, `.xlsx`, `.xls`).
* **Limpieza de Datos:** Funciones para eliminar duplicados, depurar valores nulos, eliminar y renombrar columnas.
* **Ingeniería de Características:** Calculadora matemática con *Smart Parser* para símbolos de moneda, y herramienta para combinación de textos.
* **Integración:** Interfaz visual para cruce de datos relacionales (Merge/JOIN) con vista previa progresiva.
* Sistema de auditoría (Historial de Pasos) con capacidad de revertir acciones mediante pila LIFO (Undo).
* Módulo de exportación multiformato (CSV, Excel y bases de datos SQLite).