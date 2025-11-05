import os
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib
import sys
from weather_utils import get_city_from_ip, get_weather, get_aqi, aqi_meaning, health_advice

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASS = os.getenv("SMTP_PASS")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO")

if not API_KEY:
    print("❌ ERROR: WEATHER_API_KEY is missing in .env file")
    sys.exit(1)


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

- Automatic Weather Monitor
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
        print("🌍 Detecting city via IP...")
        city = get_city_from_ip() or "Zurich"
        print(f"✅ Using city: {city}")

    # Weather API
    weather_data = get_weather(city, API_KEY)

    if weather_data.get("cod") != 200:
        print(f"❌ Invalid city or API issue: {weather_data.get('message')}")
        sys.exit(1)

    # Extract values
    name = weather_data["name"]
    country = weather_data["sys"]["country"]
    desc = weather_data["weather"][0]["description"].title()
    temp = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"]
    wind = weather_data["wind"]["speed"]
    lon = weather_data["coord"]["lon"]
    lat = weather_data["coord"]["lat"]

    # AQI API
    aqi = get_aqi(lat, lon, API_KEY)
    meaning = aqi_meaning[aqi]
    advice = health_advice[aqi]

    # UI Output
    print("\n==============================================")
    print(f"📍 City: {name}, {country}")
    print(f"🌡️  Temperature: {temp}°C")
    print(f"💧 Humidity: {humidity}% | 🌀 Wind: {wind} m/s")
    print(f"🔎 Condition: {desc}")
    print("----------------------------------------------")
    print(f"🫁 AQI: {aqi} ({meaning})")
    print(f"💡 Health Advice: {advice}")
    print("==============================================\n")

    # Email alert if AQI ≥ 4
    if aqi >= 4:
        print("⚠️ AQI is high! Sending alert email...")
        send_alert_email(name, aqi, meaning)
    else:
        print("✅ AQI is safe. No alert sent.")


if __name__ == "__main__":
    main()
