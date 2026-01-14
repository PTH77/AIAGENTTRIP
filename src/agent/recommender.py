class Recommender:
    def __init__(self, model):
        self.model = model

    def suggest(self, decision_path):


        recommendations = []

        for step in decision_path:
            feature = step["feature"]
            value = step["value"]
            threshold = step["threshold"]
            direction = step["direction"]

            if feature == "user_budget_low" and value > threshold:
                recommendations.append(
                    "Zwiększ budżet lub wybierz tańszą ofertę"
                )

            elif feature == "trip_cost_high" and value > threshold:
                recommendations.append(
                    "Rozważ krótszą wycieczkę lub tańszy kierunek"
                )

            elif feature == "activities_match" and value <= threshold:
                recommendations.append(
                    "Wybierz ofertę lepiej dopasowaną do stylu podróży"
                )

            elif feature == "season_match" and value <= threshold:
                recommendations.append(
                    "Rozważ inny termin wyjazdu"
                )

        return list(dict.fromkeys(recommendations))
