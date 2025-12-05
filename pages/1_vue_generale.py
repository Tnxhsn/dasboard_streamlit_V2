import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Chargement
df = pd.read_csv("data_clean.csv", sep=";")
df["date/heure"] = pd.to_datetime(df["date/heure"], errors="coerce")
df = df.dropna(subset=["date/heure"])
df["DATETIME"] = df["date/heure"]

st.title(" Vue générale")

variables = ["PM10", "PM2.5", "TEMP", "HUMI"]

color_map = {
    "PM10": "#009C6B",
    "PM2.5": "#0055A4",
    "TEMP": "#E67E22",
    "HUMI": "#3498DB"
}

var = st.selectbox("Variable :", variables)

# Graphique
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["DATETIME"], df[var], linewidth=1.3, color=color_map[var])
ax.grid(True)
ax.set_xlabel("Date / Heure")
ax.set_ylabel(var)
st.pyplot(fig)

# Statistiques
st.subheader("Statistiques descriptives")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Moyenne", f"{df[var].mean():.2f}")
col2.metric("Max", f"{df[var].max():.2f}")
col3.metric("Min", f"{df[var].min():.2f}")
col4.metric("Missing", int(df[var].isna().sum()))

# Histogramme
fig2, ax2 = plt.subplots(figsize=(6, 4))
ax2.hist(df[var].dropna(), bins=30, color=color_map[var], edgecolor="#2E2E2E")
ax2.grid(True)
st.pyplot(fig2)
