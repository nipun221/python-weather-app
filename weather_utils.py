import requests

def get_city_from_ip():
    """Returns city based on public IP"""
    try:
        res = requests.get("http://ip-api.com/json/", timeout=5)
        data = res.json()
        return data.get("city")
    except Exception as e:
        print(f"Error getting city from IP: {e}")
        return None

def get_weather(city, api_key):
    """Returns weather json for a city"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    return requests.get(url).json()


def get_aqi(lat, lon, api_key):
    """Returns AQI number"""
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    data = requests.get(url).json()
    return data["list"][0]["main"]["aqi"]

aqi_meaning = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor"
}

health_advice = {
    1: "✅ Enjoy the fresh air!",
    2: "🙂 Air is okay for most people.",
    3: "😐 Sensitive groups should reduce outdoor time.",
    4: "⚠️ Unhealthy! Limit outdoor exposure.",
    5: "🚨 Very unhealthy! Stay indoors."
}
