import joblib
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt

#ŚCIEŻKI
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "raw" / "dane_v2.csv"
MODEL_PATH = BASE_DIR / "models" / "model_tree.pkl"
FEATURES_PATH = BASE_DIR / "models" / "feature_columns.pkl"

#DANE
df = pd.read_csv(DATA_PATH)
X = df.drop("satisfied", axis=1)
y = df["satisfied"]

# Wczytanie wcześniej zapisanych kolumn (feature_columns)
feature_columns = joblib.load(FEATURES_PATH)

# One-hot encoding dla kolumn kategorycznych
X = pd.get_dummies(X, columns=["user_budget", "trip_cost"])

# Dodanie brakujących kolumn (np. jeśli w danych testowych ich brakuje)
for col in feature_columns:
    if col not in X.columns:
        X[col] = 0

# Usunięcie nadmiarowych kolumn
X = X[feature_columns]

# Lista nazw cech do wykresów
feature_names = feature_columns

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = joblib.load(MODEL_PATH)

#TRENING i PREDYKCJE
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

print("TRAIN RESULTS")
print(classification_report(y_train, y_train_pred))

print("TEST RESULTS")
print(classification_report(y_test, y_test_pred))

#MACIERZE POMYŁEK
cm_train = confusion_matrix(y_train, y_train_pred)
disp_train = ConfusionMatrixDisplay(cm_train)
disp_train.plot()
plt.title("Confusion Matrix - TRAIN (max_depth=5)")
plt.show()

cm_test = confusion_matrix(y_test, y_test_pred)
disp_test = ConfusionMatrixDisplay(cm_test)
disp_test.plot()
plt.title("Confusion Matrix - TEST (max_depth=5)")
plt.show()

#KRZYWA ROC
y_train_proba = model.predict_proba(X_train)[:, 1]
y_test_proba = model.predict_proba(X_test)[:, 1]

fpr_train, tpr_train, _ = roc_curve(y_train, y_train_proba)
fpr_test, tpr_test, _ = roc_curve(y_test, y_test_proba)

plt.plot(fpr_train, tpr_train, label="TRAIN")
plt.plot(fpr_test, tpr_test, label="TEST")
plt.plot([0,1], [0,1], linestyle="--", color="gray")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve (max_depth=5)")
plt.legend()
plt.show()

#WIZUALIZACJA DRZEWA
plt.figure(figsize=(20,10))
plot_tree(
    model,
    feature_names=feature_names,
    class_names=["0", "1"],
    filled=True,
    max_depth=3
)
plt.title("Decision Tree (depth <= 3) (max_depth=5)")
plt.show()

#FEATURE IMPORTANCE
importances = model.feature_importances_
df_importance = pd.DataFrame({
    "feature": feature_names,
    "importance": importances
}).sort_values(by="importance", ascending=False)

df_importance.plot(kind="bar", x="feature", y="importance", legend=False)
plt.title("Feature Importance")
plt.ylabel("Importance")
plt.show()
