import streamlit as st
import pandas as pd
from datetime import datetime

# Funzione di valutazione dello stress vegetale basata su soglie
@st.cache_data
def evaluate_plant_health(fvfm, spad, chl_tot, car_tot, qp, qn):
    if fvfm < 0.6 or spad < 20 or chl_tot < 1.0 or car_tot < 1.0 or qp < 0.4 or qn > 0.6:
        return "❌ High Stress", "Reduce light intensity and check nutrient availability."
    elif fvfm < 0.75 or spad < 30 or chl_tot < 2.0 or car_tot < 2.0 or qp < 0.6 or qn > 0.5:
        return "⚠️ Moderate Stress", "Monitor environmental conditions closely."
    else:
        return "✅ Healthy", "Keep current cultivation conditions."

# Titolo e firma
st.title("🌿 Plant Health Evaluation")
st.markdown("<h5 style='text-align: right; color: gray;'>Developed by Giuseppe Muscari Tomajoli ©2025</h5>", unsafe_allow_html=True)

# Input utente
st.subheader("📥 Insert Sample Data")
species = st.text_input("Species")
sample_name = st.text_input("Sample Name")
fvfm = st.slider("Fv/Fm", 0.0, 1.0, 0.75)
chl_tot = st.slider("Chl TOT", 0.0, 5.0, 1.5)
car_tot = st.slider("CAR TOT", 0.0, 5.0, 1.0)
spad = st.slider("SPAD", 0.0, 60.0, 30.0)
qp = st.slider("qp", 0.0, 1.0, 0.6)
qn = st.slider("qN", 0.0, 1.0, 0.4)

# Valutazione
if st.button("Evaluate"):
    status, advice = evaluate_plant_health(fvfm, spad, chl_tot, car_tot, qp, qn)
    st.subheader("🧪 Evaluation Result")
    st.success(f"Status: {status}")
    st.info(f"Advice: {advice}")

    result = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Species": species,
        "Sample": sample_name,
        "FvFm": fvfm,
        "SPAD": spad,
        "ChlTOT": chl_tot,
        "CARTOT": car_tot,
        "qp": qp,
        "qN": qn,
        "Status": status,
        "Advice": advice
    }

    try:
        existing_df = pd.read_csv("results.csv")
        df = pd.concat([existing_df, pd.DataFrame([result])], ignore_index=True)
    except:
        df = pd.DataFrame([result])

    df.to_csv("results.csv", index=False)

# Visualizzazione dati salvati
st.markdown("---")
st.subheader("📅 Recorded Evaluations")
try:
    saved_df = pd.read_csv("results.csv")
    st.dataframe(saved_df)
    if st.button("🔁 Reset Table"):
        saved_df = pd.DataFrame()
        saved_df.to_csv("results.csv", index=False)
        st.experimental_rerun()
except:
    st.info("No saved data yet.")
