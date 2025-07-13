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

# ---------- ESEMPIO DI SALVATAGGIO ----------
sample_id = st.text_input("🔍 Sample ID")
value = st.number_input("Enter a plant measurement value:")

if st.button("💾 Save Result") and sample_id:
    df = pd.DataFrame({"Sample ID": [sample_id], "Value": [value]})
    save_path = os.path.join(user_dir, f"{sample_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(save_path, index=False)
    st.success(f"✅ File saved as `{os.path.basename(save_path)}`")

# ---------- VISIONE FILE SALVATI ----------
st.markdown("### 📂 Your Saved Analyses")
files = os.listdir(user_dir)
if files:
    selected_file = st.selectbox("Choose a file to view:", files)
    if selected_file:
        df_loaded = pd.read_csv(os.path.join(user_dir, selected_file))
        st.dataframe(df_loaded)
else:
    st.info("You haven't saved any analysis yet.")
