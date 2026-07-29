import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import re
import time
import base64

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
# Load CSS
# -----------------------------
def load_css():
    try:
        with open('styles.css', 'r', encoding='utf-8') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback: use inline CSS if file not found
        st.markdown("""
        <style>
            .main-header {
                background: linear-gradient(135deg, #0d1b2a 0%, #1a3a5c 30%, #2196F3 70%, #00BCD4 100%);
                padding: 2rem 2.5rem;
                border-radius: 24px;
                color: white;
                margin-bottom: 2rem;
            }
            .badge-group {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
                margin-top: 0.5rem;
            }
            .badge {
                display: inline-block;
                padding: 0.25rem 1rem;
                border-radius: 30px;
                font-weight: 700;
                font-size: 0.7rem;
                color: white;
            }
            .badge-canada { background: #d84b20; }
            .badge-live { background: #4CAF50; }
            .badge-api { background: #2196F3; }
            .badge-premium { background: #9b59b6; }
            .weather-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 1rem;
                margin-bottom: 1rem;
            }
            .weather-card {
                background: rgba(255,255,255,0.95);
                padding: 1.5rem 1rem;
                border-radius: 20px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.06);
                min-height: 140px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .weather-card .value-large {
                font-size: 3.5rem;
                font-weight: 800;
            }
            .weather-card .value {
                font-size: 2.2rem;
                font-weight: 800;
            }
            .weather-card .label {
                font-size: 0.7rem;
                color: #888;
                text-transform: uppercase;
                letter-spacing: 1.5px;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(6, 1fr);
                gap: 0.8rem;
                margin: 0.5rem 0 1rem 0;
            }
            .stat-card {
                background: rgba(255,255,255,0.9);
                padding: 1rem 0.5rem;
                border-radius: 14px;
                text-align: center;
                border-left: 4px solid #2196F3;
            }
            .stat-card .value {
                font-size: 1.4rem;
                font-weight: 700;
                color: #0d1b2a;
            }
            .stat-card .label {
                font-size: 0.65rem;
                color: #999;
                text-transform: uppercase;
            }
            .forecast-grid {
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 0.8rem;
                margin: 1rem 0;
            }
            .forecast-card {
                background: rgba(255,255,255,0.9);
                padding: 1rem 0.5rem;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            }
            .forecast-card .day {
                font-weight: 700;
                font-size: 1rem;
            }
            .forecast-card .temp-high {
                font-size: 1.4rem;
                font-weight: 700;
                color: #2196F3;
            }
            .city-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 0.5rem;
                margin: 0.5rem 0;
            }
            .sun-info {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
                padding: 1rem;
                background: rgba(255,255,255,0.9);
                border-radius: 16px;
                text-align: center;
            }
            .sun-info .value {
                font-size: 1.2rem;
                font-weight: 700;
                color: #0d1b2a;
            }
            @media (max-width: 1200px) {
                .weather-grid { grid-template-columns: repeat(2, 1fr); }
                .stats-grid { grid-template-columns: repeat(3, 1fr); }
                .forecast-grid { grid-template-columns: repeat(4, 1fr); }
            }
            @media (max-width: 768px) {
                .weather-grid { grid-template-columns: repeat(2, 1fr); }
                .stats-grid { grid-template-columns: repeat(3, 1fr); }
                .forecast-grid { grid-template-columns: repeat(3, 1fr); }
            }
            @keyframes pulse-dot {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .badge-live { animation: pulse-dot 1.5s ease-in-out infinite; }
        </style>
        """, unsafe_allow_html=True)

load_css()

# -----------------------------
# Initialize Session State
# -----------------------------
if 'city' not in st.session_state:
    st.session_state.city = "Toronto"
if 'lat' not in st.session_state:
    st.session_state.lat = 43.6532
if 'lon' not in st.session_state:
    st.session_state.lon = -79.3832
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'theme' not in st.session_state:
    st.session_state.theme = "light"
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Detailed"
if 'weather_history' not in st.session_state:
    st.session_state.weather_history = []

