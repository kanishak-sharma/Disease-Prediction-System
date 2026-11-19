import pandas as pd
import streamlit as st

from core.diseases import DISEASES
from core.knowledge import GENERAL_TIPS, KNOWLEDGE, LEVEL_LABEL
from core.ui import disclaimer, page_head

page_head("Health guide", "Plain-language facts, home care, and the numbers that mean 'see a doctor' for each condition.")

key = st.segmented_control("Condition", list(DISEASES), format_func=lambda k: f"{DISEASES[k]['emoji']} {DISEASES[k]['name']}",
                           default="diabetes", label_visibility="collapsed") or "diabetes"
cfg, kb = DISEASES[key], KNOWLEDGE[key]

st.subheader(f"{cfg['emoji']} {cfg['name']}")
st.write(kb["about"])

a, b = st.columns(2)
with a:
    st.markdown("**Common risk factors**")
    for x in kb["risk_factors"]:
        st.markdown(f"- {x}")
with b:
    st.markdown("**Warning signs: get care straight away**")
    for x in kb["red_flags"]:
        st.markdown(f"- {x}")

st.markdown("#### Home care and lifestyle")
t = st.tabs(["Low risk", "Moderate risk", "High risk"])
for tab, tier in zip(t, ["low", "moderate", "high"]):
    with tab:
        for x in kb["remedies"][tier]:
            st.markdown(f"- {x}")

st.markdown("#### When to see a doctor: the numbers")
table = []
for feat, op, thr, level, msg in kb["rules"]:
    f = next(x for x in cfg["features"] if x["name"] == feat)
    if f["kind"] == "cat":
        cond = f"{f['label']}: {f['options'].get(int(thr), thr) if op == '==' else 'Yes' if f['options'] == {0: 'No', 1: 'Yes'} else f'{op} {thr:g}'}"
    else:
        cond = f"{f['label']} {op} {thr:g}" + (f" {f['unit']}" if f["unit"] else "")
    table.append({"If": cond, "Action": LEVEL_LABEL[level], "Why": msg})
st.dataframe(pd.DataFrame(table), hide_index=True, width="stretch")

normals = [(f["label"], f"{f['normal'][0]:g} - {f['normal'][1]:g} {f['unit']}".strip()) for f in cfg["features"] if f.get("normal")]
if normals:
    st.markdown("#### Normal reference ranges")
    st.dataframe(pd.DataFrame(normals, columns=["Test", "Normal range"]), hide_index=True, width="stretch")

st.markdown("#### Tests to ask your doctor about")
st.markdown(", ".join(kb["tests"]) + ".")

st.divider()
st.subheader("Everyday habits")
cols = st.columns(3)
for i, (t_, d) in enumerate(GENERAL_TIPS):
    cols[i % 3].markdown(f'<div class="tip"><b>{t_}</b><span>{d}</span></div>', unsafe_allow_html=True)
    if i % 3 == 2:
        st.write("")
st.write("")
disclaimer()
