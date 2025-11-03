#!/usr/bin/env python3
"""
Weather + AQI Monitor
- Auto-detect city via IP if user presses Enter
- Fetch weather & air pollution from OpenWeatherMap
- Nicely formatted terminal UI (emojis + colors)
- Send detailed email alert via Gmail SMTP if AQI >= 4 (Poor/Very Poor)
- Uses dotenv for secrets
"""

import os
import sys
import time
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# ----------------------------
# Configuration
# ----------------------------
RETRIES = 3
RETRY_DELAY = 2  # seconds between retries
AQI_ALERT_THRESHOLD = 4  # send email when AQI >= this value

# ----------------------------
# Terminal Colors & Emojis
# ----------------------------
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
MAGENTA = "\033[95m"

EMOJI_CITY = "🌍"
EMOJI_TEMP = "🌡️"
EMOJI_HUMID = "💧"
EMOJI_WIND = "💨"
EMOJI_COND = "🌥️"
EMOJI_AQI = "⚠️"
EMOJI_HEALTH = "⚕️"
EMOJI_CLOCK = "🕒"

# ----------------------------
# Email template (custom)
# ----------------------------
EMAIL_SUBJECT_TEMPLATE = "⚠️ Air Quality Alert: {CITY} - {AQI_MEANING}"
EMAIL_BODY_TEMPLATE = """🚨 AIR QUALITY ALERT 🚨

City: {CITY}, {COUNTRY}
AQI Level: {AQI} ({AQI_MEANING})

🌡️ Temperature: {TEMP}°C
💧 Humidity: {HUMIDITY}%
💨 Wind Speed: {WIND} m/s
🌥️ Condition: {WEATHER_DESC}

⚕️ Health Advisory:
{HEALTH_ADVICE}

Stay safe and avoid outdoor activity if possible.
— Automated Weather Monitor
"""

# ----------------------------
# Helpers
# ----------------------------

def load_config():
    load_dotenv()
    cfg = {
        "WEATHER_API_KEY": os.getenv("WEATHER_API_KEY"),
        "SMTP_EMAIL": os.getenv("SMTP_EMAIL"),
        "SMTP_PASS": os.getenv("SMTP_PASS"),
        "ALERT_EMAIL_TO": os.getenv("ALERT_EMAIL_TO"),
    }
    return cfg

def fail(msg, code=1):
    print(f"{RED}{BOLD}Error:{RESET} {msg}")
    sys.exit(code)

def pretty_dt_from_ts(ts, tz_offset_seconds=0):
    """Convert unix timestamp + tz offset to readable local time string."""
    try:
        dt = datetime.fromtimestamp(ts + tz_offset_seconds)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)

def get_city_from_ip():
    """Auto-detect city via ipapi.co (no key required)."""
    try:
        r = requests.get("https://ipapi.co/json", timeout=6)
        if r.status_code == 200:
            data = r.json()
            city = data.get("city")
            region = data.get("region")
            country = data.get("country")
            display = city or region or country
            return display
    except Exception:
        return None
    return None

def fetch_json_with_retry(url, params=None, retries=RETRIES, delay=RETRY_DELAY):
    """GET JSON with simple retry logic."""
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, timeout=8)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_exc = e
            if attempt < retries:
                time.sleep(delay)
            else:
                raise
    raise last_exc

def map_aqi_value(aqi):
    meanings = {
        1: ("Good", "Air quality is ideal. No health risk."),
        2: ("Fair", "Acceptable. Slight risk for unusually sensitive people."),
        3: ("Moderate", "Sensitive groups should reduce prolonged outdoor exertion."),
        4: ("Poor", "Unhealthy for sensitive groups. Limit outdoor exposure."),
        5: ("Very Poor", "Health alert! Everyone may experience serious effects. Stay indoors."),
    }
    return meanings.get(aqi, ("Unknown", "No data available"))

def send_email_alert(cfg, city, country, aqi, aqi_meaning, temp, humidity, wind, weather_desc, health_advice):
    smtp_user = cfg.get("SMTP_EMAIL")
    smtp_pass = cfg.get("SMTP_PASS")
    to_addr = cfg.get("ALERT_EMAIL_TO")

    if not smtp_user or not smtp_pass or not to_addr:
        print(f"{YELLOW}Email not sent:{RESET} SMTP credentials or recipient missing in .env")
        return False

    subject = EMAIL_SUBJECT_TEMPLATE.format(CITY=city, AQI_MEANING=aqi_meaning)
    body = EMAIL_BODY_TEMPLATE.format(
        CITY=city,
        COUNTRY=country,
        AQI=aqi,
        AQI_MEANING=aqi_meaning,
        TEMP=f"{temp:.1f}",
        HUMIDITY=humidity,
        WIND=wind,
        WEATHER_DESC=weather_desc,
        HEALTH_ADVICE=health_advice
    )

    msg = EmailMessage()
    msg["From"] = smtp_user
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"{GREEN}Email alert sent to {to_addr}{RESET}")
        return True
    except Exception as e:
        print(f"{RED}Failed to send email:{RESET} {e}")
        return False

# ----------------------------
# Main functionality
# ----------------------------

