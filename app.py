import streamlit as st
import requests
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src" / "agent"))
from agent import TravelAgent, UserPreferences

def get_city_coordinates(city_name):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        response = requests.get(url, headers={'User-Agent': 'TravelAgent/1.0'}, timeout=10)
        data = response.json()
        
        if not data:
            return None
        
        return {
            'name': data[0].get('name', city_name),
            'display_name': data[0].get('display_name', city_name),
            'lat': float(data[0]['lat']),
            'lon': float(data[0]['lon'])
        }
    except Exception as e:
        st.error(f"Blad geocoding: {e}")
        return None

def get_attractions_data(lat, lon, radius=5000):
    try:
        query = f"""
        [out:json];
        (
          node["tourism"](around:{radius},{lat},{lon});
          way["tourism"](around:{radius},{lat},{lon});
        );
        out count;
        """
        
        url = "https://overpass-api.de/api/interpreter"
        response = requests.post(url, data={'data': query}, timeout=30)
        data = response.json()
        
        if 'elements' in data and data['elements']:
            tags = data['elements'][0].get('tags', {})
            total = int(tags.get('total', 0))
            
            attractions_quality = min(int(total / 40) + 1, 5)
            activities_match = min(int(total / 80), 2)
            
            return {
                'total_attractions': total,
                'attractions_quality': attractions_quality,
                'activities_match': activities_match
            }
        return None
    except Exception as e:
        st.error(f"Blad pobierania atrakcji: {e}")
        return None

def find_alternative_cities(user_prefs, current_city_score):
    cities = [
        "Paris", "London", "Tokyo", "New York", "Barcelona", 
        "Rome", "Amsterdam", "Prague", "Vienna", "Berlin",
        "Dubai", "Singapore", "Lisbon", "Copenhagen", "Istanbul"
    ]
    
    alternatives = []
    for city in cities[:5]:
        coords = get_city_coordinates(city)
        if coords:
            attractions = get_attractions_data(coords['lat'], coords['lon'])
            if attractions:
                test_prefs = UserPreferences(
                    travel_comfort=user_prefs.travel_comfort,
                    attractions_quality=attractions['attractions_quality'],
                    activities_match=attractions['activities_match'],
                    season_match=user_prefs.season_match,
                    user_budget=user_prefs.user_budget,
                    trip_cost=user_prefs.trip_cost
                )
                score = test_prefs.compute_score()
                
                if score > current_city_score:
                    alternatives.append({
                        'city': city,
                        'score': score,
                        'attractions_quality': attractions['attractions_quality'],
                        'activities_match': attractions['activities_match']
                    })
    
    return sorted(alternatives, key=lambda x: x['score'], reverse=True)[:3]

st.set_page_config(page_title="Agent Turystyczny", layout="wide")

st.title("Agent Decyzyjny - Rekomendacja Podrozy")
st.markdown("System analizujacy czy destynacja spelnia Twoje wymagania na podstawie prawdziwych danych z OpenStreetMap")

st.sidebar.header("Krok 1: Twoje wymagania")

travel_comfort = st.sidebar.slider("Komfort podrozy", 1, 5, 3, 
    help="1=basic, 5=luxury")
season_match = st.sidebar.selectbox("Dobry sezon?", [1, 0], 
    format_func=lambda x: "Tak" if x == 1 else "Nie")
user_budget = st.sidebar.selectbox("Twoj budzet", ["low", "medium", "high"])
trip_cost = st.sidebar.selectbox("Akceptowalny koszt wycieczki", ["low", "medium", "high"])

st.sidebar.markdown("---")
st.sidebar.header("Krok 2: Wybierz miasto")

city_input = st.sidebar.text_input("Wpisz nazwe miasta (po angielsku)", "Paris")

if st.sidebar.button("Sprawdz to miasto", type="primary"):
    with st.spinner("Pobieram dane z OpenStreetMap..."):
        coords = get_city_coordinates(city_input)
        
        if not coords:
            st.error(f"Nie znaleziono miasta: {city_input}")
        else:
            st.success(f"Znaleziono: {coords['display_name']}")
            
            attractions = get_attractions_data(coords['lat'], coords['lon'])
            
            if not attractions:
                st.error("Nie udalo sie pobrac danych o atrakcjach")
            else:
                st.session_state['city_data'] = {
                    'coords': coords,
                    'attractions': attractions,
                    'user_prefs': {
                        'travel_comfort': travel_comfort,
                        'season_match': season_match,
                        'user_budget': user_budget,
                        'trip_cost': trip_cost
                    }
                }

if 'city_data' in st.session_state:
    data = st.session_state['city_data']
    coords = data['coords']
    attractions = data['attractions']
    user_prefs_dict = data['user_prefs']
    
    st.subheader(f"Analiza: {coords['name']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Liczba atrakcji", attractions['total_attractions'])
    with col2:
        st.metric("Jakosc atrakcji (obliczona)", f"{attractions['attractions_quality']}/5")
    with col3:
        st.metric("Dopasowanie aktywnosci", f"{attractions['activities_match']}/2")
    
    st.markdown("---")
    
    try:
        model_path = Path(__file__).parent / "models" / "model_tree.pkl"
        agent = TravelAgent(str(model_path))
        
        prefs = UserPreferences(
            travel_comfort=user_prefs_dict['travel_comfort'],
            attractions_quality=attractions['attractions_quality'],
            activities_match=attractions['activities_match'],
            season_match=user_prefs_dict['season_match'],
            user_budget=user_prefs_dict['user_budget'],
            trip_cost=user_prefs_dict['trip_cost']
        )
        
        decision = agent.decide(prefs)
        score = prefs.compute_score()
        
        st.subheader("Wynik analizy")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Score", f"{score}/10")
        with col2:
            st.metric("Pewnosc modelu", f"{decision.probability:.1%}")
        with col3:
            if decision.accepted:
                st.success("ZAAKCEPTOWANA")
            else:
                st.error("ODRZUCONA")
        
        st.info(decision.explanation)
        
        if decision.recommended_changes:
            st.subheader("Rekomendacje dla tego miasta")
            for rec in decision.recommended_changes:
                st.write(f"- {rec}")
        
        if not decision.accepted:
            st.markdown("---")
            st.subheader("Alternatywne miasta ktore moga lepiej pasowac")
            
            with st.spinner("Szukam lepszych opcji..."):
                alternatives = find_alternative_cities(prefs, score)
                
                if alternatives:
                    for alt in alternatives:
                        with st.expander(f"{alt['city']} (Score: {alt['score']}/10)"):
                            st.write(f"Jakosc atrakcji: {alt['attractions_quality']}/5")
                            st.write(f"Dopasowanie aktywnosci: {alt['activities_match']}/2")
                            st.write(f"Przewidywany score: {alt['score']}/10")
                else:
                    st.info("Nie znaleziono lepszych alternatyw w bazie")
        
        with st.expander("Sciezka decyzyjna"):
            if decision.decision_path:
                for step in decision.decision_path:
                    status = "[+]" if step["passed"] else "[-]"
                    operator = ">" if step["passed"] else "<="
                    st.text(f"{status} {step['feature']}: {step['value']:.2f} {operator} {step['threshold']:.2f}")
    
    except Exception as e:
        st.error(f"Blad agenta: {e}")

else:
    st.info("Ustaw swoje wymagania w panelu bocznym, potem wpisz miasto i kliknij 'Sprawdz to miasto'")

st.markdown("---")
st.caption("Dane z OpenStreetMap via Overpass API | System rekomendacyjny oparty na drzewie decyzyjnym")