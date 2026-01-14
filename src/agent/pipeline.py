import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "models" / "model_tree.pkl"
FEATURES_PATH = BASE_DIR / "models" / "feature_columns.pkl"

model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(FEATURES_PATH)

def predict_satisfaction(user_input: dict):

    df = pd.DataFrame([user_input])

    df = pd.get_dummies(df, columns=["user_budget", "trip_cost"])

    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0

    df = df[feature_columns]

    pred = model.predict(df)[0]
    proba = model.predict_proba(df)[0, 1]

    return {
        "satisfied_prediction": int(pred),
        "satisfaction_probability": float(proba)
    }
