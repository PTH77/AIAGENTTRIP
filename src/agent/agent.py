import joblib
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class UserPreferences:
    travel_comfort: float
    attractions_quality: float
    activities_match: float
    season_match: float
    score: float
    user_budget: str
    trip_cost: str


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
        input_dict = {
            'travel_comfort': prefs.travel_comfort,
            'attractions_quality': prefs.attractions_quality,
            'activities_match': prefs.activities_match,
            'season_match': prefs.season_match,
            'score': prefs.score,
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
            explanation = "Oferta odrzucona przez model"
        else:
            recommendations = None
            explanation = "Oferta zaakceptowana przez model"
        
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
                    recommendations.append("Zwiększ budżet lub wybierz tańszą ofertę")
                elif "trip_cost_high" in feature:
                    recommendations.append("Wybierz tańszy kierunek lub krótszy pobyt")
                elif "activities_match" in feature:
                    recommendations.append("Wybierz ofertę lepiej dopasowaną do twoich zainteresowań")
                elif "season_match" in feature:
                    recommendations.append("Rozważ inny termin wyjazdu")
                elif "attractions_quality" in feature:
                    recommendations.append("Wybierz miejsce z lepszymi atrakcjami")
                elif "travel_comfort" in feature:
                    recommendations.append("Rozważ ofertę z lepszym komfortem podróży")
        
        return list(dict.fromkeys(recommendations))
    
    def print_decision(self, decision: Decision):
        print("\n" + "="*50)
        print(f"DECYZJA: {'ZAAKCEPTOWANA' if decision.accepted else 'ODRZUCONA'}")
        print(f"Pewność: {decision.probability:.1%}")
        print(f"Wyjaśnienie: {decision.explanation}")
        
        if decision.recommended_changes:
            print("\mRekomendacje:")
            for rec in decision.recommended_changes:
                print(f"  • {rec}")
        
        if decision.decision_path:
            print("\nŚcieżka decyzyjna:")
            for step in decision.decision_path:
                status = "✓" if step["passed"] else "✗"
                print(f"  {status} {step['feature']}: {step['value']:.2f} {'>' if step['passed'] else '≤'} {step['threshold']:.2f}")
        
        print("="*50 + "\n")