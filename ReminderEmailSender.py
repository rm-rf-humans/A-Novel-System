import smtplib
from datetime import datetime

class ReminderEmailSender:
    def __init__(self, sender_email, sender_password):
        self.__sender_email = sender_email
        self.__sender_password = sender_password

    def send_reminder(self, passenger_name, recipient_email, flight_date):
        try :
            days_until_flight = (datetime.strptime(flight_date, "%Y-%m-%d") - datetime.now()).days

            if days_until_flight in [7, 3, 1]:
                message = f"Subject: {days_until_flight} Day Reminder\n\n Dear {passenger_name}. + \n + I hope you are doing well, + \n + I want to anounce you that your flight is in{days_until_flight} day(s)! + \n + Best regards. "
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.sendmail(self.sender_email, recipient_email, message)
                print(f"Reminder sent to {recipient_email}")
        except Exception as e:
            print(f"Error: {e}")

sender = ReminderEmailSender("your_email@gmail.com", "your_password")
sender.send_reminder("Adel Shakal", "passenger_email@example.com", "10-3-2025")
