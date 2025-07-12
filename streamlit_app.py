import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Imposta il layout e il titolo della pagina
st.set_page_config(page_title="Plant Health App", page_icon="🌿", layout="centered")

# CSS con sfondo animato "Verdant Flow" (gradienti verdi-azzurri tenui)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #e0f7fa, #c8e6c9, #f1f8e9, #b2dfdb);
        background-size: 400% 400%;
        animation: gradientBG 20s ease infinite;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    </style>
""", unsafe_allow_html=True)

# Funzione per valutare la salute della pianta
def evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn):
    score = 0

    # Fv/Fm
    if fvfm >= 0.80:
        score += 2
    elif fvfm >= 0.75:
        score += 1
    else:
        score -= 1

    # Chl TOT
    if chl_tot >= 1.5:
        score += 2
    elif chl_tot >= 1.0:
        score += 1
    else:
        score -= 1

    # CAR TOT
    if car_tot >= 0.5:
        score += 2
    elif car_tot >= 0.3:
        score += 1
    else:
        score -= 1

    # SPAD
    if spad >= 40:
        score += 2
    elif spad >= 30:
        score += 1
    else:
        score -= 1

    # qp
    if qp >= 0.7:
        score += 2
    elif qp >= 0.5:
        score += 1
    else:
        score -= 1

    # qN
    if 0.3 <= qn <= 0.7:
        score += 2
    elif 0.2 <= qn < 0.3 or 0.7 < qn <= 0.8:
        score += 1
    else:
        score -= 1

    # Interpretazione
    if score >= 10:
        return "🌿 Healthy – Optimal physiological state"
    elif 6 <= score < 10:
        return "🌱 Moderate stress – Monitor closely"
    else:
        return "⚠️ High stress – Likely physiological damage"

# Titolo principale con emoji e stile HTML
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>🌿 Plant Health Checker</h1>
    <p style='text-align: center;'>Enter the physiological parameters of your plant to assess its health status.</p>
    """, unsafe_allow_html=True)

# Input dei parametri con layout a due colonne
col1, col2 = st.columns(2)

with col1:
    fvfm = st.number_input("Fv/Fm", min_value=0.0, max_value=1.0, step=0.01)
    chl_tot = st.number_input("Chlorophyll Total (Chl TOT)", min_value=0.0, step=0.1)
    spad = st.number_input("SPAD Value", min_value=0.0, step=0.1)

with col2:
    car_tot = st.number_input("Carotenoids Total (CAR TOT)", min_value=0.0, step=0.1)
    qp = st.number_input("qp (photochemical quenching)", min_value=0.0, max_value=1.0, step=0.01)
    qn = st.number_input("qN (non-photochemical quenching)", min_value=0.0, max_value=1.0, step=0.01)

# Valutazione al click del pulsante
if st.button("🔍 Evaluate Health"):
    result = evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn)

    if "Healthy" in result:
        st.success(result)
    elif "Moderate" in result:
        st.warning(result)
    else:
        st.error(result)

    # Salvataggio dei dati in CSV
    data = {
        "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Fv/Fm": [fvfm],
        "Chl TOT": [chl_tot],
        "CAR TOT": [car_tot],
        "SPAD": [spad],
        "qp": [qp],
        "qN": [qn],
        "Health Status": [result]
    }
    df = pd.DataFrame(data)

    if not os.path.exists("results.csv"):
        df.to_csv("results.csv", index=False)
    else:
        df.to_csv("results.csv", mode='a', header=False, index=False)

    st.info("Data saved to results.csv")

# Visualizza tabella dei risultati salvati, se presente
if os.path.exists("results.csv"):
    st.subheader("📅 Recorded Evaluations")
    saved_df = pd.read_csv("results.csv")
    st.dataframe(saved_df)

    # Grafici temporali dei parametri
    st.subheader("🌿 Trends Over Time")
    selected_param = st.selectbox("Select parameter to visualize:", ["Fv/Fm", "Chl TOT", "CAR TOT", "SPAD", "qp", "qN"])
    chart_df = saved_df[["timestamp", selected_param]]
    chart_df["timestamp"] = pd.to_datetime(chart_df["timestamp"])
    chart_df = chart_df.sort_values("timestamp")
    st.line_chart(chart_df.set_index("timestamp"))

    # Pulsante per scaricare il file
    csv = saved_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name='results.csv',
        mime='text/csv',
    )
