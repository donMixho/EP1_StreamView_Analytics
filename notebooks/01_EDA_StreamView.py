# =============================================================================
# STREAMVIEW ANALYTICS — Análisis Exploratorio de Datos (EDA)
# Evaluación Parcial N°1 | Visualización de Datos | DUOC UC
# Audiencia objetivo: Gerente de Contenidos
# =============================================================================
# Objetivo: Entregar una visión accionable sobre el desempeño del catálogo
# para apoyar decisiones de adquisición, producción y promoción de contenidos.
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 1 ─ LIBRERÍAS
# ─────────────────────────────────────────────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# Paleta corporativa StreamView (coherencia visual en todo el EDA)
SV_BLUE      = "#1565C0"   # acción / tendencia
SV_BLUE_SOFT = "#B0BEC5"   # puntos dispersos / neutro
SV_ORANGE    = "#FF8C00"   # acento / llamada de atención
SV_RED       = "#E53935"   # anotación / alerta
SV_TEXT      = "#1A1A2E"   # títulos
SV_GRID      = "#EEEEEE"   # grillas suaves

sns.set_theme(style="whitegrid", font_scale=1.05)
plt.rcParams.update({
    "figure.dpi": 120,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#CCCCCC",
    "grid.color": SV_GRID,
    "grid.linestyle": "--",
    "grid.alpha": 0.6,
})


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 2 ─ CARGA E INTEGRACIÓN DE DATOS
# ─────────────────────────────────────────────────────────────────────────────
df_movies   = pd.read_csv("../data/netflix_movies_detailed_up_to_2025.csv")
df_shows    = pd.read_csv("../data/netflix_tv_shows_detailed_up_to_2025.csv")

print(f"Películas cargadas : {df_movies.shape[0]:,} filas × {df_movies.shape[1]} columnas")
print(f"Series cargadas    : {df_shows.shape[0]:,} filas × {df_shows.shape[1]} columnas")

# Unir en un único DataFrame maestro
df = pd.concat([df_movies, df_shows], ignore_index=True)
print(f"\nDataset unificado  : {df.shape[0]:,} filas × {df.shape[1]} columnas")


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 3 ─ PREPARACIÓN Y LIMPIEZA
# ─────────────────────────────────────────────────────────────────────────────
print("\n── Valores nulos antes de limpiar ──")
print(df.isnull().sum()[df.isnull().sum() > 0])

# 3.1 Rellenar campos de texto opcionales
COLS_TEXTO = ["director", "cast", "country", "genres", "description"]
df[COLS_TEXTO] = df[COLS_TEXTO].fillna("Sin registro")

# 3.2 Parsear fecha de incorporación al catálogo
df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
df["year_added"]  = df["date_added"].dt.year
df["month_added"] = df["date_added"].dt.month

# 3.3 Extraer número de temporadas (solo TV Shows)
df_series = df[df["type"] == "TV Show"].copy()
df_series["seasons"] = df_series["duration"].str.extract(r"(\d+)").astype(float)

# 3.4 Separadores de géneros (vista expandida para análisis)
df_gen = (
    df.assign(genres=df["genres"].str.split(", "))
      .explode("genres")
      .query("genres != 'Sin registro'")
)

print("\n── Valores nulos después de limpiar columnas de texto ──")
print(df[COLS_TEXTO].isnull().sum())
print(f"\nDistribución de tipos:\n{df['type'].value_counts()}")


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 4 ─ ANÁLISIS EXPLORATORIO Y VISUALIZACIONES
# ─────────────────────────────────────────────────────────────────────────────

# ── 4.1  Proporción de Películas vs. Series ──────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))

conteo_tipo = df["type"].value_counts()
colores = [SV_BLUE, SV_ORANGE]
bars = ax.bar(conteo_tipo.index, conteo_tipo.values, color=colores, width=0.5)

for bar in bars:
    ax.annotate(
        f"{int(bar.get_height()):,}",
        xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
        xytext=(0, 6), textcoords="offset points",
        ha="center", fontsize=12, fontweight="bold", color=SV_TEXT,
    )

ax.set_title(
    "El catálogo está dividido en partes iguales\nentre Películas y Series de TV",
    fontsize=14, fontweight="bold", loc="left", color=SV_TEXT, pad=10,
)
ax.set_xlabel("Tipo de Contenido", fontsize=11)
ax.set_ylabel("Cantidad de Títulos", fontsize=11)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("../images/01_proporcion_tipo.png", bbox_inches="tight")
plt.show()

# ── 4.2  Top 10 Géneros por Cantidad de Títulos ──────────────────────────────
top10_generos = df_gen["genres"].value_counts().head(10)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=top10_generos.values, y=top10_generos.index,
            color=SV_BLUE, ax=ax)

