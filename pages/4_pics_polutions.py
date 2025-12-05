import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data_clean.csv", sep=";")
df["date/heure"] = pd.to_datetime(df["date/heure"])
df = df.dropna(subset=["date/heure"])
df["DATETIME"] = df["date/heure"]

st.title(" Détection des pics de pollution")

variables = ["PM10", "PM2.5", "TEMP", "HUMI"]

color_map = {
    "PM10": "#009C6B",
    "PM2.5": "#0055A4",
    "TEMP": "#E67E22",
    "HUMI": "#3498DB"
}

var = st.selectbox("Variable :", variables)

series = df[var]
mean = series.mean()
std = series.std()
seuil = mean + 2 * std

df_peaks = df[df[var] > seuil]

st.write(f"Nombre de pics détectés : **{df_peaks.shape[0]}**")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["DATETIME"], df[var], color=color_map[var], linewidth=1.3)

ax.scatter(df_peaks["DATETIME"], df_peaks[var],
           color="#0055A4", edgecolors="white", s=40)

ax.grid(True)
st.pyplot(fig)

st.subheader("Top 20 des pics")
st.dataframe(df_peaks.sort_values(var, ascending=False).head(20)[["DATETIME", var]])
