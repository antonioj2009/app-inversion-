import os
from google import genai
import pandas_ta as ta
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Inversión IA", page_icon="📈")

st.title("📈 Analizador de Inversiones con IA")

api_key = st.text_input("1. Tu Gemini API Key:", type="password")
ticker = st.text_input(
    "2. Ticker de la empresa (ej: NVDA, AAPL, TSLA):", "NVDA"
).upper()

if st.button("🚀 Analizar Oportunidad"):
    if not api_key:
        st.error("Por favor introduce tu API Key.")
    else:
        with st.spinner("Analizando mercado..."):
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(period="6mo")

                if df.empty:
                    st.error("No se encontraron datos para ese Ticker.")
                else:
                    df["RSI"] = ta.rsi(df["Close"], length=14)
                    rsi = round(df["RSI"].iloc[-1], 2)
                    precio = round(df["Close"].iloc[-1], 2)

                    col1, col2 = st.columns(2)
                    col1.metric("Precio Actual", f"${precio}")
                    col2.metric("RSI (14)", rsi)

                    client = genai.Client(api_key=api_key)
                    prompt = f"Analiza la acción {ticker}. Precio: ${precio}, RSI: {rsi}. Da un diagnóstico breve en español: estado técnico, si conviene comprar o esperar, y riesgos."

                    response = client.models.generate_content(
                        model="gemini-2.5-flash", contents=prompt
                    )

                    st.subheader("💡 Diagnóstico IA")
                    st.info(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
