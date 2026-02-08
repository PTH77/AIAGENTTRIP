from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from agent import TravelAgent, UserPreferences


def run_test():
    print("TEST AGENTA TURYSTYCZNEGO")
    
    try:
        model_path = Path(__file__).parent.parent.parent / "models" / "model_tree.pkl"
        agent = TravelAgent(str(model_path))
        print(f"Agent zaladowany\n")
    except Exception as e:
        print(f"BLAD: {e}")
        return
    
    test_cases = [
        ("IDEALNA", UserPreferences(5, 5, 2, 1, "high", "high"), True),
        ("DOBRA", UserPreferences(4, 4, 1, 1, "medium", "medium"), True),
        ("SREDNIA", UserPreferences(3, 3, 1, 1, "medium", "medium"), None),
        ("SLABA", UserPreferences(2, 2, 0, 0, "low", "high"), False),
        ("FATALNA", UserPreferences(1, 1, 0, 0, "low", "high"), False),
    ]
    
    results = []
    correct = 0
    accepted = 0
    rejected = 0
    
    for i, (name, prefs, expected) in enumerate(test_cases, 1):
        print(f"\nTEST {i}/5: {name}")
        
        score = prefs.compute_score()
        print(f"INPUT:")
        print(f"  travel_comfort: {prefs.travel_comfort}/5")
        print(f"  attractions_quality: {prefs.attractions_quality}/5")
        print(f"  activities_match: {prefs.activities_match}/2")
        print(f"  season_match: {'TAK' if prefs.season_match == 1 else 'NIE'}")
        print(f"  user_budget: {prefs.user_budget} | trip_cost: {prefs.trip_cost}")
        print(f"  SCORE: {score}/10")
        
        decision = agent.decide(prefs)
        
        if decision.accepted:
            status = "[+] ZAAKCEPTOWANA"
            accepted += 1
        else:
            status = "[-] ODRZUCONA"
            rejected += 1
        
        print(f"\n{status}")
        print(f"Pewnosc: {decision.probability:.1%}")
        
        if expected is not None:
            if expected == decision.accepted:
                print(f"[OK] ZGODNE")
                correct += 1
            else:
                print(f"[!] NIEZGODNE")
        
        if decision.recommended_changes:
            print(f"\nRekomendacje:")
            for rec in decision.recommended_changes:
                print(f"  {rec}")
        
        results.append({
            "name": name,
            "score": score,
            "accepted": decision.accepted,
            "probability": decision.probability,
        })
    
    print("\n\nPODSUMOWANIE")
    print(f"\nZaakceptowane: {accepted}/5 ({accepted/5*100:.0f}%)")
    print(f"Odrzucone: {rejected}/5 ({rejected/5*100:.0f}%)")
    
    tests_with_expected = [tc for tc in test_cases if tc[2] is not None]
    if tests_with_expected:
        accuracy = correct / len(tests_with_expected) * 100
        print(f"Dokladnosc: {correct}/{len(tests_with_expected)} ({accuracy:.0f}%)")
    
    scores = [r['score'] for r in results]
    print(f"\nScore MIN: {min(scores)}, MAX: {max(scores)}, SREDNIA: {sum(scores)/len(scores):.1f}")
    
    print(f"\n{'TEST':<15} {'SCORE':<8} {'WYNIK':<18} {'PEWNOSC'}")
    for r in results:
        result = "[+] ACCEPT" if r['accepted'] else "[-] REJECT"
        print(f"{r['name']:<15} {r['score']:<8} {result:<18} {r['probability']:.1%}")
    
    print("\nTEST ZAKONCZONY")


if __name__ == "__main__":
    run_test()