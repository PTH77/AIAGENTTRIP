from .memory import AgentMemory
from .policy import PolicyEngine
from .decision import DecisionEngine
from .recommender import Recommender
from .types import Decision
from .vectorizer import FeatureVectorizer


class TravelAgent:
    def __init__(self, model):
        self.memory = AgentMemory()
        self.vectorizer = FeatureVectorizer(model)
        self.policy = PolicyEngine(self.memory)

        self.decision_engine = DecisionEngine(
            model=model,
            vectorizer=self.vectorizer,
            feature_names=list(model.feature_names_in_)
        )

        self.recommender = Recommender(model)

    def handle(self, prefs):
        prefs = self.policy.apply(prefs)

        accepted, prob, confidence, blocked, decision_path = \
            self.decision_engine.decide(prefs)

        if not accepted:
            recs = self.recommender.suggest(blocked)
            decision = Decision(
                accepted=False,
                probability=prob,
                explanation="Oferta nie spełnia warunków decyzyjnych modelu",
                recommended_changes=recs,
                decision_path=decision_path
            )
        else:
            decision = Decision(
                accepted=True,
                probability=prob,
                explanation="Oferta spełnia warunki decyzyjne modelu",
                decision_path=decision_path
            )

        self.memory.remember(prefs, decision)
        return decision
