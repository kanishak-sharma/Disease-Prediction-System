import streamlit as st

from core.diseases import DISEASES
from core.knowledge import GENERAL_TIPS
from core.training import load_bundle
from core.ui import disclaimer, disease_card, hero, stat


@st.cache_resource(show_spinner=False)
def bundle(key):
    return load_bundle(key)


bundles = {k: bundle(k) for k in DISEASES}
records = sum(b["rows"] for b in bundles.values())

hero("Check your health risk <br>in under a minute",
     "Six machine-learning models read your test results, compare them with a healthy person, "
     "and tell you what to do next: home care, and the exact values at which to see a doctor.",
     ["6 diseases", "Compare with normal", "Home-care tips", "When to see a doctor", "Free & private"])

c = st.columns(4)
for col, (v, l) in zip(c, [(str(len(DISEASES)), "diseases covered"), (f"{records:,}", "patient records learned from"),
                           (f"{sum(b['metrics']['accuracy'] for b in bundles.values()) / len(bundles) * 100:.0f}%", "average model accuracy"),
                           ("0", "personal data stored")]):
    col.markdown(stat(v, l), unsafe_allow_html=True)

st.write("")
st.subheader("Choose a check")
cols = st.columns(3)
for i, (key, cfg) in enumerate(DISEASES.items()):
    with cols[i % 3]:
        st.markdown(disease_card(cfg), unsafe_allow_html=True)
        if st.button(f"Check {cfg['name'].lower()}", key=f"go_{key}", width="stretch"):
            st.session_state["disease"] = key
            st.switch_page("views/check.py")
        st.write("")

st.subheader("How it works")
steps = [("Enter your numbers", "Type values from a recent lab report or check-up. Use the sample buttons to explore."),
         ("Get your risk", "A trained model gives a risk percentage and shows which inputs pushed it up or down."),
         ("Compare with normal", "See every value next to the normal range and a typical healthy person."),
         ("Know what to do", "Home-care tips and clear values at which to book a doctor.")]
cols = st.columns(4)
for i, (col, (t, d)) in enumerate(zip(cols, steps), start=1):
    col.markdown(f'<div class="step"><div class="n">{i}</div><div><b>{t}</b><br><span style="color:#5b6b69;font-size:.9rem">{d}</span></div></div>',
                 unsafe_allow_html=True)

st.write("")
st.subheader("Six habits that protect almost everything")
cols = st.columns(3)
for i, (t, d) in enumerate(GENERAL_TIPS):
    cols[i % 3].markdown(f'<div class="tip"><b>{t}</b><span>{d}</span></div>', unsafe_allow_html=True)
    if i % 3 == 2:
        st.write("")

st.write("")
disclaimer()
