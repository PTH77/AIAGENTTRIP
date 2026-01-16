import streamlit as st
import requests
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src" / "agent"))
from src.agent import TravelAgent, UserPreferences

API_KEY = "5ae2e3f221c38a28845f05b6b07d1f6a686641a43c8cef2d7ed1ae7b"

def get_place_data(city_name):
    try:
        geocode_url = f"https://api.opentripmap.com/0.1/en/places/geoname?name={city_name}&apikey={API_KEY}"
        geo_response = requests.get(geocode_url, timeout=10)
        geo_data = geo_response.json()
        
        if not geo_data or 'lat' not in geo_data:
            return None
        
        lat = geo_data['lat']
        lon = geo_data['lon']
        
        places_url = f"https://api.opentripmap.com/0.1/en/places/radius"
        params = {
            "radius": 5000,
            "lon": lon,
            "lat": lat,
            "apikey": API_KEY,
            "limit": 50
        }
        places_response = requests.get(places_url, params=params, timeout=10)
        places = places_response.json()
        
        if not places or 'features' not in places:
            return None
            
        features = places['features']
        
        kinds = []
        for feature in features:
            props = feature.get('properties', {})
            kind_str = props.get('kinds', '')
            if kind_str:
                kinds.extend(kind_str.split(','))
        
        unique_kinds = len(set(kinds))
        attractions_count = len(features)
        
        attractions_quality = min(int(attractions_count / 10) + 1, 5)
        activities_match = min(int(unique_kinds / 5), 2)
        
        return {
            'city': geo_data.get('name', city_name),
            'attractions_count': attractions_count,
            'unique_kinds': unique_kinds,
            'attractions_quality': attractions_quality,
            'activities_match': activities_match
        }
    except Exception as e:
        st.error(f"Blad pobierania danych: {e}")
        return None

st.set_page_config(page_title="Agent Turystyczny", page_icon="", layout="wide")

st.title("Agent Decyzyjny - Rekomendacja Podrozy")
st.markdown("System oparty na modelu drzewa decyzyjnego analizujacy czy oferta turystyczna spelnia Twoje wymagania")

st.sidebar.header("Wybierz destynacje")
city_input = st.sidebar.text_input("Wpisz nazwe miasta", "Warsaw")

if st.sidebar.button("Pobierz dane o miescie"):
    with st.spinner("Pobieram dane z OpenTripMap..."):
        place_data = get_place_data(city_input)
        if place_data:
            st.session_state['place_data'] = place_data
            st.sidebar.success(f"Pobrano dane dla: {place_data['city']}")
        else:
            st.sidebar.error("Nie znaleziono miasta lub brak danych")

if 'place_data' in st.session_state:
    place_data = st.session_state['place_data']
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Dane z API")
    st.sidebar.metric("Liczba atrakcji", place_data['attractions_count'])
    st.sidebar.metric("Roznorodnosc", place_data['unique_kinds'])
    st.sidebar.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parametry z API")
        attractions_quality = st.slider(
            "Jakosc atrakcji", 
            1, 5, 
            place_data['attractions_quality'],
            help="Obliczone na podstawie liczby atrakcji"
        )
        activities_match = st.slider(
            "Dopasowanie aktywnosci", 
            0, 2, 
            place_data['activities_match'],
            help="Obliczone na podstawie roznorodnosci atrakcji"
        )
    
    with col2:
        st.subheader("Twoje preferencje")
        travel_comfort = st.slider("Komfort podrozy", 1, 5, 3)
        season_match = st.selectbox("Dobry sezon?", [1, 0], format_func=lambda x: "Tak" if x == 1 else "Nie")
        user_budget = st.selectbox("Twoj budzet", ["low", "medium", "high"])
        trip_cost = st.selectbox("Koszt wycieczki", ["low", "medium", "high"])
    
    if st.button("Sprawdz oferte", type="primary"):
        try:
            model_path = Path(__file__).parent / "models" / "model_tree.pkl"
            agent = TravelAgent(str(model_path))
            
            prefs = UserPreferences(
                travel_comfort=travel_comfort,
                attractions_quality=attractions_quality,
                activities_match=activities_match,
                season_match=season_match,
                user_budget=user_budget,
                trip_cost=trip_cost
            )
            
            decision = agent.decide(prefs)
            
            st.markdown("---")
            st.subheader("Wynik analizy")
            
            score = prefs.compute_score()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{score}/10")
            with col2:
                st.metric("Pewnosc", f"{decision.probability:.1%}")
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
            
            if decision.decision_path:
                with st.expander("Sciezka decyzyjna"):
                    for step in decision.decision_path:
                        status = "[+]" if step["passed"] else "[-]"
                        operator = ">" if step["passed"] else "<="
                        st.text(f"{status} {step['feature']}: {step['value']:.2f} {operator} {step['threshold']:.2f}")
        
        except Exception as e:
            st.error(f"Blad agenta: {e}")
else:
    st.info("Wpisz nazwe miasta w panelu bocznym i kliknij 'Pobierz dane o miescie'")
    
st.markdown("---")
st.caption("System rekomendacyjny oparty na drzewie decyzyjnym | Praca inzynierska 2025")