from pathlib import Path

import streamlit as st

from core.diseases import DISEASES
from core.ui import disclaimer, hero

# ---------------------------------------------------------------- EDIT ME
COURSE = "Systematic Machine Learning"
UNIVERSITY = "Bennett University"  # e.g. "Bennett University"
GITHUB_URL = "https://github.com/kanishak-sharma/disease-management-system"
TEAM = [  # (name, role)  -- add your teammates here
    ("Kanishak Sharma", "Front-end, UI, Team Management, Github Management"),
    ("Shreshtha Sharma", "Model Developer ,Model Trainer, Presentation, Project Lead "),
    ("Rohan Singla", "Data Analyst, Model Evaluator "),
    ("Bhoumik Sharma", "Backend Developer"),
]
# ----------------------------------------------------------------------

hero("About this project", f"A multi-disease prediction and health-guidance website built for the {COURSE} course"
     + (f" at {UNIVERSITY}." if UNIVERSITY else "."), ["Python", "scikit-learn", "Plotly", "Streamlit", "Open source"])

st.subheader("What it does")
st.write("You enter results from a check-up or lab report. A machine-learning model trained on real patient records estimates your risk, "
         "the app compares every value with the normal range and with a typical healthy person, then suggests home care and "
         "the exact values at which you should see a doctor.")

st.subheader("The pipeline")
img = Path(__file__).resolve().parent.parent / "assets" / "pipeline.png"
if img.exists():
    st.image(str(img), caption="Project pipeline: data → cleaning → model → saved file → website", width="stretch")
st.markdown("1. **Data**: public medical datasets (CSV files in the repository).\n"
            "2. **Cleaning**: fill gaps with the median, scale all numbers to the same range.\n"
            "3. **Model**: each disease has its own trained classifier, checked with 5-fold cross-validation.\n"
            "4. **Saved model**: the trained pipeline is stored as a `.joblib` file.\n"
            "5. **Website**: this Streamlit app loads the model and explains every result.")

st.subheader("Diseases and data")
st.dataframe([{"Disease": c["name"], "Model": c["model_name"], "Data": c["data_source"], "Status": c["status"]} for c in DISEASES.values()],
             hide_index=True, width="stretch")

st.subheader("The team")
cols = st.columns(min(4, len(TEAM)))
for i, (name, role) in enumerate(TEAM):
    cols[i % len(cols)].markdown(
        f'<div class="card"><div class="ico">👤</div><h4>{name}</h4><p>{role}</p></div>', unsafe_allow_html=True)

st.subheader("Known limitations")
st.markdown("- Models learn from small public datasets, so they are not as reliable as a doctor or a lab.\n"
            "- The diabetes data covers women of one population only. The Parkinson's data is synthetic. "
            "The kidney data is unusually easy. The liver data is hard to predict from.\n"
            "- The model only sees the numbers you type in. It cannot examine you, and it does not know your history.\n"
            "- Home-care tips are general wellness advice. They never replace treatment.")

st.subheader("Privacy")
st.write("Nothing you type is saved. Values live only in your browser session and disappear when you close the page.")

st.link_button("View the code on GitHub", GITHUB_URL)
st.write("")
disclaimer()
