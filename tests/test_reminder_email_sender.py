import unittest
from unittest.mock import patch, MagicMock
from utilities.ReminderEmailSender import ReminderEmailSender
from datetime import datetime, timedelta


class TestReminderEmailSender(unittest.TestCase):

    def setUp(self):
        self.sender_email = "testsender@example.com"
        self.sender_password = "testpassword"
        self.reminder_sender = ReminderEmailSender(self.sender_email, self.sender_password)

    @patch("utilities.ReminderEmailSender.smtplib.SMTP")
    def test_send_reminder_valid_days(self, mock_smtp):
        """Test send_reminder sends emails for 7, 3, 1 days before flight"""
        for days_before in [7, 3, 1]:
            flight_date = (datetime.now() + timedelta(days=days_before)).strftime("%Y-%m-%d")
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            result = self.reminder_sender.send_reminder(
                "John Doe", "recipient@example.com", flight_date
            )

            self.assertTrue(result)
            mock_server.sendmail.assert_called_once()
            mock_server.sendmail.reset_mock()

    @patch("utilities.ReminderEmailSender.smtplib.SMTP")
    def test_send_reminder_invalid_day(self, mock_smtp):
        """Test send_reminder does not send email for days not in [7, 3, 1]"""
        flight_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        result = self.reminder_sender.send_reminder(
            "John Doe", "recipient@example.com", flight_date
        )

        self.assertFalse(result)
        mock_smtp.assert_not_called()

    @patch("utilities.ReminderEmailSender.smtplib.SMTP", side_effect=Exception("SMTP error"))
    def test_send_reminder_exception(self, mock_smtp):
        """Test send_reminder handles SMTP exceptions"""
        flight_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        result = self.reminder_sender.send_reminder(
            "John Doe", "recipient@example.com", flight_date
        )
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
