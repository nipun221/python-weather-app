[![Weather + Aqi App Pipeline](https://github.com/nipun221/python-weather-app/actions/workflows/ci.yml/badge.svg)](https://github.com/nipun221/python-weather-app/actions/workflows/ci.yml)
![Docker Image Version](https://ghcr-badge.egpl.dev/nipun221/weather-cli/latest_tag)
# WEATHER + AQI CLI APP

---

It includes:
* Fancy dashboard-style terminal UI with emojis and ANSI colors
* Auto-detect city via IP if you press Enter
* Retry logic (3 attempts) for API calls with delays
* Full error handling (bad city, missing API key, network errors)
* Sends a **detailed** email alert (Gmail SMTP) when AQI ≥ 4 (Poor/Very Poor) using your custom template
* Uses `.env` for secrets

---

## 🔧 Setup (before running)

1. Install dependency:

```bash
pip install python-dotenv requests
```

2. Create `.env` in same folder with:

```
WEATHER_API_KEY=YOUR_OPENWEATHERMAP_API_KEY
SMTP_EMAIL=your.email@gmail.com
SMTP_PASS=YOUR_GMAIL_APP_PASSWORD
ALERT_EMAIL_TO=recipient@example.com
```

> `SMTP_PASS` must be a Gmail App Password (not your normal password).

3. Run:

```bash
python main.py
```

---



## ✅ Notes & tips

* If you get `smtplib.SMTPAuthenticationError`, make sure:

  * 2FA is enabled on your Google account, and
  * You created an **App Password** and used it as `SMTP_PASS` in `.env`.
* If auto IP detection fails, the script falls back to `Zurich`. Feel free to change default.
* You can adjust `RETRIES` and `RETRY_DELAY` constants at the top.
* On Windows PowerShell, colors should work in modern terminals; if colors look weird, remove ANSI codes or run in a terminal that supports them.

---

### Run locally

```bash
docker run -it ghcr.io/nipun221/weather-cli:latest
```

## Screenshot with demo

<img width="921" height="536" alt="image" src="https://github.com/user-attachments/assets/0c6a529b-46d7-4357-8ea6-d39900262be8" />
<img width="913" height="500" alt="image" src="https://github.com/user-attachments/assets/1c866924-6338-42ce-8587-0b1bb74f4242" />
<img width="728" height="458" alt="image" src="https://github.com/user-attachments/assets/db8522ad-9d6f-4ee4-be11-ca3c9ba2414f" />


