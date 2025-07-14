import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64


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

# Carica il dataset TRY da GitHub (solo nomi specie)
try_df = pd.read_csv("https://raw.githubusercontent.com/Ares777nonnt/Plant-Health-Checker/main/try_subset.csv")
species_list = sorted(try_df["AccSpeciesName"].dropna().unique())

# Species input (autocomplete + default)
species_input = st.text_input("Species (start typing to search)", "")
matches = [sp for sp in species_list if species_input.lower() in sp.lower()]
species = st.selectbox("Select species", matches) if matches else species_input

# Sample name
sample_name = st.text_input("Sample name or ID")
