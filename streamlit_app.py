import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Imposta il layout e il titolo della pagina
st.set_page_config(page_title="Plant Health App", page_icon="🌿", layout="centered")

# CSS con gradiente "Forest Twilight" – scuro, elegante, con contrasto
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        height: 100%;
        margin: 0;
        padding: 0;
        font-family: 'sans-serif';
    }

    .stApp {
        background: linear-gradient(135deg, #263238, #2e7d32, #004d40);
        background-size: 400% 400%;
        animation: gradientBG 30s ease infinite;
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

# Funzione rule-based per tipo di stress con log di trigger

def predict_stress_type(fvfm, chl_tot, car_tot, spad, qp, qn):
    triggers = []

    if fvfm < 0.75 and chl_tot < 1.0 and spad < 30:
        triggers.append("Low Fv/Fm, Chl TOT and SPAD suggest Nutrient Deficiency")
        return "Nutrient Deficiency", triggers
    elif fvfm < 0.75 and qp < 0.5 and qn > 0.7:
        triggers.append("Low Fv/Fm and qp with high qN suggest Excess Light Stress")
        return "Excess Light Stress", triggers
    elif fvfm < 0.75 and car_tot < 0.3 and spad < 30:
        triggers.append("Low Fv/Fm, CAR TOT and SPAD suggest Drought Stress")
        return "Drought Stress", triggers
    elif fvfm < 0.7 and chl_tot < 1.0 and car_tot < 0.3:
        triggers.append("Low Fv/Fm, Chl TOT and CAR TOT suggest Cold Stress")
        return "Cold Stress", triggers
    else:
        triggers.append("No rules triggered based on input thresholds")
        return "No specific stress pattern detected", triggers

# Titolo principale
st.markdown("""
    <h1 style='text-align: center;'>🌿 Plant Health Checker</h1>
    <p style='text-align: center;'>Enter the physiological parameters of your plant to assess its health status.</p>
""", unsafe_allow_html=True)

# Input: specie e nome campione
species = st.text_input("Species (e.g., Arabidopsis thaliana)")
sample_name = st.text_input("Sample name or ID")

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
    stress_type, triggers = predict_stress_type(fvfm, chl_tot, car_tot, spad, qp, qn)

    if "Healthy" in result:
        st.success(result)
    elif "Moderate" in result:
        st.warning(result)
    else:
        st.error(result)

    st.markdown(f"<h4>🩸 Predicted Stress Type: <i>{stress_type}</i></h4>", unsafe_allow_html=True)

    with st.expander("View stress rule triggers"):
        for t in triggers:
            st.markdown(f"- {t}")

    # Salvataggio dei dati in CSV
    data = {
        "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Species": [species],
        "Sample Name": [sample_name],
        "Fv/Fm": [fvfm],
        "Chl TOT": [chl_tot],
        "CAR TOT": [car_tot],
        "SPAD": [spad],
        "qp": [qp],
        "qN": [qn],
        "Health Status": [result],
        "Stress Type": [stress_type]
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

    # Pulsante per resettare i dati
    if st.button("Reset Table"):
        os.remove("results.csv")
        st.warning("All recorded evaluations have been deleted.")
    else:
        saved_df = pd.read_csv("results.csv")
        st.dataframe(saved_df)

        # Pulsante per scaricare il file
        csv = saved_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name='results.csv',
            mime='text/csv',
        )
