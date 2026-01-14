import joblib
from src.agent.agent import TravelAgent
from src.agent.types import UserPreferences

MODEL_PATH = "models/model_tree.pkl"

if __name__ == "__main__":
    model = joblib.load(MODEL_PATH)

    print("Model expects:", model.n_features_in_)
    print("Feature names from model:")
    for f in model.feature_names_in_:
        print(" -", f)

    agent = TravelAgent(model)

    prefs = UserPreferences(
        travel_comfort=0.7,
        attractions_quality=0.6,
        activities_match=0.5,
        season_match=0.8,
        score=0.6,

        user_budget_low=0,
        user_budget_medium=1,
        user_budget_high=0,

        trip_cost_low=0,
        trip_cost_medium=1,
        trip_cost_high=0
    )

    decision = agent.handle(prefs)
    print(decision)

    print("\nŚcieżka decyzyjna modelu:")
    for line in agent.decision_engine.get_decision_path_text(
        decision.decision_path
    ):
        print(" -", line)
