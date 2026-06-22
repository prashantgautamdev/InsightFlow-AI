"""
Auto EDA Generator.

Given a pandas DataFrame, produces a complete EDA report:
missing values, outliers (IQR method), per-column statistics,
correlation matrix, histogram bins, and boxplot quartiles —
all as JSON-serializable dicts ready for Recharts/Plotly on the frontend.
"""
from typing import Any, Dict

import numpy as np
import pandas as pd


def _clean_for_json(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if pd.isna(value):
        return None
    return value


def run_full_eda(df: pd.DataFrame) -> Dict[str, Any]:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    summary = {
        "n_rows": int(df.shape[0]),
        "n_columns": int(df.shape[1]),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage_kb": round(df.memory_usage(deep=True).sum() / 1024, 2),
    }

    # ---- Missing values ----
    missing_counts = df.isnull().sum()
    missing_values = {
        col: {
            "missing_count": int(missing_counts[col]),
            "missing_pct": round(float(missing_counts[col]) / len(df) * 100, 2) if len(df) else 0,
        }
        for col in df.columns
    }

    # ---- Outliers (IQR method, numeric only) ----
    outliers: Dict[str, Any] = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            outliers[col] = {"count": 0, "lower_bound": None, "upper_bound": None}
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_outliers = int(((series < lower) | (series > upper)).sum())
        outliers[col] = {
            "count": n_outliers,
            "lower_bound": _clean_for_json(lower),
            "upper_bound": _clean_for_json(upper),
        }

    # ---- Per-column statistics ----
    statistics: Dict[str, Any] = {}
    for col in numeric_cols:
        desc = df[col].describe()
        statistics[col] = {k: _clean_for_json(v) for k, v in desc.to_dict().items()}
        statistics[col]["skew"] = _clean_for_json(df[col].skew())
        statistics[col]["dtype"] = "numeric"
    for col in categorical_cols:
        statistics[col] = {
            "unique_values": int(df[col].nunique()),
            "top_value": _clean_for_json(df[col].mode().iloc[0]) if not df[col].mode().empty else None,
            "dtype": "categorical",
        }

    # ---- Correlation matrix ----
    correlation: Dict[str, Any] = {}
    if len(numeric_cols) >= 2:
        corr_df = df[numeric_cols].corr().round(3)
        correlation = {
            "columns": numeric_cols,
            "matrix": [[_clean_for_json(v) for v in row] for row in corr_df.values.tolist()],
        }

    # ---- Histograms (numeric) ----
    histograms: Dict[str, Any] = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue
        counts, bin_edges = np.histogram(series, bins=10)
        histograms[col] = {
            "bins": [round(float(b), 2) for b in bin_edges],
            "counts": [int(c) for c in counts],
        }

    # ---- Boxplots (numeric quartile summary) ----
    boxplots: Dict[str, Any] = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue
        boxplots[col] = {
            "min": _clean_for_json(series.min()),
            "q1": _clean_for_json(series.quantile(0.25)),
            "median": _clean_for_json(series.median()),
            "q3": _clean_for_json(series.quantile(0.75)),
            "max": _clean_for_json(series.max()),
        }

    return {
        "summary": summary,
        "missing_values": missing_values,
        "outliers": outliers,
        "statistics": statistics,
        "correlation": correlation,
        "histograms": histograms,
        "boxplots": boxplots,
    }


def top_correlated_pairs(df: pd.DataFrame, top_n: int = 10):
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        return []
    corr = df[numeric_cols].corr().abs()
    pairs = []
    for i, c1 in enumerate(numeric_cols):
        for c2 in numeric_cols[i + 1:]:
            pairs.append((c1, c2, round(float(corr.loc[c1, c2]), 3)))
    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs[:top_n]


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Basic automated cleaning: drop fully-empty cols, impute numeric with
    median, categorical with mode, drop exact duplicate rows."""
    df = df.dropna(axis=1, how="all").drop_duplicates()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())
    for col in categorical_cols:
        mode = df[col].mode()
        if not mode.empty:
            df[col] = df[col].fillna(mode.iloc[0])
    return df
