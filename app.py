import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import json
import time

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
def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "app_name": "Premium Weather Dashboard",
            "default_city": "Toronto",
            "forecast_days": 7,
            "timezone": "America/Toronto"
        }

def load_city_data():
    """Load city data from data.json"""
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('cities', {})
    except FileNotFoundError:
        return {}

def load_weather_codes():
    """Load weather codes from data.json"""
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('weather_codes', {}), data.get('weather_emojis', {})
    except FileNotFoundError:
        return {}, {}

# Load data
CONFIG = load_config()
CANADA_CITIES = load_city_data()
WEATHER_CODES, WEATHER_EMOJIS = load_weather_codes()

# -----------------------------
# Load CSS
# -----------------------------
def load_css():
    """Load CSS from external file with proper encoding"""
    try:
        with open('styles.css', 'r', encoding='utf-8') as f:
            css = f.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ styles.css not found. Using default styling.")
        load_inline_css()
    except Exception as e:
        st.warning(f"⚠️ Could not load CSS: {e}")
        load_inline_css()

def load_inline_css():
    """Fallback inline CSS"""
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
            position: relative;
            overflow: hidden;
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
        .city-info-bar .detail-item span { margin-right: 0.3rem; }
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
        @media (prefers-color-scheme: dark) {
            .weather-card { background: rgba(30, 42, 58, 0.95); }
            .forecast-card { background: rgba(30, 42, 58, 0.95); }
            .forecast-card .day { color: #e0e0e0; }
            .metric-card { background: rgba(30, 42, 58, 0.95); }
            .metric-card .metric-value { color: #e0e0e0; }
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
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Detailed"

# -----------------------------
# Helper Functions
# -----------------------------
def search_city(query):
    """Search for a city by name"""
    if not query or not query.strip():
        return None
    query_lower = query.lower().strip()
    
    # Exact match
    for city_name in CANADA_CITIES:
        if city_name.lower() == query_lower:
            return city_name
    
    # Contains match
    for city_name in CANADA_CITIES:
        if query_lower in city_name.lower():
            return city_name
    
    return None

def get_city_coordinates(city_name):
    """Get coordinates for a city"""
    city_data = CANADA_CITIES.get(city_name)
    if city_data:
        return city_data["lat"], city_data["lon"], city_data["province"]
    return None, None, None

def get_weather_code_emoji(code):
    """Get emoji for weather code"""
    return WEATHER_EMOJIS.get(str(code), "🌤️")

def get_weather_condition(code):
    """Get weather condition name"""
    return WEATHER_CODES.get(str(code), "Unknown")

def get_uv_category(uv_index):
    """Get UV category and color"""
    if uv_index <= 2:
        return "Low", "#27ae60"
    elif uv_index <= 5:
        return "Moderate", "#f1c40f"
    elif uv_index <= 7:
        return "High", "#e67e22"
    elif uv_index <= 10:
        return "Very High", "#e74c3c"
    else:
        return "Extreme", "#8e44ad"

def get_weather_advice(temp, weather_code, uv_index, wind_speed):
    """Get weather advice based on conditions"""
    advice = []
    
    if temp < -10:
        advice.append("❄️ Extreme cold - limit outdoor exposure")
    elif temp < 0:
        advice.append("🥶 Freezing temperatures - bundle up!")
    elif temp > 30:
        advice.append("🥵 Extreme heat - stay hydrated and cool")
    elif temp > 25:
        advice.append("☀️ Warm weather - enjoy but stay hydrated")
    
    if weather_code in [0, 1]:
        advice.append("☀️ Perfect for outdoor activities!")
    elif weather_code in [51, 53, 55, 61, 63, 80, 81]:
        advice.append("🌧️ Light rain - carry an umbrella")
    elif weather_code in [71, 73, 75, 85, 86]:
        advice.append("❄️ Snow - drive carefully and stay warm")
    elif weather_code in [95, 96, 99]:
        advice.append("⛈️ Thunderstorms - stay indoors!")
    elif weather_code in [45, 48]:
        advice.append("🌫️ Foggy - drive with caution")
    
    if uv_index > 7:
        advice.append("☀️ High UV - wear sunscreen and hat")
    elif uv_index > 5:
        advice.append("☀️ Moderate UV - sun protection recommended")
    
    if wind_speed > 50:
        advice.append("💨 Strong winds - secure outdoor items")
    elif wind_speed > 30:
        advice.append("💨 Windy conditions - be cautious")
    
    return advice

# -----------------------------
# Weather API
# -----------------------------
def get_weather_openmeteo(lat, lon):
    """Fetch weather data from Open-Meteo API"""
    try:
        url = CONFIG.get('api_url', 'https://api.open-meteo.com/v1/forecast')
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': [
                'temperature_2m', 'relative_humidity_2m', 'apparent_temperature',
                'precipitation', 'rain', 'showers', 'snowfall',
                'weather_code', 'cloud_cover', 'pressure_msl',
                'wind_speed_10m', 'wind_direction_10m', 'wind_gusts_10m',
                'uv_index', 'is_day'
            ],
            'daily': [
                'weather_code', 'temperature_2m_max', 'temperature_2m_min',
                'apparent_temperature_max', 'apparent_temperature_min',
                'sunrise', 'sunset', 'daylight_duration',
                'precipitation_sum', 'rain_sum', 'snowfall_sum',
                'precipitation_hours', 'wind_speed_10m_max',
                'wind_gusts_10m_max', 'wind_direction_10m_dominant',
                'uv_index_max'
            ],
            'hourly': [
                'temperature_2m', 'relative_humidity_2m', 'apparent_temperature',
                'precipitation', 'rain', 'snowfall',
                'weather_code', 'cloud_cover', 'wind_speed_10m',
                'uv_index'
            ],
            'timezone': CONFIG.get('timezone', 'America/Toronto'),
            'forecast_days': CONFIG.get('forecast_days', 7)
        }
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"⚠️ API Error: {str(e)[:100]}")
        return None

