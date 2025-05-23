
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import ta

st.set_page_config(page_title="Monitor Cripto", layout="centered")

API_BASE = "https://api.coingecko.com/api/v3"

MONEDAS = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Solana (SOL)": "solana",
    "Cardano (ADA)": "cardano",
    "Ripple (XRP)": "ripple",
    "Polygon (MATIC)": "matic-network"
}

def obtener_precio(moneda_id):
    try:
        url = f"{API_BASE}/simple/price?ids={moneda_id}&vs_currencies=clp"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data[moneda_id]["clp"]
    except Exception as e:
        st.error(f"No se pudo obtener el precio: {e}")
        return None

def obtener_datos_tecnicos(moneda_id):
    try:
        url = f"{API_BASE}/coins/{moneda_id}/market_chart?vs_currency=clp&days=30"
        response = requests.get(url, timeout=5)
        data = response.json()
        precios = data["prices"]
        fechas = [datetime.fromtimestamp(p[0] / 1000) for p in precios]
        valores = [p[1] for p in precios]
        df = pd.DataFrame({"Fecha": fechas, "Precio": valores})
        df["SMA_7"] = df["Precio"].rolling(window=7).mean()
        df["RSI_14"] = ta.momentum.RSIIndicator(df["Precio"], window=14).rsi()
        return df
    except Exception as e:
        st.error(f"No se pudieron obtener los datos técnicos: {e}")
        return pd.DataFrame()

st.title("📊 Monitor Cripto con Indicadores")

seleccion = st.selectbox("Selecciona una criptomoneda:", list(MONEDAS.keys()))
moneda_id = MONEDAS[seleccion]

if st.button("🔍 Ver precio actual"):
    precio = obtener_precio(moneda_id)
    if precio:
        st.success(f"💰 Precio actual de {seleccion}: ${precio:,.0f} CLP")

        df = obtener_datos_tecnicos(moneda_id)
        if not df.empty:
            variacion = ((df["Precio"].iloc[-1] - df["Precio"].iloc[0]) / df["Precio"].iloc[0]) * 100
            color = "🟢" if variacion > 0 else "🔴"
            st.info(f"{color} Variación en 30 días: {variacion:.2f}%")

if st.button("📈 Ver gráfico"):
    df = obtener_datos_tecnicos(moneda_id)
    if not df.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df["Fecha"], df["Precio"], label="Precio CLP", linewidth=2)
        ax.plot(df["Fecha"], df["SMA_7"], label="SMA 7", linestyle="--")
        ax.set_title(f"{seleccion} - Precio + Media Móvil (30 días)")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Precio en CLP")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

if st.button("💾 Exportar a Excel"):
    df = obtener_datos_tecnicos(moneda_id)
    if not df.empty:
        archivo = f"{moneda_id}_analisis.xlsx"
        df.to_excel(archivo, index=False)
        with open(archivo, "rb") as f:
            st.download_button(
                label="Descargar archivo Excel",
                data=f,
                file_name=archivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

st.markdown("---")
st.caption("Desarrollado por LuisFarming · v1.0 · luisfarming@gmail.com")
