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

# (resto del codice invariato fino a...)

# Evaluation
if st.button("🔍 Evaluate Health"):
    result = evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn)
    stress_type, triggers, suggestion = predict_stress_type(fvfm, chl_tot, car_tot, spad, qp, qn)
    show_result_card(result, stress_type, suggestion)
    with st.expander("📋 Stress Rule Triggers"):
        for t in triggers:
            st.markdown(f"- {t}")

    # Confronto con TRY
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

    # Salvataggio risultati
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
