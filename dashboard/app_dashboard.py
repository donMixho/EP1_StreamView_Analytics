from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="StreamView Analytics", layout="wide")

# Tipografía corporativa (Montserrat) para títulos y subtítulos
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    h1, h2, h3, .subtitulo { font-family: 'Montserrat', sans-serif !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGO_PATH = BASE_DIR / "images" / "logo.png"

ACCENT = "#E50914"
VERDE = "#4CAF50"
GRIS_BARRA = "#555555"  # barras no destacadas (contrasta con el fondo #141414)
GRIS = "#8C8C8C"        # puntos no destacados del scatter

IDIOMAS = {
    "en": "Inglés", "ja": "Japonés", "zh": "Chino", "ko": "Coreano", "es": "Español",
    "fr": "Francés", "de": "Alemán", "pt": "Portugués", "ru": "Ruso", "tr": "Turco",
    "it": "Italiano", "hi": "Hindi", "th": "Tailandés", "sv": "Sueco", "da": "Danés",
    "nl": "Neerlandés", "pl": "Polaco", "ar": "Árabe", "id": "Indonesio", "cn": "Cantonés",
}

st.markdown(
    f"""
    <style>
    div[data-testid="stMetric"] {{
        background: #2B2B2B; border-left: 5px solid {ACCENT};
        padding: 16px 20px; border-radius: 4px;
    }}
    div[data-testid="stMetricValue"] {{ font-size: 2.4rem; font-weight: 700; }}
    .narrativa {{ font-size: 1.05rem; line-height: 1.65; padding-top: 8px; }}
    .subtitulo {{ font-size: 1.4rem; font-weight: 700; margin: 28px 0 4px 0; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- Estilo
def estilo_minimo(fig, titulo, height=420):
    """Plotly limpio: sin grillas, sin bordes superior/derecho."""
    fig.update_layout(template="plotly_dark", title=dict(text=titulo, x=0),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",  # hereda el fondo #141414
                      showlegend=False, height=height, margin=dict(l=10, r=10, t=60, b=10))
    fig.update_xaxes(showgrid=False, showline=True, linecolor=GRIS_BARRA)
    fig.update_yaxes(showgrid=False, showline=True, linecolor=GRIS_BARRA)
    return fig


def colores(valores, destacado):
    """Gris para todo, rojo solo para el valor destacado."""
    return [ACCENT if v == destacado else GRIS_BARRA for v in valores]


def resaltar(texto, positivo=True):
    """Texto en negrita: verde si es insight positivo, rojo si es punto de atención."""
    color = VERDE if positivo else ACCENT
    return f'<b style="color:{color}">{texto}</b>'


def subtitulo(antes, destacado, despues=""):
    st.markdown(f'<div class="subtitulo">{antes} <span style="color:{ACCENT}">{destacado}</span>'
                f'{despues}</div>', unsafe_allow_html=True)


def narrativa(html):
    st.markdown(f'<div class="narrativa">{html}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- Datos
@st.cache_data
def cargar_datos():
    movies = pd.read_csv(DATA_DIR / "netflix_movies_detailed_up_to_2025.csv")
    shows = pd.read_csv(DATA_DIR / "netflix_tv_shows_detailed_up_to_2025.csv")
    df = pd.concat([movies, shows], ignore_index=True)

    df = df.drop_duplicates(["show_id", "type"])
    df = df.drop(columns=["rating", "duration", "budget", "revenue"])
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    for c in ["genres", "country", "language"]:
        df[c] = df[c].fillna("Unknown")

    # vote_average = 0 significa "sin votos", no "mala nota"
    val = df[df.vote_count > 0].copy()
    val["engagement"] = np.log1p(val.vote_count) * val.vote_average
    return val


def explotar_generos(df):
    g = df.assign(genre=df.genres.str.split(", ")).explode("genre")
    return g[g.genre != "Unknown"]


df = cargar_datos()

# ---------------------------------------------------------------- Barra lateral
if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), width="stretch")
else:
    st.sidebar.markdown(
        f'<div style="font-size:1.5rem;font-weight:800"><span style="color:{ACCENT}">Stream</span>View</div>',
        unsafe_allow_html=True)

st.sidebar.header("Filtros")
tipo = st.sidebar.radio("Tipo de contenido", ["Ambos", "Películas", "Series"])
top_n = st.sidebar.slider("Top N géneros a visualizar", min_value=5, max_value=20, value=10)

# Filtro temporal por año de lanzamiento (release_year), no por date_added (ver README)
anio_min, anio_max = int(df.release_year.min()), int(df.release_year.max())
rango_anios = st.sidebar.slider("Año de lanzamiento", min_value=anio_min, max_value=anio_max,
                                value=(anio_min, anio_max))

if tipo == "Películas":
    dff = df[df.type == "Movie"]
elif tipo == "Series":
    dff = df[df.type == "TV Show"]
else:
    dff = df

dff = dff[dff.release_year.between(*rango_anios)]

if dff.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

generos = explotar_generos(dff)

# Tablas de apoyo (usadas en los tres gráficos y en sus narrativas)
vol = generos.genre.value_counts().head(top_n).sort_values()
agg = (generos.groupby("genre")
       .agg(titulos=("title", "count"), nota=("vote_average", "mean"), engagement=("engagement", "mean"))
       .query("titulos >= 30")
       .sort_values("titulos", ascending=False)
       .head(top_n)
       .reset_index())
if agg.empty:
    st.warning("No hay géneros con suficientes títulos para los filtros seleccionados.")
    st.stop()

idiomas = (dff.groupby("language")
           .agg(titulos=("title", "count"), nota=("vote_average", "mean"))
           .rename(index=lambda i: IDIOMAS.get(i, i)))

# ---------------------------------------------------------------- Encabezado
st.markdown(
    f'<h1 style="margin-bottom:0"><span style="color:{ACCENT}">StreamView</span> Analytics: '
    f'desempeño del catálogo</h1>',
    unsafe_allow_html=True)
st.markdown(
    "**Problema de negocio:** ¿en qué géneros, formatos e idiomas conviene concentrar la próxima "
    "inversión en adquisición y producción? Este panel contrasta el **volumen** del catálogo con la "
    "**calidad percibida** y el **engagement** de la audiencia para apoyar esa decisión.")

# ---------------------------------------------------------------- KPIs (delta = vs. catálogo completo)
d_nota = dff.vote_average.mean() - df.vote_average.mean()
d_votos = dff.vote_count.median() - df.vote_count.median()

k1, k2, k3 = st.columns(3)
k1.metric("Total de títulos", f"{len(dff):,}",
          delta=f"{len(dff) / len(df):.0%} del catálogo", delta_color="off")
k2.metric("Nota promedio", f"{dff.vote_average.mean():.2f}",
          delta=f"{d_nota:+.2f} vs. catálogo" if abs(d_nota) >= 0.005 else None)
k3.metric("Mediana de votos", f"{dff.vote_count.median():,.0f}",
          delta=f"{d_votos:+,.0f} vs. catálogo" if abs(d_votos) >= 0.5 else None)
st.caption("Solo se consideran títulos con al menos un voto. Engagement = log(1 + votos) × nota. "
           "Las variaciones comparan la selección actual con el catálogo completo.")

# ---------------------------------------------------------------- 1. Volumen por género
subtitulo("1. ¿Dónde está el", "volumen", " del catálogo?")
col_texto, col_grafico = st.columns([1, 2])

lider, n_lider = vol.idxmax(), vol.max()
share = n_lider / len(dff)
mejor_nota = agg.loc[agg.nota.idxmax()]

with col_texto:
    txt = (f"{resaltar(lider, share < 0.4)} lidera el catálogo con {n_lider:,} títulos, presente en "
           f"{resaltar(f'{share:.0%}', share < 0.4)} de la oferta. ")
    txt += ("Esta concentración es un " + resaltar("punto de atención", False) +
            ": la oferta depende de un solo género. " if share >= 0.4
            else "La oferta está razonablemente diversificada. ")
    if mejor_nota.genre != lider:
        txt += (f"En calidad, en cambio, destaca {resaltar(mejor_nota.genre)} con nota "
                f"{resaltar(f'{mejor_nota.nota:.2f}')}: mayor volumen no implica mejor valoración.")
    narrativa(txt)

with col_grafico:
    fig = px.bar(vol, orientation="h")
    fig.update_traces(marker_color=colores(vol.index, lider),
                      hovertemplate="%{y}: %{x:,} títulos<extra></extra>")
    estilo_minimo(fig, f"Los {top_n} géneros con más títulos", height=max(360, 30 * top_n + 100))
    fig.update_xaxes(title="Títulos").update_yaxes(title="")
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- 2. Nota vs. engagement
subtitulo("2. ¿Qué géneros generan más", "engagement", "?")
col_texto, col_grafico = st.columns([1, 2])

mejor = agg.loc[agg.engagement.idxmax()]
peor = agg.loc[agg.nota.idxmin()]

with col_texto:
    txt = (f"{resaltar(mejor.genre)} combina la mejor respuesta de audiencia, con un índice de engagement "
           f"de {resaltar(f'{mejor.engagement:.1f}')} y nota {mejor.nota:.2f}. ")
    if peor.genre != mejor.genre:
        bajo = peor.nota < dff.vote_average.mean()  # rojo solo si está bajo el promedio de la vista
        txt += (f"En el otro extremo, {resaltar(peor.genre, not bajo)} tiene la nota más baja "
                f"({resaltar(f'{peor.nota:.2f}', not bajo)}) entre los géneros mostrados")
        txt += (": está bajo el promedio, así que conviene revisar la inversión antes de ampliarlo."
                if bajo else ", aun así sobre el promedio general: no representa un problema de calidad.")
    narrativa(txt)

with col_grafico:
    fig = px.scatter(agg, x="nota", y="engagement", text="genre", color="genre",
                     size="titulos", size_max=35,  # tamaño de burbuja = cantidad de títulos
                     color_discrete_map={g: (ACCENT if g == mejor.genre else GRIS) for g in agg.genre},
                     hover_data={"genre": False, "titulos": ":,", "nota": ":.2f", "engagement": ":.1f"})
    fig.update_traces(textposition="top center", marker=dict(opacity=0.8, line=dict(width=0)))
    estilo_minimo(fig, "Matriz estratégica: nota vs. engagement por género")
    fig.update_xaxes(title="Nota promedio").update_yaxes(title="Índice de engagement")

    # Matriz de cuadrantes: líneas en el promedio de los géneros graficados
    prom_nota, prom_eng = agg.nota.mean(), agg.engagement.mean()
    fig.add_vline(x=prom_nota, line_dash="dash", line_color="#4D4D4D", line_width=1)
    fig.add_hline(y=prom_eng, line_dash="dash", line_color="#4D4D4D", line_width=1)

    # Nombres de cuadrantes en las esquinas del área del gráfico (coordenadas relativas)
    for texto, x, y, xa, ya in [
        ("ESTRELLAS", 0.99, 0.99, "right", "top"),
        ("JOYAS OCULTAS", 0.99, 0.01, "right", "bottom"),
        ("ALTO TRÁFICO", 0.01, 0.99, "left", "top"),
        ("REVISAR", 0.01, 0.01, "left", "bottom"),
    ]:
        fig.add_annotation(text=texto, x=x, y=y, xref="paper", yref="paper", xanchor=xa, yanchor=ya,
                           showarrow=False, font=dict(size=12, color="#8C8C8C"))
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- 3. Nota por idioma
subtitulo("3. ¿Qué", "idiomas", " conviene adquirir?")
col_texto, col_grafico = st.columns([1, 2])

top_idi = idiomas.query("titulos >= 300").nota.nlargest(8).sort_values()

with col_texto:
    if top_idi.empty:
        narrativa("No hay idiomas con suficientes títulos (≥300) para esta selección.")
    else:
        mejor_idi = top_idi.idxmax()
        mayor_idi = idiomas.titulos.idxmax()
        nota_mayor = idiomas.loc[mayor_idi, "nota"]
        share_idi = idiomas.loc[mayor_idi, "titulos"] / idiomas.titulos.sum()
        if mejor_idi == mayor_idi:
            txt = (f"{resaltar(mejor_idi)} es el idioma mayoritario ({share_idi:.0%} del catálogo) y además "
                   f"el mejor valorado, con nota {resaltar(f'{top_idi.max():.2f}')}.")
        else:
            bajo = nota_mayor < dff.vote_average.mean()
            txt = (f"{resaltar(mejor_idi)} es el idioma mejor valorado, con nota "
                   f"{resaltar(f'{top_idi.max():.2f}')}. En contraste, {mayor_idi} concentra "
                   f"{resaltar(f'{share_idi:.0%}', False)} del catálogo con una nota de "
                   f"{resaltar(f'{nota_mayor:.2f}', not bajo)}"
                   f"{' (bajo el promedio)' if bajo else ''}: existe una oportunidad de adquisición "
                   f"en contenido {mejor_idi.lower()}.")
        narrativa(txt)

with col_grafico:
    if not top_idi.empty:
        fig = px.bar(top_idi, orientation="h", text_auto=".2f")
        fig.update_traces(marker_color=colores(top_idi.index, top_idi.idxmax()),
                          hovertemplate="%{y}: nota %{x:.2f}<extra></extra>")
        estilo_minimo(fig, "Nota promedio por idioma (≥300 títulos)")
        fig.update_xaxes(title="Nota promedio", range=[5, 8]).update_yaxes(title="")
        st.plotly_chart(fig, width="stretch")
