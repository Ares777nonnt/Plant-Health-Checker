import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# Imposta il layout e il titolo della pagina
st.set_page_config(page_title="Plant Health App", page_icon="🌿", layout="centered")

# CSS stile e sfondo
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

# Logo + Header
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

# Carica dataset TRY filtrato da Google Drive
file_id = "1ERs5PVDraOtvG20KLxO-g49l8AIyFoZo"
url = f"https://drive.google.com/uc?id={file_id}&export=download"
try_df = pd.read_csv(url)
try_df["AccSpeciesName"] = try_df["AccSpeciesName"].astype(str).str.strip().str.title()
species_list = sorted(try_df["AccSpeciesName"].dropna().unique())

# Input utente
species = st.selectbox("🌱 Select or search for the species", options=species_list, index=None, placeholder="Start typing...")
sample_name = st.text_input("Sample name or ID")

# Parametri fisiologici
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

# Valutazione
if st.button("🔍 Evaluate Health"):
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
        return "TBD", [], "Suggestion TBD"

    def show_result_card(result, stress_type, suggestion):
        st.success(result)
        st.info(f"Stress Type: {stress_type}\nSuggestion: {suggestion}")

    result = evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn)
    stress_type, triggers, suggestion = predict_stress_type(fvfm, chl_tot, car_tot, spad, qp, qn)
    show_result_card(result, stress_type, suggestion)

    with st.expander("📋 Stress Rule Triggers"):
        for t in triggers:
            st.markdown(f"- {t}")

    matched_species = next((s for s in species_list if s.lower() == species.lower()), None)
    if matched_species:
        subset = try_df[try_df["AccSpeciesName"] == matched_species]

        

        means = subset.groupby("TraitID")["StdValue"].mean()

        trait_map = {
            "Fv/Fm": 3393,
            "Chl TOT": 413,
            "CAR TOT": 491,
            "SPAD": 3001,
            "qN": 3978
        }

        st.markdown("<div class='section-title'>📊 Comparison with TRY Database</div>", unsafe_allow_html=True)
        for label, trait_id in trait_map.items():
            mean_val = means.get(trait_id, None)
            if mean_val is not None and not pd.isna(mean_val):
                user_val = {
    "Fv/Fm": fvfm,
    "Chl TOT": chl_tot,
    "CAR TOT": car_tot,
    "SPAD": spad,
    "qN": qn
}.get(label, None)
                diff = user_val - mean_val
                st.markdown(f"**{label}**: You = {user_val:.2f}, TRY Mean = {mean_val:.2f} → Δ = {diff:.2f}")
            else:
                st.markdown(f"**{label}**: No valid data available in TRY for this trait.")

# Footer contatti
st.markdown("""
<hr class="divider">
<p style='text-align: center; color: lightgray;'>For inquiries or feedback, contact <a href="mailto:giuseppemuscari.gm@gmail.com">giuseppemuscari.gm@gmail.com</a></p>
""", unsafe_allow_html=True)
