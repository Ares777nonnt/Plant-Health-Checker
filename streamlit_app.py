import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path

# === CONFIGURAZIONE UTENTI ===
CREDENTIALS_FILE = "users.json"

# Carica o inizializza gli utenti
if Path(CREDENTIALS_FILE).exists():
    with open(CREDENTIALS_FILE, "r") as f:
        credentials = json.load(f)
else:
    credentials = {"usernames": {}}

# Funzione per registrare un nuovo utente
def register_user():
    st.subheader("📝 Register")
    new_name = st.text_input("Full Name")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    if st.button("Register"):
        if new_username in credentials["usernames"]:
            st.warning("⚠️ Username already exists.")
        else:
            hashed_pw = stauth.Hasher([new_password]).generate()[0]
            credentials["usernames"][new_username] = {
                "name": new_name,
                "password": hashed_pw
            }
            with open(CREDENTIALS_FILE, "w") as f:
                json.dump(credentials, f, indent=4)
            st.success("✅ Registration successful! Please log in.")

# === AUTENTICAZIONE ===
authenticator = stauth.Authenticate(
    list(credentials['usernames'].values()),
    list(credentials['usernames'].keys()),
    [v['password'] for v in credentials['usernames'].values()],
    "plant_health_app", "abcdef", cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status is None:
    st.warning("🔒 Please log in or register.")
    with st.expander("Don't have an account?"):
        register_user()

elif authentication_status is False:
    st.error("❌ Incorrect username or password")

elif authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Logged in as {name}")

    # === APP PRINCIPALE ===

    st.set_page_config(page_title="Plant Health App", page_icon="🌿", layout="centered")

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
        </style>
    """, unsafe_allow_html=True)

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

    def show_result_card(result, stress_type, suggestion):
        if "Healthy" in result: color = "#388e3c"; emoji = "🌿"
        elif "Moderate" in result: color = "#fbc02d"; emoji = "🌱"
        else: color = "#d32f2f"; emoji = "⚠️"
        st.markdown(f'''
        <div style="background-color:{color}; padding:20px; border-radius:10px; color:white;">
            <h3 style="margin-bottom:0;">{emoji} {result}</h3>
            <p style="font-size:16px;"><b>🔎 Stress Type:</b> {stress_type}</p>
            <p style="font-size:16px;"><b>💡 Suggestion:</b> {suggestion}</p>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("""
        <h1 style='text-align: center;'>🌿 Plant Health Checker</h1>
        <p style='text-align: center;'>Enter the physiological parameters of your plant to assess its health status.</p>
        <p style='text-align: right; color: lightgray; font-size: 14px;'>Developed by Giuseppe Muscari Tomajoli ©2025</p>
    """, unsafe_allow_html=True)

    species = st.text_input("Species (e.g., Arabidopsis thaliana)")
    sample_name = st.text_input("Sample name or ID")

    col1, col2 = st.columns(2)
    with col1:
        fvfm = st.number_input("Fv/Fm", min_value=0.0, max_value=1.0, step=0.01)
        chl_tot = st.number_input("Chlorophyll Total (Chl TOT)", min_value=0.0, step=0.1)
        spad = st.number_input("SPAD Value", min_value=0.0, step=0.1)
    with col2:
        car_tot = st.number_input("Carotenoids Total (CAR TOT)", min_value=0.0, step=0.1)
        qp = st.number_input("qp (photochemical quenching)", min_value=0.0, max_value=1.0, step=0.01)
        qn = st.number_input("qN (non-photochemical quenching)", min_value=0.0, max_value=1.0, step=0.01)

    if st.button("🔍 Evaluate Health"):
        result = evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn)
        stress_type, triggers, suggestion = predict_stress_type(fvfm, chl_tot, car_tot, spad, qp, qn)
        show_result_card(result, stress_type, suggestion)

        with st.expander("📋 Stress Rule Triggers"):
            for t in triggers:
                st.markdown(f"- {t}")

        data = {
            "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "User": [username],
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
        st.subheader("🗂️ Your Evaluations")
        if st.button("♻️ Reset Table"):
            os.remove("results.csv")
            st.warning("All recorded evaluations have been deleted.")
        else:
            try:
                saved_df = pd.read_csv("results.csv")
                user_df = saved_df[saved_df['User'] == username]
                st.dataframe(user_df)

                csv = user_df.to_csv(index=False).encode('utf-8')
                st.download_button("💾 Download Your Results (CSV)", csv, "results.csv", "text/csv")
            except pd.errors.ParserError:
                st.error("⚠️ The results file is corrupted. Please reset the table.")
