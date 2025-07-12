import streamlit as st

# Funzione di valutazione
def evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn):
    score = 0

    # Fv/Fm
    if fvfm >= 0.80:
        score += 2
    elif fvfm >= 0.75:
        score += 1
    else:
        score -= 1

    # Chl TOT
    if chl_tot >= 1.5:
        score += 2
    elif chl_tot >= 1.0:
        score += 1
    else:
        score -= 1

    # CAR TOT
    if car_tot >= 0.5:
        score += 2
    elif car_tot >= 0.3:
        score += 1
    else:
        score -= 1

    # SPAD
    if spad >= 40:
        score += 2
    elif spad >= 30:
        score += 1
    else:
        score -= 1

    # qp
    if qp >= 0.7:
        score += 2
    elif qp >= 0.5:
        score += 1
    else:
        score -= 1

    # qN
    if 0.3 <= qn <= 0.7:
        score += 2
    elif 0.2 <= qn < 0.3 or 0.7 < qn <= 0.8:
        score += 1
    else:
        score -= 1

    # Interpretazione
    if score >= 10:
        return "🌿 Healthy – Optimal physiological state"
    elif 6 <= score < 10:
        return "🌱 Moderate stress – Monitor closely"
    else:
        return "⚠️ High stress – Likely physiological damage"

# UI Streamlit
st.set_page_config(page_title="Plant Health Checker", layout="centered")
st.title("🌿 Plant Health Checker")
st.markdown("Enter the physiological parameters of your plant to assess its health status.")

# Input
fvfm = st.number_input("Fv/Fm", min_value=0.0, max_value=1.0, step=0.01)
chl_tot = st.number_input("Chlorophyll Total (Chl TOT)", min_value=0.0, step=0.1)
car_tot = st.number_input("Carotenoids Total (CAR TOT)", min_value=0.0, step=0.1)
spad = st.number_input("SPAD Value", min_value=0.0, step=0.1)
qp = st.number_input("qp (photochemical quenching)", min_value=0.0, max_value=1.0, step=0.01)
qn = st.number_input("qN (non-photochemical quenching)", min_value=0.0, max_value=1.0, step=0.01)

if st.button("🔍 Evaluate Health"):
    result = evaluate_plant_health(fvfm, chl_tot, car_tot, spad, qp, qn)
    st.success(result)
