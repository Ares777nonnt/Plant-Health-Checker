import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------- Configurazione iniziale ----------
st.set_page_config(page_title="Plant Health App", page_icon="🌿", layout="centered")

# ---------- Gradient background CSS ----------
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
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(to right, #4caf50, #81c784, #a5d6a7);
        margin: 30px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
    <h1 style='text-align: center;'>🌿 Plant Health Checker</h1>
    <p style='text-align: center;'>Enter the physiological parameters of your plant to assess its health status.</p>
    <p style='text-align: right; color: lightgray; font-size: 14px;'>Developed by Giuseppe Muscari Tomajoli ©2025</p>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------- USER DIRECTORY (NO LOGIN) ----------
user_dir = os.path.join("user_data", "default_user")
os.makedirs(user_dir, exist_ok=True)
st.info(f"📁 You are working in your personal space: `{user_dir}`")

# ---------- Input Sample Info ----------
species = st.text_input("Species (e.g., Arabidopsis thaliana)")
sample_name = st.text_input("Sample name or ID")

# ---------- Input dei parametri ----------
col1, col2 = st.columns(2)

with col1:
    fvfm = st.number_input("Fv/Fm", min_value=0.0, max_value=1.0, step=0.01)
    chl_tot = st.number_input("Chlorophyll Total (Chl TOT)", min_value=0.0, step=0.1)
    spad = st.number_input("SPAD Value", min_value=0.0, step=0.1)

with col2:
    car_tot = st.number_input("Carotenoids Total (CAR TOT)", min_value=0.0, step=0.1)
    qp = st.number_input("qp (photochemical quenching)", min_value=0.0, max_value=1.0, step=0.01)
    qn = st.number_input("qN (non-photochemical quenching)", min_value=0.0, max_value=1.0, step=0.01)

# ---------- Funzione di valutazione ----------
def evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn):
    score = 0
    if fvfm >= 0.80:
        score += 2
    elif fvfm >= 0.75:
        score += 1
    else:
        score -= 1
    if chl_tot >= 1.5:
        score += 2
    elif chl_tot >= 1.0:
        score += 1
    else:
        score -= 1
    if car_tot >= 0.5:
        score += 2
    elif car_tot >= 0.3:
        score += 1
    else:
        score -= 1
    if spad >= 40:
        score += 2
    elif spad >= 30:
        score += 1
    else:
        score -= 1
    if qp >= 0.7:
        score += 2
    elif qp >= 0.5:
        score += 1
    else:
        score -= 1
    if 0.3 <= qn <= 0.7:
        score += 2
    elif 0.2 <= qn < 0.3 or 0.7 < qn <= 0.8:
        score += 1
    else:
        score -= 1

    if score >= 10:
        return "🌿 Healthy – Optimal physiological state"
    elif 6 <= score < 10:
        return "🌱 Moderate stress – Monitor closely"
    else:
        return "⚠️ High stress – Likely physiological damage"

# ---------- Funzione di predizione stress ----------
def predict_stress_type(fvfm, chl_tot, car_tot, spad, qp, qn):
    triggers = []
    suggestion = ""
    if fvfm < 0.75 and chl_tot < 1.0 and spad < 30:
        triggers.append("Low Fv/Fm, Chl TOT and SPAD suggest Nutrient Deficiency")
        suggestion = "Consider fertilizing with nitrogen-rich nutrients and monitor chlorophyll content."
        return "Nutrient Deficiency", triggers, suggestion
    elif fvfm < 0.75 and qp < 0.5 and qn > 0.7:
        triggers.append("Low Fv/Fm and qp with high qN suggest Excess Light Stress")
        suggestion = "Reduce light intensity or duration; consider partial shading during peak sunlight."
        return "Excess Light Stress", triggers, suggestion
    elif fvfm < 0.75 and car_tot < 0.3 and spad < 30:
        triggers.append("Low Fv/Fm, CAR TOT and SPAD suggest Drought Stress")
        suggestion = "Increase irrigation frequency and ensure consistent soil moisture levels."
        return "Drought Stress", triggers, suggestion
    elif fvfm < 0.7 and chl_tot < 1.0 and car_tot < 0.3:
        triggers.append("Low Fv/Fm, Chl TOT and CAR TOT suggest Cold Stress")
        suggestion = "Protect plant from low temperatures; consider temporary heating or insulation."
        return "Cold Stress", triggers, suggestion
    else:
        triggers.append("No rules triggered based on input thresholds")
        suggestion = "No specific corrective action identified; continue monitoring."
        return "No specific stress pattern detected", triggers, suggestion

# ---------- Valutazione ----------
if st.button("🔍 Evaluate Health"):
    result = evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn)
    stress_type, triggers, suggestion = predict_stress_type(fvfm, chl_tot, car_tot, spad, qp, qn)

    if "Healthy" in result:
        st.success(result)
    elif "Moderate" in result:
        st.warning(result)
    else:
        st.error(result)

    st.markdown(f"<h4>🧬 Predicted Stress Type: <i>{stress_type}</i></h4>", unsafe_allow_html=True)
    with st.expander("View stress rule triggers"):
        for t in triggers:
            st.markdown(f"- {t}")
    st.info(f"💡 Suggestion: {suggestion}")

    # ---------- Salvataggio ----------
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

    csv_path = os.path.join(user_dir, "results.csv")
    if not os.path.exists(csv_path):
        df.to_csv(csv_path, index=False)
    else:
        df.to_csv(csv_path, mode='a', header=False, index=False)
    st.success("Data saved successfully!")

# ---------- Visualizzazione ----------
if os.path.exists(os.path.join(user_dir, "results.csv")):
    st.markdown("### 📅 Recorded Evaluations")
    if st.button("Reset Table"):
        os.remove(os.path.join(user_dir, "results.csv"))
        st.warning("All recorded evaluations have been deleted.")
    else:
        try:
            saved_df = pd.read_csv(os.path.join(user_dir, "results.csv"))
            st.dataframe(saved_df)
            csv = saved_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Results as CSV", data=csv, file_name='results.csv', mime='text/csv')
        except pd.errors.ParserError:
            st.error("⚠️ The results file is corrupted. Please reset the table.")