# -----------------------------
# City Database
# -----------------------------
CANADA_CITIES = {
    "Toronto": {"lat": 43.6532, "lon": -79.3832, "province": "ON", "population": "2.9M"},
    "Vancouver": {"lat": 49.2827, "lon": -123.1207, "province": "BC", "population": "0.7M"},
    "Montreal": {"lat": 45.5017, "lon": -73.5673, "province": "QC", "population": "1.8M"},
    "Calgary": {"lat": 51.0447, "lon": -114.0719, "province": "AB", "population": "1.3M"},
    "Edmonton": {"lat": 53.5461, "lon": -113.4938, "province": "AB", "population": "1.0M"},
    "Ottawa": {"lat": 45.4215, "lon": -75.6972, "province": "ON", "population": "1.0M"},
    "Halifax": {"lat": 44.6488, "lon": -63.5752, "province": "NS", "population": "0.4M"},
    "Winnipeg": {"lat": 49.8951, "lon": -97.1384, "province": "MB", "population": "0.8M"},
    "Quebec City": {"lat": 46.8033, "lon": -71.3687, "province": "QC", "population": "0.5M"},
    "Victoria": {"lat": 48.4284, "lon": -123.3656, "province": "BC", "population": "0.1M"},
    "St. John's": {"lat": 47.5615, "lon": -52.7126, "province": "NL", "population": "0.1M"},
    "Yellowknife": {"lat": 62.4540, "lon": -114.3718, "province": "NT", "population": "0.02M"},
    "Iqaluit": {"lat": 63.7467, "lon": -68.5170, "province": "NU", "population": "0.007M"},
    "Whitehorse": {"lat": 60.7212, "lon": -135.0568, "province": "YT", "population": "0.03M"},
    "Kelowna": {"lat": 49.8879, "lon": -119.4962, "province": "BC", "population": "0.2M"},
    "Kingston": {"lat": 44.2312, "lon": -76.4810, "province": "ON", "population": "0.1M"},
    "Niagara Falls": {"lat": 43.0896, "lon": -79.0849, "province": "ON", "population": "0.09M"},
    "Thunder Bay": {"lat": 48.3809, "lon": -89.2477, "province": "ON", "population": "0.1M"},
    "Sherbrooke": {"lat": 45.4049, "lon": -71.8928, "province": "QC", "population": "0.2M"},
    "Moncton": {"lat": 46.0878, "lon": -64.7782, "province": "NB", "population": "0.08M"},
    "Charlottetown": {"lat": 46.2382, "lon": -63.1311, "province": "PE", "population": "0.04M"},
    "Regina": {"lat": 50.4452, "lon": -104.6189, "province": "SK", "population": "0.2M"},
    "Saskatoon": {"lat": 52.1579, "lon": -106.6702, "province": "SK", "population": "0.3M"},
}

# -----------------------------
# Search & Helper Functions
# -----------------------------
def search_city(query):
    if not query or not query.strip():
        return None
    query_lower = query.lower().strip()
    
    # Exact match
    for city_name in CANADA_CITIES:
        if city_name.lower() == query_lower:
            return city_name
    
    # Contains match
    matches = []
    for city_name in CANADA_CITIES:
        if query_lower in city_name.lower():
            matches.append(city_name)
    if matches:
        return matches[0]
    
    # Starts with match
    for city_name in CANADA_CITIES:
        if city_name.lower().startswith(query_lower):
            return city_name
    
    return None

def get_city_coordinates(city_name):
    city_data = CANADA_CITIES.get(city_name)
    if city_data:
        return city_data["lat"], city_data["lon"], city_data["province"]
    return None, None, None

