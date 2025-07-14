import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
import io

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
      .footer-container {{
      position: relative;
      bottom: 0;
      width: 100%;
      background-color: #002220;
      color: #cccccc;
      text-align: center;
      padding: 20px 0;
      margin-top: 50px;
  }}
  .footer-container img {{
      width: 40px;
      margin-bottom: 10px;
  }}
  .footer-container a {{
      color: #76c7a1;
      text-decoration: none;
      margin: 0 10px;
      font-weight: bold;
  }}
  .footer-container a:hover {{
      text-decoration: underline;
  }}
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

# Inizializza memoria per i risultati multipli
if "results" not in st.session_state:
    st.session_state.results = []

# Funzioni principali
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

    matched_species = next((s for s in species_list if s.lower() == species.lower()), None)
    if matched_species:
        subset = try_df[try_df["AccSpeciesName"] == matched_species]
        means = subset.groupby("TraitID")["StdValue"].mean()

        trait_map = {
            "Chl TOT": 413
        }

        st.markdown("<div class='section-title'>📊 Comparison with TRY Database</div>", unsafe_allow_html=True)
        for label, trait_id in trait_map.items():
            mean_val = means.get(trait_id, None)
            if mean_val is not None and not pd.isna(mean_val):
                user_val = eval(label.lower().replace("/", "").replace(" ", "_"))
                diff = user_val - mean_val
                st.markdown(f"**{label}**: You = {user_val:.2f}, TRY Mean = {mean_val:.2f} → Δ = {diff:.2f}")
            else:
                st.markdown(f"**{label}**: No valid data available in TRY for this trait.")

# Tabella risultati
if st.session_state.results:
    st.markdown("<div class='section-title'>📁 Sampled Records</div>", unsafe_allow_html=True)
    result_df = pd.DataFrame(st.session_state.results)
    st.dataframe(result_df, use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        result_df.to_excel(writer, index=False)

    st.download_button(
        "⬇️ Download Excel File",
        data=output.getvalue(),
        file_name="plant_health_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("🗑️ Reset All Records"):
        st.session_state.results.clear()
        st.success("Records have been cleared. You may manually rerun the app if needed.")

footer = f"""
<div class="footer-container">
    <img src='data:image/png;base64,{data}' alt="Logo"/>
    <div>
        <a href="mailto:giuseppemuscari.gm@gmail.com">📩 Email</a> ·
        <a href="https://www.linkedin.com/in/giuseppemuscaritomajoli" target="_blank">🔗 LinkedIn</a> ·
        <a href="https://www.instagram.com/giuseppemuscari" target="_blank">📸 Instagram</a>
    </div>
    <div style="margin-top: 5px;">©2025 Giuseppe Muscari Tomajoli</div>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
