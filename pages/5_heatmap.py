import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("data_clean.csv", sep=";")
df["date/heure"] = pd.to_datetime(df["date/heure"])
df = df.dropna(subset=["date/heure"])

df["ANNEE"] = df["date/heure"].dt.year
df["MOIS"] = df["date/heure"].dt.month

variables = ["PM10", "PM2.5", "TEMP", "HUMI"]

st.title(" Heatmap annuelle")

var = st.selectbox("Variable :", variables)

pivot = df.pivot_table(
    index="ANNEE",
    columns="MOIS",
    values=var,
    aggfunc="mean"
)

ratp_palette = ["#E3F9F0", "#78D2AD", "#009C6B", "#007756"]

fig, ax = plt.subplots(figsize=(10, 5))
sns.heatmap(pivot, cmap=sns.color_palette(ratp_palette), ax=ax)
ax.set_title("Heatmap annuelle")
st.pyplot(fig)