def format_time(time_str):
    try:
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return dt.strftime('%I:%M %p')
    except:
        return time_str

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
# Weather Code Helpers
# -----------------------------
def get_weather_code_emoji(code):
    weather_codes = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️",
        51: "🌧️", 53: "🌧️", 55: "🌧️", 56: "🌧️", 57: "🌧️",
        61: "🌧️", 63: "🌧️", 65: "🌧️", 66: "🌧️", 67: "🌧️",
        71: "❄️", 73: "❄️", 75: "❄️", 77: "🌨️",
        80: "🌧️", 81: "🌧️", 82: "🌧️",
        85: "❄️", 86: "❄️",
        95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    return weather_codes.get(code, "🌤️")

def get_weather_condition(code):
    conditions = {
        0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
        45: "Fog", 48: "Freezing Fog",
        51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
        61: "Light Rain", 63: "Moderate Rain", 65: "Heavy Rain",
        71: "Light Snow", 73: "Moderate Snow", 75: "Heavy Snow", 77: "Snow Grains",
        80: "Rain Showers", 81: "Moderate Showers", 82: "Heavy Showers",
        85: "Snow Showers", 86: "Heavy Snow Showers",
        95: "Thunderstorm", 96: "Thunderstorm", 99: "Heavy Thunderstorm"
    }
    return conditions.get(code, "Unknown")

