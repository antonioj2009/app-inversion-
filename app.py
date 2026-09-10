import os
from google import genai
import pandas as pd
import streamlit as st
import yfinance as yf

# ==========================================
# PEGA AQUÍ TU CLAVE QUE EMPIECE POR AIza...
API_KEY_FIJA = "AIzaSy..."
# ==========================================

st.set_page_config(page_title="Ranking Inversión IA", page_icon="📈")

st.title("🏆 Ranking de Acciones con IA")
st.write(
    "Analiza automáticamente las principales empresas del mercado para descubrir cuál es más rentable ahora mismo."
)

tickers_por_defecto = ["NVDA", "AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "META"]


def calcular_rsi(data, window=14):
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


if st.button("🚀 Escanear Mercado y Generar Ranking"):
    with st.spinner("Analizando múltiples acciones en tiempo real..."):
        try:
            resultados = []
            for t in tickers_por_defecto:
                stock = yf.Ticker(t)
                df = stock.history(period="3mo")
                if not df.empty:
                    df["RSI"] = calcular_rsi(df)
                    rsi = round(df["RSI"].iloc[-1], 2)
                    precio = round(df["Close"].iloc[-1], 2)
                    resultados.append({"Ticker": t, "Precio": precio, "RSI": rsi})

            df_res = pd.DataFrame(resultados)

            st.subheader("📊 Datos Técnicos Recientes")
            st.dataframe(df_res, use_container_width=True)

            # Intentar ejecutar la IA de forma segura
            try:
                client = genai.Client(api_key=API_KEY_FIJA)
                prompt = f"""
                Actúa como un gestor de fondos experto. Basándote en esta tabla de acciones y sus indicadores RSI actuales:
                {df_res.to_string()}
                
                Indica claramente:
                1. ¿Cuál es la acción más rentable/oportuna para invertir HOY y por qué?
                2. ¿Cuáles deberíamos evitar por estar sobrecompradas?
                Da una respuesta directa, profesional y estructurada en español.
                """
                response = client.models.generate_content(
                    model="gemini-2.5-flash", contents=prompt
                )
                st.subheader("💡 Veredicto de la Inteligencia Artificial")
                st.success(response.text)
            except Exception as ai_error:
                st.warning(
                    "⚠️ La tabla técnica funciona perfectamente, pero la IA no respondió debido a la API Key. (Asegúrate de usar una clave que empiece por AIza...)"
                )

        except Exception as e:
            st.error(f"Error general: {e}")
