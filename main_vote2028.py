"""
main_vote2028.py â€” Global presidential county model (Phase 6)
=============================================================
Trains a single model on ALL county-year rows (~19,000) and predicts
the 2028 outcome for a requested county using its most recent election
features.

Why global vs. per-county:
  - Per-county trained on â‰¤ 6 rows â†’ meaningless accuracy, single-class
    fallback for always-Dem/Rep counties (e.g. Fulton GA, Glacier MT)
  - Global trains on 80 % of 19,155 rows, tests on 20 % â†’ valid metrics
  - County prediction = predict(most-recent features for target county)

Models are cached process-wide after first training (warm-up on startup).
"""

import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from preprocess import load_data

# ---------------------------------------------------------------------------
# Module-level cache â€” populated once per process (cold start), then reused
# ---------------------------------------------------------------------------
_cache = {
    "models": None,       # dict of {model_name: fitted_model}
    "scaler": None,       # fitted StandardScaler
    "feature_cols": None, # ordered list of feature column names
    "reports": None,      # classification_reports from global test set
    "df_features": None,  # encoded feature DataFrame aligned with training
    "df_raw": None,       # raw DataFrame (County / State / Election Year)
}

_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'voting_pres_data.csv')


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_features(df: pd.DataFrame):
    """
    Compute model features from the raw DataFrame.
    Returns (feature_df, y_series, cleaned_df).
    """
    d = df.copy()

    # Vote shares (primary signal)
    d['Total Voted'] = d['Total Voted'].replace(0, np.nan)
    d['Democratic Vote Share'] = d['Democratic Votes'] / d['Total Voted']
    d['Republican Vote Share']  = d['Republican Votes']  / d['Total Voted']

    # Turnout: 0.0 where Total Registered Voters is unknown (MEDSL rows store 0)
    d['Turnout'] = np.where(
        d['Total Registered Voters'] > 0,
        d['Total Ballots Cast'] / d['Total Registered Voters'],
        0.0,
    )

    # Target: did Democrats win this county-year?
    d['Democratic Wins'] = (d['Democratic Votes'] > d['Republican Votes']).astype(int)

    # Drop rows with no usable vote-share data
    d = d.dropna(subset=['Democratic Vote Share', 'Republican Vote Share'])

    # One-hot encode State (2-letter code)
    state_dummies = pd.get_dummies(d['State'].str.upper(), prefix='State')

    numeric_cols = ['Democratic Vote Share', 'Republican Vote Share', 'Turnout', 'Election Year']
    feature_df = pd.concat(
        [d[numeric_cols].reset_index(drop=True), state_dummies.reset_index(drop=True)],
        axis=1,
    ).fillna(0.0)

    return feature_df, d['Democratic Wins'].reset_index(drop=True), d.reset_index(drop=True)


def _train_global_models():
    """Load data, train all four models, populate the module cache."""
    print("Loading data for global model training...")
    df = load_data(_DATA_PATH)
    if df is None:
        raise RuntimeError("Failed to load voting data")

    feature_df, y, df_clean = _build_features(df)
    feature_cols = list(feature_df.columns)

    X = feature_df.values

    # Stratified 80/20 split across all county-years
    X_train, X_test, y_train, y_test = train_test_split(
        X, y.values, test_size=0.2, random_state=42, stratify=y.values
    )

    # Scaler for LR / SVM
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    # SVC uses kernel='linear' â€” RBF is O(nÂ²) which is too slow at ~15 K rows
    model_specs = {
        'Random Forest':      (RandomForestClassifier(n_estimators=100, random_state=42), X_train,   X_test),
        'Logistic Regression':(LogisticRegression(max_iter=1000, random_state=42),         X_train_s, X_test_s),
        'SVM':                (SVC(kernel='linear', max_iter=5000, random_state=42),        X_train_s, X_test_s),
        'Gradient Boosting':  (GradientBoostingClassifier(random_state=42),                 X_train,   X_test),
    }

    fitted_models = {}
    reports = {}

    for name, (model, Xtr, Xte) in model_specs.items():
        print(f"  Training {name}...")
        model.fit(Xtr, y_train)
        y_pred = model.predict(Xte)
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        reports[name] = _serialise_report(report)
        fitted_models[name] = model
        print(f"    accuracy = {reports[name].get('accuracy', 'N/A'):.3f}")

    # Populate cache
    _cache["models"]       = fitted_models
    _cache["scaler"]       = scaler
    _cache["feature_cols"] = feature_cols
    _cache["reports"]      = reports
    _cache["df_features"]  = feature_df
    _cache["df_raw"]       = df_clean

    n_counties = df_clean['County'].nunique()
    print(f"Global model ready â€” {len(df_clean):,} rows, {n_counties:,} counties.")


def _serialise_report(report: dict) -> dict:
    """Convert numpy scalar types in a classification report to Python natives."""
    out = {}
    for key, value in report.items():
        if isinstance(value, dict):
            out[key] = {
                k: (int(v) if isinstance(v, np.integer) else float(v) if isinstance(v, np.floating) else v)
                for k, v in value.items()
            }
        elif isinstance(value, np.integer):
            out[key] = int(value)
        elif isinstance(value, np.floating):
            out[key] = float(value)
        else:
            out[key] = value
    return out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def preload_models():
    """Pre-warm the model cache. Called by app.py at startup."""
    if _cache["models"] is None:
        _train_global_models()


def main(county_name: str, state_name: str) -> dict:
    """
    Predict the 2028 presidential outcome for county_name, state_name.

    Returns a dict compatible with the frontend:
      {
        "classification_reports": {model_name: sklearn_report_dict},
        "predictions":            {model_name: [0_or_1]}
      }
    or
      {"message": "...explanation..."}
    """
    # Ensure models are trained (no-op on subsequent calls)
    if _cache["models"] is None:
        _train_global_models()

    df_raw        = _cache["df_raw"]
    feature_df    = _cache["df_features"]
    feature_cols  = _cache["feature_cols"]
    fitted_models = _cache["models"]
    scaler        = _cache["scaler"]
    reports       = _cache["reports"]

    # Locate the target county (case-insensitive)
    mask = (
        (df_raw['County'].str.lower() == county_name.strip().lower()) &
        (df_raw['State'].str.upper()  == state_name.strip().upper())
    )
    if not mask.any():
        return {"message": f"No data found for {county_name}, {state_name}"}

    # Use the most recent election year as the feature vector for prediction
    latest_pos = df_raw[mask]['Election Year'].idxmax()
    X_target   = feature_df.loc[latest_pos, feature_cols].values.reshape(1, -1)
    X_target_s = scaler.transform(X_target)

    # Map each model to its appropriate feature matrix (raw vs. scaled)
    target_by_model = {
        'Random Forest':       X_target,
        'Logistic Regression': X_target_s,
        'SVM':                 X_target_s,
        'Gradient Boosting':   X_target,
    }

    predictions = {}
    for name, model in fitted_models.items():
        try:
            pred = int(model.predict(target_by_model[name])[0])
        except Exception as e:
            print(f"Prediction error ({name}): {e}")
            pred = 0
        predictions[name] = [pred]

    return {
        "classification_reports": reports,
        "predictions": predictions,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main_vote2028.py <county_name> <state_abbreviation>")
        print("Example: python main_vote2028.py Fulton GA")
        sys.exit(1)
    result = main(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2))
