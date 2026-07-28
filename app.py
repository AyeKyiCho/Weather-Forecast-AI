import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import json
import time
import os

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="🍁 Premium Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Load Configuration
# -----------------------------
@st.cache_data
def load_config():
    """Load configuration from config.json"""
    try:
        # Try to load from file
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    
    # Default config if file not found
    return {
        "app_name": "Premium Weather Dashboard",
        "default_city": "Toronto",
        "forecast_days": 7,
        "timezone": "America/Toronto",
        "api_url": "https://api.open-meteo.com/v1/forecast"
    }

@st.cache_data
def load_city_data():
    """Load city data"""
    try:
        if os.path.exists('data.json'):
            with open('data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('cities', {})
    except:
        pass
    
    # Fallback cities
    return {
        "Toronto": {"lat": 43.6532, "lon": -79.3832, "province": "ON", "population": "2.9M"},
        "Vancouver": {"lat": 49.2827, "lon": -123.1207, "province": "BC", "population": "0.7M"},
        "Montreal": {"lat": 45.5017, "lon": -73.5673, "province": "QC", "population": "1.8M"},
        "Calgary": {"lat": 51.0447, "lon": -114.0719, "province": "AB", "population": "1.3M"},
        "Edmonton": {"lat": 53.5461, "lon": -113.4938, "province": "AB", "population": "1.0M"},
        "Ottawa": {"lat": 45.4215, "lon": -75.6972, "province": "ON", "population": "1.0M"},
        "Halifax": {"lat": 44.6488, "lon": -63.5752, "province": "NS", "population": "0.4M"},
        "Winnipeg": {"lat": 49.8951, "lon": -97.1384, "province": "MB", "population": "0.8M"},
        "Quebec City": {"lat": 46.8033, "lon": -71.3687, "province": "QC", "population": "0.5M"},
        "Victoria": {"lat": 48.4284, "lon": -123.3656, "province": "BC", "population": "0.1M"}
    }

@st.cache_data
def load_weather_codes():
    """Load weather codes"""
    try:
        if os.path.exists('data.json'):
            with open('data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('weather_codes', {}), data.get('weather_emojis', {})
    except:
        pass
    
    # Fallback codes
    codes = {
        "0": "Clear Sky", "1": "Mainly Clear", "2": "Partly Cloudy", "3": "Overcast",
        "45": "Fog", "48": "Freezing Fog",
        "51": "Light Drizzle", "53": "Moderate Drizzle", "55": "Dense Drizzle",
        "61": "Light Rain", "63": "Moderate Rain", "65": "Heavy Rain",
        "71": "Light Snow", "73": "Moderate Snow", "75": "Heavy Snow",
        "80": "Rain Showers", "81": "Moderate Showers", "82": "Heavy Showers",
        "95": "Thunderstorm", "96": "Thunderstorm", "99": "Heavy Thunderstorm"
    }
    emojis = {
        "0": "☀️", "1": "🌤️", "2": "⛅", "3": "☁️",
        "45": "🌫️", "48": "🌫️",
        "51": "🌧️", "53": "🌧️", "55": "🌧️",
        "61": "🌧️", "63": "🌧️", "65": "🌧️",
        "71": "❄️", "73": "❄️", "75": "❄️",
        "80": "🌧️", "81": "🌧️", "82": "🌧️",
        "95": "⛈️", "96": "⛈️", "99": "⛈️"
    }
    return codes, emojis

# Load data
CONFIG = load_config()
CANADA_CITIES = load_city_data()
WEATHER_CODES, WEATHER_EMOJIS = load_weather_codes()

# -----------------------------
# CSS
# -----------------------------
def load_css():
    """Load CSS"""
    css = """
    <style>
        * { font-family: 'Inter', sans-serif; }
        .main-header {
            background: linear-gradient(135deg, #0d1b2a 0%, #1a3a5c 30%, #2196F3 70%, #00BCD4 100%);
            padding: 2.5rem 3rem;
            border-radius: 24px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 12px 48px rgba(33, 150, 243, 0.25);
            border-bottom: 4px solid #d84b20;
        }
        .main-header h1 {
            font-weight: 800;
            margin: 0;
            font-size: 2.8rem;
            background: linear-gradient(135deg, #ffffff, #90caf9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .badge-group {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 0.5rem;
        }
        .badge {
            display: inline-block;
            padding: 0.3rem 1.2rem;
            border-radius: 30px;
            font-weight: 700;
            font-size: 0.75rem;
            color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        .badge-canada { background: linear-gradient(135deg, #d84b20 0%, #e67e22 100%); }
        .badge-live { background: #4CAF50; animation: pulse-dot 1.5s ease-in-out infinite; }
        .badge-api { background: linear-gradient(135deg, #2196F3, #00BCD4); }
        .badge-premium { background: linear-gradient(135deg, #9b59b6, #8e44ad); }
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .weather-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 2rem 1.5rem;
            border-radius: 20px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            height: 100%;
            min-height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .weather-card:hover {
            transform: translateY(-6px) scale(1.02);
            box-shadow: 0 16px 48px rgba(33, 150, 243, 0.15);
        }
        .forecast-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            padding: 1.2rem 0.8rem;
            border-radius: 16px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(0, 0, 0, 0.04);
        }
        .forecast-card:hover {
            transform: translateY(-8px) scale(1.03);
            box-shadow: 0 12px 40px rgba(33, 150, 243, 0.12);
        }
        .forecast-card .day { font-weight: 700; font-size: 1.1rem; color: #0d1b2a; }
        .forecast-card .date { font-size: 0.7rem; color: #999; }
        .forecast-card .temp-high { font-size: 1.6rem; font-weight: 700; color: #2196F3; }
        .forecast-card .temp-low { font-size: 0.9rem; color: #999; }
        .city-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
            margin: 0.5rem 0;
        }
        .city-info-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255,255,255,0.05);
            padding: 0.5rem 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        .city-info-bar .city-name { font-size: 1.8rem; font-weight: 700; }
        .city-info-bar .city-details { display: flex; gap: 2rem; flex-wrap: wrap; }
        .city-info-bar .detail-item { color: #888; font-size: 0.9rem; }
        .metric-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        }
        .metric-card .metric-value { font-size: 1.5rem; font-weight: 700; color: #0d1b2a; }
        .metric-card .metric-label {
            font-size: 0.7rem;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 0.2rem;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

load_css()

# -----------------------------
# Initialize Session State
# -----------------------------
if 'city' not in st.session_state:
    st.session_state.city = CONFIG.get('default_city', 'Toronto')
if 'lat' not in st.session_state:
    st.session_state.lat = 43.6532
if 'lon' not in st.session_state:
    st.session_state.lon = -79.3832
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# -----------------------------
# Helper Functions
# -----------------------------
def search_city(query):
    if not query or not query.strip():
        return None
    query_lower = query.lower().strip()
    
    for city_name in CANADA_CITIES:
        if city_name.lower() == query_lower:
            return city_name
    
    for city_name in CANADA_CITIES:
        if query_lower in city_name.lower():
            return city_name
    
    return None

def get_city_coordinates(city_name):
    city_data = CANADA_CITIES.get(city_name)
    if city_data:
        return city_data["lat"], city_data["lon"], city_data.get("province", "")
    return None, None, None

def get_weather_code_emoji(code):
    return WEATHER_EMOJIS.get(str(code), "🌤️")

def get_weather_condition(code):
    return WEATHER_CODES.get(str(code), "Unknown")

# -----------------------------
# Weather API
# -----------------------------
def get_weather_openmeteo(lat, lon):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': [
                'temperature_2m', 'relative_humidity_2m', 'apparent_temperature',
                'precipitation', 'rain', 'snowfall',
                'weather_code', 'cloud_cover', 'pressure_msl',
                'wind_speed_10m', 'wind_direction_10m', 'wind_gusts_10m',
                'uv_index', 'is_day'
            ],
            'daily': [
                'weather_code', 'temperature_2m_max', 'temperature_2m_min',
                'precipitation_sum', 'wind_speed_10m_max', 'uv_index_max'
            ],
            'timezone': 'America/Toronto',
            'forecast_days': 7
        }
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"⚠️ API Error: {str(e)[:100]}")
        return None

# -----------------------------
# Main App
# -----------------------------
st.markdown("""
    <div class="main-header">
        <h1>🍁 Premium Weather Dashboard</h1>
        <p>Real-time weather, 7-day forecast, and interactive maps</p>
        <div class="badge-group">
            <span class="badge badge-canada">🇨🇦 Canada</span>
            <span class="badge badge-live">● LIVE</span>
            <span class="badge badge-api">📡 Open-Meteo</span>
            <span class="badge badge-premium">💎 Premium</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🍁 Weather Pro")
    
    city_input = st.text_input("🔍 Search City", placeholder="e.g., Toronto")
    
    if st.button("🔍 Search", use_container_width=True):
        if city_input:
            matched = search_city(city_input)
            if matched:
                lat, lon, prov = get_city_coordinates(matched)
                if lat:
                    st.session_state.city = matched
                    st.session_state.lat = lat
                    st.session_state.lon = lon
                    st.success(f"✅ Found: {matched}")
                    st.rerun()
            else:
                st.error("❌ City not found")
    
    st.caption(f"📍 Current: **{st.session_state.city}**")
    
    st.divider()
    st.markdown("### 📍 Popular Cities")
    
    popular = ["Toronto", "Vancouver", "Montreal", "Calgary", "Edmonton", "Ottawa"]
    for city_name in popular:
        if st.button(city_name, key=f"pop_{city_name}", use_container_width=True):
            city_data = CANADA_CITIES.get(city_name)
            if city_data:
                st.session_state.city = city_name
                st.session_state.lat = city_data["lat"]
                st.session_state.lon = city_data["lon"]
                st.rerun()

# Main content
city = st.session_state.city
lat = st.session_state.lat
lon = st.session_state.lon

if city and lat and lon:
    with st.spinner(f"Loading weather for {city}..."):
        data = get_weather_openmeteo(lat, lon)
        
        if data:
            current = data.get('current', {})
            daily = data.get('daily', {})
            
            if current and daily:
                # Current Weather
                st.markdown(f"### ☀️ Current Weather in {city}")
                
                temp = current.get('temperature_2m', 'N/A')
                feels_like = current.get('apparent_temperature', 'N/A')
                humidity = current.get('relative_humidity_2m', 'N/A')
                wind_speed = current.get('wind_speed_10m', 'N/A')
                weather_code = current.get('weather_code', 0)
                precipitation = current.get('precipitation', 'N/A')
                uv_index = current.get('uv_index', 'N/A')
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                        <div class="weather-card" style="background: linear-gradient(135deg, #1a3a5c 0%, #2196F3 100%); color: white; border: none;">
                            <div style="font-size: 3.5rem;">{get_weather_code_emoji(weather_code)}</div>
                            <div style="font-size: 3.2rem; font-weight: 800;">{temp}°C</div>
                            <div style="font-size: 1.1rem; font-weight: 600;">{get_weather_condition(weather_code)}</div>
                            <div style="font-size: 0.9rem; opacity: 0.7;">Feels like {feels_like}°C</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="weather-card">
                            <div style="font-size: 2.5rem;">💨</div>
                            <div style="font-size: 2.2rem; font-weight: 700;">{wind_speed}</div>
                            <div style="font-size: 0.9rem;">km/h</div>
                            <div style="font-size: 0.8rem; color: #888;">Wind Speed</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div class="weather-card">
                            <div style="font-size: 2.5rem;">💧</div>
                            <div style="font-size: 2.2rem; font-weight: 700;">{humidity}%</div>
                            <div style="font-size: 0.9rem;">Humidity</div>
                            <div style="font-size: 0.8rem; color: #888;">Precip: {precipitation}mm</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                        <div class="weather-card">
                            <div style="font-size: 2.5rem;">☀️</div>
                            <div style="font-size: 2.2rem; font-weight: 700;">{uv_index}</div>
                            <div style="font-size: 0.9rem;">UV Index</div>
                            <div style="font-size: 0.8rem; color: #888;">{'Day' if current.get('is_day', 1) else 'Night'}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Forecast
                st.markdown("---")
                st.markdown("### 📅 7-Day Forecast")
                
                dates = daily.get('time', [])
                temp_max = daily.get('temperature_2m_max', [])
                temp_min = daily.get('temperature_2m_min', [])
                weather_codes = daily.get('weather_code', [])
                precip_sum = daily.get('precipitation_sum', [])
                
                cols = st.columns(7)
                for i, col in enumerate(cols):
                    if i < len(dates):
                        with col:
                            date_obj = datetime.strptime(dates[i], '%Y-%m-%d')
                            st.markdown(f"""
                                <div class="forecast-card">
                                    <div class="day">{date_obj.strftime('%a')}</div>
                                    <div class="date">{date_obj.strftime('%b %d')}</div>
                                    <div style="font-size:2.5rem;">{get_weather_code_emoji(weather_codes[i])}</div>
                                    <div class="temp-high">{temp_max[i]}°C</div>
                                    <div class="temp-low">↓ {temp_min[i]}°C</div>
                                    <div style="font-size:0.7rem; color:#888;">💧 {precip_sum[i]}mm</div>
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Could not parse weather data")
        else:
            st.error("❌ Could not fetch weather data")
else:
    st.info("👈 Select a Canadian city to get started")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🍁 Premium Weather Dashboard")
with col2:
    st.caption("🌤️ Powered by Open-Meteo")
with col3:
    st.caption(f"📅 {datetime.now().strftime('%B %d, %Y')}")