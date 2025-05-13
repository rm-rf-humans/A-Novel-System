import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class ReminderEmailSender:
    def __init__(self, sender_email: str, sender_password: str):
        self._sender_email = sender_email
        self._sender_password = sender_password

    def send_reminder(self, passenger_name: str, recipient_email: str, flight_date: str) -> bool:
        try:
            days_until_flight = (datetime.strptime(flight_date, "%Y-%m-%d") - datetime.now()).days
            if days_until_flight in [7, 3, 1]:
                subject = f"{days_until_flight}-Day Flight Reminder"
                body = (
                    f"Dear {passenger_name},\n\n"
                    f"This is a reminder that your flight is in {days_until_flight} day(s).\n"
                    f"Please check your itinerary and be prepared.\n\n"
                    f"Best regards,\nFlight System"
                )

                msg = MIMEMultipart()
                msg["From"] = self._sender_email
                msg["To"] = recipient_email
                msg["Subject"] = subject
                msg.attach(MIMEText(body, "plain"))

                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(self._sender_email, self._sender_password)
                    server.sendmail(self._sender_email, recipient_email, msg.as_string())

                return True
            return False
        except Exception as e:
            print(f"Reminder Email Error: {e}")
            return False
