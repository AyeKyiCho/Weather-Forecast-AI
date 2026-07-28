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
# Premium CSS
# -----------------------------
def load_css():
    css = """
    <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
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
        
        .main-header::before {
            content: '🍁';
            position: absolute;
            right: 3rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 8rem;
            opacity: 0.08;
        }
        
        .main-header::after {
            content: '🌤️';
            position: absolute;
            right: 9rem;
            top: 15%;
            font-size: 4rem;
            opacity: 0.06;
        }
        
        .main-header h1 {
            font-weight: 800;
            margin: 0;
            font-size: 2.8rem;
            letter-spacing: -1px;
            background: linear-gradient(135deg, #ffffff, #90caf9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .main-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
            color: #e3f2fd;
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
            letter-spacing: 0.5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            color: white;
        }
        
        .badge-canada {
            background: linear-gradient(135deg, #d84b20 0%, #e67e22 100%);
        }
        
        .badge-live {
            background: #4CAF50;
            animation: pulse-dot 1.5s ease-in-out infinite;
        }
        
        .badge-api {
            background: linear-gradient(135deg, #2196F3, #00BCD4);
        }
        
        .badge-premium {
            background: linear-gradient(135deg, #9b59b6, #8e44ad);
        }
        
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Weather Cards */
        .weather-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 2rem 1.5rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            height: 100%;
            min-height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow: hidden;
        }
        
        .weather-card:hover {
            transform: translateY(-6px) scale(1.02);
            box-shadow: 0 16px 48px rgba(33, 150, 243, 0.15);
            border-color: rgba(33, 150, 243, 0.2);
        }
        
        .weather-card .icon {
            font-size: 2.5rem;
            margin-bottom: 0.3rem;
        }
        
        .weather-card .value {
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #0d1b2a, #2196F3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .weather-card .value-large {
            font-size: 4.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #0d1b2a, #2196F3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .weather-card .label {
            font-size: 0.8rem;
            color: #888;
            margin-top: 0.3rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
        }
        
        /* Forecast Cards */
        .forecast-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            padding: 1.2rem 0.8rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(0, 0, 0, 0.04);
        }
        
        .forecast-card:hover {
            transform: translateY(-8px) scale(1.03);
            box-shadow: 0 12px 40px rgba(33, 150, 243, 0.12);
            border-color: rgba(33, 150, 243, 0.2);
        }
        
        .forecast-card .day {
            font-weight: 700;
            font-size: 1.1rem;
            color: #0d1b2a;
        }
        
        .forecast-card .date {
            font-size: 0.7rem;
            color: #999;
        }
        
        .forecast-card .temp-high {
            font-size: 1.6rem;
            font-weight: 700;
            color: #2196F3;
        }
        
        .forecast-card .temp-low {
            font-size: 0.9rem;
            color: #999;
        }
        
        /* City Grid */
        .city-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
            margin: 0.5rem 0;
        }
        
        .city-btn {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border: 2px solid #e8e8e8;
            border-radius: 12px;
            padding: 0.7rem 0.4rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.85rem;
            color: #333;
        }
        
        .city-btn:hover {
            border-color: #d84b20;
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(216, 75, 32, 0.12);
            background: #fdf2e9;
        }
        
        .city-btn.active {
            background: linear-gradient(135deg, #d84b20 0%, #e67e22 100%);
            border-color: #d84b20;
            color: white;
            box-shadow: 0 4px 16px rgba(216, 75, 32, 0.3);
        }
        
        .city-btn .province {
            font-size: 0.55rem;
            opacity: 0.6;
            display: block;
            font-weight: 400;
            margin-top: 0.1rem;
        }
        
        .city-btn.active .province {
            opacity: 0.8;
            color: rgba(255,255,255,0.8);
        }
        
        /* Quick Cities Header */
        .quick-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.8rem;
            padding: 0.5rem 0;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .quick-header h4 {
            margin: 0;
            font-weight: 700;
            color: #0d1b2a;
            font-size: 1rem;
        }
        
        .quick-header .leaf {
            font-size: 1.2rem;
            display: inline-block;
            animation: leaf-spin 3s ease-in-out infinite;
        }
        
        @keyframes leaf-spin {
            0%, 100% { transform: rotate(0deg); }
            50% { transform: rotate(10deg); }
        }
        
        /* Dark Mode */
        @media (prefers-color-scheme: dark) {
            .weather-card {
                background: rgba(30, 42, 58, 0.95);
                border-color: rgba(255, 255, 255, 0.05);
            }
            .weather-card .label {
                color: #888;
            }
            .forecast-card {
                background: rgba(30, 42, 58, 0.95);
                border-color: rgba(255, 255, 255, 0.05);
            }
            .forecast-card:hover {
                background: rgba(42, 58, 74, 0.95);
            }
            .forecast-card .day {
                color: #e0e0e0;
            }
            .city-btn {
                background: rgba(30, 42, 58, 0.95);
                border-color: rgba(255, 255, 255, 0.05);
                color: #e0e0e0;
            }
            .city-btn:hover {
                background: rgba(42, 58, 74, 0.95);
                border-color: #d84b20;
            }
            .city-btn.active {
                background: linear-gradient(135deg, #d84b20 0%, #e67e22 100%);
                color: white;
            }
            .quick-header {
                border-bottom-color: rgba(255, 255, 255, 0.05);
            }
            .quick-header h4 {
                color: #e0e0e0;
            }
            .css-1d391kg {
                background: #0d1b2a;
                border-right-color: rgba(255, 255, 255, 0.05);
            }
            .weather-card .value {
                background: linear-gradient(135deg, #64B5F6, #4DD0E1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .weather-card .value-large {
                background: linear-gradient(135deg, #64B5F6, #4DD0E1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .main-header {
                padding: 1.5rem;
            }
            .main-header h1 {
                font-size: 1.8rem;
            }
            .weather-card .value-large {
                font-size: 3rem;
            }
            .weather-card .value {
                font-size: 2rem;
            }
        }
        
        /* Animations */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .weather-card {
            animation: fadeInUp 0.6s ease forwards;
        }
        
        .forecast-card {
            animation: fadeInUp 0.6s ease forwards;
        }
        
        /* Stats Cards */
        .stat-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            padding: 1.2rem;
            border-radius: 14px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
            text-align: center;
            border-left: 4px solid #2196F3;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(33, 150, 243, 0.08);
        }
        
        .stat-card .value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0d1b2a;
        }
        
        .stat-card .label {
            font-size: 0.75rem;
            color: #999;
            margin-top: 0.2rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Alert Boxes */
        .alert-box {
            padding: 1rem;
            border-radius: 12px;
            margin: 0.5rem 0;
            border-left: 4px solid;
        }
        
        .alert-rain {
            background: #e3f2fd;
            border-left-color: #2196F3;
        }
        
        .alert-snow {
            background: #e8f5e9;
            border-left-color: #4CAF50;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #2196F3, #00BCD4);
            border-radius: 4px;
        }
        
        @media (prefers-color-scheme: dark) {
            ::-webkit-scrollbar-track {
                background: #1a2a3a;
            }
        }
        
        /* Divider */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #2196F3, transparent);
            margin: 2rem 0;
            opacity: 0.3;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

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
        height=400,
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
        height=400,
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
    
    df = pd.DataFrame({
        'Date': dates,
        'Max Temp': temp_max,
        'Min Temp': temp_min,
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
    
    df = pd.DataFrame({
        'Date': dates,
        'Precipitation': precipitation,
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['Date'],
        y=df['Precipitation'],
        name='Precipitation',
        marker_color='#3498db',
        text=df['Precipitation'].round(1),
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
    dates = daily_data.get('time', [])
    wind_speed = daily_data.get('wind_speed_10m_max', [])
    
    df = pd.DataFrame({
        'Date': dates,
        'Wind Speed': wind_speed,
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

# -----------------------------
# Main App
# -----------------------------
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
        for city_name in all_cities:
            city_data = CANADA_CITIES[city_name]
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
                
                # ---------- SECTION 1: MAPS ----------
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
                
                # ---------- SECTION 2: CURRENT WEATHER ----------
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
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                        <div class="weather-card">
                            <div class="icon">🌡️</div>
                            <div class="value-large">{temp}°C</div>
                            <div class="label">Temperature</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="weather-card">
                            <div class="icon">🌡️</div>
                            <div class="value">{feels_like}°C</div>
                            <div class="label">Feels Like</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div class="weather-card">
                            <div class="icon">{get_weather_code_emoji(weather_code)}</div>
                            <div class="value">{get_weather_condition(weather_code)}</div>
                            <div class="label">Condition</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                        <div class="weather-card">
                            <div class="icon">💨</div>
                            <div class="value">{wind_speed} km/h</div>
                            <div class="label">Wind Speed</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Row 2: Extra metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.markdown(f"""
                        <div class="stat-card">
                            <div class="value">💧 {humidity}%</div>
                            <div class="label">Humidity</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="stat-card">
                            <div class="value">📊 {pressure} hPa</div>
                            <div class="label">Pressure</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div class="stat-card">
                            <div class="value">☀️ {uv_index}</div>
                            <div class="label">UV Index</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                        <div class="stat-card">
                            <div class="value">🌧️ {precipitation} mm</div>
                            <div class="label">Precipitation</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col5:
                    st.markdown(f"""
                        <div class="stat-card">
                            <div class="value">🧭 {wind_dir}°</div>
                            <div class="label">Wind Dir</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Rain/Snow Alerts
                if rain and float(rain) > 0:
                    st.info(f"🌧️ Rain Alert: {rain} mm expected")
                if snowfall and float(snowfall) > 0:
                    st.info(f"❄️ Snow Alert: {snowfall} mm expected")
                
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
                                </div>
                            """, unsafe_allow_html=True)
                
                # ---------- SECTION 5: STATS ----------
                st.markdown("### 📈 Weekly Statistics")
                
                avg_temp = np.mean(temp_max) if temp_max else 0
                total_precip = sum(precipitation_sum) if precipitation_sum else 0
                avg_wind = np.mean(wind_speed_max) if wind_speed_max else 0
                max_uv = max(uv_index_max) if uv_index_max else 0
                min_temp = min(temp_min) if temp_min else 0
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
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