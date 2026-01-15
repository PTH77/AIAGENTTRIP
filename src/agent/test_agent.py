"""
Skrypt do testowania agenta z TWOIMI danymi
"""
from agent import TravelAgent, UserPreferences


def test_agent():
    """
    Tutaj SAMEMU nadajesz dane i sprawdzasz skuteczność
    """
    # 1. Załaduj agenta
    agent = TravelAgent(model_path="models/model_tree.pkl")
    
    # 2. Zdefiniuj test cases - TUTAJ WPISUJESZ SWOJE DANE
    # 2. Zdefiniuj test cases - TUTAJ WPISUJESZ SWOJE DANE
    # UWAGA: Wartości muszą być jak w generate.py!
    # travel_comfort: 1-5
    # attractions_quality: 1-5
    # activities_match: 0-2
    # season_match: 0 lub 1
    # score: NIE PODAJESZ, oblicza się automatycznie!
    
    test_cases = [
        {
            "name": "Dobra oferta - wszystko wysoko",
            "prefs": UserPreferences(
                travel_comfort=5,  # 1-5
                attractions_quality=5,  # 1-5
                activities_match=2,  # 0-2
                season_match=1,  # 0 lub 1
                user_budget="high",
                trip_cost="low"
            )
        },
        {
            "name": "Zła oferta - niski budżet, wysoki koszt",
            "prefs": UserPreferences(
                travel_comfort=1,
                attractions_quality=1,
                activities_match=0,
                season_match=0,
                user_budget="low",
                trip_cost="high"
            )
        },
        {
            "name": "Średnia oferta - wszystko średnie",
            "prefs": UserPreferences(
                travel_comfort=3,
                attractions_quality=3,
                activities_match=1,
                season_match=1,
                user_budget="medium",
                trip_cost="medium"
            )
        },
        {
            "name": "Custom test 1 - TWOJE DANE",
            "prefs": UserPreferences(
                travel_comfort=4,
                attractions_quality=4,
                activities_match=2,
                season_match=1,
                user_budget="medium",
                trip_cost="low"
            )
        },
        # DODAJ WIĘCEJ TESTÓW TUTAJ:
        # {
        #     "name": "Mój test 2",
        #     "prefs": UserPreferences(...)
        # },
    ]
    
    # 3. Przetestuj każdy case
    results = []
    for test in test_cases:
        print(f"\n🧪 TEST: {test['name']}")
        decision = agent.decide(test['prefs'])
        agent.print_decision(decision)
        
        results.append({
            "name": test['name'],
            "accepted": decision.accepted,
            "probability": decision.probability
        })
    
    # 4. Podsumowanie
    print("\n📊 PODSUMOWANIE TESTÓW:")
    print("-" * 60)
    for r in results:
        status = "✅ PASS" if r["accepted"] else "❌ FAIL"
        print(f"{status} | {r['name']:40} | {r['probability']:.1%}")
    print("-" * 60)
    
    accepted_count = sum(1 for r in results if r["accepted"])
    print(f"\nSkuteczność: {accepted_count}/{len(results)} zaakceptowanych ({accepted_count/len(results):.1%})")


def test_single_case():
    """
    Test pojedynczego przypadku - szybkie sprawdzanie
    """
    agent = TravelAgent(model_path="models/model_tree.pkl")
    
    # ZMIEŃ TUTAJ WARTOŚCI ABY TESTOWAĆ:
    # PAMIĘTAJ O ZAKRESACH:
    # travel_comfort: 1-5
    # attractions_quality: 1-5
    # activities_match: 0-2
    # season_match: 0 lub 1
    
    prefs = UserPreferences(
        travel_comfort=5,
        attractions_quality=5,
        activities_match=2,
        season_match=1,
        user_budget="high",
        trip_cost="medium"
    )
    
    decision = agent.decide(prefs)
    agent.print_decision(decision)


if __name__ == "__main__":
    # Uruchom pełne testy
    test_agent()
    
    # LUB uruchom pojedynczy test:
    # test_single_case()