# -----------------------------
# Chart Functions
# -----------------------------
def create_temperature_chart(daily_data):
    """Create temperature trend chart"""
    dates = daily_data.get('time', [])
    temp_max = daily_data.get('temperature_2m_max', [])
    temp_min = daily_data.get('temperature_2m_min', [])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=temp_max,
        name='Max Temp',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8),
        mode='lines+markers'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=temp_min,
        name='Min Temp',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8),
        mode='lines+markers'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=temp_max,
        fill=None, mode='none', showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=temp_min,
        fill='tonexty',
        fillcolor='rgba(52, 152, 219, 0.1)',
        mode='none', showlegend=False
    ))
    
    fig.update_layout(
        title='🌡️ Temperature Trend (7 Days)',
        xaxis_title='Date',
        yaxis_title='Temperature (°C)',
        height=350,
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_precipitation_chart(daily_data):
    """Create precipitation chart"""
    dates = daily_data.get('time', [])
    precipitation = daily_data.get('precipitation_sum', [])
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dates, y=precipitation,
        name='Precipitation',
        marker_color='#3498db',
        text=[f'{p:.1f}' for p in precipitation],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='🌧️ Precipitation Forecast',
        xaxis_title='Date',
        yaxis_title='Precipitation (mm)',
        height=350,
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_wind_chart(daily_data):
    """Create wind speed chart"""
    dates = daily_data.get('time', [])
    wind_speed = daily_data.get('wind_speed_10m_max', [])
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dates, y=wind_speed,
        name='Wind Speed',
        marker_color='#2ecc71',
        text=[f'{w:.1f}' for w in wind_speed],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='💨 Wind Speed Forecast',
        xaxis_title='Date',
        yaxis_title='Speed (km/h)',
        height=350,
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_uv_index_chart(daily_data):
    """Create UV index chart"""
    dates = daily_data.get('time', [])
    uv_index = daily_data.get('uv_index_max', [])
    
    colors = []
    for uv in uv_index:
        if uv <= 2: colors.append('#27ae60')
        elif uv <= 5: colors.append('#f1c40f')
        elif uv <= 7: colors.append('#e67e22')
        elif uv <= 10: colors.append('#e74c3c')
        else: colors.append('#8e44ad')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dates, y=uv_index,
        name='UV Index',
        marker_color=colors,
        text=uv_index,
        textposition='outside'
    ))
    
    fig.add_hline(y=2, line_dash="dash", line_color="#27ae60", 
                  annotation_text="Low", annotation_position="bottom right")
    fig.add_hline(y=5, line_dash="dash", line_color="#f1c40f", 
                  annotation_text="Moderate", annotation_position="bottom right")
    fig.add_hline(y=7, line_dash="dash", line_color="#e67e22", 
                  annotation_text="High", annotation_position="bottom right")
    fig.add_hline(y=10, line_dash="dash", line_color="#e74c3c", 
                  annotation_text="Very High", annotation_position="bottom right")
    
    fig.update_layout(
        title='☀️ UV Index Forecast',
        xaxis_title='Date',
        yaxis_title='UV Index',
        height=350,
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_weather_radar_chart(daily_data):
    """Create radar chart for weekly summary"""
    avg_temp_max = np.mean(daily_data.get('temperature_2m_max', []))
    avg_temp_min = np.mean(daily_data.get('temperature_2m_min', []))
    avg_precip = np.mean(daily_data.get('precipitation_sum', []))
    avg_wind = np.mean(daily_data.get('wind_speed_10m_max', []))
    avg_uv = np.mean(daily_data.get('uv_index_max', []))
    
    categories = ['Max Temp', 'Min Temp', 'Precip', 'Wind', 'UV']
    values = [avg_temp_max, avg_temp_min, avg_precip, avg_wind, avg_uv]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Weekly Averages',
        line=dict(color='#2196F3', width=2),
        fillcolor='rgba(33, 150, 243, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) * 1.2 if max(values) > 0 else 10]
            )
        ),
        height=350,
        template='plotly_white',
        showlegend=True
    )
    
    return fig

