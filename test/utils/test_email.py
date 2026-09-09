from unittest.mock import patch

from app.utils.email import send_email


@patch("app.utils.email.smtplib.SMTP")
def test_send_email_success(mock_smtp):
    result = send_email("user@example.com", "Welcome", "Hello")
    assert result is True
    mock_smtp.assert_called_once()