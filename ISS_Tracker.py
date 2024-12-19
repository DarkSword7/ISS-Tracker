import json
import urllib.request
import streamlit as st
from datetime import datetime, timezone
import requests
import pandas as pd
import pydeck as pdk

# Function to fetch data from API
def fetch_data(url):
    response = urllib.request.urlopen(url)
    result = json.loads(response.read())
    return result

# Fetch astronaut data
def get_astronauts():
    url = "http://api.open-notify.org/astros.json"
    data = fetch_data(url)
    astronauts = data["people"]
    return astronauts, data["number"]

# Fetch ISS location
def get_iss_location():
    url = "http://api.open-notify.org/iss-now.json"
    data = fetch_data(url)
    position = data["iss_position"]
    latitude = float(position["latitude"])
    longitude = float(position["longitude"])
    timestamp = data["timestamp"]
    return latitude, longitude, timestamp

# Fetch upcoming ISS overpasses
def get_upcoming_passes(lat, lon):
    url = f"https://api.n2yo.com/rest/v1/satellite/visualpasses/25544/{lat}/{lon}/0/5/&apiKey=DEMO_KEY"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("passes", [])
    return []

# Educational content
def iss_educational_content():
    return """
    The International Space Station (ISS) is a modular space station in low Earth orbit.
    It serves as a laboratory for scientific research, international cooperation, and space exploration.
    Modules include laboratories, living quarters, and solar arrays. Key experiments include studies on microgravity, biology, and physics.
    """

# Fetch weather data
def get_weather(lat, lon):
    api_key = "ca334a983a13b75250d1b020f3cc9dfc"
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        weather = {
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "city": data.get("name", "N/A"),
        }
    else:
        weather = None
    return weather

# Streamlit UI setup
st.set_page_config(page_title="Live ISS Tracker", page_icon="🌌", layout="wide")
st.title("🌌 Live ISS Tracker")

# Fetch current ISS location
latitude, longitude, timestamp = get_iss_location()
location_time = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

# Display astronaut data
st.sidebar.header("Astronauts on the ISS")
astronauts, num_astronauts = get_astronauts()
st.sidebar.write(f"There are currently **{num_astronauts}** astronauts aboard the ISS:")
for astronaut in astronauts:
    st.sidebar.markdown(f"- [{astronaut['name']}](https://en.wikipedia.org/wiki/{astronaut['name'].replace(' ', '_')})")

# Main content layout
col1, col2 = st.columns(2)

# ISS Location Information
with col1:
    st.header("Current Location of the ISS")
    st.write(f"**Latitude:** {latitude}")
    st.write(f"**Longitude:** {longitude}")
    st.write(f"**Last Updated:** {location_time}")

# Weather Information
with col2:
    st.header("Weather at ISS Ground Location")
    weather = get_weather(latitude, longitude)
    if weather:
        st.write(f"**City:** {weather['city']}")
        st.write(f"**Temperature:** {weather['temperature']}°C")
        st.write(f"**Conditions:** {weather['description'].capitalize()}")
    else:
        st.write("Weather data is not available.")

# Educational content
with st.expander("Learn About the ISS"):
    st.write(iss_educational_content())

# Upcoming ISS Overpasses
st.header("Upcoming ISS Overpasses")
user_lat = st.number_input("Enter Your Latitude", value=latitude, format="%f")
user_lon = st.number_input("Enter Your Longitude", value=longitude, format="%f")
if st.button("Find Overpasses"):
    overpasses = get_upcoming_passes(user_lat, user_lon)
    if overpasses:
        for overpass in overpasses:
            rise_time = datetime.utcfromtimestamp(overpass["startUTC"]).strftime('%Y-%m-%d %H:%M:%S UTC')
            st.write(f"- Visible pass starting at: {rise_time}")
    else:
        st.write("No visible passes found.")

# 3D Globe Visualization
st.header("Visualization of ISS Location")
globe_layer = pdk.Layer(
    "ScatterplotLayer",
    data=pd.DataFrame([{"lat": latitude, "lon": longitude}]),
    get_position="[lon, lat]",
    get_fill_color="[255, 0, 0, 160]",
    get_radius=500000,
)
view_state = pdk.ViewState(latitude=latitude, longitude=longitude, zoom=1, pitch=0)
st.pydeck_chart(pdk.Deck(layers=[globe_layer], initial_view_state=view_state))

# Refresh button
if st.button("Refresh ISS Data"):
    st.experimental_rerun()
