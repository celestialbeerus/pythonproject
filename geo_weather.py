import requests
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# Function to get coordinates using OpenCage API
def get_coordinates(city_name, api_key):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={city_name}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        location_data = response.json()
        if location_data['results']:
            lat = location_data['results'][0]['geometry']['lat']
            lon = location_data['results'][0]['geometry']['lng']
            return lat, lon
        else:
            print("No results found.")
    else:
        print(f"Error: {response.status_code}")
    return None, None

# Function to get weather data (you can replace this with your own implementation)
def get_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Streamlit application
st.title("GeoWeather Insights 🌤️")

# User authentication
if 'username' not in st.session_state:
    st.session_state.username = None

if st.session_state.username is None:
    st.subheader("User  Authentication")
    username = st.text_input("Enter Username")
    if st.button("Login"):
        if username:
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
        else:
            st.error("Please enter a username.")
else:
    st.subheader(f"Welcome back, {st.session_state.username}!")

    # Input for city name
    city_name = st.text_input("Enter City Name", value="San Francisco")
    api_key = st.text_input("Enter OpenCage API Key", type="password")

    if st.button("Get Weather Data"):
        lat, lon = get_coordinates(city_name, api_key)
        if lat is not None and lon is not None:
            st.write(f"Coordinates: Latitude: {lat}, Longitude: {lon}")
            data = get_weather_data(lat, lon)
            if data:
                st.write("Weather Data Retrieved Successfully")
                current_weather = data.get('hourly', {})
                temperature = current_weather.get('temperature_2m', [])
                humidity = current_weather.get('relative_humidity_2m', [])
                wind_speed = current_weather.get('wind_speed_10m', [])
                time = current_weather.get('time', [])

                if temperature and humidity and wind_speed and time:
                    df = pd.DataFrame({
                        'Time': pd.to_datetime(time),
                        'Temperature (°C)': temperature,
                        'Humidity (%)': humidity,
                        'Wind Speed (m/s)': wind_speed
                    })
                    st.write(df)

                    # Plotting
                    fig, ax1 = plt.subplots(figsize=(10, 5))
                    ax1.set_xlabel('Time')
                    ax1.set_ylabel('Temperature (°C)', color='tab:red')
                    ax1.plot(df['Time'], df['Temperature (°C)'], color='tab:red', label='Temperature (°C)')
                    ax1.tick_params(axis='y', labelcolor='tab:red')
                    ax2 = ax1.twinx()
                    ax2.set_ylabel('Humidity (%)', color='tab:blue')
                    ax2.plot(df['Time'], df['Humidity (%)'], color='tab:blue', label='Humidity (%)')
                    ax2.tick_params(axis='y', labelcolor='tab:blue')
                    fig.tight_layout()
                    st.pyplot(fig)
                else:
                    st.error("Incomplete weather data received from the API.")
            else:
                st.error("Failed to retrieve weather data.")
        else:
            st.error("Failed to retrieve coordinates.")


