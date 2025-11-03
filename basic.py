import os
import requests
from dotenv import load_dotenv

load_dotenv()

print("This is a simple weather application that uses OPENWEATHERMAP API")
print("It gives climate details on providing city name")
CITY=input("Enter city name: ")

if not CITY:
    CITY="zurich"

API_KEY=os.getenv("WEATHER_API_KEY")
weather_api_url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

weather_response = requests.get(weather_api_url)
data = weather_response.json()

lon = data["coord"]["lon"]
lat = data["coord"]["lat"]

pollution_api_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"

pollution_response = requests.get(pollution_api_url)
pollution_data = pollution_response.json()

print("---WEATHER DATA---")
print("City name:", data["name"])
print("Country code:", data["sys"]["country"])
print("Description:", data["weather"][0]["description"])
print(f"Temperature: {data["main"]["temp"]}°C")
print(f"Pressure: {data["main"]["pressure"]}hPa")
print(f"Humidity: {data["main"]["humidity"]}%")
print(f"Wind speed: {data["wind"]["speed"]}m/s")

aqi_value = pollution_data["list"][0]["main"]["aqi"]

aqi_meaning = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor"
}.get(aqi_value, "Unknown")

health_advice = {
    1: "Air quality is ideal. No health risk.",
    2: "Acceptable. Slight risk for unusually sensitive people.",
    3: "Sensitive groups should reduce prolonged outdoor exertion.",
    4: "Unhealthy for sensitive groups. Limit outdoor exposure.",
    5: "Health alert! Everyone may experience serious effects. Stay indoors."
}.get(aqi_value, "No data available")

print(f"AQI: {aqi_value} ({aqi_meaning})")
print("Health Advice:", health_advice)


