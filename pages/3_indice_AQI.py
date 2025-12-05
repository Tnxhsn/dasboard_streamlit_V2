import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("data_clean.csv", sep=";")
df["date/heure"] = pd.to_datetime(df["date/heure"])
df = df.dropna(subset=["date/heure"])
df["DATETIME"] = df["date/heure"]

st.title(" Indice AQI simplifié (PM2.5)")

def aqi(pm):
    if pd.isna(pm): return np.nan
    if pm <= 10: return "Très bon"
    if pm <= 20: return "Bon"
    if pm <= 25: return "Moyen"
    if pm <= 50: return "Médiocre"
    return "Mauvais"

df["AQI"] = df["PM2.5"].apply(aqi)

st.subheader("Répartition des catégories AQI")
counts = df["AQI"].value_counts()

fig, ax = plt.subplots(figsize=(6, 4))
counts.plot(kind="bar", ax=ax, color="#0055A4")
ax.grid(True)
st.pyplot(fig)

st.success(f"Catégorie dominante : **{counts.idxmax()}**")