ax.set_title(
    "Drama, Comedia e Internacional dominan el catálogo\n— los 3 géneros con mayor volumen de títulos",
    fontsize=13, fontweight="bold", loc="left", color=SV_TEXT,
)
ax.set_xlabel("Cantidad de Títulos", fontsize=11)
ax.set_ylabel("")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("../images/02_top10_generos.png", bbox_inches="tight")
plt.show()

# ── 4.3  Popularidad Promedio por Género (Top 10 producidos) ─────────────────
popularidad_genero = (
    df_gen[df_gen["genres"].isin(top10_generos.index)]
    .groupby("genres")["popularity"]
    .mean()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(10, 6))
bars = sns.barplot(x=popularidad_genero.values, y=popularidad_genero.index,
                   palette="Blues_r", ax=ax)

ax.set_title(
    "Acción y Animación lideran en popularidad promedio\n— no son los géneros más producidos",
    fontsize=13, fontweight="bold", loc="left", color=SV_TEXT,
)
ax.set_xlabel("Popularidad Promedio (score TMDB)", fontsize=11)
ax.set_ylabel("")
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("../images/03_popularidad_genero.png", bbox_inches="tight")
plt.show()

# ── 4.4  Rating vs. Ingresos (solo películas con ingresos > 0) ───────────────
df_ingresos = df[(df["type"] == "Movie") & (df["revenue"] > 0)].copy()

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(
    df_ingresos["vote_average"],
    df_ingresos["revenue"],
    c=SV_BLUE, alpha=0.4, s=30, linewidths=0,
)

ax.set_title(
    "Las películas mejor valoradas NO siempre generan\nlos mayores ingresos",
    fontsize=13, fontweight="bold", loc="left", color=SV_TEXT,
)
ax.set_xlabel("Calificación Promedio (Vote Average)", fontsize=11)
ax.set_ylabel("Ingresos Totales (USD)", fontsize=11)
ax.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"${x/1e9:.1f}B" if x >= 1e9 else f"${x/1e6:.0f}M")
)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("../images/04_rating_vs_ingresos.png", bbox_inches="tight")
plt.show()

# ── 4.5  Burbuja: Interacción (votos) vs. Ingresos ───────────────────────────
fig, ax = plt.subplots(figsize=(11, 6))
sc = ax.scatter(
    df_ingresos["vote_average"],
    df_ingresos["revenue"],
    s=df_ingresos["vote_count"] / df_ingresos["vote_count"].max() * 800 + 20,
    c=SV_BLUE, alpha=0.5, linewidths=0,
)

ax.set_title(
    "Mayor volumen de votos (burbujas grandes) correlaciona\nmás con ingresos que la calificación perfecta",
    fontsize=13, fontweight="bold", loc="left", color=SV_TEXT,
)
ax.set_xlabel("Calificación Promedio (Rating)", fontsize=11)
ax.set_ylabel("Ingresos Totales (USD)", fontsize=11)
ax.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"${x/1e9:.1f}B" if x >= 1e9 else f"${x/1e6:.0f}M")
)

# Leyenda manual de tamaño de burbuja
for votos, label in [(5_000, "5K"), (50_000, "50K"), (200_000, "200K")]:
    size = votos / df_ingresos["vote_count"].max() * 800 + 20
    ax.scatter([], [], s=size, c=SV_BLUE, alpha=0.6, label=f"{label} votos")
ax.legend(title="Cantidad de Votos", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)

ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("../images/05_burbuja_interaccion_ingresos.png", bbox_inches="tight")
plt.show()

# ── 4.6  Temporadas vs. Popularidad — Series TV ───────────────────────────────
# Pregunta: ¿Debe StreamView invertir en renovar series a múltiples temporadas?
df_plot_series = (
    df_series[df_series["seasons"] <= 15]
    .dropna(subset=["seasons", "popularity"])
)

print(f"\nSeries listas para graficar (≤15 temporadas): {len(df_plot_series):,}")

fig, ax = plt.subplots(figsize=(11, 6))
sns.regplot(
    data=df_plot_series, x="seasons", y="popularity", ax=ax,
    scatter_kws={"alpha": 0.25, "color": SV_BLUE_SOFT, "s": 30},
    line_kws={"color": SV_BLUE, "linewidth": 2.5},
    ci=90,
)

# Anotación del punto de rendimiento decreciente
mediana_6 = df_plot_series[df_plot_series["seasons"] == 6]["popularity"].median()
ax.annotate(
    "Rendimientos\ndecrecientes",
    xy=(6, mediana_6),
    xytext=(9.5, df_plot_series["popularity"].quantile(0.82)),
    arrowprops=dict(arrowstyle="->", color=SV_RED, lw=1.5),
    fontsize=9, color=SV_RED, fontweight="bold",
)

