import streamlit as st
import pandas as pd
import os
import yaml
import streamlit_authenticator as stauth
from datetime import datetime
from yaml.loader import SafeLoader

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

# ---------- Autenticazione ----------
users_file = "users.yaml"

# Se il file utenti non esiste, crealo
if not os.path.exists(users_file):
    with open(users_file, 'w') as f:
        yaml.dump({'credentials': {'usernames': {}}}, f)

with open(users_file, 'r') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'], 'plant_health_app', 'abcdef', cookie_expiry_days=1
)

# ---------- Registrazione Utente ----------
st.sidebar.header("🔐 User Access")
registration = st.sidebar.checkbox("Register New User")

if registration:
    st.sidebar.subheader("Create New Account")
    new_name = st.sidebar.text_input("Full Name")
    new_username = st.sidebar.text_input("Username")
    new_password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Register"):
        if new_username in config['credentials']['usernames']:
            st.sidebar.warning("Username already exists.")
        else:
            hashed_pw = stauth.Hasher([new_password]).generate()[0]
            config['credentials']['usernames'][new_username] = {
                'name': new_name,
                'password': hashed_pw
            }
            with open(users_file, 'w') as file:
                yaml.dump(config, file)
            st.sidebar.success("User registered! You can now log in.")
            st.experimental_rerun()

# ---------- Login ----------
name, authentication_status, username = authenticator.login("Login")

if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Logged in as {name}")

    # ---------- HEADER ----------
    st.markdown("""
        <h1 style='text-align: center;'>🌿 Plant Health Checker</h1>
        <p style='text-align: center;'>Enter the physiological parameters of your plant to assess its health status.</p>
        <p style='text-align: right; color: lightgray; font-size: 14px;'>Developed by Giuseppe Muscari Tomajoli ©2025</p>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ---------- FUNZIONI DI VALUTAZIONE ----------
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
            suggestion = "Fertilize with nitrogen-rich nutrients."
            return "Nutrient Deficiency", triggers, suggestion
        elif fvfm < 0.75 and qp < 0.5 and qn > 0.7:
            triggers.append("Low Fv/Fm and qp with high qN suggest Excess Light Stress")
            suggestion = "Reduce light intensity or duration."
            return "Excess Light Stress", triggers, suggestion
        elif fvfm < 0.75 and car_tot < 0.3 and spad < 30:
            triggers.append("Low Fv/Fm, CAR TOT and SPAD suggest Drought Stress")
            suggestion = "Increase irrigation and maintain moisture."
            return "Drought Stress", triggers, suggestion
        elif fvfm < 0.7 and chl_tot < 1.0 and car_tot < 0.3:
            triggers.append("Low Fv/Fm, Chl TOT and CAR TOT suggest Cold Stress")
            suggestion = "Protect plant from cold temperatures."
            return "Cold Stress", triggers, suggestion
        else:
            triggers.append("No rules triggered based on input thresholds")
            suggestion = "Continue monitoring."
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
            <p><b>🔎 Stress Type:</b> {stress_type}</p>
            <p><b>💡 Suggestion:</b> {suggestion}</p>
        </div>
        ''', unsafe_allow_html=True)

    # ---------- INPUT DATI ----------
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
        st.success("Data saved to results.csv")

    # ---------- STORICO ----------
    if os.path.exists("results.csv"):
        st.subheader("🗂️ Your Recorded Evaluations")

        if st.button("♻️ Reset Table"):
            os.remove("results.csv")
            st.warning("All recorded evaluations have been deleted.")
        else:
            try:
                saved_df = pd.read_csv("results.csv")
                user_df = saved_df[saved_df['User'] == username]
                st.dataframe(user_df)

                csv = user_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Download Your Results (CSV)",
                    data=csv,
                    file_name=f'{username}_results.csv',
                    mime='text/csv',
                )
            except pd.errors.ParserError:
                st.error("⚠️ The results file is corrupted. Please reset the table.")

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
