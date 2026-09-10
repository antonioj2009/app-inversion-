import os
import pandas as pd
import streamlit as st
import yfinance as yf
from google import genai
# ==========================================
# CONFIGURACIÓN
# ==========================================
st.set_page_config(
    page_title="Ranking Inversión IA",
    page_icon="📈",
    layout="wide"
)
st.title("🏆 Ranking de Acciones con IA")
st.write(
    "Analiza automáticamente varias empresas mediante indicadores técnicos "
    "y genera un análisis con Gemini."
)
# ==========================================
# CONFIGURACIÓN DE GEMINI
# ==========================================
# Streamlit Secrets:
# GEMINI_API_KEY = "AQ.Ab8RN6L1MtqISsMi0PZr4n0xFbYtCibtm6oT_VEgkaK0HkglwA"
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error(
        "❌ No se ha encontrado GEMINI_API_KEY. "
        "Añádela en los Secrets de Streamlit."
    )
    st.stop()
client = genai.Client(api_key=api_key)
# ==========================================
# ACCIONES A ANALIZAR
# ==========================================
tickers_por_defecto = [
    "NVDA",
    "AAPL",
    "MSFT",
    "GOOGL",
    "TSLA",
    "AMZN",
    "META"
]
# ==========================================
# CÁLCULO DEL RSI
# ==========================================
def calcular_rsi(data, window=14):
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
# ==========================================
# ESCANEAR MERCADO
# ==========================================
if st.button("🚀 Escanear Mercado y Generar Ranking"):
    resultados = []
    with st.spinner("📊 Analizando mercado..."):
        for ticker in tickers_por_defecto:
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(period="3mo")
                if df.empty:
                    continue
                df["RSI"] = calcular_rsi(df)
                rsi = df["RSI"].iloc[-1]
                precio = df["Close"].iloc[-1]
                if pd.isna(rsi):
                    continue
                resultados.append({
                    "Ticker": ticker,
                    "Precio": round(float(precio), 2),
                    "RSI": round(float(rsi), 2)
                })
            except Exception as e:
                st.warning(f"No se pudo obtener {ticker}: {e}")
    # ==========================================
    # RESULTADOS
    # ==========================================
    if not resultados:
        st.error("❌ No se han podido obtener datos del mercado.")
        st.stop()
    df_res = pd.DataFrame(resultados)
    # Ordenamos por RSI
    df_res = df_res.sort_values(
        by="RSI",
        ascending=True
    ).reset_index(drop=True)
    st.subheader("📊 Datos Técnicos Recientes")
    st.dataframe(
        df_res,
        use_container_width=True,
        hide_index=True
    )
    # ==========================================
    # ANÁLISIS DE GEMINI
    # ==========================================
    st.subheader("🤖 Veredicto de Gemini")
    try:
        with st.spinner("🧠 Gemini está analizando los datos..."):
            tabla = df_res.to_string(index=False)
            prompt = f"""
Analiza los siguientes datos técnicos de varias acciones:
{tabla}
Explica de forma clara y estructurada:
1. Qué acciones presentan un RSI más interesante.
2. Qué acciones parecen estar sobrecompradas.
3. Qué acciones parecen estar sobrevendidas.
4. Cuáles presentan una situación técnica más equilibrada.
5. Haz un ranking técnico de las acciones de mejor a peor según
   exclusivamente los datos proporcionados.
IMPORTANTE:
- No garantices beneficios.
- No presentes el análisis como asesoramiento financiero personalizado.
- Explica que el RSI por sí solo no determina si una acción va a subir o bajar.
- Responde en español.
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            st.success(response.text)
    except Exception as e:
        st.error(
            f"❌ Error al conectar con Gemini: {e}"
        )
