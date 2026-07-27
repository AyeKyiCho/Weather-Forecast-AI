import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from datetime import datetime

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌤️",
    layout="wide"
)

# -----------------------------
# Initialize Session State
# -----------------------------
if 'city' not in st.session_state:
    st.session_state.city = "Toronto"

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
    <style>
    .header {
        background: linear-gradient(135deg, #2196F3 0%, #00BCD4 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .header h1 { margin: 0; font-size: 2.5rem; }
    .header p { margin: 0.5rem 0 0 0; opacity: 0.9; }
    .weather-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #2196F3;
    }
    .temp-large {
        font-size: 4rem;
        font-weight: bold;
        color: #2196F3;
    }
    .weather-value { font-size: 2rem; font-weight: bold; color: #2196F3; }
    .weather-label { font-size: 0.9rem; color: #666; margin-top: 0.5rem; }
    .forecast-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .city-button {
        width: 100%;
        padding: 0.5rem;
        margin: 0.2rem 0;
        background-color: #e3f2fd;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .city-button:hover {
        background-color: #2196F3;
        color: white;
    }
    .city-button-active {
        background-color: #2196F3;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Weather Functions
# -----------------------------
def get_weather_wttr(city):
    """Get weather from wttr.in (free, no API key)"""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def parse_wttr_data(data):
    """Parse wttr.in data"""
    if not data:
        return None, None
    
    try:
        current = data.get('current_condition', [{}])[0]
        weather = {
            'temp': current.get('temp_C', 'N/A'),
            'feels_like': current.get('FeelsLikeC', 'N/A'),
            'humidity': current.get('humidity', 'N/A'),
            'pressure': current.get('pressure', 'N/A'),
            'condition': current.get('weatherDesc', [{}])[0].get('value', 'Unknown'),
            'wind_speed': current.get('windspeedKmph', 'N/A'),
            'wind_dir': current.get('winddir16Point', 'N/A')
        }
        
        forecast = []
        for day in data.get('weather', [])[:5]:
            forecast.append({
                'date': day.get('date', ''),
                'temp_max': day.get('maxtempC', 'N/A'),
                'temp_min': day.get('mintempC', 'N/A'),
                'condition': day.get('hourly', [{}])[0].get('weatherDesc', [{}])[0].get('value', 'Unknown')
            })
        
        return weather, forecast
    except:
        return None, None

def get_weather_emoji(condition):
    """Get emoji for weather condition"""
    condition_lower = condition.lower()
    if 'clear' in condition_lower or 'sunny' in condition_lower:
        return '☀️'
    elif 'cloud' in condition_lower:
        return '☁️'
    elif 'rain' in condition_lower or 'drizzle' in condition_lower:
        return '🌧️'
    elif 'snow' in condition_lower:
        return '❄️'
    elif 'thunder' in condition_lower:
        return '⛈️'
    elif 'mist' in condition_lower or 'fog' in condition_lower:
        return '🌫️'
    elif 'wind' in condition_lower:
        return '💨'
    else:
        return '🌤️'

# -----------------------------
# Main App
# -----------------------------
st.markdown("""
    <div class="header">
        <h1>🌤️ Weather Dashboard</h1>
        <p>Real-time weather and 5-day forecast</p>
    </div>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("📍 Location")
    
    # City input
    city_input = st.text_input(
        "Enter City Name",
        value=st.session_state.city,
        placeholder="e.g., Toronto, New York, London"
    )
    
    # Update session state when text input changes
    if city_input != st.session_state.city:
        st.session_state.city = city_input
        st.rerun()
    
    st.subheader("⚡ Quick Cities")
    quick_cities = ["Toronto", "New York", "London", "Tokyo", "Sydney", "Dubai", "Mumbai"]
    
    # Create buttons in rows of 3
    for i in range(0, len(quick_cities), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(quick_cities):
                city_name = quick_cities[i + j]
                with cols[j]:
                    # Check if this city is currently selected
                    is_active = (city_name == st.session_state.city)
                    button_label = f"📍 {city_name}" if is_active else city_name
                    
                    if st.button(
                        button_label,
                        key=f"city_{city_name}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary"
                    ):
                        st.session_state.city = city_name
                        st.rerun()

# -----------------------------
# Get Weather Data
# -----------------------------
city = st.session_state.city

if city:
    with st.spinner(f"Loading weather for {city}..."):
        data = get_weather_wttr(city)
        
        if data:
            weather, forecast = parse_wttr_data(data)
            
            if weather:
                # Display current city name
                st.subheader(f"📍 Current Weather in {city}")
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                        <div class="weather-card">
                            <div class="temp-large">{weather['temp']}°C</div>
                            <div class="weather-label">🌡️ Temperature</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="weather-card">
                            <div class="weather-value">{get_weather_emoji(weather['condition'])} {weather['condition']}</div>
                            <div class="weather-label">☁️ Condition</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div class="weather-card">
                            <div class="weather-value">💨 {weather['wind_speed']} km/h</div>
                            <div class="weather-label">Wind Speed</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # More metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("💧 Humidity", f"{weather['humidity']}%")
                with col2:
                    st.metric("📊 Pressure", f"{weather['pressure']} hPa")
                with col3:
                    st.metric("🌡️ Feels Like", f"{weather['feels_like']}°C")
                with col4:
                    st.metric("🧭 Wind Dir", weather['wind_dir'])
                
                # Forecast
                if forecast:
                    st.subheader("📊 5-Day Forecast")
                    
                    df = pd.DataFrame(forecast)
                    
                    # Temperature chart
                    fig = px.line(
                        df,
                        x='date',
                        y=['temp_max', 'temp_min'],
                        title=f'Temperature Trend for {city}',
                        markers=True,
                        labels={'value': 'Temperature (°C)', 'date': 'Date'}
                    )
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Forecast Cards
                    st.subheader("📅 Daily Forecast")
                    cols = st.columns(min(5, len(df)))
                    for i, (idx, row) in enumerate(df.iterrows()):
                        if i >= 5:
                            break
                        with cols[i]:
                            date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
                            st.markdown(f"""
                                <div class="forecast-card">
                                    <div style="font-weight:bold; font-size:1.1rem;">{date_obj.strftime('%a')}</div>
                                    <div style="font-size:0.8rem; color:#888;">{date_obj.strftime('%b %d')}</div>
                                    <div style="font-size:2.5rem; margin:0.3rem 0;">{get_weather_emoji(row['condition'])}</div>
                                    <div style="font-size:1.3rem; font-weight:bold; color:#2196F3;">{row['temp_max']}°C</div>
                                    <div style="font-size:0.8rem; color:#666;">↓ {row['temp_min']}°C</div>
                                    <div style="font-size:0.7rem; color:#888; margin-top:0.2rem;">{row['condition'][:20]}</div>
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.warning(f"⚠️ Could not parse weather data for {city}")
        else:
            st.error(f"❌ Could not fetch weather data for {city}. Please check the city name.")

else:
    st.info("👈 Enter a city name to get started")

# -----------------------------
# Footer
# -----------------------------
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🌤️ Weather Dashboard")
with col2:
    st.caption("Powered by wttr.in")
with col3:
    st.caption(f"📅 {datetime.now().strftime('%B %d, %Y')}")