# -----------------------------
# Map Functions
# -----------------------------
def create_location_map(selected_city, lat, lon):
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
        height=350,
        margin={"r":0, "t":0, "l":0, "b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_weather_map(daily_data, lat, lon):
    weather_codes = daily_data.get('weather_code', [])
    dates = daily_data.get('time', [])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scattermapbox(
        lat=[lat],
        lon=[lon],
        mode='markers',
        marker=dict(size=25, color='#d84b20', symbol='circle'),
        text=["📍 Current Location"],
        hoverinfo='text'
    ))
    
    for i, (date, code) in enumerate(zip(dates[:7], weather_codes[:7])):
        offset_lat = lat + (i - 3) * 0.3
        offset_lon = lon + (i - 3) * 0.3
        
        fig.add_trace(go.Scattermapbox(
            lat=[offset_lat],
            lon=[offset_lon],
            mode='markers',
            marker=dict(size=12, color='rgba(255,255,255,0.8)', symbol='circle'),
            text=[f"{date}: {get_weather_condition(code)} {get_weather_code_emoji(code)}"],
            hoverinfo='text',
            name=f"Day {i+1}",
            showlegend=False
        ))
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=lat, lon=lon),
            zoom=5
        ),
        height=350,
        margin={"r":0, "t":0, "l":0, "b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# -----------------------------
# Chart Functions
# -----------------------------
def create_temperature_chart(daily_data):
    dates = daily_data.get('time', [])
    temp_max = daily_data.get('temperature_2m_max', [])
    temp_min = daily_data.get('temperature_2m_min', [])
    apparent_max = daily_data.get('apparent_temperature_max', [])
    apparent_min = daily_data.get('apparent_temperature_min', [])
    
    df = pd.DataFrame({
        'Date': dates,
        'Max Temp': temp_max,
        'Min Temp': temp_min,
        'Feels Like Max': apparent_max,
        'Feels Like Min': apparent_min,
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Max Temp'],
        name='Max Temp',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8),
        mode='lines+markers'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Min Temp'],
        name='Min Temp',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8),
        mode='lines+markers'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Feels Like Max'],
        name='Feels Like Max',
        line=dict(color='#e67e22', width=2, dash='dash'),
        marker=dict(size=6),
        mode='lines+markers'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Feels Like Min'],
        name='Feels Like Min',
        line=dict(color='#1abc9c', width=2, dash='dash'),
        marker=dict(size=6),
        mode='lines+markers'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Max Temp'],
        fill=None,
        mode='none',
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Min Temp'],
        fill='tonexty',
        fillcolor='rgba(52, 152, 219, 0.1)',
        mode='none',
        showlegend=False
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
    dates = daily_data.get('time', [])
    precipitation = daily_data.get('precipitation_sum', [])
    rain = daily_data.get('rain_sum', [])
    snow = daily_data.get('snowfall_sum', [])
    
    df = pd.DataFrame({
        'Date': dates,
        'Total': precipitation,
        'Rain': rain,
        'Snow': snow,
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['Date'],
        y=df['Rain'],
        name='Rain',
        marker_color='#3498db',
        text=df['Rain'].round(1),
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        x=df['Date'],
        y=df['Snow'],
        name='Snow',
        marker_color='#bdc3c7',
        text=df['Snow'].round(1),
        textposition='outside'
    ))
    
    fig.update_layout(
        title='🌧️ Precipitation Forecast (Rain vs Snow)',
        xaxis_title='Date',
        yaxis_title='Precipitation (mm)',
        height=350,
        hovermode='x unified',
        template='plotly_white',
        barmode='stack'
    )
    
    return fig

def create_wind_chart(daily_data):
    dates = daily_data.get('time', [])
    wind_speed = daily_data.get('wind_speed_10m_max', [])
    wind_gusts = daily_data.get('wind_gusts_10m_max', [])
    
    df = pd.DataFrame({
        'Date': dates,
        'Wind Speed': wind_speed,
        'Gusts': wind_gusts,
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['Date'],
        y=df['Wind Speed'],
        name='Wind Speed',
        marker_color='#2ecc71',
        text=df['Wind Speed'].round(1),
        textposition='outside'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Gusts'],
        name='Gusts',
        line=dict(color='#e67e22', width=2, dash='dot'),
        marker=dict(size=8),
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title='💨 Wind Speed & Gusts',
        xaxis_title='Date',
        yaxis_title='Speed (km/h)',
        height=350,
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_uv_index_chart(daily_data):
    dates = daily_data.get('time', [])
    uv_index = daily_data.get('uv_index_max', [])
    
    colors = []
    for uv in uv_index:
        if uv <= 2:
            colors.append('#27ae60')
        elif uv <= 5:
            colors.append('#f1c40f')
        elif uv <= 7:
            colors.append('#e67e22')
        elif uv <= 10:
            colors.append('#e74c3c')
        else:
            colors.append('#8e44ad')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dates,
        y=uv_index,
        name='UV Index',
        marker_color=colors,
        text=uv_index,
        textposition='outside'
    ))
    
    fig.add_hline(y=2, line_dash="dash", line_color="#27ae60", annotation_text="Low", annotation_position="bottom right")
    fig.add_hline(y=5, line_dash="dash", line_color="#f1c40f", annotation_text="Moderate", annotation_position="bottom right")
    fig.add_hline(y=7, line_dash="dash", line_color="#e67e22", annotation_text="High", annotation_position="bottom right")
    fig.add_hline(y=10, line_dash="dash", line_color="#e74c3c", annotation_text="Very High", annotation_position="bottom right")
    
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

def create_cloud_cover_chart(hourly_data):
    times = hourly_data.get('time', [])[:24]
    cloud_cover = hourly_data.get('cloud_cover', [])[:24]
    
    df = pd.DataFrame({
        'Hour': [datetime.fromisoformat(t).strftime('%H:00') for t in times],
        'Cloud Cover': cloud_cover,
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Hour'],
        y=df['Cloud Cover'],
        name='Cloud Cover',
        line=dict(color='#95a5a6', width=2),
        marker=dict(size=6),
        mode='lines+markers',
        fill='tozeroy',
        fillcolor='rgba(149, 165, 166, 0.2)'
    ))
    
    fig.update_layout(
        title='☁️ Cloud Cover (Next 24 Hours)',
        xaxis_title='Time',
        yaxis_title='Cloud Cover (%)',
        height=300,
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

# -----------------------------
# Main App
# -----------------------------
st.markdown("""
    <div class="main-header">
        <h1>🍁 Premium Weather Dashboard</h1>
        <p>Real-time weather, 7-day forecast, interactive maps, and comprehensive charts</p>
        <div class="badge-group">
            <span class="badge badge-canada">🇨🇦 Canada</span>
            <span class="badge badge-live">● LIVE</span>
            <span class="badge badge-api">📡 Open-Meteo</span>
            <span class="badge badge-premium">💎 Premium</span>
        </div>
    </div>
""", unsafe_allow_html=True)

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
    
    popular_cities = ["Toronto", "Vancouver", "Montreal", "Calgary", "Edmonton", 
                      "Ottawa", "Halifax", "Winnipeg"]
    
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
        
        if is_active:
            st.caption(f"📍 {CANADA_CITIES.get(city_name, {}).get('province', '')} • Active")
        else:
            st.caption(f"📍 {CANADA_CITIES.get(city_name, {}).get('province', '')}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.expander("🗺️ All Cities"):
        all_cities = sorted(CANADA_CITIES.keys())
        cols = st.columns(2)
        for i, city_name in enumerate(all_cities):
            city_data = CANADA_CITIES[city_name]
            with cols[i % 2]:
                st.write(f"📍 {city_name} ({city_data['province']})")
    
    st.divider()
    
    # Settings
    st.markdown("### ⚙️ Settings")
    
    view_mode = st.selectbox(
        "View Mode",
        ["Detailed", "Compact", "Minimal"],
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
city = st.session_state.city
lat = st.session_state.lat
lon = st.session_state.lon

# Auto-refresh
if st.session_state.auto_refresh:
    time.sleep(30)
    st.rerun()

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
                
                # ---------- CITY INFO ----------
                st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <div>
                            <h2 style="margin: 0; font-size: 2rem;">📍 {city}, {province}</h2>
                            <p style="margin: 0; color: #888; font-size: 0.9rem;">Population: {population} • Updated: {datetime.now().strftime('%H:%M')}</p>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 3rem;">{get_weather_code_emoji(current.get('weather_code', 0))}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # ---------- SECTION 1: CURRENT WEATHER - FIXED LAYOUT ----------
                st.markdown("### ☀️ Current Weather")
                
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
                
                # Main weather cards - 4 columns
                st.markdown('<div class="weather-grid">', unsafe_allow_html=True)
                
                # Card 1: Temperature
                st.markdown(f"""
                    <div class="weather-card">
                        <div class="icon">🌡️</div>
                        <div class="value-large">{temp}°C</div>
                        <div class="label">Temperature</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Card 2: Feels Like
                st.markdown(f"""
                    <div class="weather-card">
                        <div class="icon">🌡️</div>
                        <div class="value">{feels_like}°C</div>
                        <div class="label">Feels Like</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Card 3: Condition
                st.markdown(f"""
                    <div class="weather-card">
                        <div class="icon">{get_weather_code_emoji(weather_code)}</div>
                        <div class="value" style="font-size: 1.2rem; -webkit-text-fill-color: #0d1b2a; color: #0d1b2a;">{get_weather_condition(weather_code)}</div>
                        <div class="label">Condition</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Card 4: Wind
                st.markdown(f"""
                    <div class="weather-card">
                        <div class="icon">💨</div>
                        <div class="value">{wind_speed} km/h</div>
                        <div class="label">Wind Speed</div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Stats row - 6 columns
                st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
                
                stats = [
                    ("💧", f"{humidity}%", "Humidity"),
                    ("📊", f"{pressure} hPa", "Pressure"),
                    ("☀️", f"{uv_index}", "UV Index"),
                    ("🌧️", f"{precipitation} mm", "Precip"),
                    ("🧭", f"{wind_dir}°", "Wind Dir"),
                    ("☁️", f"{cloud_cover}%", "Cloud Cover")
                ]
                
                for icon, value, label in stats:
                    st.markdown(f"""
                        <div class="stat-card">
                            <div class="value">{icon} {value}</div>
                            <div class="label">{label}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Alerts
                alerts = []
                if rain and float(rain) > 0:
                    alerts.append(("🌧️ Rain Alert", f"{rain} mm expected", "alert-rain"))
                if snowfall and float(snowfall) > 0:
                    alerts.append(("❄️ Snow Alert", f"{snowfall} mm expected", "alert-snow"))
                if wind_speed and float(wind_speed) > 50:
                    alerts.append(("💨 High Wind Alert", f"{wind_speed} km/h", "alert-wind"))
                if uv_index and float(uv_index) > 7:
                    alerts.append(("☀️ High UV Alert", f"UV Index: {uv_index}", "alert-uv"))
                
                for title, msg, cls in alerts:
                    st.markdown(f"""
                        <div class="alert-box {cls}">
                            <strong>{title}</strong> • {msg}
                        </div>
                    """, unsafe_allow_html=True)
                
                # ---------- SUNRISE/SUNSET ----------
                st.markdown("### 🌅 Sun Info")
                
                sunrise = daily.get('sunrise', [None])[0] if daily.get('sunrise') else None
                sunset = daily.get('sunset', [None])[0] if daily.get('sunset') else None
                daylight = daily.get('daylight_duration', [None])[0] if daily.get('daylight_duration') else None
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                        <div class="sun-info">
                            <div>
                                <div style="font-size: 2rem;">🌅</div>
                                <div class="value">{format_time(sunrise) if sunrise else 'N/A'}</div>
                                <div class="label">Sunrise</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div class="sun-info">
                            <div>
                                <div style="font-size: 2rem;">🌇</div>
                                <div class="value">{format_time(sunset) if sunset else 'N/A'}</div>
                                <div class="label">Sunset</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with col3:
                    hours = daylight / 3600 if daylight else 0
                    st.markdown(f"""
                        <div class="sun-info">
                            <div>
                                <div style="font-size: 2rem;">☀️</div>
                                <div class="value">{hours:.1f}h</div>
                                <div class="label">Daylight</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # ---------- SECTION 2: MAPS ----------
                st.markdown("### 🗺️ Weather Maps")
                
                col_map1, col_map2 = st.columns(2)
                
                with col_map1:
                    st.caption("📍 Location Map")
                    fig_map = create_location_map(city, lat, lon)
                    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
                
                with col_map2:
                    st.caption("🌤️ 7-Day Weather Map")
                    fig_weather = create_weather_map(daily, lat, lon)
                    st.plotly_chart(fig_weather, use_container_width=True, config={'displayModeBar': False})
                
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
                
                # Cloud cover chart
                if hourly:
                    st.markdown("### ☁️ Cloud Cover")
                    fig_cloud = create_cloud_cover_chart(hourly)
                    st.plotly_chart(fig_cloud, use_container_width=True)
                
                # Radar Chart
                st.markdown("### 📊 Weekly Summary")
                fig_radar = create_weather_radar_chart(daily)
                st.plotly_chart(fig_radar, use_container_width=True)
                
                st.markdown("---")
                
                # ---------- SECTION 4: FORECAST ----------
                st.markdown("### 📅 7-Day Forecast")
                
                dates = daily.get('time', [])
                temp_max = daily.get('temperature_2m_max', [])
                temp_min = daily.get('temperature_2m_min', [])
                weather_codes = daily.get('weather_code', [])
                precipitation_sum = daily.get('precipitation_sum', [])
                wind_speed_max = daily.get('wind_speed_10m_max', [])
                uv_index_max = daily.get('uv_index_max', [])
                sunrise_times = daily.get('sunrise', [])
                sunset_times = daily.get('sunset', [])
                
                st.markdown('<div class="forecast-grid">', unsafe_allow_html=True)
                for i in range(min(7, len(dates))):
                    date_obj = datetime.strptime(dates[i], '%Y-%m-%d')
                    st.markdown(f"""
                        <div class="forecast-card">
                            <div class="day">{date_obj.strftime('%a')}</div>
                            <div class="date">{date_obj.strftime('%b %d')}</div>
                            <div style="font-size: 2.5rem; margin: 0.2rem 0;">{get_weather_code_emoji(weather_codes[i])}</div>
                            <div class="temp-high">{temp_max[i]}°C</div>
                            <div class="temp-low">↓ {temp_min[i]}°C</div>
                            <div style="font-size: 0.65rem; color: #888; margin-top: 0.2rem;">💧 {precipitation_sum[i]}mm</div>
                            <div style="font-size: 0.65rem; color: #888;">💨 {wind_speed_max[i]} km/h</div>
                            <div style="font-size: 0.65rem; color: #888;">☀️ UV {uv_index_max[i]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # ---------- SECTION 5: STATS ----------
                st.markdown("### 📈 Weekly Statistics")
                
                avg_temp = np.mean(temp_max) if temp_max else 0
                total_precip = sum(precipitation_sum) if precipitation_sum else 0
                avg_wind = np.mean(wind_speed_max) if wind_speed_max else 0
                max_uv = max(uv_index_max) if uv_index_max else 0
                min_temp = min(temp_min) if temp_min else 0
                avg_humidity = current.get('relative_humidity_2m', 'N/A')
                
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                
                with col1:
                    st.metric("📈 Avg High", f"{avg_temp:.1f}°C")
                with col2:
                    st.metric("📉 Min Temp", f"{min_temp:.1f}°C")
                with col3:
                    st.metric("🌧️ Total Rain", f"{total_precip:.1f}mm")
                with col4:
                    st.metric("💨 Avg Wind", f"{avg_wind:.1f} km/h")
                with col5:
                    st.metric("☀️ Max UV", f"{max_uv:.0f}")
                with col6:
                    st.metric("💧 Humidity", f"{avg_humidity}%")
                
                # ---------- SECTION 6: HOURLY FORECAST ----------
                if hourly:
                    st.markdown("### ⏰ Hourly Forecast (Next 12 Hours)")
                    
                    times = hourly.get('time', [])[:12]
                    temps = hourly.get('temperature_2m', [])[:12]
                    weather_codes_hourly = hourly.get('weather_code', [])[:12]
                    precip_hourly = hourly.get('precipitation', [])[:12]
                    
                    cols = st.columns(12)
                    for i, col in enumerate(cols):
                        if i < len(times):
                            with col:
                                hour_str = datetime.fromisoformat(times[i]).strftime('%H:00')
                                st.markdown(f"""
                                    <div style="text-align: center; background: rgba(255,255,255,0.9); padding: 0.5rem; border-radius: 12px;">
                                        <div style="font-size: 0.7rem; font-weight: 600;">{hour_str}</div>
                                        <div style="font-size: 1.8rem;">{get_weather_code_emoji(weather_codes_hourly[i])}</div>
                                        <div style="font-size: 1.1rem; font-weight: 700;">{temps[i]}°C</div>
                                        <div style="font-size: 0.6rem; color: #888;">💧 {precip_hourly[i]}mm</div>
                                    </div>
                                """, unsafe_allow_html=True)
                
                # ---------- ADDITIONAL INFO ----------
                st.markdown("---")
                st.markdown("### 📋 Weather Details")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"""
                        **📍 Location Details**
                        - City: {city}, {province}
                        - Population: {population}
                        - Coordinates: {lat}, {lon}
                        - Timezone: America/Toronto
                    """)
                with col2:
                    st.info(f"""
                        **🌤️ Current Conditions**
                        - Condition: {get_weather_condition(weather_code)}
                        - Day/Night: {"☀️ Day" if is_day else "🌙 Night"}
                        - Cloud Cover: {cloud_cover}%
                        - Humidity: {humidity}%
                        - Pressure: {pressure} hPa
                    """)
                
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
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.caption("🍁 Premium Weather Dashboard")
with col2:
    st.caption("🌤️ Powered by Open-Meteo")
with col3:
    st.caption(f"📅 {datetime.now().strftime('%B %d, %Y')}")
with col4:
    st.caption("📊 15+ Charts & Maps")
with col5:
    st.caption("🏙️ 23 Canadian Cities")