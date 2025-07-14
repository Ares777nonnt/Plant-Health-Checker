import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

st.set_page_config(page_title="Plant Health App", page_icon="🌿", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="css"]  {
        height: 100%;
        margin: 0;
        padding: 0;
        font-family: 'Segoe UI', sans-serif;
    }
    .stApp {
        background-color: #002220;
        color: white;
        padding-bottom: 120px;
    }
    .section-title {
        font-size: 24px;
        margin-bottom: 10px;
        font-weight: bold;
        color: white;
    }
    hr.divider {
        border: none;
        border-top: 2px dashed #bdbdbd;
        margin: 30px 0;
    }
    @media (max-width: 768px) {
        .header-container {
            flex-direction: column !important;
            text-align: center;
        }
        .header-container img {
            margin-bottom: 10px;
            width: 300px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_try_data():
    url = "https://raw.githubusercontent.com/Ares777nonnt/Plant-Health-Checker/refs/heads/main/try_subset.csv"
    return pd.read_csv(url)

trait_map = {
    "SPAD": 3001,
    "Fv/Fm": 3393,
    "Chl TOT": 413,
    "CAR TOT": 491,
    "NPQ": 3978
}

def compare_to_try(species_name, user_values, try_df):
    results = {}
    for trait_label, trait_id in trait_map.items():
        subset = try_df[
            (try_df["AccSpeciesName"].str.lower() == species_name.lower()) &
            (try_df["TraitID"] == trait_id)
        ]
        if not subset.empty:
            mean = subset["StdValue"].mean()
            std = subset["StdValue"].std()
            val = user_values.get(trait_label)
            if val is not None:
                if val < mean - std:
                    status = "🔴 Below typical range"
                elif val > mean + std:
                    status = "🟠 Above typical range"
                else:
                    status = "🟢 Within typical range"
                results[trait_label] = {
                    "User value": val,
                    "TRY mean": round(mean, 2),
                    "TRY std": round(std, 2),
                    "Status": status
                }
    return results

try_df = load_try_data()
species_list = sorted(try_df["AccSpeciesName"].dropna().unique())

with open("logo.png", "rb") as f:
    data = base64.b64encode(f.read()).decode("utf-8")

st.markdown(f"""
    <div class='header-container' style='display: flex; justify-content: center; align-items: center;'>
        <img src='data:image/png;base64,{data}' width='300' style='margin-right:10px;' class='header-logo'/>
        <h1 style='margin:0;'>Plant Health Checker</h1>
    </div>
    <p style='text-align: center;'>Enter the physiological parameters of your plant to assess its health status.</p>
    <p style='text-align: right; color: lightgray; font-size: 14px;'>Developed by Giuseppe Muscari Tomajoli ©2025</p>
""", unsafe_allow_html=True)

st.markdown("<div class='section-title'>🧪 Sample Information</div>", unsafe_allow_html=True)
species = st.text_input("Species (autocomplete)", placeholder="Start typing...")
if species:
    matches = sorted([s for s in species_list if species.lower() in s.lower()], key=lambda x: x.lower().startswith(species.lower()), reverse=True)
    if matches:
        species = st.selectbox("Suggestions", matches, index=0)
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

# Contact Box
st.markdown("<div class='section-title'>📫 Contact the Author</div>", unsafe_allow_html=True)
st.markdown("For questions, suggestions, or collaborations, please email: <a href='mailto:giuseppemuscari.gm@gmail.com'>giuseppemuscari.gm@gmail.com</a>", unsafe_allow_html=True)

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

def predict_stress_type(fvfm, chl_tot, car_tot, spad, qp, qn):
    triggers = []
    suggestion = ""
    confidence = "Low"

    if fvfm < 0.75 and chl_tot < 1.0 and spad < 30:
        triggers.append("Low Fv/Fm, Chl TOT and SPAD suggest Nutrient Deficiency")
        suggestion = "Consider fertilizing with nitrogen-rich nutrients and monitor chlorophyll content."
        return "Nutrient Deficiency (confidence: medium)", triggers, suggestion
    elif fvfm < 0.75 and qp < 0.5 and qn > 0.7:
        triggers.append("Low Fv/Fm and qp with high qN suggest Excess Light Stress")
        suggestion = "Reduce light intensity or duration; consider partial shading during peak sunlight."
        return "Excess Light Stress (confidence: medium)", triggers, suggestion
    elif fvfm < 0.75 and car_tot < 0.3 and spad < 30:
        triggers.append("Low Fv/Fm, CAR TOT and SPAD suggest Drought Stress")
        suggestion = "Increase irrigation frequency and ensure consistent soil moisture levels."
        return "Drought Stress (confidence: medium)", triggers, suggestion
    elif fvfm < 0.7 and chl_tot < 1.0 and car_tot < 0.3:
        triggers.append("Low Fv/Fm, Chl TOT and CAR TOT suggest Cold Stress")
        suggestion = "Protect plant from low temperatures; consider temporary heating or insulation."
        return "Cold Stress (confidence: medium)", triggers, suggestion
    elif fvfm < 0.75 and qn > 0.7 and chl_tot < 1.0:
        triggers.append("High qN, low Fv/Fm and Chl TOT suggest Heat Stress")
        suggestion = "Ensure adequate ventilation and shading; avoid peak heat exposure."
        return "Heat Stress (confidence: low)", triggers, suggestion
    elif fvfm < 0.75 and qp < 0.5 and chl_tot < 1.0:
        triggers.append("Low Fv/Fm, qp and Chl TOT suggest Salinity Stress")
        suggestion = "Check salinity levels in the soil and use salt-tolerant cultivars."
        return "Salinity Stress (confidence: low)", triggers, suggestion
    elif fvfm < 0.7 and chl_tot < 1.0 and qp < 0.5:
        triggers.append("Low Fv/Fm, qp and Chl TOT suggest Heavy Metal Stress")
        suggestion = "Consider phytoremediation or reduce metal exposure in the environment."
        return "Heavy Metal Stress (confidence: low)", triggers, suggestion
    elif qp < 0.4 and fvfm < 0.75:
        triggers.append("Low qp and Fv/Fm may indicate Pathogen or Biotic Stress")
        suggestion = "Inspect for pest/pathogen presence and apply biocontrol if needed."
        return "Biotic Stress (confidence: low)", triggers, suggestion
    elif fvfm < 0.75 and qn > 0.7 and car_tot < 0.3:
        triggers.append("Low Fv/Fm, CAR TOT and high qN may indicate Ozone Stress")
        suggestion = "Minimize exposure to air pollutants and monitor for oxidative damage."
        return "Ozone Stress (confidence: low)", triggers, suggestion
    else:
        triggers.append("No rules triggered based on input thresholds")
        suggestion = "No specific corrective action identified; continue monitoring."
        return "No specific stress pattern detected", triggers, suggestion

def show_result_card(result, stress_type, suggestion):
    if "Healthy" in result:
        color = "#388e3c"
        emoji = "🌿"
    elif "Moderate" in result:
        color = "#fbc02d"
        emoji = "🌱"
    else:
        color = "#d32f2f"
        emoji = "⚠️"

    st.markdown(f'''
    <div style="background-color:{color}; padding:20px; border-radius:10px; color:white;">
        <h3 style="margin-bottom:0;">{emoji} {result}</h3>
        <p style="font-size:16px;"><b>🔎 Stress Type:</b> {stress_type}</p>
        <p style="font-size:16px;"><b>💡 Suggestion:</b> {suggestion}</p>
    </div>
    ''', unsafe_allow_html=True)
