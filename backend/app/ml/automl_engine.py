"""
AutoML engine.

Trains several candidate models for classification or regression tasks,
evaluates them on a held-out split, and returns a comparison plus the
artifacts needed to render confusion matrices / ROC curves on the frontend.
"""
from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, auc, mean_absolute_error,
    mean_squared_error, r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier, XGBRegressor


def _prepare_features(df: pd.DataFrame, target_column: str):
    df = df.dropna(subset=[target_column]).copy()
    y_raw = df[target_column]
    X = df.drop(columns=[target_column])

    # Encode categoricals, impute numerics
    for col in X.columns:
        if X[col].dtype == object:
            X[col] = X[col].fillna("missing")
            X[col] = LabelEncoder().fit_transform(X[col].astype(str))
        else:
            X[col] = X[col].fillna(X[col].median())

    return X, y_raw


def run_classification_automl(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
    X, y_raw = _prepare_features(df, target_column)
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw.astype(str))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if len(set(y)) > 1 else None
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    candidates = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42),
        "XGBoost": XGBClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.08,
            eval_metric="logloss", random_state=42,
        ),
    }

    results = []
    fitted = {}
    for name, model in candidates.items():
        Xtr = X_train_s if name == "Logistic Regression" else X_train
        Xte = X_test_s if name == "Logistic Regression" else X_test
        model.fit(Xtr, y_train)
        preds = model.predict(Xte)
        avg = "binary" if len(set(y)) == 2 else "weighted"
        metrics = {
            "accuracy": round(float(accuracy_score(y_test, preds)), 4),
            "precision": round(float(precision_score(y_test, preds, average=avg, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, preds, average=avg, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, preds, average=avg, zero_division=0)), 4),
        }
        results.append({"name": name, "metrics": metrics})
        fitted[name] = (model, Xte, preds)

    best = max(results, key=lambda r: r["metrics"]["f1_score"])
    best_model, best_Xte, best_preds = fitted[best["name"]]

    cm = confusion_matrix(y_test, best_preds).tolist()

    roc_data = None
    if len(set(y)) == 2 and hasattr(best_model, "predict_proba"):
        probs = best_model.predict_proba(best_Xte)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, probs)
        roc_data = {
            "fpr": [round(float(v), 4) for v in fpr],
            "tpr": [round(float(v), 4) for v in tpr],
            "auc": round(float(auc(fpr, tpr)), 4),
        }

    feature_importance = {}
    if hasattr(best_model, "feature_importances_"):
        feature_importance = dict(zip(
            X.columns.tolist(),
            [round(float(v), 4) for v in best_model.feature_importances_],
        ))

    return {
        "models_trained": results,
        "best_model": best["name"],
        "metrics": best["metrics"],
        "feature_importance": feature_importance,
        "confusion_matrix": {"labels": label_encoder.classes_.tolist(), "matrix": cm},
        "roc_curve": roc_data,
    }


def run_regression_automl(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
    X, y = _prepare_features(df, target_column)
    y = y.astype(float)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    candidates = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=200, random_state=42),
        "XGBoost": XGBRegressor(
            n_estimators=200, max_depth=5, learning_rate=0.08, random_state=42
        ),
    }

    results = []
    fitted = {}
    for name, model in candidates.items():
        Xtr = X_train_s if name == "Linear Regression" else X_train
        Xte = X_test_s if name == "Linear Regression" else X_test
        model.fit(Xtr, y_train)
        preds = model.predict(Xte)
        metrics = {
            "mae": round(float(mean_absolute_error(y_test, preds)), 4),
            "rmse": round(float(np.sqrt(mean_squared_error(y_test, preds))), 4),
            "r2_score": round(float(r2_score(y_test, preds)), 4),
        }
        results.append({"name": name, "metrics": metrics})
        fitted[name] = model

    best = max(results, key=lambda r: r["metrics"]["r2_score"])
    best_model = fitted[best["name"]]

    feature_importance = {}
    if hasattr(best_model, "feature_importances_"):
        feature_importance = dict(zip(
            X.columns.tolist(),
            [round(float(v), 4) for v in best_model.feature_importances_],
        ))

    return {
        "models_trained": results,
        "best_model": best["name"],
        "metrics": best["metrics"],
        "feature_importance": feature_importance,
        "confusion_matrix": None,
        "roc_curve": None,
    }


def run_timeseries_forecast(df: pd.DataFrame, date_column: str, target_column: str, periods: int = 30) -> Dict[str, Any]:
    """Prophet-based forecast. Falls back gracefully if Prophet isn't installed."""
    try:
        from prophet import Prophet
    except ImportError:
        return {"error": "Prophet not installed", "forecast": []}

    ts_df = df[[date_column, target_column]].dropna()
    ts_df.columns = ["ds", "y"]
    ts_df["ds"] = pd.to_datetime(ts_df["ds"])

    model = Prophet()
    model.fit(ts_df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    return {
        "forecast": [
            {
                "date": row["ds"].strftime("%Y-%m-%d"),
                "yhat": round(float(row["yhat"]), 2),
                "yhat_lower": round(float(row["yhat_lower"]), 2),
                "yhat_upper": round(float(row["yhat_upper"]), 2),
            }
            for _, row in forecast.tail(periods + 30).iterrows()
        ]
    }
