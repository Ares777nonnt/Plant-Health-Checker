import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
import io

# Imposta layout e titolo
st.set_page_config(page_title="Plant Health Checker", page_icon="🌿", layout="centered")

# =============================
# CSS – Nuovo stile coerente con il sito personale
# =============================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    html, body, [class*="css"]  {
        height: 100%;
        margin: 0;
        padding: 0;
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: linear-gradient(to bottom, #001a17, #0a3d35);
        color: white;
        padding-bottom: 120px;
        overflow-x: hidden;
    }

    .hero-container {
        text-align: center;
        padding: 90px 20px 50px 20px;
        animation: fadeIn 2s ease-in-out;
    }

    @keyframes fadeIn {
        0% {opacity: 0; transform: translateY(30px);}
        100% {opacity: 1; transform: translateY(0);}
    }

    .hero-title {
        font-size: 54px;
        font-weight: 600;
        color: #76c7a1;
        margin-bottom: 10px;
        text-shadow: 0 0 12px #76c7a1, 0 0 30px #2bffb1;
        animation: glowPulse 4s infinite alternate;
    }

    @keyframes glowPulse {
        from {text-shadow: 0 0 12px #76c7a1, 0 0 30px #2bffb1;}
        to {text-shadow: 0 0 20px #2bffb1, 0 0 50px #76c7a1;}
    }

    .hero-subtitle {
        font-size: 20px;
        color: #b7ffde;
        font-weight: 300;
    }

    .section-title {
        font-size: 24px;
        margin-top: 50px;
        margin-bottom: 20px;
        font-weight: 600;
        color: #b7ffde;
        text-align: center;
        text-shadow: 0 0 10px #00ffcc40;
    }

    .result-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 25px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
        color: white;
    }

    .stButton button {
        background: linear-gradient(90deg, #00b894, #2ecc71);
        color: white;
        border: none;
        font-weight: 600;
        border-radius: 10px;
        padding: 10px 20px;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px #00b89480;
    }

    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px #00ffc380;
    }

    .dataframe tbody tr:hover {
        background-color: #013e35 !important;
    }

    .footer-container {
        background: #001a17;
        color: #cccccc;
        text-align: center;
        padding: 40px 0;
        margin-top: 80px;
        border-top: 1px solid #1f5c4f;
    }

    .footer-container a {
        color: #76c7a1;
        text-decoration: none;
        margin: 0 10px;
        font-weight: 500;
    }

    .footer-container a:hover {
        color: #b7ffde;
    }

    .contact-icons {
        display: flex;
        justify-content: center;
        gap: 25px;
        margin-top: 15px;
        flex-wrap: wrap;
    }

    .contact-icon img {
        width: 30px;
        height: 30px;
        transition: transform 0.2s ease;
    }

    .contact-icon:hover img {
        transform: scale(1.15);
    }
    </style>
""", unsafe_allow_html=True)

# =============================
# HERO SECTION
# =============================
with open("logo.png", "rb") as f:
    data = base64.b64encode(f.read()).decode("utf-8")

st.markdown(f"""
    <div class='hero-container'>
        <img src='data:image/png;base64,{data}' width='250'/>
        <h1 class='hero-title'>Plant Health Checker</h1>
        <p class='hero-subtitle'>Inspired by astrobiology research and plant physiology</p>
        <p style='color:#d1fff0; margin-top:10px;'>Enter the physiological parameters of your plant to assess its health status.</p>
    </div>
""", unsafe_allow_html=True)

# =============================
# LOGICA PRINCIPALE
# =============================
if "results" not in st.session_state:
    st.session_state.results = []

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

    if score >= 10: return "🌿 Healthy – Optimal physiological state"
    elif 6 <= score < 10: return "🌱 Moderate stress – Monitor closely"
    else: return "⚠️ High stress – Likely physiological damage"

def predict_stress_type(fvfm, chl_tot, car_tot, spad, qp, qn):
    triggers, suggestion = [], ""
    if fvfm < 0.75 and chl_tot < 1.0 and spad < 30:
        triggers.append("Low Fv/Fm, Chl TOT and SPAD suggest Nutrient Deficiency")
        suggestion = "Consider fertilizing with nitrogen-rich nutrients and monitor chlorophyll content."
        return "Nutrient Deficiency", triggers, suggestion
    elif fvfm < 0.75 and qp < 0.5 and qn > 0.7:
        triggers.append("Low Fv/Fm and qp with high qN suggest Excess Light Stress")
        suggestion = "Reduce light intensity or duration; consider partial shading during peak sunlight."
        return "Excess Light Stress", triggers, suggestion
    else:
        triggers.append("No rules triggered based on input thresholds")
        suggestion = "No specific corrective action identified; continue monitoring."
        return "No specific stress pattern detected", triggers, suggestion

def show_result_card(result, stress_type, suggestion):
    color = "#388e3c" if "Healthy" in result else ("#fbc02d" if "Moderate" in result else "#d32f2f")
    emoji = "🌿" if "Healthy" in result else ("🌱" if "Moderate" in result else "⚠️")
    st.markdown(f'''<div class="result-card" style="border-left: 5px solid {color};">
        <h3 style="margin-bottom:0; color:{color};">{emoji} {result}</h3>
        <p><b>🔎 Stress Type:</b> {stress_type}</p>
        <p><b>💡 Suggestion:</b> {suggestion}</p>
    </div>''', unsafe_allow_html=True)

# CARICA DATI TRY
file_id = "1ERs5PVDraOtvG20KLxO-g49l8AIyFoZo"
url = f"https://drive.google.com/uc?id={file_id}&export=download"
try_df = pd.read_csv(url)
try_df["AccSpeciesName"] = try_df["AccSpeciesName"].astype(str).str.strip().str.title()
species_list = sorted(try_df["AccSpeciesName"].dropna().unique())

# INPUT
species = st.selectbox("🌱 Select or search for the species", options=species_list, index=None, placeholder="Start typing...")
sample_name = st.text_input("Sample name or ID")

st.markdown("<div class='section-title'>📊 Physiological Parameters</div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    fvfm = st.number_input("🍃 Fv/Fm", min_value=0.0, max_value=1.0, step=0.01)
    chl_tot = st.number_input("🌿 Chlorophyll Total (Chl TOT)", min_value=0.0, step=0.1)
    spad = st.number_input("🔴 SPAD Value", min_value=0.0, step=0.1)
with col2:
    car_tot = st.number_input("🍊 Carotenoids Total (CAR TOT)", min_value=0.0, step=0.1)
    qp = st.number_input("💡 qp (photochemical quenching)", min_value=0.0, max_value=1.0, step=0.01)
    qn = st.number_input("🔥 qN (non-photochemical quenching)", min_value=0.0, max_value=1.0, step=0.01)

# VALUTAZIONE
if st.button("🔍 Evaluate Health"):
    result = evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn)
    stress_type, triggers, suggestion = predict_stress_type(fvfm, chl_tot, car_tot, spad, qp, qn)
    show_result_card(result, stress_type, suggestion)

    st.session_state.results.append({
        "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "Sample Name": sample_name,
        "Species": species,
        "Fv/Fm": fvfm,
        "Chl TOT": chl_tot,
        "CAR TOT": car_tot,
        "SPAD": spad,
        "qp": qp,
        "qN": qn,
        "Status": result,
        "Stress Type": stress_type
    })

    with st.expander("📋 Stress Rule Triggers"):
        for t in triggers:
            st.markdown(f"- {t}")

# TABELLA
if st.session_state.results:
    st.markdown("<div class='section-title'>📁 Sampled Records</div>", unsafe_allow_html=True)
    result_df = pd.DataFrame(st.session_state.results)
    st.dataframe(result_df, use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        result_df.to_excel(writer, index=False)

    st.download_button("⬇️ Download Excel File", data=output.getvalue(), file_name="plant_health_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if st.button("🗑️ Reset All Records"):
        st.session_state.results.clear()
        st.success("Records have been cleared.")

# FOOTER
footer = f"""
<div class='footer-container'>
    <img src='data:image/png;base64,{data}' alt='Logo'/>
    <div class='contact-icons'>
        <a href='mailto:giuseppemuscari.gm@gmail.com' class='contact-icon'>📩 Email</a>
        <a href='https://www.linkedin.com/in/giuseppemuscaritomajoli' target='_blank' class='contact-icon'>🔗 LinkedIn</a>
        <a href='https://www.instagram.com/giuseppemuscari' target='_blank' class='contact-icon'>📸 Instagram</a>
    </div>
    <div style='margin-top:10px; color:#76c7a1;'>©2025 Giuseppe Muscari Tomajoli</div>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