def get_weather_and_pollution(cfg, city):
    api_key = cfg.get("WEATHER_API_KEY")
    if not api_key:
        fail("Missing WEATHER_API_KEY in .env")

    # Weather endpoint
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        weather_data = fetch_json_with_retry(weather_url, params=params)
    except Exception as e:
        fail(f"Failed to fetch weather data: {e}")

    # Check for errors in response (OpenWeather returns 'cod' and 'message' on errors)
    if isinstance(weather_data, dict) and weather_data.get("cod") and str(weather_data.get("cod")) != "200":
        msg = weather_data.get("message", "Unknown error from weather API")
        fail(f"Weather API error: {msg}")

    # coords
    coord = weather_data.get("coord")
    if not coord:
        fail("Weather API did not return coordinates for city.")

    lat = coord.get("lat")
    lon = coord.get("lon")

    # Pollution endpoint
    pollution_url = "http://api.openweathermap.org/data/2.5/air_pollution"
    poll_params = {"lat": lat, "lon": lon, "appid": api_key}

    try:
        pollution_data = fetch_json_with_retry(pollution_url, params=poll_params)
    except Exception as e:
        fail(f"Failed to fetch air pollution data: {e}")

    return weather_data, pollution_data

def format_and_display(weather_data, pollution_data):
    # Basic weather
    name = weather_data.get("name", "Unknown")
    sys = weather_data.get("sys", {})
    country = sys.get("country", "")
    weather = weather_data.get("weather", [{}])[0]
    weather_desc = weather.get("description", "N/A").title()
    main = weather_data.get("main", {})
    temp = main.get("temp", 0.0)
    feels_like = main.get("feels_like", None)
    pressure = main.get("pressure", "N/A")
    humidity = main.get("humidity", "N/A")
    wind = weather_data.get("wind", {}).get("speed", "N/A")
    visibility = weather_data.get("visibility", None)
    timezone_offset = weather_data.get("timezone", 0)
    sunrise = sys.get("sunrise")
    sunset = sys.get("sunset")

    # Pollution
    list0 = pollution_data.get("list", [{}])[0]
    aqi_value = list0.get("main", {}).get("aqi", None)
    aqi_value = int(aqi_value) if aqi_value is not None else None
    aqi_meaning, health_advice = map_aqi_value(aqi_value)

    # Header block
    print(BOLD + CYAN + "=" * 50 + RESET)
    print(BOLD + CYAN + "            WEATHER & AIR QUALITY REPORT" + RESET)
    print(BOLD + CYAN + "=" * 50 + RESET)
    print(f"{EMOJI_CITY} {BOLD}City:{RESET} {name}, {country}")
    now = datetime.now() + timedelta(seconds=timezone_offset)
    print(f"{EMOJI_CLOCK} {BOLD}Updated (local):{RESET} {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    # Weather line
    feels_txt = f" (Feels {feels_like:.1f}°C)" if feels_like is not None else ""
    vis_txt = f"{visibility} m" if visibility is not None else "N/A"
    print(f"{EMOJI_TEMP} {BOLD}Temperature:{RESET} {temp:.1f}°C{feels_txt}   {EMOJI_HUMID} {BOLD}Humidity:{RESET} {humidity}%")
    print(f"{EMOJI_WIND} {BOLD}Wind:{RESET} {wind} m/s   {EMOJI_COND} {BOLD}Condition:{RESET} {weather_desc}")
    print(f"Pressure: {pressure} hPa   Visibility: {vis_txt}")

    # Sunrise / Sunset
    if sunrise and sunset:
        sunrise_local = pretty_dt_from_ts(sunrise, timezone_offset)
        sunset_local = pretty_dt_from_ts(sunset, timezone_offset)
        print(f"Sunrise: {sunrise_local}   Sunset: {sunset_local}")

    print("-" * 50)

    # AQI block
    if aqi_value is None:
        print(f"{EMOJI_AQI} {BOLD}AQI:{RESET} Not available")
    else:
        aqi_color = GREEN if aqi_value <= 2 else YELLOW if aqi_value == 3 else RED
        print(f"{EMOJI_AQI} {BOLD}AQI:{RESET} {aqi_color}{aqi_value}{RESET} ({aqi_meaning})")
        print(f"{EMOJI_HEALTH} {BOLD}Health Advice:{RESET} {health_advice}")

    print(BOLD + CYAN + "=" * 50 + RESET)

    # Return values for possible email
    return {
        "city": name,
        "country": country,
        "aqi_value": aqi_value,
        "aqi_meaning": aqi_meaning,
        "temp": temp,
        "humidity": humidity,
        "wind": wind,
        "weather_desc": weather_desc,
    }

def main():
    cfg = load_config()

    # Ask user for city, auto-detect if blank
    print(BOLD + "This is a friendly Weather + AQI app." + RESET)
    print("It uses OpenWeatherMap API. Press Enter to auto-detect your city via IP.")
    user_city = input("Enter city name: ").strip()

    if not user_city:
        auto = get_city_from_ip()
        if auto:
            print(f"{GREEN}Auto-detected city:{RESET} {auto}")
            city = auto
        else:
            print(f"{YELLOW}Could not auto-detect city. Using default: Zurich{RESET}")
            city = "Zurich"
    else:
        city = user_city

    # Fetch data
    try:
        weather_data, pollution_data = get_weather_and_pollution(cfg, city)
    except Exception as e:
        fail(f"Couldn't obtain data: {e}")

    # Format and display report
    summary = format_and_display(weather_data, pollution_data)

    # Check if AQI meets alert threshold
    aqi_val = summary.get("aqi_value")
    if aqi_val is not None and aqi_val >= AQI_ALERT_THRESHOLD:
        aqi_meaning = summary.get("aqi_meaning")
        health_advice = map_aqi_value(aqi_val)[1]
        # Send detailed email using your custom template
        send_email_alert(
            cfg,
            city=summary.get("city"),
            country=summary.get("country") or "",
            aqi=aqi_val,
            aqi_meaning=aqi_meaning,
            temp=summary.get("temp"),
            humidity=summary.get("humidity"),
            wind=summary.get("wind"),
            weather_desc=summary.get("weather_desc"),
            health_advice=health_advice
        )
    else:
        print(f"{GREEN}No AQI alert necessary (AQI below threshold).{RESET}")

if __name__ == "__main__":
    main()
