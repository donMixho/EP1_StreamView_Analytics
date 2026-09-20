# StreamView Analytics – Dashboard Ejecutivo

Dashboard interactivo de análisis del catálogo de contenidos de **StreamView Analytics** (empresa ficticia), desarrollado como proyecto de Visualización de Datos con Python, Pandas, Plotly Express y Streamlit.

## Problema de negocio

La gerencia de contenidos debe decidir en qué invertir su próximo presupuesto de adquisición y producción. Hoy no es claro si el **volumen** del catálogo (qué género, formato o idioma tiene más títulos) se corresponde con la **calidad percibida** y el **engagement** de la audiencia.

El dashboard responde tres preguntas:

1. ¿Dónde se concentra el volumen del catálogo?
2. ¿Qué géneros generan mayor engagement?
3. ¿Qué idiomas conviene adquirir?

Los hallazgos del análisis exploratorio (`notebooks/01_EDA_StreamView.ipynb`) sostienen la narrativa: el género con más títulos no es el mejor valorado, las series tienen mejor nota pero las películas concentran mucho más engagement, y el contenido en inglés domina el catálogo sin ser el mejor valorado.

**Índice de engagement:** `log(1 + votos) × nota promedio`. Solo se analizan títulos con al menos un voto.

## Estructura del proyecto

```
P1_StreamView/
├── .streamlit/
│   └── config.toml           # Tema oscuro corporativo
├── dashboard/
│   └── app_dashboard.py      # Aplicación Streamlit
├── data/
│   ├── netflix_movies_detailed_up_to_2025.csv
│   └── netflix_tv_shows_detailed_up_to_2025.csv
├── images/
│   ├── logo.png              # Logo mostrado en la barra lateral
│   └── eda_hallazgo*.png     # Evidencia del EDA (se genera automáticamente, ver abajo)
├── notebooks/
│   └── 01_EDA_StreamView.ipynb   # Análisis exploratorio y hallazgos
├── requirements.txt
└── README.md
```

> **Evidencia automática:** al ejecutar la sección de hallazgos de `notebooks/01_EDA_StreamView.ipynb`, cada gráfico se exporta como PNG a la carpeta `images/` (por ejemplo `eda_hallazgo1_volumen.png`, `eda_hallazgo2_engagement.png`, `eda_hallazgo3_idiomas.png`). No es necesario guardar los gráficos a mano; volver a ejecutar el notebook los regenera.

## Instalación

Requiere Python 3.10 o superior y **Google Chrome** instalado (lo usa Kaleido para exportar los gráficos a PNG).

```bash
# (Opcional) crear y activar un entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecución del dashboard

Desde la raíz del proyecto:

```bash
python -m streamlit run dashboard/app_dashboard.py
```

Streamlit abrirá el dashboard en `http://localhost:8501`.

Para explorar el análisis exploratorio y regenerar las imágenes de evidencia, abre `notebooks/01_EDA_StreamView.ipynb` en VS Code o Jupyter y ejecuta las celdas de la sección "Hallazgos clave".

## Uso

- **Tipo de contenido** (barra lateral): Películas, Series o Ambos.
- **Top N géneros**: cantidad de géneros a mostrar en los gráficos.
- Los KPIs y los tres gráficos se actualizan con cada filtro. Las variaciones de los KPIs comparan la selección con el catálogo completo.

## Decisiones de Diseño y Limitaciones de Datos

### Por qué el dashboard no incluye filtros de fecha (mes/año)

Durante el EDA se detectó una **anomalía de calidad de datos en la columna `date_added`**, que impide usarla de forma confiable como dimensión temporal:

- En el **100% de los registros** el año de `date_added` es idéntico a `release_year`. Una fecha de incorporación al catálogo real casi nunca coincide siempre con el año de estreno.
- La distribución es **perfectamente uniforme**: exactamente 1.000 películas y 1.000 series por cada año entre 2010 y 2025 (2.000 títulos por año). Un catálogo real crece de forma irregular, con años de fuerte adquisición y años de poca actividad.
- Ambas cosas indican que `date_added` no registra cuándo entró el título al catálogo, sino que es un derivado del año de estreno, y que el dataset es una muestra balanceada por año y tipo, no el catálogo completo.

Un filtro por mes o año construido sobre esa columna mostraría un patrón artificial (todos los años con el mismo volumen) y llevaría a conclusiones falsas sobre tendencias de adquisición o crecimiento del catálogo.

**Por eso los filtros se limitan a "Tipo de contenido" y "Top N géneros":**

- **Protegen la integridad del análisis:** solo se ofrecen cortes sobre variables cuyos datos son confiables, de modo que ninguna vista del dashboard presenta una tendencia inventada.
- **Minimizan la carga cognitiva del usuario ejecutivo:** dos controles claros permiten explorar el catálogo sin que el usuario deba validar por su cuenta qué filtros son fiables. Cada vista responde una pregunta de negocio concreta.

### Otras decisiones y limitaciones

- **Títulos sin votos excluidos:** 4.560 títulos tienen `vote_count = 0`. Su nota es 0 por falta de datos, no por mala valoración, y sesgarían los promedios hacia abajo. El análisis usa 27.431 de 31.991 títulos únicos.
- **Duplicados:** `show_id` se repite entre películas y series, por lo que la clave de unicidad es `(show_id, type)`.
- **Columnas descartadas:** `rating` (copia de `vote_average`), `duration` (vacía en películas), `budget` y `revenue` (solo existen para películas).
- **Fiabilidad de las series:** la mediana de votos de las series es baja (9 frente a 154 en películas), por lo que su nota promedio es menos estable.
- **Umbrales mínimos:** los rankings por idioma exigen al menos 300 títulos y el gráfico de engagement por género al menos 30, para evitar conclusiones basadas en grupos muy pequeños.

## Tecnologías

Python · Pandas · NumPy · Plotly Express · Kaleido · Streamlit
