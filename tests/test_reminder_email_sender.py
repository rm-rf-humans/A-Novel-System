import unittest
from unittest.mock import patch, MagicMock
from utilities.ReminderEmailSender import ReminderEmailSender

class TestReminderEmailSender(unittest.TestCase):

    @patch('utilities.ReminderEmailSender.smtplib.SMTP')
    def test_send_reminder(self, MockSMTP):
        """Test sending reminder email."""
        mock_smtp_instance = MockSMTP.return_value
        sender = ReminderEmailSender("test@example.com", "password")
        
        result = sender.send_reminder("John Doe", "john@example.com", "2025-05-20")
        self.assertTrue(result)  # Successful send

        # Check if the email was sent
        mock_smtp_instance.sendmail.assert_called_once()

    @patch('utilities.ReminderEmailSender.smtplib.SMTP')
    def test_send_reminder_invalid_date(self, MockSMTP):
        """Test invalid date (future flight) does not trigger email."""
        sender = ReminderEmailSender("test@example.com", "password")
        
        result = sender.send_reminder("John Doe", "john@example.com", "2025-05-30")
        self.assertFalse(result)  # Email should not be sent
