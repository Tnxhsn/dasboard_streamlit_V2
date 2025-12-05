import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------------------------------
# 1. CHARGEMENT ET PRÉPARATION DES DONNÉES
# ------------------------------------------------
df = pd.read_csv("data_clean.csv", sep=";")

# Conversion de la colonne date/heure en datetime propre
df["date/heure"] = pd.to_datetime(df["date/heure"], errors="coerce")

# Enlever le timezone si présent
try:
    df["date/heure"] = df["date/heure"].dt.tz_convert(None)
except TypeError:
    try:
        df["date/heure"] = df["date/heure"].dt.tz_localize(None)
    except TypeError:
        pass

# On enlève les lignes sans date valide
df = df.dropna(subset=["date/heure"])

# Composantes temporelles
df["ANNEE"] = df["date/heure"].dt.year
df["MOIS"] = df["date/heure"].dt.month
df["JOUR"] = df["date/heure"].dt.day
df["HEURE"] = df["date/heure"].dt.hour
df["DATETIME"] = df["date/heure"]

# ------------------------------------------------
# 2. CONFIG STREAMLIT
# ------------------------------------------------
st.set_page_config(
    page_title="Qualité de l'air - Nation RER A",
    layout="wide"
)

# Palette RATP
color_map = {
    "PM10":  "#009C6B",  # Vert RATP
    "PM2.5": "#0055A4",  # Bleu RATP
    "TEMP":  "#E67E22",  # Orange
    "HUMI":  "#3498DB"   # Bleu clair
}

variables = ["PM10", "PM2.5", "TEMP", "HUMI"]

# --- SIDEBAR ---
st.sidebar.title(" Navigation")
page = st.sidebar.radio(
    "Choisir une page :",
    [
        "Vue générale",
        "Comparaison PM10 vs PM2.5",
        "Indice AQI simplifié",
        "Pics de pollution",
        "Heatmap annuelle (année × mois)"
    ]
)

# Lien documentation
st.sidebar.markdown("---")
st.sidebar.markdown("###  Documentation des données")
st.sidebar.link_button(
    "Voir l'explication des variables",
    "https://data.ratp.fr/explore/dataset/qualite-de-lair-mesuree-dans-la-station-auber-2021-a-nos-jours/information/?dataChart=eyJxdWVyaWVzIjpbeyJjaGFydHMiOlt7InR5cGUiOiJwaWUiLCJmdW5jIjoiQ09VTlQiLCJ5QXhpcyI6InRhdWJhIiwic2NpZW50aWZpY0Rpc3BsYXkiOnRydWUsImNvbG9yIjoicmFuZ2UtQWNjZW50IiwicG9zaXRpb24iOiJjZW50ZXIifV0sInhBeGlzIjoiZGF0ZWhldXJlIiwibWF4cG9pbnRzIjpudWxsLCJzb3J0IjoiIiwidGltZXNjYWxlIjoiZGF5IiwiY29uZmlnIjp7ImRhdGFzZXQiOiJxdWFsaXRlLWRlLWxhaXItbWVzdXJlZS1kYW5zLWxhLXN0YXRpb24tYXViZXItMjAyMS1hLW5vcy1qb3VycyIsIm9wdGlvbnMiOnt9fSwic2VyaWVzQnJlYWtkb3duIjoiIiwic2VyaWVzQnJlYWtkb3duVGltZXNjYWxlIjoiIn1dLCJ0aW1lc2NhbGUiOiIiLCJkaXNwbGF5TGVnZW5kIjp0cnVlLCJhbGlnbk1vbnRoIjp0cnVlfQ%3D%3D"   # ➜ remplace ici par TON lien
)

# Filtre temporel
st.sidebar.markdown("---")
st.sidebar.subheader(" Filtre temporel global")

min_date = df["DATETIME"].min().date()
max_date = df["DATETIME"].max().date()

