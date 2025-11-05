import os
import requests
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib
import sys

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASS = os.getenv("SMTP_PASS")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO")

if not API_KEY:
    print("❌ ERROR: WEATHER_API_KEY is missing in .env file")
    sys.exit(1)


def get_city_from_ip():
    try:
        res = requests.get("http://ip-api.com/json/", timeout=5)
        data = res.json()
        city = data.get('city')
        return city
    except Exception as e:
        print(f"Error getting city from IP: {e}")
        return None


def send_alert_email(city, aqi, meaning):
    if not SMTP_EMAIL or not SMTP_PASS:
        print("⚠️ Email alert skipped (SMTP details missing in .env)")
        return

    msg = EmailMessage()
    msg["Subject"] = f"⚠️ AQI ALERT: {city} - AQI {aqi} ({meaning})"
    msg["From"] = SMTP_EMAIL
    msg["To"] = ALERT_EMAIL_TO
    msg.set_content(f"""
Air Quality Alert for {city} 🚨

AQI Level: {aqi} ({meaning})

Recommendation: Avoid outdoor activity if possible.

- Sent automatically by your Weather & AQI Monitor
""")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_PASS)
            smtp.send_message(msg)
        print("📧 Email alert sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def main():
    print("\n🌤️  Simple Weather & Air Quality Monitor")
    city = input("Enter city name (leave blank to auto-detect via IP): ").strip()

    if not city:
        print("🌍 Detecting your city via IP...")
        city = get_city_from_ip()
        if city:
            print(f"✅ Detected city: {city}")
        if not city:
            print("❌ Could not detect city automatically. Using default city i.e., Zurich.")
            city = "Zurich"

    # Weather API
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    weather_data = requests.get(weather_url).json()

    if weather_data.get("cod") != 200:
        print(f"❌ Invalid city or API issue: {weather_data.get('message')}")
        sys.exit(1)

    # Extract values
    name = weather_data["name"]
    country = weather_data["sys"]["country"]
    desc = weather_data["weather"][0]["description"].title()
    temp = weather_data["main"]["temp"]
    pressure = weather_data["main"]["pressure"]
    humidity = weather_data["main"]["humidity"]
    wind = weather_data["wind"]["speed"]
    lon = weather_data["coord"]["lon"]
    lat = weather_data["coord"]["lat"]

    # AQI API
    pollution_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    pollution_data = requests.get(pollution_url).json()
    aqi = pollution_data["list"][0]["main"]["aqi"]

    aqi_meaning = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}[aqi]
    health_advice = {
        1: "✅ Enjoy the fresh air!",
        2: "🙂 Air is okay for most people.",
        3: "😐 Sensitive groups should reduce outdoor time.",
        4: "⚠️ Unhealthy! Limit outdoor exposure.",
        5: "🚨 Very unhealthy! Stay indoors."
    }[aqi]

    # UI Output
    print("\n==============================================")
    print(f"📍 City: {name}, {country}")
    print(f"🌡️  Temperature: {temp}°C")
    print(f"💧 Humidity: {humidity}% | 🌀 Wind: {wind} m/s")
    print(f"🔎 Condition: {desc}")
    print("----------------------------------------------")
    print(f"🫁 AQI: {aqi} ({aqi_meaning})")
    print(f"💡 Health Advice: {health_advice}")
    print("==============================================\n")

    # Email alert if AQI ≥ 4
    if aqi >= 4:
        print("⚠️ AQI is high! Sending alert email...")
        send_alert_email(name, aqi, aqi_meaning)
    else:
        print("✅ AQI is safe. No alert sent.")


if __name__ == "__main__":
    main()
