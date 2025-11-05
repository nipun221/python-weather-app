from unittest.mock import patch
from weather_utils import get_city_from_ip, aqi_meaning, health_advice, get_weather, get_aqi

@patch("weather_utils.requests.get")
def test_get_city_from_ip(mock_get):
    mock_get.return_value.json.return_value = {"city": "New Delhi"}
    city = get_city_from_ip()
    assert city == "New Delhi"

@patch("weather_utils.requests.get")
def test_get_weather(mock_get):
    mock_get.return_value.json.return_value = {
        "cod": 200,
        "name": "Zurich",
        "sys": { "country": "CH" },
        "weather": [{ "description": "clear sky" }],
        "main": { "temp": 12.24, "humidity": 68 },
        "wind": { "speed": 1.5 },
        "coord": { "lon": 8.55, "lat": 47.37 }
    }
    data = get_weather("Zurich", "DUMMY_KEY")
    assert data["name"] == "Zurich"
    assert data["cod"] == 200
    assert data["sys"]["country"] == "CH"
    assert data["wind"]["speed"] == 1.5
    assert data["weather"][0]["description"] == "clear sky"

@patch("weather_utils.requests.get")
def test_get_aqi(mock_get):
    mock_get.return_value.json.return_value = {
        "list": [{ "main": { "aqi": 2 } }]
    }
    aqi = get_aqi(47.37, 8.55, "DUMMY_KEY")
    assert aqi == 2


def test_aqi_meaning_labels():
    assert aqi_meaning[1] == "Good"
    assert aqi_meaning[2] == "Fair"
    assert aqi_meaning[3] == "Moderate"
    assert aqi_meaning[4] == "Poor"
    assert aqi_meaning[5] == "Very Poor"

def test_health_advice_labels():
    assert health_advice[1] == "✅ Enjoy the fresh air!"
    assert health_advice[2] == "🙂 Air is okay for most people."
    assert health_advice[3] == "😐 Sensitive groups should reduce outdoor time."
    assert health_advice[4] == "⚠️ Unhealthy! Limit outdoor exposure."
    assert health_advice[5] == "🚨 Very unhealthy! Stay indoors."
