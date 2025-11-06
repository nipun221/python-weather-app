import os
import pytest
from unittest.mock import patch, MagicMock
from main import send_alert_email

@pytest.fixture(autouse=True)
def fake_env():
    os.environ["WEATHER_API_KEY"] = "TEST_KEY"

@patch("main.smtplib.SMTP_SSL")
def test_send_alert_email(mock_smtp):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    city = "New Delhi"
    aqi = 5
    meaning = "Very Poor"

    send_alert_email(city, aqi, meaning)

    mock_smtp.assert_called_once_with("smtp.gmail.com", 465)
    mock_server.login.assert_called()    # we don't check creds here for security
    mock_server.send_message.assert_called_once()
