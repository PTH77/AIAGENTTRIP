import numpy as np
import pandas as pd


class DecisionEngine:
    def __init__(self, model, vectorizer, feature_names):
        self.model = model
        self.vectorizer = vectorizer
        self.feature_names = feature_names
        self.tree = model.tree_

    def decide(self, prefs):
        vector = self.vectorizer.vectorize(prefs)
        X = pd.DataFrame(vector, columns=self.feature_names)

        prob = self.model.predict_proba(X)[0][1]
        accepted = self.model.predict(X)[0] == 1

        decision_path = self._extract_decision_path(X)

        blocked = [
            step for step in decision_path
            if step["direction"] == "left"
        ]

        confidence = abs(prob - 0.5) * 2

        return accepted, prob, confidence, blocked, decision_path

    def _extract_decision_path(self, X):
        node_id = 0
        path = []

        while self.tree.children_left[node_id] != -1:
            feature_index = self.tree.feature[node_id]
            threshold = self.tree.threshold[node_id]
            feature_name = self.feature_names[feature_index]
            value = X.iloc[0, feature_index]

            if value <= threshold:
                direction = "left"
                next_node = self.tree.children_left[node_id]
            else:
                direction = "right"
                next_node = self.tree.children_right[node_id]

            path.append({
                "feature": feature_name,
                "value": float(value),
                "threshold": float(threshold),
                "direction": direction
            })

            node_id = next_node

        return path

    def get_decision_path_text(self, decision_path):
        if not decision_path:
            return ["Brak ścieżki decyzyjnej"]

        lines = []
        for step in decision_path:
            symbol = "≤" if step["direction"] == "left" else ">"
            lines.append(
                f"{step['feature']}: {step['value']:.2f} {symbol} {step['threshold']:.2f}"
            )
        return lines
