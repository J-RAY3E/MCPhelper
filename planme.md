# Plan de Desarrollo: MCP Helper - Cuaderno de Análisis de Mercado

## 1. Visión General

El objetivo es crear una aplicación web interactiva, con una estética de cuaderno de notas (similar a Jupyter/Colab), que sirva como una potente herramienta para el análisis de mercado. En lugar de celdas de código puro, la interacción se basará en "comandos" específicos (ej. `/plot`, `/scrape`, `/model`) que abstraen la complejidad y agilizan el flujo de trabajo del analista.

La aplicación aprovechará la arquitectura de agente existente en el proyecto (`Planner`, `Executor`, `Tools`) para interpretar estos comandos y generar visualizaciones, resúmenes y análisis de datos.

---

## 2. Arquitectura Propuesta

### Frontend (UI)
- **Tecnología:** Se propone usar **Streamlit** o **Gradio**. Son frameworks de Python que permiten crear UIs de ciencia de datos de forma extremadamente rápida, ideal para prototipar y desarrollar esta idea.
- **Interfaz:**
    - Un área principal que contendrá una lista de "celdas".
    - Cada celda tendrá un área de texto para introducir el comando y sus parámetros.
    - Debajo del input, se renderizará el resultado: un gráfico, una tabla, texto, etc.
    - Botones para añadir, eliminar y reordenar celdas.

### Backend (Lógica Principal)
- Se reutilizará el `core` del proyecto.
- Un endpoint principal recibirá el comando de una celda desde el frontend.
- **`core.planner`:** Se adaptará para interpretar el comando (ej. `/plot stock GOOGL`) y determinar qué herramienta (`tools`) usar y con qué argumentos.
- **`core.executor`:** Ejecutará la herramienta correspondiente (ej. llamar a una función que use `matplotlib`/`plotly` para graficar, o a `scraper` para obtener datos).
- **`core.context`:** Gestionará los datos cargados en la sesión (ej. un CSV subido por el usuario) para que puedan ser referenciados por comandos en diferentes celdas.

---

## 3. Funcionalidades Clave

Para que sea una herramienta profesional, debería cubrir el ciclo completo de análisis:

### Módulo 1: Ingesta y Adquisición de Datos
- **Comando `/upload`**: Permitir al usuario subir archivos de datos (CSV, Excel, JSON) directamente a la aplicación.
- **Comando `/scrape [URL]`**: Extraer datos tabulares o de texto de una página web. (Ya tienes una base para esto en `core/scraper.py`).
- **Comando `/fetch_stock [Ticker]`**: Conectarse a una API de datos financieros (ej. Yahoo Finance, Alpha Vantage) para obtener datos históricos de acciones.
- **Comando `/search [Término]`**: Realizar una búsqueda web para encontrar noticias, artículos o informes sobre un tema de mercado y resumir los resultados.

### Módulo 2: Análisis y Procesamiento
- **Comando `/describe [Dataset]`**: Mostrar estadísticas descriptivas de un conjunto de datos cargado (media, mediana, desviación estándar, etc., como `pandas.describe()`).
- **Comando `/clean [Dataset]`**: Aplicar operaciones básicas de limpieza de datos (manejar valores nulos, eliminar duplicados).
- **Comando `/math [Expresión]`**: Realizar cálculos matemáticos y estadísticos.
- **Comando `/sentiment [Fuente]`**: Analizar el sentimiento (positivo, negativo, neutral) del texto extraído de una URL o de una búsqueda.

### Módulo 3: Modelado y Proyección
- **Comando `/model [Objetivo]`**: Usar un LLM para realizar tareas complejas como:
    - `... summarize [texto]`
    - `... forecast sales based on [Dataset]`
    - `... identify risks in [report]`
- **Comando `/forecast [Dataset] [Periodo]`**: Aplicar modelos de series temporales (como ARIMA o Prophet) para predecir valores futuros a partir de datos históricos.

### Módulo 4: Visualización y Reporte
- **Comando `/plot [Tipo] from [Dataset]`**: Generar gráficos interactivos. (Ya tienes scripts de ploteo que se pueden adaptar).
    - Tipos: `line`, `bar`, `histogram`, `scatter`, `pie`.
- **Comando `/table [Dataset]`**: Mostrar datos en una tabla interactiva con opciones para ordenar y filtrar.
- **Comando `/report [Título]`**: Ensamblar los resultados de varias celdas (texto, gráficos, tablas) en un único informe cohesivo que se pueda exportar.

### Módulo 5: Exportación
- Opción para exportar un notebook completo o un informe generado a formatos como **PDF**, **HTML** o **Markdown**.

---

## 4. Plan de Implementación (Próximos Pasos)

1.  **Fase 1: MVP (Producto Mínimo Viable)**
    1.  **Configurar el entorno de UI:** Instalar Streamlit y crear el archivo principal de la aplicación.
    2.  **Diseñar la UI básica:** Implementar la lógica para añadir y mostrar celdas de texto.
    3.  **Implementar el primer comando E2E:** Enfocarse en `/upload` para subir un CSV y `/plot line from [CSV]` para graficar una columna. Esto validará la arquitectura completa.
    4.  **Integrar `/describe`:** Un comando sencillo que devuelva texto y una tabla.

2.  **Fase 2: Expansión de Funcionalidades**
    1.  Implementar los comandos de adquisición de datos: `/scrape` y `/fetch_stock`.
    2.  Ampliar las opciones de `/plot` para incluir más tipos de gráficos.
    3.  Integrar el comando `/model` para tareas de resumen y análisis vía LLM.

3.  **Fase 3: Profesionalización**
    1.  Desarrollar los comandos más avanzados como `/forecast` y `/sentiment`.
    2.  Construir la funcionalidad de `/report`.
    3.  Añadir opciones de exportación.
    4.  Refinar la estética y la experiencia de usuario (UX).
