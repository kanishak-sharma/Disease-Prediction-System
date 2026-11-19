import pandas as pd
import streamlit as st

from core import charts
from core.diseases import DISEASES
from core.training import load_bundle
from core.ui import disclaimer, page_head


@st.cache_resource(show_spinner=False)
def bundle(key):
    return load_bundle(key)


page_head("Model insights", "How well each model works, what it pays attention to, and how patients differ from healthy people.")

bundles = {k: bundle(k) for k in DISEASES}
rows = [dict(key=k, name=DISEASES[k]["name"], **b["metrics"]) for k, b in bundles.items()]

st.subheader("All models side by side")
st.plotly_chart(charts.compare_models(rows), width="stretch", config={"displayModeBar": False})
table = pd.DataFrame([{
    "Disease": r["name"], "Model": DISEASES[r["key"]]["model_name"], "Records": r["n"],
    "Accuracy": f"{r['accuracy'] * 100:.1f}%", "Recall": f"{r['recall'] * 100:.1f}%",
    "Precision": f"{r['precision'] * 100:.1f}%", "AUC": f"{r['auc']:.3f}"} for r in rows])
st.dataframe(table, hide_index=True, width="stretch")
st.caption("All numbers come from 5-fold cross-validation, where every record is predicted by a model that never saw it. "
           "Recall = share of real patients the model catches. AUC = how well it ranks patients above healthy people (0.5 = coin flip, 1.0 = perfect).")

st.divider()
st.subheader("Look inside one model")
key = st.segmented_control("Disease", list(DISEASES), format_func=lambda k: f"{DISEASES[k]['emoji']} {DISEASES[k]['name']}",
                           default="diabetes", label_visibility="collapsed") or "diabetes"
cfg, b = DISEASES[key], bundles[key]
m = b["metrics"]

c = st.columns(4)
c[0].metric("Accuracy", f"{m['accuracy'] * 100:.1f}%")
c[1].metric("Recall", f"{m['recall'] * 100:.1f}%", help="Share of real patients caught")
c[2].metric("Precision", f"{m['precision'] * 100:.1f}%", help="Share of alarms that were real")
c[3].metric("AUC", f"{m['auc']:.3f}")
st.info(f"**Data:** {cfg['data_source']}. **Model:** {cfg['model_name']}. {cfg['caveat']}", icon="📚")

t1, t2 = st.columns(2)
with t1:
    st.markdown("**ROC curve**")
    st.plotly_chart(charts.roc_curve_fig(m), width="stretch", config={"displayModeBar": False})
with t2:
    st.markdown("**Confusion matrix**")
    st.plotly_chart(charts.confusion_fig(m), width="stretch", config={"displayModeBar": False})

st.markdown("**Which inputs matter most**")
st.plotly_chart(charts.importance_bar(b, cfg), width="stretch", config={"displayModeBar": False})

st.markdown("**Healthy vs. disease distributions**")
f = st.selectbox("Input", cfg["features"], format_func=lambda x: x["label"])
st.plotly_chart(charts.distribution(b, f), width="stretch", config={"displayModeBar": False})
s = b["stats"][f["name"]]
st.caption(f"Typical healthy value: **{s['healthy_median']:g}** · typical patient value: **{s['disease_median']:g}** (medians in the training data).")

st.write("")
disclaimer()
