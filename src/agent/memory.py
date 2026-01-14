from collections import Counter


class AgentMemory:
    def __init__(self):
        self.history = []
        self.rejections = []

    def remember(self, prefs, decision):
        self.history.append((prefs, decision))
        if not decision.accepted:
            self.rejections.append(decision)

    def rejected_budget_levels(self):
        return [
            prefs.budget
            for prefs, decision in self.history
            if not decision.accepted
        ]

    def has_rejected_budget(self, budget):
        return budget in self.rejected_budget_levels()

    def most_common_rejection_reason(self):
        reasons = []
        for _, decision in self.history:
            if not decision.accepted and decision.recommended_changes:
                for feature in decision.recommended_changes.keys():
                    reasons.append(feature)

        if not reasons:
            return None

        return Counter(reasons).most_common(1)[0]
