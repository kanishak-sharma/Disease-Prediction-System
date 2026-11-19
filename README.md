# Multi-Disease Prediction & Health Guide

A Streamlit website that predicts risk for **6 diseases** (diabetes, heart disease, Parkinson's, breast cancer,
chronic kidney disease, liver disease), compares your values with normal ranges and a typical healthy person,
and suggests home care plus the values at which to see a doctor.

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```

## Folders
| Path | What it is |
|---|---|
| `app.py` | Entry point + top navigation |
| `views/` | Pages: home, check, insights, library (health guide), about |
| `core/diseases.py` | **Add or edit a disease here** (CSV, inputs, model) |
| `core/knowledge.py` | Home remedies, doctor thresholds, red flags |
| `core/charts.py`, `core/ui.py` | Charts and styling |
| `train.py` | `python train.py` retrains all models into `models/` |
| `csv/`, `models/` | Datasets and saved models |


