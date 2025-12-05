import streamlit as st
import pandas as pd
import requests
import io
import base64
from datetime import datetime
from PIL import Image

# =============================
# CONFIGURAZIONE BASE
# =============================
st.set_page_config(page_title="Plant Health Checker", page_icon="🌿", layout="centered")

# =============================
# STILE E TEMA
# =============================
st.markdown("""
<style>
body {font-family: 'Poppins', sans-serif;}
.stApp { background: linear-gradient(to bottom, #001a17, #0a3d35); color: white; }
.hero-container { text-align: center; padding: 90px 20px 50px 20px; }
.hero-container img { width: 500px; margin-bottom: 25px; }
.hero-title { font-size: 60px; color: #76c7a1; font-weight: 700; }
.hero-subtitle { font-size: 22px; color: #b7ffde; }
.section-title { font-size: 28px; text-align: center; color: #b7ffde; margin: 50px 0 25px 0; }
.result-card { background: rgba(255,255,255,0.08); border-radius: 16px; padding: 25px; color: white; }
.stButton button { background: linear-gradient(90deg, #00b894, #2ecc71); color: white; border-radius: 10px; padding: 12px 24px; border: none; }
.stButton button:hover { transform: scale(1.05); }
.footer-container { background: linear-gradient(to right, #002c26, #001d19); color: #d1fff0; text-align: center; padding: 60px 0; margin-top: 100px; }
.contact-icons { display: flex; justify-content: center; gap: 45px; margin-top: 15px; flex-wrap: wrap; }
.contact-item img { width: 32px; height: 32px; margin-bottom: 8px; }
.contact-item a { color: #76c7a1; text-decoration: none; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# =============================
# HEADER
# =============================
with open("logo.png", "rb") as f:
    data = base64.b64encode(f.read()).decode("utf-8")

st.markdown(f"""
<div class='hero-container'>
    <img src='data:image/png;base64,{data}' alt='Logo'/>
    <h1 class='hero-title'>Plant Health Checker</h1>
    <p class='hero-subtitle'>AI-powered physiological & visual plant diagnostics</p>
</div>
""", unsafe_allow_html=True)

# =============================
# AI LEAF ANALYSIS VIA HUGGING FACE API
# =============================
HF_API_URL = "https://router.huggingface.co/liriope/PlantDiseaseDetection"

st.markdown("<div class='section-title'>🌿 AI Leaf Image Analysis</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload a leaf image for AI-based health analysis", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Leaf", use_column_width=True)

    token = st.secrets.get("HF_API_TOKEN")

    if not token:
        st.warning("⚠️ Please set your Hugging Face API token in Streamlit secrets to enable AI analysis.")
    else:
        with st.spinner("Analyzing leaf with AI model..."):
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            response = requests.post(
                HF_API_URL,
                headers={"Authorization": f"Bearer {token}"},
                data=buffered.getvalue(),
                timeout=30
            )

            if response.status_code == 200:
                try:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0 and "label" in result[0]:
                        label = result[0]["label"]
                        score = result[0]["score"] * 100
                        st.success(f"🧠 AI Diagnosis: **{label}** ({score:.1f}% confidence)")
                    else:
                        st.info("AI analysis completed, but no clear result returned.")
                except Exception:
                    st.error("Unexpected response format from Hugging Face API.")
            else:
                st.error(f"Error accessing Hugging Face API: {response.status_code} – {response.text[:200]}")

# =============================
# PHYSIOLOGICAL ANALYSIS
# =============================
if "results" not in st.session_state:
    st.session_state.results = []

file_id = "1ERs5PVDraOtvG20KLxO-g49l8AIyFoZo"
url = f"https://drive.google.com/uc?id={file_id}&export=download"
try_df = pd.read_csv(url)
try_df["AccSpeciesName"] = try_df["AccSpeciesName"].astype(str).str.strip().str.title()
species_list = sorted(try_df["AccSpeciesName"].dropna().unique())

species = st.selectbox("🌱 Select or search for the species", options=species_list, index=None, placeholder="Start typing...")
sample_name = st.text_input("Sample name or ID")

def evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn):
    score = sum([
        2 if fvfm >= 0.8 else 1 if fvfm >= 0.75 else -1,
        2 if chl_tot >= 1.5 else 1 if chl_tot >= 1.0 else -1,
        2 if car_tot >= 0.5 else 1 if car_tot >= 0.3 else -1,
        2 if spad >= 40 else 1 if spad >= 30 else -1,
        2 if qp >= 0.7 else 1 if qp >= 0.5 else -1,
        2 if 0.3 <= qn <= 0.7 else 1 if 0.2 <= qn <= 0.8 else -1
    ])
    if score >= 10: return "🌿 Healthy – Optimal physiological state"
    elif score >= 6: return "🌱 Moderate stress – Monitor closely"
    return "⚠️ High stress – Likely physiological damage"

st.markdown("<div class='section-title'>📊 Physiological Parameters</div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    fvfm = st.number_input("🍃 Fv/Fm", 0.0, 1.0, 0.0, 0.01)
    chl_tot = st.number_input("🌿 Chlorophyll Total (Chl TOT)", 0.0, 10.0, 0.0, 0.1)
    spad = st.number_input("🔴 SPAD Value", 0.0, 100.0, 0.0, 0.1)
with col2:
    car_tot = st.number_input("🍊 Carotenoids Total (CAR TOT)", 0.0, 10.0, 0.0, 0.1)
    qp = st.number_input("💡 qp (photochemical quenching)", 0.0, 1.0, 0.0, 0.01)
    qn = st.number_input("🔥 qN (non-photochemical quenching)", 0.0, 1.0, 0.0, 0.01)

if st.button("🔍 Evaluate Health"):
    result = evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn)
    st.success(result)
    st.session_state.results.append({
        "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "Sample Name": sample_name,
        "Species": species,
        "Fv/Fm": fvfm, "Chl TOT": chl_tot, "CAR TOT": car_tot, "SPAD": spad, "qp": qp, "qN": qn, "Status": result
    })

    matched_species = next((s for s in species_list if s.lower() == species.lower()), None)
    if matched_species:
        subset = try_df[try_df["AccSpeciesName"] == matched_species]
        means = subset.groupby("TraitID")["StdValue"].mean()

        trait_map = {"Chl TOT": 413}
        st.markdown("<br><div class='section-title'>📊 Comparison with TRY Database</div>", unsafe_allow_html=True)
        for label, trait_id in trait_map.items():
            mean_val = means.get(trait_id, None)
            if mean_val is not None and not pd.isna(mean_val):
                user_val = eval(label.lower().replace("/", "").replace(" ", "_"))
                diff = user_val - mean_val
                st.markdown(f"**{label}**: You = {user_val:.2f}, TRY Mean = {mean_val:.2f} → Δ = {diff:.2f}")
            else:
                st.markdown(f"**{label}**: No valid data available in TRY for this trait.")

# =============================
# RECORDS E DOWNLOAD
# =============================
if st.session_state.results:
    st.markdown("<div class='section-title'>📁 Sampled Records</div>", unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df, use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.download_button("⬇️ Download Excel File", data=output.getvalue(), file_name="plant_health_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if st.button("🗑️ Reset All Records"):
        st.session_state.results.clear()
        st.success("All records cleared.")

# =============================
# FOOTER
# =============================
footer = """
<div class='footer-container'>
<h2>📬 Contacts</h2>
<div class='contact-icons'>
<div class='contact-item'><a href='mailto:giuseppemuscari.gm@gmail.com'><img src='https://img.icons8.com/ios-filled/50/76c7a1/new-post.png'/><br>Email</a></div>
<div class='contact-item'><a href='https://www.linkedin.com/in/giuseppemuscaritomajoli'><img src='https://img.icons8.com/ios-filled/50/76c7a1/linkedin.png'/><br>LinkedIn</a></div>
<div class='contact-item'><a href='https://www.instagram.com/giuseppemuscari'><img src='https://img.icons8.com/ios-filled/50/76c7a1/instagram-new.png'/><br>Instagram</a></div>
</div>
<p>©2025 Giuseppe Muscari Tomajoli</p>
</div>
"""

st.markdown(footer, unsafe_allow_html=True)
