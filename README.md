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
├── dashboard/
│   └── app_dashboard.py      # Aplicación Streamlit
├── data/
│   ├── netflix_movies_detailed_up_to_2025.csv
│   └── netflix_tv_shows_detailed_up_to_2025.csv
├── images/
│   └── logo.png              # Logo mostrado en la barra lateral
├── notebooks/
│   └── 01_EDA_StreamView.ipynb   # Análisis exploratorio y hallazgos
├── requirements.txt
└── README.md
```

## Instalación

Requiere Python 3.10 o superior.

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

Para explorar el análisis exploratorio, abre `notebooks/01_EDA_StreamView.ipynb` en VS Code o Jupyter.

## Uso

- **Tipo de contenido** (barra lateral): Películas, Series o Ambos.
- **Top N géneros**: cantidad de géneros a mostrar en los gráficos.
- Los KPIs y los tres gráficos se actualizan con cada filtro. Las variaciones de los KPIs comparan la selección con el catálogo completo.

## Tecnologías

Python · Pandas · NumPy · Plotly Express · Streamlit
