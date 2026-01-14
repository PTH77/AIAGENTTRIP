from src.agent import TravelAgent
from src.agent.types import UserPreferences
class FakeModel:
    def predict_proba(self, X):
        probs = []
        for x in X:
            if x["budget"] >= 4000:
                probs.append([0.2, 0.8])
            else:
                probs.append([0.9, 0.1])
        return probs

model = FakeModel()
agent = TravelAgent(model)

prefs1 = UserPreferences(
    budget=3000,
    duration_days=5,
    destination_type="city",
    travel_style="budget"
)

decision1 = agent.handle(prefs1)
print(decision1)

prefs2 = UserPreferences(
    budget=3000,
    duration_days=5,
    destination_type="city",
    travel_style="budget"
)

decision2 = agent.handle(prefs2)
print(decision2)

print(agent.memory.rejected_budget_levels())
