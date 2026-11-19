"""Train the three additional screening models and generate app metadata.

Run from the project root:
    python train_extra_models.py

Datasets (clean copies live in csv/):
  * Chronic Kidney Disease  — UCI ML Repository, dataset 336
  * Indian Liver Patient    — UCI ML Repository, dataset 225
  * Thyroid Disease         — UCI ML Repository, dataset 102

The three original models in models/*.joblib are never overwritten.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from warnings import filterwarnings

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, f1_score, precision_score,
    recall_score, roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "csv"
MODELS = ROOT / "models"

ORIGINAL = {
    "diabetes": ("diabetes.csv", "Outcome"),
    "heart": ("heart_disease_data.csv", "target"),
    "parkinsons": ("parkinsons_disease_data.csv", "Diagnosis"),
}

EXTRA = {
    "ckd": {
        "file": "ckd.csv",
        "target": "CKD",
        "label": "Chronic Kidney Disease",
        "features": [
            "Age", "BloodPressure", "SpecificGravity", "Albumin", "Sugar",
            "RedBloodCells", "PusCells", "PusCellClumps", "Bacteria",
            "BloodGlucoseRandom", "BloodUrea", "SerumCreatinine", "Sodium",
            "Potassium", "Hemoglobin", "PackedCellVolume", "WhiteBloodCells",
            "RedBloodCellsCount", "Hypertension", "Diabetes",
            "CoronaryArteryDisease", "Appetite", "PedalEdema", "Anemia",
        ],
        "note": (
            "Trained on 24 routine blood and urine measurements from the UCI "
            "CKD dataset. It estimates the likelihood of chronic kidney disease "
            "and is not a substitute for eGFR or a nephrology assessment."
        ),
        "source": "UCI ML Repository — Chronic Kidney Disease (ID 336)",
    },
    "liver": {
        "file": "liver.csv",
        "target": "LiverDisease",
        "label": "Liver Disorder",
        "features": [
            "Age", "Gender", "TotalBilirubin", "DirectBilirubin",
            "AlkalinePhosphatase", "ALT", "AST", "TotalProteins", "Albumin",
            "AlbuminGlobulinRatio",
        ],
        "note": (
            "Trained on the Indian Liver Patient Dataset (ILPD) using standard "
            "liver-function blood tests. 'Liver disorder' is a broad label, not "
            "a specific diagnosis."
        ),
        "source": "UCI ML Repository — Indian Liver Patient Dataset (ID 225)",
    },
    "thyroid": {
        "file": "thyroid.csv",
        "target": "Hypothyroid",
        "label": "Hypothyroidism",
        "features": ["Age", "Sex", "TSH", "T3", "TT4", "T4U", "FTI", "Goitre",
                     "Tumor", "ThyroidSurgery"],
        "note": (
            "Trained on the UCI Thyroid Disease dataset using thyroid function "
            "tests and a short history. Thyroid results are strongly affected by "
            "medication and illness, so interpretation always needs a clinician."
        ),
        "source": "UCI ML Repository — Thyroid Disease (ID 102)",
    },
}


def clean_number(value: float):
    if pd.isna(value):
        return 0
    if float(value).is_integer():
        return int(value)
    return round(float(value), 4)


def build_pipeline() -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=5000, class_weight="balanced", random_state=42
        )),
    ])


def cross_val_metrics(bundle: dict, X: pd.DataFrame, y: pd.Series) -> dict:
    pipe = bundle["pipeline"]
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    pred = cross_val_predict(pipe, X, y, cv=cv, method="predict")
    try:
        proba = cross_val_predict(pipe, X, y, cv=cv, method="predict_proba")[:, 1]
        auc = float(roc_auc_score(y, proba))
    except Exception:
        auc = None
    return {
        "accuracy": round(float(accuracy_score(y, pred)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(y, pred)), 4),
        "precision": round(float(precision_score(y, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y, pred, zero_division=0)), 4),
        "roc_auc": None if auc is None else round(auc, 4),
        "samples": int(len(y)),
        "positives": int(y.sum()),
        "cv_folds": 5,
        "model": type(pipe.named_steps["model"]).__name__,
    }


def main() -> None:
    MODELS.mkdir(exist_ok=True)
    all_bundles = {}
    metrics = {}

    # ------------------------------------------------------------------
    # 1. Train the three extra models from real public datasets
    # ------------------------------------------------------------------
    for key, spec in EXTRA.items():
        df = pd.read_csv(CSV / spec["file"])
        X = df[spec["features"]].astype(float)
        y = df[spec["target"]].astype(int)
        pipe = build_pipeline()
        pipe.fit(X, y)
        defaults = {}
        for feature in spec["features"]:
            defaults[feature] = clean_number(X[feature].median())
        bundle = {
            "pipeline": pipe,
            "features": spec["features"],
            "defaults": defaults,
            "label": spec["label"],
            "note": spec["note"],
            "source": spec["source"],
            "derived": False,
        }
        joblib.dump(bundle, MODELS / f"{key}.joblib")
        all_bundles[key] = (bundle, df, X, y)
        print(f"[trained] {key:12s} n={len(X):4d} positives={int(y.sum()):4d}")

    # ------------------------------------------------------------------
    # 2. Metrics for every model (including the original three)
    # ------------------------------------------------------------------
    for key, (filename, target) in ORIGINAL.items():
        df = pd.read_csv(CSV / filename)
        bundle = joblib.load(MODELS / f"{key}.joblib")
        X = df[bundle["features"]]
        y = df[target]
        metrics[key] = cross_val_metrics(bundle, X, y)
        all_bundles[key] = (bundle, df, X, y)
        print(f"[metrics] {key:12s} acc={metrics[key]['accuracy']:.3f} "
              f"auc={metrics[key]['roc_auc']}")

    for key, (bundle, _df, X, y) in list(all_bundles.items()):
        if key in EXTRA:
            metrics[key] = cross_val_metrics(bundle, X, y)
            print(f"[metrics] {key:12s} acc={metrics[key]['accuracy']:.3f} "
                  f"auc={metrics[key]['roc_auc']}")

    metrics["_meta"] = {
        "generated": date.today().isoformat(),
        "evaluation": "5-fold stratified cross-validation",
        "note": "Metrics describe the saved models on their source datasets, not clinical performance.",
    }
    (MODELS / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    # ------------------------------------------------------------------
    # 3. Feature ranges for input widgets and comparison charts
    # ------------------------------------------------------------------
    ranges = {}
    for key, (bundle, _df, X, _y) in all_bundles.items():
        ranges[key] = {}
        for feature in bundle["features"]:
            col = pd.to_numeric(X[feature], errors="coerce")
            ranges[key][feature] = {
                "min": clean_number(col.min()),
                "max": clean_number(col.max()),
                "median": clean_number(col.median()),
                "p10": clean_number(col.quantile(0.10)),
                "p90": clean_number(col.quantile(0.90)),
            }
    (MODELS / "feature_ranges.json").write_text(
        json.dumps(ranges, indent=2), encoding="utf-8"
    )

    # ------------------------------------------------------------------
    # 4. Realistic example patients (one lower-risk, one higher-risk)
    # ------------------------------------------------------------------
    examples = {}
    for key, (bundle, _df, X, y) in all_bundles.items():
        X_filled = X.copy().astype(float)
        for feature in bundle["features"]:
            X_filled[feature] = pd.to_numeric(X_filled[feature], errors="coerce")
            X_filled[feature] = X_filled[feature].fillna(X_filled[feature].median())
        # The PIMA dataset encodes missing measurements as 0.
        if key == "diabetes":
            for feature in ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]:
                med = X_filled[feature].median()
                X_filled.loc[X_filled[feature] <= 0, feature] = med
        pipe = bundle["pipeline"]
        proba = pipe.predict_proba(X_filled)[:, 1]
        y_arr = np.asarray(y)

        # Pick a *typical* low-risk and high-risk patient rather than an outlier.
        median = X_filled.median()
        spread = X_filled.std().replace(0, 1)
        distance = (((X_filled - median) / spread) ** 2).sum(axis=1).to_numpy()

        def choose(mask: np.ndarray, target: int, fallback: str) -> int:
            pool = np.where(mask & (y_arr == target))[0]
            if len(pool) == 0:
                pool = np.where(y_arr == target)[0]
            return int(pool[np.argmin(distance[pool])])

        low_idx = choose(proba <= 0.35, 0, "min")
        high_idx = choose(proba >= 0.65, 1, "max")
        examples[key] = {
            "low": {f: clean_number(X_filled.iloc[low_idx][f]) for f in bundle["features"]},
            "high": {f: clean_number(X_filled.iloc[high_idx][f]) for f in bundle["features"]},
        }

    (MODELS / "examples.json").write_text(
        json.dumps(examples, indent=2), encoding="utf-8"
    )

    print("\nWrote models/metrics.json, models/feature_ranges.json, models/examples.json")


if __name__ == "__main__":
    main()
