import pandas as pd
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix

# ŚCIEŻKI
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "raw" / "dane_v2.csv"
BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "models" / "model_tree.pkl"

# WCZYTANIE DANYCH
df = pd.read_csv(DATA_PATH)

X = df.drop("satisfied", axis=1)
y = df["satisfied"]

# ONE-HOT
X = pd.get_dummies(X)
FEATURE_COLUMNS = X.columns
joblib.dump(FEATURE_COLUMNS, BASE_DIR / "models" / "feature_columns.pkl")


# PODZIAŁ
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# MODEL
model = DecisionTreeClassifier(
    max_depth=5,
    min_samples_leaf=20,
    random_state=42
    )

# TRENING
model.fit(X_train, y_train)

# EWALUACJA
y_pred = model.predict(X_test)
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(model, MODEL_PATH)

print("CONFUSION MATRIX:")
print(confusion_matrix(y_test, y_pred))

print("\nCLASSIFICATION REPORT:")
print(classification_report(y_test, y_pred))
