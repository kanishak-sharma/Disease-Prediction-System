"""Disease catalogue: which CSV, which columns, what each input means.

To add a new disease, add one entry to DISEASES (and a matching entry in
core/knowledge.py), then run `python train.py`.
Everything else in the app (forms, charts, pages) is generated from this file.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = ROOT / "csv"
MODEL_DIR = ROOT / "models"

YES_NO = {0: "No", 1: "Yes"}


def num(name, label, unit="", normal=None, step=1.0, help="", lo=None, hi=None, decimals=0):
    """A numeric input. `normal` = clinical reference range (low, high) if one exists."""
    return dict(name=name, label=label, kind="num", unit=unit, normal=normal, step=step,
                help=help, lo=lo, hi=hi, decimals=decimals)


def cat(name, label, options, help="", normal_value=None):
    """A choice input. `options` maps the numeric code used by the model -> text shown."""
    return dict(name=name, label=label, kind="cat", options=options, help=help,
                normal_value=normal_value, unit="", normal=None)


def _svc():
    # Linear SVM + probability calibration (the modern replacement for SVC(probability=True))
    return CalibratedClassifierCV(SVC(kernel="linear", class_weight="balanced", random_state=42),
                                  method="sigmoid", cv=5, ensemble=False)


def _lr(balanced=False, C=1.0):
    return LogisticRegression(C=C, max_iter=5000, class_weight="balanced" if balanced else None)


# ---------------------------------------------------------------- data loaders
def _load_diabetes():
    df = pd.read_csv(CSV_DIR / "diabetes.csv")
    # In this dataset a 0 in these columns means "not measured", not a real zero.
    for c in ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]:
        df[c] = df[c].replace(0, np.nan)
    return df, df["Outcome"]


def _load_heart():
    df = pd.read_csv(CSV_DIR / "heart_disease_data.csv")
    # In this CSV target == 1 means HEALTHY (the opposite of what many tutorials say).
    return df, (df["target"] == 0).astype(int)


def _load_parkinsons():
    df = pd.read_csv(CSV_DIR / "parkinsons_disease_data.csv")
    return df, df["Diagnosis"]


def _load_breast():
    df = pd.read_csv(CSV_DIR / "breast_cancer.csv")
    return df, df["malignant"]


def _load_kidney():
    df = pd.read_csv(CSV_DIR / "kidney_disease.csv")
    df = df.map(lambda v: v.strip() if isinstance(v, str) else v).replace({"?": np.nan, "": np.nan})
    for c in ["age", "bp", "sg", "al", "su", "bgr", "bu", "sc", "sod", "pot", "hemo", "pcv", "wbcc", "rbcc"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    yes = {"yes": 1, "no": 0}
    for c in ["htn", "dm", "cad", "pe", "ane"]:
        df[c] = df[c].map(yes)
    df["appet"] = df["appet"].map({"poor": 1, "good": 0})
    y = (df["class"].astype(str).str.strip().str.lower() == "ckd").astype(int)
    return df, y


def _load_liver():
    df = pd.read_csv(CSV_DIR / "indian_liver_patient.csv")
    df["Gender"] = (df["Gender"] == "Male").astype(int)
    return df, (df["Dataset"] == 1).astype(int)  # 1 = liver patient in the original file


# --------------------------------------------------------------------- catalogue
DISEASES: dict[str, dict] = {
    "diabetes": dict(
        name="Diabetes", icon=":material/glucose:", emoji="🩸", color="#e4572e",
        tagline="Blood-sugar and metabolic risk from routine check-up numbers.",
        organ="Metabolic", loader=_load_diabetes, model=_svc,
        model_name="Linear SVM (class-balanced)", status="Team model",
        data_source="Pima Indians Diabetes Database (768 women, age 21+)",
        caveat="Trained on women of Pima Indian heritage only, so it may be less accurate for other groups and for men.",
        features=[
            num("Pregnancies", "Pregnancies", "count", step=1, help="Number of times pregnant (0 if none / not applicable)."),
            num("Glucose", "Plasma glucose (2 h after glucose drink)", "mg/dL", (70, 139), step=1,
                help="Oral glucose tolerance test, 2-hour value. Under 140 is normal, 140-199 prediabetes, 200+ diabetes range."),
            num("BloodPressure", "Diastolic blood pressure", "mmHg", (60, 80), step=1, help="The lower number of a BP reading."),
            num("SkinThickness", "Triceps skin-fold thickness", "mm", (10, 30), step=1, help="Measured by a nurse with calipers. A rough body-fat indicator."),
            num("Insulin", "Serum insulin (2 h)", "µU/mL", (16, 166), step=1, help="2-hour serum insulin from a glucose tolerance test."),
            num("BMI", "Body-mass index", "kg/m²", (18.5, 24.9), step=0.1, decimals=1, help="Weight (kg) divided by height (m) squared."),
            num("DiabetesPedigreeFunction", "Family-history score", "", step=0.01, decimals=2,
                help="A score of how strongly diabetes runs in the family. Higher = stronger family history."),
            num("Age", "Age", "years", step=1),
        ],
    ),
    "heart": dict(
        name="Heart disease", icon=":material/cardiology:", emoji="❤️", color="#c8102e",
        tagline="Cardiac risk from blood pressure, cholesterol, ECG and stress-test results.",
        organ="Cardiovascular", loader=_load_heart, model=_svc,
        model_name="Linear SVM", status="Team model",
        data_source="Cleveland Heart Disease data (303 patients)",
        caveat="Only 303 patients, so results are less stable than for larger datasets.",
        features=[
            num("age", "Age", "years", step=1),
            cat("sex", "Sex", {0: "Female", 1: "Male"}),
            cat("cp", "Chest-pain type", {0: "No symptoms (asymptomatic)", 1: "Atypical angina", 2: "Non-anginal pain", 3: "Typical angina"},
                help="Type of chest pain reported. 'No symptoms' is the most common in confirmed heart disease in this dataset.", normal_value=2),
            num("trestbps", "Resting blood pressure (systolic)", "mmHg", (90, 119), step=1, help="The upper number of a BP reading, at rest."),
            num("chol", "Serum cholesterol", "mg/dL", (125, 199), step=1, help="Total cholesterol. Under 200 is desirable."),
            cat("fbs", "Fasting blood sugar above 120 mg/dL?", YES_NO, normal_value=0),
            cat("restecg", "Resting ECG result", {0: "Normal", 1: "ST-T wave abnormality", 2: "Left-ventricular hypertrophy"}, normal_value=0),
            num("thalach", "Maximum heart rate reached", "bpm", step=1, help="Highest heart rate during the exercise stress test. Higher is generally better."),
            cat("exang", "Chest pain during exercise?", YES_NO, normal_value=0),
            num("oldpeak", "ST depression after exercise", "mm", (0, 1), step=0.1, decimals=1, help="ECG change during exercise compared with rest."),
            cat("slope", "Slope of the ST segment at peak exercise", {0: "Downsloping", 1: "Flat", 2: "Upsloping"}, normal_value=2),
            cat("ca", "Major vessels with blockage (fluoroscopy)", {0: "0", 1: "1", 2: "2", 3: "3", 4: "4"}, normal_value=0),
            cat("thal", "Thallium stress-test result", {1: "Fixed defect", 2: "Normal", 3: "Reversible defect"}, normal_value=2),
        ],
    ),
    "parkinsons": dict(
        name="Parkinson's disease", icon=":material/neurology:", emoji="🧠", color="#6c4ab6",
        tagline="Neurological screening from movement, cognition and lifestyle scores.",
        organ="Neurological", loader=_load_parkinsons, model=lambda: _lr(C=0.5),
        model_name="Logistic regression", status="Team model",
        data_source="Parkinson's disease dataset (2,105 patients, Kaggle)",
        caveat="This Kaggle dataset is synthetic (computer-generated), so it demonstrates the method but is not a clinical-grade screen.",
        features=[
            num("Age", "Age", "years", step=1),
            num("BMI", "Body-mass index", "kg/m²", (18.5, 24.9), step=0.1, decimals=1),
            num("SleepQuality", "Sleep quality (0 poor - 10 excellent)", "score", step=0.1, decimals=1),
            num("UPDRS", "UPDRS motor score", "points", (0, 40), step=1, help="Unified Parkinson's Disease Rating Scale (0-199). Higher = more severe."),
            num("MoCA", "MoCA cognitive score", "points", (26, 30), step=1, help="Montreal Cognitive Assessment, 0-30. 26 or more is normal."),
            num("FunctionalAssessment", "Functional assessment (0 poor - 10 good)", "score", (8, 10), step=0.1, decimals=1, help="How well the person manages daily tasks."),
            cat("Tremor", "Tremor (shaking at rest)", YES_NO, normal_value=0),
            cat("Rigidity", "Muscle rigidity / stiffness", YES_NO, normal_value=0),
            cat("Bradykinesia", "Slowness of movement", YES_NO, normal_value=0),
            cat("PosturalInstability", "Balance problems / unsteadiness", YES_NO, normal_value=0),
            cat("SpeechProblems", "Speech problems (soft or slurred voice)", YES_NO, normal_value=0),
            cat("SleepDisorders", "Sleep disorders", YES_NO, normal_value=0),
            cat("Constipation", "Constipation", YES_NO, normal_value=0),
            cat("FamilyHistoryParkinsons", "Family history of Parkinson's", YES_NO, normal_value=0),
            cat("TraumaticBrainInjury", "Past serious head injury", YES_NO, normal_value=0),
            cat("Depression", "Depression", YES_NO, normal_value=0),
        ],
    ),
    "breast": dict(
        name="Breast cancer", icon=":material/female:", emoji="🎗️", color="#d6336c",
        tagline="Benign-vs-malignant check from cell measurements of a breast-lump biopsy.",
        organ="Oncology", loader=_load_breast, model=lambda: _lr(C=1.0),
        model_name="Logistic regression", status="New",
        data_source="Wisconsin Diagnostic Breast Cancer (569 biopsies, UCI via scikit-learn)",
        caveat="Inputs come from a lab report of a fine-needle biopsy, not from self-examination. A clinician must always confirm.",
        features=[
            num("mean_radius", "Average cell radius", "", step=0.1, decimals=1, help="Mean of distances from the centre to the edge of the cell nuclei."),
            num("mean_texture", "Average texture variation", "", step=0.1, decimals=1, help="Standard deviation of gray-scale values in the image."),
            num("mean_smoothness", "Average smoothness", "", step=0.001, decimals=3, help="Local variation in radius lengths."),
            num("mean_compactness", "Average compactness", "", step=0.001, decimals=3),
            num("mean_concavity", "Average concavity", "", step=0.001, decimals=3, help="Severity of concave portions of the cell outline."),
            num("mean_concave_points", "Average number of concave points", "", step=0.001, decimals=3),
            num("worst_radius", "Largest cell radius", "", step=0.1, decimals=1, help="Mean of the three largest values in the sample."),
            num("worst_texture", "Worst texture variation", "", step=0.1, decimals=1),
            num("worst_smoothness", "Worst smoothness", "", step=0.001, decimals=3),
            num("worst_concave_points", "Worst concave points", "", step=0.001, decimals=3),
        ],
    ),
    "kidney": dict(
        name="Chronic kidney disease", icon=":material/nephrology:", emoji="🫘", color="#1c7ed6",
        tagline="Kidney health from blood and urine test results.",
        organ="Renal", loader=_load_kidney, model=lambda: _lr(C=1.0),
        model_name="Logistic regression", status="New",
        data_source="Chronic Kidney Disease dataset (400 patients, UCI)",
        caveat="The two groups in this dataset are very easy to tell apart, so the accuracy shown is optimistic compared with real clinics.",
        features=[
            num("age", "Age", "years", step=1),
            num("bp", "Diastolic blood pressure", "mmHg", (60, 80), step=1),
            num("sg", "Urine specific gravity", "", (1.005, 1.030), step=0.005, decimals=3, help="How concentrated the urine is."),
            cat("al", "Urine albumin (protein)", {0: "0 (none)", 1: "1 (trace)", 2: "2", 3: "3", 4: "4", 5: "5 (high)"}, normal_value=0,
                help="Dipstick scale 0-5. Protein in the urine is an early sign of kidney damage."),
            cat("su", "Urine sugar", {0: "0 (none)", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5 (high)"}, normal_value=0),
            num("bgr", "Random blood glucose", "mg/dL", (70, 140), step=1),
            num("bu", "Blood urea", "mg/dL", (7, 20), step=1, help="Waste product normally filtered by the kidneys."),
            num("sc", "Serum creatinine", "mg/dL", (0.6, 1.3), step=0.1, decimals=1, help="Key kidney-function marker. High = kidneys filtering poorly."),
            num("sod", "Sodium", "mEq/L", (135, 145), step=1),
            num("pot", "Potassium", "mEq/L", (3.5, 5.1), step=0.1, decimals=1),
            num("hemo", "Haemoglobin", "g/dL", (12, 17.5), step=0.1, decimals=1, help="Low haemoglobin (anaemia) is common in kidney disease."),
            num("pcv", "Packed cell volume", "%", (36, 50), step=1),
            num("wbcc", "White-blood-cell count", "cells/µL", (4000, 11000), step=100),
            num("rbcc", "Red-blood-cell count", "million/µL", (4.2, 6.1), step=0.1, decimals=1),
            cat("htn", "High blood pressure (hypertension)", YES_NO, normal_value=0),
            cat("dm", "Diabetes", YES_NO, normal_value=0),
            cat("cad", "Coronary artery disease", YES_NO, normal_value=0),
            cat("appet", "Poor appetite", YES_NO, normal_value=0),
            cat("pe", "Swollen feet / ankles (pedal oedema)", YES_NO, normal_value=0),
            cat("ane", "Anaemia", YES_NO, normal_value=0),
        ],
    ),
    "liver": dict(
        name="Liver disease", icon=":material/gastroenterology:", emoji="🫀", color="#e8a317",
        tagline="Liver health from a standard liver-function blood panel.",
        organ="Hepatic", loader=_load_liver, model=lambda: _lr(balanced=True),
        model_name="Logistic regression (class-balanced)", status="Experimental",
        data_source="Indian Liver Patient Records (583 patients, UCI)",
        caveat="Experimental: this dataset is hard to learn from (about 72% of patients in it have liver disease), so treat results as a rough hint only.",
        features=[
            num("Age", "Age", "years", step=1),
            cat("Gender", "Sex", {0: "Female", 1: "Male"}),
            num("Total_Bilirubin", "Total bilirubin", "mg/dL", (0.1, 1.2), step=0.1, decimals=1, help="Yellow pigment from red-cell breakdown. High levels cause jaundice."),
            num("Direct_Bilirubin", "Direct bilirubin", "mg/dL", (0.0, 0.3), step=0.1, decimals=1),
            num("Alkaline_Phosphotase", "Alkaline phosphatase (ALP)", "IU/L", (44, 147), step=1),
            num("Alamine_Aminotransferase", "ALT (SGPT)", "IU/L", (7, 56), step=1, help="Liver enzyme that leaks into the blood when liver cells are damaged."),
            num("Aspartate_Aminotransferase", "AST (SGOT)", "IU/L", (10, 40), step=1),
            num("Total_Protiens", "Total protein", "g/dL", (6.0, 8.3), step=0.1, decimals=1),
            num("Albumin", "Albumin", "g/dL", (3.5, 5.0), step=0.1, decimals=1, help="Main protein made by the liver. Low = liver making less."),
            num("Albumin_and_Globulin_Ratio", "Albumin / globulin ratio", "", (1.1, 2.5), step=0.1, decimals=1),
        ],
    ),
}


def make_pipeline(key: str) -> Pipeline:
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("model", DISEASES[key]["model"]()),
    ])


def feature_names(key: str) -> list[str]:
    return [f["name"] for f in DISEASES[key]["features"]]
