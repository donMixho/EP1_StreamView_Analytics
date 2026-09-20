# StreamView Analytics - Dashboard Ejecutivo

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white) ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white) ![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)

## Descripción del Proyecto

**StreamView Analytics** (empresa ficticia) necesita decidir en qué invertir su próximo presupuesto de adquisición y producción de contenidos. El problema de negocio es entender cómo se relacionan el **volumen** del catálogo, la **retención y el engagement** de la audiencia y sus **preferencias** (género, formato e idioma), para no invertir solo donde ya hay más títulos.

El proyecto tiene dos partes:

1. **Análisis exploratorio (EDA)** en `notebooks/01_EDA_StreamView.ipynb`: limpia los datos y obtiene los hallazgos clave.
2. **Dashboard ejecutivo** en Streamlit, que responde tres preguntas:
   - ¿Dónde se concentra el volumen del catálogo?
   - ¿Qué géneros generan mayor engagement?
   - ¿Qué idiomas conviene adquirir?

**Índice de engagement:** `log(1 + votos) × nota promedio`. El dataset no contiene datos de retención ni de tiempo de visualización, por lo que el engagement se mide con la nota y el volumen de votos de la audiencia.

**Hallazgos del EDA:** el género con más títulos (Drama) no es el mejor valorado; las series tienen mejor nota, pero las películas concentran mucho más engagement (mediana de votos); y el inglés domina el catálogo sin ser el idioma mejor valorado (lidera el japonés).

## Índice

- [Características del Dashboard](#características-del-dashboard)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Decisiones de Diseño y Limitaciones de Datos](#decisiones-de-diseño-y-limitaciones-de-datos)
- [Instalación y Ejecución](#instalación-y-ejecución)

## Características del Dashboard

- **KPIs con deltas dinámicos:** Total de títulos, Nota promedio y Mediana de votos. Cada KPI muestra su variación (con flecha verde o roja) frente al catálogo completo y se recalcula con los filtros.
- **Filtros en la barra lateral:** Tipo de contenido (Películas, Series o Ambos) y Top N géneros. Actualizan toda la vista.
- **Data Storytelling:** cada gráfico tiene la narrativa a la izquierda y la visualización a la derecha. El texto integra cifras dinámicas en verde (insight positivo) o rojo (punto de atención), según los datos filtrados.
- **Matriz Estratégica interactiva:** gráfico de burbujas de nota promedio (eje X) contra engagement (eje Y), con el tamaño de cada burbuja según la cantidad de títulos del género. Dos líneas de promedio dividen el gráfico en cuatro cuadrantes: **Estrellas**, **Joyas ocultas**, **Alto tráfico** y **Revisar**. Solo el género destacado va en rojo.
- **Diseño minimalista:** gráficos sin grillas ni bordes superior/derecho, en tonos de gris con un único color de acento (#E50914) para el hallazgo principal.

## Estructura del Proyecto

```
P1_StreamView/
├── .streamlit/
│   └── config.toml                 # Tema oscuro corporativo (fondo #141414, acento #E50914)
├── dashboard/
│   └── app_dashboard.py            # Aplicación Streamlit
├── data/
│   ├── netflix_movies_detailed_up_to_2025.csv
│   └── netflix_tv_shows_detailed_up_to_2025.csv
├── images/
│   ├── logo.png                    # Logo de la barra lateral
│   └── eda_hallazgo*.png           # Evidencia gráfica, autogenerada por el EDA
├── notebooks/
│   └── 01_EDA_StreamView.ipynb     # Análisis exploratorio y hallazgos
├── requirements.txt
└── README.md
```

## Decisiones de Diseño y Limitaciones de Datos

### Por qué no hay filtros de fecha (mes/año)

Durante el EDA se detectó una **anomalía de calidad de datos en la columna `date_added`**:

- En el **100% de los registros** el año de `date_added` es idéntico a `release_year`. Una fecha real de incorporación al catálogo casi nunca coincide siempre con el año de estreno.
- La distribución es **perfectamente uniforme**: exactamente 1.000 películas y 1.000 series por cada año entre 2010 y 2025 (2.000 títulos por año). Un catálogo real crece de forma irregular.
- Por lo tanto, `date_added` no registra cuándo entró el título al catálogo, y el dataset es una muestra balanceada por año y tipo, no el catálogo completo.

Un filtro por mes o año sobre esa columna mostraría una tendencia artificial y llevaría a conclusiones falsas sobre el crecimiento del catálogo. Limitar los filtros a **"Tipo de contenido"** y **"Top N géneros"** protege la integridad del análisis y minimiza la carga cognitiva del usuario ejecutivo: solo se ofrecen cortes sobre variables confiables.

### Exclusión de valoraciones en 0 (títulos sin votos)

4.560 títulos tienen `vote_count = 0`. En esos casos la nota es 0 por falta de datos, no porque el público los haya valorado mal, y sesgarían todos los promedios hacia abajo. Se excluyen del análisis, que usa 27.431 de los 31.991 títulos únicos. Esto se documenta también en el pie de los KPIs del dashboard.

### Modo oscuro y tipografía Montserrat

El dashboard usa un tema oscuro (fondo `#141414`, texto blanco) y la fuente **Montserrat** en títulos y subtítulos. El objetivo es reducir la carga cognitiva de los usuarios C-Level:

- El fondo oscuro con un único color de acento hace que el rojo señale de inmediato lo importante y reduce la fatiga visual, siguiendo el lenguaje visual de las plataformas de streaming.
- Una tipografía corporativa y consistente da jerarquía clara a los títulos y facilita el escaneo rápido de la página.

### Otras limitaciones

- **Duplicados:** `show_id` se repite entre películas y series, por lo que la clave de unicidad es `(show_id, type)`.
- **Columnas descartadas:** `rating` (copia de `vote_average`), `duration` (vacía en películas), `budget` y `revenue` (solo existen para películas).
- **Fiabilidad de las series:** su mediana de votos es baja (9 frente a 154 en películas), por lo que su nota promedio es menos estable.
- **Umbrales mínimos:** el ranking por idioma exige al menos 300 títulos y la Matriz Estratégica al menos 30 por género, para evitar conclusiones basadas en grupos muy pequeños.

## Instalación y Ejecución

Requiere Python 3.10 o superior y **Google Chrome** instalado (lo usa Kaleido para exportar los gráficos del EDA a PNG).

**1. Instalar dependencias**

```bash
pip install -r requirements.txt
```

**2. Ejecutar el dashboard** (desde la raíz del proyecto)

```bash
python -m streamlit run dashboard/app_dashboard.py
```

Streamlit abrirá el dashboard en `http://localhost:8501`.

**3. (Opcional) Ejecutar el EDA**

Abre `notebooks/01_EDA_StreamView.ipynb` en VS Code o Jupyter y ejecuta la sección "Hallazgos clave". **El script del EDA autogenera la evidencia gráfica en la carpeta `images/`** (por ejemplo `eda_hallazgo1_volumen.png`, `eda_hallazgo2_engagement.png` y `eda_hallazgo3_idiomas.png`); no hace falta guardar los gráficos a mano.

## Autores / Integrantes

- Leandro Ruiz
- Miguel Tropa
- Año: 2026
