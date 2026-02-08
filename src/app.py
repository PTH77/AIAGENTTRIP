import streamlit as st
import requests
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent / "src" / "agent"))
from agent import TravelAgent, UserPreferences

PRESET_CITIES = {
    "Paris": {
        "total": 232,
        "quality": 5,
        "offers": ["culture", "food", "romance", "shopping", "history"]
    },
    "London": {
        "total": 215,
        "quality": 5,
        "offers": ["culture", "shopping", "nightlife", "history", "music"]
    },
    "Rome": {
        "total": 198,
        "quality": 4,
        "offers": ["culture", "history", "food", "romance"]
    },
    "Barcelona": {
        "total": 187,
        "quality": 4,
        "offers": ["culture", "beach", "nightlife", "food", "sport"]
    },
    "Amsterdam": {
        "total": 165,
        "quality": 4,
        "offers": ["culture", "nightlife", "family", "history"]
    },
    "Prague": {
        "total": 142,
        "quality": 4,
        "offers": ["culture", "romance", "history", "nightlife"]
    },
    "Vienna": {
        "total": 138,
        "quality": 4,
        "offers": ["culture", "history", "music", "food"]
    },
    "Berlin": {
        "total": 125,
        "quality": 4,
        "offers": ["culture", "nightlife", "history", "shopping"]
    },
    "Warsaw": {
        "total": 82,
        "quality": 3,
        "offers": ["culture", "history", "family", "food"]
    },
    "Lisbon": {
        "total": 95,
        "quality": 3,
        "offers": ["culture", "beach", "food", "nightlife"]
    },
    "Budapest": {
        "total": 88,
        "quality": 3,
        "offers": ["culture", "history", "spa", "nightlife"]
    },
    "Copenhagen": {
        "total": 76,
        "quality": 3,
        "offers": ["culture", "family", "design", "food"]
    },
    "Dublin": {
        "total": 65,
        "quality": 3,
        "offers": ["culture", "nightlife", "nature", "music"]
    },
    "Krakow": {
        "total": 45,
        "quality": 2,
        "offers": ["culture", "history", "food", "nightlife"]
    },
    "Porto": {
        "total": 38,
        "quality": 2,
        "offers": ["culture", "food", "beach", "history"]
    }
}

ALL_ACTIVITIES = [
    "culture", "history", "food", "beach", "nightlife", 
    "shopping", "nature", "family", "romance", "sport", 
    "music", "design", "spa"
]

def get_city_coordinates(city_name):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        response = requests.get(url, headers={'User-Agent': 'TravelAgent/1.0'}, timeout=10)
        data = response.json()
        
        if not data:
            return None
        
        return {
            'name': data[0].get('name', city_name),
            'lat': float(data[0]['lat']),
            'lon': float(data[0]['lon'])
        }
    except:
        return None

def get_attractions_overpass(lat, lon):
    try:
        query = f"""
        [out:json][timeout:25];
        (
          node["tourism"](around:5000,{lat},{lon});
          way["tourism"](around:5000,{lat},{lon});
        );
        out count;
        """
        
        url = "https://overpass-api.de/api/interpreter"
        response = requests.post(url, data={'data': query}, timeout=30)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        if 'elements' in data and data['elements']:
            tags = data['elements'][0].get('tags', {})
            total = int(tags.get('total', 0))
            
            if total >= 200:
                quality = 5
            elif total >= 100:
                quality = 4
            elif total >= 50:
                quality = 3
            elif total >= 20:
                quality = 2
            else:
                quality = 1
            
            return {'total': total, 'quality': quality}
        return None
    except:
        return None

def calculate_activities_match(city_offers, user_interests):
    if not user_interests:
        return 1
    
    common = set(city_offers) & set(user_interests)
    
    if len(common) >= 2:
        return 2
    elif len(common) >= 1:
        return 1
    else:
        return 0

st.set_page_config(page_title="Agent Turystyczny", layout="wide")
st.title("Agent Decyzyjny - Rekomendacja Podrozy")

st.sidebar.header("KROK 1: Twoje preferencje")

comfort = st.sidebar.slider("Komfort podrozy (1=basic, 5=luxury)", 1, 5, 3)
season = st.sidebar.selectbox("Dobry sezon?", ["Tak", "Nie"])
season_value = 1 if season == "Tak" else 0
budget = st.sidebar.selectbox("Twoj budzet", ["low", "medium", "high"])
cost = st.sidebar.selectbox("Akceptowalny koszt wycieczki", ["low", "medium", "high"])

st.sidebar.markdown("---")
st.sidebar.subheader("Co Cie interesuje?")