ax.set_title(
    "Las series con más temporadas acumulan más popularidad —\npero el retorno se aplana a partir de la temporada 6",
    fontsize=13, fontweight="bold", loc="left", color=SV_TEXT, pad=12,
)
ax.set_xlabel("Número de Temporadas", fontsize=11, color="#444444")
ax.set_ylabel("Popularidad (score TMDB)", fontsize=11, color="#444444")
ax.set_xticks(range(1, 16))
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("../images/06_temporadas_vs_popularidad.png", bbox_inches="tight")
plt.show()

# ── 4.7  Evolución anual de títulos agregados al catálogo ────────────────────
titulos_por_año = (
    df.dropna(subset=["year_added"])
    .groupby(["year_added", "type"])
    .size()
    .reset_index(name="count")
)

fig, ax = plt.subplots(figsize=(11, 6))
for tipo, color in [("Movie", SV_BLUE), ("TV Show", SV_ORANGE)]:
    data_tipo = titulos_por_año[titulos_por_año["type"] == tipo]
    ax.plot(data_tipo["year_added"], data_tipo["count"],
            marker="o", linewidth=2.2, markersize=5,
            color=color, label=tipo)

ax.set_title(
    "El catálogo creció sostenidamente hasta 2020 —\nlas series TV ganaron protagonismo desde 2018",
    fontsize=13, fontweight="bold", loc="left", color=SV_TEXT,
)
ax.set_xlabel("Año de incorporación", fontsize=11)
ax.set_ylabel("Títulos incorporados", fontsize=11)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.legend(frameon=False, fontsize=10)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("../images/07_evolucion_catalogo.png", bbox_inches="tight")
plt.show()

# ── 4.8  Contenido por País (Top 10) ─────────────────────────────────────────
paises_separados = (
    df[df["country"] != "Sin registro"]["country"]
    .str.split(", ")
    .explode()
    .str.strip()
)
top10_paises = paises_separados.value_counts().head(10)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=top10_paises.values, y=top10_paises.index, color=SV_BLUE, ax=ax)

ax.set_title(
    "Estados Unidos y la India lideran la producción —\noportunidad de diversificación regional",
    fontsize=13, fontweight="bold", loc="left", color=SV_TEXT,
)
ax.set_xlabel("Cantidad de Títulos", fontsize=11)
ax.set_ylabel("")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("../images/08_top10_paises.png", bbox_inches="tight")
plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 5 ─ RESUMEN DE HALLAZGOS (KPIs PARA EL GERENTE)
# ─────────────────────────────────────────────────────────────────────────────
total_titulos   = len(df)
total_peliculas = (df["type"] == "Movie").sum()
total_series    = (df["type"] == "TV Show").sum()
pct_peliculas   = total_peliculas / total_titulos * 100

genero_top_prod = top10_generos.index[0]
genero_top_pop  = popularidad_genero.index[0]

titulo_max_ingresos = df_ingresos.loc[df_ingresos["revenue"].idxmax(), "title"]
ingreso_max         = df_ingresos["revenue"].max()

series_1t = (df_series["seasons"] == 1).sum()
pct_1t    = series_1t / len(df_series) * 100

print("\n" + "=" * 60)
print("  HALLAZGOS CLAVE — STREAMVIEW ANALYTICS")
print("=" * 60)
print(f"  Total de títulos en catálogo : {total_titulos:,}")
print(f"  Películas                    : {total_peliculas:,}  ({pct_peliculas:.1f}%)")
print(f"  Series de TV                 : {total_series:,}  ({100-pct_peliculas:.1f}%)")
print(f"  Género más producido         : {genero_top_prod}")
print(f"  Género más popular (score)   : {genero_top_pop}")
print(f"  Película con mayores ingresos: {titulo_max_ingresos}")
print(f"  Ingresos máximos registrados : ${ingreso_max/1e9:.2f}B USD")
print(f"  Series con solo 1 temporada  : {series_1t:,}  ({pct_1t:.1f}%)")
print("=" * 60)
print()
print("RECOMENDACIONES AL GERENTE DE CONTENIDOS:")
print("  1. Priorizar géneros Acción y Animación: alta popularidad,")
print("     subrepresentados respecto a Drama y Comedia.")
print("  2. Renovar series hasta 5.ª–6.ª temporada con criterio")
print("     estratégico; el retorno se aplana después de esa marca.")
print("  3. No otorgar 2.ª temporada automática a series sin tracción")
print(f"     ({pct_1t:.0f}% del catálogo se estanca en 1 temporada).")
print("  4. Evaluar diversificar producción fuera de EE.UU. e India")
print("     para ampliar audiencias y nuevos mercados.")
print("  5. Volumen de votos (engagement) predice ingresos mejor que")
print("     la calificación — priorizar campañas de interacción.")
print("=" * 60)
