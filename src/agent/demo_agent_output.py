from agent.agent import TravelAIAgent
from agent.wejscie import UserPreferences


def run_demo_case(title, prefs):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)

    agent = TravelAIAgent()
    result = agent.decide(prefs)

    print(f"Recommended: {'YES' if result.decision == 1 else 'NO'}")
    print(f"Confidence: {round(result.probability, 2)}")
    print("Explanation:")
    for e in result.explanation:
        print("-", e)

    if result.recommendations:
        print("Suggested changes:")
        for r in result.recommendations:
            print("-", r)


def main():
    # SCENARIUSZ 1 – dobra oferta
    prefs_good = UserPreferences(
        travel_comfort=0.9,
        attractions_quality=0.9,
        activities_match=0.8,
        season_match=1.0,
        score=0.9,
        user_budget="high",
        trip_cost="low"
    )

    # SCENARIUSZ 2 – słaba oferta
    prefs_bad = UserPreferences(
        travel_comfort=0.2,
        attractions_quality=0.3,
        activities_match=0.1,
        season_match=0.0,
        score=0.2,
        user_budget="low",
        trip_cost="high"
    )

    # SCENARIUSZ 3 – oferta graniczna
    prefs_border = UserPreferences(
        travel_comfort=0.5,
        attractions_quality=0.5,
        activities_match=0.5,
        season_match=1.0,
        score=0.5,
        user_budget="medium",
        trip_cost="medium"
    )

    run_demo_case("SCENARIO 1 – GOOD OFFER", prefs_good)
    run_demo_case("SCENARIO 2 – BAD OFFER", prefs_bad)
    run_demo_case("SCENARIO 3 – BORDERLINE OFFER", prefs_border)


if __name__ == "__main__":
    main()
