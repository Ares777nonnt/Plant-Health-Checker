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

# Qui andrebbero le funzioni evaluate_plant_health(), predict_stress_type() e show_result_card(),
# che non erano incluse nel canvas ma sono essenziali. Vanno incollate qui per far funzionare l'app.

# Valutazione
if st.button("🔍 Evaluate Health"):
    result = evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn)
    stress_type, triggers, suggestion = predict_stress_type(fvfm, chl_tot, car_tot, spad, qp, qn)
    show_result_card(result, stress_type, suggestion)

    with st.expander("📋 Stress Rule Triggers"):
        for t in triggers:
            st.markdown(f"- {t}")

    try_df = load_try_data()
    if isinstance(try_df, pd.DataFrame) and species:
        user_vals = {
            "SPAD": spad,
            "Fv/Fm": fvfm,
            "Chl TOT": chl_tot,
            "CAR TOT": car_tot,
            "NPQ": qn
        }
        st.markdown("### 📊 Comparison with TRY Database:")
        result_table = compare_to_try(species, user_vals, try_df)
        for trait, data in result_table.items():
            st.markdown(f"**{trait}**: {data['Status']}  \n"
                        f"Your value: {data['User value']} | TRY avg: {data['TRY mean']} ± {data['TRY std']}")

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
    st.info("Data saved to results.csv")

if os.path.exists("results.csv"):
    st.subheader("💼 Recorded Evaluations")
    if st.button("♻️ Reset Table"):
        os.remove("results.csv")
        st.warning("All recorded evaluations have been deleted.")
    else:
        try:
            saved_df = pd.read_csv("results.csv")
            st.dataframe(saved_df)
            csv = saved_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results (CSV)",
                data=csv,
                file_name='results.csv',
                mime='text/csv',
            )
        except pd.errors.ParserError:
            st.error("⚠️ The results file is corrupted. Please reset the table.")

st.markdown("""
<hr class="divider">
<div class='section-title'>📘 Interpretation of Confidence Levels</div>
<ul>
  <li><b>High confidence</b>: strong match with one known stress profile.</li>
  <li><b>Medium confidence</b>: moderate consistency; some overlap possible.</li>
  <li><b>Low confidence</b>: ambiguous or mixed stress indicators.</li>
</ul>
""", unsafe_allow_html=True)
