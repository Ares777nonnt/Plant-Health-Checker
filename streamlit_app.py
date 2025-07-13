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
    .auth-box {
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        background-color: transparent;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Autenticazione ----------
users_file = "users.yaml"

if not os.path.exists(users_file):
    with open(users_file, 'w') as f:
        yaml.dump({'credentials': {'usernames': {}}}, f)

with open(users_file, 'r') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'], 'plant_health_app', 'abcdef', cookie_expiry_days=1
)

# ---------- Sidebar: Accesso utente ----------
st.sidebar.header("🔐 User Access")
registration = st.sidebar.checkbox("Register New User")

with st.sidebar.container():
    with st.container():
        if registration:
            st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
            st.subheader("🆕 Create New Account")
            new_name = st.text_input("👤 Full Name")
            new_username = st.text_input("🆔 Username")
            new_password = st.text_input("🔑 Password", type="password")

            if st.button("✅ Register"):
                if new_username in config['credentials']['usernames']:
                    st.warning("⚠️ Username already exists.")
                else:
                    hashed_pw = stauth.Hasher([new_password]).generate()[0]
                    config['credentials']['usernames'][new_username] = {
                        'name': new_name,
                        'password': hashed_pw
                    }
                    with open(users_file, 'w') as file:
                        yaml.dump(config, file)
                    st.success("✅ User registered! You can now log in.")
                    st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)

name, authentication_status, username = authenticator.login("🔑 Login", location="sidebar")

if authentication_status:
    authenticator.logout('🚪 Logout', 'sidebar')
    st.sidebar.success(f"🔓 Logged in as {name}")

    # ---------- HEADER ----------
    st.markdown("""
        <h1 style='text-align: center;'>🌿 Plant Health Checker</h1>
        <p style='text-align: center;'>Enter the physiological parameters of your plant to assess its health status.</p>
        <p style='text-align: right; color: lightgray; font-size: 14px;'>Developed by Giuseppe Muscari Tomajoli ©2025</p>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # [Resto del codice invariato per elaborazione dati e salvataggio...]

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
