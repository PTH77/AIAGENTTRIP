import joblib
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UserPreferences:
    travel_comfort: int
    attractions_quality: int
    activities_match: int
    season_match: int
    user_budget: str
    trip_cost: str
    
    def compute_score(self) -> int:
        score = 0
        if self.travel_comfort >= 4:
            score += 2
        elif self.travel_comfort >= 3:
            score += 1
        if self.attractions_quality >= 4:
            score += 2
        elif self.attractions_quality >= 3:
            score += 1
        score += self.activities_match
        if self.season_match == 1:
            score += 1
        if self.user_budget == self.trip_cost:
            score += 2
        elif self.user_budget == "high" and self.trip_cost != "high":
            score += 1
        return score


@dataclass
class Decision:
    accepted: bool
    probability: float
    explanation: str
    recommended_changes: Optional[List[str]] = None
    decision_path: Optional[List[dict]] = None


class TravelAgent:
    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)
        self.feature_names = list(self.model.feature_names_in_)
        self.tree = self.model.tree_
    
    def decide(self, prefs: UserPreferences) -> Decision:
        score = prefs.compute_score()
        
        input_dict = {
            'travel_comfort': prefs.travel_comfort,
            'attractions_quality': prefs.attractions_quality,
            'activities_match': prefs.activities_match,
            'season_match': prefs.season_match,
            'score': score,
            'user_budget': prefs.user_budget,
            'trip_cost': prefs.trip_cost
        }
        
        df = pd.DataFrame([input_dict])
        df = pd.get_dummies(df, columns=['user_budget', 'trip_cost'])
        
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0
        
        df = df[self.feature_names]
        
        prediction = self.model.predict(df)[0]
        probability = self.model.predict_proba(df)[0][1]
        
        decision_path = self._extract_decision_path(df)
        
        if prediction == 0:
            recommendations = self._generate_recommendations(decision_path)
            explanation = f"Oferta odrzucona przez model (score: {score})"
        else:
            recommendations = None
            explanation = f"Oferta zaakceptowana przez model (score: {score})"
        
        return Decision(
            accepted=(prediction == 1),
            probability=probability,
            explanation=explanation,
            recommended_changes=recommendations,
            decision_path=decision_path
        )
    
    def _extract_decision_path(self, X: pd.DataFrame) -> List[dict]:
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
                "direction": direction,
                "passed": direction == "right"
            })
            
            node_id = next_node
        
        return path
    
    def _generate_recommendations(self, decision_path: List[dict]) -> List[str]:
        recommendations = []
        
        for step in decision_path:
            if step["direction"] == "left":
                feature = step["feature"]
                
                if "user_budget_low" in feature:
                    recommendations.append("Zwieksz budzet lub wybierz tansza oferte")
                elif "trip_cost_high" in feature:
                    recommendations.append("Wybierz tanszy kierunek lub krotszy pobyt")
                elif "activities_match" in feature:
                    recommendations.append("Wybierz oferte lepiej dopasowana do twoich zainteresowan")
                elif "season_match" in feature:
                    recommendations.append("Rozwaz inny termin wyjazdu")
                elif "attractions_quality" in feature:
                    recommendations.append("Wybierz miejsce z lepszymi atrakcjami")
                elif "travel_comfort" in feature:
                    recommendations.append("Rozwaz oferte z lepszym komfortem podrozy")
        
        return list(dict.fromkeys(recommendations))
    
    def print_decision(self, decision: Decision):
        print("\n")
        print(f"DECYZJA: {'ZAAKCEPTOWANA' if decision.accepted else 'ODRZUCONA'}")
        print(f"Pewnosc: {decision.probability:.1%}")
        print(f"Wyjasnienie: {decision.explanation}")
        
        if decision.recommended_changes:
            print("\nRekomendacje:")
            for rec in decision.recommended_changes:
                print(f"  {rec}")
        
        if decision.decision_path:
            print("\nSciezka decyzyjna:")
            for step in decision.decision_path:
                status = "[+]" if step["passed"] else "[-]"
                print(f"  {status} {step['feature']}: {step['value']:.2f} {'>' if step['passed'] else '<='} {step['threshold']:.2f}")
        
        print()