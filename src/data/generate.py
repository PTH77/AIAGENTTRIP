import numpy as np
import pandas as pd
from pathlib import Path

N_SAMPLES = 1000
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

OUTPUT_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / "dane_v2.csv"

def generate_row() -> dict:
    return {
        "travel_comfort": np.random.randint(1, 6),
        "attractions_quality": np.random.randint(1, 6),
        "activities_match": np.random.randint(0, 3),
        "season_match": np.random.choice([0, 1], p=[0.3, 0.7]),
        "user_budget": np.random.choice(["low", "medium", "high"], p=[0.4, 0.4, 0.2]),
        "trip_cost": np.random.choice(["low", "medium", "high"], p=[0.4, 0.4, 0.2]),
    }
def generate_dataset(n_samples: int) -> pd.DataFrame:
    data = [generate_row() for _ in range(n_samples)]
    return pd.DataFrame(data)

def compute_score(row):
    score = 0
    if row["travel_comfort"] >= 4:
        score += 2
    elif row["travel_comfort"] >= 3:
        score += 1
    if row["attractions_quality"] >= 4:
        score += 2
    elif row["attractions_quality"] >= 3: 
        score += 1
    score += row["activities_match"]
    if row["season_match"] == 1:
        score += 1
    if row["user_budget"] == row["trip_cost"]:
        score += 2
    elif row["user_budget"] == "high" and row["trip_cost"] != "high": 
        score += 1
    return score

def compute_satisfied(row):
    base_prob = 0.08 + 0.09 * row["score"] 
    noise = np.random.uniform(-0.03, 0.03)
    prob = np.clip(base_prob + noise, 0.05, 0.92) 
    return int(np.random.rand() < prob)

if __name__ == "__main__": 
    df = generate_dataset(N_SAMPLES)
    df["score"] = df.apply(compute_score, axis=1) 
    df["satisfied"] = df.apply(compute_satisfied, axis=1)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True) 
    df.to_csv(OUTPUT_PATH, index=False)

    print("Dataset wygenerowany:") 
    print(df.head())
    print("\nRozkład satisfied:") 
    print(df["satisfied"].value_counts(normalize=True))
    print("\nŚredni score:") 
    print(df.groupby("satisfied")["score"].mean())
    print("\nRozkład score:")
    print(df["score"].describe())
    print( 
        df.groupby("score")["satisfied"] 
        .mean()
        .reset_index() 
        .rename(columns={"satisfied": "satisfied=1"})
    )
    numeric_cols = [
        "travel_comfort", 
        "attractions_quality", 
        "activities_match",
        "season_match", 
        "score",
        "satisfied" 
    ]

print(df[numeric_cols].corr()) 
print(df.groupby("score")["satisfied"].mean())