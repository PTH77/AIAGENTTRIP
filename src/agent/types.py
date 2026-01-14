from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UserPreferences:
    travel_comfort: float
    attractions_quality: float
    activities_match: float
    season_match: float
    score: float
    user_budget_low: int
    user_budget_medium: int
    user_budget_high: int
    trip_cost_low: int
    trip_cost_medium: int
    trip_cost_high: int


@dataclass
class Decision:
    accepted: bool
    probability: float
    explanation: str
    recommended_changes: Optional[List[str]] = None
    decision_path: Optional[List[dict]] = None
