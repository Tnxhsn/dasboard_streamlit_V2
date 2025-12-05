import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data_clean.csv", sep=";")
df["date/heure"] = pd.to_datetime(df["date/heure"])
df = df.dropna(subset=["date/heure"])
df["DATETIME"] = df["date/heure"]

st.title(" Comparaison PM10 vs PM2.5")

# Courbes
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["DATETIME"], df["PM10"], color="#009C6B", linewidth=1.3, label="PM10")
ax.plot(df["DATETIME"], df["PM2.5"], color="#0055A4", linewidth=1.3, label="PM2.5")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Scatter
st.subheader("Nuage de points PM10 vs PM2.5")

fig2, ax2 = plt.subplots(figsize=(6, 6))
ax2.scatter(df["PM10"], df["PM2.5"], alpha=0.4, color="#78D2AD")
ax2.grid(True)
st.pyplot(fig2)

# Corrélation
corr = df[["PM10", "PM2.5"]].corr().iloc[0, 1]
st.info(f"Corrélation PM10 / PM2.5 : **{corr:.2f}**")
