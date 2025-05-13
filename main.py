import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QHBoxLayout, QSpinBox, QDoubleSpinBox, QGroupBox, QTabWidget, QDateEdit
from PyQt5.QtCore import Qt
from datetime import datetime

from passengers.PassengerClass import Passenger as BasePassenger
from flights.Flight import Flight
from utilities.Feedback import Feedback
from utilities.ReminderEmailSender import ReminderEmailSender
from utilities.seat_swap import Passenger, Socializer, TallPassenger, EcoPassenger, SeatSwapper 
from baggage.Baggage import Baggage


class SeatSelectionWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Initial available seats
        self.available_seats = {
            "1A": True, "1B": True, "1C": True, "1D": True,
            "2A": True, "2B": True, "2C": True, "2D": True,
            "3A": True, "3B": True, "3C": True, "3D": True,
            "4A": True, "4B": True, "4C": True, "4D": True,
        }

        self.selected_seat = None  # Track selected seat
        self.seat_swapper = SeatSwapper()  # Initialize seat swapper
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title/Instruction
        self.title_label = QLabel("Select Your Seat", self)
        layout.addWidget(self.title_label)

        # Seat Map Layout (Grid)
        self.grid_layout = QGridLayout()
        self.create_seat_buttons()
        
        layout.addLayout(self.grid_layout)

        # Display selected seat
        self.selected_seat_label = QLabel("Selected Seat: None", self)
        layout.addWidget(self.selected_seat_label)

        # Passenger Type Selection
        passenger_group = QGroupBox("Passenger Type")
        passenger_layout = QFormLayout()
        
        self.passenger_type = QComboBox(self)
        self.passenger_type.addItems(["Regular", "Socializer", "Tall", "Eco-Friendly"])
        self.passenger_type.currentIndexChanged.connect(self.update_passenger_options)
        passenger_layout.addRow("Type:", self.passenger_type)
        
        # Additional fields for passenger types
        self.interest_input = QLineEdit(self)
        self.interest_input.setPlaceholderText("Enter your interests")
        self.interest_input.setVisible(False)
        passenger_layout.addRow("Interests:", self.interest_input)
        
        self.height_input = QSpinBox(self)
        self.height_input.setRange(150, 220)
        self.height_input.setSuffix(" cm")
        self.height_input.setVisible(False)
        passenger_layout.addRow("Height:", self.height_input)
        
        passenger_group.setLayout(passenger_layout)
        layout.addWidget(passenger_group)

        # Seat preference selection
        preference_group = QGroupBox("Seating Preference")
        preference_layout = QFormLayout()
        
        self.preference_combo = QComboBox(self)
        self.preference_combo.addItems(["Networking", "Sleep", "Work", "Comfort", "Eco-Friendly"])
        preference_layout.addRow("Preference:", self.preference_combo)
        
        preference_group.setLayout(preference_layout)
        layout.addWidget(preference_group)

        # Seat selection form (for user details)
        self.details_form = QFormLayout()
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter Your Name")
        self.details_form.addRow("Name: ", self.name_input)

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Enter Your Email")
        self.details_form.addRow("Email: ", self.email_input)

        self.flight_combo = QComboBox(self)
        self.flight_combo.addItems(["Flight 1", "Flight 2", "Flight 3"])  # Flight options
        self.details_form.addRow("Select Flight: ", self.flight_combo)

        self.flight_date = QDateEdit(self)
        self.flight_date.setDate(datetime.now().date())
        self.flight_date.setCalendarPopup(True)
        self.details_form.addRow("Flight Date:", self.flight_date)

        self.age_input = QSpinBox(self)
        self.age_input.setRange(18, 100)  # Age range
        self.details_form.addRow("Age: ", self.age_input)

        # Baggage information section
        baggage_group = QGroupBox("Baggage Information")
        baggage_layout = QFormLayout()
        
        self.baggage_weight = QDoubleSpinBox(self)
        self.baggage_weight.setRange(0, 50)  # Weight range in kg
        self.baggage_weight.setDecimals(1)
        self.baggage_weight.setSuffix(" kg")
        self.baggage_weight.setValue(15.0)  # Default weight
        baggage_layout.addRow("Baggage Weight:", self.baggage_weight)
        
        self.check_baggage_button = QPushButton("Check Baggage Fee", self)
        self.check_baggage_button.clicked.connect(self.check_baggage)
        baggage_layout.addRow(self.check_baggage_button)
        
        self.baggage_status = QLabel("No baggage checked yet", self)
        baggage_layout.addRow(self.baggage_status)
        
        baggage_group.setLayout(baggage_layout)
        
        layout.addLayout(self.details_form)
        layout.addWidget(baggage_group)

        # Submit button for booking the seat
        self.submit_button = QPushButton("Book Seat", self)
        self.submit_button.clicked.connect(self.book_seat)
        layout.addWidget(self.submit_button)

        # Swap Seat button
        self.swap_button = QPushButton("Swap Seat", self)
        self.swap_button.clicked.connect(self.swap_seat)
        layout.addWidget(self.swap_button)

        # Show available zone seats
        self.zone_button = QPushButton("Show Zone Seats", self)
        self.zone_button.clicked.connect(self.show_zone_seats)
        layout.addWidget(self.zone_button)

        # Send reminder email button
        self.reminder_button = QPushButton("Schedule Reminder Email", self)
        self.reminder_button.clicked.connect(self.schedule_reminder)
        layout.addWidget(self.reminder_button)

        self.setLayout(layout)
        self.setWindowTitle('Seat Selection & Booking')
        self.setGeometry(100, 100, 600, 800)
        self.show()

    def update_passenger_options(self):
        passenger_type = self.passenger_type.currentText()
        
        # Hide all optional fields first
        self.interest_input.setVisible(False)
        self.height_input.setVisible(False)
        
        # Show fields based on passenger type
        if passenger_type == "Socializer":
            self.interest_input.setVisible(True)
        elif passenger_type == "Tall":
            self.height_input.setVisible(True)
        elif passenger_type == "Eco-Friendly":
            # For Eco-Friendly, no additional fields needed
            pass

    def create_seat_buttons(self):
        row = 0
        col = 0

        for seat, available in self.available_seats.items():
            seat_button = QPushButton(seat, self)
            seat_button.setFixedSize(50, 50)
            seat_button.setEnabled(available)  
            seat_button.clicked.connect(self.select_seat)
            self.grid_layout.addWidget(seat_button, row, col)
            
            col += 1
            if col > 3:  
                col = 0
                row += 1

    def select_seat(self):
        selected_button = self.sender()  
        selected_seat = selected_button.text()

        if self.available_seats[selected_seat]:  
            self.selected_seat = selected_seat
            self.selected_seat_label.setText(f"Selected Seat: {self.selected_seat}")
            self.available_seats[selected_seat] = False  
            selected_button.setEnabled(False)
        else:
            self.selected_seat_label.setText("Seat already taken, please select another.")

    def check_baggage(self):
        passenger_name = self.name_input.text()
        weight = self.baggage_weight.value()
        
        if passenger_name == "":
            self.baggage_status.setText("Please enter your name first.")
            return
        
        # Create baggage instance
        baggage = Baggage(passenger_name, weight)
        
        # Calculate fee
        baggage.calculate_fee()
        
        # Update status
        self.baggage_status.setText(baggage.get_fee_summary())

    def create_appropriate_passenger(self, name, seat, preference):
        """Create the appropriate passenger type based on selection"""
        passenger_type = self.passenger_type.currentText()
        
        if passenger_type == "Socializer":
            interest = self.interest_input.text() or "General socializing"
            return Socializer(name, seat, preference, interest)
        elif passenger_type == "Tall":
            height = self.height_input.value()
            return TallPassenger(name, seat, preference, height)
        elif passenger_type == "Eco-Friendly":
            eco_passenger = EcoPassenger(name, seat, preference)
            recommended_meal = eco_passenger.recommend_meal()
            self.selected_seat_label.setText(f"Selected Seat: {seat}\nRecommended Meal: {recommended_meal}")
            return eco_passenger
        else:
            return Passenger(name, seat, preference)

    def book_seat(self):
        if self.selected_seat is None:
            self.selected_seat_label.setText("No seat selected. Please select a seat first.")
            return
        
        passenger_name = self.name_input.text()
        flight = self.flight_combo.currentText()
        preference = self.preference_combo.currentText()
        age = self.age_input.value()
        baggage_weight = self.baggage_weight.value()

        if passenger_name == "":
            self.selected_seat_label.setText("Please enter your name.")
            return

        passenger = self.create_appropriate_passenger(
            name=passenger_name, 
            seat=self.selected_seat, 
            preference=preference
        )
        
        # Handle baggage
        baggage = Baggage(passenger_name, baggage_weight)
        baggage.calculate_fee()
        baggage_fee = baggage.baggage_fee
        
        self.seat_swapper.add_passenger(passenger)

        confirmation_text = f"Booking confirmed for {passenger_name} on {flight} with seat {self.selected_seat}"
        confirmation_text += f"\nPreference: {preference}"
        
        # Add passenger type specific info
        passenger_type = self.passenger_type.currentText()
        if passenger_type == "Socializer":
            confirmation_text += f"\nInterests: {self.interest_input.text()}"
        elif passenger_type == "Tall":
            confirmation_text += f"\nHeight: {self.height_input.value()} cm"
        elif passenger_type == "Eco-Friendly":
            eco_passenger = passenger
            confirmation_text += f"\nRecommended Meal: {eco_passenger.recommend_meal()}"
        
        # Add baggage information to confirmation
        if baggage_fee > 0:
            confirmation_text += f"\nBaggage fee: ${baggage_fee} (Weight: {baggage_weight}kg)"
        else:
            confirmation_text += f"\nNo baggage fee (Weight: {baggage_weight}kg)"
        
        self.selected_seat_label.setText(confirmation_text)

    def swap_seat(self):
        self.seat_swapper.assign_seats()
        passenger_data = self.seat_swapper.get_passenger_data()

        if not passenger_data:
            self.selected_seat_label.setText("No passengers available for seat swapping.")
            return

        swap_message = "\n".join([f"{data['name']} -> Seat {data['seat']} (Preference: {data['preference']})"
                                  for data in passenger_data])
        self.selected_seat_label.setText(f"Seat Swap Complete:\n{swap_message}")

    def show_zone_seats(self):
        available_zones = self.seat_swapper.get_available_seats()
        zone_info = []
        
        for zone, seats in available_zones.items():
            if seats:
                seat_list = ", ".join(seats)
                zone_info.append(f"{zone} Zone: {seat_list}")
            else:
                zone_info.append(f"{zone} Zone: No seats available")
        
        self.selected_seat_label.setText("Available Zone Seats:\n" + "\n".join(zone_info))

    def schedule_reminder(self):
        passenger_name = self.name_input.text()
        email = self.email_input.text()
        flight_date = self.flight_date.date().toString("yyyy-MM-dd")
        
        if not passenger_name or not email:
            self.selected_seat_label.setText("Please enter your name and email to schedule a reminder.")
            return
        
        # Initialize the email sender with dummy credentials (for demo purposes)
        # In a real app, these would be securely stored credentials
        email_sender = ReminderEmailSender(
            sender_email="flightsystem@example.com",
            sender_password="password123"
        )
        
        # Attempt to send/schedule reminder
        success = email_sender.send_reminder(
            passenger_name=passenger_name,
            recipient_email=email,
            flight_date=flight_date
        )
        
        if success:
            self.selected_seat_label.setText(f"Reminder emails scheduled for {flight_date}")
        else:
            self.selected_seat_label.setText("Failed to schedule reminder. Please try again later.")


class FeedbackWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Provide Your Feedback", self)
        layout.addWidget(self.title_label)

        # Feedback Form
        self.feedback_input = QLineEdit(self)
        self.feedback_input.setPlaceholderText("Enter your feedback here...")
        layout.addWidget(self.feedback_input)

        # Submit Button
        self.submit_button = QPushButton("Submit Feedback", self)
        self.submit_button.clicked.connect(self.submit_feedback)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.setWindowTitle('Feedback')
        self.setGeometry(100, 100, 400, 200)

    def submit_feedback(self):
        feedback_text = self.feedback_input.text()
        if feedback_text == "":
            self.feedback_input.setText("Please enter feedback.")
        else:
            self.feedback_input.setText("Thank you for your feedback!")


class BaggageInfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Baggage Policy Information", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Policy information
        from baggage.BaggageFeeCalc import BaggageFeeCalculatorProxy
        calculator = BaggageFeeCalculatorProxy()
        
        policy_info = QLabel(f"""
        Baggage Policy:
        - Weight limit: {calculator.get_limit()} kg
        - Fee per kg overweight: ${calculator.calculator.policy.get_fee_per_kg()}
        
        Excess baggage fees will be charged for any baggage exceeding the weight limit.
        """, self)
        policy_info.setAlignment(Qt.AlignLeft)
        layout.addWidget(policy_info)

        self.setLayout(layout)
        self.setWindowTitle('Baggage Policy')
        self.setGeometry(100, 100, 400, 200)


class MainApplication(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Create individual window instances
        self.seat_window = SeatSelectionWindow()
        self.feedback_window = FeedbackWindow()
        self.baggage_window = BaggageInfoWindow()
        
        # Add windows to tabs
        tabs.addTab(self.seat_window, "Seat Selection")
        tabs.addTab(self.feedback_window, "Feedback")
        tabs.addTab(self.baggage_window, "Baggage Info")
        
        layout.addWidget(tabs)
        
        self.setLayout(layout)
        self.setWindowTitle("Flight Booking System")
        self.setGeometry(100, 100, 800, 900)


if __name__ == "__main__":
    app = QApplication(sys.argv)  

    # Option 1: Use separate windows
    # seat_window = SeatSelectionWindow()
    # seat_window.show()
    # feedback_window = FeedbackWindow()
    # feedback_window.show()
    # baggage_info_window = BaggageInfoWindow()
    # baggage_info_window.show()
    
    # Option 2: Use tabbed interface (recommended)
    main_app = MainApplication()
    main_app.show()

    sys.exit(app.exec_())