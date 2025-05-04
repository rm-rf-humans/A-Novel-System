import sys
from passengers.PassengerClass import Passenger
from flights.Flight import Flight
from flights.CrewMember import CrewMember
from passengers.ticket import Ticket
from utilities.seat_swap import SeatSwapper
from baggage.Baggage import Baggage
from baggage.BaggageFeeCalc import Baggage
from utilities.Feedback import Feedback
from utilities.ReminderEmailSender import ReminderEmailSender

def main_menu():
    """
    Displays the main menu and returns the user's choice.
    """
    print("\n--- Welcome to A-Novel-System ---")
    print("1. Manage Passengers")
    print("2. Manage Flights")
    print("3. Manage Crew Members")
    print("4. Manage Tickets")
    print("5. Seat Swapping System")
    print("6. Manage Baggage")
    print("7. Provide Feedback")
    print("8. Send Reminder Emails")
    print("9. Exit")
    
    return input("Enter your choice: ").strip()

def manage_passengers():
    """
    Provides functionality to manage passengers.
    """
    print("\n--- Manage Passengers ---")
    passenger = Passenger(passenger_id=1, name="John Doe", age=30, sex="Male", phone_number="1234567890")
    passenger.getinfo()
    passenger.ViewBookingDetails()

def manage_flights():
    """
    Provides functionality to manage flights.
    """
    print("\n--- Manage Flights ---")
    flight = Flight(flight_id=101, airline="Airline A", source="City A", destination="City B",
                    departure_time="10:00", arrival_time="12:00", date="2025-12-01", available_seats=100)
    flight.check_availability()
    flight.flightschedule()

def manage_crew_members():
    """
    Provides functionality to manage crew members.
    """
    print("\n--- Manage Crew Members ---")
    crew_member = CrewMember(crew_id=201, name="Jane Smith", role="Pilot", contact_info="jane.smith@example.com")
    crew_member.view_schedule()
    crew_member.update_status("On Duty")

def manage_tickets():
    """
    Provides functionality to manage tickets.
    """
    print("\n--- Manage Tickets ---")
    ticket = Ticket(ticket_id=301, passenger="John Doe", flight="101", seat_number="12A", payment_statues=1)
    ticket.GetTicketDetails()

def seat_swapping_system():
    """
    Provides functionality for the seat swapping system.
    """
    print("\n--- Seat Swapping System ---")
    swapper = SeatSwapper()
    swapper.show_available_seats()
    swapper.show_details()

def manage_baggage():
    """
    Provides functionality to manage baggage.
    """
    print("\n--- Manage Baggage ---")
    baggage = Baggage(baggage_id=1, owner="John Doe", weight=25, dimensions=(50, 40, 20))
    baggage.display_details()

    fee_calculator = Baggage(weight=baggage.weight, dimensions=baggage.dimensions)
    fee = fee_calculator.calculate_fee()
    print(f"Baggage Fee: ${fee:.2f}")

def provide_feedback():
    """
    Provides functionality to collect feedback.
    """
    print("\n--- Provide Feedback ---")
    feedback = Feedback(user="John Doe", message="Great service!", rating=5)
    feedback.display_feedback()

def send_reminder_emails():
    """
    Provides functionality to send reminder emails.
    """
    print("\n--- Send Reminder Emails ---")
    reminder = ReminderEmailSender(email="johndoe@example.com", subject="Flight Reminder", message="Your flight is scheduled for tomorrow.")
    reminder.send_email()

if __name__ == "__main__":
    while True:
        choice = main_menu()
        if choice == "1":
            manage_passengers()
        elif choice == "2":
            manage_flights()
        elif choice == "3":
            manage_crew_members()
        elif choice == "4":
            manage_tickets()
        elif choice == "5":
            seat_swapping_system()
        elif choice == "6":
            manage_baggage()
        elif choice == "7":
            provide_feedback()
        elif choice == "8":
            send_reminder_emails()
        elif choice == "9":
            print("Exiting the system. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice. Please try again.")