date_range = st.sidebar.date_input(
    "Période",
    (min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

start_ts = pd.to_datetime(start_date)
end_ts = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
df_sel = df[(df["DATETIME"] >= start_ts) & (df["DATETIME"] <= end_ts)]

# ------------------------------------------------
# 3. PAGE 1 – VUE GÉNÉRALE
# ------------------------------------------------
if page == "Vue générale":
    st.title(" Qualité de l'air – Vue générale")

    var = st.selectbox("Variable à afficher :", variables, key="var_general")

    if df_sel.empty:
        st.warning("Aucune donnée sur la période sélectionnée.")
    else:
        # Série temporelle
        st.subheader(f" Évolution de {var} dans le temps")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(
            df_sel["DATETIME"],
            df_sel[var],
            linewidth=1.3,
            color=color_map[var]
        )
        ax.set_xlabel("Date / Heure")
        ax.set_ylabel(var)
        ax.grid(True)
        st.pyplot(fig)

        # Statistiques
        st.subheader(" Statistiques descriptives")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Moyenne", f"{df_sel[var].mean():.2f}")
        col2.metric("Max", f"{df_sel[var].max():.2f}")
        col3.metric("Min", f"{df_sel[var].min():.2f}")
        col4.metric("Valeurs manquantes", int(df_sel[var].isna().sum()))

        # Histogramme
        st.subheader(" Distribution (histogramme)")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.hist(
            df_sel[var].dropna(),
            bins=30,
            color=color_map[var],
            edgecolor="#2E2E2E"
        )
        ax2.set_xlabel(var)
        ax2.set_ylabel("Fréquence")
        ax2.grid(True)
        st.pyplot(fig2)


# ------------------------------------------------
# 4. PAGE 2 – COMPARAISON
# ------------------------------------------------
elif page == "Comparaison PM10 vs PM2.5":
    st.title(" Comparaison PM10 vs PM2.5")

    if df_sel.empty:
        st.warning("Aucune donnée sur la période sélectionnée.")
    else:
        # Courbes superposées
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df_sel["DATETIME"], df_sel["PM10"], label="PM10",
                linewidth=1.3, color=color_map["PM10"])
        ax.plot(df_sel["DATETIME"], df_sel["PM2.5"], label="PM2.5",
                linewidth=1.3, color=color_map["PM2.5"])
        ax.set_xlabel("Date / Heure")
        ax.set_ylabel("µg/m³")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        # Scatter
        st.subheader(" Nuage de points PM10 vs PM2.5")
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        ax2.scatter(df_sel["PM10"], df_sel["PM2.5"], alpha=0.4, color="#78D2AD")
        ax2.set_xlabel("PM10 (µg/m³)")
        ax2.set_ylabel("PM2.5 (µg/m³)")
        ax2.grid(True)
        st.pyplot(fig2)

        # Corrélation
        corr = df_sel[["PM10", "PM2.5"]].corr().iloc[0, 1]
        st.info(f" Corrélation PM10 / PM2.5 : **{corr:.2f}**")


# ------------------------------------------------
# 5. PAGE 3 – INDICE AQI
# ------------------------------------------------
elif page == "Indice AQI simplifié":
    st.title(" Indice AQI simplifié (basé sur PM2.5)")

    if df_sel.empty:
        st.warning("Aucune donnée sur la période sélectionnée.")
    else:

        def aqi_pm25(pm):
            if pd.isna(pm): return np.nan
            if pm <= 10: return "Très bon"
            if pm <= 20: return "Bon"
            if pm <= 25: return "Moyen"
            if pm <= 50: return "Médiocre"
            return "Mauvais"

        df_aqi = df_sel.copy()
        df_aqi["AQI_cat"] = df_aqi["PM2.5"].apply(aqi_pm25)

        st.subheader("Répartition des catégories AQI")
        counts = df_aqi["AQI_cat"].value_counts()

        fig, ax = plt.subplots(figsize=(6, 4))
        counts.plot(kind="bar", ax=ax, color=color_map["PM2.5"])
        ax.set_xlabel("Catégorie AQI")
        ax.set_ylabel("Nombre d'heures")
        ax.grid(True)
        st.pyplot(fig)

        st.success(f"Catégorie dominante : **{counts.idxmax()}**")


# ------------------------------------------------
# 6. PAGE 4 – PICS DE POLLUTION
# ------------------------------------------------
elif page == "Pics de pollution":
    st.title(" Détection des pics de pollution")

    var = st.selectbox("Variable :", variables, key="var_peaks")

    if df_sel.empty:
        st.warning("Aucune donnée sur la période sélectionnée.")
    else:
        series = df_sel[var].dropna()

        mean = series.mean()
        std = series.std()
        seuil = mean + 2 * std

        df_peaks = df_sel[df_sel[var] > seuil]

        st.write(f"Nombre de pics détectés : **{df_peaks.shape[0]}**")

        # Graphique
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(
            df_sel["DATETIME"],
            df_sel[var],
            label=var,
            linewidth=1.3,
            color=color_map[var]
        )

        ax.scatter(
            df_peaks["DATETIME"],
            df_peaks[var],
            s=35,
            color="#0055A4",  # Bleu RATP pour pics
            edgecolors="white",
            linewidth=0.6,
            zorder=3,
            label="Pics"
        )

        ax.set_xlabel("Date / Heure")
        ax.set_ylabel(var)
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        st.subheader("Détail des pics (top 20)")
        st.dataframe(df_peaks.sort_values(var, ascending=False).head(20)[["DATETIME", var]])


# ------------------------------------------------
# 7. PAGE 5 – HEATMAP
# ------------------------------------------------
elif page == "Heatmap annuelle (année × mois)":
    st.title(" Heatmap annuelle (année × mois)")

    var = st.selectbox("Variable :", variables, key="var_heat")

    df_heat = df.dropna(subset=["ANNEE", "MOIS", var]).copy()
    df_heat["ANNEE"] = df_heat["ANNEE"].astype(int)
    df_heat["MOIS"] = df_heat["MOIS"].astype(int)

    pivot = df_heat.pivot_table(
        index="ANNEE",
        columns="MOIS",
        values=var,
        aggfunc="mean"
    )

    st.write("Moyenne mensuelle par année :")
    st.dataframe(pivot)

    # Palette RATP
    ratp_palette = ["#E3F9F0", "#78D2AD", "#009C6B", "#007756"]

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(pivot, cmap=sns.color_palette(ratp_palette), ax=ax)
    ax.set_title(f"Heatmap annuelle de {var}")
    ax.set_xlabel("Mois")
    ax.set_ylabel("Année")
    st.pyplot(fig)
