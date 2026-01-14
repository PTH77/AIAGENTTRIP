import requests

class OpenTripMapClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.opentripmap.com/0.1/en"

    def get_place_summary(self, lat: float, lon: float, radius: int = 5000):
        url = f"{self.base_url}/places/radius"
        params = {
            "radius": radius,
            "lon": lon,
            "lat": lat,
            "apikey": self.api_key,
            "limit": 50
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()["features"]

    def analyze_place(self, places):
        attractions_count = len(places)

        kinds = []
        for p in places:
            kinds.extend(p["properties"].get("kinds", "").split(","))

        unique_kinds = set(kinds)

        return {
            "attractions_quality": min(attractions_count / 50, 1.0),
            "activities_match": min(len(unique_kinds) / 10, 1.0),
            "score": min((attractions_count + len(unique_kinds)) / 60, 1.0)
        }
