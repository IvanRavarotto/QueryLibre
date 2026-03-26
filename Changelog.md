# Registro de Cambios (Changelog)

Todos los cambios notables en el proyecto **QueryLibre** serán documentados en este archivo.

## [1.1.0] - 2026-03-26
### Añadido
- Ventana de "Acerca de" con información del proyecto, hoja de ruta (Roadmap) y cumplimientos de licencias Open Source.
- Botones de anticipación (Teasers) en la barra de herramientas principal para generar expectativa sobre las futuras funciones de Feature Engineering (Dividir Columna, Filtrar Datos).

---

## [1.0.0] - 2026-03-23
### Añadido
- Lanzamiento de la primera versión estable del motor ETL.
- Módulo de carga universal de archivos (`.csv`, `.xlsx`, `.xls`).
- **Limpieza de Datos:** Funciones para eliminar duplicados, depurar valores nulos, eliminar y renombrar columnas.
- **Ingeniería de Características:** Calculadora matemática con *Smart Parser* para símbolos de moneda, y herramienta para combinación de textos.
- **Integración:** Interfaz visual para cruce de datos relacionales (Merge/JOIN) con vista previa progresiva.
- Sistema de auditoría (Historial de Pasos) con capacidad de revertir acciones mediante pila LIFO (Undo).
- Módulo de exportación multiformato (CSV, Excel y bases de datos SQLite).