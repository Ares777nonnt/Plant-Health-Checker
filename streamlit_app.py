import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Imposta il layout e il titolo della pagina
st.set_page_config(page_title="Plant Health App", page_icon="🌿", layout="centered")

# CSS professionale
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #1b5e20, #2e7d32);
        background-size: 400% 400%;
        animation: gradientBG 30s ease infinite;
    }

    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    h1, h2, h3, h4 {
        color: #ffffff;
        font-weight: 600;
        margin-bottom: 0.2em;
    }

    .section-box {
        background-color: rgba(255, 255, 255, 0.06);
        padding: 1.5em;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin-bottom: 1.5em;
        color: #fff;
    }

    .section-title {
        font-size: 1.3em;
        margin-bottom: 1em;
        color: #ffffff;
        border-left: 5px solid #81c784;
        padding-left: 0.5em;
    }

    label {
        font-weight: 500;
        color: #eeeeee !important;
    }

    .stTextInput > div > input,
    .stNumberInput > div > div > input {
        background-color: #263238;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 0.5em;
    }

    .stDownloadButton button, .stButton button {
        background-color: #263238;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6em 1.2em;
        margin-top: 1em;
    }

    .stDownloadButton button:hover, .stButton button:hover {
        background-color: #37474f;
        color: white;
    }

    .footer-note {
        font-size: 0.85em;
        color: #cccccc;
        text-align: right;
        margin-top: 2em;
    }
    </style>
""", unsafe_allow_html=True)

# Funzione per valutare la salute della pianta
def evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn):
    score = 0
    if fvfm >= 0.80: score += 2
    elif fvfm >= 0.75: score += 1
    else: score -= 1

    if chl_tot >= 1.5: score += 2
    elif chl_tot >= 1.0: score += 1
    else: score -= 1

    if car_tot >= 0.5: score += 2
    elif car_tot >= 0.3: score += 1
    else: score -= 1

    if spad >= 40: score += 2
    elif spad >= 30: score += 1
    else: score -= 1

    if qp >= 0.7: score += 2
    elif qp >= 0.5: score += 1
    else: score -= 1

    if 0.3 <= qn <= 0.7: score += 2
    elif 0.2 <= qn < 0.3 or 0.7 < qn <= 0.8: score += 1
    else: score -= 1

    if score >= 10:
        return "🌿 Healthy – Optimal physiological state"
    elif 6 <= score < 10:
        return "🌱 Moderate stress – Monitor closely"
    else:
        return "⚠️ High stress – Likely physiological damage"

# Predizione del tipo di stress
def predict_stress_type(fvfm, chl_tot, car_tot, spad, qp, qn):
    triggers = []
    suggestion = ""

    if fvfm < 0.75 and chl_tot < 1.0 and spad < 30:
        triggers.append("Low Fv/Fm, Chl TOT and SPAD suggest Nutrient Deficiency")
        suggestion = "Consider fertilizing with nitrogen-rich nutrients."
        return "Nutrient Deficiency", triggers, suggestion
    elif fvfm < 0.75 and qp < 0.5 and qn > 0.7:
        triggers.append("Low Fv/Fm and qp with high qN suggest Excess Light Stress")
        suggestion = "Reduce light intensity and exposure duration."
        return "Excess Light Stress", triggers, suggestion
    elif fvfm < 0.75 and car_tot < 0.3 and spad < 30:
        triggers.append("Low Fv/Fm, CAR TOT and SPAD suggest Drought Stress")
        suggestion = "Increase irrigation frequency."
        return "Drought Stress", triggers, suggestion
    elif fvfm < 0.7 and chl_tot < 1.0 and car_tot < 0.3:
        triggers.append("Low Fv/Fm, Chl TOT and CAR TOT suggest Cold Stress")
        suggestion = "Protect from low temperatures."
        return "Cold Stress", triggers, suggestion
    else:
        triggers.append("No rules triggered.")
        suggestion = "Continue monitoring."
        return "No specific stress pattern detected", triggers, suggestion

# Titolo
st.markdown("""
    <h1 style='text-align: center;'>🌿 Plant Health Checker</h1>
    <p style='text-align: center;'>Enter the physiological parameters of your plant to assess its health status.</p>
    <p class="footer-note">Developed by Giuseppe Muscari Tomajoli ©2025</p>
""", unsafe_allow_html=True)

# Sezione sample info
with st.container():
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🧪 Sample Information</div>", unsafe_allow_html=True)
    species = st.text_input("Species (e.g., Arabidopsis thaliana)")
    sample_name = st.text_input("Sample name or ID")
    st.markdown("</div>", unsafe_allow_html=True)

# Sezione parametri fisiologici
with st.container():
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📊 Physiological Parameters</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        fvfm = st.number_input("🌿 Fv/Fm", min_value=0.0, max_value=1.0, step=0.01)
        chl_tot = st.number_input("🌿 Chlorophyll Total (Chl TOT)", min_value=0.0, step=0.1)
        spad = st.number_input("🔴 SPAD Value", min_value=0.0, step=0.1)

    with col2:
        car_tot = st.number_input("🍑 Carotenoids Total (CAR TOT)", min_value=0.0, step=0.1)
        qp = st.number_input("💡 qp (photochemical quenching)", min_value=0.0, max_value=1.0, step=0.01)
        qn = st.number_input("🔥 qN (non-photochemical quenching)", min_value=0.0, max_value=1.0, step=0.01)
    st.markdown("</div>", unsafe_allow_html=True)

# Valutazione
if st.button("🔍 Evaluate Health"):
    result = evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn)
    stress_type, triggers, suggestion = predict_stress_type(fvfm, chl_tot, car_tot, spad, qp, qn)

    st.markdown(f"""
        <div class='section-box'>
            <h4>{result}</h4>
            <p><b>Stress Type:</b> {stress_type}</p>
            <p><b>Suggestion:</b> {suggestion}</p>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Stress Rule Triggers"):
        for t in triggers:
            st.markdown(f"- {t}")

    # Salva su CSV
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
        "Stress Type": [stress_type],
        "Suggestion": [suggestion]
    }
    df = pd.DataFrame(data)
    if not os.path.exists("results.csv"):
        df.to_csv("results.csv", index=False)
    else:
        df.to_csv("results.csv", mode='a', header=False, index=False)
    st.success("✅ Data saved to results.csv")

# Risultati salvati
if os.path.exists("results.csv"):
    st.subheader("🗂️ Recorded Evaluations")
    if st.button("♻️ Reset Table"):
        os.remove("results.csv")
        st.warning("All evaluations deleted.")
    else:
        try:
            saved_df = pd.read_csv("results.csv")
            st.dataframe(saved_df)
            csv = saved_df.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Download Results (CSV)", data=csv, file_name='results.csv', mime='text/csv')
        except pd.errors.ParserError:
            st.error("⚠️ The results file is corrupted. Please reset the table.")
