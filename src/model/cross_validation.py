import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.tree import DecisionTreeClassifier

# ŚCIEŻKI
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "raw" / "dane_v2.csv"

# DANE
df = pd.read_csv(DATA_PATH)
X = pd.get_dummies(df.drop("satisfied", axis=1))
y = df["satisfied"]

# MODEL (TEN SAM CO W TRAIN)
model = DecisionTreeClassifier(
    max_depth=4,
    min_samples_leaf=20,
    random_state=42
)

# CROSS-VALIDATION
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scoring = {
    "accuracy": "accuracy",
    "f1": "f1"
}

results = cross_validate(
    model,
    X,
    y,
    cv=cv,
    scoring=scoring,
    return_train_score=True
)

# RAPORT
print("=== CROSS-VALIDATION RESULTS ===\n")

for metric in scoring.keys():
    train_scores = results[f"train_{metric}"]
    test_scores = results[f"test_{metric}"]

    print(f"{metric.upper()}:")
    print(f"  TRAIN mean: {train_scores.mean():.3f} ± {train_scores.std():.3f}")
    print(f"  TEST  mean: {test_scores.mean():.3f} ± {test_scores.std():.3f}\n")
