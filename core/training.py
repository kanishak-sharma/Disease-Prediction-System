"""Training, saving, loading and explaining models."""
from __future__ import annotations

import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split

from core.diseases import DISEASES, MODEL_DIR, feature_names, make_pipeline

LOW, HIGH = 0.33, 0.66


def build_bundle(key: str) -> dict:
    """Train one disease model and collect everything the app needs to explain it."""
    cfg = DISEASES[key]
    df, y = cfg["loader"]()
    names = feature_names(key)
    X = df[names].astype(float)
    y = y.astype(int)

    # 5-fold cross-validated predictions = honest estimate of performance
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    proba = cross_val_predict(make_pipeline(key), X, y, cv=cv, method="predict_proba")[:, 1]
    pred = (proba >= 0.5).astype(int)
    fpr, tpr, _ = roc_curve(y, proba)
    metrics = dict(
        accuracy=accuracy_score(y, pred), precision=precision_score(y, pred, zero_division=0),
        recall=recall_score(y, pred), f1=f1_score(y, pred), auc=roc_auc_score(y, proba),
        confusion=confusion_matrix(y, pred).tolist(),
        roc=dict(fpr=np.round(fpr, 4).tolist(), tpr=np.round(tpr, 4).tolist()),
        n=int(len(y)), n_disease=int(y.sum()), n_features=len(names),
    )

    # Which inputs matter overall (permutation importance on a held-out 25 %)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y, random_state=7)
    tmp = make_pipeline(key).fit(Xtr, ytr)
    imp = permutation_importance(tmp, Xte, yte, n_repeats=20, random_state=0, scoring="roc_auc")
    importance = dict(zip(names, np.round(imp.importances_mean, 4).tolist()))

    pipe = make_pipeline(key).fit(X, y)  # final model uses all data

    healthy, sick = X[y == 0], X[y == 1]
    stats = {}
    for n in names:
        stats[n] = dict(
            min=float(X[n].min()), max=float(X[n].max()),
            healthy_median=float(healthy[n].median()), disease_median=float(sick[n].median()),
            healthy_p10=float(healthy[n].quantile(.10)), healthy_p90=float(healthy[n].quantile(.90)),
            disease_p10=float(sick[n].quantile(.10)), disease_p90=float(sick[n].quantile(.90)),
        )
    # small samples for the histograms on the Insights page
    sample = X.copy()
    sample["_disease"] = y.values
    sample = sample.sample(min(len(sample), 600), random_state=1).round(4)

    return dict(key=key, pipeline=pipe, features=names, metrics=metrics, importance=importance,
                stats=stats, sample=sample, rows=int(len(df)))


def save_all(keys=None) -> None:
    MODEL_DIR.mkdir(exist_ok=True)
    for k in keys or DISEASES:
        b = build_bundle(k)
        joblib.dump(b, MODEL_DIR / f"{k}.joblib", compress=3)
        m = b["metrics"]
        print(f"{k:11s} acc={m['accuracy']:.3f} recall={m['recall']:.3f} auc={m['auc']:.3f} (n={m['n']})")


def load_bundle(key: str) -> dict:
    """Load the saved model. If the file is missing or made with another scikit-learn
    version, quietly retrain from the CSV so the app never crashes."""
    path = MODEL_DIR / f"{key}.joblib"
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # a version-mismatch warning -> retrain
            return joblib.load(path)
    except Exception:
        return build_bundle(key)


# ------------------------------------------------------------------ prediction
def risk_level(p: float) -> str:
    return "Low" if p < LOW else "Moderate" if p < HIGH else "High"


def predict(bundle: dict, values: dict) -> float:
    row = pd.DataFrame([[values[n] for n in bundle["features"]]], columns=bundle["features"]).astype(float)
    return float(bundle["pipeline"].predict_proba(row)[0, 1])


def explain(bundle: dict, values: dict) -> pd.DataFrame:
    """Per-input effect on this result: swap one input at a time for the typical healthy
    value and see how much the risk changes. Works for any model type."""
    base = predict(bundle, values)
    rows = []
    for n in bundle["features"]:
        alt = dict(values)
        alt[n] = bundle["stats"][n]["healthy_median"]
        rows.append((n, base - predict(bundle, alt)))
    out = pd.DataFrame(rows, columns=["feature", "effect"])
    return out.reindex(out.effect.abs().sort_values(ascending=False).index).reset_index(drop=True)


def out_of_range(bundle: dict, values: dict) -> list[str]:
    """Inputs outside what the model saw in training (its answer is a guess there)."""
    bad = []
    for n in bundle["features"]:
        s = bundle["stats"][n]
        if values[n] < s["min"] - 1e-9 or values[n] > s["max"] + 1e-9:
            bad.append(n)
    return bad