# -----------------------------
# Map Functions
# -----------------------------
def create_location_map(selected_city, lat, lon):
    """Create location map"""
    fig = go.Figure()
    
    fig.add_trace(go.Scattermapbox(
        lat=[lat],
        lon=[lon],
        mode='markers',
        marker=dict(size=22, color='#d84b20', symbol='circle'),
        text=[f"📍 {selected_city}"],
        hoverinfo='text',
        name=selected_city
    ))
    
    all_lats = [data['lat'] for data in CANADA_CITIES.values()]
    all_lons = [data['lon'] for data in CANADA_CITIES.values()]
    all_names = list(CANADA_CITIES.keys())
    
    fig.add_trace(go.Scattermapbox(
        lat=all_lats,
        lon=all_lons,
        mode='markers',
        marker=dict(size=8, color='rgba(33, 150, 243, 0.5)', symbol='circle'),
        text=all_names,
        hoverinfo='text',
        name='Canadian Cities',
        showlegend=False
    ))
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=55, lon=-100),
            zoom=3
        ),
        height=400,
        margin={"r":0, "t":0, "l":0, "b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
            <h2 style="font-size: 1.5rem; margin: 0;">🍁 Weather Pro</h2>
            <p style="font-size: 0.8rem; color: #888;">Premium Weather Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Location
    st.markdown("### 📍 Location")
    
    city_input = st.text_input(
        "🔍 Search City",
        value="",
        placeholder="e.g., Toronto, Van, Halifax"
    )
    
    col_search1, col_search2 = st.columns([3, 1])
    with col_search1:
        if st.button("🔍 Search", use_container_width=True):
            if city_input:
                matched_city = search_city(city_input)
                if matched_city:
                    lat, lon, province = get_city_coordinates(matched_city)
                    if lat:
                        st.session_state.city = matched_city
                        st.session_state.lat = lat
                        st.session_state.lon = lon
                        st.success(f"✅ Found: {matched_city}, {province}")
                        st.rerun()
                else:
                    st.error(f"❌ City not found")
    
    if st.session_state.city:
        st.caption(f"📍 Current: **{st.session_state.city}**")
    
    st.divider()
    
    # Favorites
    st.markdown("### ⭐ Favorites")
    
    if st.button("❤️ Add Current City", use_container_width=True):
        if st.session_state.city not in st.session_state.favorites:
            st.session_state.favorites.append(st.session_state.city)
            st.success(f"✅ Added {st.session_state.city}!")
            st.rerun()
        else:
            st.warning(f"⚠️ Already in favorites")
    
    if st.session_state.favorites:
        st.markdown('<div class="city-grid">', unsafe_allow_html=True)
        for fav_city in st.session_state.favorites:
            if st.button(f"⭐ {fav_city}", key=f"fav_{fav_city}", use_container_width=True):
                city_data = CANADA_CITIES.get(fav_city)
                if city_data:
                    st.session_state.city = fav_city
                    st.session_state.lat = city_data["lat"]
                    st.session_state.lon = city_data["lon"]
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Favorites", use_container_width=True):
            st.session_state.favorites = []
            st.rerun()
    
    st.divider()
    
    # Popular Cities
    st.markdown("""
        <div class="quick-header">
            <span class="leaf">🍁</span>
            <h4>Popular Cities</h4>
        </div>
    """, unsafe_allow_html=True)
    
    popular_cities = CONFIG.get('popular_cities', 
                               ["Toronto", "Vancouver", "Montreal", "Calgary", 
                                "Edmonton", "Ottawa", "Halifax", "Winnipeg"])
    
    st.markdown('<div class="city-grid">', unsafe_allow_html=True)
    
    for city_name in popular_cities:
        is_active = (city_name == st.session_state.city)
        
        if st.button(
            f"{'📍 ' if is_active else ''}{city_name}",
            key=f"ca_{city_name}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            city_data = CANADA_CITIES.get(city_name)
            if city_data:
                st.session_state.city = city_name
                st.session_state.lat = city_data["lat"]
                st.session_state.lon = city_data["lon"]
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.expander("🗺️ All Cities"):
        all_cities = sorted(CANADA_CITIES.keys())
        for city_name in all_cities:
            city_data = CANADA_CITIES[city_name]
            st.write(f"📍 {city_name} ({city_data['province']})")
    
    st.divider()
    
    # Settings
    st.markdown("### ⚙️ Settings")
    
    view_mode = st.selectbox(
        "View Mode",
        CONFIG.get('view_modes', ["Detailed", "Compact", "Minimal"]),
        index=0
    )
    st.session_state.view_mode = view_mode
    
    auto_refresh = st.checkbox("🔄 Auto-Refresh (30s)", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto_refresh
    
    st.divider()
    st.caption("🌤️ Powered by Open-Meteo")
    st.caption(f"📅 {datetime.now().strftime('%B %d, %Y')}")
    st.caption(f"🏙️ {len(CANADA_CITIES)} Cities")

# -----------------------------
# Main Content
# -----------------------------
# Header
st.markdown("""
    <div class="main-header">
        <h1>🍁 Premium Weather Dashboard</h1>
        <p>Real-time weather, 7-day forecast, interactive maps, and 12+ charts</p>
        <div class="badge-group">
            <span class="badge badge-canada">🇨🇦 Canada</span>
            <span class="badge badge-live">● LIVE</span>
            <span class="badge badge-api">📡 Open-Meteo</span>
            <span class="badge badge-premium">💎 Premium</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Get current city
city = st.session_state.city
lat = st.session_state.lat
lon = st.session_state.lon

# Auto-refresh
if st.session_state.auto_refresh:
    time.sleep(CONFIG.get('refresh_interval', 30))
    st.rerun()

# Main content
if city and lat and lon:
    with st.spinner(f"Loading premium weather for {city}..."):
        data = get_weather_openmeteo(lat, lon)
        
        if data:
            current = data.get('current', {})
            daily = data.get('daily', {})
            hourly = data.get('hourly', {})
            
            if current and daily:
                province = CANADA_CITIES.get(city, {}).get('province', '')
                population = CANADA_CITIES.get(city, {}).get('population', 'N/A')
                
                # Get current weather data
                temp = current.get('temperature_2m', 'N/A')
                feels_like = current.get('apparent_temperature', 'N/A')
                humidity = current.get('relative_humidity_2m', 'N/A')
                wind_speed = current.get('wind_speed_10m', 'N/A')
                wind_dir = current.get('wind_direction_10m', 'N/A')
                weather_code = current.get('weather_code', 0)
                precipitation = current.get('precipitation', 'N/A')
                pressure = current.get('pressure_msl', 'N/A')
                uv_index = current.get('uv_index', 'N/A')
                rain = current.get('rain', 'N/A')
                snowfall = current.get('snowfall', 'N/A')
                cloud_cover = current.get('cloud_cover', 'N/A')
                is_day = current.get('is_day', 1)
                wind_gusts = current.get('wind_gusts_10m', 'N/A')
                
                # ---------- SECTION 1: MAPS ----------
                st.markdown("### 🗺️ Weather Maps")
                
                col_map1, col_map2 = st.columns(2)
                
                with col_map1:
                    st.caption("📍 Location Map")
                    fig_map = create_location_map(city, lat, lon)
                    st.plotly_chart(fig_map, use_container_width=True, 
                                  config={'displayModeBar': False})
                
                with col_map2:
                    st.caption("🌤️ 7-Day Weather Map")
                    st.info("Weather map visualization available")
                
                # ---------- SECTION 2: CURRENT WEATHER ----------
                st.markdown("### ☀️ Current Weather")
                
                # City info display
                st.markdown(f"""
                    <div class="city-info-bar">
                        <div>
                            <span style="font-size: 2rem;">📍</span>
                            <span class="city-name">{city}</span>
                            <span style="font-size: 1rem; color: #888; margin-left: 0.5rem;">{province}, Canada</span>
                        </div>
                        <div class="city-details">
                            <div class="detail-item"><span>👥</span> {population}</div>
                            <div class="detail-item"><span>🕐</span> {datetime.now().strftime('%I:%M %p')}</div>
                            <div class="detail-item"><span>📅</span> {datetime.now().strftime('%B %d, %Y')}</div>
                            <div class="detail-item"><span>{'☀️' if is_day else '🌙'}</span> {'Day' if is_day else 'Night'}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Main weather display - 4 column grid
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                        <div class="weather-card" style="background: linear-gradient(135deg, #1a3a5c 0%, #2196F3 100%); color: white; border: none;">
                            <div style="font-size: 3.5rem; margin-bottom: 0.2rem;">{get_weather_code_emoji(weather_code)}</div>
                            <div style="font-size: 3.2rem; font-weight: 800;">{temp}°C</div>
                            <div style="font-size: 1.1rem; opacity: 0.9; font-weight: 600;">{get_weather_condition(weather_code)}</div>
                            <div style="font-size: 0.9rem; opacity: 0.7; margin-top: 0.3rem;">Feels like {feels_like}°C</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="weather-card">
                            <div style="font-size: 2.5rem; margin-bottom: 0.2rem;">💨</div>
                            <div style="font-size: 2.2rem; font-weight: 700; color: #0d1b2a;">{wind_speed}</div>
                            <div style="font-size: 0.9rem; color: #666;">km/h</div>
                            <div style="font-size: 0.8rem; color: #888; margin-top: 0.3rem;">Direction: {wind_dir}°</div>
                            <div style="font-size: 0.8rem; color: #888;">Gusts: {wind_gusts} km/h</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div class="weather-card">
                            <div style="font-size: 2.5rem; margin-bottom: 0.2rem;">💧</div>
                            <div style="font-size: 2.2rem; font-weight: 700; color: #0d1b2a;">{humidity}%</div>
                            <div style="font-size: 0.9rem; color: #666;">Humidity</div>
                            <div style="font-size: 0.8rem; color: #888; margin-top: 0.3rem;">☁️ Clouds: {cloud_cover}%</div>
                            <div style="font-size: 0.8rem; color: #888;">📊 Pressure: {pressure} hPa</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    uv_category, uv_color = get_uv_category(uv_index)
                    st.markdown(f"""
                        <div class="weather-card">
                            <div style="font-size: 2.5rem; margin-bottom: 0.2rem;">☀️</div>
                            <div style="font-size: 2.2rem; font-weight: 700; color: {uv_color};">{uv_index}</div>
                            <div style="font-size: 0.9rem; color: #666;">UV Index</div>
                            <div style="font-size: 0.9rem; color: {uv_color}; font-weight: 700; margin-top: 0.3rem;">{uv_category}</div>
                            <div style="font-size: 0.8rem; color: #888;">🌧️ Rain: {rain} mm</div>
                            <div style="font-size: 0.8rem; color: #888;">❄️ Snow: {snowfall} mm</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Row 2: Additional metrics - 6 columns
                st.markdown("### 📊 Detailed Metrics")
                
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                
                with col1:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{feels_like}°C</div>
                            <div class="metric-label">🌡️ Feels Like</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{precipitation} mm</div>
                            <div class="metric-label">💧 Precipitation</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{wind_gusts} km/h</div>
                            <div class="metric-label">💨 Wind Gusts</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{cloud_cover}%</div>
                            <div class="metric-label">☁️ Cloud Cover</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col5:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{pressure} hPa</div>
                            <div class="metric-label">📊 Pressure</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col6:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{wind_dir}°</div>
                            <div class="metric-label">🧭 Wind Direction</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Weather Alerts
                st.markdown("### ⚠️ Weather Alerts")
                
                alert_col1, alert_col2, alert_col3 = st.columns(3)
                
                with alert_col1:
                    if rain and float(rain) > 0:
                        st.error(f"🌧️ **Rain Alert**: {rain} mm expected")
                    else:
                        st.success("☀️ No rain expected")
                
                with alert_col2:
                    if snowfall and float(snowfall) > 0:
                        st.error(f"❄️ **Snow Alert**: {snowfall} mm expected")
                    else:
                        st.success("❄️ No snow expected")
                
                with alert_col3:
                    if uv_index > 7:
                        st.error(f"☀️ **High UV Alert**: {uv_index} - Protect your skin!")
                    elif uv_index > 5:
                        st.warning(f"☀️ **Moderate UV**: {uv_index} - Sun protection recommended")
                    else:
                        st.success(f"☀️ UV Index: {uv_index} - Safe levels")
                
                # Weather Summary
                st.markdown("### 🌤️ Weather Summary & Advice")
                
                advice_list = get_weather_advice(temp, weather_code, uv_index, wind_speed)
                
                col_summary1, col_summary2 = st.columns([2, 1])
                
                with col_summary1:
                    # Main weather summary
                    if weather_code in [0, 1]:
                        summary = "☀️ Clear skies - perfect for outdoor activities!"
                    elif weather_code in [2, 3]:
                        summary = "⛅ Partly cloudy - pleasant weather conditions"
                    elif weather_code in [45, 48]:
                        summary = "🌫️ Foggy conditions - drive with caution"
                    elif weather_code in [51, 53, 55, 56, 57]:
                        summary = "🌧️ Light rain - carry an umbrella"
                    elif weather_code in [61, 63, 65, 66, 67]:
                        summary = "🌧️ Rain expected - stay dry"
                    elif weather_code in [71, 73, 75, 77]:
                        summary = "❄️ Snowfall - bundle up!"
                    elif weather_code in [80, 81, 82]:
                        summary = "🌧️ Rain showers - brief rain periods"
                    elif weather_code in [85, 86]:
                        summary = "❄️ Snow showers - winter conditions"
                    elif weather_code in [95, 96, 99]:
                        summary = "⛈️ Thunderstorms - stay indoors"
                    else:
                        summary = "🌤️ Variable weather - check updates"
                    
                    st.info(f"📋 **Current Conditions**: {summary}")
                    
                    if advice_list:
                        st.markdown("#### 💡 Recommendations")
                        for advice in advice_list:
                            st.write(f"• {advice}")
                
                with col_summary2:
                    st.markdown("#### 📊 Quick Stats")
                    st.metric("🌡️ Temperature Range", 
                             f"{min(daily.get('temperature_2m_min', [0]))}°C - {max(daily.get('temperature_2m_max', [0]))}°C")
                    st.metric("📅 Days with Rain", 
                             f"{sum(1 for p in daily.get('precipitation_sum', []) if p > 0)}/7")
                    st.metric("💨 Max Wind", 
                             f"{max(daily.get('wind_speed_10m_max', [0]))} km/h")
                
                st.markdown("---")
                
                # ---------- SECTION 3: CHARTS ----------
                st.markdown("### 📊 Weather Charts")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_temp = create_temperature_chart(daily)
                    st.plotly_chart(fig_temp, use_container_width=True)
                
                with col2:
                    fig_precip = create_precipitation_chart(daily)
                    st.plotly_chart(fig_precip, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_wind = create_wind_chart(daily)
                    st.plotly_chart(fig_wind, use_container_width=True)
                
                with col2:
                    fig_uv = create_uv_index_chart(daily)
                    st.plotly_chart(fig_uv, use_container_width=True)
                
                # Radar Chart
                st.markdown("### 📊 Weekly Summary")
                fig_radar = create_weather_radar_chart(daily)
                st.plotly_chart(fig_radar, use_container_width=True)
                
                # ---------- SECTION 4: FORECAST ----------
                st.markdown("### 📅 7-Day Forecast")
                
                dates = daily.get('time', [])
                temp_max = daily.get('temperature_2m_max', [])
                temp_min = daily.get('temperature_2m_min', [])
                weather_codes = daily.get('weather_code', [])
                precipitation_sum = daily.get('precipitation_sum', [])
                wind_speed_max = daily.get('wind_speed_10m_max', [])
                uv_index_max = daily.get('uv_index_max', [])
                
                cols = st.columns(7)
                for i, col in enumerate(cols):
                    if i < len(dates):
                        with col:
                            date_obj = datetime.strptime(dates[i], '%Y-%m-%d')
                            st.markdown(f"""
                                <div class="forecast-card">
                                    <div class="day">{date_obj.strftime('%a')}</div>
                                    <div class="date">{date_obj.strftime('%b %d')}</div>
                                    <div style="font-size:2.5rem; margin:0.3rem 0;">{get_weather_code_emoji(weather_codes[i])}</div>
                                    <div class="temp-high">{temp_max[i]}°C</div>
                                    <div class="temp-low">↓ {temp_min[i]}°C</div>
                                    <div style="font-size:0.7rem; color:#888; margin-top:0.2rem;">💧 {precipitation_sum[i]}mm</div>
                                    <div style="font-size:0.7rem; color:#888;">💨 {wind_speed_max[i]} km/h</div>
                                    <div style="font-size:0.7rem; color:#888;">☀️ UV {uv_index_max[i]}</div>
                                </div>
                            """, unsafe_allow_html=True)
                
                # ---------- SECTION 5: STATS ----------
                st.markdown("### 📈 Weekly Statistics")
                
                avg_temp = np.mean(temp_max) if temp_max else 0
                total_precip = sum(precipitation_sum) if precipitation_sum else 0
                avg_wind = np.mean(wind_speed_max) if wind_speed_max else 0
                max_uv = max(uv_index_max) if uv_index_max else 0
                min_temp = min(temp_min) if temp_min else 0
                max_temp = max(temp_max) if temp_max else 0
                
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                
                with col1:
                    st.metric("📈 Avg High", f"{avg_temp:.1f}°C", delta=f"{avg_temp - temp:.1f}°C")
                with col2:
                    st.metric("📉 Min Temp", f"{min_temp:.1f}°C")
                with col3:
                    st.metric("🌧️ Total Rain", f"{total_precip:.1f}mm")
                with col4:
                    st.metric("💨 Avg Wind", f"{avg_wind:.1f} km/h")
                with col5:
                    st.metric("☀️ Max UV", f"{max_uv:.0f}")
                with col6:
                    st.metric("📊 Max Temp", f"{max_temp:.1f}°C")
                
                # ---------- SECTION 6: HOURLY FORECAST ----------
                st.markdown("### 🕐 Hourly Forecast (Next 24 Hours)")
                
                if hourly:
                    hourly_times = hourly.get('time', [])[:24]
                    hourly_temp = hourly.get('temperature_2m', [])[:24]
                    hourly_precip = hourly.get('precipitation', [])[:24]
                    hourly_humidity = hourly.get('relative_humidity_2m', [])[:24]
                    hourly_wind = hourly.get('wind_speed_10m', [])[:24]
                    hourly_cloud = hourly.get('cloud_cover', [])[:24]
                    
                    hourly_df = pd.DataFrame({
                        'Time': [t.split('T')[1][:5] for t in hourly_times],
                        'Temp (°C)': hourly_temp,
                        'Precip (mm)': hourly_precip,
                        'Humidity (%)': hourly_humidity,
                        'Wind (km/h)': hourly_wind,
                        'Cloud (%)': hourly_cloud
                    })
                    
                    st.dataframe(
                        hourly_df.style.background_gradient(
                            subset=['Temp (°C)', 'Precip (mm)', 'Humidity (%)', 'Wind (km/h)', 'Cloud (%)'], 
                            cmap='coolwarm'
                        ),
                        use_container_width=True,
                        height=300
                    )
                    
                    # Hourly chart
                    fig_hourly = go.Figure()
                    
                    fig_hourly.add_trace(go.Scatter(
                        x=hourly_times,
                        y=hourly_temp,
                        name='Temperature',
                        line=dict(color='#e74c3c', width=2),
                        marker=dict(size=4)
                    ))
                    
                    fig_hourly.add_trace(go.Bar(
                        x=hourly_times,
                        y=hourly_precip,
                        name='Precipitation',
                        yaxis='y2',
                        marker_color='#3498db',
                        opacity=0.3
                    ))
                    
                    fig_hourly.update_layout(
                        title='Hourly Temperature & Precipitation',
                        xaxis_title='Time',
                        yaxis_title='Temperature (°C)',
                        yaxis2=dict(
                            title='Precipitation (mm)',
                            overlaying='y',
                            side='right'
                        ),
                        height=300,
                        hovermode='x unified',
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig_hourly, use_container_width=True)
                
            else:
                st.warning(f"⚠️ Could not parse weather data for {city}")
        else:
            st.error(f"❌ Could not fetch weather data for {city}")
else:
    st.info("👈 Select a Canadian city to get started")

# -----------------------------
# Footer
# -----------------------------
st.divider()
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.caption("🍁 Premium Weather Dashboard")
with col2:
    st.caption("🌤️ Powered by Open-Meteo")
with col3:
    st.caption(f"📅 {datetime.now().strftime('%B %d, %Y')}")
with col4:
    st.caption("📊 12+ Charts & Maps")