interests = st.sidebar.multiselect(
    "Wybierz swoje zainteresowania (min 1)",
    ALL_ACTIVITIES,
    default=["culture"]
)

st.sidebar.markdown("---")
st.sidebar.header("KROK 2: Wybierz miasto")

use_preset = st.sidebar.checkbox("Uzyj gotowej listy (polecane)", value=True)

if use_preset:
    city = st.sidebar.selectbox("Miasto", list(PRESET_CITIES.keys()))
    st.sidebar.info("Dane z cache - natychmiastowe wyniki")
else:
    city = st.sidebar.text_input("Wpisz nazwe miasta (po angielsku)", "Paris")
    st.sidebar.warning("Pobieranie z Overpass API - moze nie dzialac (rate limit)")

if st.sidebar.button("SPRAWDZ MIASTO", type="primary"):
    
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    if use_preset and city in PRESET_CITIES:
        preset = PRESET_CITIES[city]
        match = calculate_activities_match(preset["offers"], interests)
        
        st.session_state["result"] = {
            "city": city,
            "total": preset["total"],
            "quality": preset["quality"],
            "match": match,
            "offers": preset["offers"],
            "interests": list(interests),
            "common": list(set(preset["offers"]) & set(interests)),
            "comfort": comfort,
            "season": season_value,
            "budget": budget,
            "cost": cost,
            "source": "preset"
        }
        st.success(f"Zaladowano: {city}")
    else:
        with st.spinner("Szukam miasta..."):
            coords = get_city_coordinates(city)
            
            if not coords:
                st.error(f"Nie znaleziono: {city}")
            else:
                with st.spinner("Pobieram atrakcje (30 sek)..."):
                    time.sleep(2)
                    attractions = get_attractions_overpass(coords['lat'], coords['lon'])
                
                if not attractions:
                    st.error("Blad Overpass API - uzyj gotowej listy")
                else:
                    match = 1
                    
                    st.session_state["result"] = {
                        "city": coords['name'],
                        "total": attractions['total'],
                        "quality": attractions['quality'],
                        "match": match,
                        "offers": [],
                        "interests": list(interests),
                        "common": [],
                        "comfort": comfort,
                        "season": season_value,
                        "budget": budget,
                        "cost": cost,
                        "source": "api"
                    }
                    st.success(f"Pobrano: {coords['name']}")

if "result" in st.session_state:
    r = st.session_state["result"]
    
    st.subheader(f"Analiza: {r['city']}")
    
    if r['source'] == 'preset':
        st.caption(f"Miasto oferuje: {', '.join(r['offers'])}")
        st.caption(f"Twoje zainteresowania: {', '.join(r['interests'])}")
        if r['common']:
            st.caption(f"Wspolne: {', '.join(r['common'])}")
    else:
        st.caption(f"Zrodlo: Overpass API | Zainteresowania: {', '.join(r['interests'])}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Liczba atrakcji", r['total'])
    with col2:
        st.metric("Jakosc atrakcji", f"{r['quality']}/5")
    with col3:
        st.metric("Dopasowanie zainteresowan", f"{r['match']}/2")
    
    st.markdown("---")
    
    try:
        model_path = Path(__file__).parent / "models" / "model_tree.pkl"
        agent = TravelAgent(str(model_path))
        
        prefs = UserPreferences(
            travel_comfort=r['comfort'],
            attractions_quality=r['quality'],
            activities_match=r['match'],
            season_match=r['season'],
            user_budget=r['budget'],
            trip_cost=r['cost']
        )
        
        decision = agent.decide(prefs)
        score = prefs.compute_score()
        
        st.subheader("Wynik analizy")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("SCORE", f"{score}/10")
        with col2:
            st.metric("Pewnosc modelu", f"{decision.probability:.1%}")
        with col3:
            if decision.accepted:
                st.success("ZAAKCEPTOWANA")
            else:
                st.error("ODRZUCONA")
        
        st.info(decision.explanation)
        
        if decision.recommended_changes:
            st.subheader("Rekomendacje")
            for rec in decision.recommended_changes:
                st.write(f"- {rec}")
        
        with st.expander("Sciezka decyzyjna"):
            if decision.decision_path:
                for step in decision.decision_path:
                    symbol = "[+]" if step["passed"] else "[-]"
                    op = ">" if step["passed"] else "<="
                    st.text(f"{symbol} {step['feature']}: {step['value']:.2f} {op} {step['threshold']:.2f}")
    
    except Exception as e:
        st.error(f"Blad agenta: {e}")

else:
    st.info("Ustaw preferencje, wybierz miasto i kliknij SPRAWDZ MIASTO")

st.markdown("---")
st.caption("System rekomendacyjny | 15 miast preset + Overpass API | Praca inzynierska 2025")