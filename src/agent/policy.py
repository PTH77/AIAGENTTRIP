class PolicyEngine:
    def __init__(self, memory):
        self.memory = memory

    def apply(self, prefs):
        common_reason = self.memory.most_common_rejection_reason()

        if common_reason:
            feature, _ = common_reason

            if feature == "budget":
                prefs.budget = int(prefs.budget * 1.1)

            if feature == "duration_days":
                prefs.duration_days += 2

        return prefs
