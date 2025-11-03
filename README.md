# WEATHER + AQI CLI app

It includes:
* Fancy dashboard-style terminal UI with emojis and ANSI colors
* Auto-detect city via IP if you press Enter
* Retry logic (3 attempts) for API calls with delays
* Full error handling (bad city, missing API key, network errors)
* Sends a **detailed** email alert (Gmail SMTP) when AQI ≥ 4 (Poor/Very Poor) using your custom template
* Uses `.env` for secrets (only dependency: `python-dotenv`)
* No logs saved (you asked `Logs: no`)

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


